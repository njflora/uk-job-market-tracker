"""Write raw records and cleaned postings to Postgres.

Rules (see docs/FIELD_MAPPING.md):
- Every raw API record is saved to raw_postings before anything else.
- A posting is matched on its dedup_key (company | title | region).
- Every town a posting was seen in is kept in `towns`, so the tracker can filter by town.
- When the same job exists from both sources, Reed wins: an Adzuna row can be
  replaced by Reed, but a Reed row is never overwritten by Adzuna.
- Re-seeing a posting updates last_seen and keeps it active.
"""

from psycopg.types.json import Jsonb

from pipeline.tag.clean import normalise_company

POSTING_COLUMNS = [
    "dedup_key", "source", "source_job_id", "company_id", "title", "location_text",
    "region", "seniority", "salary_min", "salary_max", "salary_period",
    "salary_is_predicted", "description", "url", "posted_at", "expires_at",
    "contract_type", "full_time", "applications", "role_family",
]

# Adds a town to the list without repeating it.
ADD_TOWN = "towns = (select array(select distinct t from unnest(towns || %s::text[]) as t where t is not null))"


def save_raw(conn, source, source_job_id, payload):
    """Save a raw API record, but only if it differs from the latest stored copy.

    Unchanged: the latest copy's last_seen_at is updated instead (migration 007).
    Returns True if a new row was written.
    """
    latest = conn.execute(
        "select raw_id, payload from raw_postings where source = %s and source_job_id = %s "
        "order by fetched_at desc, raw_id desc limit 1",
        (source, str(source_job_id)),
    ).fetchone()
    if latest is not None and latest[1] == payload:
        conn.execute("update raw_postings set last_seen_at = now() where raw_id = %s", (latest[0],))
        return False
    conn.execute(
        "insert into raw_postings (source, source_job_id, payload, last_seen_at) values (%s, %s, %s, now())",
        (source, str(source_job_id), Jsonb(payload)),
    )
    return True


def company_id_for(conn, name):
    """Find the company by its normalised name, or create it."""
    key = normalise_company(name)
    if not key:
        return None
    row = conn.execute(
        """insert into companies (name, name_normalised) values (%s, %s)
           on conflict (name_normalised) do update set name = companies.name
           returning company_id""",
        (name.strip(), key),
    ).fetchone()
    return row[0]


def upsert_posting(conn, posting, seen_at=None):
    """Insert a new posting, or refresh an existing one. Returns 'new', 'updated' or 'kept'.

    seen_at is normally now(); the rebuild passes the original fetch time instead.
    """
    town = [posting.get("town")] if posting.get("town") else []
    existing = conn.execute(
        "select posting_id, source from postings where dedup_key = %s", (posting["dedup_key"],)
    ).fetchone()

    if existing is None:
        cols = POSTING_COLUMNS + ["towns", "first_seen", "last_seen"]
        marks = ", ".join(["%s"] * len(POSTING_COLUMNS)) + ", %s, coalesce(%s, now()), coalesce(%s, now())"
        conn.execute(
            f"insert into postings ({', '.join(cols)}) values ({marks})",
            [posting.get(c) for c in POSTING_COLUMNS] + [town, seen_at, seen_at],
        )
        return "new"

    posting_id, existing_source = existing
    if existing_source == "reed" and posting["source"] == "adzuna":
        # Reed wins: only record the extra town and that the job is still live.
        conn.execute(
            f"update postings set {ADD_TOWN}, last_seen = greatest(last_seen, coalesce(%s, now())), "
            "is_active = true where posting_id = %s",
            (town, seen_at, posting_id),
        )
        return "kept"

    sets = ", ".join(f"{c} = %s" for c in POSTING_COLUMNS if c != "dedup_key")
    values = [posting.get(c) for c in POSTING_COLUMNS if c != "dedup_key"]
    conn.execute(
        f"update postings set {sets}, {ADD_TOWN}, "
        "last_seen = greatest(last_seen, coalesce(%s, now())), is_active = true where posting_id = %s",
        values + [town, seen_at, posting_id],
    )
    return "updated"


def mark_inactive(conn, adzuna_grace_days=3, include_adzuna=True):
    """Close postings that have expired (Reed) or not been seen for a few days (Adzuna).

    Rows are never deleted, so trend data survives.
    include_adzuna=False skips the Adzuna rule, used when Adzuna failed this run.
    """
    reed = conn.execute(
        "update postings set is_active = false "
        "where is_active and source = 'reed' and expires_at < now()"
    ).rowcount
    if not include_adzuna:
        return reed
    adzuna = conn.execute(
        "update postings set is_active = false "
        "where is_active and source = 'adzuna' and last_seen < now() - make_interval(days => %s)",
        (adzuna_grace_days,),
    ).rowcount
    return reed + adzuna

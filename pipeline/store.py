"""Write raw records and cleaned postings to Postgres.

Rules (see docs/FIELD_MAPPING.md):
- Every raw API record is saved to raw_postings before anything else.
- A posting is matched on its dedup_key (company | title | location).
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


def save_raw(conn, source, source_job_id, payload):
    conn.execute(
        "insert into raw_postings (source, source_job_id, payload) values (%s, %s, %s)",
        (source, str(source_job_id), Jsonb(payload)),
    )


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


def upsert_posting(conn, posting):
    """Insert a new posting, or refresh an existing one. Returns 'new', 'updated' or 'kept'."""
    existing = conn.execute(
        "select posting_id, source from postings where dedup_key = %s", (posting["dedup_key"],)
    ).fetchone()

    if existing is None:
        cols = ", ".join(POSTING_COLUMNS)
        marks = ", ".join(["%s"] * len(POSTING_COLUMNS))
        conn.execute(
            f"insert into postings ({cols}) values ({marks})",
            [posting.get(c) for c in POSTING_COLUMNS],
        )
        return "new"

    posting_id, existing_source = existing
    if existing_source == "reed" and posting["source"] == "adzuna":
        # Reed wins: only record that the job is still live.
        conn.execute(
            "update postings set last_seen = now(), is_active = true where posting_id = %s",
            (posting_id,),
        )
        return "kept"

    sets = ", ".join(f"{c} = %s" for c in POSTING_COLUMNS if c != "dedup_key")
    values = [posting.get(c) for c in POSTING_COLUMNS if c != "dedup_key"]
    conn.execute(
        f"update postings set {sets}, last_seen = now(), is_active = true where posting_id = %s",
        values + [posting_id],
    )
    return "updated"


def mark_inactive(conn, adzuna_grace_days=3):
    """Close postings that have expired (Reed) or not been seen for a few days (Adzuna).

    Rows are never deleted, so trend data survives.
    """
    reed = conn.execute(
        "update postings set is_active = false "
        "where is_active and source = 'reed' and expires_at < now()"
    ).rowcount
    adzuna = conn.execute(
        "update postings set is_active = false "
        "where is_active and source = 'adzuna' and last_seen < now() - make_interval(days => %s)",
        (adzuna_grace_days,),
    ).rowcount
    return reed + adzuna

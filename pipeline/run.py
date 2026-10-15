"""One full pass of the pipeline: ingest, filter, clean and store.

Run from the repo root:
    python -m pipeline.run              # normal run
    python -m pipeline.run --dry-run    # call the APIs and print a summary, write nothing

API budget per run (defaults below):
    Reed:   up to 8 terms x 2 pages = 16 search calls, plus 1 details call per NEW in-scope job
    Adzuna: up to 6 terms x 2 pages = 12 calls (daily limit is 250)
"""

import argparse
import os
import time
from collections import Counter

import psycopg
import requests
from dotenv import load_dotenv

from pipeline import mapping, store
from pipeline.sources import adzuna, reed
from pipeline.tag.titles import classify_title

REED_TERMS = [
    "data analyst", "business intelligence", "power bi", "bi developer",
    "bi analyst", "reporting analyst", "mi analyst", "insight analyst",
]
ADZUNA_TERMS = [
    "data analyst", "business intelligence", "power bi developer",
    "bi developer", "reporting analyst", "insight analyst",
]
MAX_PAGES = 2
ADZUNA_MAX_DAYS_OLD = 30


def collect_reed(stats):
    """Search Reed, keep in-scope titles. Returns {jobId: (search_row, role_family)}."""
    found = {}
    for term in REED_TERMS:
        for row in reed.search_all(term, max_pages=MAX_PAGES):
            stats["reed_seen"] += 1
            family, is_training = classify_title(row.get("jobTitle"))
            if is_training:
                stats["reed_training_ads"] += 1
            elif family:
                found[row["jobId"]] = (row, family)
        time.sleep(reed.PAUSE_SECONDS)
    return found


def collect_adzuna(stats):
    """Search Adzuna, keep in-scope titles. Returns {id: (row, role_family)}."""
    found = {}
    for term in ADZUNA_TERMS:
        rows = adzuna.search_all(term, max_pages=MAX_PAGES, max_days_old=ADZUNA_MAX_DAYS_OLD)
        for row in rows:
            stats["adzuna_seen"] += 1
            family, is_training = classify_title(row.get("title"))
            if is_training:
                stats["adzuna_training_ads"] += 1
            elif family:
                found[row["id"]] = (row, family)
    return found


def known_reed_ids(conn):
    """Reed jobs already stored, so we skip their details call (saves API calls)."""
    rows = conn.execute("select source_job_id from postings where source = 'reed'").fetchall()
    return {r[0] for r in rows}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="call the APIs but write nothing")
    args = parser.parse_args()

    load_dotenv()
    stats = Counter()

    reed_jobs = collect_reed(stats)
    adzuna_jobs = collect_adzuna(stats)
    stats["reed_in_scope"] = len(reed_jobs)
    stats["adzuna_in_scope"] = len(adzuna_jobs)

    if args.dry_run:
        families = Counter(f for _, f in list(reed_jobs.values()) + list(adzuna_jobs.values()))
        print_summary(stats, families)
        return

    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
        already = known_reed_ids(conn)

        # Reed first, so Reed rows win any cross-source duplicate.
        for job_id, (row, family) in reed_jobs.items():
            if str(job_id) in already:
                full = None  # already have the details; this pass just refreshes it
                stats["reed_details_skipped"] += 1
            else:
                try:
                    full = reed.details(job_id)
                except requests.HTTPError:
                    stats["reed_details_failed"] += 1  # e.g. job removed since the search
                    continue
                stats["reed_details_calls"] += 1
                time.sleep(reed.PAUSE_SECONDS)
            store.save_raw(conn, "reed", job_id, {"search": row, "details": full})
            posting = mapping.from_reed(row, full, family)
            if full is None:
                # Keep the stored salary/description rather than blanking them.
                posting = refresh_only(conn, posting)
            posting["company_id"] = store.company_id_for(conn, posting["company"] or "")
            stats[f"reed_{store.upsert_posting(conn, posting)}"] += 1

        for job_id, (row, family) in adzuna_jobs.items():
            store.save_raw(conn, "adzuna", job_id, row)
            posting = mapping.from_adzuna(row, family)
            posting["company_id"] = store.company_id_for(conn, posting["company"] or "")
            stats[f"adzuna_{store.upsert_posting(conn, posting)}"] += 1

        stats["marked_inactive"] = store.mark_inactive(conn)
        conn.commit()

    print_summary(stats)


def refresh_only(conn, posting):
    """For a Reed job seen before, reuse the stored details fields."""
    row = conn.execute(
        "select salary_min, salary_max, salary_period, description, contract_type, full_time "
        "from postings where source = 'reed' and source_job_id = %s",
        (posting["source_job_id"],),
    ).fetchone()
    if row:
        keys = ["salary_min", "salary_max", "salary_period", "description", "contract_type", "full_time"]
        posting.update(dict(zip(keys, row)))
    return posting


def print_summary(stats, families=None):
    print("\nRun summary")
    for key in sorted(stats):
        print(f"  {key:24} {stats[key]}")
    if families:
        print("\nIn-scope jobs by role family (before dedup)")
        for family, n in families.most_common():
            print(f"  {family:24} {n}")


if __name__ == "__main__":
    main()

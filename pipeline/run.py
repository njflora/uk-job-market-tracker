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
import sys
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

# Secrets each part needs. On GitHub a missing secret arrives as an empty string.
NEEDS = {
    "database": ["DATABASE_URL"],
    "reed": ["REED_API_KEY"],
    "adzuna": ["ADZUNA_APP_ID", "ADZUNA_APP_KEY"],
}


def missing_secrets(part):
    return [name for name in NEEDS[part] if not os.environ.get(name, "").strip()]


def collect_safely(name, collect, stats, errors):
    """Run one source. If it fails, record why and carry on with the other source."""
    missing = missing_secrets(name)
    if missing:
        errors.append(f"{name}: {', '.join(missing)} is empty. Add it to .env, or to GitHub secrets for scheduled runs.")
        return None
    try:
        return collect(stats)
    except requests.RequestException as exc:
        errors.append(f"{name}: {exc}")
        return None


def collect_reed(stats):
    """Search Reed, keep in-scope titles. Returns {jobId: (search_row, role_family)}."""
    found = {}
    for term in REED_TERMS:
        for row in reed.search_all(term, max_pages=MAX_PAGES):
            stats["reed_seen"] += 1
            family, is_training = classify_title(row.get("jobTitle"), row.get("employerName"))
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
            family, is_training = classify_title(row.get("title"), (row.get("company") or {}).get("display_name"))
            if is_training:
                stats["adzuna_training_ads"] += 1
            elif family:
                found[row["id"]] = (row, family)
    return found


def stored_reed_details(conn):
    """Details already fetched for each Reed job, newest first. Saves a details call per known job."""
    rows = conn.execute(
        "select distinct on (source_job_id) source_job_id, payload->'details' "
        "from raw_postings where source = 'reed' and payload->'details' <> 'null'::jsonb "
        "order by source_job_id, fetched_at desc"
    ).fetchall()
    return {job_id: details for job_id, details in rows}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="call the APIs but write nothing")
    args = parser.parse_args()

    load_dotenv()
    stats = Counter()
    errors = []

    if not args.dry_run and missing_secrets("database"):
        sys.exit("DATABASE_URL is empty. Add it to .env, or to GitHub secrets for scheduled runs.")

    # None means that source failed; {} means it worked but found nothing.
    reed_result = collect_safely("reed", collect_reed, stats, errors)
    adzuna_result = collect_safely("adzuna", collect_adzuna, stats, errors)
    reed_jobs = reed_result or {}
    adzuna_jobs = adzuna_result or {}
    stats["reed_in_scope"] = len(reed_jobs)
    stats["adzuna_in_scope"] = len(adzuna_jobs)

    if args.dry_run:
        families = Counter(f for _, f in list(reed_jobs.values()) + list(adzuna_jobs.values()))
        print_summary(stats, families)
        finish(errors)
        return

    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
        stored = stored_reed_details(conn)

        # Reed first, so Reed rows win any cross-source duplicate.
        for job_id, (row, family) in reed_jobs.items():
            fetched_now = str(job_id) not in stored
            if not fetched_now:
                full = stored[str(job_id)]  # fetched on an earlier run; no API call needed
                stats["reed_details_reused"] += 1
            else:
                try:
                    full = reed.details(job_id)
                except requests.HTTPError:
                    stats["reed_details_failed"] += 1  # e.g. job removed since the search
                    continue
                stats["reed_details_calls"] += 1
                time.sleep(reed.PAUSE_SECONDS)
            # Store details only when newly fetched, so raw_postings doesn't repeat them every day.
            store.save_raw(conn, "reed", job_id, {"search": row, "details": full if fetched_now else None})
            posting = mapping.from_reed(row, full, family)
            posting["company_id"] = store.company_id_for(conn, posting["company"] or "")
            stats[f"reed_{store.upsert_posting(conn, posting)}"] += 1

        for job_id, (row, family) in adzuna_jobs.items():
            store.save_raw(conn, "adzuna", job_id, row)
            posting = mapping.from_adzuna(row, family)
            posting["company_id"] = store.company_id_for(conn, posting["company"] or "")
            stats[f"adzuna_{store.upsert_posting(conn, posting)}"] += 1

        # Only close Adzuna jobs if Adzuna actually ran; otherwise an outage would close them all.
        stats["marked_inactive"] = store.mark_inactive(conn, include_adzuna=adzuna_result is not None)
        conn.commit()

    print_summary(stats)
    finish(errors)


def finish(errors):
    """Exit with an error (so GitHub shows the run red and emails you) if any source failed."""
    if errors:
        print("\nProblems this run:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)


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

"""Rebuild postings and companies from raw_postings, with the current rules.

Makes NO calls to Reed or Adzuna: everything comes from the raw records already stored.
(It does look up Reed postcodes on postcodes.io to get towns and regions.)
raw_postings itself is never changed.

Run from the repo root:
    python -m pipeline.rebuild --dry-run   # do it all, print the summary, then undo
    python -m pipeline.rebuild             # do it for real (asks you to type 'rebuild')
"""

import argparse
import os
from collections import Counter

import psycopg
from dotenv import load_dotenv

from pipeline import mapping, store
from pipeline.tag import skills
from pipeline.tag.titles import classify_title


def latest_raw(conn):
    """Collapse raw_postings to one record per job, keeping the newest data and the first/last fetch times."""
    jobs = {}
    rows = conn.execute(
        "select source, source_job_id, fetched_at, payload from raw_postings order by fetched_at, raw_id"
    ).fetchall()
    for source, job_id, fetched_at, payload in rows:
        job = jobs.setdefault((source, job_id), {"first": fetched_at, "details": None})
        job["last"] = fetched_at
        if source == "reed":
            job["row"] = payload.get("search")
            if payload.get("details"):
                job["details"] = payload["details"]  # later runs store None when details were skipped
        else:
            job["row"] = payload
    return jobs, len(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="rebuild, print the summary, then undo")
    args = parser.parse_args()

    if not args.dry_run:
        answer = input("This empties postings and companies and rebuilds them from raw_postings. Type 'rebuild': ")
        if answer.strip() != "rebuild":
            print("Cancelled. Nothing changed.")
            return

    load_dotenv()
    stats = Counter()
    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
        stats["postings_before"] = conn.execute("select count(*) from postings").fetchone()[0]
        jobs, stats["raw_records"] = latest_raw(conn)
        stats["unique_raw_jobs"] = len(jobs)

        conn.execute("truncate posting_skills, postings, companies restart identity cascade")

        # Reed first, so Reed rows win any cross-source duplicate.
        for source in ("reed", "adzuna"):
            for (src, job_id), job in jobs.items():
                if src != source or not job.get("row"):
                    continue
                row = job["row"]
                if source == "reed":
                    family, training = classify_title(row.get("jobTitle"), row.get("employerName"))
                else:
                    family, training = classify_title(row.get("title"), (row.get("company") or {}).get("display_name"))
                if training:
                    stats[f"{source}_training_ads_excluded"] += 1
                    continue
                if not family:
                    stats[f"{source}_out_of_scope_excluded"] += 1
                    continue

                if source == "reed":
                    posting = mapping.from_reed(row, job["details"], family)
                else:
                    posting = mapping.from_adzuna(row, family)
                posting["company_id"] = store.company_id_for(conn, posting["company"] or "")
                stats[f"{source}_{store.upsert_posting(conn, posting, seen_at=job['last'])}"] += 1
                conn.execute(
                    "update postings set first_seen = least(first_seen, %s) where dedup_key = %s",
                    (job["first"], posting["dedup_key"]),
                )

        stats["marked_inactive"] = store.mark_inactive(conn)
        stats["skill_tagged_postings"], stats["skill_links"] = skills.tag_all(conn)
        stats["postings_after"] = conn.execute("select count(*) from postings").fetchone()[0]
        stats["postings_with_several_towns"] = conn.execute(
            "select count(*) from postings where cardinality(towns) > 1"
        ).fetchone()[0]

        if args.dry_run:
            conn.rollback()
            print("\nDRY RUN: everything above was undone.")
        else:
            conn.commit()

    print("\nRebuild summary")
    for key in sorted(stats):
        print(f"  {key:32} {stats[key]}")


if __name__ == "__main__":
    main()

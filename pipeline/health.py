"""Daily health check: did the pipeline really work, even when the run went green?

Runs on GitHub Actions about two hours after the daily ingest (.github/workflows/health.yml).
If any check fails, the script exits with an error, the run goes red and GitHub emails you.
A summary table is written to the run's page either way.

Run it yourself from the repo root:
    python -m pipeline.health
"""

import os
import sys

import psycopg
import requests
from dotenv import load_dotenv

SITE_URL = "https://njflora.github.io/uk-job-market-tracker/"

# Warning levels, set at roughly a quarter of the figures on 15 Oct 2026
# (Reed 129, Adzuna 206 postings seen in a day; 335 live postings).
MIN_SEEN_PER_SOURCE = {"reed": 30, "adzuna": 40}
MIN_ACTIVE = 100
MAX_DB_MB = 400  # Supabase free tier stops at 500 MB


def database_figures(conn):
    seen = dict(conn.execute(
        "select source, count(*) from postings "
        "where last_seen > now() - interval '26 hours' group by source"
    ).fetchall())
    new = conn.execute(
        "select count(*) from postings where first_seen > now() - interval '26 hours'"
    ).fetchone()[0]
    active = conn.execute("select count(*) from postings where is_active").fetchone()[0]
    db_mb = conn.execute("select pg_database_size(current_database()) / 1024.0 / 1024.0").fetchone()[0]
    return seen, new, active, float(db_mb)


def site_responds():
    try:
        r = requests.get(SITE_URL, timeout=30)
        return r.status_code == 200 and "UK BI Job Tracker" in r.text
    except requests.RequestException:
        return False


def public_api_works():
    """The site reads public_postings with the public key. Check that path returns rows."""
    url, key = os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_PUBLISHABLE_KEY")
    if not url or not key:
        return None  # not configured: reported, but not a failure
    try:
        r = requests.get(
            f"{url}/rest/v1/public_postings?select=posting_id&limit=1",
            headers={"apikey": key, "Authorization": f"Bearer {key}"},
            timeout=30,
        )
        return r.status_code == 200 and len(r.json()) == 1
    except (requests.RequestException, ValueError):
        return False


def run_checks(seen, new, active, db_mb, site_ok, api_ok):
    """Return a list of (check, value, passed). passed is None for 'not checked'."""
    rows = []
    for source, minimum in MIN_SEEN_PER_SOURCE.items():
        n = seen.get(source, 0)
        rows.append((f"{source.title()} postings seen in last 26 hours (min {minimum})", n, n >= minimum))
    rows.append(("New postings in last 26 hours", new, True))  # for information only
    rows.append((f"Live postings (min {MIN_ACTIVE})", active, active >= MIN_ACTIVE))
    rows.append((f"Database size, MB (max {MAX_DB_MB})", round(db_mb, 1), db_mb <= MAX_DB_MB))
    rows.append(("Live site responds", "yes" if site_ok else "no", site_ok))
    rows.append(("Public data API returns rows",
                 "not configured" if api_ok is None else ("yes" if api_ok else "no"), api_ok))
    return rows


def report(rows):
    lines = ["## Pipeline health", "", "| Check | Value | Result |", "| --- | --- | --- |"]
    for check, value, passed in rows:
        result = "not checked" if passed is None else ("OK" if passed else "**PROBLEM**")
        lines.append(f"| {check} | {value} | {result} |")
    text = "\n".join(lines) + "\n"
    print(text)
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as f:
            f.write(text)


def main():
    load_dotenv()
    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
        seen, new, active, db_mb = database_figures(conn)
    rows = run_checks(seen, new, active, db_mb, site_responds(), public_api_works())
    report(rows)
    problems = [check for check, _, passed in rows if passed is False]
    if problems:
        print("Problems found: " + "; ".join(problems))
        sys.exit(1)
    print("All checks passed.")


if __name__ == "__main__":
    main()

"""First test call: one page of UK 'data analyst' jobs from Adzuna.

Run from the repo root:
    python -m scripts.test_adzuna

Uses 1 of your 250 daily Adzuna calls.
"""

import json
from pathlib import Path

from dotenv import load_dotenv

from pipeline.sources.adzuna import search

load_dotenv()  # reads .env in the repo root

data = search("data analyst", page=1, results_per_page=20)
jobs = data.get("results", [])

print(f"Adzuna says there are {data.get('count', '?')} matching UK jobs in total.")
print(f"This page returned {len(jobs)}.\n")

for job in jobs[:10]:
    title = job.get("title")
    company = job.get("company", {}).get("display_name")
    location = job.get("location", {}).get("display_name")
    low, high = job.get("salary_min"), job.get("salary_max")
    predicted = " (estimated)" if str(job.get("salary_is_predicted")) == "1" else ""
    salary = f"£{low:,.0f} to £{high:,.0f}{predicted}" if low and high else "no salary"
    print(f"- {title} | {company} | {location} | {salary}")

# How long are the descriptions? This shows why Reed matters for skill tagging.
lengths = [len(job.get("description", "")) for job in jobs]
if lengths:
    print(f"\nDescription length: shortest {min(lengths)}, longest {max(lengths)} characters.")

# Save the raw response so we can study every field before designing the tables.
out = Path("data/sample_adzuna.json")
out.parent.mkdir(exist_ok=True)
out.write_text(json.dumps(data, indent=2), encoding="utf-8")
print(f"Raw response saved to {out}")

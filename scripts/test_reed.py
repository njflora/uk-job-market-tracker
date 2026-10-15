"""First test call to Reed: one page of UK 'data analyst' jobs, plus one full description.

Run from the repo root:
    python -m scripts.test_reed

Makes 2 calls: 1 search + 1 details.
"""

import json
import re
from pathlib import Path

from dotenv import load_dotenv

from pipeline.sources.reed import details, search

load_dotenv()

data = search("data analyst", results_to_take=20)
jobs = data.get("results", [])

print(f"Reed says there are {data.get('totalResults', '?')} matching UK jobs in total.")
print(f"This page returned {len(jobs)}.\n")

for job in jobs[:10]:
    low, high = job.get("minimumSalary"), job.get("maximumSalary")
    salary = f"£{low:,.0f} to £{high:,.0f}" if low and high else "no salary shown"
    print(f"- {job.get('jobTitle')} | {job.get('employerName')} | {job.get('locationName')} | {salary}")

if not jobs:
    raise SystemExit("No jobs returned; check the key in .env.")

# Compare the search snippet with the full description for the first job.
first = jobs[0]
full = details(first["jobId"])
snippet = first.get("jobDescription", "")
full_text = re.sub(r"<[^>]+>", " ", full.get("jobDescription", ""))  # strip HTML tags
full_text = re.sub(r"\s+", " ", full_text).strip()

print(f"\nFirst job: {first.get('jobTitle')}")
print(f"Search snippet length:   {len(snippet)} characters")
print(f"Full description length: {len(full_text)} characters")
print(f"Fields in the details record: {sorted(full.keys())}")

out = Path("data")
out.mkdir(exist_ok=True)
(out / "sample_reed_search.json").write_text(json.dumps(data, indent=2), encoding="utf-8")
(out / "sample_reed_details.json").write_text(json.dumps(full, indent=2), encoding="utf-8")
print("\nRaw responses saved to data/sample_reed_search.json and data/sample_reed_details.json")

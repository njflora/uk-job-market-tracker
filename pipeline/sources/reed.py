"""Fetch job postings from the Reed Jobseeker API (UK).

Docs: https://www.reed.co.uk/developers/jobseeker
Auth: the API key is the Basic Auth username; the password is left empty.
Search returns up to 100 jobs per call with a shortened description.
The details endpoint returns one job with its FULL description.
No rate limit is published, so we pause between calls to be polite.
"""

import os
import time

import requests

BASE_URL = "https://www.reed.co.uk/api/1.0"
PAUSE_SECONDS = 1


def _auth():
    return (os.environ["REED_API_KEY"], "")


def search(keywords, results_to_take=100, results_to_skip=0, **filters):
    """Return one page of Reed search results as a dict (raw JSON).

    Extra filters are passed straight through, e.g. locationName="Manchester".
    """
    params = {
        "keywords": keywords,
        "resultsToTake": results_to_take,
        "resultsToSkip": results_to_skip,
        **filters,
    }
    response = requests.get(f"{BASE_URL}/search", params=params, auth=_auth(), timeout=30)
    response.raise_for_status()
    return response.json()


def details(job_id):
    """Return one job's full record, including the complete description."""
    response = requests.get(f"{BASE_URL}/jobs/{job_id}", auth=_auth(), timeout=30)
    response.raise_for_status()
    return response.json()


def search_all(keywords, max_pages=3, **filters):
    """Fetch several pages of search results, 100 at a time."""
    results = []
    for page in range(max_pages):
        data = search(keywords, results_to_skip=page * 100, **filters)
        batch = data.get("results", [])
        results.extend(batch)
        if len(batch) < 100:
            break
        time.sleep(PAUSE_SECONDS)
    return results

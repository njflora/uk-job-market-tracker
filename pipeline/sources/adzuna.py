"""Fetch job postings from the Adzuna API (UK).

Docs: https://developer.adzuna.com/docs/search
Free limits: 25 calls/min, 250/day, 1,000/week, 2,500/month.
"""

import os
import time

import requests

BASE_URL = "https://api.adzuna.com/v1/api/jobs/gb/search/{page}"


def search(what, page=1, results_per_page=50, max_days_old=None):
    """Return one page of Adzuna search results as a dict (raw JSON)."""
    params = {
        "app_id": os.environ["ADZUNA_APP_ID"],
        "app_key": os.environ["ADZUNA_APP_KEY"],
        "what": what,
        "results_per_page": results_per_page,
        "content-type": "application/json",
    }
    if max_days_old is not None:
        params["max_days_old"] = max_days_old

    response = requests.get(BASE_URL.format(page=page), params=params, timeout=30)
    response.raise_for_status()  # stops with a clear error on 401, 429 etc.
    return response.json()


def search_all(what, max_pages=3, **kwargs):
    """Fetch several pages, pausing between calls to stay under the rate limit."""
    results = []
    for page in range(1, max_pages + 1):
        data = search(what, page=page, **kwargs)
        batch = data.get("results", [])
        results.extend(batch)
        if len(batch) == 0:
            break
        time.sleep(3)  # 25 calls/min allowed; 3 seconds keeps us well under
    return results

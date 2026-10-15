"""Work out the UK region for Reed locations, which are a mix of towns and postcodes.

Uses postcodes.io (free, no key): https://postcodes.io
Results are cached for the run, so each place is looked up once.
If the lookup fails, the region is left empty rather than stopping the pipeline.
"""

import requests

from pipeline.tag.clean import canonical_region, is_postcode

API = "https://api.postcodes.io"
_cache = {}


def _region_from_record(record):
    """postcodes.io gives an English region, or only a country for Scotland, Wales and NI."""
    if not record:
        return None
    return canonical_region(record.get("region")) or canonical_region(record.get("country"))


def region_for(location):
    """Return one of the 12 UK regions for a Reed locationName, or None."""
    if not location:
        return None
    key = location.strip().lower()
    if key in _cache:
        return _cache[key]

    region = canonical_region(location)  # e.g. 'London' is already a region
    try:
        if region is None and is_postcode(location):
            r = requests.get(f"{API}/postcodes/{location.strip()}", timeout=15)
            if r.status_code == 200:
                region = _region_from_record(r.json().get("result"))
        elif region is None:
            r = requests.get(f"{API}/places", params={"q": location, "limit": 1}, timeout=15)
            if r.status_code == 200 and r.json().get("result"):
                region = _region_from_record(r.json()["result"][0])
    except requests.RequestException:
        region = None

    _cache[key] = region
    return region

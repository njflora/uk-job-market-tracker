"""Work out the region and town for Reed locations, which mix towns and postcodes.

Uses postcodes.io (free, no key): https://postcodes.io
Results are cached for the run, so each place is looked up once.
If a lookup fails, the region is left empty rather than stopping the pipeline.
"""

import requests

from pipeline.tag.clean import canonical_region, is_postcode, tidy

API = "https://api.postcodes.io"
_cache = {}


def _region_from_record(record):
    """postcodes.io gives an English region, or only a country for Scotland, Wales and NI."""
    if not record:
        return None
    return canonical_region(record.get("region")) or canonical_region(record.get("country"))


def place_for(location):
    """Return (region, town) for a Reed locationName. Either may be None.

    - Postcode 'M53EE'  -> ('North West', 'Salford')   town = the local authority
    - Town 'Exeter'     -> ('South West', 'Exeter')
    - 'London'          -> ('London', 'London')
    """
    if not location:
        return None, None
    key = location.strip().lower()
    if key in _cache:
        return _cache[key]

    region = canonical_region(location)
    town = None if is_postcode(location) else tidy(location)
    try:
        if is_postcode(location):
            r = requests.get(f"{API}/postcodes/{location.strip()}", timeout=15)
            if r.status_code == 200:
                record = r.json().get("result") or {}
                region = _region_from_record(record)
                town = tidy(record.get("admin_district"))
        elif region is None:
            r = requests.get(f"{API}/places", params={"q": location, "limit": 1}, timeout=15)
            if r.status_code == 200 and r.json().get("result"):
                region = _region_from_record(r.json()["result"][0])
    except requests.RequestException:
        pass

    _cache[key] = (region, town)
    return region, town


def region_for(location):
    """Kept for older callers: the region only."""
    return place_for(location)[0]

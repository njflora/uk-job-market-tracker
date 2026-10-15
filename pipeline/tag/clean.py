"""Small cleaning helpers used when mapping API records to the postings table.

Each rule here is documented in docs/FIELD_MAPPING.md.
"""

import html
import re
from datetime import datetime, timezone

# The 12 UK regions (ITL1), named the way the tracker will show them.
# Adzuna and postcodes.io each use slightly different names; both map here.
REGION_NAMES = {
    "london": "London",
    "south east": "South East", "south east england": "South East",
    "south west": "South West", "south west england": "South West",
    "east of england": "East of England", "eastern england": "East of England",
    "east midlands": "East Midlands",
    "west midlands": "West Midlands",
    "yorkshire and the humber": "Yorkshire and The Humber",
    "north west": "North West", "north west england": "North West",
    "north east": "North East", "north east england": "North East",
    "wales": "Wales",
    "scotland": "Scotland",
    "northern ireland": "Northern Ireland",
}

COMPANY_SUFFIXES = r"\b(ltd|limited|plc|llp|llc|inc|uk)\b"

UK_POSTCODE = re.compile(r"^[A-Z]{1,2}\d[A-Z\d]?\s?\d[A-Z]{2}$", re.IGNORECASE)


def tidy(text):
    """Trim and collapse repeated spaces. Returns None for empty values."""
    if text is None:
        return None
    text = re.sub(r"\s+", " ", str(text)).strip()
    return text or None


def normalise_key_part(text):
    """Lower-case, drop punctuation and extra spaces: used to build the dedup key."""
    text = (text or "").lower()
    text = re.sub(r"[^a-z0-9 ]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def normalise_company(name):
    """'Marshall Wolfe Ltd' and 'Marshall Wolfe' both become 'marshall wolfe'."""
    text = normalise_key_part(name)
    text = re.sub(COMPANY_SUFFIXES, " ", text)
    return re.sub(r"\s+", " ", text).strip()


def dedup_key(company, title, town):
    """The plan's dedup rule: same company + title + location = same job."""
    return "|".join([normalise_company(company), normalise_key_part(title), normalise_key_part(town)])


def strip_html(text):
    """Reed descriptions are HTML; keep the words only."""
    if not text:
        return None
    text = re.sub(r"<[^>]+>", " ", text)
    return tidy(html.unescape(text))


def parse_reed_date(text):
    """Reed dates are day/month/year text, e.g. '07/10/2026'."""
    if not text:
        return None
    return datetime.strptime(text, "%d/%m/%Y").replace(tzinfo=timezone.utc)


def parse_iso_date(text):
    """Adzuna dates are ISO 8601, e.g. '2026-10-07T20:58:46Z'."""
    if not text:
        return None
    return datetime.fromisoformat(text.replace("Z", "+00:00"))


def canonical_region(name):
    """Map any source's region name to one of the 12 UK regions, or None."""
    return REGION_NAMES.get(normalise_key_part(name)) if name else None


def is_postcode(text):
    return bool(text) and bool(UK_POSTCODE.match(text.strip()))

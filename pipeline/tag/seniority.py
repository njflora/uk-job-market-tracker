"""Tag a posting's seniority from its job title.

Titles only: descriptions mention several levels ("you will support senior analysts"),
so they would give wrong answers. Most titles name no level; those stay None
and show as "Not stated" on the site. See docs/FIELD_MAPPING.md, rule 10.

Checked in this order, so "Senior Lead" counts as Lead and "Graduate Senior" as Senior:
  Lead   - lead, principal, head of
  Senior - senior, snr, sr
  Entry  - junior, jnr, graduate, entry level, trainee, apprentice, intern, placement
  Mid    - mid level, intermediate
"""

import re

LEVELS = [
    ("Lead", re.compile(r"\b(lead|principal|head\s+of)\b", re.I)),
    ("Senior", re.compile(r"\b(senior|snr|sr)\b\.?", re.I)),
    ("Entry", re.compile(
        r"\b(junior|jnr|graduate|grad|entry[\s-]?level|trainee|apprentice(ship)?|intern(ship)?|placement)\b",
        re.I,
    )),
    ("Mid", re.compile(r"\b(mid[\s-]?level|mid|intermediate)\b", re.I)),
]


def seniority_for(title):
    """Return 'Lead', 'Senior', 'Entry', 'Mid' or None."""
    if not title:
        return None
    for level, pattern in LEVELS:
        if pattern.search(title):
            return level
    return None

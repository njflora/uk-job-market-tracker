"""Decide whether a job title is in scope, and which role family it belongs to.

In scope: Data Analyst, BI Analyst / Developer / Specialist, Business Intelligence
Analyst / Developer / Specialist, Power BI Developer, Reporting / MI Analyst, Insight Analyst.
Out of scope: everything else (Data Engineer, Data Scientist, Business Analyst, ...).
Training-course adverts posing as jobs are flagged separately so they can be counted.
"""

import re

# Order matters: the first pattern that matches wins.
ROLE_FAMILIES = [
    ("Power BI Developer", r"\bpower\s?bi\b.*\b(developer|analyst|specialist|consultant)\b"),
    ("BI Developer", r"\b(bi|business intelligence)\b.*\b(developer|engineer)\b"),
    ("BI Specialist", r"\b(bi|business intelligence)\b.*\bspecialist\b"),
    ("BI Analyst", r"\b(bi|business intelligence)\b.*\banalyst\b"),
    ("Reporting / MI Analyst", r"\b(reporting|mi|management information)\b.*\banalyst\b"),
    ("Insight Analyst", r"\binsights?\b.*\banalyst\b"),
    ("Data Analyst", r"\bdata\b.*\banalyst\b"),
]

# Adverts for paid courses dressed up as jobs.
TRAINING_AD = r"no experience (needed|required)|placement programme|career change programme|retrain"


def classify_title(title):
    """Return (role_family, is_training_ad). role_family is None when out of scope."""
    text = (title or "").lower()
    is_training_ad = re.search(TRAINING_AD, text) is not None
    for family, pattern in ROLE_FAMILIES:
        if re.search(pattern, text):
            return family, is_training_ad
    return None, is_training_ad

"""Decide whether a job is in scope, and which role family it belongs to.

In scope: Data Analyst, BI Analyst / Developer / Specialist, Business Intelligence
Analyst / Developer / Specialist, Power BI Developer, Reporting / MI Analyst, Insight Analyst.
Out of scope: everything else (Data Engineer, Data Scientist, Business Analyst,
finance and risk reporting roles, ...).
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

# Finance and risk roles that use "reporting" or "insight" in the title (excluded by scope decision),
# e.g. "Financial Reporting & Control Analyst", "FP&A Insights Analyst".
FINANCE_REPORTING = r"\b(financial|finance|fp\s?&\s?a|risk|regulatory|treasury|accounting)\b"
FINANCE_SENSITIVE = {"Reporting / MI Analyst", "Insight Analyst"}

# Adverts for paid courses dressed up as jobs: by title wording ...
TRAINING_AD = r"no experience (needed|required)|placement programme|career change programme|retrain"
# ... and by advertiser, because their titles vary ("Trainee Data Analyst", "Data Analyst Trainee").
TRAINING_PROVIDERS = {"itol recruit", "it online learning"}


def _clean_company(name):
    text = re.sub(r"[^a-z0-9 ]+", " ", (name or "").lower())
    text = re.sub(r"\b(ltd|limited|plc|llp|uk)\b", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def classify_title(title, company=None):
    """Return (role_family, is_training_ad). role_family is None when out of scope."""
    text = (title or "").lower()
    is_training_ad = (
        re.search(TRAINING_AD, text) is not None
        or _clean_company(company) in TRAINING_PROVIDERS
    )
    for family, pattern in ROLE_FAMILIES:
        if re.search(pattern, text):
            if family in FINANCE_SENSITIVE and re.search(FINANCE_REPORTING, text):
                return None, is_training_ad
            return family, is_training_ad
    return None, is_training_ad

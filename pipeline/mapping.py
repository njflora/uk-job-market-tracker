"""Turn one raw API record into a row for the postings table.

Follows docs/FIELD_MAPPING.md column by column.
"""

from pipeline.tag.clean import (
    canonical_region, dedup_key, parse_iso_date, parse_reed_date, strip_html, tidy,
)
from pipeline.tag.regions import place_for


def from_reed(search_row, details_row, role_family):
    """Reed: search gives `applications`; details gives the full description and yearly salary."""
    d = details_row or {}
    company = tidy(search_row.get("employerName"))
    title = tidy(search_row.get("jobTitle"))
    location = tidy(search_row.get("locationName"))
    region, town = place_for(location)
    return {
        "dedup_key": dedup_key(company, title, region, town),
        "source": "reed",
        "source_job_id": str(search_row["jobId"]),
        "company": company,
        "title": title,
        "location_text": location,
        "town": town,
        "region": region,
        "seniority": None,  # tagged in a later step
        "salary_min": d.get("yearlyMinimumSalary"),
        "salary_max": d.get("yearlyMaximumSalary"),
        "salary_period": d.get("salaryType"),
        "salary_is_predicted": False,
        "description": strip_html(d.get("jobDescription")) or strip_html(search_row.get("jobDescription")),
        "url": search_row.get("jobUrl") or d.get("jobUrl"),
        "posted_at": parse_reed_date(d.get("datePosted") or search_row.get("date")),
        "expires_at": parse_reed_date(d.get("expirationDate") or search_row.get("expirationDate")),
        "contract_type": d.get("contractType"),
        "full_time": d.get("fullTime"),
        "applications": search_row.get("applications"),
        "role_family": role_family,
    }


def from_adzuna(row, role_family):
    """Adzuna: one record per job; description is a 500-character snippet."""
    area = (row.get("location") or {}).get("area") or []
    company = tidy((row.get("company") or {}).get("display_name"))
    title = tidy(row.get("title"))
    town = area[-1] if len(area) > 1 else None
    region = canonical_region(area[1]) if len(area) > 1 else None
    return {
        "dedup_key": dedup_key(company, title, region, town),
        "source": "adzuna",
        "source_job_id": str(row["id"]),
        "company": company,
        "title": title,
        "location_text": tidy((row.get("location") or {}).get("display_name")),
        "town": town,
        "region": region,
        "seniority": None,
        "salary_min": row.get("salary_min"),
        "salary_max": row.get("salary_max"),
        "salary_period": "per annum" if row.get("salary_min") else None,
        "salary_is_predicted": str(row.get("salary_is_predicted")) == "1",
        "description": tidy(row.get("description")),
        "url": row.get("redirect_url"),
        "posted_at": parse_iso_date(row.get("created")),
        "expires_at": None,
        "contract_type": (row.get("contract_type") or "").title() or None,  # match Reed's 'Permanent'
        "full_time": {"full_time": True, "part_time": False}.get(row.get("contract_time")),
        "applications": None,
        "role_family": role_family,
    }

"""Seniority from job titles. Most titles name no level and stay None."""

import pytest

from pipeline.tag.seniority import seniority_for


@pytest.mark.parametrize("title, level", [
    ("Senior BI Analyst", "Senior"),
    ("Snr Data Analyst", "Senior"),
    ("Sr. Power BI Developer", "Senior"),
    ("Lead Data Analyst", "Lead"),
    ("Principal Insight Analyst", "Lead"),
    ("Head of Business Intelligence", "Lead"),
    ("Senior Lead BI Developer", "Lead"),
    ("Junior Data Analyst", "Entry"),
    ("Graduate Data Analyst", "Entry"),
    ("Data Analyst Apprenticeship", "Entry"),
    ("Trainee MI Analyst", "Entry"),
    ("Data Analyst - Entry Level", "Entry"),
    ("Mid-Level BI Developer", "Mid"),
    ("Intermediate Data Analyst", "Mid"),
    ("Data Analyst", None),
    ("BI Analyst - Leading retailer", None),
    ("Internal Reporting Analyst", None),
    ("", None),
    (None, None),
])
def test_seniority(title, level):
    assert seniority_for(title) == level

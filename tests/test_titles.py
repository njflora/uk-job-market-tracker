"""Title scope: which jobs are kept, and which role family they get."""

import pytest

from pipeline.tag.titles import classify_title


@pytest.mark.parametrize("title, family", [
    ("Data Analyst", "Data Analyst"),
    ("Senior Data Analyst", "Data Analyst"),
    ("BI Analyst", "BI Analyst"),
    ("Business Intelligence Analyst", "BI Analyst"),
    ("BI Developer", "BI Developer"),
    ("Business Intelligence Engineer", "BI Developer"),
    ("BI Specialist", "BI Specialist"),
    ("Power BI Developer", "Power BI Developer"),
    ("PowerBI Analyst", "Power BI Developer"),
    ("Reporting Analyst", "Reporting / MI Analyst"),
    ("MI Analyst", "Reporting / MI Analyst"),
    ("Customer Insight Analyst", "Insight Analyst"),
])
def test_in_scope(title, family):
    assert classify_title(title) == (family, False)


@pytest.mark.parametrize("title", [
    "Data Engineer",
    "Data Scientist",
    "Business Analyst",
    "Financial Reporting Analyst",
    "FP&A Insights Analyst",
    "Risk Reporting Analyst",
])
def test_out_of_scope(title):
    assert classify_title(title)[0] is None


def test_training_ad_by_wording():
    assert classify_title("Data Analyst - No Experience Needed")[1] is True


@pytest.mark.parametrize("company", ["ITOL Recruit", "IT Online Learning Ltd"])
def test_training_ad_by_advertiser(company):
    assert classify_title("Trainee Data Analyst", company)[1] is True


def test_real_employer_is_not_a_training_ad():
    assert classify_title("Data Analyst", "NHS Digital")[1] is False

"""Cleaning rules: company names, dedup keys, dates and regions."""

from datetime import datetime, timezone

from pipeline.tag.clean import (
    canonical_region, dedup_key, is_postcode, normalise_company, parse_iso_date,
    parse_reed_date, strip_html,
)


def test_company_suffixes_dropped():
    assert normalise_company("Marshall Wolfe Ltd") == normalise_company("Marshall Wolfe")


def test_dedup_key_uses_region_not_town():
    a = dedup_key("Acme Ltd", "Data Analyst", "North West", "Liverpool")
    b = dedup_key("Acme", "Data Analyst", "North West", "Manchester")
    assert a == b


def test_dedup_key_falls_back_to_town():
    assert dedup_key("Acme", "Data Analyst", None, "Leeds").endswith("|leeds")


def test_reed_date():
    assert parse_reed_date("07/10/2026") == datetime(2026, 10, 7, tzinfo=timezone.utc)


def test_iso_date():
    assert parse_iso_date("2026-10-07T20:58:46Z") == datetime(2026, 10, 7, 20, 58, 46, tzinfo=timezone.utc)


def test_strip_html():
    assert strip_html("<p>SQL &amp; <b>Power BI</b></p>") == "SQL & Power BI"


def test_region_names():
    assert canonical_region("North West England") == "North West"
    assert canonical_region("Atlantis") is None


def test_postcode():
    assert is_postcode("M1 1AE")
    assert not is_postcode("Manchester")

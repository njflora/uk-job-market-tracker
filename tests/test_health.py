"""The health check flags the right problems (no database or network needed)."""

from pipeline.health import run_checks


def failed(rows):
    return [check for check, _, passed in rows if passed is False]


def test_healthy_day_passes():
    rows = run_checks({"reed": 129, "adzuna": 206}, 12, 335, 40.0, True, True)
    assert failed(rows) == []


def test_missing_source_fails():
    rows = run_checks({"reed": 129}, 0, 335, 40.0, True, True)
    assert len(failed(rows)) == 1 and "Adzuna" in failed(rows)[0]


def test_database_too_big_fails():
    assert any("Database" in c for c in failed(run_checks({"reed": 129, "adzuna": 206}, 0, 335, 450.0, True, True)))


def test_site_down_fails():
    assert any("site" in c for c in failed(run_checks({"reed": 129, "adzuna": 206}, 0, 335, 40.0, False, True)))


def test_api_not_configured_is_not_a_failure():
    assert failed(run_checks({"reed": 129, "adzuna": 206}, 0, 335, 40.0, True, None)) == []

"""Tag each posting with the skills and tools its title and description mention.

The list came from a scan of 339 real postings (15 Oct 2026). See docs/SKILLS.md.
Patterns are case-insensitive unless marked otherwise. Order inside a category does not matter.

Adzuna descriptions are 500-character snippets, so their tags are incomplete:
those rows get skills_from_snippet = true, and market-wide skill figures use Reed rows only.
"""

import re

# (skill, category, pattern, case_sensitive)
SKILLS = [
    # Languages
    ("SQL", "Languages", r"\bsql\b", False),
    ("T-SQL", "Languages", r"\bt-?sql\b", False),
    ("Python", "Languages", r"\bpython\b", False),
    ("R", "Languages", r"(?<![&\w])R(?![&\w])", True),  # not "A&R" or "R&Rs"
    ("DAX", "Languages", r"\bdax\b", False),
    ("VBA", "Languages", r"\bvba\b|\bmacros?\b", False),
    # BI tools
    ("Power BI", "BI tools", r"power\s?bi|\bpbi\b", False),
    ("Power Query", "BI tools", r"power\s?query", False),
    ("Excel", "BI tools", r"\b(?:Excel|EXCEL)\b(?!\s+(?:in|at|as|across)\b)", True),  # not "excel in"
    ("Tableau", "BI tools", r"\btableau\b", False),
    ("Looker", "BI tools", r"\blooker\b", False),
    ("Qlik", "BI tools", r"\bqlik", False),
    ("SSRS", "BI tools", r"\bssrs\b", False),
    ("Google Analytics", "BI tools", r"google analytics|\bga4\b", False),
    # Microsoft data platform
    ("Azure", "Microsoft data platform", r"\bazure\b", False),
    ("Microsoft Fabric", "Microsoft data platform", r"(?i:microsoft fabric)|\bFabric\b", True),  # not "the fabric of"
    ("Synapse", "Microsoft data platform", r"\bsynapse\b", False),
    ("Data Factory", "Microsoft data platform", r"data factory|\badf\b", False),
    ("SQL Server", "Microsoft data platform", r"sql server|\bmssql\b", False),
    ("SSIS", "Microsoft data platform", r"\bssis\b", False),
    ("SSAS", "Microsoft data platform", r"\bssas\b", False),
    ("Power Automate", "Microsoft data platform", r"power\s?automate", False),
    ("Power Apps", "Microsoft data platform", r"power\s?apps", False),
    ("SharePoint", "Microsoft data platform", r"sharepoint", False),
    # Cloud and data platforms
    ("Databricks", "Cloud and data platforms", r"databricks", False),
    ("Snowflake", "Cloud and data platforms", r"snowflake", False),
    ("AWS", "Cloud and data platforms", r"\baws\b|amazon web services|redshift", False),
    ("Google Cloud", "Cloud and data platforms", r"\bgcp\b|google cloud|bigquery", False),
    ("PostgreSQL", "Cloud and data platforms", r"postgres", False),
    ("MySQL", "Cloud and data platforms", r"\bmysql\b", False),
    ("dbt", "Cloud and data platforms", r"\bdbt\b", False),
    ("Airflow", "Cloud and data platforms", r"airflow", False),
    ("Spark", "Cloud and data platforms", r"\bSpark\b|(?i:pyspark|apache spark)", True),  # not "spark ideas"
    ("Alteryx", "Cloud and data platforms", r"alteryx", False),
    ("SAS", "Cloud and data platforms", r"\bsas\b", False),
    ("SPSS", "Cloud and data platforms", r"\bspss\b", False),
    # Concepts
    ("Data modelling", "Concepts", r"data model", False),
    ("Data warehousing", "Concepts", r"data\s?warehous", False),
    ("ETL", "Concepts", r"\betl\b|\belt\b", False),
    ("Statistics", "Concepts", r"statistic", False),
    ("Machine learning", "Concepts", r"machine learning|\bml\b", False),
    ("AI", "Concepts", r"\bai\b|artificial intelligence|\bgenai\b|\bllms?\b", False),
    # Ways of working
    ("Agile", "Ways of working", r"\bagile\b|\bscrum\b", False),
    ("Jira", "Ways of working", r"\bjira\b", False),
    ("Git", "Ways of working", r"\bgit\b|github|gitlab", False),
    # Business apps
    ("Salesforce", "Business apps", r"salesforce", False),
    ("Dynamics 365", "Business apps", r"(?:microsoft )?dynamics\s?(?:365|crm|ax|nav|f&o|bc)|microsoft dynamics", False),  # not "team dynamics"
    ("SAP", "Business apps", r"\bsap\b", False),
]

_COMPILED = [
    (name, re.compile(pattern, 0 if case_sensitive else re.IGNORECASE))
    for name, _category, pattern, case_sensitive in SKILLS
]


def find_skills(text):
    """Return the set of skill names mentioned in the text."""
    text = text or ""
    return {name for name, regex in _COMPILED if regex.search(text)}


def tag_all(conn):
    """Re-tag every posting from scratch. Fast (a few hundred rows), and picks up list changes.

    Returns (postings_tagged, links_written).
    """
    for name, category, _pattern, _cs in SKILLS:
        conn.execute(
            "insert into skills (name, category) values (%s, %s) "
            "on conflict (name) do update set category = excluded.category",
            (name, category),
        )
    skill_ids = dict(conn.execute("select name, skill_id from skills").fetchall())

    rows = conn.execute("select posting_id, title, description from postings").fetchall()
    links = [
        (posting_id, skill_ids[name])
        for posting_id, title, description in rows
        for name in find_skills(f"{title or ''}\n{description or ''}")
    ]
    conn.execute("delete from posting_skills")
    with conn.cursor() as cur:
        cur.executemany("insert into posting_skills (posting_id, skill_id) values (%s, %s)", links)
    conn.execute("update postings set skills_from_snippet = (source = 'adzuna')")
    return len(rows), len(links)

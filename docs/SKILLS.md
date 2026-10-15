# Skills tagging

How skills are found in each posting, and why the figures use Reed postings only.
Code: `pipeline/tag/skills.py`. Database view: `skill_demand`.

## How the list was chosen

On 15 October 2026 a SQL scan checked 48 candidate skills against 339 active postings (130 Reed, 209 Adzuna).
Every candidate was kept. Low counts cost nothing to store, and they may grow as data builds up.

## Why figures use Reed only

Adzuna returns a 500-character snippet of each advert. The skills section is usually further down, so it is cut off.

| Skill | Reed (full text) | Adzuna (snippet) |
| --- | --- | --- |
| SQL | 77% | 4% |
| Power BI | 73% | 12% |
| Data modelling | 38% | 2% |
| Excel | 31% | 1% |
| Python | 31% | 0.5% |
| Tableau | 25% | 1% |
| DAX | 23% | 1% |
| Microsoft Fabric | 15% | 1% |

These scan figures use the first, looser patterns. Excel, Fabric and Spark may be a little lower once the tightened rules below apply; the `skill_demand` view gives the current figures.

Adzuna postings are still tagged, but they carry `skills_from_snippet = true`. The `skill_demand` view and any market-wide figure use full-text postings only. The CV matcher will treat an Adzuna posting's skills as partly unknown.

## The list (48 skills, 7 categories)

| Category | Skills |
| --- | --- |
| Languages | SQL, T-SQL, Python, R, DAX, VBA |
| BI tools | Power BI, Power Query, Excel, Tableau, Looker, Qlik, SSRS, Google Analytics |
| Microsoft data platform | Azure, Microsoft Fabric, Synapse, Data Factory, SQL Server, SSIS, SSAS, Power Automate, Power Apps, SharePoint |
| Cloud and data platforms | Databricks, Snowflake, AWS, Google Cloud, PostgreSQL, MySQL, dbt, Airflow, Spark, Alteryx, SAS, SPSS |
| Concepts | Data modelling, Data warehousing, ETL, Statistics, Machine learning, AI |
| Ways of working | Agile, Jira, Git |
| Business apps | Salesforce, Dynamics 365, SAP |

## Patterns that needed care

| Skill | Problem | Rule |
| --- | --- | --- |
| R | A single letter matched "A&R" and "R&Rs" (2 of 10 hits) | Capital R only, and not next to "&" or another letter |
| Excel | "You will excel in..." | Capital "Excel", and not followed by in / at / as / across |
| Dynamics 365 | "team dynamics" | Must say Dynamics 365, CRM, AX, NAV, F&O, BC or Microsoft Dynamics |
| Microsoft Fabric | "the fabric of our business" | "Microsoft Fabric", or capital "Fabric" |
| Spark | "spark ideas" | Capital "Spark", PySpark or Apache Spark |

Each posting's title and description are both searched, so "Power BI Developer" is tagged Power BI even if the text never repeats it.
Tags are rebuilt from scratch on every run, so a change to the list applies to all postings the next morning.

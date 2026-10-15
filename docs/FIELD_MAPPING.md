# Field mapping: Reed and Adzuna to `postings`

Based on the first samples (15 October 2026): 20 Reed search results, 1 Reed details record, 20 Adzuna results.

## What the samples showed

| Finding | Reed | Adzuna |
| --- | --- | --- |
| Jobs matching "data analyst" (API total) | 1,973 | 1,862 |
| In-scope titles in the 20-row sample | 2 of 20 | 11 of 20 (plus 9 training adverts) |
| Description | Full text from details (1,490 chars vs 453 in search) | Always cut at 500 chars |
| Locations | 7 of 20 are postcodes (e.g. `M53EE`) | Clean hierarchy, e.g. `['UK', 'North West England', 'Merseyside', 'Liverpool']` |
| Salary | `yearlyMinimumSalary`/`yearlyMaximumSalary` + `salaryType` | 6 of 20 are Adzuna estimates (`salary_is_predicted = 1`), always min = max |
| Dates | `dd/mm/yyyy` text | ISO 8601 (`2026-10-07T20:58:46Z`) |
| Employer names | Trailing spaces (`"Matchtech "`) | Clean, but with suffixes (`"Marshall Wolfe Ltd"`) |

The same job appeared in both sources: Lead Data Analyst at Marshall Wolfe, London. Reed lists £70,000 to £80,000; Adzuna lists £70,000.

## Column mapping

| `postings` column | Reed field | Adzuna field | Rule |
| --- | --- | --- | --- |
| `source_job_id` | `jobId` | `id` | Stored as text |
| `title` | `jobTitle` | `title` | Trim spaces |
| `company_id` | `employerName` | `company.display_name` | Trim, lower-case, drop Ltd / Limited / PLC / LLP and punctuation, then look up or insert in `companies` |
| `location_text` | `locationName` | `location.display_name` | As given |
| `region` | Postcode or town lookup | `location.area[1]` | Reed needs a lookup (postcodes.io is free); Adzuna has it already |
| `towns` | postcode → local authority (postcodes.io), else `locationName` | `location.area[-1]` | Every town the posting was seen in; used for the town filter |
| `salary_min` / `salary_max` | `yearlyMinimumSalary` / `yearlyMaximumSalary` (details) | `salary_min` / `salary_max` | Always yearly figures; never use Reed's raw min/max for hourly or daily rates |
| `salary_period` | `salaryType` | `per annum` | |
| `salary_is_predicted` | always `false` | `salary_is_predicted == 1` | Estimates are labelled in the tracker, never shown as the employer's figure |
| `description` | `jobDescription` (details), HTML stripped | `description` (snippet) | Skill tagging trusts Reed text more |
| `url` | `jobUrl` | `redirect_url` | Every listing links out to the original |
| `posted_at` | `datePosted` / `date` | `created` | Parse Reed dates as day/month/year |
| `expires_at` | `expirationDate` | none | Adzuna jobs expire when they stop appearing |
| `contract_type` | `contractType` (details) | none | Permanent / Contract / Temporary |
| `full_time` | `fullTime` (details) | none | |
| `applications` | `applications` (search) | none | Use the search value; details returned `applicationCount = 0` for a job with 118 in search |
| `role_family` | from `jobTitle` | from `title` | `pipeline/tag/titles.py`, e.g. `BI Developer` |
| `skills_from_snippet` | `false` | `true` | Adzuna text is a 500-character snippet, so its skill tags are incomplete |

## Rules decided so far

1. **Title scope:** Data Analyst, BI Analyst, BI Developer, Business Intelligence Analyst / Developer / Specialist, Power BI Developer, Reporting / MI Analyst, Insight Analyst. Reporting titles that also say financial, finance, risk, regulatory, treasury or accounting are out. Code: `pipeline/tag/titles.py`.
2. **Training adverts:** excluded, and never stored. Caught by title wording ("No Experience Needed", "Placement Programme") and by advertiser (ITOL Recruit, IT Online Learning), because their titles vary. ITOL alone made up at least 118 of the first 548 rows.
3. **Cross-source duplicates:** when Reed and Adzuna hold the same job, the Reed row wins, because it has the full description and the employer's own salary.
4. **Extra Reed fields:** `contract_type`, `full_time` and `applications` are loaded (migration `002`). Applications measures competition per job.
5. **Dedup key = company | title | region** (changed 15 Oct 2026, was town). One job is often listed under several towns or postcodes (e.g. Halton Housing: "Cronton, Widnes", "Bold Heath, Widnes", "Widnes"). Every town is kept in `towns`, so filtering by town still works. Trade-off: the same role at the same company in two towns of one region becomes one row. If the region is unknown, the town is used instead.
6. **Regions:** both sources map to the 12 UK regions (`pipeline/tag/clean.py`). Adzuna uses `location.area[1]`; Reed locations are looked up on postcodes.io (`pipeline/tag/regions.py`). A failed lookup leaves the region empty instead of stopping the run.
7. **Inactive postings:** a Reed job is closed after its `expires_at`; an Adzuna job is closed when it has not been seen for 3 days. Rows are never deleted.
8. **Rebuilds:** `python -m pipeline.rebuild` replays `raw_postings` with the current rules. No Reed or Adzuna calls; first-seen and last-seen dates are kept.
9. **Skills:** 48 skills in 7 categories, tagged from title + description on every run (`pipeline/tag/skills.py`, `docs/SKILLS.md`). Adzuna rows are flagged `skills_from_snippet`; market-wide skill figures use Reed rows only.

## Open questions

- **postcodes.io town field:** regions are confirmed by the first real load (516 of 548 rows had one). The town for a Reed postcode comes from `admin_district`, which is tested only with fake responses so far.

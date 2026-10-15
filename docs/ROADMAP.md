# Roadmap

How this project could continue after the v1 tracker and v2 CV matcher. Each phase builds on the one before it and produces something that works on its own.

## Where it stands (15 October 2026)

| Done | What it does |
| --- | --- |
| Pipeline | Daily ingest from Reed and Adzuna, title filter, cleaning, region and town mapping, deduplication |
| Skills | 48 skills in 7 categories, tagged from full-text postings |
| v1 tracker | Public, filterable table and skill-demand chart on GitHub Pages |
| v2 matcher | In-browser CV reading, role-archetype scores, best-match job sorting |
| Security | Row level security: the public key can only read three views |
| Upkeep | Tests on every push, weekly backup, monthly keep-alive, seniority filter |

## Phase 1: Harden the foundations (done)

The goal is a pipeline that can run untouched for months.

- ~~Store raw data only when it changes~~ (done 15 Oct 2026).
- ~~Weekly backup~~ (done 15 Oct 2026).
- ~~Automatic tests~~ (done 15 Oct 2026). Python and JavaScript share one list of skill test cases, so the two copies of the rules cannot drift apart.
- ~~Seniority tagging~~ (done 15 Oct 2026). From titles only; most titles name no level and show as "Not stated".
- ~~Keep-alive~~ (done 15 Oct 2026). A monthly job adds an empty commit when the repository has been quiet for 45 days.

Still to prove: 30 days of daily runs with no failures (see the success measures below).

## Phase 2: Gap-to-project library (2 to 3 sessions)

The feature none of the ten tools reviewed in the plan offer: every missing skill links to a small, real project that closes the gap.

- One entry per skill: why it matters (from live data), a scoped project, a time estimate and a starting link.
- Start with the gaps the data shows most often: Microsoft Fabric, Azure, Data warehousing, ETL, Tableau, Python.
- Link each "Missing" skill on the role cards straight to its entry.

## Phase 3: Trends over time (2 sessions, after about 8 weeks of data)

The pipeline already keeps first-seen and last-seen dates and never deletes rows, so trends come almost for free.

- Weekly snapshot of skill demand and median salary per role.
- "Rising and falling skills" chart: for example, is Microsoft Fabric growing month on month?
- Posting volume by region over time.

## Phase 4: All data roles (1 session)

- Add Data Engineer, Data Scientist and Analytics Engineer to the title scope.
- Add about 20 skills those roles ask for (for example Airflow, Kafka, scikit-learn, Terraform).
- The matcher and tracker need no structural change.

## Phase 5: Optional AI-assisted matching (2 sessions)

From the original plan: a visitor may add their own AI provider key for a sharper match.

- The key is used for one request, straight from the browser to the provider, and never stored.
- It can recognise related experience the rules miss, such as "Looker" experience counting towards a Power BI role.
- The free rule-based match stays the default and works without it.

## Phase 6: All tech roles (about a week)

- Software, cloud, cyber security, IT support and product roles.
- A skills list of roughly 150 to 200 items, tested the same way as today's 48.
- Store skill tags rather than full descriptions, so storage stays within the free tier.

## Phase 7: Any UK job (several weeks; likely paid tiers)

This is a different product, so it comes last and only if the earlier phases prove useful.

| Challenge | Approach |
| --- | --- |
| Every sector has its own vocabulary ("NMC registration", "CSCS card", "QTS") | Adopt the free ESCO skills taxonomy (about 13,900 skills, each with alternative wordings) instead of hand-written rules |
| Hundreds of thousands of live UK adverts | Sample each sector on a daily quota instead of collecting everything |
| Free API limits (Adzuna: 2,500 calls a month) | Apply for higher limits, or add other licensed sources |
| Role types for every job | Map titles to the ONS occupation codes (SOC 2020) |
| Database size | Keep tags and salaries; drop full descriptions after tagging |
| Matching quality across sectors | Test each sector on a hand-checked sample before it goes live |

## How success is measured

| Phase | Measure |
| --- | --- |
| 1 | 30 days of daily runs with no failures; database under 100 MB |
| 2 | Every "Missing" skill on a role card has a library entry |
| 3 | First trend chart published from 8 or more weeks of data |
| 4 to 6 | Match results checked by hand on 20 sample CVs per new role group |
| 7 | Skill tagging accuracy of at least 90% on a hand-checked sample per sector |

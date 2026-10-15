# Changelog

Newest first. One line per change.

| Date | Change |
| --- | --- |
| 2026-10-15 | v2 "Match my CV" added and moved to the top of the page: in-browser CV reading (PDF, Word, paste), role-archetype scores with have / close / missing skills, "Your match" column and best-match sort in the tracker; migration `006` (`role_skill_profile` view) |
| 2026-10-15 | Site live at njflora.github.io/uk-job-market-tracker. Finance exclusion extended to Insight titles and FP&A; empty role filters hidden; missing locations show "Not stated"; README written |
| 2026-10-15 | Added the v1 public site (`frontend/`, Vite + React), read-only access rules and public views (migration `005`), and a GitHub Pages deploy workflow |
| 2026-10-15 | Added skill tagging: 48 skills from a scan of 339 postings (`pipeline/tag/skills.py`, `docs/SKILLS.md`), migration `004` (`skills_from_snippet` flag, `skill_demand` view) |
| 2026-10-15 | Hardened `pipeline/run.py`: checks secrets at start; if one source fails the other still loads, then the run exits red. Adzuna jobs are not closed on a day Adzuna fails |
| 2026-10-15 | First scheduled-style run on GitHub Actions succeeded (5m 53s), after adding the missing `REED_API_KEY` secret |
| 2026-10-15 | Dedup key changed to company \| title \| region; added `towns` (migration `003`), training-provider blocklist (ITOL), finance-reporting exclusion and `pipeline/rebuild.py`; Reed details now reused from `raw_postings` |
| 2026-10-15 | Added daily GitHub Actions workflow (`.github/workflows/ingest.yml`), 05:17 UTC plus a manual run button |
| 2026-10-15 | First real load: 548 postings stored; 516 (94%) have a region |
| 2026-10-15 | Added the first loader: `pipeline/run.py`, `store.py`, `mapping.py`, `tag/clean.py`, `tag/regions.py` (tested on fake data) |
| 2026-10-15 | Added title filter (`pipeline/tag/titles.py`), field mapping (`docs/FIELD_MAPPING.md`) and migration `002` (contract type, full time, applications, role family) |
| 2026-10-15 | Added Reed client and test script; first Reed call returned 1,973 matches |
| 2026-10-13 | Added starter files: `.env.example`, `requirements.txt`, Adzuna client, two test scripts and the first schema (`sql/migrations/001_init.sql`) |
| 2026-10-13 | Created the GitHub repo, the Supabase project (London) and the Adzuna API key; Reed API key requested |

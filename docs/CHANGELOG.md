# Changelog

Newest first. One line per change.

| Date | Change |
| --- | --- |
| 2026-10-15 | Dedup key changed to company \| title \| region; added `towns` (migration `003`), training-provider blocklist (ITOL), finance-reporting exclusion and `pipeline/rebuild.py`; Reed details now reused from `raw_postings` |
| 2026-10-15 | Added daily GitHub Actions workflow (`.github/workflows/ingest.yml`), 05:17 UTC plus a manual run button |
| 2026-10-15 | First real load: 548 postings stored; 516 (94%) have a region |
| 2026-10-15 | Added the first loader: `pipeline/run.py`, `store.py`, `mapping.py`, `tag/clean.py`, `tag/regions.py` (tested on fake data) |
| 2026-10-15 | Added title filter (`pipeline/tag/titles.py`), field mapping (`docs/FIELD_MAPPING.md`) and migration `002` (contract type, full time, applications, role family) |
| 2026-10-15 | Added Reed client and test script; first Reed call returned 1,973 matches |
| 2026-10-13 | Added starter files: `.env.example`, `requirements.txt`, Adzuna client, two test scripts and the first schema (`sql/migrations/001_init.sql`) |
| 2026-10-13 | Created the GitHub repo, the Supabase project (London) and the Adzuna API key; Reed API key requested |

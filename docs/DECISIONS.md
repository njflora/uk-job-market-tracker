# Decisions

Why each service was chosen. Checked 13 October 2026.

## Job data: Reed first, Adzuna second

- Reed's details endpoint returns the full job description. The Tag stage needs full text to find skills.
- Adzuna only returns a description snippet. It adds wider coverage (it aggregates many boards) and clean location and salary fields.
- Adzuna free limits: 25 calls a minute, 250 a day, 1,000 a week, 2,500 a month.
- Adzuna terms: every displayed Adzuna listing carries an "Adzuna" label of at least 116 x 23 px.

## Database: Supabase (Free)

- Permanent free tier with an always-on Postgres database (500 MB), London region.
- Railway was rejected: after a 30-day trial its Free plan gives $1 a month of credit, which will not run a database all month.
- Free projects pause after a week without activity; the daily ingest job prevents this.
- Connections from GitHub Actions use the Session pooler (IPv4). The direct connection is IPv6 only.
- No backups on Free, so a weekly `pg_dump` job is planned.

## Scheduling: GitHub Actions

- Free on public repos. Scheduled workflows switch off after 60 days with no repo activity.

## Hosting: GitHub Pages, no separate API for v1 (decided 15 Oct 2026)

- The site is static (Vite + React) on GitHub Pages: no extra account, and it fits a portfolio kept on GitHub.
- It reads Supabase's built-in REST API with the public "publishable" key. Migration `005` makes that key read-only: it can see `public_postings` and `skill_demand`, and nothing in `raw_postings`.
- Render is no longer needed for v1. v2's CV matching is planned to run in the browser, so the CV never leaves the visitor's machine.
- Rule for every future table: enable row level security in the same migration that creates it.

## Match my CV (v2): how it works and why (decided 15 Oct 2026)

- **The page starts with the match.** A visitor answers "where do I stand?" first, then drops into the tracker filtered to the jobs that fit them.
- **The CV never leaves the browser.** PDF (pdf.js), Word (mammoth) and pasted text are read on the visitor's own machine. Nothing is uploaded or stored, so there is no personal data to protect on the server.
- **Same rules as job adverts.** `frontend/src/skills.js` copies the 48 patterns in `pipeline/tag/skills.py`. Both are tested on the same 13 phrases.
- **Core skills.** A role's core skills are those named in at least 25% of its full-text postings (at most 10), from the `role_skill_profile` view.
- **Scoring.** Have = 1 point. Close = half a point, when the CV has a sibling skill (for example Tableau when the role asks for Power BI). Missing = 0.
- **Thin data is flagged.** A role with fewer than 5 full-text postings is labelled "limited data" and listed last.

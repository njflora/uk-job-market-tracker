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

## Hosting (later): Vercel for the front end, Render for the API

- Vercel Hobby is non-commercial only, which fits a portfolio project.
- Render's free web service sleeps after 15 idle minutes and takes about a minute to wake.

-- 002_reed_fields_and_role.sql
-- Adds the extra Reed fields (decided 15 Oct 2026) and the role family from the title filter.
-- Safe to run more than once.

alter table postings
  add column if not exists contract_type text,      -- Reed: Permanent / Contract / Temporary
  add column if not exists full_time     boolean,   -- Reed: fullTime
  add column if not exists applications  integer,   -- Reed search: applications (competition per job)
  add column if not exists role_family   text;      -- from pipeline/tag/titles.py, e.g. 'BI Developer'

create index if not exists postings_role_family_idx on postings (role_family);

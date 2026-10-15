-- 003_towns.sql
-- The dedup key now uses region (decided 15 Oct 2026), so one posting can cover several towns.
-- `towns` keeps every town the posting was seen in, so the tracker can still filter by town.
-- Safe to run more than once.

alter table postings
  add column if not exists towns text[] not null default '{}';

-- GIN index: makes "where 'Manchester' = any(towns)" fast.
create index if not exists postings_towns_idx on postings using gin (towns);

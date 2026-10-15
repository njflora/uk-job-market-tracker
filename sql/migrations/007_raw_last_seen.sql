-- 007_raw_last_seen.sql
-- Stop raw_postings growing every day with identical copies.
-- From now on a raw record is saved again only when it has changed. When it has not,
-- the latest copy's last_seen_at is updated instead, so rebuilds still know when each
-- job was last seen. Safe to run more than once.

alter table raw_postings
  add column if not exists last_seen_at timestamptz;

update raw_postings set last_seen_at = fetched_at where last_seen_at is null;

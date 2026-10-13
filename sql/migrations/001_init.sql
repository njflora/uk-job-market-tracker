-- 001_init.sql
-- First schema for the UK Job Market Tracker.
-- Follows the plan's Data pipeline section: raw payloads kept as-is,
-- postings / companies / skills in separate tables, inactive flag instead of deletes,
-- dedup on normalised company + title + location.

-- 1. Raw API responses, stored before any parsing so a bad parse never loses data.
create table if not exists raw_postings (
  raw_id        bigint generated always as identity primary key,
  source        text not null check (source in ('reed', 'adzuna')),
  source_job_id text not null,
  fetched_at    timestamptz not null default now(),
  payload       jsonb not null
);
create index if not exists raw_postings_source_job_idx on raw_postings (source, source_job_id);

-- 2. One row per employer, matched on a cleaned-up name ("Acme Ltd" = "ACME Limited").
create table if not exists companies (
  company_id      bigint generated always as identity primary key,
  name            text not null,
  name_normalised text not null unique
);

-- 3. One row per real job, whichever source(s) it came from.
create table if not exists postings (
  posting_id          bigint generated always as identity primary key,
  dedup_key           text not null unique,  -- normalised company|title|location
  source              text not null check (source in ('reed', 'adzuna')),
  source_job_id       text not null,
  company_id          bigint references companies (company_id),
  title               text not null,
  location_text       text,
  region              text,
  seniority           text,
  salary_min          numeric,
  salary_max          numeric,
  salary_period       text,
  salary_is_predicted boolean not null default false,
  description         text,
  url                 text not null,
  posted_at           timestamptz,
  expires_at          timestamptz,
  first_seen          timestamptz not null default now(),
  last_seen           timestamptz not null default now(),
  is_active           boolean not null default true
);
create index if not exists postings_active_idx on postings (is_active);
create index if not exists postings_region_idx on postings (region);

-- 4. The skills we tag for (SQL, Python, Power BI ...), with alternative spellings.
create table if not exists skills (
  skill_id bigint generated always as identity primary key,
  name     text not null unique,
  category text,
  aliases  text[] not null default '{}'
);

-- 5. Which skills each posting mentions (many-to-many).
create table if not exists posting_skills (
  posting_id bigint not null references postings (posting_id) on delete cascade,
  skill_id   bigint not null references skills (skill_id),
  primary key (posting_id, skill_id)
);
create index if not exists posting_skills_skill_idx on posting_skills (skill_id);

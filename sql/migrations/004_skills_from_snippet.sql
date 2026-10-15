-- 004_skills_from_snippet.sql
-- Adzuna descriptions are 500-character snippets, so their skill tags are incomplete.
-- This flag lets market-wide skill figures use full-text (Reed) postings only.
-- Safe to run more than once.

alter table postings
  add column if not exists skills_from_snippet boolean not null default false;

-- Share of full-text postings that mention each skill: the tracker's headline skill figures.
create or replace view skill_demand as
with full_text as (
  select posting_id from postings where is_active and not skills_from_snippet
)
select s.name as skill,
       s.category,
       count(ps.posting_id)                                                    as postings,
       round(100.0 * count(ps.posting_id) / nullif((select count(*) from full_text), 0), 1) as pct_of_postings
from skills s
left join posting_skills ps
  on ps.skill_id = s.skill_id and ps.posting_id in (select posting_id from full_text)
group by s.name, s.category
order by postings desc;

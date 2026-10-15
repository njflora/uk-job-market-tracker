-- 006_role_skill_profile.sql
-- What each role family asks for: for every role family, the share of its full-text (Reed)
-- postings that mention each skill. The "Match my CV" section uses it to find each role's
-- core skills (named in at least 25% of that role's postings).
-- Read-only for the public, like the other views. Safe to run more than once.

drop view if exists role_skill_profile;
create view role_skill_profile
with (security_invoker = true) as
with full_text as (
  select posting_id, role_family
  from postings
  where is_active and not skills_from_snippet and role_family is not null
),
family_size as (
  select role_family, count(*) as postings
  from full_text
  group by role_family
)
select ft.role_family,
       fs.postings,
       s.name                                              as skill,
       s.category,
       count(*)                                            as mentions,
       round(100.0 * count(*) / fs.postings, 1)            as pct
from full_text ft
join posting_skills ps on ps.posting_id = ft.posting_id
join skills s          on s.skill_id    = ps.skill_id
join family_size fs    on fs.role_family = ft.role_family
group by ft.role_family, fs.postings, s.name, s.category
order by ft.role_family, mentions desc;

grant select on role_skill_profile to anon, authenticated;

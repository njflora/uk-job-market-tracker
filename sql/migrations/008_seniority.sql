-- 008_seniority.sql
-- Show each posting's seniority on the website.
-- The pipeline now fills postings.seniority from the job title (pipeline/tag/seniority.py).
-- This recreates public_postings with one extra column, seniority. Everything else is
-- unchanged from 005, including security_invoker, so the read-only rules still apply.
-- Run the rebuild afterwards to fill seniority for existing postings.
-- Safe to run more than once.

drop view if exists public_postings;
create view public_postings
with (security_invoker = true) as
select p.posting_id,
       p.title,
       c.name                       as company,
       p.role_family,
       p.seniority,
       p.region,
       p.towns,
       p.salary_min,
       p.salary_max,
       p.salary_period,
       p.salary_is_predicted,
       p.contract_type,
       p.full_time,
       p.applications,
       p.posted_at,
       p.first_seen,
       p.last_seen,
       p.url,
       p.source,
       p.skills_from_snippet,
       coalesce(array_agg(s.name order by s.name) filter (where s.name is not null), '{}') as skills
from postings p
left join companies c       on c.company_id = p.company_id
left join posting_skills ps on ps.posting_id = p.posting_id
left join skills s          on s.skill_id = ps.skill_id
where p.is_active
group by p.posting_id, c.name;

grant select on public_postings to anon, authenticated;

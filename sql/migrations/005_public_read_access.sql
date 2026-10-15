-- 005_public_read_access.sql
-- Lock the database down before the website goes public.
--
-- The website uses Supabase's public ("publishable") key, which anyone can see in the page source.
-- Without these rules that key could read raw_postings and even change or delete data.
-- After this migration the public key can only READ postings, companies and skills.
-- raw_postings stays private. The pipeline is unaffected: it connects as the database owner.
-- Safe to run more than once.

-- 1. Row level security on every table. With RLS on and no policy, the public key sees nothing.
alter table raw_postings   enable row level security;
alter table companies      enable row level security;
alter table postings       enable row level security;
alter table skills         enable row level security;
alter table posting_skills enable row level security;

-- 2. Belt and braces: the public roles may never write, whatever policies say.
revoke insert, update, delete, truncate on all tables in schema public from anon, authenticated;

-- 3. Read-only policies for the website. raw_postings deliberately gets none.
drop policy if exists "public read" on companies;
create policy "public read" on companies      for select to anon, authenticated using (true);
drop policy if exists "public read" on postings;
create policy "public read" on postings       for select to anon, authenticated using (true);
drop policy if exists "public read" on skills;
create policy "public read" on skills         for select to anon, authenticated using (true);
drop policy if exists "public read" on posting_skills;
create policy "public read" on posting_skills for select to anon, authenticated using (true);

-- 4. One tidy view for the tracker table: active postings with company name and skills.
--    security_invoker = the view obeys the rules above instead of bypassing them.
--    The description is left out: it is large, and not needed in the table.
drop view if exists public_postings;
create view public_postings
with (security_invoker = true) as
select p.posting_id,
       p.title,
       c.name                       as company,
       p.role_family,
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

alter view skill_demand set (security_invoker = true);

grant select on public_postings, skill_demand to anon, authenticated;

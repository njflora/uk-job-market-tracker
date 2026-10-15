import React, { useEffect, useMemo, useState } from 'react'
import { loadPostings, loadSkillDemand, loadRoleProfiles } from './api.js'
import { buildProfiles, rankArchetypes, matchPosting } from './match.js'
import MatchSection from './MatchSection.jsx'

const ROLE_FAMILIES = [
  'Data Analyst', 'BI Analyst', 'BI Developer', 'Power BI Developer',
  'BI Specialist', 'Reporting / MI Analyst', 'Insight Analyst',
]
const CONTRACTS = ['Permanent', 'Contract', 'Temporary']
const LEVELS = ['Entry', 'Mid', 'Senior', 'Lead', 'Not stated']
const levelOf = (p) => p.seniority || 'Not stated'
const QUICK_SKILLS = ['SQL', 'Power BI', 'Excel', 'Python', 'DAX', 'Tableau', 'Azure', 'Microsoft Fabric']
const PAGE_SIZE = 25

const gbp = (n) => '£' + Math.round(n).toLocaleString('en-GB')
const shortDate = (d) => (d ? new Date(d).toLocaleDateString('en-GB', { day: 'numeric', month: 'short' }) : '–')

function salaryText(p) {
  const lo = p.salary_min, hi = p.salary_max
  if (!lo && !hi) return null
  if (lo && hi && Math.round(lo) !== Math.round(hi)) return `${gbp(lo)}–${gbp(hi)}`
  return gbp(hi || lo)
}

function toggle(set, value) {
  const next = new Set(set)
  next.has(value) ? next.delete(value) : next.add(value)
  return next
}

const EMPTY_FILTERS = {
  q: '', roles: new Set(ROLE_FAMILIES), levels: new Set(LEVELS), region: '', town: '', minSalary: 0,
  hideEstimated: false, skills: new Set(), contracts: new Set(CONTRACTS),
}

export default function App() {
  const [postings, setPostings] = useState([])
  const [demand, setDemand] = useState([])
  const [profiles, setProfiles] = useState([])
  const [cvSkills, setCvSkills] = useState(null)
  const [status, setStatus] = useState('loading')
  const [f, setF] = useState(EMPTY_FILTERS)
  const [sort, setSort] = useState('newest')
  const [page, setPage] = useState(0)
  const [filtersOpen, setFiltersOpen] = useState(false)

  useEffect(() => {
    Promise.all([loadPostings(), loadSkillDemand(), loadRoleProfiles()])
      .then(([p, d, r]) => { setPostings(p); setDemand(d); setProfiles(buildProfiles(r)); setStatus('ready') })
      .catch((e) => { console.error(e); setStatus('error') })
  }, [])

  const update = (patch) => { setF((old) => ({ ...old, ...patch })); setPage(0) }

  const regions = useMemo(
    () => [...new Set(postings.map((p) => p.region).filter(Boolean))].sort(),
    [postings],
  )
  const skillRank = useMemo(() => new Map(demand.map((d, i) => [d.skill, i])), [demand])

  const archetypes = useMemo(() => (cvSkills ? rankArchetypes(profiles, cvSkills) : []), [profiles, cvSkills])
  const demandBySkill = useMemo(() => new Map(demand.map((d) => [d.skill, Number(d.pct_of_postings)])), [demand])
  const matches = useMemo(() => {
    const m = new Map()
    if (cvSkills) for (const p of postings) m.set(p.posting_id, matchPosting(p, cvSkills))
    return m
  }, [postings, cvSkills])

  function seeJobs(family) {
    setF({ ...EMPTY_FILTERS, roles: new Set([family]) })
    setSort('match')
    setPage(0)
    document.getElementById('tracker')?.scrollIntoView({ behavior: 'smooth' })
  }

  function clearCv() {
    setCvSkills(null)
    if (sort === 'match') setSort('newest')
  }

  const filtered = useMemo(() => {
    const q = f.q.trim().toLowerCase()
    const town = f.town.trim().toLowerCase()
    const rows = postings.filter((p) => {
      if (!f.roles.has(p.role_family)) return false
      if (!f.levels.has(levelOf(p))) return false
      if (q && !`${p.title} ${p.company ?? ''}`.toLowerCase().includes(q)) return false
      if (f.region && p.region !== f.region) return false
      if (town && !(p.towns || []).some((t) => t.toLowerCase().includes(town))) return false
      if (f.hideEstimated && p.salary_is_predicted) return false
      if (f.minSalary > 0 && !((p.salary_max || p.salary_min || 0) >= f.minSalary)) return false
      if (p.contract_type && !f.contracts.has(p.contract_type)) return false
      for (const s of f.skills) if (!(p.skills || []).includes(s)) return false
      return true
    })
    const by = {
      newest: (a, b) => (b.posted_at || '').localeCompare(a.posted_at || ''),
      salary: (a, b) => (b.salary_max || b.salary_min || 0) - (a.salary_max || a.salary_min || 0),
      applicants: (a, b) => (a.applications ?? 1e9) - (b.applications ?? 1e9),
      match: (a, b) => {
        const ma = matches.get(a.posting_id), mb = matches.get(b.posting_id)
        return ((mb?.ratio ?? -1) - (ma?.ratio ?? -1)) || ((mb?.met ?? 0) - (ma?.met ?? 0))
      },
    }[sort]
    return rows.sort(by)
  }, [postings, f, sort, matches])

  const roleCounts = useMemo(() => {
    const c = Object.fromEntries(ROLE_FAMILIES.map((r) => [r, 0]))
    for (const p of postings) if (p.role_family in c) c[p.role_family] += 1
    return c
  }, [postings])

  const levelCounts = useMemo(() => {
    const c = Object.fromEntries(LEVELS.map((l) => [l, 0]))
    for (const p of postings) c[levelOf(p)] += 1
    return c
  }, [postings])

  const lastRefresh = useMemo(() => {
    const t = postings.reduce((m, p) => (p.last_seen > m ? p.last_seen : m), '')
    return t ? new Date(t).toLocaleString('en-GB', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' }) : '–'
  }, [postings])

  const fullTextCount = useMemo(() => postings.filter((p) => !p.skills_from_snippet).length, [postings])
  const pageRows = filtered.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE)
  const pages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE))

  return (
    <div className="app">
      <header className="topbar">
        <div className="wrap topbar-inner">
          <a className="brand" href="#top">
            <svg width="28" height="28" viewBox="0 0 28 28" aria-hidden="true"><rect x="2" y="14" width="5" height="12" rx="1" fill="#0E5E5E" /><rect x="11.5" y="8" width="5" height="18" rx="1" fill="#0E5E5E" /><rect x="21" y="2" width="5" height="24" rx="1" fill="#16181D" /></svg>
            <span>UK BI Job Tracker</span>
          </a>
          <nav aria-label="Main" className="nav">
            <a href="#match" className="nav-link active">Match my CV</a>
            <a href="#tracker" className="nav-link">Jobs</a>
            <a href="#skills" className="nav-link">Skill demand</a>
            <a href="#about" className="nav-link">About the data</a>
          </nav>
        </div>
      </header>

      <main id="top" className="wrap main">
        {status === 'error' && (
          <p role="alert" className="panel error">The job data could not be loaded just now. Please try again in a minute.</p>
        )}

        <MatchSection
          cvSkills={cvSkills}
          onCv={(skills) => setCvSkills(skills)}
          onClear={clearCv}
          archetypes={archetypes}
          demandBySkill={demandBySkill}
          onSeeJobs={seeJobs}
          ready={status === 'ready'}
        />

        <section className="hero market" aria-labelledby="market-h">
          <div className="hero-text">
            <p className="eyebrow">Updated daily from Reed and Adzuna</p>
            <h2 id="market-h" className="market-h">Every UK BI and Data Analyst job, in one table.</h2>
            <p className="lede">Duplicates merged, training-course adverts removed, and every listing tagged with the skills it asks for.</p>
          </div>
          <dl className="stats">
            <div className="stat"><dt>Live postings</dt><dd>{status === 'ready' ? postings.length : '…'}</dd></div>
            <div className="stat"><dt>Skills tracked</dt><dd>{status === 'ready' ? demand.length : '…'}</dd></div>
            <div className="stat"><dt>Last refresh</dt><dd className="small">{status === 'ready' ? lastRefresh : '…'}</dd></div>
          </dl>
        </section>

        <div className="layout" id="tracker">
          <aside className="panel filters" aria-label="Filters">
            <div className="filters-head">
              <h2>Filters</h2>
              <div className="filters-actions">
                <button type="button" className="link-btn" onClick={() => { setF(EMPTY_FILTERS); setPage(0) }}>Clear all</button>
                <button type="button" className="btn mobile-only" aria-expanded={filtersOpen} aria-controls="filters-body" onClick={() => setFiltersOpen(!filtersOpen)}>
                  {filtersOpen ? 'Hide filters' : 'Show filters'}
                </button>
              </div>
            </div>
            <div id="filters-body" className={filtersOpen ? 'filters-body open' : 'filters-body'}>

            <div className="field">
              <label htmlFor="q">Search</label>
              <input id="q" type="search" placeholder="Title or company" value={f.q} onChange={(e) => update({ q: e.target.value })} />
            </div>

            <fieldset className="field">
              <legend>Role</legend>
              {ROLE_FAMILIES.filter((r) => status !== 'ready' || roleCounts[r] > 0).map((r) => (
                <label key={r} className="check">
                  <span><input type="checkbox" checked={f.roles.has(r)} onChange={() => update({ roles: toggle(f.roles, r) })} />{r}</span>
                  <span className="count">{roleCounts[r]}</span>
                </label>
              ))}
            </fieldset>

            <fieldset className="field">
              <legend>Seniority</legend>
              {LEVELS.filter((l) => status !== 'ready' || levelCounts[l] > 0).map((l) => (
                <label key={l} className="check">
                  <span><input type="checkbox" checked={f.levels.has(l)} onChange={() => update({ levels: toggle(f.levels, l) })} />{l}</span>
                  <span className="count">{levelCounts[l]}</span>
                </label>
              ))}
            </fieldset>

            <div className="field">
              <label htmlFor="region">Region</label>
              <select id="region" value={f.region} onChange={(e) => update({ region: e.target.value })}>
                <option value="">All regions</option>
                {regions.map((r) => <option key={r} value={r}>{r}</option>)}
              </select>
            </div>

            <div className="field">
              <label htmlFor="town">Town</label>
              <input id="town" type="text" placeholder="e.g. Liverpool" value={f.town} onChange={(e) => update({ town: e.target.value })} />
            </div>

            <div className="field">
              <label htmlFor="sal">Minimum salary</label>
              <input id="sal" type="range" min="0" max="100000" step="5000" value={f.minSalary} onChange={(e) => update({ minSalary: Number(e.target.value) })} />
              <span className="mono">{f.minSalary ? `${gbp(f.minSalary)}+` : 'Any salary'}</span>
              <label className="check"><span><input type="checkbox" checked={f.hideEstimated} onChange={(e) => update({ hideEstimated: e.target.checked })} />Hide estimated salaries</span></label>
            </div>

            <fieldset className="field">
              <legend>Must mention</legend>
              <div className="pills">
                {QUICK_SKILLS.map((s) => (
                  <button key={s} type="button" aria-pressed={f.skills.has(s)} className={f.skills.has(s) ? 'pill on' : 'pill'} onClick={() => update({ skills: toggle(f.skills, s) })}>
                    {s === 'Microsoft Fabric' ? 'Fabric' : s}
                  </button>
                ))}
              </div>
            </fieldset>

            <fieldset className="field">
              <legend>Contract</legend>
              {CONTRACTS.map((c) => (
                <label key={c} className="check"><span><input type="checkbox" checked={f.contracts.has(c)} onChange={() => update({ contracts: toggle(f.contracts, c) })} />{c}</span></label>
              ))}
            </fieldset>
            </div>
          </aside>

          <div className="content">
            <section id="skills" className="panel pad" aria-labelledby="skills-h">
              <div className="section-head">
                <h2 id="skills-h">What employers ask for</h2>
                <p className="note">Share of full-text postings that mention each skill ({fullTextCount} Reed postings)</p>
              </div>
              <div className="bars">
                {demand.slice(0, 10).map((d) => (
                  <div className="bar-row" key={d.skill}>
                    <span className="bar-label">{d.skill}</span>
                    <span className="bar-track"><span className="bar-fill" style={{ width: `${d.pct_of_postings}%` }} /></span>
                    <span className="mono right">{Number(d.pct_of_postings).toFixed(1)}%</span>
                  </div>
                ))}
              </div>
            </section>

            <section className="panel" aria-labelledby="results-h">
              <div className="results-head">
                <h2 id="results-h">{filtered.length} postings <span className="muted-text">match your filters</span></h2>
                <label className="sort">Sort by
                  <select value={sort} onChange={(e) => { setSort(e.target.value); setPage(0) }}>
                    {cvSkills && <option value="match">Best match for my CV</option>}
                    <option value="newest">Newest first</option>
                    <option value="salary">Highest salary</option>
                    <option value="applicants">Fewest applicants</option>
                  </select>
                </label>
              </div>
              <div className="table-scroll">
                <table>
                  <thead>
                    <tr>
                      <th scope="col">Role</th>
                      <th scope="col">Location</th>
                      <th scope="col">Salary</th>
                      {cvSkills && <th scope="col">Your match</th>}
                      <th scope="col">Skills</th>
                      <th scope="col" className="right">Applicants</th>
                      <th scope="col">Posted</th>
                      <th scope="col">Source</th>
                    </tr>
                  </thead>
                  <tbody>
                    {status === 'loading' && (
                      <tr><td colSpan={cvSkills ? 8 : 7} className="empty">Loading today’s postings…</td></tr>
                    )}
                    {status === 'ready' && pageRows.length === 0 && (
                      <tr><td colSpan={cvSkills ? 8 : 7} className="empty">No postings match these filters. Try clearing one.</td></tr>
                    )}
                    {pageRows.map((p) => {
                      const skills = [...(p.skills || [])].sort((a, b) => (skillRank.get(a) ?? 99) - (skillRank.get(b) ?? 99))
                      const salary = salaryText(p)
                      return (
                        <tr key={p.posting_id}>
                          <td>
                            <a className="job-title" href={p.url} target="_blank" rel="noopener noreferrer">{p.title}</a>
                            <div className="sub">{p.company}</div>
                            <div className="family">{p.role_family}{p.seniority ? ` · ${p.seniority}` : ''}{p.contract_type ? ` · ${p.contract_type}` : ''}</div>
                          </td>
                          <td>
                            <div>{p.region || <span className="sub">Not stated</span>}</div>
                            <div className="sub small">{(p.towns || []).join(', ')}</div>
                          </td>
                          <td className="nowrap">
                            <div className="mono">{salary || <span className="sub">Not stated</span>}</div>
                            {salary && p.salary_is_predicted && <span className="tag-est">Adzuna estimate</span>}
                          </td>
                          {cvSkills && (
                            <td className="nowrap">
                              {(() => {
                                const m = matches.get(p.posting_id)
                                if (!m) return <span className="sub small">No skills listed</span>
                                return (
                                  <>
                                    <div className="mono">{m.met} of {m.total}</div>
                                    <div className="mini-meter" role="img" aria-label={`${m.met} of ${m.total} skills`}><span style={{ width: `${Math.round(m.ratio * 100)}%` }} /></div>
                                    {m.partial && <div className="sub small">snippet only</div>}
                                  </>
                                )
                              })()}
                            </td>
                          )}
                          <td>
                            <div className="chips">
                              {skills.slice(0, 5).map((s) => <span className={cvSkills?.has(s) ? 'chip yours' : 'chip'} key={s}>{s}</span>)}
                              {skills.length > 5 && <span className="chip more">+{skills.length - 5}</span>}
                              {p.skills_from_snippet && <span className="partial">Partial: description is a snippet</span>}
                            </div>
                          </td>
                          <td className="mono right">{p.applications ?? '–'}</td>
                          <td className="nowrap sub">{shortDate(p.posted_at)}</td>
                          <td>
                            {p.source === 'adzuna'
                              ? <a className="adzuna" href={p.url} target="_blank" rel="noopener noreferrer">Jobs by Adzuna</a>
                              : <a className="reed" href={p.url} target="_blank" rel="noopener noreferrer">View on Reed</a>}
                          </td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
              </div>
              <div className="pager">
                <span>{filtered.length ? `Showing ${page * PAGE_SIZE + 1} to ${Math.min((page + 1) * PAGE_SIZE, filtered.length)} of ${filtered.length}` : 'Showing 0'}</span>
                <div className="pager-btns">
                  <button type="button" className="btn" disabled={page === 0} onClick={() => setPage(page - 1)}>Previous</button>
                  <button type="button" className="btn primary" disabled={page >= pages - 1} onClick={() => setPage(page + 1)}>Next</button>
                </div>
              </div>
            </section>
          </div>
        </div>

        <footer id="about" className="footer">
          <div className="about">
            <h2>About the data</h2>
            <p>Postings come from the Reed and Adzuna APIs every morning. The same job listed in several towns is shown once, with every town kept. Skill figures use Reed postings only, because Adzuna provides a short snippet of each advert. Salaries marked as estimates are Adzuna’s, not the employer’s.</p>
          </div>
          <div className="credits">
            <span>Jobs by <a href="https://www.adzuna.co.uk" target="_blank" rel="noopener noreferrer">Adzuna</a> · Powered by <a href="https://www.reed.co.uk" target="_blank" rel="noopener noreferrer">Reed</a></span>
            <a href="https://github.com/njflora/uk-job-market-tracker" target="_blank" rel="noopener noreferrer">Source code on GitHub</a>
            <span>Built by Nick · <a href="https://github.com/njflora" target="_blank" rel="noopener noreferrer">github.com/njflora</a></span>
          </div>
        </footer>
      </main>
    </div>
  )
}

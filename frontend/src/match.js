// Scores a CV's skills against each role family ("archetype") and against single postings.
//
// Core skills: the skills named in at least CORE_PCT% of a role's full-text postings (at most MAX_CORE).
// Have = 1 point. Close = 0.5: the CV has a sibling skill (e.g. Tableau when the role asks for Power BI).

import { SIBLINGS } from './skills.js'

export const CORE_PCT = 25
export const MAX_CORE = 10
export const MIN_POSTINGS = 5

export function buildProfiles(rows) {
  const byFamily = new Map()
  for (const r of rows) {
    if (!byFamily.has(r.role_family)) byFamily.set(r.role_family, { family: r.role_family, postings: r.postings, skills: [] })
    byFamily.get(r.role_family).skills.push({ skill: r.skill, pct: Number(r.pct) })
  }
  for (const p of byFamily.values()) p.skills.sort((a, b) => b.pct - a.pct)
  return [...byFamily.values()]
}

function siblingIn(skill, cv) {
  for (const group of SIBLINGS) {
    if (!group.includes(skill)) continue
    const found = group.find((s) => s !== skill && cv.has(s))
    if (found) return found
  }
  return null
}

export function scoreArchetype(profile, cv) {
  const core = profile.skills.filter((s) => s.pct >= CORE_PCT).slice(0, MAX_CORE)
  const have = [], close = [], missing = []
  for (const s of core) {
    if (cv.has(s.skill)) have.push(s)
    else {
      const via = siblingIn(s.skill, cv)
      if (via) close.push({ ...s, via })
      else missing.push(s)
    }
  }
  const score = core.length ? (have.length + 0.5 * close.length) / core.length : 0
  return {
    family: profile.family,
    postings: profile.postings,
    limited: profile.postings < MIN_POSTINGS,
    core, have, close, missing,
    pct: Math.round(100 * score),
  }
}

export function rankArchetypes(profiles, cv) {
  return profiles
    .map((p) => scoreArchetype(p, cv))
    .filter((a) => a.core.length > 0)
    .sort((a, b) => (a.limited - b.limited) || (b.pct - a.pct) || (b.postings - a.postings))
}

// One posting: how many of the skills it names does the CV have?
export function matchPosting(posting, cv) {
  const asked = posting.skills || []
  if (!asked.length) return null
  const met = asked.filter((s) => cv.has(s)).length
  return { met, total: asked.length, ratio: met / asked.length, partial: posting.skills_from_snippet }
}

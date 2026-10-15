// Reads from Supabase's built-in REST API with the public (read-only) key.
// Migration 005 makes this key read-only: it can see public_postings and skill_demand, nothing else.

const URL = import.meta.env.VITE_SUPABASE_URL
const KEY = import.meta.env.VITE_SUPABASE_KEY

async function get(path) {
  if (!URL || !KEY) throw new Error('Missing VITE_SUPABASE_URL or VITE_SUPABASE_KEY')
  const res = await fetch(`${URL}/rest/v1/${path}`, {
    headers: { apikey: KEY, Authorization: `Bearer ${KEY}` },
  })
  if (!res.ok) throw new Error(`Supabase ${res.status}: ${await res.text()}`)
  return res.json()
}

// A few hundred rows today, so the page loads them all once and filters in the browser.
// Supabase returns at most 1,000 rows per request: page through if the table grows past that.
export async function loadPostings() {
  const rows = []
  for (let from = 0; ; from += 1000) {
    const batch = await get(`public_postings?select=*&order=posted_at.desc.nullslast&offset=${from}&limit=1000`)
    rows.push(...batch)
    if (batch.length < 1000) return rows
  }
}

export function loadSkillDemand() {
  return get('skill_demand?select=*&order=postings.desc')
}

export function loadRoleProfiles() {
  return get('role_skill_profile?select=*')
}

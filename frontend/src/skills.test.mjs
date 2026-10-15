// Run from the repo root with: node frontend/src/skills.test.mjs
// Uses the same cases as the Python tagger (tests/skill_cases.json), so the two copies cannot drift apart.
import { readFileSync } from 'node:fs'
import { findSkills } from './skills.js'

const fixture = new URL('../../tests/skill_cases.json', import.meta.url)
const { cases } = JSON.parse(readFileSync(fixture, 'utf8'))

let failures = 0
for (const { text, skills: expected } of cases) {
  const got = [...findSkills(text)].sort()
  const ok = JSON.stringify(got) === JSON.stringify([...expected].sort())
  if (!ok) failures++
  console.log(ok ? 'OK ' : 'XX ', got.join(', ') || '(none)', '|', text.slice(0, 55))
}
console.log(`${cases.length - failures} of ${cases.length} passed`)
process.exit(failures ? 1 : 0)

import React, { useRef, useState } from 'react'
import { readCv } from './cv.js'
import { findSkills } from './skills.js'
import { CORE_PCT, MIN_POSTINGS } from './match.js'

const Tick = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="M5 12l5 5 9-10" /></svg>
)
const Dash = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" aria-hidden="true"><path d="M6 12h12" /></svg>
)
const Cross = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" aria-hidden="true"><path d="M7 7l10 10M17 7L7 17" /></svg>
)

function Meter({ pct, label }) {
  return (
    <div className="meter" role="img" aria-label={label}>
      <div className="meter-fill" style={{ width: `${pct}%` }} />
    </div>
  )
}

export default function MatchSection({ cvSkills, onCv, onClear, archetypes, demandBySkill, onSeeJobs, ready }) {
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [pasting, setPasting] = useState(false)
  const [pasted, setPasted] = useState('')
  const [dragOver, setDragOver] = useState(false)
  const fileInput = useRef(null)

  async function handleFile(file) {
    if (!file) return
    setBusy(true); setError('')
    try {
      const text = await readCv(file)
      const found = findSkills(text)
      if (!found.size) setError('No tracked skills were found in that file. If it is a scanned image, try pasting the text instead.')
      onCv(found, file.name)
    } catch (e) {
      setError(e.message || 'That file could not be read. Try pasting the text instead.')
    } finally {
      setBusy(false)
    }
  }

  function handlePaste() {
    const found = findSkills(pasted)
    setError(found.size ? '' : 'No tracked skills were found in that text.')
    onCv(found, 'pasted text')
  }

  const best = archetypes.find((a) => !a.limited)

  return (
    <section id="match" className="match" aria-labelledby="match-h">
      <div className="match-grid">
        <div className="panel pad match-intro">
          <p className="eyebrow">Live UK BI and Data Analyst postings, updated daily</p>
          <h1 id="match-h">See where you stand in the UK BI job market.</h1>
          <p className="lede">Add your CV to compare your skills with what employers are asking for right now, role by role.</p>

          {!cvSkills && (
            <>
              <button
                type="button"
                className={dragOver ? 'dropzone over' : 'dropzone'}
                onClick={() => fileInput.current?.click()}
                onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
                onDragLeave={() => setDragOver(false)}
                onDrop={(e) => { e.preventDefault(); setDragOver(false); handleFile(e.dataTransfer.files[0]) }}
                disabled={busy || !ready}
              >
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="M12 16V4" /><path d="M7 9l5-5 5 5" /><path d="M4 16v3a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1v-3" /></svg>
                <span className="dz-main">{busy ? 'Reading your CV…' : 'Drop a PDF or Word CV, or click to choose'}</span>
                <span className="dz-sub">{ready ? 'PDF, .docx or .txt' : 'Loading live job data…'}</span>
              </button>
              <input ref={fileInput} type="file" accept=".pdf,.docx,.txt,.md" hidden onChange={(e) => handleFile(e.target.files[0])} />
              {!pasting && <button type="button" className="link-btn left" onClick={() => setPasting(true)}>Or paste your CV text instead</button>}
              {pasting && (
                <div className="paste">
                  <label htmlFor="cvtext">CV text</label>
                  <textarea id="cvtext" rows="6" value={pasted} onChange={(e) => setPasted(e.target.value)} placeholder="Paste your CV, or just a list of your skills" />
                  <button type="button" className="btn primary" disabled={!pasted.trim() || !ready} onClick={handlePaste}>Check my skills</button>
                </div>
              )}
            </>
          )}

          {error && <p role="alert" className="notice">{error}</p>}

          <p className="privacy">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><rect x="5" y="11" width="14" height="10" rx="2" /><path d="M8 11V7a4 4 0 0 1 8 0v4" /></svg>
            Your CV is read in your browser. It is never uploaded or stored.
          </p>
        </div>

        <div className="panel pad match-summary" aria-live="polite">
          {!cvSkills && (
            <div className="how">
              <h2>How it works</h2>
              <ol>
                <li>Your CV is checked for 48 skills and tools, the same way every job advert is.</li>
                <li>Each role type has <strong>core skills</strong>: the ones named in at least {CORE_PCT}% of its postings.</li>
                <li>You see how many core skills you have, which ones you are close on, and which are missing.</li>
                <li>Then jump straight to the jobs that fit you best.</li>
              </ol>
              <a href="#tracker" className="link-arrow">Or just browse all jobs</a>
            </div>
          )}

          {cvSkills && (
            <>
              <div className="summary-head">
                <h2>Skills found in your CV</h2>
                <button type="button" className="link-btn" onClick={onClear}>Use a different CV</button>
              </div>
              <div className="pills static">
                {[...cvSkills].sort().map((s) => <span key={s} className="pill-static">{s}</span>)}
                {!cvSkills.size && <span className="sub">None of the 48 tracked skills were found.</span>}
              </div>
              {best && (
                <div className="best">
                  <p className="best-label">Your closest role</p>
                  <div className="best-row">
                    <span className="best-name">{best.family}</span>
                    <span className="mono">{best.have.length} of {best.core.length} core skills{best.close.length ? ` + ${best.close.length} close` : ''}</span>
                  </div>
                  <Meter pct={best.pct} label={`${best.pct}% match with ${best.family}`} />
                </div>
              )}
            </>
          )}
        </div>
      </div>

      {cvSkills && archetypes.length > 0 && (
        <div className="archetypes" aria-labelledby="arch-h">
          <div className="section-head">
            <h2 id="arch-h">How close you are to each role</h2>
            <p className="note">Core skills = named in at least {CORE_PCT}% of that role's full-text postings</p>
          </div>
          <div className="cards">
            {archetypes.map((a) => {
              const topGap = demandBySkill && a.missing.length
                ? [...a.missing].sort((x, y) => (demandBySkill.get(y.skill) || 0) - (demandBySkill.get(x.skill) || 0))[0]
                : null
              return (
              <article key={a.family} className="card">
                <div className="card-head">
                  <h3>{a.family}</h3>
                  <span className="sub small">{a.postings} full-text posting{a.postings === 1 ? '' : 's'}</span>
                </div>
                {a.limited && <p className="limited">Limited data: fewer than {MIN_POSTINGS} postings, so treat this as a rough guide.</p>}
                <div>
                  <div className="meter-label"><span>{a.have.length} of {a.core.length} core skills</span><span className="mono">{a.pct}%</span></div>
                  <Meter pct={a.pct} label={`${a.pct}% match with ${a.family}`} />
                </div>
                <ul className="status-list">
                  {a.have.length > 0 && (
                    <li className="have"><Tick /><span><strong>Have:</strong> {a.have.map((s) => s.skill).join(', ')}</span></li>
                  )}
                  {a.close.length > 0 && (
                    <li className="close"><Dash /><span><strong>Close:</strong> {a.close.map((s) => `${s.skill} (you have ${s.via})`).join(', ')}</span></li>
                  )}
                  {a.missing.length > 0 && (
                    <li className="missing"><Cross /><span><strong>Missing:</strong> {a.missing.map((s) => `${s.skill} (${Math.round(s.pct)}% of these jobs)`).join(', ')}</span></li>
                  )}
                </ul>
                {topGap && (
                  <p className="gap-hint">Biggest gap to close first: <strong>{topGap.skill}</strong>, named in {Math.round(demandBySkill.get(topGap.skill) || 0)}% of all full-text BI and data postings.</p>
                )}
                <button type="button" className="btn primary card-btn" onClick={() => onSeeJobs(a.family)}>See best-matching jobs</button>
              </article>
              )
            })}
          </div>
        </div>
      )}
    </section>
  )
}

// Checks web/src/market/model.ts against the parity cases computed by pipeline/fullload/market.py.
// Run: npm run parity   (Node >= 23 runs TypeScript directly by stripping types)
import { readFileSync } from 'node:fs'
import { fnv1a, simulate } from '../src/market/model.ts'

const bundle = JSON.parse(readFileSync(new URL('../public/data/bundle.json', import.meta.url), 'utf-8'))
const m = bundle.market
let failures = 0
const close = (a: number, b: number) => Math.abs(a - b) <= 1e-6 * Math.max(1, Math.abs(b))

if (fnv1a('a') !== 0xe40c292c) { console.error('fnv1a mismatch'); failures++ }
for (const [i, c] of m.parity.entries()) {
  const got = simulate(m.inputs, m.operators, m.sigma_inc, m.sigma_ent, c.params).summary as Record<string, unknown>
  for (const [k, want] of Object.entries(c.summary as Record<string, unknown>)) {
    const g = got[k]
    const ok = typeof want === 'number' ? close(g as number, want)
      : Object.entries(want as Record<string, number>).every(([o, v]) => close((g as Record<string, number>)[o], v))
    if (!ok) { console.error(`case ${i} ${k}: ts=${JSON.stringify(g)} py=${JSON.stringify(want)}`); failures++ }
  }
}
console.log(failures ? `PARITY FAILED (${failures})` : `parity OK (${m.parity.length} cases)`)
process.exit(failures ? 1 : 0)

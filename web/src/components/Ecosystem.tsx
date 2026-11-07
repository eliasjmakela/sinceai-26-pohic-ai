import { bundle } from '../bundle'

/**
 * Who is in the market and what changes with OpenWeight, as a progressive reveal.
 * Step 0 is today (screen 1 shows only this). Steps 1–3 each add one arrow:
 *   1 the compactor weighs every lift → Europress
 *   2 Europress gives every operator the same forecast
 *   3 operators bid per kilo → the customer picks
 * Three boxes, at most three arrows, nothing moves except fades. Step captions: src/pitch/steps.ts.
 */
const C = {
  ink: '#0f172a', body: '#334155', muted: '#64748b', line: '#94a3b8', faint: '#cbd5e1',
  teal: '#0f766e', tealBg: '#f0fdfa', amber: '#b45309', amberBg: '#fffbeb', paper: '#ffffff',
}
const FADE = { transition: 'opacity 450ms ease, fill 450ms ease, stroke 450ms ease' }

function Box({ x, y, w, h, title, lines, active, dim = false }: { x: number; y: number; w: number; h: number; title: string; lines: string[]; active: boolean; dim?: boolean }) {
  return (
    <g style={{ ...FADE, opacity: dim ? 0.45 : 1 }}>
      <rect x={x} y={y} width={w} height={h} rx={16} fill={active ? C.tealBg : C.paper} stroke={active ? C.teal : C.line} strokeWidth={active ? 3 : 1.5} style={FADE} />
      <text x={x + 22} y={y + 38} fontSize={22} fontWeight={700} fill={C.ink}>{title}</text>
      {lines.map((l, i) => <text key={l} x={x + 22} y={y + 70 + i * 26} fontSize={17} fill={C.body}>{l}</text>)}
    </g>
  )
}

function Chip({ y, title, line, tone }: { y: number; title: string; line: string; tone: 'amber' | 'faded' | 'teal' }) {
  const stroke = tone === 'amber' ? C.amber : tone === 'teal' ? C.teal : C.faint
  const fill = tone === 'amber' ? C.amberBg : tone === 'teal' ? C.tealBg : C.paper
  return (
    <g style={FADE}>
      <rect x={762} y={y} width={196} height={66} rx={12} fill={fill} stroke={stroke} strokeWidth={tone === 'faded' ? 1.5 : 2.5}
        strokeDasharray={tone === 'faded' ? '6 5' : undefined} style={FADE} />
      <text x={778} y={y + 27} fontSize={17} fontWeight={700} fill={tone === 'faded' ? C.muted : C.ink}>{title}</text>
      <text x={778} y={y + 50} fontSize={15} fill={tone === 'faded' ? C.muted : C.body}>{line}</text>
    </g>
  )
}

function Arrow({ d, label, lx, ly, show, color = C.teal, reverse = false }: { d: string; label: string; lx: number; ly: number; show: boolean; color?: string; reverse?: boolean }) {
  const id = color === C.teal ? 'eco-teal' : 'eco-grey'
  return (
    <g style={{ ...FADE, opacity: show ? 1 : 0 }}>
      <path d={d} fill="none" stroke={color} strokeWidth={4} markerEnd={reverse ? undefined : `url(#${id})`} markerStart={reverse ? `url(#${id})` : undefined} />
      <text x={lx} y={ly} fontSize={18} fontWeight={700} fill={color} textAnchor="middle" stroke="#fff" strokeWidth={6} paintOrder="stroke">{label}</text>
    </g>
  )
}

export function Ecosystem({ step }: { step: number }) {
  const m = bundle.market
  const inc = Math.round(100 * m.sigma_inc)
  const ent = Math.round(100 * m.sigma_ent)
  const fee = bundle.business.params.fee_eur_per_device_month
  const open = step >= 2
  return (
    <svg viewBox="0 0 1000 385" className="h-auto w-full" role="img"
      aria-label={step === 0 ? 'Today: the customer pays the incumbent per trip; only the incumbent knows the tonnes.'
        : 'With OpenWeight: the compactor weighs every lift, Europress gives every operator the same forecast, operators bid per kilo.'}>
      <defs>
        {[['eco-teal', C.teal], ['eco-grey', C.line]].map(([id, c]) => (
          <marker key={id} id={id} viewBox="0 0 10 10" refX={8} refY={5} markerWidth={5} markerHeight={5} orient="auto-start-reverse">
            <path d="M0,0 L10,5 L0,10 z" fill={c} />
          </marker>
        ))}
      </defs>

      <Box x={30} y={90} w={250} h={150} title="Customer" active={false}
        lines={step === 0 ? ['pays per truck visit', 'can’t see its tonnes'] : ['uses OpenWeight free', 'owns its data']} />
      <Box x={385} y={90} w={250} h={150} title="Europress" active={step >= 1} dim={step === 0}
        lines={step === 0 ? ['sells the compactor', 'then steps aside'] : ['compactor weighs', 'every lift']} />

      {/* operators: one group, three chips */}
      <g style={FADE}>
        <rect x={745} y={20} width={230} height={300} rx={18} fill="none" stroke={open ? C.teal : C.faint} strokeWidth={open ? 3 : 1.5} style={FADE} />
        <text x={860} y={14} fontSize={16} fontWeight={600} fill={C.muted} textAnchor="middle">Operators</text>
      </g>
      <Chip y={224} title="Incumbent" line={open ? `forecast ±${inc} %` : 'knows every tonne'} tone={open ? 'teal' : 'amber'} />
      <Chip y={36} title="Challenger A" line={open ? `forecast ±${inc} %` : `guesses ±${ent} %`} tone={open ? 'teal' : 'faded'} />
      <Chip y={130} title="Challenger B" line={open ? `forecast ±${inc} %` : `guesses ±${ent} %`} tone={open ? 'teal' : 'faded'} />

      {/* today: money goes to the incumbent; step 3: per-kg bids come back from the whole operator group */}
      <Arrow d="M155,240 C155,340 600,340 758,262" lx={450} ly={345} show={step === 0} color={C.line} label="trucks on schedule · € per trip" />
      <Arrow d="M155,240 C155,350 700,360 800,320" lx={450} ly={372} show={step >= 3} reverse label="per-kg bids · customer picks the best" />
      <Arrow d="M280,165 L380,165" lx={330} ly={150} show={step >= 1} label="weight" />
      <Arrow d="M635,165 L740,165" lx={690} ly={150} show={step >= 2} label="same data" />
      <text x={860} y={350} fontSize={16} fontWeight={600} fill={C.teal} textAnchor="middle" style={{ ...FADE, opacity: step >= 3 ? 1 : 0 }}>pay €{fee} / device / month</text>
    </svg>
  )
}

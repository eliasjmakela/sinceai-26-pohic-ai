import { bundle } from '../bundle'

/**
 * Who is in the system and what flows between them, today vs with OpenWeight. The same picture appears on the
 * first screen (today) and the last one (OpenWeight), so the audience sees exactly which arrows change.
 */
type Mode = 'today' | 'ow'

const C = {
  ink: '#0f172a', muted: '#64748b', line: '#94a3b8', faint: '#cbd5e1', paper: '#ffffff',
  teal: '#0f766e', tealBg: '#f0fdfa', violet: '#6d28d9', amber: '#b45309', amberBg: '#fffbeb', rose: '#be123c',
}

interface NodeSpec { x: number; y: number; w: number; h: number; title: string; lines: Record<Mode, string[]>; tone: Record<Mode, 'plain' | 'teal' | 'faded' | 'amber'>; badge?: Partial<Record<Mode, string>> }
interface EdgeSpec { d: string; label?: Partial<Record<Mode, string>>; lx: number; ly: number; style: Partial<Record<Mode, keyof typeof STROKE>>; anchor?: 'start' | 'middle' | 'end' }

function nodes(): NodeSpec[] {
  const m = bundle.market
  const ent = Math.round(100 * m.sigma_ent)
  return [
    { x: 30, y: 185, w: 250, h: 180, title: 'Customer site', tone: { today: 'plain', ow: 'plain' },
      lines: { today: ['retail, logistics, industry', 'pays per truck visit', 'cannot see its own tonnes'],
        ow: ['sees its weights and contract', 'uses OpenWeight free', 'owns its data'] },
      badge: { ow: 'free' } },
    { x: 425, y: 170, w: 250, h: 210, title: 'Europress', tone: { today: 'plain', ow: 'teal' },
      lines: { today: ['builds the compactor', 'SMART: fill level, service', 'sells the machine once'],
        ow: ['compactor weighs every lift', 'SMART + OpenWeight engine', 'same forecast for every operator', 'never drives a truck'] } },
    { x: 820, y: 40, w: 250, h: 110, title: 'Challenger A', tone: { today: 'faded', ow: 'plain' },
      lines: { today: [`guesses the site: ±${ent} %`, 'risk premium, rarely wins'], ow: ['prices per kg on real data', 'wins on efficiency'] } },
    { x: 820, y: 215, w: 250, h: 110, title: 'Challenger B', tone: { today: 'faded', ow: 'plain' },
      lines: { today: [`guesses the site: ±${ent} %`, 'risk premium, rarely wins'], ow: ['prices per kg on real data', 'wins on efficiency'] } },
    { x: 820, y: 390, w: 250, h: 110, title: 'Incumbent operator', tone: { today: 'amber', ow: 'plain' },
      lines: { today: ['the only one who knows', 'every site’s tonnes'], ow: ['keeps its routes and scale', 'competes on price'] },
      badge: { today: 'private site history' } },
    { x: 425, y: 445, w: 250, h: 85, title: 'Certified weighbridge', tone: { today: 'plain', ow: 'plain' },
      lines: { today: ['operator’s own scale'], ow: ['billing stays here, as today'] } },
  ]
}

function edges(): EdgeSpec[] {
  const inc = Math.round(100 * bundle.market.sigma_inc)
  const fee = bundle.business.params.fee_eur_per_device_month
  return [
    // compactor -> Europress
    { d: 'M280,245 L425,245', lx: 352, ly: 235, style: { today: 'solid', ow: 'flow' }, label: { today: 'fill level', ow: 'weight, every lift' } },
    // customer consent
    { d: 'M280,305 L425,305', lx: 352, ly: 325, style: { ow: 'solid' }, label: { ow: 'consent to share' } },
    // Europress -> operators: the same forecast for all
    { d: 'M675,215 C750,215 750,95 820,95', lx: 0, ly: 0, style: { ow: 'flow' } },
    { d: 'M675,262 L820,262', lx: 748, ly: 252, style: { ow: 'flow' }, label: { ow: `forecast ±${inc} %` } },
    { d: 'M675,300 C750,300 750,430 820,430', lx: 0, ly: 0, style: { ow: 'flow' } },
    // operators -> Europress: the fee
    { d: 'M820,357 L675,345', lx: 748, ly: 375, style: { ow: 'fee' }, label: { ow: `€${fee} / device / month` } },
    // operators -> customer: per-kg tenders
    { d: 'M905,40 C820,4 300,4 155,185', lx: 540, ly: 50, style: { today: 'faint', ow: 'flow' },
      label: { today: 'no safe per-kg bid from a challenger: the incumbent renews', ow: 'per-kg bids from every operator; the customer picks' } },
    // truck: site -> weighbridge
    { d: 'M240,365 C240,490 330,490 425,490', lx: 230, ly: 470, anchor: 'end', style: { today: 'solid', ow: 'solid' },
      label: { today: 'truck on schedule · € per trip', ow: 'truck when full · € per kg' } },
    // weighbridge -> incumbent: private tonnes (today) / certified bill (OpenWeight)
    { d: 'M675,480 L820,465', lx: 748, ly: 500, style: { today: 'solid', ow: 'solid' }, label: { today: 'tonnes stay private', ow: 'certified bill' } },
    // weighbridge tickets -> Europress: calibration and cross-check
    { d: 'M550,445 L550,380', lx: 558, ly: 418, anchor: 'start', style: { ow: 'ticket' }, label: { ow: 'tickets: calibrate, cross-check' } },
  ]
}

const STROKE = {
  flow: { stroke: C.teal, width: 3, dash: '7 6', marker: 'teal' },
  solid: { stroke: C.line, width: 2, dash: undefined, marker: 'grey' },
  fee: { stroke: C.violet, width: 2.5, dash: undefined, marker: 'violet' },
  ticket: { stroke: C.amber, width: 2.5, dash: '3 4', marker: 'amber' },
  faint: { stroke: C.faint, width: 2, dash: '4 6', marker: 'faint' },
} as const

function Node({ n, mode }: { n: NodeSpec; mode: Mode }) {
  const tone = n.tone[mode]
  const fill = tone === 'teal' ? C.tealBg : tone === 'amber' ? C.amberBg : C.paper
  const stroke = tone === 'teal' ? C.teal : tone === 'amber' ? C.amber : tone === 'faded' ? C.faint : C.line
  const ink = tone === 'faded' ? C.muted : C.ink
  const badge = n.badge?.[mode]
  return (
    <g className="eco-fade">
      <rect x={n.x} y={n.y} width={n.w} height={n.h} rx={14} fill={fill} stroke={stroke} strokeWidth={tone === 'plain' || tone === 'faded' ? 1.5 : 2.5}
        strokeDasharray={tone === 'faded' ? '6 5' : undefined} style={{ transition: 'all 400ms ease' }} />
      <text x={n.x + 18} y={n.y + 30} fontSize={18} fontWeight={700} fill={ink}>{n.title}</text>
      {n.lines[mode].map((l, i) => (
        <text key={`${mode}-${l}`} x={n.x + 18} y={n.y + 56 + i * 21} fontSize={14.5} fill={tone === 'faded' ? C.muted : '#334155'} className="eco-in">{l}</text>
      ))}
      {badge && (
        <g className="eco-in">
          <rect x={n.x + n.w - 14 - (badge.length * 7.4 + 20)} y={n.y - 13} width={badge.length * 7.4 + 20} height={26} rx={13}
            fill={mode === 'ow' ? C.teal : C.amber} />
          <text x={n.x + n.w - 14 - (badge.length * 7.4 + 20) / 2} y={n.y + 5} fontSize={13} fontWeight={600} fill="#fff" textAnchor="middle">{badge}</text>
        </g>
      )}
    </g>
  )
}

export function Ecosystem({ mode }: { mode: Mode }) {
  return (
    <svg viewBox="0 0 1100 545" className="h-auto w-full" role="img"
      aria-label={mode === 'today' ? 'Today: only the incumbent operator knows the tonnes; challengers guess.' : 'With OpenWeight: Europress shares the same weight-based forecast with every operator; customers choose per-kg bids.'}>
      <defs>
        {Object.entries({ teal: C.teal, grey: C.line, violet: C.violet, amber: C.amber, faint: C.faint }).map(([k, c]) => (
          <marker key={k} id={`arrow-${k}`} viewBox="0 0 10 10" refX={9} refY={5} markerWidth={7} markerHeight={7} orient="auto-start-reverse">
            <path d="M0,0 L10,5 L0,10 z" fill={c} />
          </marker>
        ))}
      </defs>
      {edges().map((e) => {
        const kind = e.style[mode]
        const s = kind ? STROKE[kind] : null
        const label = e.label?.[mode]
        return (
          <g key={e.d} style={{ opacity: s ? 1 : 0, transition: 'opacity 400ms ease' }}>
            <path d={e.d} fill="none" stroke={s?.stroke ?? C.line} strokeWidth={s?.width ?? 2} strokeDasharray={s?.dash}
              markerEnd={s ? `url(#arrow-${s.marker})` : undefined} className={kind === 'flow' ? 'eco-flow' : undefined} />
            {label && (
              <text x={e.lx} y={e.ly} fontSize={14} fontWeight={600} textAnchor={e.anchor ?? 'middle'} fill={s?.stroke === C.line || s?.stroke === C.faint ? C.muted : s?.stroke}
                stroke="#f8fafc" strokeWidth={5} paintOrder="stroke" className="eco-in">{label}</text>
            )}
          </g>
        )
      })}
      {nodes().map((n) => <Node key={n.title} n={n} mode={mode} />)}
    </svg>
  )
}

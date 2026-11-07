import { useEffect, useRef, useState } from 'react'
import { bundle } from '../bundle'

/**
 * H7 hydraulic self-lift (part1/WEIGHING_CONCEPT.md §19): side view of a COMBI that lifts its own door end ~10 mm on
 * a cylinder driven by its power pack. Pressure × piston area = door-end reaction R; W = (R − R0) · L / x_w.
 * Numbers come from the bundle (`weighing.h7.example`, computed by pipeline/fullload/weighing.py).
 */
const GROUND = 300
const PIVOT_X = 140
const CYL_X = 680
const TILT_DEG = 2.5 // exaggerated: the real lift is 10 mm
const LIFT_PX = (CYL_X - PIVOT_X) * Math.sin((TILT_DEG * Math.PI) / 180)
const HOLD_MS = 2600

type Step = 'tare' | 'reading'

export function H7Diagram() {
  const ex = bundle.weighing.h7.example
  const L = CYL_X - PIVOT_X
  const xW = PIVOT_X + ex.x_w_over_l * L
  const xM = PIVOT_X + ex.door_end_share * L
  const [loaded, setLoaded] = useState(false)
  const [lifted, setLifted] = useState(false)
  const [done, setDone] = useState<Record<Step, boolean>>({ tare: false, reading: false })
  const timer = useRef<number | undefined>(undefined)
  useEffect(() => () => window.clearTimeout(timer.current), [])

  const measure = (step: Step) => {
    window.clearTimeout(timer.current)
    setLoaded(step === 'reading')
    setLifted(true)
    timer.current = window.setTimeout(() => {
      setLifted(false)
      setDone((d) => ({ ...d, [step]: true }))
    }, HOLD_MS)
  }
  const bar = lifted ? (loaded ? ex.loaded_bar : ex.tare_bar) : 0
  const needle = -120 + (240 * Math.min(bar, 200)) / 200
  const diffBar = ex.loaded_bar - ex.tare_bar

  return (
    <div className="grid items-center gap-6 lg:grid-cols-[1fr_17rem]">
      <svg viewBox="0 6 900 379" className="h-auto w-full" role="img"
        aria-label="Side view of a compactor container. A cylinder near the door end lifts it 10 mm about the front of its runners; the cylinder pressure gives the weight.">
        <defs>
          <pattern id="waste" width="10" height="10" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
            <rect width="10" height="10" fill="#fde68a" /><line x1="0" y1="0" x2="0" y2="10" stroke="#f59e0b" strokeWidth="3" />
          </pattern>
          <marker id="h7-up" viewBox="0 0 10 10" refX={5} refY={1} markerWidth={8} markerHeight={8} orient="auto">
            <path d="M0,10 L5,0 L10,10 z" fill="#0f766e" />
          </marker>
          <marker id="h7-down" viewBox="0 0 10 10" refX={5} refY={9} markerWidth={8} markerHeight={8} orient="auto">
            <path d="M0,0 L5,10 L10,0 z" fill="#475569" />
          </marker>
        </defs>

        {/* ground */}
        <line x1={20} y1={GROUND} x2={880} y2={GROUND} stroke="#475569" strokeWidth={2} />
        {Array.from({ length: 43 }, (_, i) => (
          <line key={i} x1={24 + i * 20} y1={GROUND + 1} x2={14 + i * 20} y2={GROUND + 11} stroke="#cbd5e1" strokeWidth={1.5} />
        ))}

        {/* rod and foot stay on the ground while the body tilts */}
        <rect x={CYL_X - 6} y={GROUND - 4 - (lifted ? LIFT_PX : 0)} width={12} height={4 + (lifted ? LIFT_PX : 0)} fill="#0f766e"
          style={{ transition: 'all 1.2s ease-in-out' }} />
        <rect x={CYL_X - 20} y={GROUND - 5} width={40} height={6} rx={2} fill="#134e4a" />

        {/* the compactor, tilting about the front of its runners */}
        <g style={{ transform: `rotate(${lifted ? -TILT_DEG : 0}deg)`, transformOrigin: `${PIVOT_X}px ${GROUND}px`, transition: 'transform 1.2s ease-in-out' }}>
          <rect x={150} y={110} width={612} height={172} rx={6} fill="#f1f5f9" stroke="#64748b" strokeWidth={2} />
          <rect x={150} y={110} width={140} height={172} rx={6} fill="#cbd5e1" stroke="#64748b" strokeWidth={2} />
          <text x={220} y={190} fontSize={16} fill="#334155" textAnchor="middle">press +</text>
          <text x={220} y={208} fontSize={16} fill="#334155" textAnchor="middle">power pack</text>
          <rect x={752} y={110} width={12} height={172} fill="#334155" />
          <text x={758} y={100} fontSize={15} fill="#475569" textAnchor="middle">door</text>
          <text x={160} y={100} fontSize={15} fill="#475569">hook end</text>
          <rect x={296} y={150} width={452} height={128} fill="url(#waste)" style={{ opacity: loaded ? 1 : 0, transition: 'opacity 500ms' }} />
          <rect x={130} y={282} width={640} height={14} rx={3} fill="#334155" />
          {/* cylinder housing in the rear frame */}
          <rect x={CYL_X - 14} y={262} width={28} height={34} rx={3} fill="#0f766e" />
          {/* weights */}
          <line x1={xM} y1={58} x2={xM} y2={104} stroke="#475569" strokeWidth={2.5} markerEnd="url(#h7-down)" />
          <text x={xM} y={50} fontSize={15} fill="#334155" textAnchor="middle">machine M</text>
          <g style={{ opacity: loaded ? 1 : 0, transition: 'opacity 500ms' }}>
            <circle cx={xW} cy={214} r={6} fill="#b45309" />
            <line x1={xW} y1={220} x2={xW} y2={262} stroke="#b45309" strokeWidth={2.5} markerEnd="url(#h7-down)" />
            <text x={xW + 12} y={208} fontSize={16} fontWeight={600} fill="#92400e">waste W</text>
          </g>
        </g>

        {/* pivot */}
        <polygon points={`${PIVOT_X - 11},${GROUND + 15} ${PIVOT_X + 11},${GROUND + 15} ${PIVOT_X},${GROUND}`} fill="#0f766e" />
        <text x={PIVOT_X - 18} y={GROUND + 30} fontSize={15} fill="#0f766e" textAnchor="middle">pivot</text>

        {/* reaction arrow */}
        <line x1={CYL_X + 34} y1={GROUND + 72} x2={CYL_X + 34} y2={GROUND + 8} stroke="#0f766e" strokeWidth={3} markerEnd="url(#h7-up)" />
        <text x={CYL_X + 44} y={GROUND + 50} fontSize={16} fontWeight={600} fill="#0f766e">R = pressure × area</text>

        {/* dimensions */}
        {[{ y: GROUND + 46, x2: CYL_X, t: 'L' }, { y: GROUND + 68, x2: xW, t: 'x_w' }].map((d) => (
          <g key={d.t} style={{ opacity: d.t === 'x_w' && !loaded ? 0.35 : 1 }}>
            <line x1={PIVOT_X} y1={d.y} x2={d.x2} y2={d.y} stroke="#64748b" strokeWidth={1.2} />
            <line x1={PIVOT_X} y1={d.y - 5} x2={PIVOT_X} y2={d.y + 5} stroke="#64748b" />
            <line x1={d.x2} y1={d.y - 5} x2={d.x2} y2={d.y + 5} stroke="#64748b" />
            <text x={(PIVOT_X + d.x2) / 2} y={d.y - 4} fontSize={15} fill="#334155" textAnchor="middle" fontStyle="italic">{d.t}</text>
          </g>
        ))}

        {/* pressure gauge */}
        <line x1={CYL_X} y1={262} x2={812} y2={112} stroke="#94a3b8" strokeDasharray="3 4" />
        <circle cx={830} cy={64} r={50} fill="#fff" stroke="#0f766e" strokeWidth={3} />
        <line x1={830} y1={64} x2={830} y2={26} stroke="#0f172a" strokeWidth={3} strokeLinecap="round"
          style={{ transform: `rotate(${needle}deg)`, transformOrigin: '830px 64px', transition: 'transform 1s ease-out' }} />
        <circle cx={830} cy={64} r={5} fill="#0f172a" />
        <text x={830} y={98} fontSize={18} fontWeight={700} fill="#0f172a" textAnchor="middle">{bar} bar</text>
      </svg>

      <div className="space-y-3 text-sm">
        <button type="button" onClick={() => measure('tare')}
          className="w-full rounded-lg border border-slate-300 bg-white px-4 py-2 text-left font-medium text-slate-800 hover:border-teal-600">1 · Empty unit returns: tare</button>
        <button type="button" onClick={() => measure('reading')}
          className="w-full rounded-lg bg-teal-700 px-4 py-2 text-left font-medium text-white hover:bg-teal-800">2 · Full unit: reading</button>
        <div className="grid gap-2">
        <Step label="Tare, empty unit" value={done.tare ? `${ex.tare_bar} bar` : '—'} />
        <Step label="Reading, full unit" value={done.reading ? `${ex.loaded_bar} bar` : '—'} />
        <Step label="Waste W = (R − R₀) · L / x_w" strong
          value={done.tare && done.reading ? `${diffBar} bar × ${ex.kg_waste_per_bar} kg ≈ ${ex.waste_from_reading_t.toFixed(1)} t` : '—'} />
        </div>
        <p className="text-xs text-slate-500">Lift drawn exaggerated; the real lift is {bundle.weighing.h7.stroke_margin_mm} mm in ~15 s, then down at the same speed. Up and down readings are averaged to cancel seal friction.</p>
      </div>
    </div>
  )
}

function Step({ label, value, strong = false }: { label: string; value: string; strong?: boolean }) {
  return (
    <div className={`rounded-lg border p-3 ${strong ? 'border-teal-600 bg-teal-50' : 'border-slate-200 bg-white'}`}>
      <div className="text-xs text-slate-500">{label}</div>
      <div className="mt-1 text-xl font-semibold tabular-nums text-slate-900">{value}</div>
    </div>
  )
}

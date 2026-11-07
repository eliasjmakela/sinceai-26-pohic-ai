import type { ReactNode } from 'react'
import type { Tag } from '../bundle'
import { TAG_STYLE } from '../format'

/** Small shared pieces used by several screens. */

export function TagBadge({ tag }: { tag: Tag }) {
  return <span className={`inline-block rounded px-2 py-0.5 text-xs font-medium ${TAG_STYLE[tag]}`}>{tag}</span>
}

export function Card({ children, className = '' }: { children: ReactNode; className?: string }) {
  return <div className={`rounded-xl border border-slate-200 bg-white p-5 shadow-sm ${className}`}>{children}</div>
}

export function Slider(props: { label: string; value: number; min: number; max: number; step: number; fmt: (v: number) => string; onChange: (v: number) => void }) {
  return (
    <label className="block text-sm text-slate-600">
      <span className="flex justify-between"><span>{props.label}</span><span className="font-medium tabular-nums text-slate-900">{props.fmt(props.value)}</span></span>
      <input type="range" className="w-full accent-teal-700" min={props.min} max={props.max} step={props.step} value={props.value}
        onChange={(e) => props.onChange(Number(e.target.value))} />
    </label>
  )
}

/** A before/after number: shows today's value, or the simulated value with its change. */
export function Kpi({ label, before, after, fmt, showAfter }: { label: string; before: number; after: number; fmt: (v: number) => string; showAfter: boolean }) {
  const v = showAfter ? after : before
  const delta = before ? (after - before) / before : 0
  return (
    <Card>
      <div className="text-sm text-slate-500">{label}</div>
      <div className="mt-1 text-4xl font-semibold tabular-nums text-slate-900">{fmt(v)}</div>
      <div className="mt-2 h-5 text-sm tabular-nums">
        {showAfter && (before === 0
          ? <span className="text-teal-700">today: {fmt(before)}</span>
          : <span className={delta < 0 ? 'text-teal-700' : 'text-slate-600'}>{delta >= 0 ? '+' : ''}{(100 * delta).toFixed(1)} % vs today</span>)}
      </div>
      <TagBadge tag={showAfter ? 'simulated' : 'observed'} />
    </Card>
  )
}

/** Today ↔ OpenWeight switch, shared by the market screens. */
export function ModeToggle({ after, onChange }: { after: boolean; onChange: (after: boolean) => void }) {
  return (
    <div className="inline-flex rounded-lg border border-slate-300 bg-white p-1 text-sm font-medium">
      <button type="button" onClick={() => onChange(false)} className={`rounded-md px-4 py-2 ${!after ? 'bg-slate-900 text-white' : 'text-slate-600'}`}>Today: per trip, private data</button>
      <button type="button" onClick={() => onChange(true)} className={`rounded-md px-4 py-2 ${after ? 'bg-teal-700 text-white' : 'text-slate-600'}`}>OpenWeight: per kg, shared data</button>
    </div>
  )
}

const OPERATOR_COLORS = ['#0f766e', '#2563eb', '#a16207', '#7c3aed', '#db2777', '#475569']

/** Share of tonnes per operator as one stacked bar. */
export function ShareBar({ shares, ops }: { shares: Record<string, number>; ops: string[] }) {
  return (
    <div className="flex h-8 w-full overflow-hidden rounded">
      {ops.map((o, i) => shares[o] > 0.001 && (
        <div key={o} style={{ width: `${100 * shares[o]}%`, background: OPERATOR_COLORS[i % OPERATOR_COLORS.length] }}
          className="flex items-center justify-center text-xs font-medium text-white" title={`${o} ${(100 * shares[o]).toFixed(0)} %`}>
          {shares[o] > 0.08 ? `${o} ${(100 * shares[o]).toFixed(0)} %` : ''}
        </div>
      ))}
    </div>
  )
}

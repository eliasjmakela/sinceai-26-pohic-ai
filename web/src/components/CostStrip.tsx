import { bundle } from '../bundle'

/** Installed cost per weighing concept (factory fit, incl. 6-year upkeep) against the ~€2k reference from kickoff. */
const SHORT: Record<string, string> = {
  T0: 'Virtual scale', H1: 'Hopper plate', H7: 'Hydraulic self-lift', PS: 'Platform scale',
}
const MAX = 8000

export function CostStrip() {
  const c = bundle.weighing.installed_cost
  const pct = (v: number) => `${(100 * Math.min(v, MAX)) / MAX}%`
  return (
    <div className="space-y-2 text-sm">
      {c.strip.map((k) => {
        const [lo, hi] = k.factory_fit_eur
        return (
          <div key={k.id} className="grid grid-cols-[8rem_1fr_6.5rem] items-center gap-3">
            <div className={k.id === 'H7' ? 'font-semibold text-teal-800' : 'text-slate-600'}>{SHORT[k.id] ?? k.name}</div>
            <div className="relative h-6 rounded bg-slate-100">
              <div className="absolute top-0 h-full border-l-2 border-dashed border-rose-500" style={{ left: pct(c.reference_eur) }} />
              <div className={`absolute top-1 h-4 rounded ${k.id === 'H7' ? 'bg-teal-700' : 'bg-slate-400'}`}
                style={{ left: pct(lo), width: `max(4px, calc(${pct(hi)} - ${pct(lo)}))` }} />
            </div>
            <div className="text-right text-xs tabular-nums text-slate-700">€{lo.toLocaleString('en')}–{hi.toLocaleString('en')}{hi > MAX ? ' →' : ''}</div>
          </div>
        )
      })}
      <div className="text-xs text-rose-600">dashed: ~€{c.reference_eur.toLocaleString('en')} per device, the reference named at kickoff</div>
    </div>
  )
}

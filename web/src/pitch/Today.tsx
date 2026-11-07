import { bundle } from '../bundle'
import { FigureValue } from '../components/FigureValue'
import { Card, TagBadge } from '../components/ui'

/** Pitch screen 1 — the market today: customers pay per visit, so a half-empty visit costs far more per tonne.
 * The ecosystem diagram starts on screen 3. */
const FILL = [40, 75, 95] // drawn fill level per band (illustrative)
const SHORT = ['under 60 % full', '60–90 % full', '90–100 % full']

function Compactor({ fill }: { fill: number }) {
  const h = 70
  return (
    <svg viewBox="0 0 120 84" className="h-16 w-24" aria-hidden>
      <rect x={4} y={4} width={112} height={h} rx={6} fill="#f1f5f9" stroke="#64748b" strokeWidth={2} />
      <rect x={6} y={4 + h - (h - 4) * (fill / 100) - 2} width={108} height={(h - 4) * (fill / 100)} rx={4} fill="#f59e0b" opacity={0.8} />
      <rect x={0} y={74} width={120} height={8} rx={3} fill="#334155" />
    </svg>
  )
}

export function Today() {
  const f = bundle.fleet
  const m = bundle.market
  const bands = f.visit_cost_by_fill
  const max = Math.max(...bands.map((b) => b.eur_per_t.value ?? 0))
  const ratio = (bands[0].eur_per_t.value ?? 0) / (bands[bands.length - 1].eur_per_t.value ?? 1)
  return (
    <section className="space-y-6">
      <header>
        <div className="text-sm font-medium uppercase tracking-wide text-slate-500">1 · The market today</div>
        <h1 className="mt-1 text-4xl font-bold text-slate-900">Customers pay per truck visit, not per tonne.</h1>
        <p className="mt-2 max-w-3xl text-lg text-slate-600">
          A visit costs the same whether the compactor is half empty or full. Only the incumbent knows the tonnes.
        </p>
      </header>

      <div className="grid gap-4 lg:grid-cols-[2fr_1fr]">
        <Card>
          <div className="flex items-start justify-between gap-3">
            <div className="text-lg font-semibold text-slate-900">{ratio.toFixed(1)}× the price per tonne when it's half empty</div>
            <TagBadge tag="estimated" />
          </div>
          <div className="mt-4 grid grid-cols-3 gap-4">
            {bands.map((b, i) => (
              <div key={b.band} className="flex flex-col items-center text-center">
                <Compactor fill={FILL[i]} />
                <div className="mt-2 text-base font-medium text-slate-700">{SHORT[i]}</div>
                <div className="text-sm text-slate-500">€{b.visit_eur.value} / visit</div>
                <div className="mt-3 flex h-28 w-14 items-end rounded bg-slate-100">
                  <div className={`w-full rounded ${i === 0 ? 'bg-rose-600' : 'bg-slate-400'}`} style={{ height: `${(100 * (b.eur_per_t.value ?? 0)) / max}%` }} />
                </div>
                <div className={`mt-2 text-3xl font-semibold tabular-nums ${i === 0 ? 'text-rose-700' : 'text-slate-900'}`}>€{Math.round(b.eur_per_t.value ?? 0)}</div>
                <div className="text-xs text-slate-500">per tonne</div>
              </div>
            ))}
          </div>
          <p className="mt-4 text-xs text-slate-500">Per-visit charges ÷ tonnes collected, one year of invoices (synthetic). Real HSY data shows the same pattern: about a third of emptyings happen below 50 % full (Paananen, LUT 2024).</p>
        </Card>
        <div className="grid content-start gap-4">
          <FigureValue figure={f.trip_share_pct} label="of all charges are per visit, not per tonne" />
          <FigureValue figure={m.headline.contestable_before} label={`of ${m.inputs.length} customers in region ${m.region} a challenger can safely win today`} />
        </div>
      </div>

    </section>
  )
}

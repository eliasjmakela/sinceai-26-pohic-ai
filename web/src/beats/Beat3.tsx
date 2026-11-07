import { bundle } from '../bundle'

/** Beat 3 — the same customer through an operator's eyes (PRODUCT.md §4). */
const eur = (v: number) => `€${Math.round(v).toLocaleString('en')}`

function BidBars({ bids, today, highlight, title }: { bids: Record<string, number>; today: number; highlight?: string; title: string }) {
  const entries = Object.entries(bids).sort((a, b) => a[1] - b[1])
  const max = Math.max(today, ...entries.map(([, v]) => v)) * 1.05
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="mb-3 text-sm text-slate-500">{title}</div>
      <div className="space-y-2">
        {entries.map(([o, v]) => (
          <div key={o} className="flex items-center gap-3 text-sm">
            <div className="w-14 text-slate-600">{o}</div>
            <div className="relative h-6 flex-1 rounded bg-slate-100">
              <div className={`h-6 rounded ${o === highlight ? 'bg-teal-700' : 'bg-slate-400'}`} style={{ width: `${(100 * v) / max}%` }} />
              <div className="absolute top-0 h-6 border-l-2 border-dashed border-rose-500" style={{ left: `${(100 * today) / max}%` }} />
            </div>
            <div className="w-20 text-right tabular-nums">{eur(v)}</div>
          </div>
        ))}
      </div>
      <div className="mt-2 text-xs text-rose-600">dashed line: what the customer pays today ({eur(today)})</div>
    </div>
  )
}

export function Beat3() {
  const h = bundle.hero
  const o = h.operator_view
  return (
    <section className="space-y-6">
      <header>
        <div className="text-sm font-medium uppercase tracking-wide text-teal-700">Operator view · paid service</div>
        <h1 className="text-4xl font-bold text-slate-900">Without the data, only the incumbent can bid per kilo.</h1>
        <p className="mt-2 text-lg text-slate-600">{h.customer_name}, seen by an operator pricing the next tender.</p>
      </header>

      <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
        <div className="mb-3 text-sm text-slate-500">Forecast of each compactor's monthly tonnes (held-out months) — with its own history vs. guessed from similar compactors</div>
        <table className="w-full text-sm tabular-nums">
          <thead className="text-left text-slate-500">
            <tr><th className="py-1">Compactor</th><th>Actual t/month</th><th>With OpenWeight data</th><th>Error</th><th>Guess from peers</th><th>Error</th></tr>
          </thead>
          <tbody>
            {o.devices.map((d) => (
              <tr key={d.device_id} className="border-t border-slate-100">
                <td className="py-1">{d.device_id}</td>
                <td>{d.actual_t_per_month.toFixed(2)}</td>
                <td>{d.own_forecast_t_per_month.toFixed(2)}</td>
                <td className="text-teal-700">{d.own_error_pct.toFixed(1)} %</td>
                <td>{d.peer_forecast_t_per_month.toFixed(2)}</td>
                <td className="text-amber-700">{d.peer_error_pct.toFixed(1)} %</td>
              </tr>
            ))}
          </tbody>
        </table>
        <p className="mt-3 text-sm text-slate-600">
          Median error here: {o.own_error_median_pct.toFixed(1)} % with the data vs {o.peer_error_median_pct.toFixed(1)} % without. Fleet-wide
          backtest: ±{(100 * o.sigma_inc).toFixed(0)} % vs ±{(100 * o.sigma_ent).toFixed(0)} %. An operator who guesses must add a risk premium to a per-kg bid.
        </p>
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <BidBars title="Per-kg bids today: challengers must guess the volume (incumbent keeps the contract)" bids={o.bids_before_eur} today={o.price_today_eur} />
        <BidBars title={`Per-kg bids with OpenWeight data: ${o.winner_after} wins at ${eur(o.price_after_eur)}`} bids={o.bids_after_eur} today={o.price_today_eur} highlight={o.winner_after} />
      </div>
      <p className="text-xs text-slate-500">Bids are simulated with the hypothetical assumptions of the market model (beat 4); operators are fictional.</p>
    </section>
  )
}

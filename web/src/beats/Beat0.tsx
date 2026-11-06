import { Bar, BarChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { bundle } from '../bundle'
import { FigureValue } from '../components/FigureValue'

/** Beat 0 — "Paid per trip" (PRODUCT.md §4). */
export function Beat0() {
  const f = bundle.fleet
  const hist = f.fill_at_lift_histogram.map((b) => ({ ...b, label: `${b.bin_pct}–${b.bin_pct + 10} %` }))
  return (
    <section className="space-y-8">
      <header>
        <h1 className="text-4xl font-bold text-slate-900">Customers pay for trips, not tonnes.</h1>
        <p className="mt-2 text-lg text-slate-600">
          {f.devices.value} compactors, one year. Only the operator knows the weight.
        </p>
      </header>
      <div className="grid gap-4 sm:grid-cols-3">
        <FigureValue figure={f.trip_share_pct} label="of all charges are paid per trip" />
        <FigureValue figure={f.low_fill_lift_share_pct} label="of lifts empty a container under 60 % full" />
        <FigureValue figure={f.tonnes_per_year} label="collected per year" />
      </div>
      <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
        <div className="mb-3 text-sm text-slate-500">Lifts by fill level at the moment of emptying</div>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={hist}>
              <XAxis dataKey="label" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip />
              <Bar dataKey="lifts" fill="#0f766e" isAnimationActive={false} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </section>
  )
}

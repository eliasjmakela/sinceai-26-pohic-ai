import { useMemo, useState } from 'react'
import { bundle } from '../bundle'
import { FigureValue } from '../components/FigureValue'
import { simulate, type Params } from '../market/model'

/** Beat 4 — the market, before ↔ after (PRODUCT.md §3, §4). Slider maths: web/src/market/model.ts (parity-checked). */
const COLORS = ['#0f766e', '#2563eb', '#a16207', '#7c3aed', '#db2777', '#475569']

function Slider(props: { label: string; value: number; min: number; max: number; step: number; fmt: (v: number) => string; onChange: (v: number) => void }) {
  return (
    <label className="block text-sm text-slate-600">
      <span className="flex justify-between"><span>{props.label}</span><span className="tabular-nums font-medium text-slate-900">{props.fmt(props.value)}</span></span>
      <input type="range" className="w-full accent-teal-700" min={props.min} max={props.max} step={props.step}
        value={props.value} onChange={(e) => props.onChange(Number(e.target.value))} />
    </label>
  )
}

function Kpi({ label, before, after, fmt, showAfter }: { label: string; before: number; after: number; fmt: (v: number) => string; showAfter: boolean }) {
  const v = showAfter ? after : before
  const delta = before ? (after - before) / before : 0
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="text-sm text-slate-500">{label}</div>
      <div className="mt-1 text-4xl font-semibold tabular-nums text-slate-900">{fmt(v)}</div>
      <div className="mt-2 h-5 text-sm tabular-nums">
        {showAfter && (before === 0
          ? <span className="text-teal-700">today: {fmt(before)}</span>
          : <span className={delta < 0 ? 'text-teal-700' : 'text-slate-600'}>{delta >= 0 ? '+' : ''}{(100 * delta).toFixed(1)} % vs today</span>)}
      </div>
      <span className={`inline-block rounded px-2 py-0.5 text-xs font-medium ${showAfter ? 'bg-amber-100 text-amber-800' : 'bg-emerald-100 text-emerald-800'}`}>
        {showAfter ? 'simulated' : 'observed'}
      </span>
    </div>
  )
}

function ShareBar({ shares, ops }: { shares: Record<string, number>; ops: string[] }) {
  return (
    <div className="flex h-8 w-full overflow-hidden rounded">
      {ops.map((o, i) => shares[o] > 0.001 && (
        <div key={o} style={{ width: `${100 * shares[o]}%`, background: COLORS[i % COLORS.length] }}
          className="flex items-center justify-center text-xs font-medium text-white" title={`${o} ${(100 * shares[o]).toFixed(0)} %`}>
          {shares[o] > 0.08 ? `${o} ${(100 * shares[o]).toFixed(0)} %` : ''}
        </div>
      ))}
    </div>
  )
}

export function Beat4() {
  const m = bundle.market
  const [after, setAfter] = useState(true)
  const [p, setP] = useState<Params>(m.params)
  const set = (k: keyof Params) => (v: number) => setP({ ...p, [k]: v })
  const res = useMemo(() => simulate(m.inputs, m.operators, m.sigma_inc, m.sigma_ent, p), [m, p])
  const s = res.summary
  const ops = Object.keys(s.share_after)
  const eurT = (c: number) => `€${(c / 100).toFixed(0)}/t`
  return (
    <section className="space-y-6">
      <header className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-4xl font-bold text-slate-900">Same waste, fewer trucks, real competition.</h1>
          <p className="mt-2 text-lg text-slate-600">
            Region {m.region}: {s.accounts} customers, {Math.round(s.tonnes).toLocaleString('en')} t/year, {m.operators.length} fictional operators.
          </p>
        </div>
        <div className="inline-flex rounded-lg border border-slate-300 bg-white p-1 text-sm font-medium">
          <button type="button" onClick={() => setAfter(false)} className={`rounded-md px-4 py-2 ${!after ? 'bg-slate-900 text-white' : 'text-slate-600'}`}>Today: per trip, private data</button>
          <button type="button" onClick={() => setAfter(true)} className={`rounded-md px-4 py-2 ${after ? 'bg-teal-700 text-white' : 'text-slate-600'}`}>FullLoad: per kg, shared data</button>
        </div>
      </header>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Kpi label="Customer cost per tonne" before={s.cost_per_t_before} after={s.cost_per_t_after} fmt={eurT} showAfter={after} />
        <Kpi label="Truck visits per year" before={s.lifts_before} after={s.lifts_after} fmt={(v) => v.toLocaleString('en')} showAfter={after} />
        <Kpi label="Tonnes per visit" before={s.t_per_lift_before} after={s.t_per_lift_after} fmt={(v) => v.toFixed(2)} showAfter={after} />
        <Kpi label="Customers a challenger can win" before={s.accounts_contestable_today} after={s.accounts_contestable_after} fmt={(v) => `${v} / ${s.accounts}`} showAfter={after} />
      </div>

      {bundle.validation.trips_check && (
        <p className="text-sm text-slate-600">
          Fewer visits is a range: the dataset itself labels {bundle.validation.trips_check.labelled_premature_pct} % of lifts as unjustified
          today (lower bound); a weight trigger removes up to {bundle.validation.trips_check.model_removed_pct} % (validation period, per-device
          agreement r = {bundle.validation.trips_check.per_device_pearson}).
        </p>
      )}

      <div className="grid gap-4 lg:grid-cols-3">
        <div className="space-y-4 rounded-xl border border-slate-200 bg-white p-5 shadow-sm lg:col-span-2">
          <div>
            <div className="mb-2 text-sm text-slate-500">Who serves the tonnes — today</div>
            <ShareBar shares={s.share_before} ops={ops} />
          </div>
          <div>
            <div className="mb-2 text-sm text-slate-500">Who wins the per-kg tenders — FullLoad ({s.accounts_switched} of {s.accounts} customers switch)</div>
            <ShareBar shares={after ? s.share_after : s.share_before} ops={ops} />
          </div>
          <p className="text-sm text-slate-600">
            Today a challenger forecasts a site from peers (±{(100 * m.sigma_ent).toFixed(0)} %) and must add a risk premium; the incumbent
            knows the site (±{(100 * m.sigma_inc).toFixed(0)} %). With FullLoad data everyone forecasts at ±{(100 * res.sigmaAfter).toFixed(0)} %,
            so price follows efficiency, not history.
          </p>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>Operator margin: <b className="tabular-nums">€{Math.round((after ? s.operator_margin_after : s.operator_margin_before) / 100).toLocaleString('en')}</b></div>
            <div>Europress fee: <b className="tabular-nums">€{Math.round((after ? s.europress_fee : 0) / 100).toLocaleString('en')}</b></div>
          </div>
        </div>
        <div className="space-y-4 rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <div className="flex items-center justify-between">
            <div className="text-sm font-medium text-slate-900">Assumptions</div>
            <span className="rounded bg-rose-100 px-2 py-0.5 text-xs font-medium text-rose-800">hypothetical</span>
          </div>
          <Slider label="New entrants" value={p.new_entrants} min={0} max={3} step={1} fmt={(v) => `${v}`} onChange={set('new_entrants')} />
          <Slider label="Entrant cost advantage" value={p.entrant_cost_advantage} min={0} max={0.15} step={0.01} fmt={(v) => `${(100 * v).toFixed(0)} %`} onChange={set('entrant_cost_advantage')} />
          <Slider label="Sensor error (Part 1)" value={p.sigma_sensor} min={0} max={0.15} step={0.005} fmt={(v) => `±${(100 * v).toFixed(1)} %`} onChange={set('sigma_sensor')} />
          <Slider label="Risk aversion (σ priced in)" value={p.risk_z} min={0} max={2} step={0.1} fmt={(v) => v.toFixed(1)} onChange={set('risk_z')} />
          <Slider label="Europress fee" value={p.europress_fee_cents_per_t} min={0} max={1000} step={50} fmt={(v) => `€${(v / 100).toFixed(1)}/t`} onChange={set('europress_fee_cents_per_t')} />
          <button type="button" onClick={() => setP(m.params)} className="text-xs text-slate-500 underline">reset</button>
        </div>
      </div>
      <div className="grid gap-4 sm:grid-cols-3">
        <FigureValue figure={m.headline.cost_per_t_before} label="Today's cost per tonne (receipt)" />
        <FigureValue figure={m.headline.lifts_after} label="Weight-triggered visits, default assumptions (receipt)" />
        <FigureValue figure={m.headline.contestable_after} label="Contestable customers, default assumptions (receipt)" />
      </div>
    </section>
  )
}

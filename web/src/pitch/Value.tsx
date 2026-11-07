import { useMemo, useState } from 'react'
import { bundle } from '../bundle'
import { Ecosystem } from '../components/Ecosystem'
import { Card, Kpi, ModeToggle, TagBadge } from '../components/ui'
import { simulate } from '../market/model'

/** Pitch screen 3 — the value: the same picture with OpenWeight, the market result, and what each party gets. */
const eur = (v: number) => (v >= 1e6 ? `€${(v / 1e6).toFixed(1)} M` : `€${Math.round(v).toLocaleString('en')}`)

function Party({ who, pays, lines, tag }: { who: string; pays: string; lines: string[]; tag: 'simulated' | 'hypothetical' }) {
  return (
    <Card>
      <div className="flex items-start justify-between gap-2">
        <div><div className="text-lg font-semibold text-slate-900">{who}</div><div className="text-sm text-teal-800">{pays}</div></div>
        <TagBadge tag={tag} />
      </div>
      <ul className="mt-3 list-disc space-y-1 pl-5 text-sm text-slate-700">{lines.map((l) => <li key={l}>{l}</li>)}</ul>
    </Card>
  )
}

export function Value() {
  const m = bundle.market
  const [after, setAfter] = useState(true)
  const s = useMemo(() => simulate(m.inputs, m.operators, m.sigma_inc, m.sigma_ent, m.params).summary, [m])
  const t = bundle.validation.trips_check
  const svc = bundle.hero.service_check
  const biz = bundle.business
  const r = biz.default
  const perT = (c: number) => `€${(c / 100).toFixed(0)}/t`
  const saving = Math.round((100 * (s.cost_per_t_before - s.cost_per_t_after)) / s.cost_per_t_before)
  return (
    <section className="space-y-6">
      <header className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <div className="text-sm font-medium uppercase tracking-wide text-teal-700">3 · The value</div>
          <h1 className="mt-1 text-4xl font-bold text-slate-900">Same waste, fewer trucks, open competition.</h1>
          <p className="mt-2 text-lg text-slate-600">Europress shares the weight with every operator. It never drives a truck.</p>
        </div>
        <ModeToggle after={after} onChange={setAfter} />
      </header>

      <Card><Ecosystem mode={after ? 'ow' : 'today'} /></Card>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Kpi label="Customer cost per tonne" before={s.cost_per_t_before} after={s.cost_per_t_after} fmt={perT} showAfter={after} />
        <Kpi label="Truck visits per year" before={s.lifts_before} after={s.lifts_after} fmt={(v) => v.toLocaleString('en')} showAfter={after} />
        <Kpi label="Tonnes per visit" before={s.t_per_lift_before} after={s.t_per_lift_after} fmt={(v) => v.toFixed(2)} showAfter={after} />
        <Kpi label="Customers a challenger can win" before={s.accounts_contestable_today} after={s.accounts_contestable_after} fmt={(v) => `${v} / ${s.accounts}`} showAfter={after} />
      </div>

      <div className="grid gap-4 lg:grid-cols-3">
        <Party who="Customer" pays="pays nothing for OpenWeight" tag="simulated" lines={[
          `about ${saving} % less per tonne after a per-kg tender (region ${m.region})`,
          ...(t ? [`${t.labelled_premature_pct}–${t.model_removed_pct} % fewer truck visits`] : []),
          ...(svc ? [`sees whether the contract is kept: ${svc.on_time_share_pct} % of visits on time, ${eur(svc.invoice_above_contract_eur)} invoiced above contract`] : []),
        ]} />
        <Party who="Operators" pays={`pay €${biz.params.fee_eur_per_device_month} per device per month`} tag="simulated" lines={[
          `forecast any site at ±${Math.round(100 * m.sigma_inc)} %, not ±${Math.round(100 * m.sigma_ent)} %`,
          'bid per kilo without a risk premium',
          'win customers on efficiency, run fuller trucks',
        ]} />
        <Party who="Europress" pays="becomes a service company" tag="hypothetical" lines={[
          `${eur(r.service_revenue)} service revenue a year (${biz.params.devices_total.toLocaleString('en')} devices, ${Math.round(100 * biz.params.paying_coverage)} % with a paying operator)`,
          `weighing investment ${eur(r.investment)}, paid back in ${r.payback_years === null ? 'never' : r.payback_years.toFixed(1)} years`,
          'operators recommend the weighing compactor: more machine sales',
        ]} />
      </div>
      <p className="text-xs text-slate-500">
        Synthetic data, fictional operators, hypothetical prices. Every assumption and slider: <a className="underline" href="#/market">market</a> and{' '}
        <a className="underline" href="#/business">business</a> details.
      </p>
    </section>
  )
}

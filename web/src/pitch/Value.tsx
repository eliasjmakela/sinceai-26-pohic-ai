import { useEffect, useMemo, useState } from 'react'
import { bundle } from '../bundle'
import { Ecosystem } from '../components/Ecosystem'
import { Card, Kpi, TagBadge } from '../components/ui'
import { simulate } from '../market/model'
import { ECO_CAPTIONS, ECO_STEPS } from './steps'

/**
 * Pitch screen 3 — the value. The diagram from screen 1 is revealed one arrow at a time (→ / Next); after the last step
 * the market result and what each party gets appear.
 */
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
  const [step, setStep] = useState(0)
  const after = step >= ECO_STEPS
  // → advances the reveal first; only on the last step does it fall through to App's screen navigation.
  // Child effects run before the parent's, so this listener sees the key first.
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'ArrowRight' && step < ECO_STEPS) { setStep(step + 1); e.stopImmediatePropagation() }
      if (e.key === 'ArrowLeft' && step > 0) { setStep(step - 1); e.stopImmediatePropagation() }
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [step])
  const s = useMemo(() => simulate(m.inputs, m.operators, m.sigma_inc, m.sigma_ent, m.params).summary, [m])
  const t = bundle.validation.trips_check
  const svc = bundle.hero.service_check
  const pr = bundle.pricing
  const fee = pr.recommended_fee_eur_per_month
  const h = pr.headline
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
      </header>

      <Card>
        <Ecosystem step={step} />
        <div className="mt-3 flex flex-wrap items-center justify-between gap-3">
          <p className="text-xl font-semibold text-slate-900">{ECO_CAPTIONS[step]}</p>
          <div className="flex items-center gap-3">
            <div className="flex gap-1.5" aria-hidden>
              {ECO_CAPTIONS.map((c, i) => <span key={c} className={`h-2 w-2 rounded-full ${i <= step ? 'bg-teal-700' : 'bg-slate-300'}`} />)}
            </div>
            {step < ECO_STEPS
              ? <button type="button" onClick={() => setStep(step + 1)} className="rounded-lg bg-teal-700 px-4 py-2 text-sm font-medium text-white hover:bg-teal-800">Next ›</button>
              : <button type="button" onClick={() => setStep(0)} className="rounded-lg border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700">Back to today</button>}
          </div>
        </div>
        <p className="mt-2 text-xs text-slate-500">Billing stays on the operator's certified weighbridge, as today; shared tickets calibrate and cross-check the device weights.</p>
      </Card>

      <div className={`space-y-4 transition-opacity duration-500 ${after ? 'opacity-100' : 'pointer-events-none opacity-0'}`}>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Kpi label={`Customer cost per tonne, region ${m.region}`} before={s.cost_per_t_before} after={s.cost_per_t_after} fmt={perT} showAfter={after} />
        <Kpi label={`Truck visits per year, region ${m.region}`} before={s.lifts_before} after={s.lifts_after} fmt={(v) => v.toLocaleString('en')} showAfter={after} />
        <Kpi label="Tonnes per visit" before={s.t_per_lift_before} after={s.t_per_lift_after} fmt={(v) => v.toFixed(2)} showAfter={after} />
        <Kpi label="Customers a challenger can win" before={s.accounts_contestable_today} after={s.accounts_contestable_after} fmt={(v) => `${v} / ${s.accounts}`} showAfter={after} />
      </div>

      <div className="grid gap-4 lg:grid-cols-3">
        <Party who="Customer" pays="pays nothing for OpenWeight" tag="simulated" lines={[
          `about ${saving} % less per tonne after a per-kg tender (region ${m.region})`,
          ...(t ? [`${t.labelled_premature_pct}–${t.model_removed_pct} % fewer truck visits`] : []),
          ...(svc ? [`sees whether the contract is kept: ${svc.on_time_share_pct} % of visits on time, ${eur(svc.invoice_above_contract_eur)} invoiced above contract`] : []),
        ]} />
        <Party who="Operators" pays={`pay €${fee} per weighed device per month`} tag="simulated" lines={[
          `forecast any site at ±${Math.round(100 * m.sigma_inc)} %, not ±${Math.round(100 * m.sigma_ent)} %`,
          'bid per kilo without a risk premium',
          'win customers on efficiency, run fuller trucks',
        ]} />
        <Party who="Europress" pays="becomes a service company" tag="hypothetical" lines={[
          `every new compactor weighs itself (${pr.params.new_units_per_year.toLocaleString('en')} a year)`,
          `NPV ${eur(h.npv_30_eur.value ?? 0)} over 10 years, pays back in year ${h.payback_30_year.value} (self-lift at €${pr.params.h7_capex_eur.toLocaleString('en')})`,
          `€${fee} is the break-even fee: below it the plan does not pay back`,
          'operators recommend the weighing compactor: more machine sales',
        ]} />
      </div>
      </div>
      <p className="text-xs text-slate-500">
        Synthetic data, fictional operators, hypothetical prices. Every assumption and slider: <a className="underline" href="#/market">market</a> and{' '}
        <a className="underline" href="#/business">business</a> details.
      </p>
    </section>
  )
}

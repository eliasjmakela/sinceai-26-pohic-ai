import { bundle } from '../bundle'
import { Ecosystem } from '../components/Ecosystem'
import { FigureValue } from '../components/FigureValue'
import { Card } from '../components/ui'

/** Pitch screen 1 — the market today: paid per trip, and only the incumbent knows the tonnes. */
export function Today() {
  const f = bundle.fleet
  const m = bundle.market
  return (
    <section className="space-y-6">
      <header>
        <div className="text-sm font-medium uppercase tracking-wide text-slate-500">1 · The market today</div>
        <h1 className="mt-1 text-4xl font-bold text-slate-900">Customers pay for trips. Only the incumbent knows the tonnes.</h1>
      </header>
      <div className="grid gap-4 sm:grid-cols-3">
        <FigureValue figure={f.trip_share_pct} label="of all charges are paid per truck visit, not per tonne" />
        <FigureValue figure={f.low_fill_lift_share_pct} label="of visits empty a compactor less than 60 % full" />
        <FigureValue figure={m.headline.contestable_before} label={`of ${m.inputs.length} customers in region ${m.region} a challenger can safely win today`} />
      </div>
      <Card>
        <Ecosystem step={0} />
        <p className="mt-2 text-sm text-slate-600">
          Forecasting a site's tonnes: the incumbent, from its own history, ±{Math.round(100 * m.sigma_inc)} %; a challenger, guessing from similar
          sites, ±{Math.round(100 * m.sigma_ent)} % (backtest on the synthetic dataset). A challenger who bids per kilo on a guess must add a risk
          premium, so the customer never gets a better offer.
        </p>
      </Card>
    </section>
  )
}

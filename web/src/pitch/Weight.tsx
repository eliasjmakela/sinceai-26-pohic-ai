import { bundle } from '../bundle'
import { CostStrip } from '../components/CostStrip'
import { H7Diagram } from '../components/H7Diagram'
import { Card, TagBadge } from '../components/ui'

/** Pitch screen 2 — how we get the weight: H7 hydraulic self-lift on every new COMBI, calibrated by shared weighbridge tickets. */
export function Weight() {
  const h7 = bundle.weighing.h7
  const retro = bundle.weighing.installed_cost.strip.find((k) => k.id === 'H7')?.retrofit_eur
  const [lo1, mid1, hi1] = h7.sigma_one_point_pct
  const mid2 = h7.sigma_two_end_pct[1]
  return (
    <section className="space-y-6">
      <header>
        <div className="text-sm font-medium uppercase tracking-wide text-teal-700">2 · How we get the weight</div>
        <h1 className="mt-1 text-4xl font-bold text-slate-900">The compactor weighs itself.</h1>
        <p className="mt-2 max-w-3xl text-lg text-slate-600">
          A COMBI already has hydraulics. One extra cylinder lifts the door end {h7.stroke_margin_mm} mm; its pressure is the weight.
          No load cell carries the load, except for the 30 seconds of a reading.
        </p>
      </header>

      <Card>
        <div className="mb-2 flex items-center justify-between">
          <div className="text-sm font-medium text-slate-900">Hydraulic self-lift (H7), worked example: {h7.example.machine_t} t machine, {h7.example.waste_t} t of waste</div>
          <TagBadge tag="estimated" />
        </div>
        <H7Diagram />
      </Card>

      <div className="grid gap-4 lg:grid-cols-3">
        <Card>
          <div className="flex items-center justify-between"><div className="text-sm text-slate-500">Accuracy per pick-up (1σ, 2.5 t, after 10 shared tickets)</div><TagBadge tag="estimated" /></div>
          <div className="mt-1 text-4xl font-semibold tabular-nums text-slate-900">±{mid1} %</div>
          <p className="mt-1 text-sm text-slate-600">Error budget range {lo1}–{hi1} %; ±{mid2} % if both ends lift. Target ≤ 5 %. Untested.</p>
        </Card>
        <Card>
          <div className="mb-3 flex items-center justify-between"><div className="text-sm text-slate-500">Installed cost per device, new units</div><TagBadge tag="estimated" /></div>
          <CostStrip />
        </Card>
        <Card>
          <div className="text-sm text-slate-500">Limits we know</div>
          <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-slate-700">
            <li>New COMBI units only; retrofit costs €{retro?.[0].toLocaleString('en')}–{retro?.[1].toLocaleString('en')}</li>
            <li>At most {h7.pressure_bar[1]} bar of the ~{h7.system_pressure_bar} bar system pressure ({h7.design_bore_mm} mm bore)</li>
            <li>{h7.stroke_margin_mm} mm stroke margin: rails and soft ground need a pad</li>
            <li>Narrow support while lifted: an off-centre load can tip it sideways (tilt sensors reject the reading)</li>
            <li>Ice or debris under the runner fronts can carry load (lift-curve check)</li>
            <li>A new machine function: CE risk assessment needed</li>
          </ul>
        </Card>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <div className="text-xs font-semibold uppercase tracking-wide text-teal-700">a · Every new compactor weighs</div>
          <p className="mt-2 text-sm text-slate-700">The self-lift is built into every new COMBI at the factory, {bundle.pricing.params.new_units_per_year.toLocaleString('en')} units a year. Each reading goes to SMART with its uncertainty.</p>
        </Card>
        <Card>
          <div className="text-xs font-semibold uppercase tracking-wide text-teal-700">b · Tickets calibrate it</div>
          <p className="mt-2 text-sm text-slate-700">
            Each weighbridge ticket the operator shares gives the true weight of one load. Ten tickets fit the unit's own geometry and
            bring the error from about ±{h7.sigma_one_point_no_tickets_pct} % to ±{mid1} %.
          </p>
        </Card>
        <Card>
          <div className="text-xs font-semibold uppercase tracking-wide text-teal-700">c · The bill stays certified</div>
          <p className="mt-2 text-sm text-slate-700">
            We bill by the real scale: the operator's certified weighbridge, as today. The self-lift gives the estimates for planning,
            and every shared ticket checks it, so a drifting sensor is caught and recalibrated.
          </p>
        </Card>
      </div>
    </section>
  )
}

// TypeScript mirror of pipeline/fullload/pricing.py `cash_flows` and `summarise` (the Python file documents the
// model). Checked by `npm run parity` against the cases in bundle.pricing.parity.
export interface PricingParams {
  years: number
  discount_rate: number
  ramp_years: number
  new_units_per_year: number
  adoption: number
  h7_capex_eur: number
  platform_eur_per_unit_year: number
  h7_upkeep_eur_per_unit_year: number
  fixed_cost_eur_per_year: number
  package_eur: number
  bidders: number
  tender_share: number
  tender_interval_years: number
  sales_growth: number
  device_price_eur: number
  device_margin: number
}

export interface PricingSummary { npv_eur: number; payback_year: number | null; deepest_eur: number; cumulative_eur: number }

export function cashFlows(p: PricingParams, fee: number): number[] {
  const out: number[] = []
  for (let y = 1; y <= p.years; y++) {
    const weighed = p.new_units_per_year * y
    const ramp = Math.min(y / p.ramp_years, 1)
    const fees = weighed * p.adoption * ramp * fee * 12
    const packages = (weighed / p.tender_interval_years) * p.tender_share * p.bidders * p.package_eur * ramp
    const sales = p.new_units_per_year * p.sales_growth * Math.min((y - 1) / p.ramp_years, 1) * p.device_price_eur * p.device_margin
    const costs = p.fixed_cost_eur_per_year + weighed * (p.platform_eur_per_unit_year + p.h7_upkeep_eur_per_unit_year)
    out.push(fees + packages + sales - costs - p.new_units_per_year * p.h7_capex_eur)
  }
  return out
}

// Python's round() is round-half-even; the parity check compares with a 1-euro tolerance.
export function summarise(cfs: number[], rate: number): PricingSummary {
  let cum = 0
  let deepest = 0
  let payback: number | null = null
  cfs.forEach((c, i) => {
    cum += c
    deepest = Math.min(deepest, cum)
    if (payback === null && cum >= 0) payback = i + 1
  })
  const npv = cfs.reduce((a, c, i) => a + c / (1 + rate) ** (i + 1), 0)
  return { npv_eur: Math.round(npv), payback_year: payback, deepest_eur: Math.round(deepest), cumulative_eur: Math.round(cum) }
}

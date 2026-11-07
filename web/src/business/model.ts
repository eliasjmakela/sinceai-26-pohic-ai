// TypeScript mirror of pipeline/fullload/business.py `simulate` (the Python file documents the model).
// `npm run parity` checks it against the cases the pipeline writes into the bundle.

export interface BizParams {
  devices_total: number
  paying_coverage: number
  fee_mode: 'per_device_month' | 'per_tonne'
  fee_eur_per_device_month: number
  fee_eur_per_t: number
  t0_share: number
  t0_cost_eur: number
  h1_share: number
  h1_cost_eur: number
  opex_eur_per_device_year: number
  sales_growth: number
  device_price_eur: number
  device_margin: number
  renewal_years: number
  horizon_years: number
  tonnes_per_device_year: number
}

export interface BizResult {
  fee_per_device_year: number
  investment: number
  service_revenue: number
  extra_sales_margin: number
  opex: number
  net_per_year: number
  payback_years: number | null
  cumulative_net_horizon: number
  customer_pays: number
}

export function simulateBusiness(p: BizParams): BizResult {
  const feeYear = p.fee_mode === 'per_device_month' ? p.fee_eur_per_device_month * 12 : p.fee_eur_per_t * p.tonnes_per_device_year
  const investment = p.devices_total * (p.t0_share * p.t0_cost_eur + p.h1_share * p.h1_cost_eur)
  const revenue = p.devices_total * p.paying_coverage * feeYear
  const extraSales = (p.devices_total / p.renewal_years) * p.sales_growth * p.device_price_eur * p.device_margin
  const opex = p.devices_total * p.opex_eur_per_device_year
  const net = revenue + extraSales - opex
  return {
    fee_per_device_year: feeYear,
    investment,
    service_revenue: revenue,
    extra_sales_margin: extraSales,
    opex,
    net_per_year: net,
    payback_years: net > 0 ? investment / net : null,
    cumulative_net_horizon: net * p.horizon_years - investment,
    customer_pays: 0,
  }
}

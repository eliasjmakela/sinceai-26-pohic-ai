// Types for web/public/data/bundle.json, written by `fullload build` (pipeline/fullload/export.py).
// Keep in sync with the pipeline: change schema_version on both sides together.
import raw from '../public/data/bundle.json'

export type Tag = 'observed' | 'estimated' | 'simulated' | 'hypothetical'

export interface Figure {
  value: number | null
  unit: string
  tag: Tag
  formula: string
  sources: string[]
  sigma: number | null
  row_ids: string[]
  assumptions: string[]
}

export interface Fleet {
  devices: Figure
  devices_with_weighing: Figure
  gross_charges_eur: Figure
  trip_charges_eur: Figure
  trip_share_pct: Figure
  tonne_charges_eur: Figure
  tonnes_per_year: Figure
  low_fill_lift_share_pct: Figure
  fill_at_lift_histogram: { bin_pct: number; lifts: number }[]
  fill_by_trigger: { trigger_type: string; lifts: number; median_fill_pct: number }[]
  visit_cost_by_fill: { band: string; lifts: number; share_pct: number; visit_eur: Figure; kg: Figure; eur_per_t: Figure }[]
}

export interface Market {
  region: string
  operators: string[]
  sigma_inc: number
  sigma_ent: number
  params: import('./market/model').Params
  inputs: import('./market/model').Account[]
  headline: Record<string, Figure>
}

export interface HeroLift { date: string; device_id: string; fill_pct: number | null; kg: number | null; trigger: string; flagged: boolean }
export interface HeroDevice { device_id: string; site: string; material: string; policy: string; schedule_per_week: number | null;
  container_m3: number; equipment: string; lifts: number; weight_triggered_lifts: number; tonnes: number; median_fill_at_lift_pct: number | null }
export interface Hero {
  customer_id: string
  customer_name: string
  sector: string
  region: string
  devices: HeroDevice[]
  lifts: HeroLift[]
  figures: Record<string, Figure>
  facts: Record<string, number | string>
  report: { status: string; text: string | null; label?: string; unmatched_numbers?: string[] }
  service_check: { jobs: number; lifts: number; on_time_share_pct: number; missed_visits: number; tickets_shared_share_pct: number;
    invoice_lines: number; invoice_lines_differing: number; invoice_above_contract_eur: number; invoice_below_contract_eur: number;
    definitions: Record<string, string>; note: string } | null
  proposal: Record<string, unknown>
  operator_view: {
    devices: { device_id: string; actual_t_per_month: number; own_forecast_t_per_month: number; peer_forecast_t_per_month: number; own_error_pct: number; peer_error_pct: number }[]
    own_error_median_pct: number
    peer_error_median_pct: number
    sigma_inc: number
    sigma_ent: number
    price_today_eur: number
    bids_before_eur: Record<string, number>
    bids_after_eur: Record<string, number>
    incumbent: string
    winner_after: string
    price_after_eur: number
  }
}

export interface ValueRow { lever: string; who: string; needs_weight: string; ours: Figure | null; ours_range: [number, number] | null; team: number | null; note?: string }
export interface TripsCheck { lifts: number; model_removed_pct: number; labelled_premature_pct: number; per_device_pearson: number }

export interface CostConcept { id: string; name: string; factory_fit_eur: [number, number]; retrofit_eur: [number, number] }
export interface Weighing {
  h7: {
    design_bore_mm: number
    pressure_bar: [number, number]
    system_pressure_bar: number
    stroke_margin_mm: number
    example: { machine_t: number; door_end_share: number; waste_t: number; x_w_over_l: number; bore_mm: number;
      tare_bar: number; loaded_bar: number; waste_from_reading_t: number; kg_waste_per_bar: number }
    sigma_one_point_pct: [number, number, number]
    sigma_one_point_no_tickets_pct: number
    sigma_two_end_pct: [number, number, number]
    figures: Record<'sigma_one_point_pct' | 'installed_eur_low' | 'installed_eur_high', Figure>
  }
  installed_cost: { reference_eur: number; strip: CostConcept[] }
}
export interface VirtualScale { devices: number; lifts: number; reference_share: number; reading: string; headline: Record<string, Figure> }

export interface PricingScenario { break_even_fee: number | null; break_even_adoption_at_20: number | null; break_even_adoption_at_30: number | null;
  by_fee: Record<string, import('./pricing/model').PricingSummary> }
export interface Pricing {
  recommended_fee_eur_per_month: number
  max_h7_capex_eur: Record<string, number | null>
  params: import('./pricing/model').PricingParams & { fees_eur_per_month: number[] }
  h7_cost: { capex_eur: [number, number]; capex_mid_eur: number; upkeep_eur_per_year: [number, number]; upkeep_mid_eur_per_year: number }
  scenarios: Record<string, PricingScenario>
  operator: { visits_per_device: number; fewer_visits_pct: [number, number]; hard_gain_eur: [number, number, number]; spend_median_eur: number;
    profit_per_device_today_eur: [number, number]; team_value_eur: number;
    by_fee: { fee_eur_per_month: number; fee_eur_per_year: number; share_of_hard_gain_mid_pct: number; share_of_team_value_pct: number;
      share_of_profit_today_pct: [number, number]; net_hard_gain_eur: [number, number, number] }[] }
  headline: Record<string, Figure>
}

export interface Bundle {
  schema_version: 1
  provenance: { kit_version: string; data: string; synthetic: boolean }
  fleet: Fleet
  forecast: Record<string, unknown>
  trips: Record<string, unknown>
  market: Market
  hero: Hero
  value_per_device: { devices: number; rows: ValueRow[]; note: string }
  pricing: Pricing
  validation: { trips_check?: TripsCheck } & Record<string, unknown>
  virtual_scale: VirtualScale
  weighing: Weighing
}

// Statically imported so the demo has no runtime fetch. The pipeline test checks tags and sources.
export const bundle = raw as unknown as Bundle

# How OpenWeight plugs into SMART

Deliverable (2): "proposed SMART integration". OpenWeight is a layer on Europress SMART, not a separate system. The
compactor already sends fill level, ram pressure and compaction cycles to SMART. OpenWeight adds one new signal
(the weight from the hydraulic self-lift) and three outputs (forecasts, lift orders and customer reports). All
payloads below are illustrative and extend the starter kit's `smve.recommendation.v0` mock
(`examples/recommendation_api_mock.py`). The data is synthetic.

## Data flow

```
 Compactor (every new COMBI)                SMART cloud + OpenWeight engine                Out
 ─────────────────────────                  ───────────────────────────────                ───
 fill %, ram pressure, cycles   ──────────▶  per-device weight history (± σ)      ──────▶  Operators (pay €30 / device / month)
 H7 reading: kg ± σ, tare,                   calibration from shared tickets                 · site tonnage forecast ± σ
   friction, "no reading" flags              12-month tonnage forecast per site              · lift order when the weight says so
                                             weight-triggered lift orders                    · per-kg tender package (with consent)
 Operator's certified weighbridge ────────▶  cross-check: device vs ticket        ──────▶  Customers (free)
   (shared tickets)                          contract and invoice check                      · report: what happened, what to decide
                                             AI-written report, numbers checked              · is the contract kept?
                                                                                             · tender proposal; a human approves
```

**Rule:** we bill by the real scales. The bill is always the operator's certified weighbridge ticket (EU Directive
2014/31/EU). The device weight is for planning, forecasting and cross-checking, never for billing.

## What SMART gets from the compactor

| Signal | Source | Exists today? | Used for |
|---|---|---|---|
| Fill level, compaction cycles, ram pressure, days since last lift | SMART modem | yes | fill model, centre of mass of the waste (§19.5) |
| H7 reading: door-end pressure up/down plateaus, tare, oil temperature, tilt, stroke | H7 pressure sensor and position switch on the SMART modem | **new** | weight W = (R − R₀)·L / x_w, friction (seal health), "no reading" flags |
| Interlocks: hook attached, door open, ram moving, motion | existing switches + new motion sensor | partly | a reading starts only when all are clear (§19.4) |

SMART schedules the readings: a tare when the empty unit returns, a pick-up weight at the fill alarm and one
reading per night for the trend. The firmware returns "no reading" rather than a wrong number (stroke ran out,
plateau not flat, tilt fired, relief valve opened).

## What SMART sends out

1. **Forecast API (operators, paid).** Per device: monthly tonnes for the next 12 months with ±σ, plus the weight
   history. With the site's own history the error is ±10 %; guessing from similar sites gives ±37 % (backtest,
   synthetic data). This is what lets a challenger bid per kilo without a risk premium.
2. **Lift order (operators).** Sent when the weight, not the calendar, says the unit is full enough:

   ```json
   {
     "schema": "openweight.lift_order.v1 (illustrative)", "synthetic": true,
     "device_id": "CMP-00280", "operator_id": "OP-E", "trigger": "WEIGHT",
     "estimated_net_kg": 1850, "sigma_kg": 81, "fill_pct": 86,
     "window": {"earliest": "2026-11-10T06:00", "latest": "2026-11-11T18:00"},
     "billing_basis": "operator's certified weighbridge"
   }
   ```
3. **Customer proposal (customers, free).** Built from the customer's own data. It never acts by itself:

   ```json
   {
     "schema": "openweight.proposal.v1 (extends smve.recommendation.v0, illustrative)", "synthetic": true,
     "customer_id": "ORG-0036",
     "rationale": "81 of 163 lifts emptied a container under 60 % full.",
     "proposal": {"action": "TENDER_PER_KG", "requires_human_approval": true, "auto_execute": false,
                  "terms": "per-kg price, weight-triggered lifts, billing on the operator's certified weighbridge"},
     "reversal": "No commitment: the customer can keep today's contract; a tender only invites bids.",
     "not_proven": ["Savings are simulated on synthetic data, not demonstrated"]
   }
   ```
   The full payload, with its observed and simulated evidence, is in the bundle (`hero.proposal`) and on the
   Customer detail screen.

## Consent and control

- **The customer owns the data.** An operator sees a site's weight profile only for a tender the customer has
  approved, or for sites it already serves.
- **A human approves every action.** Proposals carry `requires_human_approval: true` and `auto_execute: false`.
  Nothing is sent to an operator until the customer presses Approve.
- **Numbers come from the calculation, not from the language model.** The AI writes the customer report from a
  template, and every number in it is checked against the computed facts before it is shown
  (`pipeline/fullload/customer.py`).

## What Europress builds, and what it does not

| Builds | Does not build |
|---|---|
| H7 hardware in new COMBIs; the reading routine in the SMART firmware | Transport, routing, truck scheduling |
| The OpenWeight engine on SMART cloud: calibration, forecasts, lift orders, reports | Billing (stays with the operator's weighbridge) |
| Operator API and portal (bid pack, offer planning, weight check) and the customer portal | A marketplace that sets prices, or a channel for offers: offers go from operator to customer the usual way, and the customer uploads them to compare |

## In this repo

| Part | Where |
|---|---|
| Forecasts and backtest | `pipeline/fullload/forecast.py` |
| Weight-triggered lifts | `pipeline/fullload/trips.py` |
| Contract and invoice check | `pipeline/fullload/scorecard.py`, `customer.py` |
| Proposal payload and AI report | `pipeline/fullload/customer.py`, `pipeline/fullload/reports/` |
| The service itself, the demo (portals over an API) | `app/backend/server.py` (FastAPI; the waste company endpoints never return the customer's prices, invoices or choice), `app/frontend/` |

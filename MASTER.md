# MASTER.md: OpenWeight, the team's single understanding

Internal reference for the final submission TO-DO and the teammate briefing. Written 7 Nov 2026 (evening) from
`OpenWeight.pdf`, `LIITE_perustelut.md`, this repo and the brief. **Where this file and an older source disagree,
this file wins** (overrides 1–5 of 7 Nov). The working tree was being edited while this was written, so web/pipeline
line numbers in §G are a snapshot: check them before editing.

---

## A. The story in 10 sentences

1. **Problem:** customers pay for truck visits, not tonnes. 56.5 % of all charges are per visit, and a visit costs about
   the same (€143–160) whether the compactor is under 60 % or over 90 % full.
2. Visits made under 60 % full therefore cost the customer €167/t, against €49/t when over 90 % full (3.4×).
3. **Insight:** only the incumbent operator knows each site's weight. It forecasts a site's tonnage to ±10 %, while a
   challenger working from peer sites is ±37 % off. So no challenger can safely bid per kg (0 of 19 customers
   contestable in our simulated region), and the incumbent has no reason to drive less.
4. **Product:** OpenWeight puts the weight in the compactor. Europress gives every operator the same site forecasts and
   weight data, with the customer's consent.
5. **Who pays:** customers use it free. Operators pay Europress a service fee per weighed device per month
   (€30, decided 7 Nov evening), and Europress funds the hardware.
6. **Weighing:** every new compactor gets the H7 hydraulic self-lift. One cylinder on the unit's own power pack lifts the
   door end 10 mm, and the pressure gives the waste weight. Accuracy is ±4.4 % (1σ, estimate, after 10 shared
   weighbridge tickets). Untested; COMBI only.
7. **Billing rule:** we bill by the real scales and the hydraulic scale gives the estimates. The bill stays on the
   operator's certified weighbridge (Directive 2014/31/EU). Device weight is used for planning, forecasts and
   cross-checks, and is calibrated by the weighbridge tickets.
8. **Value (simulated):** in one region, customer €/t falls about 12 % (with the €30 fee), visits fall 19 % and all 19 customers become
   contestable. Per fleet device, avoidable visits fall 6–18 %.
9. **Business:** the team plans with H7 at €1,000 capex per new unit (upkeep €73/yr). On that base €30 is the
   break-even fee: NPV +€0.18 M over 10 years at 8 %, payback year 9, deepest cash −€3.83 M, needing ≥ 59 % paying
   adoption; €20 gives −€2.46 M. The margin is thin (above ~€1,020 capex €30 loses money; Part 1's mid €1,585 gives
   −€4.53 M), so a supplier quote for the self-lift comes first, then a pilot.
10. **Risks:** the H7 cost (the biggest: a thin margin above the €1,000 base), whether operators will pay and adopt (untested guesses), H7 physics in the
    field (centre of mass, sideways tipping, runner contact, CE), and the fact that all market numbers come from
    synthetic data.

---

## B. Decisions (current)

| # | Decision | Value | Source | Date |
|---|---|---|---|---|
| 1 | Product name | OpenWeight (package stays `fullload`) | PRODUCT.md §1 | 7 Nov |
| 2 | Thesis | Pay for tonnes, not trips; break the incumbent's information monopoly | PRODUCT.md §1 | 7 Nov |
| 3 | Weighing hardware | **H7 hydraulic self-lift on every new compactor**, factory-fit; customer cannot opt out | Lead override 1; PDF p3, p5 | 7 Nov |
| 4 | Virtual scale | **Not in the main story**; at most a roadmap item for the existing fleet | Lead override 1; PDF p7 | 7 Nov |
| 5 | Existing fleet / retrofit | No H7 retrofit (€1,994–6,168); roadmap only | WEIGHING_CONCEPT §19.3 | 7 Nov |
| 6 | DUO | **Open**: separate DUO mechanism review pending (§H). COMBI/DUO split of new units unknown (no data); the model assumes all ~1,200 new units are weighed | Lead override 5 | 7 Nov |
| 7 | Billing | Operator's certified weighbridge (2014/31/EU); device weight = estimates, cross-check | Override 2; PRODUCT.md §1 | 7 Nov |
| 8 | Who pays | Operators: fee per weighed device per month; customer €0; Europress funds H7 | PDF p3; PRODUCT.md §1 | 7 Nov |
| 9 | Fee level | **€30 / device / month** (decided 7 Nov evening; the break-even fee at the base), plus €500 tender packages (team model) | Override 4; pricing.py `RECOMMENDED_FEE` | 7 Nov |
| 10 | H7 planning cost | **€1,000 capex per new unit** (team decision; upkeep €73/yr, Part 1 midpoint); break-even capex €1,020 at €30; supplier quote to confirm | `params.yaml: pricing.h7_capex_eur`; `pricing.max_h7_capex` | 7 Nov evening |
| 11 | Business model of record | Team cash-flow model (LIITE §6.3) reproduced in `pipeline/fullload/pricing.py`; old `business.py` (€20, 1.6 y) deleted | Override 4; git status | 7 Nov |
| 12 | Demo | 3 pitch screens: Today / How we get the weight / The value; detail screens Fleet, Customer, Operator, Market, Business | Override 3; PRODUCT.md §4 | 7 Nov 15:30 |
| 13 | Data ownership | Customer owns the data; sharing with bidders is consent per tender | PRODUCT.md §1; PDF p4 | 7 Nov |
| 14 | Out of scope | Route optimisation, municipal waste, device-weight billing, live LLM chat, biowaste in business claims | PRODUCT.md §1, §6; PDF p7 | 7 Nov |
| 15 | Rules over ML | Explainable premature-lift rule over kit ML; ML shown only as the brief's comparison | PRODUCT.md §8 | 7 Nov |
| 16 | Source of truth for numbers | Repo pipeline (`bundle.json`) + pricing.py; PDF numbers only where §C says agreed | PRODUCT.md §1 | 7 Nov |

---

## C. Numbers ledger

Tags: obs = observed (synthetic data, public source or Tommi), est = estimated (team calc), sim = simulated,
hyp = hypothetical (assumption). "Synthetic" applies to every data figure.

### C1. Market today (screen 1, Fleet)

| Number | Value | Tag | Source | Status |
|---|---|---|---|---|
| Devices / with device weight | 447 / 404 | obs | `fleet.devices`, `devices_with_weighing` | agreed |
| Gross charges; per-visit charges | €6.33 M; €3.58 M = **56.5 %** | obs | `fleet.trip_share_pct` | agreed |
| Lifts under 60 % full | **33.4 %** ("1 in 3"; PDF 33 %) | obs | `fleet.low_fill_lift_share_pct` | agreed |
| Visit cost by fill band | **€143 / €150 / €160** (<60 %, 60–90 %, ≥90 %) | obs | `fleet.visit_cost_by_fill` | agreed |
| €/t by fill band | **€167 / €70 / €49**, 3.4× | obs (kg are device estimates) | same | agreed; tag caveat (F7) |
| Median fill at lift by trigger | on-call 82 %, scheduled 52 %, max-interval 44 %, customer request 39 % | obs | `fleet.fill_by_trigger` | agreed |
| Contestable customers today | **0 of 19** | **sim** | `market.headline.contestable_before` | agreed; it is simulated, not observed |
| Forecast error own history vs peers | **±10 % vs ±37 %** (median; p80 23.5 vs 95 %) | est | `forecast.*_error_median_pct` | agreed |
| PDF: 21 % vs 9 % (kg per visit) | 20.6 / 9.1 % | sim | LIITE §2.3 | **superseded** by ±37/±10; do not show both |
| Today's price check | 97.6 % of 1,586 collections exact to the cent | obs | `validation.economics_check` | agreed |
| Tommi / public facts | SMART −37 % lifts (epsmart.fi); Insights ~15 %; ~3 % of a manager's time; HSY quote; contracts ~3 y | obs | PRODUCT.md §2; LIITE §2 | agreed; keep SMART's 37 % away from ±37 % |
| PDF: "incumbent wins every third year" | none | – | LIITE §2.4 | **do-not-cite** → "retendered ~every 3 y, mostly on price" |

### C2. Weighing (screen 2)

| Number | Value | Tag | Source | Status |
|---|---|---|---|---|
| H7 worked example | tare 27 bar → 57 bar → 2.5 t; 85 kg waste per bar | est | `weighing.h7.example`; §19.2 | agreed |
| Pressure | ≤113 bar of ~200 bar system, 80 mm bore | est / obs (200) | §19.2 | agreed (PDF 4–6 t, ~120 bar: conservative, OK) |
| Accuracy, one-point + 10 tickets | **±4.4 % 1σ** (range 2.6–9.7), target ≤5 % | est | `weighing.h7.sigma_one_point_pct` | agreed |
| Two-end lift | 3.2 % (1.7–8.4); front cylinder €510–1,150 not costed in | est | §19.5 | agreed (as option) |
| No tickets | ~10.7 % | est | §19.5 case A | agreed |
| PDF: ±3 % full, ±8–10 % half, "3.1 t ± 0.1 t" | – | est | PDF p5 | **superseded** by ±4.4 % / ±0.15 t |
| PDF: sensor ±30 kg | is force; ≈ ±50–75 kg of waste | est | LIITE §9 | **superseded** |
| Installed cost factory-fit (incl. 6-y upkeep) | **€1,034–3,008** | est | `installed_cost.json`, §19.7 | agreed |
| H7 capex / upkeep split | **€800–2,370, mid €1,585; €39–106/yr (mid €73)** | est | `pricing.h7_cost_split()` | agreed |
| PDF: €550–1,100 parts; €825 per unit; ~€190/yr | – | est | PDF p5–6 | **superseded** (parts only); €825 kept only as "team-document case" |
| Retrofit | €1,994–6,168 | est | §19.3 | agreed (not recommended) |
| Reference points | ~€2,000 option on a €20–25k COMBI; platform scale €7,860–22,160; H1 €548–2,363 | obs / est | §0, §7 | agreed |
| Stroke margin; foot pressure | 10 mm; 0.63 MPa (pad on hot asphalt/gravel) | est | §19.6 | agreed (PDF 400 mm ≈ 0.4 MPa OK) |
| Sideways tipping; runner contact | support ±0.21 m; ~1.8 mm lift at 1 m from pivot | est | §19.6, RED_TEAM R29–R30 | agreed (limits) |
| Lifts per year | ≈445 (PDF ~1,000) | est | §19.6 | PDF superseded (harmless) |
| Kit tolerance | ±3.3 % device vs weighbridge ("e.g.") | obs (kit) | ECONOMIC_MODEL §2b | agreed as "kit's example" |
| Virtual scale | 8.3 % / 7.6 % (5 tickets) / 5.5 % monthly; fill only 16.2 % | sim | `virtual_scale.headline` | **roadmap only**; not in pitch |
| H1 self-calibration | 9.5 → 3.4 % after 10 tickets | est | §4 | not in pitch (H1 not chosen) |

### C3. Value (screen 3, Market, Customer)

| Number | Value | Tag | Source | Status |
|---|---|---|---|---|
| Customer €/t, region FI-01 | **€113.1 → €99.6, −12 %** with the €30 fee (€3.9/t) | obs → sim | `market.headline.cost_per_t_*`; `market.params.europress_fee_cents_per_t` 390 | agreed (F3 resolved: the bundle uses €3.9/t) |
| Visits in region | 3,845 → 3,102, **−19 %** | sim | `market.headline.lifts_*` | conflict with fleet 6–18 % framing (F4) |
| Contestable | **0 → 19 of 19**; customers switching 9 (8–19 by assumption) | sim | `market.headline` | agreed |
| HHI | ~5,350 → ~6,170 (concentration can rise) | sim | LIMITATIONS §4 | agreed (say it if asked) |
| Fewer visits, fleet | **6–18 %** (labels 6.1 %, model 18.1 %, r = 0.85) | sim | `validation.trips_check` | agreed; PDF "18 %" superseded |
| Showcase customer | −30.8 % = best case (€137.6 → €95.2/t) | sim | LIMITATIONS §5 | agreed only with "best case" |
| Value per device: avoidable visits / expensive tonnes | €686–1,469 / €1,278 (team 1,570 / 1,245) | sim / est | `value_per_device` | agreed; do not add up |
| Operator pricing risk | ours €2,712, team €1,930 | hyp | `value_per_device` | **do-not-cite**; say "removes the risk premium" |
| PDF customer gain ~€1,900 | overlapping levers (worst case €1.1–1.3k) | sim + guess | LIITE §1.1 | **do-not-cite** as a single figure |
| PDF operator gain ~€1,400 | 634 + 130 + 643; visit value should be €60–116 | sim + hyp | LIITE §1.2, §9 | **do-not-cite**; pricing.py uses €1,360 internally |
| Operators earn €0–800 per device | €10,220 median spend × 2.7–8.0 % = €276–818 | obs + est | `pricing.operator` | agreed with caveat (spend ≠ operator revenue) |
| Margins L&T 8.0 %, Stena 2.7 %, L&T Q1 −0.8 %, Remeo −3.7 % | – | obs | LIITE §6.2 | agreed (−0.8, not −0.9) |
| Premature-lift rule | F1 0.81, recall 71 %, 0 justified flagged; kit ML F1 0.93 with 13 justified | obs (vs labels) | `validation.premature` | agreed |
| Kit baselines (PDF p8) | A 96 %, B F1 0.73, B2 68/100, C2 regret €240 (dev split) | obs | kit BENCHMARK | agreed; €240 is dev split; 0.59 recall is the kit's |
| PDF demo "save €2,100–3,400/yr" | invented | – | LIITE §7.6 | **do-not-cite** |

### C4. Business (Business screen, pitch party cards)

All hyp; 10 years, 8 %, 1,200 new units a year all weighed, adoption 60 % over 4 years, €500 × 2.5 bidders × 35 %
of tenders every 3 y, +5 % machine sales × €22.5k × 25 %, fixed €400k/yr, platform €26/unit/yr (`params.yaml: pricing`).

| Number | Value | Source | Status |
|---|---|---|---|
| Team model (H7 €825, upkeep €50), €30 | **NPV +€2.49 M**, payback y7, deepest −€2.94 M, cumulative +€6.41 M; +€2.38 M/yr in y10 | pricing.py = LIITE §6.3 (test-pinned) | agreed as the "team-document case" only |
| Team model break-even fee | €21 | same | superseded as headline |
| **Base (H7 capex €1,000, upkeep €73, team decision), €30** | **NPV +€0.18 M, payback y9, deepest −€3.83 M, cumulative +€2.79 M** | `pricing.headline.npv_30_eur`, `payback_30_year`, `deepest_30_eur` | agreed: the base |
| Base, €20 | NPV −€2.46 M, never | `npv_20_eur` | agreed |
| **Break-even fee** at the base | **€30** | `pricing.headline.break_even_fee` | agreed |
| Break-even adoption at €30, base | 59 % | scenarios | agreed |
| Part 1 mid cost (capex €1,585, upkeep €73), €30 / €20 | NPV −€4.53 M / −€7.17 M, never; break-even fee €48 | scenarios `Part 1 mid H7` | agreed: sensitivity |
| **Max H7 capex** at €30 | **€1,020** (upkeep €73); **€1,130** (upkeep €50) | `max_h7_capex_eur` | agreed: thin margin above the €1,000 base |
| Max H7 capex at €15/20/25 | €530 / €690 / €850 | same | agreed |
| Cheap H7 (€800, €39) at €30 | NPV +€3.12 M, payback y7 | scenarios | agreed |
| Dear H7 (€2,370, €106) at €30 | NPV −€12.1 M | scenarios | agreed |
| Break-even adoption at €30, Part 1 mid cost | 95 % | scenarios | agreed (sensitivity) |
| Operator hard gain from fewer visits | €150 / 437 / 862 per device-year | `pricing.operator` | agreed |
| €30 = €360/yr | 82 % of mid hard gain; net −€210 / +€77 / +€502; 26 % of team value; **44–130 % of today's profit per device** | same | agreed; a willingness-to-pay risk |
| Europress PBT 2025 €4.0 M; "deepest = 0.7 × profit"; "+60 % of profit" | from Orbis (academic licence) | LIITE §6.4 | **do-not-cite** until PRH fetched |
| Pilot loss if stopped | ~€1.5 M (PDF "~€1 M"); "€5–11 M" | LIITE §7.3 | PDF **superseded**; "5–11" **do-not-cite** |
| "10–25 % opt-outs kill paid model" | older model | LIITE §3.2 | superseded → "even 10 % opt-outs remove most of the gain" |
| Installed base | ~20,000 (Tommi, group) vs 10,000 (old business.py) | LIITE §8.3 | 20,000 agreed (pricing.py does not need it); 10,000 retired |
| **Old: €20, payback 1.6 y (1.8 y in last bundle), €500 hopper, 5–10 % reference units** | – | old business.py | **superseded** (overrides 1, 4) |

---

## D. Scoring map (brief §06)

| Criterion (weight) | Where we earn it | Gaps |
|---|---|---|
| Weighing concept (25 %): feasibility, accuracy reasoning, cost, retrofit | H7 statics with working (§19.2), error budget (§19.5), installed cost by line (App. A), safety/CE/ground (§19.6), validation plan (§19.11), claims ledger, red team, prior art; PDF p5 | Concept doc still leads with H1 + virtual scale (§G). No H7 figure in `part1/figures/`. **Retrofit story is weak**: existing fleet gets nothing (virtual scale = roadmap). DUO open. Cost gap vs target |
| Customer / business value (25 %) | Screen 1 evidence (3.4×), market sim (−12 %, 19/19), fewer visits 6–18 %, contract visibility (`customer.service_check`), party cards | Customer € per device is a set of non-additive levers. Business NPV only just positive at the €1,000 H7 base (+€0.18 M); negative above ~€1,020 |
| Data-driven value, traceable calcs (20 %) | Every number is a `Figure` with tag + sources; forecast backtest; trips validated vs labels (r 0.85); rules vs ML (F1 0.81 vs 0.93); economics check 97.6 %; pricing.py reproduces LIITE exactly with a test | LIITE's `analysis/` scripts are not in the repo (pricing.py replaces the cash-flow part only; value-pool and opt-out calcs untraceable). Bundle must be rebuilt after each params change |
| Software workflow + SMART pathway (15 %) | Customer proposal → approve (`requires_human_approval`), tender brief, operator forecast table, lift-order payload, "How it plugs into SMART" box (Business screen) | **No recorded walkthrough yet**. H7 trigger/interlock via SMART not shown in the software flow |
| Commercial productisation (10 %) | Operator fee, free customer side, tender packages, adoption ramp, sensitivity sliders, pilot (~1,000 units, one challenger, 2 y), operators as sales channel | Fee untested (no reference point); adoption a guess; extra-sales margin booked one-off though ~70 % are leased |
| Clarity / uncertainty / limits (5 %) | Synthetic banner, evidence tags, LIMITATIONS.md, "not proven" list, H7 limits on screen 2 | LIMITATIONS.md stale (§G); PDF tags exist but some numbers superseded |

---

## E. Required deliverables (brief §07)

| Deliverable | Status | Path / note |
|---|---|---|
| (1) Illustrated weighing concept: principle, placement, BOM + cost, installation, calibration, error sources, validation | **partial** | `part1/WEIGHING_CONCEPT.md` (§19 = H7, but §0/§3/§17 lead with H1 + virtual scale); `part1/figures/*.svg` (H1-era); demo H7 animation (`web/src/pitch/Weight.tsx`); PDF p5 (needs the C2 fixes). Needs a short H7-first concept, ideally in English |
| (2a) Working software demo | **exists** | `web/` (`npm run build && npm run preview`), bundle `web/public/data/bundle.json`. Pitch screens being edited now |
| (2b) Recorded walkthrough | **missing** | none in repo; PRODUCT.md plan: by Sun 00:00 |
| (2c) Code / setup notes | **exists** | `README.md` (stale line on `business.py`) |
| (2d) Traceable economics | **partial** | Figures + `pricing.py` + tests; LIITE `analysis/` scripts absent |
| (2e) Proposed SMART integration | **partial** | Business detail screen "How it plugs into SMART"; proposal payload `openweight.proposal.v1`; no stand-alone diagram/doc |
| (3) Customer value + business case + productisation in SMART | **partial** | `OpenWeight.pdf` (Finnish, outside repo; numbers need §C fixes; business case must use the €1,000 H7 base and show the Part 1 range as sensitivity) |
| Third-party list with licences | **exists** | `THIRD_PARTY.md`, `part1/THIRD_PARTY_part1.md`. PDF p8 lists only pandas, pyarrow, numpy: point to THIRD_PARTY.md |
| Assumptions and what remains untested | **partial** | `LIMITATIONS.md` (stale: §2, §2b, §8); LIITE |
| Demo freeze tag | **missing** | no `demo-frozen` git tag yet |

---

## F. Conflicts needing a human decision

| # | Conflict | Recommended answer |
|---|---|---|
| F1 | **Fee and the H7 cost.** Resolved 7 Nov evening: H7 planned at €1,000 capex (team decision). €30 is then the break-even fee (NPV +€0.18 M, y9); Part 1's mid cost (€1,585) gives −€4.53 M | Keep €30. Headline: "at the €1,000 planning cost €30 just pays back (year 9); the margin is thin and a supplier quote comes first". Show the Part 1 range as sensitivity on the Business screen. Do not put the team-document +€2.5 M on a pitch screen |
| F2 | Operator willingness to pay: €360/yr is 82 % of the mid hard gain and 44–130 % of today's profit per device | Pitch the fee against the risk premium removed and contracts won, not against avoided visits. Name it a pilot hypothesis |
| F3 | **Resolved:** the bundle now uses €3.9/t (€30); market €/t is −12.0 %. (Was −13 % with the €20 fee, €2.6/t) | Set `market.europress_fee_eur_per_t` to 3.9 and say "about −12 %" (range unchanged in spirit). Or keep €2.6 and label it, but a pitch with €30 should not use a €20-based KPI |
| F4 | Screen 3 "visits −19 %" (one region) vs "6–18 % fewer visits" elsewhere | Screen 3: "−19 % in the simulated region"; customer card keeps 6–18 % fleet-wide. Never both without the label |
| F5 | DUO and the 1,200 units/yr. The model assumes every new unit gets H7, but H7 is costed for COMBI only. The PDF puts a DUO cylinder in the rail; Part 1 calls DUO speculative | Wait for the DUO review (§H). Until then: "every new COMBI; DUO variant under review". The COMBI/DUO split is unknown (no data); say the model assumes all new units are weighed |
| F6 | Information-gap figure: ±37/±10 (repo) vs 21/9 (PDF) | Use ±37 vs ±10 everywhere; PDF p2/p4/p7 to change |
| F7 | Screen 1 €/t is tagged observed, but its kg are device estimates | Tag the €/t "estimated (device kg)" or say "per visit observed, tonnes from device weight" |
| F8 | Submission language: the PDF is Finnish; repo and brief are English | Submit English (judges plus Since AI); keep the Finnish PDF as an annex if time allows |
| F9 | Europress profit comparison (Orbis licence) | Drop it unless PRH is fetched before submission |

---

## G. Stale items after overrides 1–4

Priority: P1 = judges or teammates see it, P2 = submitted docs, P3 = internal.

| P | File | Line / section | Stale text | Change to |
|---|---|---|---|---|
| P1 | `web/src/pitch/Value.tsx` | ~95 | Europress card shows team NPV +€2.5 M, payback y7 as fact | Condition it: "if H7 ≤ €1,020: NPV …; at our mid estimate it does not pay back" (F1) |
| P1 | `web/src/pitch/Weight.tsx` | 6 (docstring) | "H7 on reference units, a virtual scale on the rest" | "H7 on every new compactor" (the cards were already being rewritten) |
| P1 | `web/src/details/Business.tsx` | 27, 123 | `fee_basis: 'verified tonnes'`; "fee per verified tonne / device" | "per weighed device per month"; avoid "verified" (sounds legal-for-trade) |
| P1 | `pipeline/fullload/params.yaml` | 39–42 `market.europress_fee_eur_per_t` | 2.6 = €20 | 3.9 (= €360 / 92.6 t), rebuild (F3) |
| P1 | `web/public/data/bundle.json` | `virtual_scale.reference_share` 0.1; `market` fee | built on old params | rebuild after params; drop VS from pitch |
| P1 | `reviews/briefing.html` | "Fee: €20 … decided"; "Lead weighing story: virtual scale + reference subset (hopper)"; payback ~9 y / €1,860 | team briefing page | Regenerate from this file or mark superseded |
| P1 | `reviews/OPENWEIGHT_PDF_FIXES.md` | items 1, 3, 4 (installed-base row) | tells PDF author: use €20/1.6 y; keep virtual scale; use 10,000 | Reverse: €30 pending + cost gap; virtual scale removal is right; 20,000 |
| P1 | `reviews/LIITE_VS_OPENWEIGHT_CHECK.md` | Verdict; rows 7, 8, 9, 20, 21, 32; fixes 1–2 | €20 / 1.6 y / virtual scale as "agreed" | Add a header note: superseded by MASTER.md §B |
| P2 | `PRODUCT.md` | §1 l.37–42 | "~€20 per device per month (decided)"; hardware via `briefs/WEIGHING_V2.md` | €30 pending; H7 on every new unit; design-to-cost |
| P2 | `PRODUCT.md` | §1 l.75–79 | "Weighing architecture: … virtual scale on every device … hopper plate and/or rails … ~5 % reference" | H7 on every new compactor; VS = roadmap for the existing fleet |
| P2 | `PRODUCT.md` | Figure decisions l.93–95 | operator row cites "€1.4k / €1.9k" (attribution); Europress "€20 … payback 1.6 years at €500 … ~€1.9k"; Weighing "virtual scale on every device … only for the ~5 % reference subset" | Operator: "removes the risk premium"; Europress: €30, NPV conditional on H7 ≤ €1,020; Weighing: H7 ±4.4 %, €1,034–3,008 installed, every new COMBI |
| P2 | `PRODUCT.md` | l.101–105 | Part 1 = "hopper-stage weighing and guide rails as co-leads" | H7 lead |
| P2 | `PRODUCT.md` | §4 l.179 | "Fleet layer: ~10 % reference units weigh, the virtual scale estimates the rest" | "every new unit weighs; weighbridge stays the bill and calibrates it" |
| P2 | `PRODUCT.md` | §4 l.180 | "operators €20 / device / month, Europress … payback" | €30 (pending), "pays back if H7 ≤ ~€1,000" |
| P2 | `PRODUCT.md` | §5 l.194; §7.2 l.302; §7.5 l.327–342; §9 l.399, 408 | "Three tiers incl. zero-BOM virtual weight"; `business.py`; "T1 strain gauges — the chosen concept", H1/H5; "T0 as zero-hardware fallback"; fee open question | H7; `pricing.py`; H7 chosen; risk = H7 cost gap; fee €30 pending |
| P2 | `LIMITATIONS.md` | §2 l.21–32 | branch `weighing-v2`, H1 self-calibration 3.4 %, hopper | H7 basis (§19), its tickets calibration |
| P2 | `LIMITATIONS.md` | §2b l.34–40 | "trained on 10 % reference devices" | Mark as roadmap / not in the product claim |
| P2 | `LIMITATIONS.md` | §2c l.43–45 | COMBI only, €1,034–3,008 | Keep; add capex €800–2,370 + upkeep €39–106/yr; "every new COMBI" |
| P2 | `LIMITATIONS.md` | §4 l.71–74; §8 l.100–110 | Europress fee placeholder; "€500 hopper … ~1.6 years … €2,363 … 9 years"; `business.py` | pricing.py results: −€4.5 M at €30, break-even €48, max capex €1,020; team case +€2.49 M |
| P2 | `README.md` | l.59–60 | `business.py` (deleted); `virtual_scale.py` as core | `pricing.py`; VS "roadmap analysis" |
| P2 | `part1/WEIGHING_CONCEPT.md` | §0 l.19–48; l.71; §3 l.105; §17 l.567–572 | Three-layer architecture, H1 recommended, "real scale does not have to go on every unit", `chosen_tier` H1 | H7-first one-pager; H1 and T0 as alternatives; VS roadmap |
| P2 | `part1/WEIGHING_CONCEPT.md` | §19 l.826; §19.8 l.1071–1089 | "a new idea to explore, not a design"; "H7 as a reference device … ~5 % … new COMBI units are enough" | "Chosen concept (untested)"; H7 on every new unit, H2 tickets calibrate it |
| P2 | `part1/RED_TEAM.md` | R27 l.46 | mitigation "H7 only for the reference subset" | Mitigation: operator fee + design-to-cost ≤ ~€1,000 + pilot; status open |
| P2 | `part1/README.md`; `part1/sigma_tiers.json` | l.3, l.12; `"chosen_tier": "H1"` | H1 deliverable / chosen tier | H7 |
| P2 | `OpenWeight.pdf` (outside repo) | p2/p4/p7 21 vs 9; p2 18 %; p5 ±3 %, ±30 kg, €550–1,100, "Europress own IP", "all compactors", "Varmennettu paino"; p6 €825/€190/yr, €130 visits, NPV +2.5 M€ unconditioned, Orbis profit; p7 pilot ~1 M€, 5–11 M€, demo €2,100–3,400; p3 "10–25 %" | see §C statuses | Apply §C; add cost-gap paragraph, CE note, 2014/31/EU, two H7 risks |
| P3 | `pipeline/fullload/pricing.py` | l.1, l.31; Business.tsx l.6 | cite `PRICING.md` (does not exist); "EUR 20 or 30?" | Point to MASTER.md §C4 or write PRICING.md |
| P3 | `pipeline/fullload/virtual_scale.py` | l.9, l.29, l.134–137 | reference devices (rails), `DEFAULT_SHARE = 0.10` | OK as roadmap analysis; no change needed unless shown |
| P3 | `part1/GATES_REPORT.md` QG7 l.48; `briefs/*` | lead story = virtual scale | historical | leave; do not cite |

Grep terms checked: reference, 10 %, 5 %, virtual scale, hopper, €20, 1.6 years, payback. "Payback" in
`web/src/pricing/model.ts` and `pricing.py` is current logic, not stale.

---

## H. DUO weighing mechanism (placeholder)

*Pending the separate DUO PDF review. To fill in: mechanism, statics, cost (capex/upkeep), accuracy, risks (coupling
load bypass RED_TEAM R10, container exchange, jack in the exchange path), the DUO share of the ~1,200 new units a
year, and the effect on `pricing.py` (capex mix). Until then the pitch says "every new COMBI; DUO under review".*

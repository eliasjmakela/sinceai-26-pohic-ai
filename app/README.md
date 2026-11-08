# OpenWeight: the two portals

**Pay for tonnes, not trips.** Fill level has been known for years, and the weight has belonged to the waste company. The compactor now weighs itself, so the customer can see whether the contract is kept and tender on a price per tonne, and every waste company can bid without guessing.

This app is the demo. Every screen serves that move:

| Portal | Screen | What it does |
|---|---|---|
| Customer (free) | Contract (opens first) | Is the contract kept? Response to orders, schedule, tickets, invoices. Every pickup traces from the order to the ticket, contract version and invoice lines |
| | Today | Each compactor's fill level and weight, when it needs a pickup (at 80 % full), cost per tonne before the truck leaves, and the decisions waiting, each with one action |
| | Tender | Offer comparison: the offers the customer received, uploaded to compare per tonne with service beside price |
| Waste company | Tenders | Offer planning for a tender request it uploaded (bid pack: the compactors and the forecast), opening on **Potential customers**: accounts in its region it doesn't serve yet, with contract end, its price and estimated margin (no customer names or prices) |

Each list holds only what needs doing, with one action per row. A finished item leaves the list, can be undone, and an empty list says so plainly.

## Run

From the repository root:

```bash
python -m venv .venv
.venv/bin/pip install -r app/requirements.txt
.venv/bin/python app/backend/build_data.py      # about 30 s; writes app/backend/data/
(cd app/frontend && npm install && npm run build)
echo "GEMINI_API_KEY=your-key" > app/.env       # optional
.venv/bin/uvicorn server:app --app-dir app/backend --port 8000
```

Open http://127.0.0.1:8000 and sign in as the customer or the waste company. The waste company plans its price for a tender request it has already uploaded; the customer compares offers it has already uploaded and chooses. OpenWeight does not pass offers between them: Europress doesn't want to sit in the middle of a tender, so offers travel the usual way. "Reset the demo" on the sign-in page clears the state.

## Where the figures come from

- **Market figures** come from the pipeline: `build_data.py` reads `pipeline/out/bundle.json` directly, so the app and the documents agree (`MASTER.md` section C). The demo account is the pitch's hero, ORG-0036. After `fullload build`, rerun `build_data.py`.
- **Row-level records** (each pickup, ticket, contract version, invoice line) are computed in `backend/build_data.py` with the challenge kit's baselines.
- **The price calculator** uses the team's market formula, `cost × (1 + margin) × (1 + σ)`. Its starting values reproduce the team's simulated bid of €18,745 (€91.41 per tonne).
- **Gemini never produces a figure.** It rewrites report paragraphs, the invoice query and the offer summary. A number guard rejects any reply containing a figure that isn't in the facts, and the app falls back to a template. `GEMINI_MODEL` changes the model (default `gemini-3.6-flash`).
- **Gemini is called only for wording it has never produced.** Replies are stored in `backend/llm_cache.json` by the hash of the model, prompt and facts, so reloads, demo resets and restarts cost nothing. Nothing is sent for 10 minutes after an error.

## Rules kept from the team's decisions

The bill stays on the certified weighbridge (Directive 2014/31/EU), and compactor weight is for planning and checking. Nothing says "verified". Biowaste is left out of the claims, there is no chat, and there's no route optimisation. No offer is relayed. The customer's prices, invoices and choice never reach the waste company's endpoints, and the API refuses the bid pack once the customer withdraws its weights.

## Invoice lines

The kit's `SCHEMA.md` warns that about 1.2 % of job references on invoices have typos and says to fall back to contract and service date. The pipeline (`invoice_lines_vs_contract`) and this app both do that, so a mistyped reference no longer counts its whole amount as above the contract, and both report 8 of 712 lines differing for ORG-0036, €269 above the contract. Two of those lines (€167) carry a job reference that matches no pickup at all.

## Assumptions

- Contract end dates assume a 3-year cycle from the start date. The dataset has no end dates.
- The 48-hour response time is an assumption. A real service reads it from the contract. It's measured on on-call orders, since scheduled pickups have no order time.
- Contract prices and invoices come from the customer. Europress isn't a party to them, so a real service would need the customer to add them.
- "Right now" uses each compactor's last reading in the data (30 Sep 2026) and the rates of its last 8 pickups, credits included.
- The customer's uploaded offers come from the market simulation: each bidder offers its own floor, and the winner (Hauler Epsilon, floor €18,745) prices at the runner-up's bid, €19,518 (€95.18 per tonne). So the lowest offer equals the pitch's best case (−€8,699), and Epsilon and Beta tie on price; the service record decides. The waste company's planned price is not sent anywhere.
- The −€8,699 is this account's best case. Across the region the simulated fall is about 12 %.
- The demo starts with one open tender and the weights already shared, so the customer's consent is assumed. The customer can withdraw it. The €500 bid pack is stated but not charged.
- Sign-in has no password: choosing a role only picks the portal. This isn't production security.

## Evaluation

Truck tare rule: of the labelled weight differences on flagged trucks, 97 % are tare errors, against 64 % elsewhere. An alternative weight-only rule for needless pickups (an app experiment, not the pitch's premature-lift rule, which scores F1 0.81 with 0 justified lifts flagged; see `docs/LIMITATIONS.md` §6), on the challenge's own evaluator (validation): recall 0.59 → 0.82, precision 0.90 → 0.84, F1 0.72 → 0.83, justified pickups flagged 0 → 16. Its threshold was chosen on the same period, so the result may be slightly optimistic. The app's "came early" list uses the team's rule, so that it agrees with the pitch.

## Third-party components

| Component | Licence | Use |
|---|---|---|
| pandas, NumPy, scikit-learn | BSD-3-Clause | data processing, baseline dependency |
| PyArrow | Apache-2.0 | Parquet |
| DuckDB, FastAPI | MIT | queries, API |
| Uvicorn | BSD-3-Clause | server |
| PyYAML, pytz, tabulate | MIT | baseline dependencies |
| google-genai | Apache-2.0 | Gemini client |
| React, React Router, Vite, @vitejs/plugin-react | MIT | frontend |
| TypeScript | Apache-2.0 | frontend build |
| @fontsource-variable/manrope | OFL-1.1 (font), MIT (package) | typeface |
| Google Gemini API | Google's API terms | wording of texts; check commercial-use terms before production |
| Challenge dataset and baselines | Since AI / Europress | synthetic data, calculations |

Licences are listed from memory of each project. Check them against the installed packages before submitting.

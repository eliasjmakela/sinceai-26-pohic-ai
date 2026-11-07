"""Final economics. Data = synthetic challenge dataset; ext = public sources (see PROJECT.md)."""
RATE, YEARS = .08, 6
ANN = sum(1 / (1 + RATE) ** t for t in range(1, YEARS + 1))

# --- Per device per year (data) ---
SPEND = 10_200            # customer total spend
FULL_LOAD_POOL = 1_269    # collection cost removed if every lift is full (-18 % lifts)
WASTED = 130              # wasted trips / missed visits operator could avoid
RISK_PER_BID = 1_930      # mis-pricing avoided per tendered site (21 % -> 9 % error)
TENDER_CYCLE = 3          # contracts tendered every ~3 years (challenge lead)

# --- Operator margins (ext) ---
MARGINS = {"L&T 2025 liikevoitto 8,0 %": .080, "L&T Q1/2026 −0,9 %": -.009, "Remeo 2025 −3,7 %": -.037}

op_value = FULL_LOAD_POOL / 2 + WASTED + RISK_PER_BID / TENDER_CYCLE
print("== 1. Jäteyhtiö: arvo ja maksukyky per laite/v")
print(f"   arvo: täydet kuormat {FULL_LOAD_POOL/2:.0f} + turhat käynnit {WASTED} + hinnoitteluriski {RISK_PER_BID/TENDER_CYCLE:.0f} = {op_value:.0f} €/v ({op_value/12:.0f} €/kk)")
for k, m in MARGINS.items():
    print(f"   {k:28s}: nykyinen liikevoitto per laite {SPEND*m:6.0f} €/v -> palvelun arvo on {op_value/max(SPEND*m,1):4.1f}x" if m > 0 else
          f"   {k:28s}: nykyinen liikevoitto per laite {SPEND*m:6.0f} €/v -> palvelu kääntää tappion voitoksi")
for share in (.15, .25, .35):
    print(f"   Europress ottaa {share:.0%} arvosta: {op_value*share/12:5.1f} €/kk, jäteyhtiölle jää {op_value*(1-share):.0f} €/v")
win_profit = SPEND * .08
print(f"   Haastaja voittaa kohteen: uusi liikevaihto {SPEND} €/v, liikevoitto 8 % = {win_profit:.0f} €/v x {TENDER_CYCLE} v = {win_profit*TENDER_CYCLE:.0f} €")
print(f"   -> tarjouspaketti 500 € on {500/(win_profit*TENDER_CYCLE):.0%} yhden voitetun sopimuksen voitosta")

# --- Hardware (ext + estimate) ---
HW = {"halpa (OEM-kennot, asennus uuden laitteen mukana)": 450, "perus": 650, "kallis (merkkikennot)": 1_000}
print("\n== 2. Punnituksen vuosikustannus per laite (6 v, 8 %, kalibrointi 50 €/v)")
for k, hw in HW.items():
    print(f"   {k:50s} {hw:5d} € -> {hw/ANN+50:4.0f} €/v = {(hw/ANN+50)/12:4.1f} €/kk")

# --- Europress 6-year P&L, weighing on every NEW device, customer pays nothing ---
N, NEW, MARGIN = 10_000, 10_000 / 6, .25 * 22_500
ADOPT = (.10, .25, .40, .50, .55, .60)
TSHARE = (.05, .15, .25, .30, .35, .35)
UPLIFT = (0, .01, .03, .05, .05, .05)

def pnl(fee=30, hw=650, tpack=500, bidders=2.5, adopt=ADOPT, uplift=UPLIFT, fixed=400_000, years=YEARS, show=False):
    w = npv = cum = 0; pb = None
    for y in range(years):
        i = min(y, 5)
        w = min(N, w + NEW)
        rev = w * adopt[i] * fee * 12 + (N / TENDER_CYCLE) * (w / N) * TSHARE[i] * tpack * bidders + NEW * uplift[i] * MARGIN
        cost = fixed + N * 26 + w * 50 + (NEW * hw if y < 6 else NEW * hw)
        cf = rev - cost; cum += cf; npv += cf / (1 + RATE) ** (y + 1)
        pb = pb or (y + 1 if cum >= 0 else None)
        if show: print(f"   v{y+1:2d} tulot {rev/1e3:6.0f}k  kulut {cost/1e3:6.0f}k  kassavirta {cf/1e3:6.0f}k  kertymä {cum/1e3:7.0f}k")
    return npv / 1e6, pb

print("\n== 3. Europress, punnitus jokaiseen uuteen laitteeseen, asiakas ei maksa (perus: 30 €/kk, 650 €, paketti 500 € x 2,5)")
print("   NPV %.2f M€, kertymä plussalla vuonna %s" % pnl(show=True))
print("   10 vuotta: NPV %.2f M€, plussalla vuonna %s" % pnl(years=10))
print("\n== 4. Herkkyys (6 v / 10 v NPV M€)")
cases = {"maksu 20 €/kk": dict(fee=20), "maksu 40 €/kk": dict(fee=40), "laite 450 €": dict(hw=450), "laite 1 000 €": dict(hw=1000),
         "ei lisämyyntiä": dict(uplift=(0,)*6), "omaksuminen puolet hitaampi": dict(adopt=tuple(a/2 for a in ADOPT)),
         "pessimistinen (20 €/kk, 1 000 €, hidas, ei lisämyyntiä)": dict(fee=20, hw=1000, adopt=tuple(a/2 for a in ADOPT), uplift=(0,)*6)}
for k, kw in cases.items():
    a, b = pnl(**kw)[0], pnl(years=10, **kw)[0]
    print(f"   {k:55s} {a:6.2f} / {b:6.2f}")
print("\n== 5. Kannattavuusraja: pienin maksu €/kk, jolla NPV >= 0")
for hw in (450, 650, 1000):
    f6 = next(f for f in range(200) if pnl(fee=f, hw=hw)[0] >= 0)
    f10 = next(f for f in range(200) if pnl(fee=f, hw=hw, years=10)[0] >= 0)
    print(f"   laite {hw:5d} €: 6 v {f6} €/kk, 10 v {f10} €/kk")

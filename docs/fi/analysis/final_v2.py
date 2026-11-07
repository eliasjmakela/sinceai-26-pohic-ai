"""Final model with public figures. Weighing on every NEW device, customer pays nothing.
Sources: synthetic dataset (values per device), L&T Q1/2026, Asiakastieto (Stena), Finder (Remeo),
challenge lead (10 000 devices FI, 20-25 k€ COMBI, ~3 yr tender cycle), BOM estimate (team + distributor ranges)."""
RATE = .08
N = 10_000                 # Finnish installed base (challenge lead)
LIFE = 8                   # device life in years -> new/replacement devices per year
NEW = N / LIFE             # 1 250/yr  (x ~22 k€ ≈ 27 M€ equipment sales, plausible vs ~40 M€ Finnish entity)
DEVICE_PRICE, CONTRIB = 22_500, .25
TENDER_CYCLE, BIDDERS, TPACK = 3, 2.5, 500

BOM = {  # per device, installed with a new device
    "matala": dict(cells=4*60,  box=40, amp=60,  cable=30, mech=80,  install=80),
    "perus":  dict(cells=4*100, box=50, amp=100, cable=50, mech=100, install=100),
    "korkea": dict(cells=4*200, box=50, amp=100, cable=50, mech=150, install=150),
}
HW = {k: sum(v.values()) for k, v in BOM.items()}

def pnl(fee=30, hw=HW["perus"], adopt_max=.60, ramp=4, uplift_max=.05, years=10, fixed=400_000,
        pilot=False, show=False):
    w = cum = npv = 0; pb = None; trough = 0; rows = []
    for y in range(years):
        if pilot and y < 2:
            add = 1_000 if y == 0 else 0           # pilot region retrofit-free: 1 000 new installs
        else:
            add = NEW
        w = min(N, w + add)
        a = adopt_max * min(1, (y + 1) / ramp)    # operator adoption ramps to max in `ramp` years
        u = uplift_max * min(1, max(0, y) / ramp)
        sub = w * a * fee * 12
        tender = (N / TENDER_CYCLE) * (w / N) * (a / adopt_max) * .35 * TPACK * BIDDERS
        sales = NEW * u * DEVICE_PRICE * CONTRIB
        opex = fixed + w * 26 + w * 50          # platform+LLM 26 €/dev, calibration/service 50 €/dev
        capex = add * hw
        cf = sub + tender + sales - opex - capex
        cum += cf; npv += cf / (1 + RATE) ** (y + 1); trough = min(trough, cum)
        pb = pb or (y + 1 if cum >= 0 else None)
        rows.append((y + 1, w, sub, tender, sales, opex, capex, cf, cum))
    if show:
        print(f"{'v':>3} {'punnittu':>8} {'jäteyhtiöt':>10} {'paketit':>8} {'lisämyynti':>10} {'kulut':>8} {'invest.':>8} {'kassav.':>8} {'kertymä':>8}")
        for r in rows:
            print(f"{r[0]:>3} {r[1]:>8.0f} " + " ".join(f"{x/1e6:>9.2f}" for x in r[2:]))
    return npv / 1e6, pb, trough / 1e6

print("Punnituksen hinta asennettuna:", {k: f"{v} €" for k, v in HW.items()})
print("\n== Perus: 30 €/kk, perus-BOM, omaksuminen 60 % / 4 v, lisämyynti 5 %, 10 v (M€)")
npv, pb, tr = pnl(show=True)
print(f"NPV {npv:.2f} M€, kertymä plussalla vuonna {pb}, syvin kertymä {tr:.2f} M€")
print("\n== Pilotti ensin (1 000 laitetta 2 v, sitten koko kanta)")
npv, pb, tr = pnl(pilot=True)
print(f"NPV {npv:.2f} M€, plussalla vuonna {pb}, syvin kertymä {tr:.2f} M€")

print("\n== Herkkyys: NPV 10 v (M€) / plussalla vuonna / syvin kertymä")
cases = {
  "perus": {},
  "maksu 20 €/kk": dict(fee=20), "maksu 40 €/kk": dict(fee=40),
  "BOM matala": dict(hw=HW["matala"]), "BOM korkea": dict(hw=HW["korkea"]),
  "omaksuminen 40 %": dict(adopt_max=.40), "omaksuminen 80 %": dict(adopt_max=.80),
  "hidas ramppi 6 v": dict(ramp=6), "ei lisämyyntiä": dict(uplift_max=0),
  "pessimistinen (20 €/kk, BOM korkea, 40 %, 6 v, ei lisämyyntiä)": dict(fee=20, hw=HW["korkea"], adopt_max=.4, ramp=6, uplift_max=0),
  "optimistinen (40 €/kk, BOM matala, 80 %, 3 v, 8 %)": dict(fee=40, hw=HW["matala"], adopt_max=.8, ramp=3, uplift_max=.08),
}
for k, kw in cases.items():
    n, p, t = pnl(**kw)
    print(f"  {k:62s} {n:6.2f} {str(p):>5} {t:6.2f}")
print("\n== Kannattavuusraja: pienin maksu €/kk, jolla NPV(10 v) >= 0")
for b, hw in HW.items():
    for am in (.4, .6):
        f = next(f for f in range(300) if pnl(fee=f, hw=hw, adopt_max=am)[0] >= 0)
        print(f"  BOM {b:6s} ({hw} €), omaksuminen {am:.0%}: {f} €/kk")

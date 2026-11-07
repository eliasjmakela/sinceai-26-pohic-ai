"""6-year rollout P&L for Europress (Finland, 10 000 devices). Team assumptions, see PROJECT.md."""
import itertools

def run(fee=20, adopt=(.10, .25, .40, .50, .55, .60), tender_share=(.05, .15, .25, .30, .35, .35),
        uplift=(0, .01, .03, .05, .05, .05), rail_cost=800, retrofit=(500, 300, 0, 0, 0, 0), retro_cost=1500, rail_share=1.0,
        fixed=400_000, rate=.08, verbose=False):
    N, NEW, TENDERS = 10_000, 10_000 / 6, 10_000 / 3
    MARGIN = .25 * 22_500
    rails, npv, cum, payback = 0, 0, 0, None
    rows = []
    for y in range(6):
        rails += NEW * rail_share + retrofit[y]
        capex = NEW * rail_share * rail_cost + retrofit[y] * retro_cost
        sub = N * adopt[y] * fee * 12
        tender = TENDERS * tender_share[y] * 200
        sales = NEW * uplift[y] * MARGIN
        opex = fixed + N * 26 + rails * 50
        cf = sub + tender + sales - opex - capex
        cum += cf
        npv += cf / (1 + rate) ** (y + 1)
        if payback is None and cum >= 0:
            payback = y + 1
        rows.append((y + 1, sub, tender, sales, opex, capex, cf, cum))
    if verbose:
        print(f"{'v':>2} {'palvelu':>9} {'tarjous':>8} {'lisämyynti':>10} {'kulut':>9} {'invest.':>9} {'kassavirta':>10} {'kertymä':>9}")
        for y, *v in rows:
            print(f"{y:>2} " + " ".join(f"{x/1e3:>9.0f}k" for x in v))
    return npv, payback

BASE = dict(rail_share=.10, retrofit=(300, 0, 0, 0, 0, 0))
print("== Perusskenaario: kiskot 10 % uusista + 300 kalibrointikohdetta (k€)")
npv, pb = run(verbose=True, **BASE)
print(f"NPV 6 v: {npv/1e6:.2f} M€, kertymä plussalla vuonna {pb}\n")
print("== Herkkyys")
for name, kw in {
    "maksu 10 €/kk": dict(fee=10),
    "maksu 30 €/kk": dict(fee=30),
    "omaksuminen puolet hitaampi": dict(adopt=(.05, .12, .20, .25, .28, .30)),
    "ei lisämyyntiä": dict(uplift=(0,) * 6),
    "kiskot 1 200 € asennettuna": dict(rail_cost=1200),
    "kiskot kaikkiin uusiin": dict(rail_share=1.0),
    "kiskot 30 % uusista": dict(rail_share=.30),
    "pessimistinen (10 €/kk, puolet hitaampi, ei lisämyyntiä)": dict(fee=10, adopt=(.05, .12, .20, .25, .28, .30), uplift=(0,) * 6),
}.items():
    npv, pb = run(**{**BASE, **kw})
    print(f"  {name:55s} NPV {npv/1e6:5.2f} M€, plussalla vuonna {pb}")
print("\n== Kannattavuusraja: pienin maksu (€/kk), jolla NPV >= 0")
for adopt_name, ad in {"perus": (.10, .25, .40, .50, .55, .60), "hidas": (.05, .12, .20, .25, .28, .30)}.items():
    for upl in ((0, .01, .03, .05, .05, .05), (0,) * 6):
        f = next(f for f in range(0, 200) if run(fee=f, adopt=ad, uplift=upl, **BASE)[0] >= 0)
        print(f"  omaksuminen {adopt_name}, lisämyynti {'kyllä' if upl[-1] else 'ei'}: {f} €/kk")

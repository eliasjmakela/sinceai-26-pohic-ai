"""Weighing rails on EVERY device. Who pays the hardware? 6-year P&L, Finland 10 000 devices."""
N, NEW, TENDERS, MARGIN, RATE = 10_000, 10_000 / 6, 10_000 / 3, .25 * 22_500, .08
ADOPT = (.10, .25, .40, .50, .55, .60)          # operators paying the service
TSHARE = (.05, .15, .25, .30, .35, .35)
UPLIFT = (0, .01, .03, .05, .05, .05)

def run(hw=800, retro=0, retro_hw=1500, fee=20, lease=0, tpack=200, adopt=ADOPT, uplift=UPLIFT, fixed=400_000):
    """retro: share of installed base retrofitted in year 1; lease: €/kk added to the device lease."""
    weighed, npv, cum, pb = 0, 0, 0, None
    for y in range(6):
        add_new, add_retro = NEW, (N - NEW) * retro if y == 0 else 0
        weighed = min(N, weighed + add_new + add_retro)
        capex = add_new * hw + add_retro * retro_hw
        rev = weighed * adopt[y] * fee * 12 + TENDERS * TSHARE[y] * tpack * weighed / N \
              + weighed * lease * 12 + NEW * uplift[y] * MARGIN
        cf = rev - fixed - N * 26 - weighed * 50 - capex
        cum += cf; npv += cf / (1 + RATE) ** (y + 1)
        pb = pb or (y + 1 if cum >= 0 else None)
    return npv / 1e6, pb, weighed

S = {
 "A  Europress maksaa kaiken, uudet laitteet (800 €)":            dict(),
 "B  + volyymihinta 400 € (kennot sarjatuotannossa)":              dict(hw=400),
 "C  Vuokraan +10 €/kk, Europress 800 €":                          dict(lease=10),
 "D  Vuokraan +15 €/kk, Europress 800 €":                          dict(lease=15),
 "E  Vuokraan +10 €/kk, 400 €":                                    dict(lease=10, hw=400),
 "F  E + jälkiasennus 30 % kannasta (1 500 €)":                    dict(lease=10, hw=400, retro=.3),
 "G  E, jäteyhtiömaksu 30 €/kk":                                   dict(lease=10, hw=400, fee=30),
 "H  E, pessimistinen (10 €/kk, puolet hitaampi, ei lisämyyntiä)": dict(lease=10, hw=400, fee=10, adopt=tuple(a/2 for a in ADOPT), uplift=(0,)*6),
}
print(f"{'skenaario':66s} {'NPV M€':>7} {'kertymä +':>9} {'punnittu v6':>11}")
for k, kw in S.items():
    npv, pb, w = run(**kw)
    print(f"{k:66s} {npv:7.2f} {str(pb):>9} {w:11.0f}")

hw_year = 800 / 4.623 + 50
print(f"\nLaitteiston vuosikustannus (800 €, 6 v, 8 %): {hw_year:.0f} €/laite/v = {hw_year/12:.1f} €/kk")
print("Arvo per laite/v: asiakas ~1 900 €, jäteyhtiö ~1 400 € -> yhteensä ~3 300 € = "
      f"{3300/hw_year:.0f}x laitteiston kustannus")

print("\n== Tarjouspaketti hinnoiteltuna arvon mukaan (1 930 €/kohde arvo tarjoajalle; 2,5 tarjoajaa ostaa à 500 € = 1 250 €/kohde)")
S2 = {
 "I  Europress maksaa kaiken 800 €, ei vuokralisää":                dict(tpack=1250),
 "J  400 €, ei vuokralisää":                                        dict(tpack=1250, hw=400),
 "K  600 €, vuokraan +5 €/kk":                                      dict(tpack=1250, hw=600, lease=5),
 "L  600 €, vuokraan +10 €/kk":                                     dict(tpack=1250, hw=600, lease=10),
 "M  L pessimistinen (10 €/kk, puolet hitaampi, ei lisämyyntiä)":   dict(tpack=1250, hw=600, lease=10, fee=10, adopt=tuple(a/2 for a in ADOPT), uplift=(0,)*6),
 "N  L + jälkiasennus 30 % kannasta":                               dict(tpack=1250, hw=600, lease=10, retro=.3),
}
for k, kw in S2.items():
    npv, pb, w = run(**kw)
    print(f"{k:66s} {npv:7.2f} {str(pb):>9}")

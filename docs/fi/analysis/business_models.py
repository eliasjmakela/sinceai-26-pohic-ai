"""Per-device economics of business models over a 6-year lease. All prices are team assumptions."""
YEARS, RATE = 6, 0.08
ANNUITY = sum(1 / (1 + RATE) ** t for t in range(1, YEARS + 1))
OPEX = 74  # €/device/yr: data platform 24 + calibration/support 50 (assumption)

# Value pools per device/yr from value_pools.py (synthetic data)
OPERATOR_RISK_REDUCTION = 2900 - 970   # transport mis-pricing blind vs profile
CUSTOMER_AVOIDABLE_LIFTS = 1572

HW = {"vaakataso nyt (~20 % laitteen hinnasta)": 4500, "vetäjän mainitsema": 2000,
      "suppilopunnitus (anturit)": 500, "virtuaalivaaka (ohjelmisto)": 0}

print(f"Annuiteettikerroin {YEARS} v / {RATE:.0%}: {ANNUITY:.2f}\n")
print("1) Europress maksaa punnituksen – mikä kuukausimaksu laitetta kohden tarvitaan, jotta kannattaa:")
for name, hw in HW.items():
    for cov in (1.0, 0.5):
        fee = (hw / ANNUITY + OPEX) / 12 / cov
        print(f"   {name:40s} maksajia {cov:4.0%}: {fee:6.1f} €/kk")

print("\n2) Mikä punnituslaite on enintään kannattava, kun jäteyhtiö maksaa F €/kk ja 50 % laitteista on maksavan yhtiön piirissä:")
for fee in (10, 15, 25, 40):
    hw_max = (fee * 12 * 0.5 - OPEX) * ANNUITY
    print(f"   F = {fee:3d} €/kk -> laite enintään {max(hw_max,0):6.0f} €")

print("\n3) Mitä jäteyhtiö saa ja mitä se voisi maksaa:")
for share in (0.1, 0.2, 0.3):
    print(f"   osuus {share:.0%} hinnoitteluriskin pienenemisestä ({OPERATOR_RISK_REDUCTION} €/v): "
          f"{OPERATOR_RISK_REDUCTION*share/12:5.1f} €/kk")

print("\n4) Loppuasiakas maksaa itse (vertailu): Insights-osuus 15 %, hinta 10 €/kk")
print(f"   tulo keskimäärin per laite: {0.15*10*12:.0f} €/v  vs. asiakkaan saama hyöty {CUSTOMER_AVOIDABLE_LIFTS} €/v")

print("\n5) Lisämyynti (oletus: 10 000 laitetta, uusiutuu 6 v välein, kate 25 % x 22 500 €):")
renew = 10000 / YEARS
for uplift in (0.02, 0.05, 0.10):
    extra = renew * uplift * 0.25 * 22500
    print(f"   +{uplift:.0%} myyntiä -> {extra/1e6:4.2f} M€/v = {extra/10000:5.0f} €/laite/v")

print("\n6) Koko verkosto (10 000 laitetta), suositeltu malli: virtuaalivaaka kaikkiin + suppilopunnitus 30 %:iin,")
print("   jäteyhtiö maksaa 20 €/kk 50 %:sta laitteista, +5 % lisämyynti:")
hw_total = 0.3 * 10000 * 500
rev = 10000 * 0.5 * 20 * 12
opex = 10000 * OPEX
sales = renew * 0.05 * 0.25 * 22500
print(f"   investointi {hw_total/1e6:.1f} M€, palvelutulo {rev/1e6:.2f} M€/v, kulut {opex/1e6:.2f} M€/v, "
      f"lisämyynnin kate {sales/1e6:.2f} M€/v")
npv = -hw_total + (rev - opex + sales) * ANNUITY
print(f"   nettonykyarvo 6 v: {npv/1e6:.1f} M€, takaisinmaksu {hw_total/(rev-opex+sales)*12:.0f} kk")

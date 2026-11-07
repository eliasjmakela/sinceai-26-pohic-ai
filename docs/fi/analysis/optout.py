"""Free weighing (100 % coverage) vs. charging the customer +10 €/kk with opt-outs.
Network effect: an operator's willingness to adopt, and tender usefulness, scale with coverage**k."""
N, NEW, TENDERS, MARGIN, RATE = 10_000, 10_000 / 6, 10_000 / 3, .25 * 22_500, .08
ADOPT = (.10, .25, .40, .50, .55, .60)
TSHARE = (.05, .15, .25, .30, .35, .35)
UPLIFT = (0, .01, .03, .05, .05, .05)

def run(lease=0, optout=0, k=1.5, hw=600, fee=20, tpack=1250, fixed=400_000):
    cov = 1 - optout
    net = cov ** k                       # network effect on operator adoption and tender usefulness
    weighed, npv, cum, pb = 0, 0, 0, None
    for y in range(6):
        add = NEW * cov
        weighed += add
        rev = (weighed * ADOPT[y] * net * fee * 12            # operator subscriptions on weighed devices
               + TENDERS * (weighed / N) * TSHARE[y] * net * tpack
               + weighed * lease * 12                          # customer lease add-on
               + NEW * UPLIFT[y] * net * MARGIN)               # sales uplift via operator promotion
        cf = rev - fixed - N * 26 - weighed * 50 - add * hw
        cum += cf; npv += cf / (1 + RATE) ** (y + 1)
        pb = pb or (y + 1 if cum >= 0 else None)
    return npv / 1e6, pb

base, _ = run()
print(f"Ilmainen asiakkaalle, kattavuus 100 %: NPV {base:.2f} M€\n")
print(f"{'pois jättävät':>13} | {'k=1 (lineaarinen)':>18} | {'k=1.5':>8} | {'k=2 (vahva verkostovaikutus)':>28}")
for p in (0, .1, .2, .3, .5):
    row = [run(lease=10, optout=p, k=k)[0] for k in (1, 1.5, 2)]
    print(f"{p:13.0%} | {row[0]:18.2f} | {row[1]:8.2f} | {row[2]:28.2f}")
print("\nKannattavuusraja: montako % saa jättää pois, ennen kuin maksullinen on huonompi kuin ilmainen")
for k in (1, 1.5, 2):
    p = next(p / 100 for p in range(0, 101) if run(lease=10, optout=p / 100, k=k)[0] < base)
    print(f"  k={k}: {p:.0%}")

print("\nIlmainen malli: millä jäteyhtiön kuukausimaksulla NPV >= 0 (tarjouspaketti 1 250 €/kohde)?")
f = next(f for f in range(0, 200) if run(fee=f)[0] >= 0)
print(f"  {f} €/kk")
for hw in (400, 500):
    f = next(f for f in range(0, 200) if run(fee=f, hw=hw)[0] >= 0)
    print(f"  laitteisto {hw} €: {f} €/kk")

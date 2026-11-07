"""Review check script for H7-2 (two-end lift, WEIGHING_CONCEPT.md §20; reviews/DUO_MECHANISM_REVIEW.md).

Scratch-level checks behind the §20 numbers, kept for traceability. Run: python calc/h7_2_statics.py (prints only).
"""
import math, random, statistics as st
from statistics import NormalDist
N=NormalDist()
g=9.81
# implied sigma from "within +-5% in p of readings" (unbiased normal)
for p in (0.999,0.956):
    z=N.inv_cdf(0.5+p/2); print(f"p={p}: z={z:.3f} sigma={5/z:.2f}%")
# our case C -> P(|e|<5%)
for s in (0.9,1.9,4.8,1.7,3.2,8.4):
    print(f"sigma {s}% -> P(<5%) {2*N.cdf(5/s)-1:.3f}")
# audit floor 1.3% over 20 pickups
print("audit: sigma if 1.3 = 1.96 s/sqrt20:", 1.3*math.sqrt(20)/1.96, " if 1.3 = s/sqrt20:", 1.3*math.sqrt(20))
# cost %
print(860/20000*100, 1725/20000*100, 860/25000*100, 1725/25000*100)
# geometry: assume bf, br, a, c (m from front)
def forces(M,xm,Wst,xw,bf,br,a,c):
    W=M+Wst; x=(M*xm+Wst*xw)/W
    Rf=W*(br-x)/(br-a); Rr=W*(x-bf)/(c-bf); return W,x,Rf,Rr
A80=math.pi*0.08**2/4
for bf,br in ((0.3,6.7),(0.5,6.5)):
  for M,share in ((3.0,0.55),(4.5,0.70)):
    xm=br-share*(br-bf)
    for Wst,xw in ((0,3.5),(5.0,3.0),(5.0,4.5)):
        W,x,Rf,Rr=forces(M,xm,Wst,xw,bf,br,0.8,6.2)
        print(f"bf{bf} br{br} M{M} sh{share} W{Wst}@{xw}: x={x:.2f} Rf={Rf*g:.1f}kN {Rf*g*1e3/A80/1e5:.0f}bar Rr={Rr*g:.1f}kN {Rr*g*1e3/A80/1e5:.0f}bar")
# sensitivity of net waste to pivot position error (tare and full with different pivot error)
def solve(Rf,Rr,bf,br,a,c): return (Rf*(br-a)+Rr*(c-bf))/(br-bf)
bf,br,a,c=0.4,6.6,0.8,6.2; M=4.0; xm=br-0.625*(br-bf); Wst=2.5; xw=3.8
for d in (0.01,0.02,0.05):
    # pivot truly at bf+d in full reading only (settling), model uses bf
    W,x,Rf,Rr=forces(M,xm,Wst,xw,bf+d,br,a,c)
    We,xe,Rfe,Rre=forces(M,xm,0,xw,bf,br,a,c)
    net=solve(Rf,Rr,bf,br,a,c)-solve(Rfe,Rre,bf,br,a,c)
    # same pivot error in both (constant): 
    W2,_,Rf2,Rr2=forces(M,xm,0,xw,bf+d,br,a,c)
    net2=solve(Rf,Rr,bf,br,a,c)-solve(Rf2,Rr2,bf,br,a,c)
    print(f"front pivot shift {d*100:.0f}cm between tare/full: net err {100*(net-Wst)/Wst:.2f}%  constant: {100*(net2-Wst)/Wst:.2f}%")
    W,x,Rf,Rr=forces(M,xm,Wst,xw,bf,br-d,a,c)
    net=solve(Rf,Rr,bf,br,a,c)-solve(Rfe,Rre,bf,br,a,c)
    print(f"  rear pivot shift {d*100:.0f}cm: net err {100*(net-Wst)/Wst:.2f}%")
# sensor: one shared sensor 0-250 bar, 0.1-0.25%FS -> kg of total W per bar for each cylinder
for lev in (0.10,0.15,0.25):
    dp=lev/100*250  # bar
    dF=dp*1e5*A80/g # kg-force
    # W error from Rf: dW = dRf*(br-a)/(br-bf); from Rr: dRr*(c-bf)/(br-bf); tare + full => 4 readings
    e=math.sqrt(2*((dF*(br-a)/(br-bf))**2+(dF*(c-bf)/(br-bf))**2))
    print(f"sensor {lev}%FS: {dp:.2f} bar = {dF:.0f} kgf; net waste sigma {e:.0f} kg = {100*e/2500:.1f}% of 2.5t, {100*e/5000:.1f}% of 5t")
# lateral triangle half-width at CoG, runner spacing 1.0 m
for (name,piv,cyl,xx) in (("step1",br,a,3.3),("step2",bf,c,3.3)):
    hw=0.5*abs(xx-cyl)/abs(piv-cyl); print(name,"half width at CoG",round(hw,2))
# tilt change between 20 and 30 mm lift: CoG horizontal shift h*dtheta
for h in (1.0,1.5):
    dth=0.010/(br-a); print("h",h,"shift mm",round(h*dth*1000,2),"relative to arm 3 m %",round(h*dth/3*100,3))
# stroke: feet >=30mm above rail underside + 30mm lift
print("stroke needed before ground tolerance:",30+30,"mm")
# oil per lift 30mm both
print("oil cm3 per 30mm lift:", A80*0.03*1e6)
# runner rise near pivot for step 2: point 1 m from front pivot, 10/30mm lift at c
for lift in (10,30): print("rise 1m from pivot", lift*1/(c-bf))

"""Review check script for H7-2 (two-end lift, WEIGHING_CONCEPT.md §20; reviews/DUO_MECHANISM_REVIEW.md).

Scratch-level checks behind the §20 numbers, kept for traceability. Run: python calc/h7_2_cost.py (prints only).
"""
lab=(55,90)
h7={"sensors":(60,200),"electronics":(40,150),"mechanical":(450,950),"site work":(0,150),"labour":(165,540),"calibration":(55,180),"maintenance (6 y)":(234,638),"development (NRE)":(30,200)}
# two-end (Duo sheet) team estimate
insp=(0.75*6*lab[0],0.75*6*lab[1])
seal=(2*0.30*(80+2*lab[0]),2*0.60*(300+2*lab[1]))
sens=(0.20*60,0.40*200)
maint=tuple(round(insp[i]+seal[i]+sens[i]) for i in (0,1))
print("insp",insp,"seal",seal,"sens",sens,"maint",maint)
duo={"sensors":(80,270),"electronics":(50,190),"mechanical":(900,1900),"site work":(0,250),
     "labour":(5*lab[0],9*lab[1]),"calibration":(round(1.5*lab[0]),round(3*lab[1])),
     "maintenance (6 y)":maint,"development (NRE)":(round(200e3/5000),round(550e3/2000))}
for name,d in (("H7",h7),("two-end",duo)):
    lo=sum(v[0] for v in d.values()); hi=sum(v[1] for v in d.values())
    cap_lo=lo-d["maintenance (6 y)"][0]; cap_hi=hi-d["maintenance (6 y)"][1]
    hw=(d["sensors"][0]+d["electronics"][0]+d["mechanical"][0], d["sensors"][1]+d["electronics"][1]+d["mechanical"][1])
    print(name,d,"total",lo,hi,"capex",cap_lo,cap_hi,"hardware",hw, "vs 20k %",round(cap_lo/200,1),round(cap_hi/200,1))
# DUO product docking jack (order of magnitude)
dock={"sensors":(80,250),"electronics":(100,350),"mechanical":(700,1800),"site work":(300,1500),
      "labour":(6*lab[0],16*lab[1]),"calibration":(round(2*lab[0]),round(5*lab[1])),"maintenance (6 y)":(300,900),"development (NRE)":(50,300)}
lo=sum(v[0] for v in dock.values()); hi=sum(v[1] for v in dock.values())
print("dock",dock,lo,hi,"capex",lo-300,hi-900)
# DUO container forces: container 2-3 t + 8 t waste, coupling-end share 0.4-0.6, 80 & 100 mm bore
import math
for b in (80,100):
    A=math.pi*(b/1000)**2/4
    for F in ((2.0*0.4)*9.81,(11*0.6)*9.81):
        print(b,"mm", round(F,1),"kN", round(F*1e3/A/1e5),"bar")

# Questions for a Europress engineer (Discord-ready, ≤ 14)

Context (updated 7 Nov evening): our chosen concept is now the H7 hydraulic self-lift on every new COMBI
(`WEIGHING_CONCEPT.md` §0, §19; questions 11–14). Questions 1–10 are about the earlier lead and the DUO option, Tommi's hopper idea: a load-cell plate in the
charging-chamber floor weighs each charge before and after the ram stroke, and the fleet calibrates the sum from
shared weighbridge tickets. We are not mechanical engineers; these are the facts we could not find publicly.

1. **Chamber floor.** Could a ~1.4 × 0.8 m part of the charging-chamber floor be a separate plate on four load cells
   (with overload stops), without weakening the chamber? Is the floor the same design on COMBI and DUO?
2. **Ram guidance and cycle.** Does the ram slide on the chamber floor or on side guides / wear strips? What is the
   stroke sequence (door switch → start delay → stroke → retract), and how is spill-back prevented?
3. **Floor loads.** Roughly what vertical pressure does the floor see during a stroke? We estimate 7–14 t on such a
   plate (25 t ram force, our assumed pressure ratio 0.3–0.6; `calc/loads.py`).
4. **Start delay.** Could the automatic press start wait 2–3 s after the door closes, so the plate can settle and be
   read? Does SMART log door and cycle events with timestamps?
5. **Bridging.** In your experience, how much of a thrown charge (cardboard boxes, film, bags) stays wedged in the
   hopper or on top of the ram instead of falling to the floor? We guessed 1–6 % depending on material.
6. **Liquids.** Where do liquids go in a biowaste COMBI, during compaction and when the unit is tipped for emptying?
   Is there a sump or drain we could route the plate's gap into?
7. **Climate.** What temperature range must components in the press section survive (we assume −30…+35 °C)?
   Load-cell datasheets compensate only from −10 °C.
8. **Rails (H5).** Do your guide rails carry the whole weight of a COMBI (8–9.5 t) or a DUO container, or does part of
   it go through the skids, feet or the DUO coupling? How fast does a hook-lift typically set a unit down?
9. **Platform scales.** Why are the existing platform scales "almost as expensive"? Which part dominates: the scale,
   the foundation, installation, or verification?
10. **Modem.** Does the SMART modem have a free serial / I²C port and power for a 4-channel weighing board?

H7, the team's hydraulic self-lift idea (§19): a COMBI lifts its own door end ~10 mm with one cylinder on its
own power pack, and the pressure gives the weight.

11. **Rear frame.** Is there room between the runners, 0.5–1 m from the door end, for a cylinder housing (80 mm bore,
    50 mm stroke)? Could the frame there take a 30–60 kN point load with local reinforcement?
12. **Hydraulics and safety.** What is the maximum system pressure (we assume ~200 bar)? Is there a free valve section?
    Would an automatic 10 mm self-lift at night be acceptable in your machinery risk assessment, and is pump noise
    a problem? Do you have OEM prices for a small cylinder, valve and pressure sensor?
13. **Ground.** How often do COMBIs stand on guide rails, plinths, gravel or asphalt rather than concrete? How much
    clearance is there under the frame?
14. **Fill pattern.** Is the press at the hook end? Where does waste build up first in a CombiMax: at the ram face, or
    pushed towards the door? Does the ram's pressure rise per stroke show how far the packed waste reaches?
15. **Runners.** How far apart are a CombiMax's runners, and how often is waste loaded off-centre (one side heavier)?
    In winter, do runners freeze to the ground, and is there ice or debris under the front of the runners?
16. **Front frame (H7-2).** Is there room between the runners about 0.8 m from the front, under the press unit, for
    an 80 mm cylinder housing with an 80–100 mm stroke? Can the frame there take up to ~65 kN with local
    reinforcement? Does the truck's tilting frame or roller pass there during pick-up?
17. **Docked units.** How many COMBIs stand against a wall chute, hood or bin lifter fixed to the building? Would a
    10–30 mm rise of the press end touch it?
18. **Pivots.** When one end of a CombiMax is lifted, where does the other end rest: on the rear rollers or on the
    runner ends? Are the runner fronts curved up, and where does the flat part start?
19. **DUO coupling and containers.** How is a DUO container coupled to the press (latches, hydraulic clamps)? Does
    the coupling carry vertical load? Could it be released for ~2 min before pick-up? How many container models
    rotate through one DUO site?

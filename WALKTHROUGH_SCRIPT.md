# Walkthrough video script (~4:30)

Record from the frozen build: `cd web && npm run build && npm run preview`, then open the printed URL at
`#/beat-1`. Browser full screen, 1440×900 or larger, zoom 100 %. Press → to move on; nothing needs typing. The
words below are a draft to say in your own words. The numbers are the ones on screen; keep them as they are.

| Time | Screen and action | Say |
|---|---|---|
| 0:00–0:15 | `#/beat-1` | "Europress compactors sit behind shops and warehouses. A truck empties them, and the customer pays per visit." |
| 0:15–0:50 | Point at the three compactors | "The visit costs about the same, €143 to €160, whether the compactor is half empty or full. So a half-empty visit costs €167 per tonne and a full one €49: 3.4 times more. Real HSY data shows the same: about a third of emptyings happen below half full." |
| 0:50–1:15 | Point at 56.5 % and 0 of 19 | "More than half of what customers pay is per visit, not per tonne. Why does nobody offer per-kilo prices? Only the incumbent knows how much each site produces. A challenger has to guess, so in our simulated region none of the 19 customers can safely be won." |
| 1:15–1:20 | → to `#/beat-2` | |
| 1:20–1:45 | Read the headline | "So we need the weight. The compactor can weigh itself with the hydraulics it already has. One extra cylinder lifts the door end ten millimetres." |
| 1:45–2:15 | Click **1 · Empty unit**, wait, then **2 · Full unit** | "Empty: 27 bar. Full: 57 bar. Each bar is about 85 kilos of waste, so that's two and a half tonnes. The lift is drawn exaggerated; it really is ten millimetres in fifteen seconds." |
| 2:15–2:45 | Point at accuracy, cost, limits | "After ten weighbridge tickets the estimate is within about 4 % (an estimate; nothing is built yet). It costs around a thousand euros on a new unit, against up to €22,000 for today's platform scale. We know the limits: new COMBIs only, a CE risk assessment, ground and ice." |
| 2:45–2:55 | Point at card c | "And the bill never changes: we bill by the real scale, the operator's certified weighbridge. The self-lift is for planning." |
| 2:55–3:00 | → to `#/beat-3` | |
| 3:00–3:10 | Screen opens on "today" | "Here is the market today: the customer pays the incumbent per trip." |
| 3:10–3:40 | → three times, one per step | "One: the compactor weighs every lift. Two: Europress gives every operator the same data. Three: operators bid per kilo, and the customer picks the best price." |
| 3:40–4:10 | Results appear; point at the KPIs | "In our simulated region the customer pays about 12 % less per tonne, there are 19 % fewer truck visits, and every customer is open to a challenger." |
| 4:10–4:30 | Point at the three party cards | "The customer pays nothing. Operators pay €30 per device per month. For Europress, at a thousand euros per self-lift, that pays back in year nine; €30 is the break-even fee. Europress becomes a service company, and it never drives a truck." |

Optional (if time allows, after 4:30): open **Details → Customer** to show the AI-summarized report and the
Approve button, and **Details → Business** to move the fee and self-lift cost sliders.

Checklist before recording:
- [ ] Fresh build from the frozen commit (`git describe --tags` shows `demo-frozen`).
- [ ] The amber banner "Synthetic data · hypothetical prices · simulation" is visible.
- [ ] Screen 3 starts on "today" (reload the page if you have clicked through it).
- [ ] Microphone level checked; notifications off.

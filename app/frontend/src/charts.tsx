import { useLayoutEffect, useRef, useState } from "react";
import { eur, int, monthName, shortDate } from "./ui";

function useWidth() {
  const ref = useRef<HTMLDivElement>(null);
  const [w, setW] = useState(640);
  useLayoutEffect(() => {
    if (!ref.current) return;
    setW(ref.current.clientWidth || 640);
    const ro = new ResizeObserver(([e]) => setW(Math.max(e.contentRect.width, 240)));
    ro.observe(ref.current);
    return () => ro.disconnect();
  }, []);
  return [ref, w] as const;
}

const niceMax = (v: number) => {
  const p = 10 ** Math.floor(Math.log10(v || 1));
  return ([1, 1.5, 2, 3, 4, 5, 6, 8, 10].find((s) => v / p <= s) ?? 10) * p;
};

type Tip = { x: number; y: number; text: string } | null;
const TipBox = ({ tip, w }: { tip: Tip; w: number }) => tip && <div className="chart-tip" style={{ left: Math.min(Math.max(tip.x, 90), w - 90), top: tip.y }}>{tip.text}</div>;

/** Every pickup in a year: how full the container was when the truck came. */
export function FillScatter({ rows }: { rows: { date: string; fill_pct: number | null; kg: number | null }[] }) {
  const [ref, w] = useWidth();
  const [tip, setTip] = useState<Tip>(null);
  const h = 220, l = 44, r = 10, t = 12, b = 26;
  const pts = rows.filter((p) => p.fill_pct != null).map((p) => ({ ...p, time: new Date(p.date).getTime() }));
  const min = Math.min(...pts.map((p) => p.time)), max = Math.max(...pts.map((p) => p.time));
  const x = (v: number) => l + (w - l - r) * ((v - min) / (max - min || 1));
  const y = (v: number) => t + (h - t - b) * (1 - v / 100);
  const months = ["2025-10", "2026-01", "2026-04", "2026-07"];
  return (
    <div ref={ref} className="chart" onMouseLeave={() => setTip(null)}>
      <svg width={w} height={h} role="img" aria-label="How full the container was at each pickup over the year">
        <rect x={l} y={y(60)} width={w - l - r} height={y(0) - y(60)} className="zone-low" />
        {[0, 60, 100].map((v) => (
          <g key={v}>
            <line x1={l} x2={w - r} y1={y(v)} y2={y(v)} className={v === 0 ? "axis" : v === 60 ? "ref-line" : "grid"} />
            <text x={l - 8} y={y(v) + 4} textAnchor="end" className="tick">{v} %</text>
          </g>
        ))}
        {months.map((m) => <text key={m} x={x(new Date(`${m}-01`).getTime())} y={h - 6} className="tick">{monthName(m)}</text>)}
        {pts.map((p, i) => (
          <circle key={i} cx={x(p.time)} cy={y(p.fill_pct!)} r={5} className={p.fill_pct! < 60 ? "dot-low" : "dot-ok"}
            onMouseEnter={() => setTip({ x: x(p.time), y: y(p.fill_pct!), text: `${p.date}: ${p.fill_pct!.toFixed(0)} % full${p.kg ? `, ${int(p.kg)} kg` : ""}` })} />
        ))}
      </svg>
      <TipBox tip={tip} w={w} />
      <div className="legend"><span><i className="sw sw-low" />Under 60 % full</span><span><i className="sw sw-ok" />60 % or more</span></div>
    </div>
  );
}

/** What it takes to name a price per tonne: guessing, then full loads, then less risk. */
export function PriceWaterfall({ blind, fullLoads, withData, labels }: { blind: number; fullLoads: number; withData: number; labels: [string, string, string, string] }) {
  const [ref, w] = useWidth();
  const h = 350, t = 34, b = 54, gap = Math.min(28, w * 0.05);
  const n = 4, bw = (w - gap * (n - 1)) / n;
  const max = niceMax(blind);
  const y = (v: number) => t + (h - t - b) * (1 - v / max);
  const bars = [
    { from: 0, to: blind, cls: "bar-orange", text: eur(blind) },
    { from: fullLoads, to: blind, cls: "bar-mint", text: `−${eur(blind - fullLoads)}` },
    { from: withData, to: fullLoads, cls: "bar-mint", text: `−${eur(fullLoads - withData)}` },
    { from: 0, to: withData, cls: "bar-green", text: eur(withData) },
  ];
  return (
    <div ref={ref} className="chart">
      <svg width={w} height={h} role="img" aria-label={`Price per tonne falls from ${eur(blind)} guessing to ${eur(withData)} with the weights`}>
        <line x1={0} x2={w} y1={y(0)} y2={y(0)} className="axis" />
        {bars.map((d, i) => {
          const x = i * (bw + gap);
          const top = y(d.to), height = Math.max(y(d.from) - top, 2);
          return (
            <g key={i}>
              {i < 3 && <line x1={x + bw} x2={x + bw + gap} y1={y(i === 0 ? blind : i === 1 ? fullLoads : withData)} y2={y(i === 0 ? blind : i === 1 ? fullLoads : withData)} className="connector" />}
              <rect x={x} y={top} width={bw} height={height} rx={6} className={d.cls} />
              <text x={x + bw / 2} y={top - 10} textAnchor="middle" className={i === 0 || i === 3 ? "wf-total" : "wf-step"}>{d.text}</text>
              <foreignObject x={x} y={h - b + 8} width={bw} height={b - 8}><div className="wf-label">{labels[i]}</div></foreignObject>
            </g>
          );
        })}
      </svg>
    </div>
  );
}

/** The weight nobody could see: the last weeks of readings, then where it is heading. */
export function WeightTrend({ trend, target, kgPerDay, asOf }: { trend: { date: string; kg: number | null }[]; target: number; kgPerDay: number; asOf: string }) {
  const [ref, w] = useWidth();
  const [tip, setTip] = useState<Tip>(null);
  const h = 214, l = 46, r = 12, t = 16, b = 24;
  const pts = trend.filter((p) => p.kg != null).map((p) => ({ time: new Date(p.date).getTime(), kg: p.kg as number }));
  const last = pts[pts.length - 1];
  const days = Math.max(0, Math.min(21, (target - last.kg) / (kgPerDay || 1)));
  const end = last.time + days * 864e5;
  const min = pts[0].time, max = Math.max(end, last.time + 864e5);
  const top = niceMax(Math.max(target * 1.05, ...pts.map((p) => p.kg)));
  const x = (v: number) => l + (w - l - r) * ((v - min) / (max - min));
  const y = (v: number) => t + (h - t - b) * (1 - v / top);
  const line = pts.map((p, i) => `${i ? "L" : "M"}${x(p.time).toFixed(1)},${y(p.kg).toFixed(1)}`).join(" ");
  const area = `${line} L${x(last.time).toFixed(1)},${y(0)} L${x(pts[0].time).toFixed(1)},${y(0)} Z`;
  return (
    <div ref={ref} className="chart" onMouseLeave={() => setTip(null)}
      onMouseMove={(e) => { const box = e.currentTarget.getBoundingClientRect(); const px = e.clientX - box.left; const near = pts.reduce((a, p) => Math.abs(x(p.time) - px) < Math.abs(x(a.time) - px) ? p : a, pts[0]); setTip({ x: x(near.time), y: y(near.kg), text: `${shortDate(near.time)}: ${int(near.kg)} kg` }); }}>
      <svg width={w} height={h} role="img" aria-label={`Weight over recent weeks, ${int(last.kg)} kg now, target ${int(target)} kg`}>
        {[0, 0.5, 1].map((f) => <g key={f}><line x1={l} x2={w - r} y1={y(top * f)} y2={y(top * f)} className={f === 0 ? "axis" : "grid"} /><text x={l - 8} y={y(top * f) + 4} textAnchor="end" className="tick">{top * f >= 1000 ? `${(top * f / 1000).toFixed(1)} t` : `${int(top * f)} kg`}</text></g>)}
        <line x1={l} x2={w - r} y1={y(target)} y2={y(target)} className="target-line" />
        <text x={l + 4} y={y(target) - 6} className="tick tick-strong">Target {int(target)} kg</text>
        <path d={area} className="band" />
        <path d={line} className="line-green" />
        {days > 0 && <line x1={x(last.time)} y1={y(last.kg)} x2={x(end)} y2={y(target)} className="projection" />}
        {days > 0 && <circle cx={x(end)} cy={y(target)} r={5} className="proj-dot" />}
        <circle cx={x(last.time)} cy={y(last.kg)} r={6} className="range-dot" />
        <text x={l} y={h - 6} className="tick">{shortDate(min)}</text>
        <text x={x(last.time)} y={h - 6} textAnchor="middle" className="tick tick-strong">Now</text>
        {days > 0 && <text x={x(end)} y={t + (y(target) - t) - 22 < 2 ? y(target) + 18 : y(target) - 22} textAnchor="end" className="tick">Full ~{shortDate(end)}</text>}
      </svg>
      <TipBox tip={tip} w={w} />
    </div>
  );
}

/** How sure a bidder can be of the yearly tonnes: two ranges for the same quantity. */
export function TonnesRange({ blind, data, blindLabel = "Guessing from similar sites", dataLabel = "With the weights" }: { blind: any; data?: any; blindLabel?: string; dataLabel?: string }) {
  const [ref, w] = useWidth();
  const narrow = w < 500;
  const rows = [{ name: blindLabel, v: blind, c: "bar-orange" }, ...(data ? [{ name: dataLabel, v: data, c: "bar-green" }] : [])];
  const l = narrow ? 2 : 190, r = 18, rowH = narrow ? 74 : 56;
  const h = rows.length * rowH + 26;
  const max = niceMax(Math.max(blind.high, data?.high ?? 0));
  const x = (v: number) => l + (w - l - r) * (v / max);
  return (
    <div ref={ref} className="chart">
      <svg width={w} height={h} role="img" aria-label="Range of yearly tonnes, with and without the weight profile">
        {[0, 0.5, 1].map((f) => <text key={f} x={x(max * f)} y={h - 4} textAnchor={f === 0 ? "start" : f === 1 ? "end" : "middle"} className="tick">{int(max * f)} t</text>)}
        <line x1={l} x2={w - r} y1={h - 20} y2={h - 20} className="axis" />
        {rows.map((row, i) => {
          const c = i * rowH + (narrow ? 44 : 22);
          return (
            <g key={row.name}>
              <text x={0} y={narrow ? c - 24 : c + 5} className="tick-strong">{row.name}</text>
              <rect x={x(row.v.low)} y={c - 8} width={x(row.v.high) - x(row.v.low)} height={16} rx={8} className={row.c} />
              <circle cx={x(row.v.estimate)} cy={c} r={6} className="range-dot" />
              <text x={x(row.v.low)} y={c + 25} textAnchor="middle" className="tick">{int(row.v.low)}</text>
              <text x={x(row.v.high)} y={c + 25} textAnchor="middle" className="tick">{int(row.v.high)}</text>
            </g>
          );
        })}
      </svg>
    </div>
  );
}

/** Next 12 months of tonnes with the backtest's uncertainty as a band. */
export function ForecastChart({ rows }: { rows: any[] }) {
  const [ref, w] = useWidth();
  const [i, setI] = useState<number | null>(null);
  const h = 210, l = 44, r = 10, t = 10, b = 26;
  const max = niceMax(Math.max(...rows.map((p) => p.high_kg)) / 1000);
  const x = (k: number) => l + (w - l - r) * (k / (rows.length - 1));
  const y = (v: number) => t + (h - t - b) * (1 - v / 1000 / max);
  const line = rows.map((p, k) => `${k ? "L" : "M"}${x(k)},${y(p.p50_kg)}`).join(" ");
  const band = rows.map((p, k) => `${k ? "L" : "M"}${x(k)},${y(p.high_kg)}`).join(" ") + " " + [...rows].reverse().map((p, k) => `L${x(rows.length - 1 - k)},${y(p.low_kg)}`).join(" ") + " Z";
  const cur = i == null ? null : rows[i];
  return (
    <div ref={ref} className="chart" onMouseLeave={() => setI(null)}
      onMouseMove={(e) => { const box = e.currentTarget.getBoundingClientRect(); setI(Math.min(rows.length - 1, Math.max(0, Math.round(((e.clientX - box.left - l) / (w - l - r)) * (rows.length - 1))))); }}>
      <svg width={w} height={h} role="img" aria-label="Forecast of tonnes per month for the next 12 months">
        {[0, 0.5, 1].map((f) => (
          <g key={f}>
            <line x1={l} x2={w - r} y1={t + (h - t - b) * (1 - f)} y2={t + (h - t - b) * (1 - f)} className={f === 0 ? "axis" : "grid"} />
            <text x={l - 8} y={t + (h - t - b) * (1 - f) + 4} textAnchor="end" className="tick">{(max * f).toFixed(max < 10 ? 1 : 0)} t</text>
          </g>
        ))}
        <path d={band} className="band" />
        <path d={line} className="line-green" />
        {rows.map((p, k) => (w > 520 || k % 2 === 0) && <text key={p.month} x={x(k)} y={h - 6} textAnchor={k === 0 ? "start" : k === rows.length - 1 ? "end" : "middle"} className="tick">{monthName(p.month)}</text>)}
        {cur && <><line x1={x(i!)} x2={x(i!)} y1={t} y2={h - b} className="crosshair" /><circle cx={x(i!)} cy={y(cur.p50_kg)} r={5} className="range-dot" /></>}
      </svg>
      {cur && <TipBox w={w} tip={{ x: x(i!), y: y(cur.high_kg), text: `${monthName(cur.month, true)}: ${(cur.p50_kg / 1000).toFixed(1)} t (${(cur.low_kg / 1000).toFixed(1)}–${(cur.high_kg / 1000).toFixed(1)})` }} />}
    </div>
  );
}

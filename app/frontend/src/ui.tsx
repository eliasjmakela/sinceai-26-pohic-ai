import { ReactNode, createContext, useCallback, useContext, useEffect, useRef, useState } from "react";
import { Link, NavLink } from "react-router-dom";

const nf0 = new Intl.NumberFormat("en-GB", { maximumFractionDigits: 0 });
const nf2 = new Intl.NumberFormat("en-GB", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const sign = (v: number) => (v < 0 ? "−" : "");

export const eur = (v?: number | null) => (v == null ? "–" : `${sign(v)}€${nf0.format(Math.abs(v))}`);
export const eur2 = (v?: number | null) => (v == null ? "–" : `${sign(v)}€${nf2.format(Math.abs(v))}`);
export const int = (v?: number | null) => (v == null ? "–" : nf0.format(v));
export const kg = (v?: number | null) => (v == null ? "–" : `${nf0.format(v)} kg`);
export const t1 = (v?: number | null) => (v == null ? "–" : `${v.toFixed(1)} t`);
export const pct = (v?: number | null, d = 0) => (v == null ? "–" : `${sign(v)}${Math.abs(v).toFixed(d)} %`);
export const date = (s?: string | null) => (s ? new Date(s).toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "numeric" }) : "–");
export const shortDate = (s: string | number | Date) => new Date(s).toLocaleDateString("en-GB", { day: "numeric", month: "short" });
export const monthName = (s: string, withYear = false) => new Date(`${s}-01`).toLocaleDateString("en-GB", withYear ? { month: "long", year: "numeric" } : { month: "short" }).slice(0, withYear ? undefined : 3);
export const cls = (...xs: (string | false | null | undefined)[]) => xs.filter(Boolean).join(" ");

/** A figure's evidence, shown only where it isn't simply read from the records. */
export function Tag({ kind }: { kind: "estimate" | "simulated" | "assumption" }) {
  const title = { estimate: "Calculated by OpenWeight", simulated: "From the market simulation on synthetic data", assumption: "A choice made for this demo" }[kind];
  return <span className="tag" title={title}>{kind}</span>;
}

export function Kpi({ label, value, sub, tag, tone }: { label: string; value: ReactNode; sub?: ReactNode; tag?: "estimate" | "simulated" | "assumption"; tone?: "good" | "ask" }) {
  return (
    <div className="kpi">
      <div className="kpi-label">{label}{tag && <> <Tag kind={tag} /></>}</div>
      <div className={cls("kpi-value", tone && `tone-${tone}`)}>{value}</div>
      {sub && <div className="kpi-sub">{sub}</div>}
    </div>
  );
}

export function Panel({ title, meta, children, className, flush }: { title?: ReactNode; meta?: ReactNode; children: ReactNode; className?: string; flush?: boolean }) {
  return (
    <section className={cls("panel", className)}>
      {(title || meta) && <header className="panel-head"><h2>{title}</h2>{meta && <div className="panel-meta">{meta}</div>}</header>}
      <div className={cls("panel-body", flush && "panel-flush")}>{children}</div>
    </section>
  );
}

export function Tabs({ value, onChange, items }: { value: string; onChange: (v: string) => void; items: { id: string; label: string }[] }) {
  return (
    <div className="tabs" role="tablist">
      {items.map((i) => <button key={i.id} role="tab" aria-selected={value === i.id} className={cls("tab", value === i.id && "tab-on")} onClick={() => onChange(i.id)}>{i.label}</button>)}
    </div>
  );
}

export function Loading({ error }: { error?: Error | null }) {
  return error ? <div className="notice notice-warn">This view couldn't load: {error.message}</div> : <div className="loading"><span className="spinner" aria-hidden />Loading</div>;
}

/** A side sheet: details on demand, without leaving the view you are in. */
export function Drawer({ title, onClose, children }: { title: ReactNode; onClose: () => void; children: ReactNode }) {
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => { if (e.key === "Escape") onClose(); };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);
  return (
    <div className="drawer-wrap" role="dialog" aria-modal="true">
      <button className="drawer-scrim" aria-label="Close" onClick={onClose} />
      <div className="drawer">
        <header className="drawer-head"><h2>{title}</h2><button className="icon-btn" aria-label="Close" onClick={onClose}><Icon name="close" /></button></header>
        <div className="drawer-body">{children}</div>
      </div>
    </div>
  );
}

const ICONS: Record<string, ReactNode> = {
  today: <><path d="M4 13a8 8 0 0 1 16 0" /><path d="M12 13l4-4" /><path d="M4 17h16" /></>,
  contract: <><path d="M7 3h8l4 4v14H7z" /><path d="M15 3v4h4" /><path d="M10 14l2 2 4-4" /></>,
  tender: <><path d="M4 7h10" /><path d="M4 12h16" /><path d="M4 17h7" /><circle cx="18" cy="7" r="2" /><circle cx="15" cy="17" r="2" /></>,
  truck: <><path d="M3 7h11v9H3z" /><path d="M14 10h4l3 3v3h-7" /><circle cx="7.5" cy="17.5" r="1.8" /><circle cx="17.5" cy="17.5" r="1.8" /></>,
  scale: <><path d="M12 4v16" /><path d="M7 20h10" /><path d="M5 7h14" /><path d="M5 7l-2.5 6h5z" /><path d="M19 7l-2.5 6h5z" /></>,
  close: <><path d="M6 6l12 12" /><path d="M18 6L6 18" /></>,
  check: <path d="M5 12.5l4.5 4.5L19 7.5" />,
  chevron: <path d="M9 6l6 6-6 6" />,
  spark: <path d="M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8zM19 15l.8 2.2L22 18l-2.2.8L19 21l-.8-2.2L16 18l2.2-.8z" />,
  swap: <><path d="M4 8h13l-3-3" /><path d="M20 16H7l3 3" /></>,
};
export function Icon({ name }: { name: string }) {
  return <svg className="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round" strokeLinejoin="round" aria-hidden>{ICONS[name]}</svg>;
}

/** A compactor seen from the side. The waste is pressed towards the back, so the load grows from the machine end. */
export function Compactor({ share, size = "large" }: { share: number; size?: "large" | "small" }) {
  const fill = Math.max(2, Math.min(100, share));
  return (
    <svg className={`compactor compactor-${size}`} viewBox="0 0 200 84" role="img" aria-label={`${share.toFixed(0)} % of its target weight`}>
      <rect x="4" y="76" width="192" height="4" rx="2" className="cp-ground" />
      <rect x="10" y="20" width="52" height="54" rx="7" className="cp-machine" />
      <rect x="20" y="30" width="20" height="9" rx="2.5" className="cp-panel" />
      <circle cx="50" cy="34.5" r="3.5" className="cp-light" />
      <rect x="66" y="12" width="126" height="62" rx="8" className="cp-box" />
      <rect x="70" y="16" width={118 * (fill / 100)} height="54" rx="5" className={share >= 100 ? "cp-load cp-load-full" : "cp-load"} />
      {[97, 129, 161].map((x) => <line key={x} x1={x} y1="12" x2={x} y2="74" className="cp-rib" />)}
    </svg>
  );
}

export function Logo() {
  return (
    <svg className="logo" viewBox="0 0 32 32" aria-hidden>
      <rect width="32" height="32" rx="9" className="logo-bg" />
      <path d="M8 22.5h16M16 22.5V9.5M10 12.5l6-3 6 3" className="logo-mark" />
    </svg>
  );
}

// ---- toast: every action happens at once and can be undone, instead of asking first
type ToastState = { text: string; undo?: () => void } | null;
const ToastCtx = createContext<(text: string, undo?: () => void) => void>(() => {});
export const useToast = () => useContext(ToastCtx);

export type NavItem = { to: string; label: string; icon: string; end?: boolean; badge?: number | string | null };

export function Shell({ who, sub, portal, nav, liveLabel, children }: { who: string; sub: string; portal: string; nav: NavItem[]; liveLabel: string; children: ReactNode }) {
  const [toast, setToast] = useState<ToastState>(null);
  const timer = useRef<number | undefined>(undefined);
  const show = useCallback((text: string, undo?: () => void) => {
    setToast({ text, undo });
    window.clearTimeout(timer.current);
    timer.current = window.setTimeout(() => setToast(null), 6000);
  }, []);
  return (
    <ToastCtx.Provider value={show}>
      <div className="app">
        <aside className="rail">
          <Link to="/" className="brand"><Logo /><span>OpenWeight</span></Link>
          <div className="rail-portal">{portal}</div>
          <nav className="rail-nav" aria-label={portal}>
            {nav.map((n) => (
              <NavLink key={n.to} to={n.to} end={n.end} className={({ isActive }) => cls("rail-link", isActive && "rail-on")}>
                <Icon name={n.icon} /><span className="rail-label">{n.label}</span>{n.badge ? <span className="rail-badge">{n.badge}</span> : null}
              </NavLink>
            ))}
            <Link to="/" className="rail-link rail-signout-m"><Icon name="swap" /><span className="rail-label">Sign out</span></Link>
          </nav>
          <div className="rail-foot">
            <div className="live"><span className="live-dot" aria-hidden />{liveLabel}</div>
            <div className="rail-who"><strong>{who}</strong><span>{sub}</span><Link to="/" className="rail-signout">Sign out</Link></div>
            <p className="rail-legal">Synthetic data. Fictional companies and prices.</p>
          </div>
        </aside>
        <div className="work">{children}</div>
        {toast && (
          <div className="toast" role="status">
            <Icon name="check" /><span>{toast.text}</span>
            {toast.undo && <button onClick={() => { toast.undo!(); setToast(null); }}>Undo</button>}
          </div>
        )}
      </div>
    </ToastCtx.Provider>
  );
}

export function Bar({ title, sub, children }: { title: ReactNode; sub?: ReactNode; children?: ReactNode }) {
  return (
    <header className="bar">
      <div className="bar-main"><h1>{title}</h1>{sub && <p>{sub}</p>}</div>
      {children && <div className="bar-side">{children}</div>}
    </header>
  );
}

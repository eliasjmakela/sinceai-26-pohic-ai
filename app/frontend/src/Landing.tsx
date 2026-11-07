import { useState } from "react";
import { Link } from "react-router-dom";
import { post, useData } from "./api";
import { Icon, Logo } from "./ui";

/** Sign-in, with the core value beside it: why the weight changes the market, and what each side gets. */
export function Landing() {
  const [done, setDone] = useState(false);
  const { data: a } = useData("/api/about");
  return (
    <div className="signin signin-split">
      <section className="value" aria-label="What OpenWeight does">
        <div className="brand brand-light"><Logo />OpenWeight</div>
        <h1>Pay for tonnes, not trips.</h1>
        <p className="value-lead">
          Customers pay per truck visit, however full the compactor is. Only the waste company that already serves a site
          knows how much it produces, so nobody else can safely price per tonne. Now the compactor weighs itself, and every
          bidder sees the same weights.
        </p>
        {a && (
          <dl className="value-facts">
            <div><dt>A bidder's estimate of a site's tonnes</dt><dd>±{a.sigma_blind_pct.toFixed(0)} % → ±{a.sigma_data_pct.toFixed(0)} %</dd></div>
            <div><dt>Customers a challenger can win</dt><dd>{a.contestable_before} → {a.contestable_after} of {a.accounts}</dd></div>
            <div><dt>Customer's price per tonne</dt><dd>about −{a.region_saving_pct.toFixed(0)} %</dd></div>
          </dl>
        )}
        {a && <p className="value-small">Simulated for one region on the challenge's synthetic data, with OpenWeight's fee included. Not a guaranteed saving.</p>}
        <p className="value-note">
          Europress funds the weighing in every new compactor and sells the data as a service. It never drives a truck and
          never sits in the tender: offers go from the waste company to the customer, as today. The bill stays on the
          certified weighbridge.
        </p>
      </section>
      <main className="signin-card">
        <h2 className="signin-title">Sign in</h2>
        <p className="signin-lead">Who are you signing in as?</p>
        <div className="signin-roles">
          <Link to="/customer" className="role">
            <span className="role-icon"><Icon name="today" /></span>
            <span className="role-text"><strong>Customer · free</strong><span>See each pickup's cost per tonne, whether the contract is kept, and compare offers per tonne</span></span>
            <Icon name="chevron" />
          </Link>
          <Link to="/waste-company" className="role">
            <span className="role-icon"><Icon name="truck" /></span>
            <span className="role-text"><strong>Waste company · €{a?.fee_eur_per_device_month ?? 30} per compactor a month</strong><span>Price per tonne without guessing, and send trucks only to full loads</span></span>
            <Icon name="chevron" />
          </Link>
        </div>
        <p className="signin-note">Demo: no password needed. Synthetic data, fictional companies and prices. <button className="link-btn link-quiet" onClick={async () => { await post("/api/demo/reset"); setDone(true); }}>{done ? "Demo reset" : "Reset the demo"}</button></p>
      </main>
    </div>
  );
}

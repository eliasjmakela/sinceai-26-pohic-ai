import { useState } from "react";
import { Link } from "react-router-dom";
import { post, useData } from "./api";
import { Icon, Logo } from "./ui";

/** Sign-in: choose the portal. */
export function Landing() {
  const [done, setDone] = useState(false);
  const { data: a } = useData("/api/about");
  return (
    <div className="signin">
      <main className="signin-card">
        <div className="brand signin-brand"><Logo />OpenWeight</div>
        <h1 className="signin-title">Sign in</h1>
        <p className="signin-lead">Who are you signing in as?</p>
        <div className="signin-roles">
          <Link to="/customer" className="role">
            <span className="role-icon"><Icon name="today" /></span>
            <span className="role-text"><strong>Customer · free</strong><span>See each pickup's cost per tonne, whether the contract is kept, and compare offers per tonne</span></span>
            <Icon name="chevron" />
          </Link>
          <Link to="/waste-company" className="role">
            <span className="role-icon"><Icon name="truck" /></span>
            <span className="role-text"><strong>Waste company · €{a?.fee_eur_per_device_month ?? 30} per compactor a month</strong><span>Price tenders per tonne without guessing, and check every ticket against the compactor</span></span>
            <Icon name="chevron" />
          </Link>
        </div>
        <p className="signin-note">Demo: no password needed. Synthetic data, fictional companies and prices. <button className="link-btn link-quiet" onClick={async () => { await post("/api/demo/reset"); setDone(true); }}>{done ? "Demo reset" : "Reset the demo"}</button></p>
      </main>
    </div>
  );
}

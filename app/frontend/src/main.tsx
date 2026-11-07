import { createRoot } from "react-dom/client";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import "@fontsource-variable/manrope";
import "./styles.css";
import { Landing } from "./Landing";
import { CustomerPortal } from "./customer";
import { HaulerPortal } from "./hauler";

createRoot(document.getElementById("root")!).render(
  <BrowserRouter>
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/customer/*" element={<CustomerPortal />} />
      <Route path="/waste-company/*" element={<HaulerPortal />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  </BrowserRouter>,
);

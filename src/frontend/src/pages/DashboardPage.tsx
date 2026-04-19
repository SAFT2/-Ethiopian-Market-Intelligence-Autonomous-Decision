import { useEffect, useMemo, useState } from "react";

import { AIDecisionsPanel } from "../components/AIDecisionsPanel";
import { MarketTrendsChart } from "../components/MarketTrendsChart";
import { WhatIfSimulator } from "../components/WhatIfSimulator";
import { evaluateIntelligence, fetchMarketData, login, setAuthToken } from "../services/api";
import type { IntelligenceDecision, MarketPoint } from "../types";

export function DashboardPage() {
  const [email, setEmail] = useState("analyst@ethiopia-market.ai");
  const [password, setPassword] = useState("StrongPass123");
  const [authed, setAuthed] = useState(false);
  const [points, setPoints] = useState<MarketPoint[]>([]);
  const [decision, setDecision] = useState<IntelligenceDecision | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const token = localStorage.getItem("auth_token");
    if (token) {
      setAuthToken(token);
      setAuthed(true);
    }
  }, []);

  useEffect(() => {
    if (!authed) {
      return;
    }
    fetchMarketData()
      .then(setPoints)
      .catch((err) => setError(err.message));
  }, [authed]);

  async function handleLogin() {
    setError(null);
    try {
      const result = await login(email, password);
      localStorage.setItem("auth_token", result.access_token);
      setAuthToken(result.access_token);
      setAuthed(true);
    } catch (err: any) {
      setError(err?.response?.data?.error?.message ?? err?.message ?? "Login failed");
    }
  }

  const latest = useMemo(() => points[0] ?? null, [points]);
  const historyPrices = useMemo(
    () => points.filter((p) => p.price_value !== null).slice(0, 14).map((p) => Number(p.price_value)),
    [points],
  );

  async function runDecision() {
    if (!latest || historyPrices.length < 3) {
      setError("Need at least 3 market points to evaluate decisions.");
      return;
    }

    setError(null);
    setLoading(true);
    try {
      const avgMarketPrice =
        historyPrices.reduce((sum, val) => sum + val, 0) / Math.max(historyPrices.length, 1);

      const result = await evaluateIntelligence({
        product_id: latest.product_id,
        location: latest.location ?? "Addis Ababa",
        current_price: Number(latest.price_value ?? avgMarketPrice),
        avg_market_price: avgMarketPrice,
        inventory_days_cover: 18,
        weekly_sales_units: 140,
        history_prices: historyPrices,
      });
      setDecision(result);
    } catch (err: any) {
      setError(err?.message ?? "Failed to evaluate intelligence");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="layout">
      <header>
        <h1>Ethiopian Market Intelligence Dashboard</h1>
        <p>Unified view of market trends, AI decisions, and simulation.</p>
      </header>

      {!authed && (
        <section className="card auth-card">
          <h2>Sign In</h2>
          <p>Authenticate to access protected market intelligence endpoints.</p>
          <label>
            Email
            <input value={email} onChange={(e) => setEmail(e.target.value)} type="email" />
          </label>
          <label>
            Password
            <input value={password} onChange={(e) => setPassword(e.target.value)} type="password" />
          </label>
          <button className="action" onClick={handleLogin}>
            Sign In
          </button>
        </section>
      )}

      {error && <p className="error">{error}</p>}

      {authed && <div className="grid">
        <MarketTrendsChart points={points} />
        <AIDecisionsPanel decision={decision} />
        <WhatIfSimulator
          currentPrice={Number(latest?.price_value ?? 0)}
          marketPrice={
            historyPrices.length
              ? historyPrices.reduce((sum, val) => sum + val, 0) / historyPrices.length
              : 0
          }
          weeklySalesUnits={140}
        />
      </div>}

      {authed && <button className="action" onClick={runDecision} disabled={loading}>
        {loading ? "Evaluating..." : "Generate AI Decision"}
      </button>}
    </main>
  );
}

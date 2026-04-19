import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useEffect, useMemo, useState } from "react";
import { AIDecisionsPanel } from "../components/AIDecisionsPanel";
import { MarketTrendsChart } from "../components/MarketTrendsChart";
import { WhatIfSimulator } from "../components/WhatIfSimulator";
import { evaluateIntelligence, fetchMarketData, login, setAuthToken } from "../services/api";
export function DashboardPage() {
    const [email, setEmail] = useState("analyst@ethiopia-market.ai");
    const [password, setPassword] = useState("StrongPass123");
    const [authed, setAuthed] = useState(false);
    const [points, setPoints] = useState([]);
    const [decision, setDecision] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
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
        }
        catch (err) {
            setError(err?.response?.data?.error?.message ?? err?.message ?? "Login failed");
        }
    }
    const latest = useMemo(() => points[0] ?? null, [points]);
    const historyPrices = useMemo(() => points.filter((p) => p.price_value !== null).slice(0, 14).map((p) => Number(p.price_value)), [points]);
    async function runDecision() {
        if (!latest || historyPrices.length < 3) {
            setError("Need at least 3 market points to evaluate decisions.");
            return;
        }
        setError(null);
        setLoading(true);
        try {
            const avgMarketPrice = historyPrices.reduce((sum, val) => sum + val, 0) / Math.max(historyPrices.length, 1);
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
        }
        catch (err) {
            setError(err?.message ?? "Failed to evaluate intelligence");
        }
        finally {
            setLoading(false);
        }
    }
    return (_jsxs("main", { className: "layout", children: [_jsxs("header", { children: [_jsx("h1", { children: "Ethiopian Market Intelligence Dashboard" }), _jsx("p", { children: "Unified view of market trends, AI decisions, and simulation." })] }), !authed && (_jsxs("section", { className: "card auth-card", children: [_jsx("h2", { children: "Sign In" }), _jsx("p", { children: "Authenticate to access protected market intelligence endpoints." }), _jsxs("label", { children: ["Email", _jsx("input", { value: email, onChange: (e) => setEmail(e.target.value), type: "email" })] }), _jsxs("label", { children: ["Password", _jsx("input", { value: password, onChange: (e) => setPassword(e.target.value), type: "password" })] }), _jsx("button", { className: "action", onClick: handleLogin, children: "Sign In" })] })), error && _jsx("p", { className: "error", children: error }), authed && _jsxs("div", { className: "grid", children: [_jsx(MarketTrendsChart, { points: points }), _jsx(AIDecisionsPanel, { decision: decision }), _jsx(WhatIfSimulator, { currentPrice: Number(latest?.price_value ?? 0), marketPrice: historyPrices.length
                            ? historyPrices.reduce((sum, val) => sum + val, 0) / historyPrices.length
                            : 0, weeklySalesUnits: 140 })] }), authed && _jsx("button", { className: "action", onClick: runDecision, disabled: loading, children: loading ? "Evaluating..." : "Generate AI Decision" })] }));
}

import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis, } from "recharts";
export function MarketTrendsChart({ points }) {
    const data = points
        .filter((p) => p.price_value !== null)
        .map((p) => ({
        time: new Date(p.observed_at).toLocaleDateString(),
        price: p.price_value,
    }))
        .reverse();
    return (_jsxs("section", { className: "card", children: [_jsx("h2", { children: "Market Trends" }), _jsx("div", { style: { height: 300 }, children: _jsx(ResponsiveContainer, { width: "100%", height: "100%", children: _jsxs(LineChart, { data: data, children: [_jsx(CartesianGrid, { strokeDasharray: "3 3" }), _jsx(XAxis, { dataKey: "time" }), _jsx(YAxis, {}), _jsx(Tooltip, {}), _jsx(Line, { type: "monotone", dataKey: "price", stroke: "#1770a6", strokeWidth: 3, dot: false })] }) }) })] }));
}

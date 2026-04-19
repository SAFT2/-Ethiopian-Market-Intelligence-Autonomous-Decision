import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useMemo, useState } from "react";
export function WhatIfSimulator({ currentPrice, marketPrice, weeklySalesUnits }) {
    const [priceDeltaPct, setPriceDeltaPct] = useState(0);
    const simulation = useMemo(() => {
        const newPrice = currentPrice * (1 + priceDeltaPct / 100);
        const elasticity = -0.6;
        const demandFactor = Math.pow(newPrice / Math.max(currentPrice, 1), elasticity);
        const projectedWeeklySales = weeklySalesUnits * demandFactor;
        const projectedRevenue = projectedWeeklySales * newPrice;
        const marketGap = ((marketPrice - newPrice) / marketPrice) * 100;
        return {
            newPrice,
            projectedWeeklySales,
            projectedRevenue,
            marketGap,
        };
    }, [currentPrice, marketPrice, weeklySalesUnits, priceDeltaPct]);
    return (_jsxs("section", { className: "card", children: [_jsx("h2", { children: "What-if Simulator" }), _jsxs("label", { children: ["Price change (%): ", priceDeltaPct.toFixed(1), _jsx("input", { type: "range", min: -15, max: 20, step: 0.5, value: priceDeltaPct, onChange: (e) => setPriceDeltaPct(Number(e.target.value)) })] }), _jsxs("p", { children: ["Simulated price: ", simulation.newPrice.toFixed(2), " ETB"] }), _jsxs("p", { children: ["Projected weekly sales: ", simulation.projectedWeeklySales.toFixed(1), " units"] }), _jsxs("p", { children: ["Projected weekly revenue: ", simulation.projectedRevenue.toFixed(2), " ETB"] }), _jsxs("p", { children: ["Price vs market gap: ", simulation.marketGap.toFixed(1), "%"] })] }));
}

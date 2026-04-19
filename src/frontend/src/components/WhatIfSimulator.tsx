import { useMemo, useState } from "react";

type Props = {
  currentPrice: number;
  marketPrice: number;
  weeklySalesUnits: number;
};

export function WhatIfSimulator({ currentPrice, marketPrice, weeklySalesUnits }: Props) {
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

  return (
    <section className="card">
      <h2>What-if Simulator</h2>
      <label>
        Price change (%): {priceDeltaPct.toFixed(1)}
        <input
          type="range"
          min={-15}
          max={20}
          step={0.5}
          value={priceDeltaPct}
          onChange={(e) => setPriceDeltaPct(Number(e.target.value))}
        />
      </label>
      <p>Simulated price: {simulation.newPrice.toFixed(2)} ETB</p>
      <p>Projected weekly sales: {simulation.projectedWeeklySales.toFixed(1)} units</p>
      <p>Projected weekly revenue: {simulation.projectedRevenue.toFixed(2)} ETB</p>
      <p>Price vs market gap: {simulation.marketGap.toFixed(1)}%</p>
    </section>
  );
}

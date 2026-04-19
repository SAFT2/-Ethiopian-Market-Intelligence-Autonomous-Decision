import type { IntelligenceDecision } from "../types";

type Props = {
  decision: IntelligenceDecision | null;
};

export function AIDecisionsPanel({ decision }: Props) {
  return (
    <section className="card">
      <h2>AI Decisions Panel</h2>
      {!decision && <p>No decision generated yet.</p>}
      {decision && (
        <>
          <p><strong>Pricing:</strong> {decision.pricing_recommendation}</p>
          <p><strong>Stock:</strong> {decision.stock_decision}</p>
          <p><strong>Risk:</strong> {decision.risk_alert}</p>
          <p><strong>Composite Score:</strong> {decision.score.toFixed(3)}</p>
          <p><strong>Demand Forecast:</strong> {decision.demand_forecast.toFixed(2)}</p>
          <p><strong>Product Score:</strong> {decision.product_score.toFixed(2)}</p>
          <p><strong>Anomaly Probability:</strong> {decision.anomaly_probability.toFixed(2)}</p>
          <h3>Why this decision?</h3>
          <ul>
            {decision.explanation.map((line) => (
              <li key={line}>{line}</li>
            ))}
          </ul>
        </>
      )}
    </section>
  );
}

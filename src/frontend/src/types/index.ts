export type MarketPoint = {
  id: number;
  product_id: number;
  product_name: string;
  price_value: number | null;
  observed_at: string;
  location: string | null;
};

export type IntelligenceDecision = {
  product_id: number;
  demand_forecast: number;
  product_score: number;
  anomaly_probability: number;
  pricing_recommendation: string;
  stock_decision: string;
  risk_alert: string;
  score: number;
  explanation: string[];
};

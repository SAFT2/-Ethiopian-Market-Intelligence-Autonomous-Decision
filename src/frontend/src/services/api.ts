import axios from "axios";
import type { IntelligenceDecision, MarketPoint } from "../types";

const api = axios.create({
  baseURL: import.meta.env.VITE_BACKEND_URL ?? "http://localhost:8000/api/v1",
  timeout: 10000,
});

export function setAuthToken(token: string) {
  api.defaults.headers.common.Authorization = `Bearer ${token}`;
}

export async function login(email: string, password: string): Promise<{ access_token: string; role: string }> {
  const response = await api.post<{ access_token: string; token_type: string; role: string }>("/auth/login", {
    email,
    password,
  });
  return { access_token: response.data.access_token, role: response.data.role };
}

export async function fetchMarketData(productId?: number): Promise<MarketPoint[]> {
  const response = await api.get<MarketPoint[]>("/market-data", {
    params: { product_id: productId, limit: 100 },
  });
  return response.data;
}

export async function evaluateIntelligence(payload: {
  product_id: number;
  location: string;
  current_price: number;
  avg_market_price: number;
  inventory_days_cover: number;
  weekly_sales_units: number;
  history_prices: number[];
}): Promise<IntelligenceDecision> {
  const response = await api.post<IntelligenceDecision>("/intelligence/evaluate", payload);
  return response.data;
}

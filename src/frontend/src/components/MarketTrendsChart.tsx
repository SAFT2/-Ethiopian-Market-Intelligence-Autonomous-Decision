import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { MarketPoint } from "../types";

type Props = {
  points: MarketPoint[];
};

export function MarketTrendsChart({ points }: Props) {
  const data = points
    .filter((p) => p.price_value !== null)
    .map((p) => ({
      time: new Date(p.observed_at).toLocaleDateString(),
      price: p.price_value,
    }))
    .reverse();

  return (
    <section className="card">
      <h2>Market Trends</h2>
      <div style={{ height: 300 }}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="time" />
            <YAxis />
            <Tooltip />
            <Line type="monotone" dataKey="price" stroke="#1770a6" strokeWidth={3} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}

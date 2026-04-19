from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class DecisionInput:
    current_price: float
    avg_market_price: float
    inventory_days_cover: float
    weekly_sales_units: float
    forecast_demand_units: float
    product_score: float
    anomaly_flag: bool


@dataclass(slots=True)
class DecisionOutput:
    pricing_recommendation: str
    stock_decision: str
    risk_alert: str
    score: float
    explanation: list[str]


class DecisionEngine:
    """Combines deterministic rules and weighted scoring with explainability."""

    def __init__(self) -> None:
        self.weights = {
            "demand_gap": 0.35,
            "price_gap": 0.20,
            "inventory_pressure": 0.25,
            "product_score": 0.20,
        }

    def evaluate(self, data: DecisionInput) -> DecisionOutput:
        explanation: list[str] = []

        demand_gap = self._safe_ratio(data.forecast_demand_units - data.weekly_sales_units, data.weekly_sales_units)
        price_gap = self._safe_ratio(data.avg_market_price - data.current_price, data.current_price)
        inventory_pressure = 1.0 if data.inventory_days_cover < 14 else 0.3 if data.inventory_days_cover < 30 else -0.2

        score = (
            self.weights["demand_gap"] * demand_gap
            + self.weights["price_gap"] * price_gap
            + self.weights["inventory_pressure"] * inventory_pressure
            + self.weights["product_score"] * (2 * data.product_score - 1)
        )

        if data.anomaly_flag:
            score -= 0.35
            explanation.append("Anomaly detected in recent market behavior; risk score penalized.")

        pricing_reco = self._pricing_rule(data, score, explanation)
        stock_decision = self._stock_rule(data, score, explanation)
        risk_alert = self._risk_rule(data, score, explanation)

        return DecisionOutput(
            pricing_recommendation=pricing_reco,
            stock_decision=stock_decision,
            risk_alert=risk_alert,
            score=round(score, 4),
            explanation=explanation,
        )

    def _pricing_rule(self, data: DecisionInput, score: float, explanation: list[str]) -> str:
        if score > 0.25 and data.current_price < data.avg_market_price:
            explanation.append("Demand outlook is positive and current price is below market average.")
            return "increase_price_3_to_5_percent"
        if score < -0.1:
            explanation.append("Composite score is weak; price reduction can protect sales velocity.")
            return "decrease_price_2_to_4_percent"
        explanation.append("Signals are mixed; keep price stable until clearer trend emerges.")
        return "hold_price"

    def _stock_rule(self, data: DecisionInput, score: float, explanation: list[str]) -> str:
        if data.inventory_days_cover < 10 and data.forecast_demand_units > data.weekly_sales_units:
            explanation.append("Low inventory cover with rising demand forecast; urgent replenishment required.")
            return "reorder_urgent"
        if score > 0.15 and data.inventory_days_cover < 25:
            explanation.append("Moderate inventory with strong outlook; place a planned reorder.")
            return "reorder_planned"
        if data.inventory_days_cover > 45 and score < 0:
            explanation.append("High inventory and weak outlook; pause replenishment.")
            return "hold_restock"
        explanation.append("Inventory is within acceptable operating range.")
        return "monitor_stock"

    def _risk_rule(self, data: DecisionInput, score: float, explanation: list[str]) -> str:
        if data.anomaly_flag or score < -0.25:
            explanation.append("Risk elevated due to anomaly signal or low composite score.")
            return "high_risk_review_required"
        if score < 0.05:
            explanation.append("Moderate uncertainty detected; keep human-in-the-loop approval.")
            return "medium_risk_monitor"
        explanation.append("Risk profile is acceptable for automated execution.")
        return "low_risk"

    @staticmethod
    def _safe_ratio(numerator: float, denominator: float) -> float:
        if abs(denominator) < 1e-8:
            return 0.0
        return numerator / denominator

from __future__ import annotations

from dataclasses import asdict

from decision_engine.engine import DecisionEngine, DecisionInput


def build_examples() -> list[dict]:
    engine = DecisionEngine()

    scenarios = [
        DecisionInput(
            current_price=2400,
            avg_market_price=2550,
            inventory_days_cover=9,
            weekly_sales_units=180,
            forecast_demand_units=230,
            product_score=0.81,
            anomaly_flag=False,
        ),
        DecisionInput(
            current_price=2650,
            avg_market_price=2500,
            inventory_days_cover=55,
            weekly_sales_units=120,
            forecast_demand_units=90,
            product_score=0.44,
            anomaly_flag=True,
        ),
    ]

    outputs = []
    for idx, scenario in enumerate(scenarios, start=1):
        decision = engine.evaluate(scenario)
        outputs.append(
            {
                "scenario": idx,
                "input": asdict(scenario),
                "output": asdict(decision),
            }
        )
    return outputs


if __name__ == "__main__":
    for item in build_examples():
        print(item)

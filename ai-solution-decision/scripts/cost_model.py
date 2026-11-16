"""Scenario TCO with bounded per-stage retries; no vendor prices bundled."""
import argparse
import sys
from common import emit, load_json, number


def calculate(data):
    if not isinstance(data, dict):
        raise ValueError("input must be an object")
    currency = data["currency"]
    if not isinstance(currency, str) or not currency.strip():
        raise ValueError("currency must be explicit; no currency conversion is performed")
    if data["data_class"] not in ("simulated", "estimate", "observed"):
        raise ValueError("data_class must be simulated, estimate or observed")
    tasks = number(data["monthly_tasks"], "monthly_tasks", integer=True)
    fixed = number(data["fixed_monthly_cost"], "fixed_monthly_cost")
    setup = number(data["integration_cost"], "integration_cost")
    exit_cost = number(data["exit_cost"], "exit_cost")
    if not isinstance(data["stages"], list) or not data["stages"]:
        raise ValueError("at least one stage required, including a zero-cost deterministic stage")
    stages = []
    total = 0
    names = set()
    for row in data["stages"]:
        name = row["name"]
        if not isinstance(name, str) or not name or name in names:
            raise ValueError("stage names must be unique nonempty strings")
        names.add(name)
        calls = number(row["calls_per_task"], "calls_per_task", integer=True)
        failure = number(row["retry_probability"], "retry_probability", high=1)
        attempts = number(row["max_attempts"], "max_attempts", low=1, high=10, integer=True)
        expected_attempts = sum(failure ** i for i in range(int(attempts)))
        tokens_in = number(row["input_tokens"], "input_tokens")
        tokens_out = number(row["output_tokens"], "output_tokens")
        rate_in = number(row["input_per_million"], "input_per_million")
        rate_out = number(row["output_per_million"], "output_per_million")
        tool = number(row["tool_cost_per_call"], "tool_cost_per_call")
        attempt_cost = (tokens_in * rate_in + tokens_out * rate_out) / 1_000_000 + tool
        per_task = attempt_cost * calls * expected_attempts
        total += per_task
        stages.append({"name": name, "expected_attempts_per_call": round(expected_attempts, 8),
                       "cost_per_task": round(per_task, 8)})
    human = number(data["human_minutes_per_task"], "human_minutes_per_task") / 60 * number(data["human_hourly_cost"], "human_hourly_cost")
    per_task = total + human
    monthly = tasks * per_task + fixed
    success = data.get("task_success_rate")
    if success is not None:
        number(success, "task_success_rate", high=1)
    # Cost per successful task includes fixed operating cost; sunk setup/exit excluded.
    cost_success = monthly / (tasks * success) if tasks and success else None
    return {"schema_version": "1.0", "currency": currency, "data_class": data["data_class"],
            "stages": stages, "variable_cost_per_task": round(per_task, 8),
            "monthly_cost": round(monthly, 4), "tco_12_months": round(setup + 12 * monthly + exit_cost, 4),
            "tco_36_months": round(setup + 36 * monthly + exit_cost, 4),
            "operating_cost_per_success": round(cost_success, 6) if cost_success is not None else None,
            "volume_sensitivity": [{"volume_multiplier": m, "monthly_cost": round(tasks * m * per_task + fixed, 4)} for m in (0.5, 1, 2)],
            "assumptions": ["All stages attempted for every task; no conditional reach probabilities.",
                            "Retries independent with constant probability; each attempt billed equally.",
                            "No implicit FX, tax, cache discount, concurrency, queueing or latency prediction.",
                            "Success rate is a user-supplied scenario/observation, not inferred from retries.",
                            "12/36-month TCO includes one integration and one end-of-horizon exit cost."]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True)
    args = parser.parse_args()
    try:
        emit(calculate(load_json(args.input)))
    except (ValueError, KeyError, OSError, TypeError) as exc:
        print(f"cost error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())

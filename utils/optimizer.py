import numpy as np
import pandas as pd
from scipy.optimize import minimize

from utils.metrics import platform_performance


def prepare_platform_data(df):
    """Aggregate historical campaign data by platform."""

    result = platform_performance(df).copy()

    if result.empty:
        raise ValueError("No platform data available.")

    result["spend"] = pd.to_numeric(
        result["spend"], errors="coerce"
    ).fillna(0)

    result["revenue"] = pd.to_numeric(
        result["revenue"], errors="coerce"
    ).fillna(0)

    result["conversions"] = pd.to_numeric(
        result["conversions"], errors="coerce"
    ).fillna(0)

    result = result[result["spend"] > 0].copy()

    if result.empty:
        raise ValueError(
            "At least one platform needs positive spend."
        )

    # Historical revenue per advertising rupee.
    result["historical_roas"] = (
        result["revenue"] / result["spend"]
    )

    result["historical_cpa"] = np.where(
        result["conversions"] > 0,
        result["spend"] / result["conversions"],
        np.nan
    )

    return result.reset_index(drop=True)


def response_curve(allocation, roas, reference, alpha):
    """
    Estimated revenue from an advertising allocation.

    Formula:
        revenue = allocation * historical_roas
                  * (1 + allocation/reference)^(-alpha)

    alpha controls diminishing returns.
    This is a simulation assumption, not a fitted model.
    """

    allocation = np.asarray(
        allocation, dtype=float
    )

    roas = np.asarray(roas, dtype=float)
    reference = np.asarray(reference, dtype=float)

    return (
        allocation * roas
        * np.power(
            1.0 + allocation / np.maximum(reference, 1.0),
            -alpha
        )
    )


def optimize_budget(
    df,
    budget=1_000_000,
    min_share=0.05,
    max_share=0.45,
    alpha=0.25,
    max_iterations=1000
):
    """
    Allocate budget across available platforms.

    Constraints:
      - all allocations are nonnegative
      - total allocation equals the full budget
      - each platform obeys minimum/maximum share

    Uses scipy SLSQP with multiple starting points.
    The resulting estimate is scenario-based.
    """

    budget = float(budget)

    if not np.isfinite(budget) or budget <= 0:
        raise ValueError("Budget must be positive.")

    if not (0 <= min_share <= max_share <= 1):
        raise ValueError("Invalid allocation limits.")

    if not (0 <= alpha <= 1):
        raise ValueError("Alpha must be between 0 and 1.")

    platform_data = prepare_platform_data(df)

    n = len(platform_data)

    if n * min_share > 1 + 1e-9:
        raise ValueError(
            "Minimum shares exceed 100% of budget."
        )

    if n * max_share < 1 - 1e-9:
        raise ValueError(
            "Maximum shares cannot cover 100%."
        )

    historical_spend = platform_data[
        "spend"
    ].to_numpy(dtype=float)

    historical_roas = platform_data[
        "historical_roas"
    ].to_numpy(dtype=float)

    # Reference scale proportional to historical mix,
    # with a floor to avoid extreme small references.
    spend_share = historical_spend / historical_spend.sum()

    reference = np.maximum(
        budget * spend_share,
        budget * 0.05 / n
    )

    lower = np.full(n, min_share)
    upper = np.full(n, max_share)

    bounds = list(zip(lower, upper))

    def projected_revenue(shares):
        return float(
            response_curve(
                shares * budget,
                historical_roas,
                reference,
                alpha
            ).sum()
        )

    def objective(shares):
        return -projected_revenue(shares) / budget

    constraints = [{
        "type": "eq",
        "fun": lambda x: np.sum(x) - 1.0
    }]

    # Start with feasible equal allocation.
    equal_start = np.full(n, 1.0 / n)

    # Historical mix may violate share constraints,
    # so optimize from the guaranteed feasible start.
    starts = [equal_start]

    candidates = []

    for start in starts:
        outcome = minimize(
            objective,
            start,
            method="SLSQP",
            bounds=bounds,
            constraints=constraints,
            options={
                "maxiter": max_iterations,
                "ftol": 1e-11
            }
        )

        if (
            outcome.success
            and np.isfinite(outcome.fun)
            and abs(outcome.x.sum() - 1) < 1e-5
            and np.all(outcome.x >= lower - 1e-6)
            and np.all(outcome.x <= upper + 1e-6)
        ):
            candidates.append(outcome.x)

    if not candidates:
        raise RuntimeError(
            "Optimization did not converge. "
            "Try less restrictive allocation limits."
        )

    best_shares = min(
        candidates,
        key=objective
    )

    allocation = best_shares * budget

    predicted_revenue = response_curve(
        allocation,
        historical_roas,
        reference,
        alpha
    )

    # Baseline is the observed historical spend mix
    # applied to the same future budget.
    baseline_allocation = spend_share * budget

    baseline_revenue = response_curve(
        baseline_allocation,
        historical_roas,
        reference,
        alpha
    )

    result = platform_data[
        [
            "platform",
            "historical_roas",
            "historical_cpa",
            "spend",
            "revenue",
            "conversions"
        ]
    ].copy()

    result = result.rename(columns={
        "spend": "historical_spend",
        "revenue": "historical_revenue",
        "conversions": "historical_conversions"
    })

    result["allocation_pct"] = best_shares * 100
    result["recommended_budget"] = allocation

    result["baseline_budget"] = baseline_allocation

    result["estimated_revenue"] = predicted_revenue
    result["baseline_estimated_revenue"] = baseline_revenue

    result["estimated_roas"] = (
        predicted_revenue / np.maximum(allocation, 1e-9)
    )

    result["estimated_conversions"] = np.where(
        result["historical_cpa"].notna(),
        allocation / result["historical_cpa"].fillna(np.inf),
        0
    )

    result["estimated_revenue_after_ad_spend"] = (
        result["estimated_revenue"]
        - result["recommended_budget"]
    )

    total_revenue = float(predicted_revenue.sum())
    baseline_total = float(baseline_revenue.sum())

    summary = {
        "budget": budget,
        "estimated_revenue": total_revenue,
        "estimated_roas": total_revenue / budget,
        "baseline_revenue": baseline_total,
        "baseline_roas": baseline_total / budget,
        "estimated_revenue_change": (
            total_revenue - baseline_total
        ),
        "estimated_revenue_change_pct": (
            (total_revenue - baseline_total)
            / baseline_total * 100
            if baseline_total > 0 else 0
        ),
        "estimated_conversions": float(
            result["estimated_conversions"].sum()
        ),
        "alpha": alpha,
        "min_share": min_share,
        "max_share": max_share
    }

    result = result.sort_values(
        "recommended_budget",
        ascending=False
    ).reset_index(drop=True)

    return result, summary


def build_scenarios(
    df,
    budget=1_000_000,
    min_share=0.05,
    max_share=0.45
):
    """Compare different response-curve assumptions."""

    scenarios = [
        ("Low saturation", 0.10),
        ("Moderate saturation", 0.25),
        ("High saturation", 0.45)
    ]

    rows = []

    for name, alpha in scenarios:
        allocation, summary = optimize_budget(
            df=df,
            budget=budget,
            min_share=min_share,
            max_share=max_share,
            alpha=alpha
        )

        rows.append({
            "scenario": name,
            "alpha": alpha,
            "estimated_revenue": summary[
                "estimated_revenue"
            ],
            "estimated_roas": summary[
                "estimated_roas"
            ],
            "revenue_change_pct": summary[
                "estimated_revenue_change_pct"
            ],
            "budget": budget
        })

    return pd.DataFrame(rows)

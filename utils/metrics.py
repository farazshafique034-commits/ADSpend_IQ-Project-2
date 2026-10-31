import numpy as np
import pandas as pd


def safe_divide(numerator, denominator):
    """
    Prevent division-by-zero errors.
    """

    return (
        float(numerator) / float(denominator)
        if denominator != 0
        else 0.0
    )


def calculate_kpis(df):
    """
    Calculate marketing KPIs from aggregated totals.
    """

    impressions = df["impressions"].sum()
    clicks = df["clicks"].sum()
    spend = df["spend"].sum()
    conversions = df["conversions"].sum()
    revenue = df["revenue"].sum()

    return {
        "records": int(len(df)),
        "impressions": int(impressions),
        "clicks": int(clicks),
        "spend": round(float(spend), 2),
        "conversions": int(conversions),
        "revenue": round(float(revenue), 2),

        "ctr": round(
            safe_divide(clicks, impressions) * 100, 2
        ),

        "cpc": round(
            safe_divide(spend, clicks), 2
        ),

        "cpa": round(
            safe_divide(spend, conversions), 2
        ),

        "conversion_rate": round(
            safe_divide(conversions, clicks) * 100, 2
        ),

        "roas": round(
            safe_divide(revenue, spend), 3
        ),

        "revenue_after_ad_spend": round(
            float(revenue - spend), 2
        )
    }


def platform_performance(df):
    """
    Calculate platform performance from aggregated totals.
    """

    grouped = (
        df.groupby("platform", as_index=False)
        .agg(
            impressions=("impressions", "sum"),
            clicks=("clicks", "sum"),
            spend=("spend", "sum"),
            conversions=("conversions", "sum"),
            revenue=("revenue", "sum")
        )
    )

    grouped["ctr"] = np.where(
        grouped["impressions"] > 0,
        grouped["clicks"] / grouped["impressions"] * 100,
        0
    )

    grouped["cpc"] = np.where(
        grouped["clicks"] > 0,
        grouped["spend"] / grouped["clicks"],
        0
    )

    grouped["cpa"] = np.where(
        grouped["conversions"] > 0,
        grouped["spend"] / grouped["conversions"],
        0
    )

    grouped["conversion_rate"] = np.where(
        grouped["clicks"] > 0,
        grouped["conversions"] / grouped["clicks"] * 100,
        0
    )

    grouped["roas"] = np.where(
        grouped["spend"] > 0,
        grouped["revenue"] / grouped["spend"],
        0
    )

    return grouped.round(3)


def campaign_performance(df):
    """
    Calculate campaign-level performance.
    """

    grouped = (
        df.groupby(
            ["campaign", "platform"],
            as_index=False
        )
        .agg(
            impressions=("impressions", "sum"),
            clicks=("clicks", "sum"),
            spend=("spend", "sum"),
            conversions=("conversions", "sum"),
            revenue=("revenue", "sum")
        )
    )

    grouped["roas"] = np.where(
        grouped["spend"] > 0,
        grouped["revenue"] / grouped["spend"],
        0
    )

    grouped["ctr"] = np.where(
        grouped["impressions"] > 0,
        grouped["clicks"] / grouped["impressions"] * 100,
        0
    )

    grouped["conversion_rate"] = np.where(
        grouped["clicks"] > 0,
        grouped["conversions"] / grouped["clicks"] * 100,
        0
    )

    return grouped.round(3)


def daily_performance(df):
    """
    Aggregate advertising performance by day.
    """

    grouped = (
        df.groupby("date", as_index=False)
        .agg(
            spend=("spend", "sum"),
            revenue=("revenue", "sum"),
            clicks=("clicks", "sum"),
            conversions=("conversions", "sum")
        )
        .sort_values("date")
    )

    grouped["roas"] = np.where(
        grouped["spend"] > 0,
        grouped["revenue"] / grouped["spend"],
        0
    )

    return grouped


def audience_performance(df, column="city"):
    """
    Compare performance across audience segments.
    """

    allowed = ["city", "device", "gender", "age"]

    if column not in allowed:
        raise ValueError("Invalid audience dimension")

    grouped = (
        df.groupby(column, as_index=False)
        .agg(
            impressions=("impressions", "sum"),
            clicks=("clicks", "sum"),
            spend=("spend", "sum"),
            conversions=("conversions", "sum"),
            revenue=("revenue", "sum")
        )
    )

    grouped["roas"] = np.where(
        grouped["spend"] > 0,
        grouped["revenue"] / grouped["spend"],
        0
    )

    return grouped.round(3)

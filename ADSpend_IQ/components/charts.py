import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from config.settings import PLATFORM_COLORS
from utils.metrics import (
    platform_performance,
    daily_performance,
    campaign_performance
)

BACKGROUND = "#101B2F"
TEXT_COLOR = "#EAF2FF"
GRID_COLOR = "#263752"


def style_chart(fig, height=430):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=BACKGROUND,
        plot_bgcolor=BACKGROUND,
        font=dict(
            family="Arial",
            color=TEXT_COLOR,
            size=12
        ),
        height=height,
        margin=dict(l=35, r=30, t=65, b=40),
        hovermode="closest",
        legend=dict(
            orientation="h",
            y=-0.22,
            x=0
        )
    )

    fig.update_xaxes(
        showgrid=False,
        zeroline=False
    )

    fig.update_yaxes(
        gridcolor=GRID_COLOR,
        zeroline=False
    )

    return fig


def revenue_spend_chart(df):
    daily = daily_performance(df)

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=daily["date"],
            y=daily["revenue"],
            name="Revenue",
            mode="lines",
            line=dict(
                color="#38BDF8",
                width=3
            ),
            fill="tozeroy",
            fillcolor="rgba(56,189,248,0.07)"
        )
    )

    fig.add_trace(
        go.Scatter(
            x=daily["date"],
            y=daily["spend"],
            name="Advertising Spend",
            mode="lines",
            line=dict(
                color="#F59E0B",
                width=2
            )
        )
    )

    fig.update_layout(
        title="Advertising Spend vs Revenue",
        xaxis_title="Date",
        yaxis_title="PKR"
    )

    return style_chart(fig)


def platform_roas_chart(df):
    perf = platform_performance(df)
    perf = perf.sort_values("roas", ascending=False)

    fig = px.bar(
        perf,
        x="platform",
        y="roas",
        color="platform",
        color_discrete_map=PLATFORM_COLORS,
        text="roas",
        title="Return on Ad Spend by Platform",
        labels={
            "platform": "Platform",
            "roas": "ROAS (x)"
        }
    )

    fig.update_traces(
        texttemplate="%{text:.2f}x",
        textposition="outside"
    )

    fig.update_layout(showlegend=False)

    return style_chart(fig)


def spend_distribution_chart(df):
    perf = platform_performance(df)

    fig = px.pie(
        perf,
        names="platform",
        values="spend",
        hole=0.65,
        color="platform",
        color_discrete_map=PLATFORM_COLORS,
        title="Advertising Spend Distribution"
    )

    fig.update_traces(
        textinfo="percent",
        hovertemplate=(
            "%{label}<br>"
            "Spend: Rs. %{value:,.0f}<br>"
            "Share: %{percent}<extra></extra>"
        )
    )

    return style_chart(fig)


def conversions_chart(df):
    perf = platform_performance(df)

    fig = px.bar(
        perf,
        x="platform",
        y="conversions",
        color="platform",
        color_discrete_map=PLATFORM_COLORS,
        title="Conversions by Advertising Platform",
        text="conversions"
    )

    fig.update_traces(
        textposition="outside"
    )

    fig.update_layout(showlegend=False)

    return style_chart(fig)


def ctr_chart(df):
    perf = platform_performance(df)

    fig = px.bar(
        perf.sort_values("ctr"),
        x="ctr",
        y="platform",
        orientation="h",
        color="platform",
        color_discrete_map=PLATFORM_COLORS,
        title="Click-Through Rate Comparison",
        labels={
            "ctr": "CTR (%)",
            "platform": "Platform"
        },
        text="ctr"
    )

    fig.update_traces(
        texttemplate="%{text:.2f}%",
        textposition="outside"
    )

    fig.update_layout(showlegend=False)

    return style_chart(fig)


def cpa_chart(df):
    perf = platform_performance(df)

    fig = px.bar(
        perf,
        x="platform",
        y="cpa",
        color="platform",
        color_discrete_map=PLATFORM_COLORS,
        title="Cost Per Acquisition Comparison",
        labels={
            "cpa": "CPA (PKR)",
            "platform": "Platform"
        }
    )

    fig.update_layout(showlegend=False)

    return style_chart(fig)


def campaign_performance_chart(df):
    perf = campaign_performance(df)

    # Aggregate across platforms for a campaign-level chart
    grouped = (
        perf.groupby("campaign", as_index=False)
        .agg(
            spend=("spend", "sum"),
            revenue=("revenue", "sum")
        )
    )

    grouped["roas"] = np.where(
        grouped["spend"] > 0,
        grouped["revenue"] / grouped["spend"],
        0
    )

    grouped = grouped.sort_values(
        "roas", ascending=True
    )

    fig = px.bar(
        grouped,
        x="roas",
        y="campaign",
        orientation="h",
        color="roas",
        color_continuous_scale="Blues",
        title="Campaign ROAS Ranking",
        labels={
            "roas": "ROAS (x)",
            "campaign": "Campaign"
        }
    )

    fig.update_layout(
        coloraxis_showscale=False
    )

    return style_chart(fig, 470)


def platform_performance_table(df):
    perf = platform_performance(df)

    return perf[
        [
            "platform",
            "impressions",
            "clicks",
            "spend",
            "conversions",
            "revenue",
            "ctr",
            "cpc",
            "cpa",
            "conversion_rate",
            "roas"
        ]
    ].sort_values(
        "roas",
        ascending=False
    )

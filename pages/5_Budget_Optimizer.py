import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from components.theme import load_theme, render_hero
from components.sidebar import load_data_with_sidebar
from components.charts import style_chart

from utils.optimizer import (
    optimize_budget,
    prepare_platform_data,
    build_scenarios
)

st.set_page_config(
    page_title="Budget Optimizer | AdSpend IQ",
    page_icon="💰",
    layout="wide"
)

load_theme()

render_hero(
    "Marketing Budget Optimization Studio",
    "Discover a constrained, explainable allocation "
    "for your next advertising investment.",
    eyebrow="ADSPEND IQ / DECISION INTELLIGENCE"
)

df = load_data_with_sidebar()

if df.empty:
    st.warning("No records match your selected filters.")
    st.stop()

st.markdown("### Optimization Controls")

c1, c2 = st.columns(2)

with c1:
    budget = st.number_input(
        "Total Marketing Budget (PKR)",
        min_value=10000,
        max_value=100000000,
        value=1000000,
        step=50000
    )

with c2:
    alpha = st.slider(
        "Diminishing Returns Strength",
        min_value=0.0,
        max_value=0.80,
        value=0.25,
        step=0.05,
        help=(
            "Higher values assume performance drops "
            "more strongly when platform spend increases."
        )
    )

c3, c4 = st.columns(2)

with c3:
    min_pct = st.slider(
        "Minimum Budget per Platform (%)",
        0, 30, 5, 1
    )

with c4:
    max_pct = st.slider(
        "Maximum Budget per Platform (%)",
        20, 100, 45, 1
    )

min_share = min_pct / 100
max_share = max_pct / 100

n_platforms = len(prepare_platform_data(df))

if (
    n_platforms * min_share > 1
    or n_platforms * max_share < 1
):
    st.error(
        "These allocation limits are not feasible "
        f"for {n_platforms} selected platforms. "
        "Adjust minimum and maximum percentages."
    )
    st.stop()

try:
    allocation, summary = optimize_budget(
        df,
        budget=budget,
        min_share=min_share,
        max_share=max_share,
        alpha=alpha
    )
except Exception as exc:
    st.error(f"Optimization error: {exc}")
    st.stop()

st.success(
    "Optimization completed. Recommended allocations "
    "sum to the full selected advertising budget."
)

st.caption(
    "Estimates use historical simulated ROAS with "
    "assumed diminishing returns. They are not "
    "guaranteed revenue forecasts."
)

# ==========================================================
# SUMMARY CARDS
# ==========================================================

st.markdown("### Recommended Business Outcome")

a, b, c, d = st.columns(4)

a.metric(
    "Marketing Budget",
    f'Rs. {summary["budget"]:,.0f}'
)

b.metric(
    "Estimated Revenue",
    f'Rs. {summary["estimated_revenue"]:,.0f}'
)

c.metric(
    "Estimated ROAS",
    f'{summary["estimated_roas"]:.2f}x'
)

d.metric(
    "Estimated Revenue Change",
    f'{summary["estimated_revenue_change_pct"]:+.2f}%'
)

st.divider()

# ==========================================================
# BUDGET ALLOCATION CHARTS
# ==========================================================

left, right = st.columns(2, gap="large")

with left:
    fig = px.pie(
        allocation,
        names="platform",
        values="recommended_budget",
        hole=0.65,
        title="Recommended Advertising Budget Split"
    )

    fig.update_traces(
        textinfo="label+percent"
    )

    st.plotly_chart(
        style_chart(fig, 470),
        use_container_width=True
    )

with right:
    fig = px.bar(
        allocation,
        x="platform",
        y="recommended_budget",
        color="platform",
        text="allocation_pct",
        title="Platform-wise Recommended Investment"
    )

    fig.update_traces(
        texttemplate="%{text:.1f}%",
        textposition="outside"
    )

    fig.update_layout(
        showlegend=False,
        yaxis_title="Recommended Spend (PKR)"
    )

    st.plotly_chart(
        style_chart(fig, 470),
        use_container_width=True
    )

# ==========================================================
# BASELINE VS OPTIMIZED
# ==========================================================

st.markdown("### Historical Mix vs Optimized Mix")

fig = go.Figure()

fig.add_bar(
    x=allocation["platform"],
    y=allocation["baseline_budget"],
    name="Historical Mix Baseline",
    marker_color="#F59E0B"
)

fig.add_bar(
    x=allocation["platform"],
    y=allocation["recommended_budget"],
    name="Optimized Budget",
    marker_color="#38BDF8"
)

fig.update_layout(
    barmode="group",
    title="Budget Reallocation Comparison",
    yaxis_title="Budget (PKR)"
)

st.plotly_chart(
    style_chart(fig, 480),
    use_container_width=True
)

# ==========================================================
# ESTIMATED PLATFORM REVENUE
# ==========================================================

st.markdown("### Estimated Revenue by Platform")

fig = px.bar(
    allocation,
    x="platform",
    y="estimated_revenue",
    color="platform",
    title="Scenario-based Revenue Estimation",
    hover_data=[
        "recommended_budget",
        "estimated_roas",
        "historical_roas"
    ]
)

fig.update_layout(showlegend=False)

st.plotly_chart(
    style_chart(fig, 450),
    use_container_width=True
)

# ==========================================================
# REVENUE COMPARISON
# ==========================================================

st.markdown("### Baseline vs Recommendation")

comparison = pd.DataFrame({
    "Strategy": [
        "Historical Spend Mix",
        "Optimized Spend Mix"
    ],
    "Estimated Revenue": [
        summary["baseline_revenue"],
        summary["estimated_revenue"]
    ]
})

fig = px.bar(
    comparison,
    x="Strategy",
    y="Estimated Revenue",
    color="Strategy",
    text="Estimated Revenue",
    title="Estimated Revenue Comparison"
)

fig.update_traces(
    texttemplate="Rs. %{text:,.0f}",
    textposition="outside"
)

fig.update_layout(showlegend=False)

st.plotly_chart(
    style_chart(fig, 440),
    use_container_width=True
)

# ==========================================================
# WHAT-IF SCENARIOS
# ==========================================================

st.markdown("### What-if Scenario Analysis")

try:
    scenarios = build_scenarios(
        df,
        budget=budget,
        min_share=min_share,
        max_share=max_share
    )

    fig = px.bar(
        scenarios,
        x="scenario",
        y="estimated_revenue",
        color="scenario",
        title="Estimated Revenue Under Different Assumptions"
    )

    fig.update_layout(showlegend=False)

    st.plotly_chart(
        style_chart(fig, 450),
        use_container_width=True
    )

    st.dataframe(
        scenarios.round(2),
        use_container_width=True,
        hide_index=True
    )

except Exception as exc:
    st.warning(f"Scenario comparison unavailable: {exc}")

# ==========================================================
# EXPLAINABLE RECOMMENDATION TABLE
# ==========================================================

st.markdown("### Platform Allocation Recommendations")

display_columns = [
    "platform",
    "historical_roas",
    "historical_cpa",
    "baseline_budget",
    "allocation_pct",
    "recommended_budget",
    "estimated_revenue",
    "estimated_roas",
    "estimated_conversions"
]

st.dataframe(
    allocation[display_columns].round(2),
    use_container_width=True,
    hide_index=True
)

best = allocation.iloc[0]

st.info(
    f"The largest recommended allocation is "
    f"{best['platform']} at "
    f"{best['allocation_pct']:.1f}% "
    f"(Rs. {best['recommended_budget']:,.0f}). "
    "This result follows the selected model assumptions "
    "and platform allocation constraints."
)

st.download_button(
    "Download Budget Recommendation CSV",
    data=allocation.to_csv(index=False),
    file_name="budget_recommendations.csv",
    mime="text/csv",
    use_container_width=True
)

st.caption(
    "Revenue is not profit. The optimization model "
    "does not include product costs, taxes, customer "
    "lifetime value or verified market response curves."
)

# ADSPEND_PROJECT1_INTEGRATION
from components.sentiment_ui import render_sentiment_connection
render_sentiment_connection()

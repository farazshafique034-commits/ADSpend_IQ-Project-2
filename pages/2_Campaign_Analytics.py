import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from components.theme import load_theme, render_hero
from components.sidebar import load_data_with_sidebar
from components.charts import style_chart
from utils.metrics import calculate_kpis, campaign_performance

st.set_page_config(
    page_title="Campaign Analytics | AdSpend IQ",
    page_icon="📈",
    layout="wide"
)

load_theme()

render_hero(
    "Campaign Performance Intelligence",
    "Analyze campaign revenue, advertising costs, "
    "conversions, ROAS and acquisition efficiency.",
    eyebrow="ADSPEND IQ / CAMPAIGN ANALYTICS"
)

df = load_data_with_sidebar()

if df.empty:
    st.warning("No records match the selected filters.")
    st.stop()


def safe_ratio(a, b, scale=1):
    return np.where(
        np.asarray(b) > 0,
        np.asarray(a) /
        np.maximum(np.asarray(b), 1e-12) * scale,
        0
    )


campaigns = (
    df.groupby("campaign", as_index=False)
    .agg(
        impressions=("impressions", "sum"),
        clicks=("clicks", "sum"),
        spend=("spend", "sum"),
        conversions=("conversions", "sum"),
        revenue=("revenue", "sum")
    )
)

campaigns["ctr"] = safe_ratio(
    campaigns["clicks"], campaigns["impressions"], 100
)

campaigns["cvr"] = safe_ratio(
    campaigns["conversions"], campaigns["clicks"], 100
)

campaigns["roas"] = safe_ratio(
    campaigns["revenue"], campaigns["spend"]
)

campaigns["cpc"] = safe_ratio(
    campaigns["spend"], campaigns["clicks"]
)

campaigns["cpa"] = safe_ratio(
    campaigns["spend"], campaigns["conversions"]
)

campaigns = campaigns.sort_values(
    "revenue", ascending=False
)

kpis = calculate_kpis(df)

st.markdown("### Campaign Performance Summary")

a, b, c, d = st.columns(4)

a.metric("Campaigns", len(campaigns))
b.metric("Total Ad Spend", f'Rs. {kpis["spend"]:,.0f}')
c.metric("Revenue", f'Rs. {kpis["revenue"]:,.0f}')
d.metric("Overall ROAS", f'{kpis["roas"]:.2f}x')

st.divider()

# CHART 1 - REVENUE VS SPEND

st.markdown("### Campaign Revenue vs Advertising Spend")

fig = go.Figure()

fig.add_bar(
    x=campaigns["campaign"],
    y=campaigns["spend"],
    name="Ad Spend",
    marker_color="#F59E0B"
)

fig.add_bar(
    x=campaigns["campaign"],
    y=campaigns["revenue"],
    name="Revenue",
    marker_color="#38BDF8"
)

fig.update_layout(
    barmode="group",
    title="Campaign Financial Performance",
    xaxis_title="Campaign",
    yaxis_title="PKR"
)

st.plotly_chart(
    style_chart(fig, 480),
    use_container_width=True
)

# CHART 2 - ROAS AND CPA

left, right = st.columns(2)

with left:
    ranked = campaigns.sort_values("roas")

    fig = px.bar(
        ranked,
        x="roas",
        y="campaign",
        orientation="h",
        color="roas",
        color_continuous_scale="Blues",
        title="Campaign ROAS Ranking"
    )

    fig.update_layout(coloraxis_showscale=False)

    st.plotly_chart(
        style_chart(fig, 460),
        use_container_width=True
    )

with right:
    ranked = campaigns.sort_values("cpa")

    fig = px.bar(
        ranked,
        x="cpa",
        y="campaign",
        orientation="h",
        color="cpa",
        color_continuous_scale="Oranges",
        title="Cost Per Acquisition by Campaign"
    )

    fig.update_layout(coloraxis_showscale=False)

    st.plotly_chart(
        style_chart(fig, 460),
        use_container_width=True
    )

# CHART 3 - CONVERSION FUNNEL

st.markdown("### Interactive Campaign Conversion Funnel")

selected_campaign = st.selectbox(
    "Choose campaign",
    campaigns["campaign"].tolist()
)

row = campaigns[
    campaigns["campaign"] == selected_campaign
].iloc[0]

fig = go.Figure(
    go.Funnel(
        y=["Impressions", "Clicks", "Conversions"],
        x=[
            int(row["impressions"]),
            int(row["clicks"]),
            int(row["conversions"])
        ],
        marker=dict(
            color=["#38BDF8", "#8B5CF6", "#22C55E"]
        ),
        textinfo="value+percent initial"
    )
)

fig.update_layout(
    title=f"Conversion Funnel - {selected_campaign}"
)

st.plotly_chart(
    style_chart(fig, 460),
    use_container_width=True
)

# CHART 4 - SPEND DISTRIBUTION AND PERFORMANCE

left, right = st.columns(2)

with left:
    fig = px.pie(
        campaigns,
        names="campaign",
        values="spend",
        hole=0.60,
        title="Advertising Spend Distribution"
    )

    st.plotly_chart(
        style_chart(fig, 450),
        use_container_width=True
    )

with right:
    fig = px.scatter(
        campaigns,
        x="ctr",
        y="cvr",
        size="spend",
        color="campaign",
        hover_name="campaign",
        title="CTR vs Conversion Rate",
        labels={
            "ctr": "CTR (%)",
            "cvr": "Conversion Rate (%)"
        }
    )

    st.plotly_chart(
        style_chart(fig, 450),
        use_container_width=True
    )

# CHART 5 - HEATMAP

st.markdown("### Campaign vs Platform ROAS Heatmap")

cp = campaign_performance(df)

heatmap = cp.pivot(
    index="campaign",
    columns="platform",
    values="roas"
)

fig = px.imshow(
    heatmap,
    color_continuous_scale="Blues",
    text_auto=".2f",
    aspect="auto",
    title="Campaign and Platform Performance"
)

st.plotly_chart(
    style_chart(fig, 480),
    use_container_width=True
)

# CAMPAIGN TABLE

st.markdown("### Detailed Campaign Analytics")

st.dataframe(
    campaigns.round(2),
    use_container_width=True,
    hide_index=True
)

st.download_button(
    "Download Campaign Analytics CSV",
    data=campaigns.to_csv(index=False),
    file_name="campaign_analytics.csv",
    mime="text/csv"
)

st.caption(
    "These results describe the loaded advertising "
    "dataset. Synthetic demo results are simulations."
)

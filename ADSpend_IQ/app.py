import streamlit as st

from components.theme import (
    load_theme,
    render_hero
)

from components.sidebar import load_data_with_sidebar
from components.kpi_cards import render_kpi_cards

from components.charts import (
    revenue_spend_chart,
    platform_roas_chart,
    spend_distribution_chart,
    platform_performance_table
)


st.set_page_config(
    page_title="AdSpend IQ | Marketing Intelligence",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

load_theme()

render_hero(
    "AdSpend IQ",
    "A professional digital advertising analytics "
    "and budget intelligence platform. "
    "Explore marketing KPIs, campaign trends "
    "and advertising performance across "
    "Facebook, Instagram, Google, TikTok and YouTube.",
    eyebrow="DIGITAL ADVERTISING INTELLIGENCE"
)

df = load_data_with_sidebar()

if df.empty:
    st.warning(
        "No data available for selected filters."
    )
    st.stop()

st.markdown("### Executive Performance Snapshot")

render_kpi_cards(df)

st.divider()

st.markdown("### Marketing Revenue Intelligence")

st.plotly_chart(
    revenue_spend_chart(df),
    use_container_width=True
)

left, right = st.columns(2, gap="large")

with left:
    st.plotly_chart(
        platform_roas_chart(df),
        use_container_width=True
    )

with right:
    st.plotly_chart(
        spend_distribution_chart(df),
        use_container_width=True
    )

st.markdown("### Platform Performance Summary")

st.dataframe(
    platform_performance_table(df),
    use_container_width=True,
    hide_index=True
)

st.info(
    "Use the navigation menu to access individual "
    "dashboard sections. Campaign Analytics, "
    "Audience Insights, Big Data Benchmarks and "
    "Budget Optimizer will be implemented "
    "in the next development steps."
)

st.caption(
    "AdSpend IQ | Big Data Analytics Project 2 "
    "| Synthetic marketing data demonstration"
)

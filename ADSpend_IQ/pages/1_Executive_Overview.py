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
    conversions_chart,
    ctr_chart,
    cpa_chart,
    campaign_performance_chart,
    platform_performance_table
)


def render_overview():
    load_theme()

    render_hero(
        "Executive Marketing Overview",
        "Analyze campaign efficiency, advertising "
        "spend, conversions and revenue using "
        "interactive business intelligence."
    )

    df = load_data_with_sidebar()

    if df.empty:
        st.warning(
            "No records match your current filters. "
            "Change your filters to see the dashboard."
        )
        st.stop()

    st.caption(
        f"Showing {len(df):,} records | "
        "Hover, zoom, pan and download Plotly charts."
    )

    st.markdown("### Marketing Performance KPIs")

    render_kpi_cards(df)

    st.divider()

    st.markdown("### Financial Performance")

    st.plotly_chart(
        revenue_spend_chart(df),
        use_container_width=True
    )

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.plotly_chart(
            platform_roas_chart(df),
            use_container_width=True
        )

    with col2:
        st.plotly_chart(
            spend_distribution_chart(df),
            use_container_width=True
        )

    st.markdown("### Conversion & Traffic Analytics")

    col3, col4 = st.columns(2, gap="large")

    with col3:
        st.plotly_chart(
            conversions_chart(df),
            use_container_width=True
        )

    with col4:
        st.plotly_chart(
            ctr_chart(df),
            use_container_width=True
        )

    st.markdown("### Acquisition Cost & Campaigns")

    col5, col6 = st.columns(2, gap="large")

    with col5:
        st.plotly_chart(
            cpa_chart(df),
            use_container_width=True
        )

    with col6:
        st.plotly_chart(
            campaign_performance_chart(df),
            use_container_width=True
        )

    st.divider()

    st.markdown("### Detailed Platform Performance")

    performance = platform_performance_table(df)

    st.dataframe(
        performance,
        use_container_width=True,
        hide_index=True
    )

    csv = performance.to_csv(index=False)

    st.download_button(
        "Download Platform Performance CSV",
        data=csv,
        file_name="adspend_platform_performance.csv",
        mime="text/csv"
    )

    st.info(
        "This dashboard uses simulated advertising "
        "data unless you upload your own dataset. "
        "Performance figures do not represent "
        "verified real-world campaign outcomes."
    )


if __name__ == "__main__":
    st.set_page_config(
        page_title="Executive Overview | AdSpend IQ",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    render_overview()

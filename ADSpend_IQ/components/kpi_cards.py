import streamlit as st
from utils.metrics import calculate_kpis


def money(value):
    return f"Rs. {value:,.0f}"


def render_kpi_cards(df):
    kpis = calculate_kpis(df)

    row1 = st.columns(4, gap="medium")

    with row1[0]:
        st.metric(
            "Advertising Spend",
            money(kpis["spend"])
        )

    with row1[1]:
        st.metric(
            "Generated Revenue",
            money(kpis["revenue"])
        )

    with row1[2]:
        st.metric(
            "Return on Ad Spend",
            f'{kpis["roas"]:.2f}x'
        )

    with row1[3]:
        st.metric(
            "Conversions",
            f'{kpis["conversions"]:,}'
        )

    st.write("")

    row2 = st.columns(4, gap="medium")

    with row2[0]:
        st.metric(
            "Click Through Rate",
            f'{kpis["ctr"]:.2f}%'
        )

    with row2[1]:
        st.metric(
            "Cost Per Click",
            money(kpis["cpc"])
        )

    with row2[2]:
        st.metric(
            "Cost Per Acquisition",
            money(kpis["cpa"])
        )

    with row2[3]:
        st.metric(
            "Conversion Rate",
            f'{kpis["conversion_rate"]:.2f}%'
        )

    return kpis

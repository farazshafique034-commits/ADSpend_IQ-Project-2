import pandas as pd
import streamlit as st

from config.settings import APP_NAME
from utils.data_loader import (
    load_demo_data,
    load_uploaded_data
)


def load_data_with_sidebar():
    """
    Show data selection controls and return the dataset.
    """

    with st.sidebar:
        st.markdown("## ADSPEND IQ")
        st.caption("Digital Marketing Intelligence")

        st.divider()

        st.markdown("### Data Source")

        source = st.radio(
            "Choose source",
            ["Synthetic Demo Data", "Upload CSV"],
            label_visibility="collapsed",
            key="data_source"
        )

        if source == "Synthetic Demo Data":
            n_records = st.selectbox(
                "Demo dataset size",
                [10000, 25000, 50000, 100000],
                index=0,
                key="demo_size"
            )

            df = load_demo_data(n_records)

            st.caption(
                "Simulation only — not real advertising data."
            )

        else:
            uploaded = st.file_uploader(
                "Upload advertising CSV",
                type=["csv"],
                key="uploaded_ads"
            )

            if uploaded is None:
                st.info(
                    "Upload a CSV with the required "
                    "advertising columns."
                )
                st.stop()

            try:
                df = load_uploaded_data(uploaded)
            except Exception as exc:
                st.error(f"Invalid dataset: {exc}")
                st.stop()

        st.divider()
        st.markdown("### Dashboard Filters")

        platforms = sorted(
            df["platform"].dropna().unique().tolist()
        )

        selected_platforms = st.multiselect(
            "Platforms",
            platforms,
            default=platforms,
            key="platform_filter"
        )

        cities = sorted(
            df["city"].dropna().unique().tolist()
        )

        selected_cities = st.multiselect(
            "Cities",
            cities,
            default=cities,
            key="city_filter"
        )

        campaigns = sorted(
            df["campaign"].dropna().unique().tolist()
        )

        selected_campaigns = st.multiselect(
            "Campaigns",
            campaigns,
            default=campaigns,
            key="campaign_filter"
        )

        devices = sorted(
            df["device"].dropna().unique().tolist()
        )

        selected_devices = st.multiselect(
            "Devices",
            devices,
            default=devices,
            key="device_filter"
        )

        min_date = pd.Timestamp(df["date"].min()).date()
        max_date = pd.Timestamp(df["date"].max()).date()

        selected_dates = st.date_input(
            "Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
            key="date_filter"
        )

        st.divider()

        st.caption(
            f"Source dataset: {len(df):,} records"
        )

    filtered = df[
        df["platform"].isin(selected_platforms)
        & df["city"].isin(selected_cities)
        & df["campaign"].isin(selected_campaigns)
        & df["device"].isin(selected_devices)
    ].copy()

    if len(selected_dates) == 2:
        start_date, end_date = selected_dates

        filtered = filtered[
            filtered["date"].dt.date.between(
                start_date, end_date
            )
        ]

    return filtered

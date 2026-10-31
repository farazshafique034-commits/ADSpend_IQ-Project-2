import pandas as pd
import streamlit as st

from config.settings import (
    REQUIRED_COLUMNS,
    RAW_DIR
)

from utils.data_generator import generate_ad_data


def validate_data(df):
    """
    Check advertising dataset structure and constraints.
    """

    missing = [
        col for col in REQUIRED_COLUMNS
        if col not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing required columns: {missing}"
        )

    df = df.copy()

    df["date"] = pd.to_datetime(
        df["date"], errors="coerce"
    )

    numeric_cols = [
        "impressions", "clicks", "spend",
        "conversions", "revenue", "age"
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(
            df[col], errors="coerce"
        )

    if df[REQUIRED_COLUMNS].isna().any().any():
        raise ValueError(
            "Dataset contains missing or invalid required values."
        )

    if (
        (df[numeric_cols] < 0).any().any()
        or (df["clicks"] > df["impressions"]).any()
        or (df["conversions"] > df["clicks"]).any()
        or (df["age"] < 0).any()
    ):
        raise ValueError(
            "Dataset contains invalid advertising metrics."
        )

    return df


@st.cache_data(show_spinner=False)
def load_demo_data(n_records=10000):
    """
    Load reproducible demonstration data.
    """

    data = generate_ad_data(n_records)

    return validate_data(data)


def load_uploaded_data(uploaded_file):
    """
    Load an uploaded advertising CSV.
    """

    df = pd.read_csv(uploaded_file)

    return validate_data(df)


def save_sample_dataset(n_records=10000):
    """
    Save demonstration records as CSV.
    """

    df = generate_ad_data(n_records)

    path = RAW_DIR / "sample_ads.csv"

    df.to_csv(path, index=False)

    return path

"""Reusable Project 1 connection widgets."""

import pandas as pd
import streamlit as st

from utils.sentiment_bridge import (
    SAVED_CSV,
    normalize_sentiment,
    sentiment_summary,
    marketing_actions
)


def linked_sentiment():
    """Read sentiment data from session or saved local CSV."""

    if "p1_sentiment_df" in st.session_state:
        return st.session_state["p1_sentiment_df"]

    if SAVED_CSV.is_file():
        try:
            data = normalize_sentiment(
                pd.read_csv(
                    SAVED_CSV,
                    encoding="utf-8-sig"
                )
            )

            st.session_state["p1_sentiment_df"] = data
            return data

        except (ValueError, OSError) as exc:
            st.warning(
                f"Saved sentiment CSV cannot be loaded: {exc}"
            )

    return None


def render_sentiment_connection():
    """Show sentiment insights alongside budget recommendations."""

    st.divider()
    st.subheader(
        "Project 1 → Project 2: Customer Sentiment"
    )

    df = linked_sentiment()

    if df is None:
        st.info(
            "Open Project 1 Connection from the navigation "
            "menu and upload Project 1's "
            "review_comments_analyzed.csv file."
        )
        return

    summary = sentiment_summary(df)

    columns = st.columns(4)

    for col, label in zip(
        columns,
        ["positive", "negative", "neutral", "mixed"]
    ):
        row = summary[
            summary["sentiment"] == label
        ].iloc[0]

        col.metric(
            label.title(),
            f"{int(row['comments']):,}",
            f"{row['percentage']:.1f}%",
            delta_color="off"
        )

    st.markdown(
        "**Customer-feedback-informed marketing actions:**"
    )

    for action in marketing_actions(df):
        st.write("• " + action)

    st.caption(
        "Sentiment influences campaign-message suggestions. "
        "Budget allocation remains based on advertising "
        "performance and explicit model assumptions."
    )

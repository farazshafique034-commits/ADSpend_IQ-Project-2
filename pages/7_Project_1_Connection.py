import pandas as pd
import plotly.express as px
import streamlit as st

from components.theme import load_theme, render_hero
from components.sidebar import load_data_with_sidebar
from components.charts import style_chart
from components.sentiment_ui import linked_sentiment

from utils.sentiment_bridge import (
    SAVED_CSV,
    normalize_sentiment,
    sentiment_summary,
    negative_themes,
    source_videos,
    marketing_actions
)

from utils.optimizer import optimize_budget


st.set_page_config(
    page_title="Project 1 Connection | AdSpend IQ",
    page_icon="🔗",
    layout="wide"
)

load_theme()

render_hero(
    "Project 1 × Project 2 Integration",
    "Combine SHEIN YouTube sentiment analysis "
    "with digital advertising intelligence.",
    eyebrow="ADSPEND IQ / CROSS-PROJECT INTELLIGENCE"
)

st.markdown("### 1. Connect Project 1 Data")

st.info(
    "Upload review_comments_analyzed.csv generated "
    "by the SHEIN Sentiment Analysis Colab notebook. "
    "No YouTube API key is required here."
)

uploaded = st.file_uploader(
    "Upload analyzed sentiment CSV",
    type=["csv"],
    key="project1_csv_uploader"
)

if uploaded is not None:
    try:
        data = normalize_sentiment(
            pd.read_csv(
                uploaded,
                encoding="utf-8-sig"
            )
        )

        st.session_state["p1_sentiment_df"] = data

        SAVED_CSV.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        data.to_csv(
            SAVED_CSV,
            index=False,
            encoding="utf-8-sig"
        )

        st.success(
            f"Successfully connected {len(data):,} "
            "analyzed comments. A local copy has "
            "been saved for future dashboard sessions."
        )

    except (
        ValueError,
        OSError,
        pd.errors.ParserError
    ) as exc:
        st.error(f"CSV import failed: {exc}")

sentiment_df = linked_sentiment()

if sentiment_df is None:
    st.warning(
        "Upload your Project 1 analyzed CSV "
        "to activate the integration."
    )
    st.stop()

if st.button("Disconnect Project 1 Data"):
    st.session_state.pop(
        "p1_sentiment_df", None
    )

    SAVED_CSV.unlink(missing_ok=True)

    st.success("Project 1 connection removed.")
    st.rerun()


# ==========================================================
# SENTIMENT METRICS
# ==========================================================

st.markdown("### 2. Customer Sentiment Dashboard")

summary = sentiment_summary(sentiment_df)

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

colors = {
    "positive": "#22C55E",
    "negative": "#EF4444",
    "neutral": "#F59E0B",
    "mixed": "#A78BFA"
}

left, right = st.columns(2)

with left:
    fig = px.bar(
        summary,
        x="sentiment",
        y="comments",
        color="sentiment",
        color_discrete_map=colors,
        text="comments",
        title="Sentiment Classification Counts"
    )

    fig.update_layout(showlegend=False)

    st.plotly_chart(
        style_chart(fig),
        use_container_width=True
    )

with right:
    fig = px.pie(
        summary,
        names="sentiment",
        values="comments",
        hole=0.6,
        color="sentiment",
        color_discrete_map=colors,
        title="Sentiment Percentage Distribution"
    )

    st.plotly_chart(
        style_chart(fig),
        use_container_width=True
    )


# ==========================================================
# NEGATIVE COMMENT THEMES
# ==========================================================

st.markdown("### 3. Negative Feedback Intelligence")

themes = negative_themes(sentiment_df)

fig = px.bar(
    themes.sort_values("negative_mentions"),
    x="negative_mentions",
    y="theme",
    orientation="h",
    title="Most Mentioned Negative Feedback Themes"
)

st.plotly_chart(
    style_chart(fig, 430),
    use_container_width=True
)

st.caption(
    "These themes are based on keywords found "
    "in negative opinion segments, not a separately "
    "trained aspect-based sentiment model."
)


# ==========================================================
# ORIGINAL YOUTUBE VIDEO SOURCES
# ==========================================================

st.markdown("### 4. Original YouTube Video Sources")

videos = source_videos(sentiment_df)

if not videos.empty:
    st.dataframe(
        videos,
        hide_index=True,
        use_container_width=True,
        column_config={
            "video_url": st.column_config.LinkColumn(
                "YouTube Video Link"
            )
        }
    )

    st.download_button(
        "Download Video Sources CSV",
        data=videos.to_csv(index=False),
        file_name="project1_video_sources.csv",
        mime="text/csv"
    )
else:
    st.warning(
        "The uploaded dataset does not contain "
        "valid YouTube video URLs."
    )


# ==========================================================
# COMBINED MARKETING RECOMMENDATIONS
# ==========================================================

st.markdown("### 5. Sentiment-Based Marketing Insights")

for recommendation in marketing_actions(sentiment_df):
    st.write("• " + recommendation)


# ==========================================================
# CONNECT TO PROJECT 2 BUDGET OPTIMIZER
# ==========================================================

st.divider()

st.markdown("### 6. Project 2 Budget Optimization")

st.write(
    "The sentiment results above support advertising "
    "creative decisions. The budget below is optimized "
    "using the advertising dataset and modeled "
    "platform performance."
)

ad_df = load_data_with_sidebar()

if ad_df.empty:
    st.warning(
        "No advertising records match your filters."
    )
    st.stop()

budget = st.number_input(
    "Total Advertising Budget (PKR)",
    min_value=10000,
    max_value=100000000,
    value=1000000,
    step=50000,
    key="integrated_budget"
)

try:
    allocation, totals = optimize_budget(
        ad_df,
        budget=budget
    )

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Marketing Budget",
        f"Rs. {totals['budget']:,.0f}"
    )

    c2.metric(
        "Model-Estimated ROAS",
        f"{totals['estimated_roas']:.2f}x"
    )

    c3.metric(
        "Analyzed Sentiment Comments",
        f"{len(sentiment_df):,}"
    )

    st.dataframe(
        allocation[
            [
                "platform",
                "allocation_pct",
                "recommended_budget",
                "estimated_revenue"
            ]
        ].round(2),
        hide_index=True,
        use_container_width=True
    )

    fig = px.pie(
        allocation,
        names="platform",
        values="recommended_budget",
        hole=0.60,
        title="Recommended Advertising Budget"
    )

    st.plotly_chart(
        style_chart(fig, 460),
        use_container_width=True
    )

    st.success(
        "Integration active: Project 1 provides "
        "customer-feedback insights and marketing "
        "creative recommendations. Project 2 provides "
        "advertising analytics and budget allocation."
    )

except (ValueError, RuntimeError) as exc:
    st.error(f"Budget optimization failed: {exc}")

st.download_button(
    "Download Sentiment Summary",
    data=summary.to_csv(index=False),
    file_name="project1_sentiment_summary.csv",
    mime="text/csv"
)

st.caption(
    "YouTube comments are not verified SHEIN purchases. "
    "Advertising revenue estimates are simulated. "
    "Do not interpret sentiment as proven platform ROAS."
)

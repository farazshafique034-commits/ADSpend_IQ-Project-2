"""Bridge between SHEIN Sentiment Analysis and AdSpend IQ."""

from pathlib import Path
from io import BytesIO
from collections import Counter
import json
import re
import zipfile

import pandas as pd

SAVED_CSV = Path(
    "data/processed/project1_sentiment_analyzed.csv"
)

LABELS = ("positive", "negative", "neutral", "mixed")

THEMES = {
    "Fit & sizing":
        r"\b(size|sizing|fit|fitting|tight|loose|small|large|length)\b",
    "Quality & fabric":
        r"\b(quality|fabric|material|stitch|stitching|seam|thin|cheap|transparent)\b",
    "Price & value":
        r"\b(price|cost|expensive|cheap|worth|value|money)\b",
    "Shipping":
        r"\b(shipping|delivery|deliver|late|delay|package|parcel)\b",
    "Style & appearance":
        r"\b(style|design|color|colour|cute|beautiful|pretty|look|looks)\b",
}


def normalize_sentiment(raw):
    """Validate and normalize Project 1 sentiment CSV."""

    df = raw.copy()
    df.columns = [
        str(c).strip().lower().replace(" ", "_")
        for c in df.columns
    ]

    aliases = {
        "sentiment": [
            "sentiment", "overall_sentiment",
            "final_sentiment", "sentiment_label",
            "predicted_sentiment"
        ],
        "clean_text": [
            "clean_text", "comment_text",
            "comment", "review", "text"
        ]
    }

    for standard, candidates in aliases.items():
        if standard not in df:
            match = next(
                (c for c in candidates if c in df),
                None
            )
            if match:
                df[standard] = df[match]

    if "sentiment" not in df:
        raise ValueError(
            "Sentiment column missing. Upload "
            "review_comments_analyzed.csv from Project 1."
        )

    if "clean_text" not in df:
        raise ValueError(
            "Comment text column missing."
        )

    df["sentiment"] = (
        df["sentiment"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.lower()
        .replace({
            "label_0": "negative",
            "label_1": "neutral",
            "label_2": "positive"
        })
    )

    if "is_mixed" in df:
        mixed = (
            df["is_mixed"]
            .astype(str)
            .str.lower()
            .isin(["true", "1", "yes"])
        )
        df.loc[mixed, "sentiment"] = "mixed"

    df["clean_text"] = (
        df["clean_text"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    df = df[
        df["sentiment"].isin(LABELS)
        & df["clean_text"].ne("")
    ].copy()

    if "comment_id" in df:
        df = df.drop_duplicates(subset=["comment_id"])
    else:
        df = df.drop_duplicates(subset=["clean_text"])

    if df.empty:
        raise ValueError(
            "No valid analyzed comments in CSV."
        )

    for col in [
        "video_title", "video_url",
        "segment_details_json"
    ]:
        if col not in df:
            df[col] = ""
        df[col] = df[col].fillna("").astype(str)

    for col in [
        "positive_segments",
        "negative_segments",
        "neutral_segments",
        "avg_model_confidence"
    ]:
        if col in df:
            df[col] = pd.to_numeric(
                df[col], errors="coerce"
            )

    return df.reset_index(drop=True)


def sentiment_summary(df):
    counts = (
        df["sentiment"]
        .value_counts()
        .reindex(LABELS, fill_value=0)
    )

    return pd.DataFrame({
        "sentiment": list(LABELS),
        "comments": counts.astype(int).to_numpy(),
        "percentage": (
            counts / len(df) * 100
        ).round(2).to_numpy()
    })


def negative_themes(df):
    """
    Count negative-segment keyword mentions.
    This is heuristic analysis, not a trained
    aspect-based sentiment model.
    """

    counter = Counter({
        key: 0 for key in THEMES
    })

    for row in df.itertuples(index=False):
        texts = []
        details = getattr(
            row, "segment_details_json", ""
        )

        if details:
            try:
                parts = json.loads(details)

                if isinstance(parts, list):
                    texts = [
                        str(part.get("text", ""))
                        for part in parts
                        if isinstance(part, dict)
                        and str(
                            part.get("sentiment", "")
                        ).lower() == "negative"
                    ]
            except (ValueError, TypeError):
                pass

        if (
            not texts
            and getattr(row, "sentiment") == "negative"
        ):
            texts = [str(getattr(row, "clean_text"))]

        for text in texts:
            for theme, pattern in THEMES.items():
                if re.search(
                    pattern, text, re.IGNORECASE
                ):
                    counter[theme] += 1

    result = pd.DataFrame([
        {
            "theme": theme,
            "negative_mentions": count
        }
        for theme, count in counter.items()
    ])

    return result.sort_values(
        "negative_mentions", ascending=False
    )


def source_videos(df):
    known = df[
        df["video_url"].str.startswith((
            "https://www.youtube.com/",
            "https://youtu.be/"
        ))
    ]

    if known.empty:
        return pd.DataFrame(columns=[
            "video_title", "video_url", "comments"
        ])

    return (
        known.groupby(
            ["video_title", "video_url"],
            dropna=False
        )
        .size()
        .reset_index(name="comments")
        .sort_values(
            "comments", ascending=False
        )
    )


def marketing_actions(df):
    summary = (
        sentiment_summary(df)
        .set_index("sentiment")["percentage"]
    )

    themes = negative_themes(df)

    recommendations = [
        "Use advertising ROAS and CPA for platform "
        "budget decisions. YouTube sentiment cannot "
        "establish which advertising platform converts best."
    ]

    if (
        not themes.empty
        and themes.iloc[0]["negative_mentions"] > 0
    ):
        top = themes.iloc[0]["theme"]

        recommendations.append(
            f"Test clearer advertising messages about "
            f"{top.lower()}. First manually review "
            "the relevant negative comments."
        )

    if summary["positive"] >= 40:
        recommendations.append(
            "Test positively discussed product features "
            "in advertising creatives, after verifying "
            "the comments and obtaining permission "
            "before quoting individuals."
        )

    if (
        summary["negative"] >= 30
        or summary["mixed"] >= 15
    ):
        recommendations.append(
            "Test expectation-setting advertising "
            "messages against regular creatives. "
            "Measure actual click and conversion results."
        )

    recommendations.append(
        "YouTube comments are exploratory social "
        "listening data, not verified buyer reviews."
    )

    return recommendations


def combined_report_zip(ad_report, sentiment_df):
    """Combine existing advertising reports and sentiment insights."""

    from utils.export import create_report_zip

    buffer = BytesIO(
        create_report_zip(ad_report)
    )

    summary = sentiment_summary(sentiment_df)
    themes = negative_themes(sentiment_df)
    videos = source_videos(sentiment_df)

    lines = [
        "ADSPEND IQ - INTEGRATED MARKETING REPORT",
        "",
        "PROJECT 1: SHEIN SENTIMENT ANALYSIS",
        f"Analyzed comments: {len(sentiment_df):,}",
        "",
        "PROJECT 2: DIGITAL ADVERTISING OPTIMIZER",
        "Platform budgets come from advertising "
        "performance and modeled response assumptions.",
        "",
        "MARKETING RECOMMENDATIONS:"
    ]

    lines.extend(
        "- " + action
        for action in marketing_actions(sentiment_df)
    )

    with zipfile.ZipFile(
        buffer, "a", zipfile.ZIP_DEFLATED
    ) as archive:

        archive.writestr(
            "project1_sentiment_summary.csv",
            summary.to_csv(index=False)
        )

        archive.writestr(
            "project1_negative_themes.csv",
            themes.to_csv(index=False)
        )

        archive.writestr(
            "project1_video_sources.csv",
            videos.to_csv(index=False)
        )

        archive.writestr(
            "integrated_marketing_brief.txt",
            "\n".join(lines)
        )

    return buffer.getvalue()

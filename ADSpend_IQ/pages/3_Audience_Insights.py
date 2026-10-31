import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

from components.theme import load_theme, render_hero
from components.sidebar import load_data_with_sidebar
from components.charts import style_chart

st.set_page_config(
    page_title="Audience Insights | AdSpend IQ",
    page_icon="🌍",
    layout="wide"
)

load_theme()

render_hero(
    "Audience Intelligence",
    "Explore advertising performance across cities, "
    "age groups, devices and demographic segments.",
    eyebrow="ADSPEND IQ / AUDIENCE INSIGHTS"
)

df = load_data_with_sidebar()

if df.empty:
    st.warning("No audience data matches the filters.")
    st.stop()


def aggregate(data, dimension):
    result = (
        data.groupby(dimension, observed=True, as_index=False)
        .agg(
            impressions=("impressions", "sum"),
            clicks=("clicks", "sum"),
            spend=("spend", "sum"),
            conversions=("conversions", "sum"),
            revenue=("revenue", "sum")
        )
    )

    result["roas"] = np.where(
        result["spend"] > 0,
        result["revenue"] / result["spend"],
        0
    )

    result["ctr"] = np.where(
        result["impressions"] > 0,
        result["clicks"] / result["impressions"] * 100,
        0
    )

    result["cvr"] = np.where(
        result["clicks"] > 0,
        result["conversions"] / result["clicks"] * 100,
        0
    )

    result["cpa"] = np.where(
        result["conversions"] > 0,
        result["spend"] / result["conversions"],
        0
    )

    return result


# SUMMARY

st.markdown("### Audience Performance Overview")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Cities", df["city"].nunique())
c2.metric("Device Types", df["device"].nunique())
c3.metric("Average Segment Age", f'{df["age"].mean():.1f}')
c4.metric(
    "Conversions",
    f'{df["conversions"].sum():,}'
)

st.caption(
    "Each record is a simulated audience segment, "
    "not a unique person or customer."
)

st.divider()

# CITY ANALYTICS

city = aggregate(df, "city")

left, right = st.columns(2)

with left:
    fig = px.bar(
        city.sort_values("revenue"),
        x="revenue",
        y="city",
        orientation="h",
        color="revenue",
        color_continuous_scale="Blues",
        title="Revenue by City"
    )

    fig.update_layout(coloraxis_showscale=False)

    st.plotly_chart(
        style_chart(fig, 470),
        use_container_width=True
    )

with right:
    fig = px.bar(
        city.sort_values("roas"),
        x="roas",
        y="city",
        orientation="h",
        color="roas",
        color_continuous_scale="Viridis",
        title="ROAS by City"
    )

    fig.update_layout(coloraxis_showscale=False)

    st.plotly_chart(
        style_chart(fig, 470),
        use_container_width=True
    )

# DEVICE ANALYTICS

st.markdown("### Device Performance")

device = aggregate(df, "device")

left, right = st.columns(2)

with left:
    fig = px.pie(
        device,
        names="device",
        values="impressions",
        hole=0.6,
        title="Impressions by Device"
    )

    st.plotly_chart(
        style_chart(fig, 440),
        use_container_width=True
    )

with right:
    fig = px.bar(
        device,
        x="device",
        y="cvr",
        color="device",
        title="Conversion Rate by Device"
    )

    fig.update_layout(showlegend=False)

    st.plotly_chart(
        style_chart(fig, 440),
        use_container_width=True
    )

# AGE SEGMENTATION

st.markdown("### Age Group Segmentation")

age_data = df.copy()

age_data["age_group"] = pd.cut(
    age_data["age"],
    bins=[17, 24, 34, 44, 54, 200],
    labels=[
        "18-24", "25-34", "35-44",
        "45-54", "55+"
    ]
)

age_perf = aggregate(age_data, "age_group")

left, right = st.columns(2)

with left:
    fig = px.bar(
        age_perf,
        x="age_group",
        y="conversions",
        color="age_group",
        title="Conversions by Age Group"
    )

    fig.update_layout(showlegend=False)

    st.plotly_chart(
        style_chart(fig, 440),
        use_container_width=True
    )

with right:
    fig = px.line(
        age_perf,
        x="age_group",
        y="roas",
        markers=True,
        title="ROAS by Age Group"
    )

    fig.update_traces(
        line=dict(color="#38BDF8", width=3),
        marker=dict(size=10)
    )

    st.plotly_chart(
        style_chart(fig, 440),
        use_container_width=True
    )

# GENDER ANALYTICS

st.markdown("### Gender Performance")

gender = aggregate(df, "gender")

left, right = st.columns(2)

with left:
    fig = px.bar(
        gender,
        x="gender",
        y="conversions",
        color="gender",
        title="Conversions by Gender"
    )

    st.plotly_chart(
        style_chart(fig, 430),
        use_container_width=True
    )

with right:
    fig = px.bar(
        gender,
        x="gender",
        y="roas",
        color="gender",
        title="ROAS by Gender"
    )

    st.plotly_chart(
        style_chart(fig, 430),
        use_container_width=True
    )

# CITY x DEVICE HEATMAP

st.markdown("### City and Device Performance Heatmap")

combined = (
    df.groupby(["city", "device"], as_index=False)
    .agg(
        spend=("spend", "sum"),
        revenue=("revenue", "sum")
    )
)

combined["roas"] = np.where(
    combined["spend"] > 0,
    combined["revenue"] / combined["spend"],
    0
)

pivot = combined.pivot(
    index="city",
    columns="device",
    values="roas"
)

fig = px.imshow(
    pivot,
    text_auto=".2f",
    color_continuous_scale="Blues",
    aspect="auto",
    title="City x Device ROAS Heatmap"
)

st.plotly_chart(
    style_chart(fig, 480),
    use_container_width=True
)

# CUSTOM AUDIENCE EXPLORER

st.markdown("### Interactive Audience Explorer")

dimension = st.selectbox(
    "Choose Audience Dimension",
    ["city", "device", "gender", "age_group"]
)

metric = st.selectbox(
    "Choose Performance Metric",
    [
        "revenue", "spend", "conversions",
        "roas", "ctr", "cvr", "cpa"
    ]
)

source = (
    age_data if dimension == "age_group" else df
)

explorer = aggregate(source, dimension)

fig = px.bar(
    explorer,
    x=dimension,
    y=metric,
    color=metric,
    color_continuous_scale="Blues",
    title=f"{metric.upper()} by {dimension}"
)

fig.update_layout(coloraxis_showscale=False)

st.plotly_chart(
    style_chart(fig, 460),
    use_container_width=True
)

# EXPORT

st.markdown("### Audience Analytics Table")

st.dataframe(
    explorer.round(2),
    use_container_width=True,
    hide_index=True
)

st.download_button(
    "Download Audience Analytics CSV",
    data=explorer.to_csv(index=False),
    file_name="audience_analytics.csv",
    mime="text/csv"
)

st.info(
    "Audience results are based on the selected "
    "dataset and should not be interpreted as "
    "verified individual customer behavior."
)

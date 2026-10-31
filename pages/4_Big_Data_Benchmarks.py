import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from components.theme import load_theme, render_hero
from components.charts import style_chart

from utils.benchmark import (
    run_local_benchmark,
    normalize_benchmarks
)


st.set_page_config(
    page_title="Big Data Benchmarks | AdSpend IQ",
    page_icon="⚡",
    layout="wide"
)

load_theme()

render_hero(
    "Big Data Processing Laboratory",
    "Benchmark data processing methods, visualize "
    "execution times and evaluate scalability.",
    eyebrow="ADSPEND IQ / BIG DATA ENGINEERING"
)

st.info(
    "This page benchmarks equivalent platform-level "
    "aggregations. Python MapReduce is a local "
    "algorithm demonstration, not Hadoop. "
    "PySpark results must be measured separately "
    "and imported from Google Colab."
)

# -----------------------------------------------------------
# DATA SOURCE
# -----------------------------------------------------------

st.markdown("### Benchmark Data Source")

source = st.radio(
    "Choose benchmark input",
    [
        "Run Local Benchmark",
        "Upload Colab Benchmark CSV"
    ],
    horizontal=True
)

bench = None

if source == "Run Local Benchmark":

    st.markdown("#### Select Dataset Sizes")

    sizes = st.multiselect(
        "Number of records",
        options=[10000, 25000, 50000, 100000],
        default=[10000, 50000, 100000],
        format_func=lambda x: f"{x:,} records"
    )

    repeats = st.slider(
        "Benchmark repetitions",
        min_value=1,
        max_value=5,
        value=3
    )

    st.caption(
        "Run small benchmarks locally. Large datasets "
        "such as 1M and 10M should be tested in Colab "
        "with appropriate memory management."
    )

    if st.button(
        "Run Benchmark",
        type="primary",
        use_container_width=True
    ):

        if not sizes:
            st.error("Select at least one dataset size.")

        else:
            with st.spinner(
                "Running real benchmark measurements..."
            ):
                try:
                    result = run_local_benchmark(
                        sizes=sizes,
                        repeats=repeats
                    )

                    st.session_state[
                        "benchmark_results"
                    ] = result

                except Exception as exc:
                    st.error(
                        f"Benchmark failed: {exc}"
                    )

    if "benchmark_results" in st.session_state:
        bench = st.session_state[
            "benchmark_results"
        ].copy()

else:

    uploaded = st.file_uploader(
        "Upload benchmark results from Google Colab",
        type=["csv"]
    )

    if uploaded is not None:
        try:
            bench = normalize_benchmarks(
                pd.read_csv(uploaded)
            )
            st.success(
                "Benchmark data loaded successfully."
            )

        except Exception as exc:
            st.error(str(exc))


# -----------------------------------------------------------
# EMPTY STATE
# -----------------------------------------------------------

if bench is None or bench.empty:
    st.markdown("### Expected Benchmark CSV Format")

    st.code(
        "dataset_size,method,time_seconds\n"
        "10000,Pandas,0.12\n"
        "10000,Python MapReduce,0.43\n"
        "10000,PySpark,1.80",
        language="text"
    )

    st.caption(
        "The numbers above demonstrate CSV structure "
        "only. They are NOT measured benchmark results."
    )

    st.stop()


bench = normalize_benchmarks(bench)

# -----------------------------------------------------------
# INTERACTIVE FILTERS
# -----------------------------------------------------------

st.markdown("### Benchmark Filters")

f1, f2 = st.columns(2)

with f1:
    methods = st.multiselect(
        "Processing Methods",
        sorted(bench["method"].unique()),
        default=sorted(bench["method"].unique())
    )

with f2:
    dataset_sizes = st.multiselect(
        "Dataset Sizes",
        sorted(bench["dataset_size"].unique()),
        default=sorted(bench["dataset_size"].unique()),
        format_func=lambda x: f"{x:,}"
    )

filtered = bench[
    bench["method"].isin(methods)
    & bench["dataset_size"].isin(dataset_sizes)
].copy()

if filtered.empty:
    st.warning("No benchmark records match the filters.")
    st.stop()

# -----------------------------------------------------------
# KPI CARDS
# -----------------------------------------------------------

st.markdown("### Benchmark Summary")

k1, k2, k3, k4 = st.columns(4)

k1.metric(
    "Methods Compared",
    filtered["method"].nunique()
)

k2.metric(
    "Largest Dataset",
    f'{filtered["dataset_size"].max():,}'
)

k3.metric(
    "Fastest Recorded Run",
    f'{filtered["time_seconds"].min():.4f} sec'
)

k4.metric(
    "Measurements Displayed",
    len(filtered)
)

st.divider()

# -----------------------------------------------------------
# CHART 1 - EXECUTION TIME
# -----------------------------------------------------------

st.markdown("### Processing Time Comparison")

fig = px.bar(
    filtered,
    x="dataset_size",
    y="time_seconds",
    color="method",
    barmode="group",
    title="Execution Time by Dataset Size",
    labels={
        "dataset_size": "Number of Records",
        "time_seconds": "Execution Time (seconds)",
        "method": "Processing Engine"
    },
    hover_data=[
        "throughput_rows_per_sec",
        "environment"
    ]
)

fig.update_xaxes(type="category")

st.plotly_chart(
    style_chart(fig, 500),
    use_container_width=True
)

# -----------------------------------------------------------
# CHART 2 - SCALABILITY CURVES
# -----------------------------------------------------------

st.markdown("### Processing Scalability")

fig = px.line(
    filtered.sort_values("dataset_size"),
    x="dataset_size",
    y="time_seconds",
    color="method",
    markers=True,
    title="Execution Time Growth with Dataset Size",
    labels={
        "dataset_size": "Dataset Size",
        "time_seconds": "Execution Time (seconds)"
    },
    hover_data=["environment"]
)

fig.update_traces(
    line=dict(width=3),
    marker=dict(size=10)
)

st.plotly_chart(
    style_chart(fig, 480),
    use_container_width=True
)

# -----------------------------------------------------------
# CHART 3 - THROUGHPUT COMPARISON
# -----------------------------------------------------------

st.markdown("### Data Processing Throughput")

fig = px.bar(
    filtered,
    x="dataset_size",
    y="throughput_rows_per_sec",
    color="method",
    barmode="group",
    title="Rows Processed per Second",
    labels={
        "dataset_size": "Dataset Size",
        "throughput_rows_per_sec": "Rows / Second"
    }
)

fig.update_xaxes(type="category")

st.plotly_chart(
    style_chart(fig, 480),
    use_container_width=True
)

# -----------------------------------------------------------
# CHART 4 - BENCHMARK HEATMAP
# -----------------------------------------------------------

st.markdown("### Execution Time Heatmap")

pivot = filtered.pivot_table(
    index="method",
    columns="dataset_size",
    values="time_seconds",
    aggfunc="median"
)

fig = px.imshow(
    pivot,
    text_auto=".3f",
    color_continuous_scale="Blues",
    aspect="auto",
    title="Median Execution Time by Engine and Size",
    labels={
        "x": "Dataset Size",
        "y": "Processing Method",
        "color": "Seconds"
    }
)

st.plotly_chart(
    style_chart(fig, 430),
    use_container_width=True
)

# -----------------------------------------------------------
# CHART 5 - SPEEDUP RELATIVE TO PANDAS
# -----------------------------------------------------------

st.markdown("### Relative Processing Speed")

# For duplicate measurements, compare median times.
comparison = (
    filtered.groupby(
        ["dataset_size", "method"],
        as_index=False
    )["time_seconds"]
    .median()
)

pandas_base = (
    comparison[
        comparison["method"] == "Pandas"
    ][["dataset_size", "time_seconds"]]
    .rename(
        columns={"time_seconds": "pandas_seconds"}
    )
)

speedup = comparison.merge(
    pandas_base,
    on="dataset_size",
    how="inner"
)

if not speedup.empty:

    speedup["speedup"] = (
        speedup["pandas_seconds"]
        / speedup["time_seconds"]
    )

    fig = px.bar(
        speedup,
        x="dataset_size",
        y="speedup",
        color="method",
        barmode="group",
        title="Speedup Relative to Pandas",
        labels={
            "speedup": "Speedup (x)",
            "dataset_size": "Dataset Size"
        }
    )

    fig.update_xaxes(type="category")

    fig.add_hline(
        y=1,
        line_dash="dash",
        line_color="#94A3B8"
    )

    st.plotly_chart(
        style_chart(fig, 480),
        use_container_width=True
    )

    st.caption(
        "Speedup above 1x means faster than the "
        "Pandas measurement for the same size. "
        "Compare runs from the same environment "
        "and equivalent operation for fair results."
    )

else:
    st.info(
        "Add Pandas measurements for matching dataset "
        "sizes to calculate relative speedup."
    )

# -----------------------------------------------------------
# CHART 6 - INTERACTIVE SIZE-SPECIFIC COMPARISON
# -----------------------------------------------------------

st.markdown("### Detailed Dataset Comparison")

selected_size = st.selectbox(
    "Choose a dataset size",
    sorted(filtered["dataset_size"].unique()),
    format_func=lambda x: f"{x:,} records"
)

detail = filtered[
    filtered["dataset_size"] == selected_size
].copy()

fig = px.bar(
    detail,
    x="method",
    y="time_seconds",
    color="method",
    title=f"Engine Comparison — {selected_size:,} Records",
    text="time_seconds"
)

fig.update_traces(
    texttemplate="%{text:.4f}s",
    textposition="outside"
)

fig.update_layout(showlegend=False)

st.plotly_chart(
    style_chart(fig, 440),
    use_container_width=True
)

# -----------------------------------------------------------
# RESULTS TABLE
# -----------------------------------------------------------

st.markdown("### Detailed Benchmark Results")

st.dataframe(
    filtered,
    use_container_width=True,
    hide_index=True
)

st.download_button(
    "Download Benchmark Results CSV",
    data=filtered.to_csv(index=False),
    file_name="adspend_benchmark_results.csv",
    mime="text/csv",
    use_container_width=True
)

# -----------------------------------------------------------
# AUTOMATIC SUMMARY
# -----------------------------------------------------------

st.markdown("### Performance Interpretation")

largest_size = filtered["dataset_size"].max()

largest_results = filtered[
    filtered["dataset_size"] == largest_size
].sort_values("time_seconds")

fastest = largest_results.iloc[0]

st.success(
    f"For the largest selected dataset "
    f"({largest_size:,} records), "
    f"{fastest['method']} recorded the lowest "
    f"execution time of "
    f"{fastest['time_seconds']:.4f} seconds."
)

st.warning(
    "Results measure the specified aggregation only. "
    "Performance depends on hardware, available memory, "
    "execution environment, startup overhead and engine "
    "configuration. Imported measurements should be "
    "compared only when experimental conditions are "
    "equivalent."
)

st.caption(
    "AdSpend IQ | Big Data Benchmark Laboratory | "
    "Pandas vs Python MapReduce vs Apache Spark"
)

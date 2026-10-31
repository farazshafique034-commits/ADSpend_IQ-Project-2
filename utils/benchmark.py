import time
import gc

import numpy as np
import pandas as pd

from utils.data_generator import generate_ad_data


METRICS = [
    "impressions",
    "clicks",
    "spend",
    "conversions",
    "revenue"
]


def pandas_aggregation(df):
    """
    Aggregate advertising data by platform using Pandas.
    """

    result = (
        df.groupby("platform")[METRICS]
        .sum()
        .sort_index()
    )

    return result


def python_mapreduce_aggregation(df):
    """
    Demonstrate MapReduce using pure Python.

    Map:
        Convert each record into a platform/key
        and numeric metric values.

    Reduce:
        Combine metric totals for each platform.

    This is a single-process teaching implementation.
    It is NOT a distributed Hadoop benchmark.
    """

    totals = {}

    columns = [
        "platform",
        "impressions",
        "clicks",
        "spend",
        "conversions",
        "revenue"
    ]

    for row in df[columns].itertuples(
        index=False, name=None
    ):
        platform = row[0]

        if platform not in totals:
            totals[platform] = [0.0] * 5

        for index, value in enumerate(row[1:]):
            totals[platform][index] += float(value)

    result = pd.DataFrame.from_dict(
        totals,
        orient="index",
        columns=METRICS
    )

    result.index.name = "platform"

    return result.sort_index()


def results_match(pandas_result, mapreduce_result):
    """
    Verify both engines produce matching totals.
    """

    a = pandas_result.sort_index()
    b = mapreduce_result.reindex(a.index)

    if b.isna().any().any():
        return False

    return bool(
        np.allclose(
            a[METRICS].to_numpy(dtype=float),
            b[METRICS].to_numpy(dtype=float),
            rtol=1e-8,
            atol=0.05
        )
    )


def benchmark_function(func, df, repeats=3):
    """
    Measure aggregation time using perf_counter.

    Data generation and file loading are excluded.
    """

    times = []
    output = None

    for _ in range(repeats):
        gc.collect()

        start = time.perf_counter()

        output = func(df)

        elapsed = time.perf_counter() - start

        times.append(elapsed)

    return {
        "time_seconds": float(np.median(times)),
        "min_seconds": float(min(times)),
        "max_seconds": float(max(times)),
        "result": output
    }


def run_local_benchmark(
    sizes=(10000, 50000, 100000),
    repeats=3
):
    """
    Run fair local aggregation comparisons.

    Both methods receive the same generated DataFrame
    and produce the same platform-level totals.
    """

    records = []

    for size in sizes:
        size = int(size)

        # Generate outside the timed portion.
        df = generate_ad_data(size, seed=42)

        pandas_run = benchmark_function(
            pandas_aggregation,
            df,
            repeats
        )

        mapreduce_run = benchmark_function(
            python_mapreduce_aggregation,
            df,
            repeats
        )

        valid = results_match(
            pandas_run["result"],
            mapreduce_run["result"]
        )

        if not valid:
            raise ValueError(
                f"Aggregation mismatch for {size} rows."
            )

        for method, result in [
            ("Pandas", pandas_run),
            ("Python MapReduce", mapreduce_run)
        ]:
            seconds = result["time_seconds"]

            records.append({
                "dataset_size": size,
                "method": method,
                "time_seconds": seconds,
                "throughput_rows_per_sec": (
                    size / seconds if seconds > 0 else 0
                ),
                "min_seconds": result["min_seconds"],
                "max_seconds": result["max_seconds"],
                "correctness_verified": True,
                "environment": "Local Streamlit",
                "notes": (
                    "Platform aggregation; warm-process "
                    "median of repeated runs"
                )
            })

        del df
        gc.collect()

    return pd.DataFrame(records)


def normalize_benchmarks(df):
    """
    Standardize benchmark CSV column names.

    Requires:
        dataset_size, method, time_seconds

    Accepts common aliases.
    """

    data = df.copy()

    data.columns = [
        str(c).strip().lower().replace(" ", "_")
        for c in data.columns
    ]

    aliases = {
        "rows": "dataset_size",
        "n_rows": "dataset_size",
        "records": "dataset_size",
        "size": "dataset_size",
        "engine": "method",
        "framework": "method",
        "processing_method": "method",
        "execution_time": "time_seconds",
        "execution_time_seconds": "time_seconds",
        "elapsed_seconds": "time_seconds",
        "duration_seconds": "time_seconds"
    }

    data = data.rename(columns={
        old: new
        for old, new in aliases.items()
        if old in data.columns
        and new not in data.columns
    })

    required = [
        "dataset_size",
        "method",
        "time_seconds"
    ]

    missing = [
        c for c in required
        if c not in data.columns
    ]

    if missing:
        raise ValueError(
            "Benchmark CSV needs columns: "
            + ", ".join(required)
        )

    data["dataset_size"] = pd.to_numeric(
        data["dataset_size"], errors="coerce"
    )

    data["time_seconds"] = pd.to_numeric(
        data["time_seconds"], errors="coerce"
    )

    data["method"] = (
        data["method"].astype(str).str.strip()
    )

    valid = (
        data["dataset_size"].notna()
        & (data["dataset_size"] > 0)
        & data["time_seconds"].notna()
        & (data["time_seconds"] > 0)
        & data["method"].ne("")
    )

    data = data.loc[valid].copy()

    if data.empty:
        raise ValueError(
            "No valid benchmark results found."
        )

    data["dataset_size"] = (
        data["dataset_size"].astype(int)
    )

    data["throughput_rows_per_sec"] = (
        data["dataset_size"] / data["time_seconds"]
    )

    if "environment" not in data.columns:
        data["environment"] = "Not specified"

    if "correctness_verified" not in data.columns:
        data["correctness_verified"] = "Not reported"

    if "notes" not in data.columns:
        data["notes"] = ""

    return data.sort_values(
        ["dataset_size", "method"]
    ).reset_index(drop=True)

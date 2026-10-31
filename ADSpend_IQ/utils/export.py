import io
import json
import html
import zipfile

import pandas as pd

from datetime import datetime

from utils.metrics import (
    calculate_kpis,
    platform_performance,
    campaign_performance
)

from utils.optimizer import optimize_budget


def build_report_data(df, budget=1_000_000):
    """
    Prepare validated summaries for all report formats.
    """

    if df.empty:
        raise ValueError("Cannot report on empty data.")

    kpis = calculate_kpis(df)

    platforms = platform_performance(df)
    campaigns = campaign_performance(df)

    allocation, optimizer_summary = optimize_budget(
        df, budget=budget
    )

    return {
        "kpis": kpis,
        "platforms": platforms,
        "campaigns": campaigns,
        "allocation": allocation,
        "optimizer_summary": optimizer_summary,
        "generated_at": datetime.now().isoformat(
            timespec="seconds"
        )
    }


def report_json(report):
    """
    Export report summary as JSON.
    """

    data = {
        "generated_at": report["generated_at"],
        "dataset_type": "Synthetic / user-supplied",
        "marketing_kpis": report["kpis"],
        "budget_optimization": report["optimizer_summary"],
        "platform_performance": report[
            "platforms"
        ].to_dict(orient="records"),
        "budget_allocation": report[
            "allocation"
        ].to_dict(orient="records")
    }

    return json.dumps(
        data, indent=2, default=str
    )


def report_html(report):
    """
    Produce a standalone, printable HTML report.
    Can be saved as PDF using a browser print dialog.
    """

    kpis = report["kpis"]
    opt = report["optimizer_summary"]

    def fmt_money(number):
        return f"Rs. {number:,.0f}"

    def html_table(data, columns):
        clean = data[columns].copy()

        for column in clean.columns:
            if pd.api.types.is_numeric_dtype(clean[column]):
                clean[column] = clean[column].map(
                    lambda v: f"{v:,.2f}"
                    if pd.notna(v) else "-"
                )

        return clean.to_html(
            index=False,
            classes="data-table",
            border=0,
            escape=True
        )

    platform_columns = [
        "platform", "spend", "revenue",
        "conversions", "ctr", "cpa", "roas"
    ]

    budget_columns = [
        "platform", "allocation_pct",
        "recommended_budget",
        "estimated_revenue", "estimated_roas"
    ]

    platform_table = html_table(
        report["platforms"],
        platform_columns
    )

    budget_table = html_table(
        report["allocation"],
        budget_columns
    )

    generated = html.escape(report["generated_at"])

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport"
      content="width=device-width, initial-scale=1">
<title>AdSpend IQ - Marketing Report</title>
<style>
* {{
    box-sizing: border-box;
}}
body {{
    font-family: Arial, sans-serif;
    background: #f1f5f9;
    color: #172337;
    margin: 0;
    line-height: 1.6;
}}
.container {{
    max-width: 1100px;
    background: #fff;
    margin: 35px auto;
    padding: 40px;
    border-radius: 14px;
}}
.header {{
    background: #11223e;
    color: #fff;
    padding: 28px;
    border-radius: 12px;
    margin-bottom: 24px;
}}
.header h1 {{
    margin: 0;
    font-size: 28px;
}}
.header p {{
    color: #c4d6ef;
    margin-bottom: 0;
}}
.grid {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 14px;
}}
.card {{
    background: #edf5ff;
    border: 1px solid #d1e2fa;
    border-radius: 10px;
    padding: 18px;
}}
.card small {{
    color: #53647d;
}}
.card strong {{
    display: block;
    font-size: 22px;
    margin-top: 5px;
}}
h2 {{
    color: #15345e;
    border-bottom: 2px solid #dce7f5;
    padding-bottom: 7px;
    margin-top: 34px;
}}
table {{
    border-collapse: collapse;
    width: 100%;
    font-size: 12px;
    margin-top: 16px;
}}
th, td {{
    padding: 10px;
    border: 1px solid #dbe4ef;
    text-align: left;
}}
th {{
    background: #142b4a;
    color: white;
}}
tr:nth-child(even) {{
    background: #f4f8fc;
}}
.notice {{
    background: #fff7e6;
    border-left: 4px solid #f59e0b;
    padding: 15px;
    margin-top: 25px;
}}
.footer {{
    margin-top: 35px;
    padding-top: 12px;
    border-top: 1px solid #ddd;
    color: #64748b;
    font-size: 12px;
}}
@media print {{
    body {{ background: white; }}
    .container {{
        padding: 10px;
        margin: 0;
        max-width: none;
    }}
    .header, th {{
        print-color-adjust: exact;
        -webkit-print-color-adjust: exact;
    }}
    tr, .card {{ break-inside: avoid; }}
}}
</style>
</head>
<body>
<div class="container">
    <div class="header">
        <h1>AdSpend IQ</h1>
        <p>Digital Advertising Performance
           & Budget Optimization Report</p>
        <p>Generated: {generated}</p>
    </div>

    <h2>Executive Summary</h2>
    <div class="grid">
        <div class="card">
            <small>Historical Ad Spend</small>
            <strong>{fmt_money(kpis["spend"])}</strong>
        </div>
        <div class="card">
            <small>Attributed Revenue</small>
            <strong>{fmt_money(kpis["revenue"])}</strong>
        </div>
        <div class="card">
            <small>Historical ROAS</small>
            <strong>{kpis["roas"]:.2f}x</strong>
        </div>
        <div class="card">
            <small>Conversions</small>
            <strong>{kpis["conversions"]:,}</strong>
        </div>
        <div class="card">
            <small>Click-Through Rate</small>
            <strong>{kpis["ctr"]:.2f}%</strong>
        </div>
        <div class="card">
            <small>Conversion Rate</small>
            <strong>{kpis["conversion_rate"]:.2f}%</strong>
        </div>
    </div>

    <h2>Platform Performance</h2>
    <p>Aggregated platform-level metrics calculated
       from the selected advertising records.</p>
    {platform_table}

    <h2>Budget Recommendation</h2>
    <p>
        Proposed advertising budget:
        <strong>{fmt_money(opt["budget"])}</strong>
    </p>
    <p>
        Scenario-estimated revenue:
        <strong>
            {fmt_money(opt["estimated_revenue"])}
        </strong>
    </p>
    <p>
        Scenario-estimated ROAS:
        <strong>{opt["estimated_roas"]:.2f}x</strong>
    </p>
    <p>
        Estimated revenue change from the historical
        allocation mix:
        <strong>
            {opt["estimated_revenue_change_pct"]:+.2f}%
        </strong>
    </p>
    {budget_table}

    <h2>Methodology</h2>
    <p>
        The system aggregates advertising impressions,
        clicks, spend, conversions and attributed
        revenue by platform and campaign. KPI ratios
        are calculated from aggregated totals.
    </p>
    <p>
        A constrained optimization model recommends
        an advertising budget split. The model uses
        historical ROAS and a hypothetical diminishing
        returns curve, with allocation limits.
    </p>

    <h2>Management Interpretation</h2>
    <p>
        Recommended allocations are intended to support
        scenario exploration. Results should be reviewed
        against actual campaign data, conversion quality,
        business margins and platform spending capacity
        before any real marketing investment.
    </p>

    <div class="notice">
        <strong>Data & Forecast Limitations</strong>
        <p>
            Demo data is synthetic. User-uploaded data
            is not independently verified. Revenue
            projections are model-based estimates
            and do not guarantee actual financial
            performance. Revenue minus ad spend
            is not net profit.
        </p>
    </div>

    <div class="footer">
        AdSpend IQ | Big Data Analytics Project 2
        | Digital Advertising Budget Optimizer
    </div>
</div>
</body>
</html>"""


def create_report_zip(report):
    """
    Package all available report outputs in a ZIP.
    """

    memory = io.BytesIO()

    with zipfile.ZipFile(
        memory, "w", zipfile.ZIP_DEFLATED
    ) as archive:

        archive.writestr(
            "executive_report.html",
            report_html(report)
        )

        archive.writestr(
            "report_summary.json",
            report_json(report)
        )

        archive.writestr(
            "platform_performance.csv",
            report["platforms"].to_csv(index=False)
        )

        archive.writestr(
            "campaign_performance.csv",
            report["campaigns"].to_csv(index=False)
        )

        archive.writestr(
            "budget_recommendations.csv",
            report["allocation"].to_csv(index=False)
        )

    memory.seek(0)

    return memory.getvalue()

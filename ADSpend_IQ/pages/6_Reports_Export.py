import streamlit as st
import pandas as pd

from components.theme import load_theme, render_hero
from components.sidebar import load_data_with_sidebar

from utils.export import (
    build_report_data,
    report_html,
    report_json,
    create_report_zip
)

st.set_page_config(
    page_title="Reports & Export | AdSpend IQ",
    page_icon="📄",
    layout="wide"
)

load_theme()

render_hero(
    "Professional Reporting Center",
    "Generate management summaries, export "
    "marketing analytics and download budget "
    "recommendation reports.",
    eyebrow="ADSPEND IQ / REPORTING CENTER"
)

df = load_data_with_sidebar()

if df.empty:
    st.warning("No data available for reporting.")
    st.stop()

st.markdown("### Report Configuration")

budget = st.number_input(
    "Budget for Recommendation Report (PKR)",
    min_value=10000,
    max_value=100000000,
    value=1000000,
    step=50000
)

st.caption(
    f"Current filtered dataset: {len(df):,} records."
)

try:
    report = build_report_data(
        df, budget=budget
    )
except Exception as exc:
    st.error(f"Report generation failed: {exc}")
    st.stop()

kpis = report["kpis"]
opt = report["optimizer_summary"]

# ==========================================================
# EXECUTIVE SUMMARY
# ==========================================================

st.markdown("### Report Preview")

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Historical Spend",
    f'Rs. {kpis["spend"]:,.0f}'
)

c2.metric(
    "Historical Revenue",
    f'Rs. {kpis["revenue"]:,.0f}'
)

c3.metric(
    "Historical ROAS",
    f'{kpis["roas"]:.2f}x'
)

c4.metric(
    "Estimated Optimized ROAS",
    f'{opt["estimated_roas"]:.2f}x'
)

st.divider()

# ==========================================================
# PLATFORM REPORT
# ==========================================================

st.markdown("### Platform Performance")

st.dataframe(
    report["platforms"].round(2),
    hide_index=True,
    use_container_width=True
)

st.download_button(
    "Download Platform CSV",
    data=report["platforms"].to_csv(index=False),
    file_name="platform_performance.csv",
    mime="text/csv",
    use_container_width=True
)

# ==========================================================
# CAMPAIGN REPORT
# ==========================================================

st.markdown("### Campaign Performance")

st.dataframe(
    report["campaigns"].round(2),
    hide_index=True,
    use_container_width=True
)

st.download_button(
    "Download Campaign CSV",
    data=report["campaigns"].to_csv(index=False),
    file_name="campaign_performance.csv",
    mime="text/csv",
    use_container_width=True
)

# ==========================================================
# OPTIMIZER REPORT
# ==========================================================

st.markdown("### Budget Recommendation")

st.dataframe(
    report["allocation"].round(2),
    hide_index=True,
    use_container_width=True
)

st.download_button(
    "Download Budget Recommendation CSV",
    data=report["allocation"].to_csv(index=False),
    file_name="budget_recommendations.csv",
    mime="text/csv",
    use_container_width=True
)

st.divider()

# ==========================================================
# FINAL REPORT DOWNLOADS
# ==========================================================

st.markdown("### Download Executive Reports")

left, right = st.columns(2)

with left:
    st.download_button(
        "Download Printable HTML Report",
        data=report_html(report),
        file_name="AdSpend_IQ_Executive_Report.html",
        mime="text/html",
        use_container_width=True
    )

with right:
    st.download_button(
        "Download JSON Summary",
        data=report_json(report),
        file_name="AdSpend_IQ_Report.json",
        mime="application/json",
        use_container_width=True
    )

st.markdown("### Complete Report Package")

st.download_button(
    "Download Complete Reports ZIP",
    data=create_report_zip(report),
    file_name="AdSpend_IQ_Reports.zip",
    mime="application/zip",
    type="primary",
    use_container_width=True
)

st.info(
    "For a PDF report: download the HTML report, "
    "open it in Chrome or Edge, press Ctrl+P "
    "and select Save as PDF."
)

st.warning(
    "This report reflects the selected dataset. "
    "Synthetic data and modeled allocations must "
    "not be presented as real historical outcomes "
    "or guaranteed future earnings."
)

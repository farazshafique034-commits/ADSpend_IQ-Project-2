from pathlib import Path
import streamlit as st


def load_theme():
    css_path = (
        Path(__file__).resolve().parent.parent
        / "assets" / "css" / "style.css"
    )

    if css_path.exists():
        css = css_path.read_text(encoding="utf-8")
        st.markdown(
            f"<style>{css}</style>",
            unsafe_allow_html=True
        )


def render_hero(title, subtitle, eyebrow="ADSPEND IQ"):
    import html

    st.markdown(
        f"""
        <div class="hero">
            <div class="hero-eyebrow">
                {html.escape(eyebrow)}
            </div>
            <div class="hero-title">
                {html.escape(title)}
            </div>
            <div class="hero-subtitle">
                {html.escape(subtitle)}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

"""
🔍 Image Authenticity Detector
Streamlit app for detecting spoof vs real images.
"""

import streamlit as st
from ui.layout import render_page
from ui.state import init_session_state


# ── Page Configuration ──────────────────────────────────────────────
st.set_page_config(
    page_title="Image Authenticity Detector",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def main():
    """Entry point for the Streamlit application."""
    init_session_state()
    render_page()


if __name__ == "__main__":
    main()

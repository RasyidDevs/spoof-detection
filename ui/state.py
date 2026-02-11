"""
Session state initialization and management.
"""

import streamlit as st


def init_session_state():
    """Initialize all session state variables with defaults."""
    defaults = {
        "uploaded_files": [],
        "results": {},        # {filename: {"label": str, "confidence": float, "details": dict}}
        "is_processing": False,
        "processed_count": 0,
        "show_results": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_results():
    """Clear all prediction results."""
    st.session_state.results = {}
    st.session_state.processed_count = 0
    st.session_state.show_results = False


def set_processing(state: bool):
    """Toggle the processing state."""
    st.session_state.is_processing = state


def add_result(filename: str, result: dict):
    """Store a prediction result for a file."""
    st.session_state.results[filename] = result
    st.session_state.processed_count += 1

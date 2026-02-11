"""
Main page layout and rendering logic.
"""

from __future__ import annotations

import streamlit as st

from ui.styles import get_custom_css
from ui.components import (
    hero_section,
    upload_zone_label,
    section_header,
    stats_bar,
    result_card,
    image_preview_card,
    footer,
)
from ui.image_utils import (
    ALLOWED_TYPES,
    file_to_base64,
    get_mime_type,
    format_file_size,
)
from ui.state import reset_results, set_processing, add_result
from inference import predict


# ── Rendering Functions ──────────────────────────────────────────────


def render_page():
    """Render the full page layout."""
    _inject_styles()
    _render_hero()
    _render_uploader()
    _render_preview_and_controls()
    _render_results()
    _render_footer()


def _inject_styles():
    """Inject custom CSS into the page."""
    st.markdown(get_custom_css(), unsafe_allow_html=True)


def _render_hero():
    """Render the hero / header section."""
    st.markdown(hero_section(), unsafe_allow_html=True)


def _render_uploader():
    """Render the drag-and-drop file uploader."""
    st.markdown(upload_zone_label(), unsafe_allow_html=True)

    uploaded_files = st.file_uploader(
        label="Upload images",
        type=ALLOWED_TYPES,
        accept_multiple_files=True,
        label_visibility="collapsed",
        key="file_uploader",
    )

    if uploaded_files:
        st.session_state.uploaded_files = uploaded_files
    else:
        st.session_state.uploaded_files = []
        reset_results()


def _render_preview_and_controls():
    """Render image previews and the analyze button."""
    files = st.session_state.uploaded_files

    if not files:
        return

    # ── Preview Grid ─────────────────────────────────────────
    st.markdown(
        section_header("🖼️", "Uploaded Images", len(files)),
        unsafe_allow_html=True,
    )

    cols_per_row = 4
    for row_start in range(0, len(files), cols_per_row):
        row_files = files[row_start : row_start + cols_per_row]
        cols = st.columns(cols_per_row)

        for col, f in zip(cols, row_files):
            with col:
                b64 = file_to_base64(f)
                mime = get_mime_type(f)
                st.markdown(
                    image_preview_card(b64, f.name, mime),
                    unsafe_allow_html=True,
                )
                size_str = format_file_size(f.size)
                st.caption(f"📎 {size_str}")

    # ── Analyze Button ───────────────────────────────────────
    st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)

    col_l, col_btn, col_r = st.columns([1, 2, 1])
    with col_btn:
        analyze_clicked = st.button(
            f"🔍  Analyze {len(files)} Image{'s' if len(files) > 1 else ''}",
            use_container_width=True,
            type="primary",
        )

    if analyze_clicked:
        _run_analysis(files)


def _run_analysis(files):
    """Execute inference on all uploaded files with a progress bar."""
    reset_results()
    set_processing(True)

    progress_bar = st.progress(0, text="Initializing analysis…")
    total = len(files)

    for idx, f in enumerate(files):
        progress_bar.progress(
            (idx) / total,
            text=f"Analyzing {f.name} ({idx + 1}/{total})…",
        )

        result = predict(f)
        add_result(f.name, result)

    progress_bar.progress(1.0, text="✅ Analysis complete!")
    set_processing(False)
    st.session_state.show_results = True


def _render_results():
    """Render prediction result cards and summary stats."""
    if not st.session_state.show_results:
        return

    results = st.session_state.results
    files = st.session_state.uploaded_files

    if not results:
        return

    # ── Summary Stats ────────────────────────────────────────
    real_count = sum(1 for r in results.values() if r["label"].lower() == "real")
    spoof_count = len(results) - real_count

    st.markdown(
        section_header("📊", "Analysis Results", len(results)),
        unsafe_allow_html=True,
    )
    st.markdown(
        stats_bar(len(results), real_count, spoof_count),
        unsafe_allow_html=True,
    )

    # ── Result Cards Grid ────────────────────────────────────
    cols_per_row = 4
    file_map = {f.name: f for f in files}

    result_items = list(results.items())
    for row_start in range(0, len(result_items), cols_per_row):
        row = result_items[row_start : row_start + cols_per_row]
        cols = st.columns(cols_per_row)

        for col, (filename, result) in zip(cols, row):
            with col:
                f = file_map.get(filename)
                if f is None:
                    continue

                b64 = file_to_base64(f)
                mime = get_mime_type(f)
                st.markdown(
                    result_card(
                        image_b64=b64,
                        filename=filename,
                        label=result["label"],
                        confidence=result["confidence"],
                        mime_type=mime,
                    ),
                    unsafe_allow_html=True,
                )


def _render_footer():
    """Render the page footer."""
    st.markdown(footer(), unsafe_allow_html=True)

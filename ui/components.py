"""
Reusable HTML components for rendering UI elements.
"""

from __future__ import annotations


def hero_section() -> str:
    """Render the hero / header section."""
    return """
    <div class="hero-container fade-in-up">
        <div class="hero-badge">🛡️ AI-POWERED DETECTION</div>
        <h1 class="hero-title">Image Authenticity<br>Detector</h1>
        <p class="hero-subtitle">
            Upload images to detect whether they are <strong style="color:#10b981;">genuine</strong>
            or <strong style="color:#ef4444;">spoofed</strong>.
            Supports batch analysis with drag & drop.
        </p>
    </div>
    """


def upload_zone_label() -> str:
    """Render the styled upload zone label above the uploader."""
    return """
    <div style="text-align:center; margin-bottom: -0.5rem;">
        <span class="upload-icon">📂</span>
        <div class="upload-title">Drop images here or click to browse</div>
        <div class="upload-hint">PNG · JPG · JPEG · WEBP — multiple files supported</div>
    </div>
    """


def section_header(icon: str, title: str, count: int | None = None) -> str:
    """Render a section header with optional count badge."""
    count_html = (
        f'<span class="section-count">{count}</span>' if count is not None else ""
    )
    return f"""
    <div class="section-header">
        <span style="font-size:1.3rem;">{icon}</span>
        <h3>{title}</h3>
        {count_html}
    </div>
    """


def stats_bar(total: int, real_count: int, spoof_count: int) -> str:
    """Render the summary statistics bar."""
    return f"""
    <div class="stats-bar">
        <div class="stat-chip">
            📊 Total <span class="stat-value">{total}</span>
        </div>
        <div class="stat-chip real-chip">
            ✅ Real <span class="stat-value">{real_count}</span>
        </div>
        <div class="stat-chip spoof-chip">
            ⚠️ Spoof <span class="stat-value">{spoof_count}</span>
        </div>
    </div>
    """


def result_card(
    image_b64: str,
    filename: str,
    label: str,
    confidence: float,
    mime_type: str = "image/png",
) -> str:
    """
    Render a single result card with image, label, and confidence bar.

    Args:
        image_b64: Base64-encoded image string.
        filename: Original filename.
        label: 'real' or 'spoof'.
        confidence: Confidence score between 0.0 and 1.0.
        mime_type: MIME type of the image.
    """
    label_lower = label.lower()
    label_display = "AUTHENTIC" if label_lower == "real" else "SPOOFED"
    icon = "✅" if label_lower == "real" else "⚠️"
    pct = int(confidence * 100)

    return f"""
    <div class="result-card {label_lower} fade-in-up">
        <div class="result-header {label_lower}">
            <span class="result-label {label_lower}">{icon} {label_display}</span>
            <span class="result-confidence">{pct}%</span>
        </div>
        <img class="result-image" src="data:{mime_type};base64,{image_b64}" alt="{filename}" />
        <div class="result-body">
            <div class="result-filename" title="{filename}">{filename}</div>
            <div class="confidence-bar-bg">
                <div class="confidence-bar-fill {label_lower}" style="width:{pct}%;"></div>
            </div>
        </div>
    </div>
    """


def image_preview_card(image_b64: str, filename: str, mime_type: str = "image/png") -> str:
    """Render a preview card for an uploaded (but not yet analyzed) image."""
    return f"""
    <div class="image-card fade-in-up">
        <img src="data:{mime_type};base64,{image_b64}" alt="{filename}" />
        <div class="image-card-body">
            <div class="image-card-name" title="{filename}">{filename}</div>
        </div>
    </div>
    """


def footer() -> str:
    """Render the app footer."""
    return """
    <div class="app-footer">
        <p>🛡️ Image Authenticity Detector — Built with Streamlit</p>
    </div>
    """

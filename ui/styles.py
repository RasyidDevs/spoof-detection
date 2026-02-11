"""
Custom CSS styles for the application.
"""


def get_custom_css() -> str:
    """Return the full custom CSS for the app."""
    return """
    <style>
    /* ── Import Fonts ─────────────────────────────────────────── */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

    /* ── CSS Variables ────────────────────────────────────────── */
    :root {
        --bg-primary: #0a0e17;
        --bg-secondary: #111827;
        --bg-card: #1a2234;
        --bg-card-hover: #1e2a40;
        --border-color: #2a3550;
        --border-accent: #3b82f6;
        --text-primary: #f1f5f9;
        --text-secondary: #94a3b8;
        --text-muted: #64748b;
        --accent-blue: #3b82f6;
        --accent-cyan: #06b6d4;
        --accent-green: #10b981;
        --accent-red: #ef4444;
        --accent-amber: #f59e0b;
        --gradient-hero: linear-gradient(135deg, #3b82f6 0%, #06b6d4 50%, #10b981 100%);
        --gradient-card: linear-gradient(145deg, #1a2234 0%, #111827 100%);
        --shadow-glow: 0 0 30px rgba(59, 130, 246, 0.15);
        --shadow-card: 0 4px 24px rgba(0, 0, 0, 0.3);
        --radius-lg: 16px;
        --radius-md: 12px;
        --radius-sm: 8px;
    }

    /* ── Global Overrides ─────────────────────────────────────── */
    .stApp {
        background: var(--bg-primary) !important;
        font-family: 'Outfit', sans-serif !important;
    }

    .stApp header { background: transparent !important; }

    .block-container {
        padding-top: 2rem !important;
        max-width: 1200px !important;
    }

    /* ── Hero Section ─────────────────────────────────────────── */
    .hero-container {
        text-align: center;
        padding: 2.5rem 1rem 1.5rem;
        position: relative;
    }

    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(59, 130, 246, 0.1);
        border: 1px solid rgba(59, 130, 246, 0.25);
        color: var(--accent-blue);
        padding: 6px 16px;
        border-radius: 999px;
        font-size: 0.8rem;
        font-weight: 500;
        letter-spacing: 0.5px;
        margin-bottom: 1.2rem;
        font-family: 'JetBrains Mono', monospace;
    }

    .hero-title {
        font-family: 'Outfit', sans-serif;
        font-size: 3rem;
        font-weight: 800;
        background: var(--gradient-hero);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        line-height: 1.15;
        margin-bottom: 0.8rem;
        letter-spacing: -0.5px;
    }

    .hero-subtitle {
        color: var(--text-secondary);
        font-size: 1.1rem;
        font-weight: 300;
        max-width: 600px;
        margin: 0 auto;
        line-height: 1.6;
    }

    /* ── Upload Zone ──────────────────────────────────────────── */
    .upload-zone {
        background: var(--gradient-card);
        border: 2px dashed var(--border-color);
        border-radius: var(--radius-lg);
        padding: 3rem 2rem;
        text-align: center;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
        margin: 1.5rem 0;
    }

    .upload-zone::before {
        content: '';
        position: absolute;
        inset: 0;
        background: radial-gradient(
            600px circle at var(--mouse-x, 50%) var(--mouse-y, 50%),
            rgba(59, 130, 246, 0.06),
            transparent 40%
        );
        pointer-events: none;
    }

    .upload-zone:hover {
        border-color: var(--accent-blue);
        box-shadow: var(--shadow-glow);
    }

    .upload-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
        display: block;
    }

    .upload-title {
        font-family: 'Outfit', sans-serif;
        font-size: 1.25rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 0.4rem;
    }

    .upload-hint {
        color: var(--text-muted);
        font-size: 0.85rem;
        font-family: 'JetBrains Mono', monospace;
    }

    /* ── Hide default Streamlit uploader styling ─────────────── */
    [data-testid="stFileUploader"] {
        background: transparent !important;
    }

    [data-testid="stFileUploader"] > div {
        background: transparent !important;
        padding: 0 !important;
    }

    [data-testid="stFileUploader"] section {
        background: var(--bg-card) !important;
        border: 2px dashed var(--border-color) !important;
        border-radius: var(--radius-lg) !important;
        padding: 2rem !important;
        transition: all 0.3s ease !important;
    }

    [data-testid="stFileUploader"] section:hover {
        border-color: var(--accent-blue) !important;
        box-shadow: var(--shadow-glow) !important;
    }

    [data-testid="stFileUploader"] section > div {
        color: var(--text-secondary) !important;
    }

    [data-testid="stFileUploader"] small {
        color: var(--text-muted) !important;
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* ── Image Preview Cards ─────────────────────────────────── */
    .image-card {
        background: var(--gradient-card);
        border: 1px solid var(--border-color);
        border-radius: var(--radius-md);
        overflow: hidden;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: var(--shadow-card);
    }

    .image-card:hover {
        border-color: var(--border-accent);
        transform: translateY(-2px);
        box-shadow: var(--shadow-glow), var(--shadow-card);
    }

    .image-card img {
        width: 100%;
        height: 200px;
        object-fit: cover;
        display: block;
    }

    .image-card-body {
        padding: 1rem;
    }

    .image-card-name {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.8rem;
        color: var(--text-secondary);
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    /* ── Result Cards ────────────────────────────────────────── */
    .result-card {
        background: var(--gradient-card);
        border: 1px solid var(--border-color);
        border-radius: var(--radius-md);
        overflow: hidden;
        transition: all 0.3s ease;
        box-shadow: var(--shadow-card);
    }

    .result-card.real {
        border-color: rgba(16, 185, 129, 0.4);
        box-shadow: 0 0 20px rgba(16, 185, 129, 0.08);
    }

    .result-card.spoof {
        border-color: rgba(239, 68, 68, 0.4);
        box-shadow: 0 0 20px rgba(239, 68, 68, 0.08);
    }

    .result-header {
        padding: 0.8rem 1rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }

    .result-header.real { background: rgba(16, 185, 129, 0.08); }
    .result-header.spoof { background: rgba(239, 68, 68, 0.08); }

    .result-label {
        font-family: 'JetBrains Mono', monospace;
        font-weight: 600;
        font-size: 0.85rem;
        letter-spacing: 1px;
        text-transform: uppercase;
    }

    .result-label.real { color: var(--accent-green); }
    .result-label.spoof { color: var(--accent-red); }

    .result-confidence {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.8rem;
        color: var(--text-muted);
    }

    .result-image {
        width: 100%;
        height: 200px;
        object-fit: cover;
        display: block;
    }

    .result-body {
        padding: 1rem;
    }

    .result-filename {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.78rem;
        color: var(--text-secondary);
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        margin-bottom: 0.6rem;
    }

    /* ── Confidence Bar ──────────────────────────────────────── */
    .confidence-bar-bg {
        width: 100%;
        height: 6px;
        background: rgba(255, 255, 255, 0.06);
        border-radius: 3px;
        overflow: hidden;
    }

    .confidence-bar-fill {
        height: 100%;
        border-radius: 3px;
        transition: width 0.8s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .confidence-bar-fill.real {
        background: linear-gradient(90deg, #10b981, #34d399);
    }

    .confidence-bar-fill.spoof {
        background: linear-gradient(90deg, #ef4444, #f87171);
    }

    /* ── Stats Bar ───────────────────────────────────────────── */
    .stats-bar {
        display: flex;
        gap: 1rem;
        margin: 1.5rem 0;
        flex-wrap: wrap;
    }

    .stat-chip {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: var(--radius-sm);
        padding: 10px 18px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.82rem;
        color: var(--text-secondary);
        flex: 1;
        min-width: 140px;
        justify-content: center;
    }

    .stat-chip .stat-value {
        font-weight: 600;
        color: var(--text-primary);
    }

    .stat-chip.real-chip { border-color: rgba(16, 185, 129, 0.3); }
    .stat-chip.spoof-chip { border-color: rgba(239, 68, 68, 0.3); }

    /* ── Analyze Button ──────────────────────────────────────── */
    .stButton > button {
        background: linear-gradient(135deg, #3b82f6, #2563eb) !important;
        color: white !important;
        border: none !important;
        border-radius: var(--radius-sm) !important;
        padding: 0.7rem 2.5rem !important;
        font-family: 'Outfit', sans-serif !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        letter-spacing: 0.3px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3) !important;
    }

    .stButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 25px rgba(59, 130, 246, 0.45) !important;
    }

    .stButton > button:active {
        transform: translateY(0) !important;
    }

    /* ── Section Headers ─────────────────────────────────────── */
    .section-header {
        display: flex;
        align-items: center;
        gap: 10px;
        margin: 2rem 0 1rem;
        padding-bottom: 0.8rem;
        border-bottom: 1px solid var(--border-color);
    }

    .section-header h3 {
        font-family: 'Outfit', sans-serif;
        font-size: 1.2rem;
        font-weight: 600;
        color: var(--text-primary);
        margin: 0;
    }

    .section-header .section-count {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        color: var(--text-muted);
        background: var(--bg-card);
        padding: 3px 10px;
        border-radius: 999px;
        border: 1px solid var(--border-color);
    }

    /* ── Footer ──────────────────────────────────────────────── */
    .app-footer {
        text-align: center;
        padding: 2rem 0 1rem;
        margin-top: 3rem;
        border-top: 1px solid var(--border-color);
    }

    .app-footer p {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        color: var(--text-muted);
    }

    /* ── Divider ─────────────────────────────────────────────── */
    hr {
        border: none;
        border-top: 1px solid var(--border-color);
        margin: 1.5rem 0;
    }

    /* ── Streamlit element overrides ─────────────────────────── */
    .stMarkdown p, .stMarkdown li { color: var(--text-secondary); }
    .stProgress > div > div { background: var(--accent-blue) !important; }

    [data-testid="stSidebar"] {
        background: var(--bg-secondary) !important;
    }

    /* Hide hamburger & footer */
    #MainMenu, footer { visibility: hidden; }

    /* ── Animations ──────────────────────────────────────────── */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }

    .fade-in-up {
        animation: fadeInUp 0.5s ease forwards;
    }

    .processing-pulse {
        animation: pulse 1.5s ease-in-out infinite;
    }
    </style>
    """

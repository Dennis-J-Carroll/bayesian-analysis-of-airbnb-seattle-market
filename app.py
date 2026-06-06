"""Bayesian Dashboard for Recruiters - Universal Airbnb Analytics Platform.

HuggingFace Spaces entry point with st.navigation routing and glassmorphism styling.
"""
import streamlit as st
from dashboard.utils.session_manager import AppState
from dashboard.utils.styling import apply_theme
from dashboard.pages import (
    overview,
    neighborhood,
    prediction,
    market_intel,
    business_strategy,
    model_insights,
    upload,
)

# Kept for test compatibility (test_app_router checks this)
PAGE_REGISTRY = {
    "Market Overview": overview.render,
    "Neighborhood Analysis": neighborhood.render,
    "Price Prediction": prediction.render,
    "Market Intelligence": market_intel.render,
    "Business Strategy": business_strategy.render,
    "Model Insights": model_insights.render,
    "Upload Data": upload.render,
}


def inject_global_css():
    """Inject Inter font + glassmorphism base styles on top of theme CSS."""
    st.markdown(
        """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="st-"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
}

/* ── Hide Streamlit chrome ── */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header { visibility: hidden; }

/* ── Glassmorphism card ── */
.glass-card {
    background: rgba(255, 255, 255, 0.07);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 16px;
    padding: 1.5rem;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
    margin-bottom: 1rem;
}

/* ── Metric containers ── */
[data-testid="stMetric"] {
    background: rgba(255, 255, 255, 0.05) !important;
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 12px !important;
    padding: 1rem 1.5rem !important;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
    transition: box-shadow 0.2s ease;
}

[data-testid="stMetric"]:hover {
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
}

[data-testid="stMetricValue"] {
    font-size: 2rem !important;
    font-weight: 700 !important;
    letter-spacing: -0.025em;
}

[data-testid="stMetricLabel"] {
    font-size: 0.8rem !important;
    font-weight: 500 !important;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    opacity: 0.7;
}

/* ── Sidebar glass ── */
section[data-testid="stSidebar"] {
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border-right: 1px solid rgba(255, 255, 255, 0.08);
}

/* ── Buttons ── */
.stButton > button {
    border-radius: 8px !important;
    font-weight: 500 !important;
    letter-spacing: 0.025em;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
}

.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2) !important;
}

/* ── Chart containers ── */
.js-plotly-plot {
    border-radius: 12px;
    overflow: hidden;
}

/* ── Inputs / Selects ── */
[data-baseweb="select"] > div,
[data-baseweb="input"] > div {
    border-radius: 8px !important;
}

/* ── Tabs ── */
[data-baseweb="tab"] {
    border-radius: 8px 8px 0 0 !important;
    font-weight: 500 !important;
}

/* ── Navigation items (st.navigation) ── */
[data-testid="stSidebarNav"] li {
    border-radius: 8px;
    margin: 2px 0;
    transition: background 0.15s ease;
}

/* ── Section dividers ── */
hr {
    border-color: rgba(255, 255, 255, 0.1) !important;
}

/* ── Toggle widget label ── */
[data-testid="stToggle"] label {
    font-weight: 500;
}

/* ── Smooth page transitions ── */
.main .block-container {
    animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(4px); }
    to   { opacity: 1; transform: translateY(0); }
}
</style>
""",
        unsafe_allow_html=True,
    )


def main():
    """Main application entry point."""
    st.set_page_config(
        page_title="Bayesian Dashboard for Recruiters",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    AppState.init()

    # ── Theme toggle (replaces sidebar radio) ──────────────────────
    dark_mode = st.sidebar.toggle(
        "🌙 Dark Mode",
        value=st.session_state[AppState.THEME] == "deep_forest",
        key="dark_mode_toggle",
    )
    new_theme = "deep_forest" if dark_mode else "modern_neutral"
    if new_theme != st.session_state[AppState.THEME]:
        st.session_state[AppState.THEME] = new_theme
        st.rerun()

    # ── Apply CSS: theme first, glassmorphism on top ───────────────
    # Order matters: apply_theme() sets CSS vars, inject_global_css()
    # augments with glassmorphism — avoids !important specificity conflicts.
    apply_theme(st.session_state[AppState.THEME])
    inject_global_css()

    # ── Data source indicator ──────────────────────────────────────
    st.sidebar.markdown("---")
    if st.session_state[AppState.DATA_SOURCE] == "uploaded":
        st.sidebar.info("📁 Using uploaded CSV")
        if st.sidebar.button("↩ Reset to Seattle Data"):
            AppState.reset_to_default()  # calls st.rerun() internally
    else:
        st.sidebar.info("🏙 Using Seattle dataset")

    st.sidebar.markdown("---")
    st.sidebar.caption("Bayesian Dashboard v2.0")

    # ── Native multi-page navigation ──────────────────────────────
    pg = st.navigation(
        [
            st.Page(overview.render, title="Market Overview", icon="📊"),
            st.Page(neighborhood.render, title="Neighborhood Analysis", icon="📍"),
            st.Page(prediction.render, title="Price Prediction", icon="💰"),
            st.Page(market_intel.render, title="Market Intelligence", icon="🔍"),
            st.Page(business_strategy.render, title="Business Strategy", icon="💼"),
            st.Page(model_insights.render, title="Model Insights", icon="🧠"),
            st.Page(upload.render, title="Upload Data", icon="📤"),
        ],
        position="sidebar",
    )
    pg.run()


if __name__ == "__main__":
    main()

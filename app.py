"""Bayesian Dashboard for Recruiters - Universal Airbnb Analytics Platform.

HuggingFace Spaces entry point with page routing and theme management.
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
)

# Page configuration
st.set_page_config(
    page_title="Bayesian Dashboard for Recruiters",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Page registry
PAGE_REGISTRY = {
    "Market Overview": overview.render,
    "Neighborhood Analysis": neighborhood.render,
    "Price Prediction": prediction.render,
    "Market Intelligence": market_intel.render,
    "Business Strategy": business_strategy.render,
    "Model Insights": model_insights.render,
}


def main():
    """Main application entry point."""
    # Initialize session state
    AppState.init()

    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Select Page", list(PAGE_REGISTRY.keys()))

    # Theme toggle
    st.sidebar.markdown("---")
    st.sidebar.subheader("Theme")

    current_theme = st.session_state[AppState.THEME]
    theme_choice = st.sidebar.radio(
        "Select Theme",
        ["modern_neutral", "deep_forest"],
        index=0 if current_theme == "modern_neutral" else 1,
        format_func=lambda x: "Light Mode" if x == "modern_neutral" else "Dark Mode",
    )

    # Detect theme change and trigger rerun
    if theme_choice != st.session_state[AppState.THEME]:
        st.session_state[AppState.THEME] = theme_choice
        st.rerun()

    # Apply current theme
    apply_theme(st.session_state[AppState.THEME])

    # Data source indicator
    st.sidebar.markdown("---")
    st.sidebar.subheader("Data Source")
    data_source = st.session_state[AppState.DATA_SOURCE]
    if data_source == "uploaded":
        st.sidebar.info("Using uploaded CSV")
        if st.sidebar.button("Reset to Seattle Data"):
            AppState.reset_to_default()
            st.rerun()
    else:
        st.sidebar.info("Using default Seattle data")

    # Render selected page
    PAGE_REGISTRY[page]()

    # Footer
    st.sidebar.markdown("---")
    st.sidebar.caption("Bayesian Dashboard v2.0 | Universal Airbnb Analytics")


if __name__ == "__main__":
    main()

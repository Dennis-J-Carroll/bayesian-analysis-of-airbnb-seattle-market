"""
Enterprise-Grade Airbnb Seattle Pricing & Investment Dashboard

A production-ready Streamlit application for analyzing Airbnb pricing dynamics
and investment opportunities using hierarchical Bayesian modeling.

Author: Dennis J. Carroll
Version: 1.0.0
"""

import streamlit as st
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import components
from dashboard.components.price_predictor import price_predictor_page
from dashboard.components.investment_analyzer import investment_analyzer_page
from dashboard.components.neighborhood_comparison import neighborhood_comparison_page
from dashboard.components.model_validation import model_validation_page
from dashboard.components.feature_impact import feature_impact_page
from dashboard.utils.data_loader import load_data_and_model
from dashboard.utils.styling import inject_minimal_theme

# Page configuration
st.set_page_config(
    page_title="Airbnb Seattle Analytics Platform",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://github.com/Dennis-J-Carroll/Bayesian-Analysis-of-Airbnb-Seattle-Market",
        "Report a bug": "https://github.com/Dennis-J-Carroll/Bayesian-Analysis-of-Airbnb-Seattle-Market/issues",
        "About": """
        # Airbnb Seattle Analytics Platform

        **Version**: 1.0.0

        A sophisticated Bayesian analytics platform for Airbnb pricing and investment analysis.

        Built with PyMC, Streamlit, and modern data science best practices.
        """,
    },
)


# Initialize session state
if "data_loaded" not in st.session_state:
    st.session_state.data_loaded = False
    st.session_state.data = None
    st.session_state.trace = None
    st.session_state.neighborhoods_list = None
    st.session_state.neighborhoods_dict = None


# Load data and model
@st.cache_resource(show_spinner=False)
def initialize_app():
    """Initialize application data and models"""
    return load_data_and_model()


# Main application
def main():
    """Main application entry point"""

    # Apply Phase 1 minimal theme
    inject_minimal_theme()

    # Header
    st.markdown(
        """
    <div class="main-header">
        <h1>🏠 Airbnb Seattle Analytics Platform</h1>
        <p class="subtitle">Enterprise-Grade Pricing & Investment Intelligence</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Load data
    if not st.session_state.data_loaded:
        with st.spinner("🔄 Loading data and models... This may take a moment."):
            try:
                (
                    data,
                    trace,
                    neighborhoods_list,
                    neighborhoods_dict,
                    model_metadata,
                ) = initialize_app()

                st.session_state.data = data
                st.session_state.trace = trace
                st.session_state.neighborhoods_list = neighborhoods_list
                st.session_state.neighborhoods_dict = neighborhoods_dict
                st.session_state.model_metadata = model_metadata
                st.session_state.data_loaded = True

                st.success("✅ Data and models loaded successfully!")
            except Exception as e:
                st.error(f"❌ Error loading data: {str(e)}")
                st.info(
                    "Please ensure the data files are in the correct location and the model has been trained."
                )
                st.stop()

    # Sidebar navigation
    st.sidebar.title("🧭 Navigation")

    # Model status indicator
    if st.session_state.data_loaded:
        st.sidebar.success("✅ Model Active")
        st.sidebar.metric("Listings", f"{len(st.session_state.data):,}")
        st.sidebar.metric("Neighborhoods", len(st.session_state.neighborhoods_list))
        st.sidebar.metric(
            "Model R²", f"{st.session_state.model_metadata.get('r_squared', 0.481):.3f}"
        )

    st.sidebar.markdown("---")

    # Page selection
    page_options = {
        "🏠 Home": "home",
        "💰 Price Predictor": "price_predictor",
        "📊 Investment Analyzer": "investment_analyzer",
        "📍 Neighborhood Comparison": "neighborhood_comparison",
        "✅ Model Validation": "model_validation",
        "⚙️ Feature Impact": "feature_impact",
    }

    selected_page = st.sidebar.radio(
        "Select Tool", list(page_options.keys()), label_visibility="collapsed"
    )

    page = page_options[selected_page]

    st.sidebar.markdown("---")

    # Quick stats
    if st.session_state.data_loaded and page != "home":
        st.sidebar.markdown("### 📈 Quick Stats")

        data = st.session_state.data

        avg_price = data["price_clean"].mean()
        median_price = data["price_clean"].median()
        price_std = data["price_clean"].std()

        st.sidebar.metric("Avg Price", f"${avg_price:.0f}/night")
        st.sidebar.metric("Median Price", f"${median_price:.0f}/night")
        st.sidebar.metric("Price Std Dev", f"${price_std:.0f}")

        st.sidebar.markdown("---")

    # Help section
    with st.sidebar.expander("ℹ️ Help & Documentation"):
        st.markdown(
            """
        **Quick Guide**:
        - 💰 **Price Predictor**: Get price estimates with confidence intervals
        - 📊 **Investment Analyzer**: Evaluate ROI for property investments
        - 📍 **Neighborhood Comparison**: Compare multiple neighborhoods
        - ✅ **Model Validation**: See model accuracy on real properties
        - ⚙️ **Feature Impact**: Calculate value of amenities

        **Model Information**:
        - Built with hierarchical Bayesian modeling (PyMC)
        - R² = 0.481 (explains 48% of variance)
        - RMSE = $101, MAE = $63
        - Best for mid-range entire homes ($50-$300)

        **Limitations**:
        - ⚠️ Not suitable for luxury properties (>$300)
        - ⚠️ Not suitable for shared rooms
        - ⚠️ Limited to neighborhoods with >5 listings

        [📚 Full Documentation](https://github.com/Dennis-J-Carroll/Bayesian-Analysis-of-Airbnb-Seattle-Market)
        """
        )

    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown(
        """
    <div style='text-align: center; color: #666; font-size: 0.8em;'>
        <p><strong>Airbnb Seattle Analytics</strong></p>
        <p>Version 1.0.0</p>
        <p>Built with PyMC + Streamlit</p>
        <p>© 2025 Dennis J. Carroll</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Route to selected page
    if page == "home":
        show_home_page()
    elif page == "price_predictor":
        price_predictor_page()
    elif page == "investment_analyzer":
        investment_analyzer_page()
    elif page == "neighborhood_comparison":
        neighborhood_comparison_page()
    elif page == "model_validation":
        model_validation_page()
    elif page == "feature_impact":
        feature_impact_page()


def show_home_page():
    """Display home page with overview and key metrics"""

    # Welcome section
    st.markdown(
        """
    <div class="info-box">
        <h2>Welcome to the Airbnb Seattle Analytics Platform</h2>
        <p>
            This enterprise-grade platform uses <strong>hierarchical Bayesian modeling</strong>
            to provide sophisticated pricing insights and investment analysis for Seattle's
            short-term rental market.
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Key features
    st.markdown("### 🎯 Platform Capabilities")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
        <div class="feature-card">
            <h3>💰 Price Intelligence</h3>
            <ul>
                <li>Bayesian price predictions</li>
                <li>Confidence intervals</li>
                <li>Neighborhood benchmarking</li>
                <li>Uncertainty quantification</li>
            </ul>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
        <div class="feature-card">
            <h3>📊 Investment Analysis</h3>
            <ul>
                <li>ROI projections</li>
                <li>Risk assessment</li>
                <li>Sensitivity analysis</li>
                <li>Portfolio optimization</li>
            </ul>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            """
        <div class="feature-card">
            <h3>📍 Market Intelligence</h3>
            <ul>
                <li>Neighborhood comparison</li>
                <li>Strategic scoring</li>
                <li>Competitive analysis</li>
                <li>Market trends</li>
            </ul>
        </div>
        """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # Dataset overview
    st.markdown("### 📊 Dataset Overview")

    data = st.session_state.data

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total Listings",
            f"{len(data):,}",
            help="Number of Airbnb listings in dataset",
        )

    with col2:
        st.metric(
            "Neighborhoods",
            len(st.session_state.neighborhoods_list),
            help="Number of unique neighborhoods",
        )

    with col3:
        st.metric(
            "Average Price",
            f"${data['price_clean'].mean():.0f}",
            help="Mean nightly price across all listings",
        )

    with col4:
        st.metric(
            "Price Range",
            f"${data['price_clean'].min():.0f} - ${data['price_clean'].max():.0f}",
            help="Minimum to maximum nightly price",
        )

    st.markdown("---")

    # Model performance
    st.markdown("### 🎯 Model Performance")

    col1, col2, col3, col4 = st.columns(4)

    metadata = st.session_state.model_metadata

    with col1:
        st.metric(
            "R² Score",
            f"{metadata.get('r_squared', 0.481):.3f}",
            help="Proportion of variance explained (higher is better)",
        )

    with col2:
        st.metric(
            "RMSE",
            f"${metadata.get('rmse', 101):.0f}",
            help="Root Mean Squared Error in dollars",
        )

    with col3:
        st.metric(
            "MAE",
            f"${metadata.get('mae', 63):.0f}",
            help="Mean Absolute Error in dollars",
        )

    with col4:
        st.metric(
            "Calibration",
            f"{metadata.get('calibration', 90):.0f}%",
            help="Percentage of actual prices within confidence intervals",
        )

    st.markdown("---")

    # Visualization: Price distribution
    st.markdown("### 📈 Price Distribution")

    import matplotlib.pyplot as plt
    import numpy as np

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Histogram
    axes[0].hist(
        data["price_clean"], bins=50, edgecolor="black", alpha=0.7, color="steelblue"
    )
    axes[0].axvline(
        data["price_clean"].mean(),
        color="red",
        linestyle="--",
        linewidth=2,
        label=f'Mean: ${data["price_clean"].mean():.0f}',
    )
    axes[0].axvline(
        data["price_clean"].median(),
        color="orange",
        linestyle="--",
        linewidth=2,
        label=f'Median: ${data["price_clean"].median():.0f}',
    )
    axes[0].set_xlabel("Price ($/night)", fontsize=12)
    axes[0].set_ylabel("Frequency", fontsize=12)
    axes[0].set_title("Price Distribution", fontsize=14, fontweight="bold")
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    # Box plot by accommodates
    accommodates_data = [
        data[data["accommodates"] == i]["price_clean"].dropna()
        for i in range(1, 11)
        if len(data[data["accommodates"] == i]) > 0
    ]

    bp = axes[1].boxplot(
        accommodates_data,
        labels=range(1, len(accommodates_data) + 1),
        patch_artist=True,
        showfliers=False,
    )

    for patch in bp["boxes"]:
        patch.set_facecolor("lightblue")
        patch.set_alpha(0.7)

    axes[1].set_xlabel("Accommodates (guests)", fontsize=12)
    axes[1].set_ylabel("Price ($/night)", fontsize=12)
    axes[1].set_title("Price by Guest Capacity", fontsize=14, fontweight="bold")
    axes[1].grid(True, alpha=0.3, axis="y")

    plt.tight_layout()
    st.pyplot(fig)

    st.markdown("---")

    # Getting started
    st.markdown("### 🚀 Getting Started")

    st.markdown(
        """
    <div class="info-box">
        <h4>Choose a tool from the sidebar to begin:</h4>
        <ol>
            <li><strong>Price Predictor</strong>: Get instant price estimates for your property</li>
            <li><strong>Investment Analyzer</strong>: Evaluate investment opportunities with ROI analysis</li>
            <li><strong>Neighborhood Comparison</strong>: Compare multiple neighborhoods side-by-side</li>
            <li><strong>Model Validation</strong>: See model accuracy on real properties</li>
            <li><strong>Feature Impact</strong>: Calculate the value of adding amenities</li>
        </ol>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Warnings and limitations
    st.markdown("### ⚠️ Important Limitations")

    col1, col2 = st.columns(2)

    with col1:
        st.warning(
            """
        **When to Use This Model**:
        - ✅ Mid-range entire homes ($50-$300/night)
        - ✅ Standard properties (no unique features)
        - ✅ Neighborhoods with >10 listings
        - ✅ Relative price comparisons
        - ✅ Strategic market analysis
        """
        )

    with col2:
        st.error(
            """
        **When NOT to Use**:
        - ❌ Luxury properties (>$300/night)
        - ❌ Shared or private rooms
        - ❌ Unique properties (waterfront, historic)
        - ❌ New/emerging neighborhoods
        - ❌ High-stakes investment decisions (without validation)
        """
        )

    st.info(
        """
    **📌 Best Practice**: Use this tool for initial analysis and relative comparisons.
    Combine insights with local market expertise and pilot testing before making
    significant investment decisions.
    """
    )


if __name__ == "__main__":
    main()

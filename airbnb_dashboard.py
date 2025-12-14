"""
Seattle Airbnb Pricing & Investment Dashboard
Powered by Hierarchical Bayesian Modeling
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

# Page configuration
st.set_page_config(
    page_title="Seattle Airbnb Pricing & Investment Analyzer",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
)


# Dynamic Grid Layout Helper Function
def render_dynamic_grid(data, num_columns, render_item_func):
    """
    Renders a list of items in a dynamic grid layout.

    Args:
        data (list): List of data items to display.
        num_columns (int): Number of columns per row.
        render_item_func (function): Function to render a single item.
                                     It should accept a single argument (the item).
    """
    # Loop through the data in batches of 'num_columns'
    for i in range(0, len(data), num_columns):
        # Create a row of columns
        cols = st.columns(num_columns)

        # Get the current batch of items
        batch = data[i : i + num_columns]

        # Render each item in its respective column
        for col, item in zip(cols, batch):
            with col:
                render_item_func(item)


# Custom CSS for better styling
st.markdown(
    """
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #FF5A5F;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #484848;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #FF5A5F;
    }
    .success-box {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
    }
    .warning-box {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ffc107;
    }
    .danger-box {
        background-color: #f8d7da;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #dc3545;
    }
</style>
""",
    unsafe_allow_html=True,
)


# Load model and data with caching
@st.cache_resource
def load_model_and_data():
    """Load trained model and data - cached for performance"""
    from src.hierarchical_bayesian_model import HierarchicalBayesianPriceModel
    from src.baseline_comparison import BaselineComparison
    from src.varying_slopes_analysis import VaryingSlopesAnalysis
    from src.prescriptive_pricing import PrescriptivePricingEngine

    # Initialize model
    model = HierarchicalBayesianPriceModel(
        listings_path="data/raw/listings.csv",
        neighbourhoods_path="data/raw/neighbourhoods.csv",
    )

    # Load and clean data
    model.load_and_clean_data()

    # Build and fit model (using smaller sample for faster dashboard load)
    model.build_hierarchical_model()
    model.fit_model(samples=500, tune=250, chains=2)

    # Initialize analysis modules
    baseline_comp = BaselineComparison(model)
    slopes_analysis = VaryingSlopesAnalysis(model)
    pricing_engine = PrescriptivePricingEngine(model, slopes_analysis)

    return model, baseline_comp, slopes_analysis, pricing_engine


# Initialize session state
if "model_loaded" not in st.session_state:
    with st.spinner("Loading model and data... This may take a moment."):
        try:
            (
                model,
                baseline_comp,
                slopes_analysis,
                pricing_engine,
            ) = load_model_and_data()
            st.session_state.model = model
            st.session_state.baseline_comp = baseline_comp
            st.session_state.slopes_analysis = slopes_analysis
            st.session_state.pricing_engine = pricing_engine
            st.session_state.model_loaded = True
        except Exception as e:
            st.error(f"Error loading model: {str(e)}")
            st.stop()

# Get cached objects
model = st.session_state.model
baseline_comp = st.session_state.baseline_comp
slopes_analysis = st.session_state.slopes_analysis
pricing_engine = st.session_state.pricing_engine

data = model.data
neighborhoods_list = sorted(model.neighborhoods.tolist())
neighborhoods_dict = model.neighborhood_lookup


# Sidebar navigation
st.sidebar.title("🧭 Navigation")
st.sidebar.markdown("---")
page = st.sidebar.radio(
    "Select a Tool:",
    [
        "🏠 Home",
        "💰 Price Predictor",
        "📊 Investment Analyzer",
        "🗺️ Neighborhood Comparison",
        "✅ Model Validation",
        "⚙️ Feature Impact",
    ],
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📈 Quick Stats")
st.sidebar.metric("Total Listings", f"{len(data):,}")
st.sidebar.metric("Neighborhoods", f"{len(neighborhoods_list)}")
st.sidebar.metric("Avg Price", f"${data['price_clean'].mean():.0f}")

# Main title
st.markdown(
    '<div class="main-header">🏠 Seattle Airbnb Pricing Analyzer</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="sub-header">Powered by Hierarchical Bayesian Modeling</div>',
    unsafe_allow_html=True,
)
st.markdown("---")


# ===========================
# PAGE: HOME
# ===========================
if page == "🏠 Home":
    st.header("Welcome to the Seattle Airbnb Pricing & Investment Analyzer")

    st.markdown(
        """
    This dashboard uses a sophisticated **Hierarchical Bayesian statistical model** to provide data-driven insights for Airbnb hosts and investors in Seattle.
    """
    )

    # 1. Apply the Misty Morning Color Palette
    # ---------------------------------------------------------
    st.markdown(
        """
    <style>
        /* Optional: Set the main app background to Beige */
        .stApp {
            background-color: #f5f5dc;
        }

        /* Feature Card Styling */
        div.feature-card {
            background-color: #add8e6;       /* Light Blue */
            border: 2px solid #778899;       /* Grey Blue */
            border-radius: 12px;
            padding: 20px;
            height: 280px;                   /* Fixed height for uniformity */
            box-shadow: 0 4px 6px rgba(47, 79, 79, 0.2);
            transition: transform 0.2s;
        }
        div.feature-card:hover {
            transform: translateY(-5px);
        }
        div.feature-card h3 {
            color: #2f4f4f;                  /* Dark Slate */
            border-bottom: 3px solid #87ceeb; /* Sky Blue */
            padding-bottom: 12px;
            margin-bottom: 15px;
            font-size: 1.2rem;
            font-weight: bold;
        }
        div.feature-card ul {
            padding-left: 20px;
            margin: 0;
        }
        div.feature-card li {
            color: #2f4f4f;                  /* Dark Slate */
            margin-bottom: 8px;
            font-size: 0.95rem;
        }
    </style>
    """,
        unsafe_allow_html=True,
    )

    # 2. Define Data for Platform Capabilities
    # ---------------------------------------------------------
    features = [
        {
            "title": "💰 Price Intelligence",
            "items": [
                "Bayesian predictions",
                "Confidence intervals",
                "Neighborhood benchmarking",
            ],
        },
        {
            "title": "📊 Investment Analysis",
            "items": ["ROI projections", "Risk assessment", "Sensitivity analysis"],
        },
        {
            "title": "📍 Market Intelligence",
            "items": [
                "Neighborhood comparison",
                "Strategic scoring",
                "Competitive analysis",
            ],
        },
        {
            "title": "⚙️ Feature Impact",
            "items": ["Amenity valuation", "Upgrade ROI", "Premium features"],
        },
    ]

    # 3. Define Render Function
    # ---------------------------------------------------------
    def render_card(feature):
        items_html = "".join([f"<li>{x}</li>" for x in feature["items"]])
        st.markdown(
            f"""
        <div class="feature-card">
            <h3>{feature['title']}</h3>
            <ul>{items_html}</ul>
        </div>
        """,
            unsafe_allow_html=True,
        )

    # 4. Call Dynamic Grid
    # ---------------------------------------------------------
    st.markdown("### 🎯 Platform Capabilities")

    # Render with 3 columns (it will wrap the 4th item automatically)
    render_dynamic_grid(features, 3, render_card)

    st.markdown("---")

    # Dataset overview
    st.subheader("📊 Dataset Overview")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Listings", f"{len(data):,}")

    with col2:
        st.metric("Neighborhoods", f"{len(neighborhoods_list)}")

    with col3:
        st.metric("Average Price", f"${data['price_clean'].mean():.0f}/night")

    with col4:
        st.metric(
            "Price Range",
            f"${data['price_clean'].min():.0f} - ${data['price_clean'].max():.0f}",
        )

    # Model performance
    st.subheader("🎯 Model Performance")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Why Hierarchical Bayesian?")
        st.markdown(
            """
        - **Uncertainty Quantification**: Provides confidence intervals for all predictions
        - **Partial Pooling**: Shares information across neighborhoods for better estimates
        - **Interpretability**: Clear neighborhood-specific effects
        - **Calibrated**: Prediction intervals are statistically accurate
        """
        )

    with col2:
        st.markdown("#### Quick Start Guide")
        st.markdown(
            """
        1. **New Host?** → Start with *Price Predictor*
        2. **Investor?** → Check out *Investment Analyzer*
        3. **Comparing Areas?** → Use *Neighborhood Comparison*
        4. **Want Data?** → See *Model Validation*
        """
        )

    # Price distribution visualization
    st.subheader("📈 Price Distribution Across Seattle")

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Histogram
    axes[0].hist(
        data["price_clean"], bins=50, color="#FF5A5F", alpha=0.7, edgecolor="black"
    )
    axes[0].axvline(
        data["price_clean"].median(),
        color="blue",
        linestyle="--",
        linewidth=2,
        label=f'Median: ${data["price_clean"].median():.0f}',
    )
    axes[0].set_xlabel("Price ($/night)")
    axes[0].set_ylabel("Number of Listings")
    axes[0].set_title("Distribution of Listing Prices")
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    # Price by accommodates
    price_by_acc = data.groupby("accommodates")["price_clean"].median()
    axes[1].plot(
        price_by_acc.index, price_by_acc.values, marker="o", linewidth=2, markersize=8
    )
    axes[1].set_xlabel("Number of Guests")
    axes[1].set_ylabel("Median Price ($/night)")
    axes[1].set_title("Price by Property Capacity")
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    st.pyplot(fig)

    # Map (if coordinates available)
    if "latitude" in data.columns and "longitude" in data.columns:
        st.subheader("🗺️ Listing Locations")
        map_data = data[["latitude", "longitude", "price_clean"]].dropna()
        map_data = map_data.rename(columns={"latitude": "lat", "longitude": "lon"})
        st.map(map_data, zoom=10)


# ===========================
# PAGE: PRICE PREDICTOR
# ===========================
elif page == "💰 Price Predictor":
    st.header("💰 Price Predictor")
    st.markdown(
        "Get an accurate price estimate for your property based on neighborhood and capacity."
    )

    # User inputs
    col1, col2 = st.columns(2)

    with col1:
        neighborhood = st.selectbox(
            "Select Neighborhood", neighborhoods_list, index=0, key="price_neighborhood"
        )

    with col2:
        accommodates = st.slider(
            "Number of Guests", min_value=1, max_value=10, value=4, key="price_guests"
        )

    if st.button("🔮 Predict Price", type="primary"):
        with st.spinner("Generating prediction..."):
            # Get recommendation
            recommendation = pricing_engine.recommend_price(neighborhood, accommodates)

            if "error" not in recommendation:
                # Display main metrics
                st.subheader("📊 Price Recommendation")

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric(
                        "Recommended Price",
                        f"${recommendation['recommended_price']:.0f}/night",
                    )

                with col2:
                    ci_low, ci_high = recommendation["price_range_90_ci"]
                    st.metric(
                        "90% Confidence Interval", f"${ci_low:.0f} - ${ci_high:.0f}"
                    )

                with col3:
                    comp_pos = recommendation["competitive_position"]
                    diff = (
                        (
                            recommendation["recommended_price"]
                            - comp_pos["neighborhood_avg"]
                        )
                        / comp_pos["neighborhood_avg"]
                        * 100
                    )
                    st.metric("vs. Neighborhood Avg", f"{diff:+.1f}%")

                # Visualization
                st.subheader("📈 Price Distribution")

                neighborhood_idx = neighborhoods_dict[neighborhood]
                alpha_samples = model.trace.posterior["alpha"].values.reshape(
                    -1, model.n_neighborhoods
                )[:, neighborhood_idx]
                beta_samples = model.trace.posterior["beta"].values.reshape(
                    -1, model.n_neighborhoods
                )[:, neighborhood_idx]

                log_price_samples = alpha_samples + beta_samples * accommodates
                price_samples = np.exp(log_price_samples)

                fig, ax = plt.subplots(figsize=(12, 5))
                ax.hist(
                    price_samples,
                    bins=50,
                    density=True,
                    alpha=0.7,
                    color="steelblue",
                    edgecolor="black",
                )
                ax.axvline(
                    recommendation["recommended_price"],
                    color="red",
                    linestyle="--",
                    linewidth=2,
                    label=f'Recommended: ${recommendation["recommended_price"]:.0f}',
                )
                ax.axvline(
                    ci_low,
                    color="orange",
                    linestyle=":",
                    linewidth=2,
                    label="90% CI",
                )
                ax.axvline(ci_high, color="orange", linestyle=":", linewidth=2)
                ax.set_xlabel("Predicted Price ($/night)")
                ax.set_ylabel("Probability Density")
                ax.set_title(
                    f"Price Prediction for {neighborhood} ({accommodates} guests)"
                )
                ax.legend()
                ax.grid(True, alpha=0.3)
                st.pyplot(fig)

                # Rationale
                st.subheader("💡 Pricing Rationale")
                for rationale in recommendation["rationale"]:
                    st.markdown(f"- {rationale}")

                # Risk assessment
                st.subheader("⚠️ Risk Assessment")
                risk = recommendation["risk_assessment"]
                risk_color = (
                    "success"
                    if risk["level"] == "low"
                    else ("warning" if risk["level"] == "moderate" else "danger")
                )

                st.markdown(f"**Risk Level**: :{risk_color}[{risk['level'].upper()}]")
                for factor in risk["factors"]:
                    st.markdown(f"- {factor}")

                # Competitive position
                st.subheader("🎯 Competitive Position")
                comp_pos = recommendation["competitive_position"]

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric(
                        "Neighborhood Average", f"${comp_pos['neighborhood_avg']:.0f}"
                    )
                with col2:
                    st.metric(
                        "Similar Listings Average",
                        f"${comp_pos['similar_listings_avg']:.0f}",
                    )
                with col3:
                    st.metric("Number of Competitors", comp_pos["n_similar_listings"])

            else:
                st.error(recommendation["error"])


# ===========================
# PAGE: INVESTMENT ANALYZER
# ===========================
elif page == "📊 Investment Analyzer":
    st.header("📊 Investment Analyzer")
    st.markdown(
        "Evaluate investment opportunities and estimate ROI for Airbnb properties."
    )

    st.warning(
        "⚠️ This is a simplified investment model for demonstration purposes. Actual ROI depends on many factors not captured in this model."
    )

    # User inputs
    col1, col2 = st.columns(2)

    with col1:
        invest_neighborhood = st.selectbox(
            "Target Neighborhood", neighborhoods_list, key="invest_neighborhood"
        )
        investment_amount = st.slider(
            "Investment Amount ($)",
            min_value=10000,
            max_value=500000,
            value=100000,
            step=10000,
        )

    with col2:
        accommodates = st.slider(
            "Property Capacity (guests)", min_value=1, max_value=10, value=4
        )
        time_horizon = st.slider(
            "Time Horizon (years)", min_value=1, max_value=10, value=5
        )

    # Assumptions
    st.subheader("📋 Investment Assumptions")
    col1, col2, col3 = st.columns(3)

    with col1:
        occupancy_rate = st.slider(
            "Expected Occupancy Rate",
            min_value=0.3,
            max_value=0.95,
            value=0.70,
            step=0.05,
        )
    with col2:
        operating_costs_pct = st.slider(
            "Operating Costs (% of revenue)",
            min_value=0.1,
            max_value=0.5,
            value=0.30,
            step=0.05,
        )
    with col3:
        property_appreciation = st.slider(
            "Annual Property Appreciation",
            min_value=0.0,
            max_value=0.10,
            value=0.03,
            step=0.01,
        )

    if st.button("📈 Analyze Investment", type="primary"):
        with st.spinner("Running investment analysis..."):
            # Get price prediction
            recommendation = pricing_engine.recommend_price(
                invest_neighborhood, accommodates
            )

            if "error" not in recommendation:
                nightly_rate = recommendation["recommended_price"]

                # Calculate annual revenue
                annual_nights = 365 * occupancy_rate
                gross_annual_revenue = nightly_rate * annual_nights
                operating_costs = gross_annual_revenue * operating_costs_pct
                net_annual_revenue = gross_annual_revenue - operating_costs

                # Calculate total returns over time horizon
                total_rental_income = net_annual_revenue * time_horizon
                property_value_gain = investment_amount * (
                    (1 + property_appreciation) ** time_horizon - 1
                )
                total_return = total_rental_income + property_value_gain

                # ROI metrics
                total_roi = (total_return / investment_amount) * 100
                annual_roi = ((total_return / investment_amount) / time_horizon) * 100
                cash_on_cash = (net_annual_revenue / investment_amount) * 100
                payback_period = investment_amount / net_annual_revenue

                # Display results
                st.subheader("💰 Investment Summary")

                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric("Total ROI", f"{total_roi:.1f}%")
                with col2:
                    st.metric("Annual ROI", f"{annual_roi:.1f}%")
                with col3:
                    st.metric("Cash-on-Cash Return", f"{cash_on_cash:.1f}%")
                with col4:
                    st.metric("Payback Period", f"{payback_period:.1f} years")

                # Revenue breakdown
                st.subheader("📊 Financial Breakdown")

                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("**Annual Financials (Year 1)**")
                    st.metric("Gross Annual Revenue", f"${gross_annual_revenue:,.0f}")
                    st.metric("Operating Costs", f"${operating_costs:,.0f}")
                    st.metric("Net Annual Revenue", f"${net_annual_revenue:,.0f}")

                with col2:
                    st.markdown(f"**Total Returns ({time_horizon} Years)**")
                    st.metric("Total Rental Income", f"${total_rental_income:,.0f}")
                    st.metric("Property Appreciation", f"${property_value_gain:,.0f}")
                    st.metric("Total Return", f"${total_return:,.0f}")

                # Visualization
                fig, axes = plt.subplots(1, 2, figsize=(14, 5))

                # Cash flow over time
                years = np.arange(1, time_horizon + 1)
                cumulative_cash_flow = net_annual_revenue * years
                cumulative_property_value = (
                    investment_amount * ((1 + property_appreciation) ** years)
                    - investment_amount
                )

                axes[0].plot(
                    years, cumulative_cash_flow, marker="o", label="Rental Income"
                )
                axes[0].plot(
                    years,
                    cumulative_property_value,
                    marker="s",
                    label="Property Appreciation",
                )
                axes[0].plot(
                    years,
                    cumulative_cash_flow + cumulative_property_value,
                    marker="^",
                    linewidth=2,
                    label="Total Return",
                )
                axes[0].axhline(
                    investment_amount,
                    color="red",
                    linestyle="--",
                    label="Initial Investment",
                )
                axes[0].set_xlabel("Year")
                axes[0].set_ylabel("Cumulative Return ($)")
                axes[0].set_title("Cumulative Returns Over Time")
                axes[0].legend()
                axes[0].grid(True, alpha=0.3)

                # Revenue breakdown pie chart
                revenue_breakdown = {
                    "Net Rental Income": total_rental_income,
                    "Property Appreciation": property_value_gain,
                }
                axes[1].pie(
                    revenue_breakdown.values(),
                    labels=revenue_breakdown.keys(),
                    autopct="%1.1f%%",
                    startangle=90,
                    colors=["#FF5A5F", "#00A699"],
                )
                axes[1].set_title(f"Total Return Composition ({time_horizon} Years)")

                plt.tight_layout()
                st.pyplot(fig)

                # Risk assessment
                st.subheader("⚠️ Risk Considerations")

                if annual_roi > 15:
                    st.success(
                        "✅ Strong ROI: Investment shows attractive returns under assumptions"
                    )
                elif annual_roi > 8:
                    st.info(
                        "⚠️ Moderate ROI: Returns are positive but consider alternatives"
                    )
                else:
                    st.error("🛑 Low ROI: Returns below typical market expectations")

                st.markdown("**Key Risk Factors:**")
                st.markdown(
                    f"- Occupancy sensitivity: 10% drop in occupancy reduces annual revenue by ${gross_annual_revenue * 0.10:,.0f}"
                )
                st.markdown(
                    f"- Price sensitivity: 10% drop in nightly rate reduces annual revenue by ${gross_annual_revenue * 0.10:,.0f}"
                )
                st.markdown("- Regulatory risk: Seattle Airbnb regulations may change")
                st.markdown(
                    "- Market risk: Tourism demand and competition may fluctuate"
                )

            else:
                st.error(recommendation["error"])


# ===========================
# PAGE: NEIGHBORHOOD COMPARISON
# ===========================
elif page == "🗺️ Neighborhood Comparison":
    st.header("🗺️ Neighborhood Comparison")
    st.markdown("Compare pricing and market dynamics across Seattle neighborhoods.")

    # User inputs
    selected_neighborhoods = st.multiselect(
        "Select 2-5 Neighborhoods to Compare",
        neighborhoods_list,
        default=(
            [neighborhoods_list[0], neighborhoods_list[1]]
            if len(neighborhoods_list) > 1
            else [neighborhoods_list[0]]
        ),
    )

    accommodates = st.slider(
        "Property Capacity (guests)",
        min_value=1,
        max_value=10,
        value=4,
        key="comp_guests",
    )

    if len(selected_neighborhoods) < 2:
        st.warning("Please select at least 2 neighborhoods to compare.")
    elif len(selected_neighborhoods) > 5:
        st.warning("Please select no more than 5 neighborhoods.")
    else:
        with st.spinner("Comparing neighborhoods..."):
            comparison_data = []

            for neighborhood in selected_neighborhoods:
                # Get price prediction
                rec = pricing_engine.recommend_price(neighborhood, accommodates)

                if "error" not in rec:
                    # Get neighborhood data
                    neighborhood_data = data[
                        data["neighbourhood_cleansed"] == neighborhood
                    ]

                    comparison_data.append(
                        {
                            "Neighborhood": neighborhood,
                            "Predicted Price": rec["recommended_price"],
                            "90% CI Lower": rec["price_range_90_ci"][0],
                            "90% CI Upper": rec["price_range_90_ci"][1],
                            "Total Listings": len(neighborhood_data),
                            "Avg Price": neighborhood_data["price_clean"].mean(),
                            "Median Price": neighborhood_data["price_clean"].median(),
                            "Avg Reviews": neighborhood_data["number_of_reviews"].mean()
                            if "number_of_reviews" in neighborhood_data.columns
                            else 0,
                        }
                    )

            if comparison_data:
                comparison_df = pd.DataFrame(comparison_data)

                # Display table
                st.subheader("📊 Neighborhood Comparison Table")
                st.dataframe(
                    comparison_df.style.format(
                        {
                            "Predicted Price": "${:.0f}",
                            "90% CI Lower": "${:.0f}",
                            "90% CI Upper": "${:.0f}",
                            "Avg Price": "${:.0f}",
                            "Median Price": "${:.0f}",
                            "Avg Reviews": "{:.0f}",
                        }
                    ).background_gradient(subset=["Predicted Price"], cmap="RdYlGn"),
                    use_container_width=True,
                )

                # Visualizations
                st.subheader("📈 Visual Comparison")

                fig, axes = plt.subplots(2, 2, figsize=(16, 12))

                # Price comparison with error bars
                x_pos = np.arange(len(comparison_df))
                axes[0, 0].bar(
                    x_pos,
                    comparison_df["Predicted Price"],
                    alpha=0.7,
                    color="steelblue",
                )
                axes[0, 0].errorbar(
                    x_pos,
                    comparison_df["Predicted Price"],
                    yerr=[
                        comparison_df["Predicted Price"]
                        - comparison_df["90% CI Lower"],
                        comparison_df["90% CI Upper"]
                        - comparison_df["Predicted Price"],
                    ],
                    fmt="none",
                    ecolor="black",
                    capsize=5,
                )
                axes[0, 0].set_xticks(x_pos)
                axes[0, 0].set_xticklabels(
                    comparison_df["Neighborhood"], rotation=45, ha="right"
                )
                axes[0, 0].set_ylabel("Price ($/night)")
                axes[0, 0].set_title(
                    f"Predicted Prices with 90% CI ({accommodates} guests)"
                )
                axes[0, 0].grid(True, alpha=0.3, axis="y")

                # Competition level (number of listings)
                axes[0, 1].bar(
                    comparison_df["Neighborhood"],
                    comparison_df["Total Listings"],
                    alpha=0.7,
                    color="coral",
                )
                axes[0, 1].set_ylabel("Number of Listings")
                axes[0, 1].set_title("Market Competition")
                axes[0, 1].tick_params(axis="x", rotation=45)
                axes[0, 1].grid(True, alpha=0.3, axis="y")

                # Price range visualization
                for idx, row in comparison_df.iterrows():
                    axes[1, 0].plot(
                        [row["90% CI Lower"], row["90% CI Upper"]],
                        [idx, idx],
                        marker="|",
                        linewidth=2,
                        markersize=12,
                    )
                    axes[1, 0].plot(row["Predicted Price"], idx, "ro", markersize=8)
                axes[1, 0].set_yticks(range(len(comparison_df)))
                axes[1, 0].set_yticklabels(comparison_df["Neighborhood"])
                axes[1, 0].set_xlabel("Price ($/night)")
                axes[1, 0].set_title("Price Ranges (90% CI)")
                axes[1, 0].grid(True, alpha=0.3, axis="x")

                # Average reviews
                if comparison_df["Avg Reviews"].sum() > 0:
                    axes[1, 1].bar(
                        comparison_df["Neighborhood"],
                        comparison_df["Avg Reviews"],
                        alpha=0.7,
                        color="green",
                    )
                    axes[1, 1].set_ylabel("Average Reviews")
                    axes[1, 1].set_title("Market Activity")
                    axes[1, 1].tick_params(axis="x", rotation=45)
                    axes[1, 1].grid(True, alpha=0.3, axis="y")
                else:
                    axes[1, 1].text(
                        0.5,
                        0.5,
                        "Review data not available",
                        ha="center",
                        va="center",
                        transform=axes[1, 1].transAxes,
                    )

                plt.tight_layout()
                st.pyplot(fig)

                # Recommendations
                st.subheader("💡 Recommendations")

                highest_price = comparison_df.loc[
                    comparison_df["Predicted Price"].idxmax()
                ]
                lowest_price = comparison_df.loc[
                    comparison_df["Predicted Price"].idxmin()
                ]
                lowest_competition = comparison_df.loc[
                    comparison_df["Total Listings"].idxmin()
                ]

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.markdown("**Highest Pricing Power**")
                    st.info(
                        f"🏆 {highest_price['Neighborhood']}\n\n${highest_price['Predicted Price']:.0f}/night"
                    )

                with col2:
                    st.markdown("**Most Affordable**")
                    st.info(
                        f"💰 {lowest_price['Neighborhood']}\n\n${lowest_price['Predicted Price']:.0f}/night"
                    )

                with col3:
                    st.markdown("**Least Competition**")
                    st.info(
                        f"🎯 {lowest_competition['Neighborhood']}\n\n{lowest_competition['Total Listings']} listings"
                    )


# ===========================
# PAGE: MODEL VALIDATION
# ===========================
elif page == "✅ Model Validation":
    st.header("✅ Model Validation")
    st.markdown(
        "See how well the model predicts actual prices and evaluate its reliability."
    )

    # Sample size selector
    n_samples = st.slider(
        "Number of test samples", min_value=10, max_value=100, value=50, step=10
    )

    if st.button("🔍 Run Validation", type="primary"):
        with st.spinner("Validating model..."):
            # Sample random listings
            sample_listings = data.sample(n_samples, random_state=42)

            validation_results = []

            for idx, row in sample_listings.iterrows():
                actual_price = row["price_clean"]
                neighborhood = row["neighbourhood_cleansed"]
                accommodates = row["accommodates"]

                # Get prediction
                rec = pricing_engine.recommend_price(neighborhood, accommodates)

                if "error" not in rec:
                    predicted_price = rec["recommended_price"]
                    ci_lower, ci_upper = rec["price_range_90_ci"]

                    error = actual_price - predicted_price
                    pct_error = (error / actual_price) * 100
                    in_ci = (actual_price >= ci_lower) and (actual_price <= ci_upper)

                    validation_results.append(
                        {
                            "Neighborhood": neighborhood,
                            "Accommodates": accommodates,
                            "Actual Price": actual_price,
                            "Predicted Price": predicted_price,
                            "Error": error,
                            "% Error": pct_error,
                            "90% CI": f"[${ci_lower:.0f}, ${ci_upper:.0f}]",
                            "In CI?": "✓" if in_ci else "✗",
                        }
                    )

            validation_df = pd.DataFrame(validation_results)

            # Display results table
            st.subheader("📋 Validation Results")
            st.dataframe(
                validation_df.style.format(
                    {
                        "Actual Price": "${:.0f}",
                        "Predicted Price": "${:.0f}",
                        "Error": "${:.0f}",
                        "% Error": "{:.1f}%",
                    }
                ),
                use_container_width=True,
            )

            # Aggregate metrics
            st.subheader("📊 Overall Model Performance")

            mae = np.abs(validation_df["Error"]).mean()
            rmse = np.sqrt((validation_df["Error"] ** 2).mean())
            mape = np.abs(validation_df["% Error"]).mean()
            coverage = (validation_df["In CI?"] == "✓").mean()

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("MAE (Mean Absolute Error)", f"${mae:.0f}")
            with col2:
                st.metric("RMSE (Root Mean Squared Error)", f"${rmse:.0f}")
            with col3:
                st.metric("MAPE (Mean Absolute % Error)", f"{mape:.1f}%")
            with col4:
                st.metric("90% CI Coverage", f"{coverage:.0%}")

            # Interpretation
            st.info(
                """
            **Interpreting Results:**
            - **MAE**: Average prediction error in dollars (lower is better)
            - **RMSE**: Emphasizes larger errors (lower is better)
            - **MAPE**: Average % error (lower is better)
            - **CI Coverage**: % of actual prices within 90% credible interval (target: ~90%)
            """
            )

            # Visualizations
            st.subheader("📈 Model Performance Visualizations")

            fig, axes = plt.subplots(2, 2, figsize=(16, 12))

            # Actual vs Predicted scatter
            axes[0, 0].scatter(
                validation_df["Predicted Price"],
                validation_df["Actual Price"],
                alpha=0.6,
                s=80,
            )
            min_price = min(
                validation_df["Actual Price"].min(),
                validation_df["Predicted Price"].min(),
            )
            max_price = max(
                validation_df["Actual Price"].max(),
                validation_df["Predicted Price"].max(),
            )
            axes[0, 0].plot(
                [min_price, max_price],
                [min_price, max_price],
                "r--",
                linewidth=2,
                label="Perfect Prediction",
            )
            axes[0, 0].set_xlabel("Predicted Price ($)")
            axes[0, 0].set_ylabel("Actual Price ($)")
            axes[0, 0].set_title("Actual vs. Predicted Prices")
            axes[0, 0].legend()
            axes[0, 0].grid(True, alpha=0.3)

            # Residuals histogram
            axes[0, 1].hist(
                validation_df["Error"], bins=20, alpha=0.7, color="steelblue"
            )
            axes[0, 1].axvline(0, color="red", linestyle="--", linewidth=2)
            axes[0, 1].set_xlabel("Prediction Error ($)")
            axes[0, 1].set_ylabel("Frequency")
            axes[0, 1].set_title("Distribution of Prediction Errors")
            axes[0, 1].grid(True, alpha=0.3)

            # Residuals vs predicted
            axes[1, 0].scatter(
                validation_df["Predicted Price"],
                validation_df["Error"],
                alpha=0.6,
                s=80,
            )
            axes[1, 0].axhline(0, color="red", linestyle="--", linewidth=2)
            axes[1, 0].set_xlabel("Predicted Price ($)")
            axes[1, 0].set_ylabel("Prediction Error ($)")
            axes[1, 0].set_title("Residuals vs. Predicted")
            axes[1, 0].grid(True, alpha=0.3)

            # CI coverage by price range
            price_bins = pd.cut(validation_df["Predicted Price"], bins=5)
            coverage_by_bin = (
                validation_df.groupby(price_bins)["In CI?"]
                .apply(lambda x: (x == "✓").mean())
                .values
            )
            axes[1, 1].bar(range(len(coverage_by_bin)), coverage_by_bin, alpha=0.7)
            axes[1, 1].axhline(
                0.9, color="red", linestyle="--", linewidth=2, label="Target: 90%"
            )
            axes[1, 1].set_xlabel("Price Range")
            axes[1, 1].set_ylabel("CI Coverage")
            axes[1, 1].set_title("Calibration by Price Range")
            axes[1, 1].set_ylim([0, 1])
            axes[1, 1].legend()
            axes[1, 1].grid(True, alpha=0.3, axis="y")

            plt.tight_layout()
            st.pyplot(fig)

            # Model quality assessment
            st.subheader("✅ Model Quality Assessment")

            if coverage >= 0.85 and coverage <= 0.95:
                st.success(
                    "✅ **Excellent Calibration**: Credible intervals are well-calibrated"
                )
            elif coverage >= 0.75:
                st.info(
                    "⚠️ **Good Calibration**: Credible intervals are reasonably accurate"
                )
            else:
                st.warning(
                    "⚠️ **Poor Calibration**: Credible intervals may be unreliable"
                )

            if mape < 15:
                st.success(f"✅ **Low Error Rate**: {mape:.1f}% average error")
            elif mape < 25:
                st.info(f"⚠️ **Moderate Error Rate**: {mape:.1f}% average error")
            else:
                st.warning(f"⚠️ **High Error Rate**: {mape:.1f}% average error")


# ===========================
# PAGE: FEATURE IMPACT
# ===========================
elif page == "⚙️ Feature Impact":
    st.header("⚙️ Feature Impact Calculator")
    st.markdown(
        "Estimate how different features and amenities affect your pricing power."
    )

    st.info(
        "💡 **Note**: Feature impacts are estimated from industry benchmarks and market research, not from the current model. Use as rough guidelines."
    )

    # Base property inputs
    col1, col2 = st.columns(2)

    with col1:
        neighborhood = st.selectbox(
            "Neighborhood", neighborhoods_list, key="feature_neighborhood"
        )
    with col2:
        accommodates = st.slider(
            "Number of Guests", min_value=1, max_value=10, value=4, key="feature_guests"
        )

    # Get base prediction
    base_rec = pricing_engine.recommend_price(neighborhood, accommodates)

    if "error" not in base_rec:
        base_price = base_rec["recommended_price"]

        st.subheader("💰 Base Price")
        st.metric("Current Predicted Price", f"${base_price:.0f}/night")

        # Feature effects (estimated values)
        st.subheader("✨ Available Features")

        feature_effects = {
            "🚗 Parking": 20,
            "❄️ Air Conditioning": 15,
            "🧺 Washer/Dryer": 15,
            "🛁 Hot Tub": 30,
            "🐕 Pet Friendly": 10,
            "🌊 Waterfront View": 80,
            "📸 Professional Photos": 25,
            "⭐ Superhost Status": base_price * 0.12,
            "🏊 Pool": 40,
            "🔥 Fireplace": 12,
        }

        # Feature selection
        selected_features = st.multiselect(
            "Select features to add to your property:", list(feature_effects.keys())
        )

        if selected_features:
            # Calculate impact
            total_increase = sum([feature_effects[f] for f in selected_features])
            new_price = base_price + total_increase

            st.subheader("📊 Enhanced Pricing")

            col1, col2 = st.columns(2)

            with col1:
                st.metric(
                    "Enhanced Price",
                    f"${new_price:.0f}/night",
                    delta=f"+${total_increase:.0f}",
                )
            with col2:
                pct_increase = (total_increase / base_price) * 100
                st.metric("Price Increase", f"{pct_increase:.1f}%")

            # Feature breakdown
            st.subheader("🔍 Feature Impact Breakdown")

            impact_data = []
            cumulative_price = base_price

            for feature in selected_features:
                feature_value = feature_effects[feature]
                cumulative_price += feature_value
                impact_data.append(
                    {
                        "Feature": feature,
                        "Price Impact": f"+${feature_value:.0f}",
                        "Cumulative Price": f"${cumulative_price:.0f}",
                    }
                )

            impact_df = pd.DataFrame(impact_data)
            st.table(impact_df)

            # Visualization
            fig, ax = plt.subplots(figsize=(12, 6))

            features_list = ["Base"] + selected_features
            prices_list = [base_price] + [
                base_price
                + sum([feature_effects[f] for f in selected_features[: i + 1]])
                for i in range(len(selected_features))
            ]

            ax.plot(
                range(len(features_list)),
                prices_list,
                marker="o",
                linewidth=2,
                markersize=10,
                color="#FF5A5F",
            )
            ax.set_xticks(range(len(features_list)))
            ax.set_xticklabels(features_list, rotation=45, ha="right")
            ax.set_ylabel("Price ($/night)")
            ax.set_title("Cumulative Feature Impact on Price")
            ax.grid(True, alpha=0.3)
            plt.tight_layout()
            st.pyplot(fig)

            # ROI calculation
            st.subheader("💵 Investment ROI Estimate")

            feature_costs = {
                "🚗 Parking": 5000,
                "❄️ Air Conditioning": 3000,
                "🧺 Washer/Dryer": 1200,
                "🛁 Hot Tub": 8000,
                "🐕 Pet Friendly": 500,
                "🌊 Waterfront View": 0,
                "📸 Professional Photos": 500,
                "⭐ Superhost Status": 0,
                "🏊 Pool": 40000,
                "🔥 Fireplace": 2500,
            }

            total_cost = sum([feature_costs.get(f, 0) for f in selected_features])
            annual_revenue_increase = total_increase * 0.70 * 365

            if total_cost > 0:
                payback_period = total_cost / annual_revenue_increase
                roi_1year = ((annual_revenue_increase - total_cost) / total_cost) * 100

                col1, col2 = st.columns(2)

                with col1:
                    st.metric("Total Investment Required", f"${total_cost:,.0f}")
                    st.metric(
                        "Annual Revenue Increase (70% occupancy)",
                        f"${annual_revenue_increase:,.0f}",
                    )

                with col2:
                    st.metric("Payback Period", f"{payback_period:.1f} years")
                    st.metric("Year 1 ROI", f"{roi_1year:.1f}%")

                if roi_1year > 20:
                    st.success("✅ **Strong Investment**: High ROI expected")
                elif roi_1year > 0:
                    st.info("⚠️ **Moderate Investment**: Positive but lower ROI")
                else:
                    st.warning("🛑 **Poor Investment**: Negative first-year ROI")
            else:
                st.info(
                    "💡 Selected features require no investment (or cannot be added through investment)"
                )

    else:
        st.error(base_rec["error"])


# Footer
st.markdown("---")
st.markdown(
    """
<div style="text-align: center; color: #666;">
    <p><strong>Seattle Airbnb Pricing Analyzer</strong> | Built with Streamlit & PyMC</p>
    <p>Data Source: Inside Airbnb | Model: Hierarchical Bayesian Regression</p>
</div>
""",
    unsafe_allow_html=True,
)

"""
Price Predictor Component

Interactive tool for predicting Airbnb prices with confidence intervals
"""

import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from dashboard.utils.styling import create_prediction_card, create_metric_card

sns.set_style("whitegrid")


def price_predictor_page():
    """Main price predictor page"""

    st.markdown(
        """
    <div class="custom-card">
        <h2>💰 Price Predictor</h2>
        <p>
            Get instant price estimates for your Airbnb property with confidence intervals.
            Our Bayesian model provides uncertainty-aware predictions based on neighborhood
            and property characteristics.
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Get data from session state
    data = st.session_state.data
    trace = st.session_state.trace
    neighborhoods_list = st.session_state.neighborhoods_list
    neighborhoods_dict = st.session_state.neighborhoods_dict

    # Input form
    st.markdown("### 📝 Property Details")

    col1, col2 = st.columns(2)

    with col1:
        neighborhood = st.selectbox(
            "Neighborhood",
            neighborhoods_list,
            help="Select the neighborhood where the property is located",
        )

        accommodates = st.slider(
            "Number of Guests",
            min_value=1,
            max_value=10,
            value=4,
            help="Maximum number of guests the property can accommodate",
        )

    with col2:
        # Additional filters (if we had room_type in model)
        room_type = st.selectbox(
            "Room Type",
            ["Entire home/apt", "Private room", "Shared room"],
            help="Type of accommodation (Note: Current model works best for entire homes)",
        )

        # Amenity checkboxes
        st.markdown("**Key Amenities** (future feature)")
        has_parking = st.checkbox("Parking", value=False, disabled=True)
        has_ac = st.checkbox("Air Conditioning", value=False, disabled=True)
        has_washer = st.checkbox("Washer/Dryer", value=False, disabled=True)

    # Warning for non-entire homes
    if room_type != "Entire home/apt":
        st.warning(
            "⚠️ **Note**: The current model is optimized for entire homes. Predictions for private or shared rooms may be less accurate."
        )

    st.markdown("---")

    # Predict button
    if st.button("🔮 Predict Price", type="primary"):
        with st.spinner("Generating prediction..."):
            # Get predictions
            prediction_results = get_price_prediction(
                trace, neighborhoods_dict, neighborhood, accommodates
            )

            # Display results
            display_prediction_results(
                prediction_results, data, neighborhood, accommodates
            )

    # Show example predictions
    st.markdown("---")
    st.markdown("### 📊 Sample Predictions by Neighborhood")

    show_sample_predictions(data, trace, neighborhoods_dict, accommodates=4)


def get_price_prediction(trace, neighborhoods_dict, neighborhood, accommodates):
    """
    Generate price prediction with uncertainty

    Args:
        trace: PyMC trace
        neighborhoods_dict: Neighborhood name to index mapping
        neighborhood: Selected neighborhood
        accommodates: Number of guests

    Returns:
        Dictionary with prediction results
    """

    # Get neighborhood index
    neighborhood_idx = neighborhoods_dict[neighborhood]

    # Get posterior samples
    alpha_samples = (
        trace.posterior["alpha"].sel(alpha_dim_0=neighborhood_idx).values.flatten()
    )
    beta_samples = (
        trace.posterior["beta"].sel(beta_dim_0=neighborhood_idx).values.flatten()
    )

    # Compute log price
    log_price_samples = alpha_samples + beta_samples * accommodates

    # Back-transform to original scale
    price_samples = np.exp(log_price_samples)

    # Compute statistics
    price_median = np.median(price_samples)
    price_mean = np.mean(price_samples)
    price_std = np.std(price_samples)

    # Confidence intervals
    ci_50 = np.percentile(price_samples, [25, 75])
    ci_80 = np.percentile(price_samples, [10, 90])
    ci_90 = np.percentile(price_samples, [5, 95])
    ci_95 = np.percentile(price_samples, [2.5, 97.5])

    return {
        "price_samples": price_samples,
        "price_median": price_median,
        "price_mean": price_mean,
        "price_std": price_std,
        "ci_50": ci_50,
        "ci_80": ci_80,
        "ci_90": ci_90,
        "ci_95": ci_95,
        "neighborhood": neighborhood,
        "accommodates": accommodates,
    }


def display_prediction_results(results, data, neighborhood, accommodates):
    """
    Display prediction results with visualizations

    Args:
        results: Prediction results dictionary
        data: Full dataset
        neighborhood: Selected neighborhood
        accommodates: Number of guests
    """

    # Main prediction card
    neighborhood_data = data[data["neighbourhood_cleansed"] == neighborhood]
    neighborhood_avg = neighborhood_data["price_clean"].mean()

    if neighborhood_avg > 0:
        comparison_pct = (
            (results["price_median"] - neighborhood_avg) / neighborhood_avg
        ) * 100
        comparison_text = f"{'Above' if comparison_pct > 0 else 'Below'} neighborhood average by {abs(comparison_pct):.1f}%"
    else:
        comparison_text = None

    st.markdown(
        create_prediction_card(
            results["price_median"],
            results["ci_90"][0],
            results["ci_90"][1],
            comparison_text,
        ),
        unsafe_allow_html=True,
    )

    # Detailed statistics
    st.markdown("### 📈 Detailed Statistics")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Median Price",
            f"${results['price_median']:.0f}",
            help="50th percentile of predicted price distribution",
        )

    with col2:
        st.metric(
            "Mean Price",
            f"${results['price_mean']:.0f}",
            help="Average of predicted price distribution",
        )

    with col3:
        st.metric(
            "Uncertainty (Std Dev)",
            f"±${results['price_std']:.0f}",
            help="Standard deviation of predictions",
        )

    with col4:
        st.metric(
            "Neighborhood Avg",
            f"${neighborhood_avg:.0f}",
            delta=f"{comparison_pct:+.1f}%" if neighborhood_avg > 0 else None,
            help="Average price in this neighborhood",
        )

    # Confidence intervals
    st.markdown("### 🎯 Confidence Intervals")

    ci_data = pd.DataFrame(
        {
            "Confidence Level": ["50%", "80%", "90%", "95%"],
            "Lower Bound": [
                results["ci_50"][0],
                results["ci_80"][0],
                results["ci_90"][0],
                results["ci_95"][0],
            ],
            "Upper Bound": [
                results["ci_50"][1],
                results["ci_80"][1],
                results["ci_90"][1],
                results["ci_95"][1],
            ],
        }
    )

    ci_data["Range"] = ci_data["Upper Bound"] - ci_data["Lower Bound"]
    ci_data["Lower Bound"] = ci_data["Lower Bound"].map("${:.0f}".format)
    ci_data["Upper Bound"] = ci_data["Upper Bound"].map("${:.0f}".format)
    ci_data["Range"] = ci_data["Range"].map("${:.0f}".format)

    st.dataframe(ci_data, use_container_width=True, hide_index=True)

    # Visualizations
    st.markdown("### 📊 Prediction Distribution")

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Histogram of predictions
    axes[0].hist(
        results["price_samples"],
        bins=50,
        density=True,
        alpha=0.7,
        color="steelblue",
        edgecolor="black",
    )
    axes[0].axvline(
        results["price_median"],
        color="red",
        linestyle="--",
        linewidth=2,
        label=f'Median: ${results["price_median"]:.0f}',
    )
    axes[0].axvline(
        results["ci_90"][0], color="orange", linestyle=":", linewidth=2, label="90% CI"
    )
    axes[0].axvline(results["ci_90"][1], color="orange", linestyle=":", linewidth=2)
    axes[0].set_xlabel("Predicted Price ($/night)", fontsize=12)
    axes[0].set_ylabel("Probability Density", fontsize=12)
    axes[0].set_title("Price Distribution", fontsize=14, fontweight="bold")
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    # Comparison with neighborhood
    neighborhood_prices = neighborhood_data["price_clean"].values
    axes[1].hist(
        neighborhood_prices,
        bins=30,
        density=True,
        alpha=0.5,
        color="gray",
        edgecolor="black",
        label="Actual Neighborhood Prices",
    )
    axes[1].hist(
        results["price_samples"],
        bins=50,
        density=True,
        alpha=0.7,
        color="steelblue",
        edgecolor="black",
        label="Predicted Distribution",
    )
    axes[1].axvline(
        results["price_median"],
        color="red",
        linestyle="--",
        linewidth=2,
        label="Your Prediction",
    )
    axes[1].set_xlabel("Price ($/night)", fontsize=12)
    axes[1].set_ylabel("Probability Density", fontsize=12)
    axes[1].set_title("Your Property vs. Neighborhood", fontsize=14, fontweight="bold")
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    st.pyplot(fig)

    # Pricing strategies
    st.markdown("### 💡 Pricing Strategy Recommendations")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            f"""
        <div class="feature-card">
            <h4>🎯 Conservative</h4>
            <p><strong>${results['ci_90'][0]:.0f}/night</strong></p>
            <p>Set at lower bound for maximum occupancy. Best for new listings building reviews.</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
        <div class="feature-card">
            <h4>⚖️ Balanced</h4>
            <p><strong>${results['price_median']:.0f}/night</strong></p>
            <p>Median prediction balancing revenue and occupancy. Recommended for most hosts.</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            f"""
        <div class="feature-card">
            <h4>🚀 Aggressive</h4>
            <p><strong>${results['ci_90'][1]:.0f}/night</strong></p>
            <p>Set at upper bound for maximum revenue. Best for established listings with strong reviews.</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    # Reliability assessment
    st.markdown("### ⚠️ Prediction Reliability")

    reliability_score, warnings = assess_prediction_reliability(
        results, neighborhood_data, accommodates
    )

    if reliability_score >= 0.8:
        st.success(
            f"✅ **High Reliability** (Score: {reliability_score:.2f}) - This prediction is well-supported by data."
        )
    elif reliability_score >= 0.5:
        st.warning(
            f"⚠️ **Moderate Reliability** (Score: {reliability_score:.2f}) - Use with caution."
        )
    else:
        st.error(
            f"🛑 **Low Reliability** (Score: {reliability_score:.2f}) - Consider this estimate with significant uncertainty."
        )

    if warnings:
        for warning in warnings:
            st.warning(warning)


def assess_prediction_reliability(results, neighborhood_data, accommodates):
    """
    Assess the reliability of the prediction

    Args:
        results: Prediction results
        neighborhood_data: Data for the neighborhood
        accommodates: Number of guests

    Returns:
        tuple: (reliability_score, list of warnings)
    """

    score = 1.0
    warnings = []

    # Check sample size
    n_listings = len(neighborhood_data)
    if n_listings < 5:
        score *= 0.3
        warnings.append(
            f"⚠️ Very few listings in this neighborhood (n={n_listings}). Prediction highly uncertain."
        )
    elif n_listings < 20:
        score *= 0.7
        warnings.append(
            f"⚠️ Limited data for this neighborhood (n={n_listings}). Moderate uncertainty."
        )

    # Check if accommodates is within typical range
    typical_accommodates = neighborhood_data["accommodates"].values
    if accommodates > typical_accommodates.max():
        score *= 0.6
        warnings.append(
            f"⚠️ Property capacity ({accommodates}) exceeds typical for this neighborhood. Extrapolating beyond data."
        )

    # Check prediction certainty (width of CI)
    ci_width = results["ci_90"][1] - results["ci_90"][0]
    relative_uncertainty = ci_width / results["price_median"]

    if relative_uncertainty > 0.8:
        score *= 0.5
        warnings.append(
            f"⚠️ Large uncertainty in prediction (90% CI spans ${ci_width:.0f}). Model has low confidence."
        )
    elif relative_uncertainty > 0.5:
        score *= 0.8
        warnings.append(
            f"⚠️ Moderate uncertainty in prediction (90% CI spans ${ci_width:.0f})."
        )

    # Check if price is extreme
    if results["price_median"] > 300:
        score *= 0.4
        warnings.append(
            "🛑 Predicted price > $300. Model not validated for luxury properties. Use with extreme caution."
        )

    return score, warnings


def show_sample_predictions(data, trace, neighborhoods_dict, accommodates=4):
    """
    Show sample predictions for popular neighborhoods

    Args:
        data: Full dataset
        trace: PyMC trace
        neighborhoods_dict: Neighborhood mapping
        accommodates: Number of guests for predictions
    """

    # Get top neighborhoods by listing count
    top_neighborhoods = (
        data.groupby("neighbourhood_cleansed")
        .size()
        .sort_values(ascending=False)
        .head(10)
        .index.tolist()
    )

    # Generate predictions
    predictions = []

    for neighborhood in top_neighborhoods:
        result = get_price_prediction(
            trace, neighborhoods_dict, neighborhood, accommodates
        )

        predictions.append(
            {
                "Neighborhood": neighborhood,
                "Predicted Price": f"${result['price_median']:.0f}",
                "90% CI": f"${result['ci_90'][0]:.0f} - ${result['ci_90'][1]:.0f}",
                "Listings": len(data[data["neighbourhood_cleansed"] == neighborhood]),
                "Avg Actual": f"${data[data['neighbourhood_cleansed'] == neighborhood]['price_clean'].mean():.0f}",
            }
        )

    predictions_df = pd.DataFrame(predictions)

    st.dataframe(predictions_df, use_container_width=True, hide_index=True)

    st.info(
        f"💡 **Note**: These predictions are for properties accommodating {accommodates} guests."
    )

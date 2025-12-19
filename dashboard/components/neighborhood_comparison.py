"""
Neighborhood Comparison Component
Side-by-side comparison of Seattle neighborhoods for investment analysis
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def neighborhood_comparison_page():
    """Neighborhood comparison page with side-by-side analysis"""

    st.markdown(
        """
    <div class="custom-card">
        <h2>📍 Neighborhood Comparison</h2>
        <p>
            Compare multiple neighborhoods side-by-side to identify the best
            opportunities for your investment or listing strategy.
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Check if data is loaded
    if not st.session_state.data_loaded:
        st.warning("Please wait for data to load on the home page first.")
        return

    data = st.session_state.data
    neighborhoods_list = st.session_state.neighborhoods_list

    # Neighborhood Selection
    st.markdown("### 📊 Select Neighborhoods to Compare")

    col1, col2 = st.columns(2)

    with col1:
        selected_neighborhoods = st.multiselect(
            "Choose 2-4 neighborhoods",
            options=sorted(neighborhoods_list),
            default=sorted(neighborhoods_list)[:3]
            if len(neighborhoods_list) >= 3
            else neighborhoods_list,
            max_selections=4,
            help="Select between 2 and 4 neighborhoods for comparison",
        )

    with col2:
        property_type_filter = st.selectbox(
            "Property Type",
            options=["All Types", "Entire home/apt", "Private room", "Shared room"],
            help="Filter by property type for more relevant comparisons",
        )

    if len(selected_neighborhoods) < 2:
        st.warning("Please select at least 2 neighborhoods to compare.")
        return

    # Filter data
    comparison_data = data[data["neighbourhood_cleansed"].isin(selected_neighborhoods)]

    if property_type_filter != "All Types":
        comparison_data = comparison_data[
            comparison_data["room_type"] == property_type_filter
        ]

    if len(comparison_data) == 0:
        st.error(
            "No listings found for the selected filters. Please adjust your selection."
        )
        return

    # Calculate metrics for each neighborhood
    st.markdown("---")
    st.markdown("## 📊 Comparison Results")

    # Summary metrics table
    summary_metrics = []

    for neighborhood in selected_neighborhoods:
        neighborhood_data = comparison_data[
            comparison_data["neighbourhood_cleansed"] == neighborhood
        ]

        if len(neighborhood_data) == 0:
            continue

        metrics = {
            "Neighborhood": neighborhood,
            "Listings": len(neighborhood_data),
            "Avg Price": f"${neighborhood_data['price_clean'].mean():.0f}",
            "Median Price": f"${neighborhood_data['price_clean'].median():.0f}",
            "Price Range": f"${neighborhood_data['price_clean'].min():.0f} - ${neighborhood_data['price_clean'].max():.0f}",
            "Avg Accommodates": f"{neighborhood_data['accommodates'].mean():.1f}",
            "Avg Reviews": f"{neighborhood_data['number_of_reviews'].mean():.0f}",
            "Avg Rating": f"{neighborhood_data['review_scores_rating'].mean():.1f}",
        }
        summary_metrics.append(metrics)

    summary_df = pd.DataFrame(summary_metrics)
    st.dataframe(summary_df, hide_index=True, use_container_width=True)

    # Detailed Comparison
    st.markdown("### 📈 Detailed Analysis")

    # Create metric cards
    metric_cols = st.columns(len(selected_neighborhoods))

    for idx, neighborhood in enumerate(selected_neighborhoods):
        neighborhood_data = comparison_data[
            comparison_data["neighbourhood_cleansed"] == neighborhood
        ]

        if len(neighborhood_data) == 0:
            continue

        with metric_cols[idx]:
            st.markdown(
                f"""
            <div class="custom-card" style="height: 100%;">
                <h3>{neighborhood}</h3>
            </div>
            """,
                unsafe_allow_html=True,
            )

            st.metric("Listings", f"{len(neighborhood_data):,}")
            st.metric(
                "Avg Price",
                f"${neighborhood_data['price_clean'].mean():.0f}/night",
            )
            st.metric(
                "Median Price",
                f"${neighborhood_data['price_clean'].median():.0f}/night",
            )
            st.metric(
                "Avg Reviews",
                f"{neighborhood_data['number_of_reviews'].mean():.0f}",
            )
            st.metric(
                "Avg Rating",
                f"{neighborhood_data['review_scores_rating'].mean():.2f}",
            )

    # Price Distribution Comparison
    st.markdown("### 💰 Price Distribution")

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Box plot
    neighborhood_prices = [
        comparison_data[comparison_data["neighbourhood_cleansed"] == n][
            "price_clean"
        ].values
        for n in selected_neighborhoods
        if len(comparison_data[comparison_data["neighbourhood_cleansed"] == n]) > 0
    ]

    bp = axes[0].boxplot(
        neighborhood_prices,
        labels=[n[:15] for n in selected_neighborhoods],
        patch_artist=True,
        showfliers=False,
    )

    for patch in bp["boxes"]:
        patch.set_facecolor("#77b899")
        patch.set_alpha(0.7)

    axes[0].set_ylabel("Price ($/night)", fontsize=12)
    axes[0].set_title(
        "Price Distribution by Neighborhood", fontsize=14, fontweight="bold"
    )
    axes[0].grid(True, alpha=0.3, axis="y")
    axes[0].tick_params(axis="x", rotation=45)

    # Histogram overlay
    for neighborhood in selected_neighborhoods:
        neighborhood_data = comparison_data[
            comparison_data["neighbourhood_cleansed"] == neighborhood
        ]
        if len(neighborhood_data) > 0:
            axes[1].hist(
                neighborhood_data["price_clean"],
                bins=30,
                alpha=0.5,
                label=neighborhood[:15],
                edgecolor="black",
            )

    axes[1].set_xlabel("Price ($/night)", fontsize=12)
    axes[1].set_ylabel("Frequency", fontsize=12)
    axes[1].set_title("Price Distribution Overlay", fontsize=14, fontweight="bold")
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    st.pyplot(fig)

    # Property Type Breakdown
    st.markdown("### 🏠 Property Type Distribution")

    property_type_data = []
    for neighborhood in selected_neighborhoods:
        neighborhood_data = comparison_data[
            comparison_data["neighbourhood_cleansed"] == neighborhood
        ]

        if len(neighborhood_data) == 0:
            continue

        type_counts = neighborhood_data["room_type"].value_counts()

        for room_type, count in type_counts.items():
            property_type_data.append(
                {
                    "Neighborhood": neighborhood,
                    "Property Type": room_type,
                    "Count": count,
                    "Percentage": f"{(count / len(neighborhood_data) * 100):.1f}%",
                }
            )

    if property_type_data:
        property_type_df = pd.DataFrame(property_type_data)

        # Create grouped bar chart
        fig, ax = plt.subplots(figsize=(12, 6))

        room_types = property_type_df["Property Type"].unique()
        x = np.arange(len(selected_neighborhoods))
        width = 0.8 / len(room_types)

        for idx, room_type in enumerate(room_types):
            type_data = property_type_df[property_type_df["Property Type"] == room_type]
            counts = [
                type_data[type_data["Neighborhood"] == n]["Count"].values[0]
                if len(type_data[type_data["Neighborhood"] == n]) > 0
                else 0
                for n in selected_neighborhoods
            ]

            ax.bar(
                x + idx * width,
                counts,
                width,
                label=room_type,
                alpha=0.8,
            )

        ax.set_xlabel("Neighborhood", fontsize=12)
        ax.set_ylabel("Number of Listings", fontsize=12)
        ax.set_title("Property Type Distribution", fontsize=14, fontweight="bold")
        ax.set_xticks(x + width * (len(room_types) - 1) / 2)
        ax.set_xticklabels(
            [n[:15] for n in selected_neighborhoods], rotation=45, ha="right"
        )
        ax.legend()
        ax.grid(True, alpha=0.3, axis="y")

        plt.tight_layout()
        st.pyplot(fig)

    # Review Analysis
    st.markdown("### ⭐ Review Analysis")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Average Ratings")

        rating_data = []
        for neighborhood in selected_neighborhoods:
            neighborhood_data = comparison_data[
                comparison_data["neighbourhood_cleansed"] == neighborhood
            ]

            if len(neighborhood_data) == 0:
                continue

            rating_data.append(
                {
                    "Neighborhood": neighborhood,
                    "Overall Rating": f"{neighborhood_data['review_scores_rating'].mean():.2f}",
                    "Cleanliness": f"{neighborhood_data['review_scores_cleanliness'].mean():.2f}",
                    "Location": f"{neighborhood_data['review_scores_location'].mean():.2f}",
                    "Value": f"{neighborhood_data['review_scores_value'].mean():.2f}",
                }
            )

        if rating_data:
            rating_df = pd.DataFrame(rating_data)
            st.dataframe(rating_df, hide_index=True, use_container_width=True)

    with col2:
        st.markdown("#### Review Volume")

        review_volume_data = []
        for neighborhood in selected_neighborhoods:
            neighborhood_data = comparison_data[
                comparison_data["neighbourhood_cleansed"] == neighborhood
            ]

            if len(neighborhood_data) == 0:
                continue

            review_volume_data.append(
                {
                    "Neighborhood": neighborhood,
                    "Avg Reviews": f"{neighborhood_data['number_of_reviews'].mean():.0f}",
                    "Total Reviews": f"{neighborhood_data['number_of_reviews'].sum():,}",
                    "Reviews/Month": f"{neighborhood_data['reviews_per_month'].mean():.2f}",
                }
            )

        if review_volume_data:
            review_volume_df = pd.DataFrame(review_volume_data)
            st.dataframe(review_volume_df, hide_index=True, use_container_width=True)

    # Investment Opportunity Score
    st.markdown("### 🎯 Investment Opportunity Score")

    st.markdown(
        """
    This score ranks neighborhoods based on a combination of factors:
    - **Price**: Higher average prices = higher revenue potential
    - **Reviews**: More reviews = higher demand/occupancy
    - **Ratings**: Higher ratings = better guest satisfaction
    - **Competition**: Fewer listings = less competition
    """
    )

    opportunity_scores = []

    for neighborhood in selected_neighborhoods:
        neighborhood_data = comparison_data[
            comparison_data["neighbourhood_cleansed"] == neighborhood
        ]

        if len(neighborhood_data) == 0:
            continue

        # Normalize metrics (0-100 scale)
        avg_price = neighborhood_data["price_clean"].mean()
        avg_reviews = neighborhood_data["number_of_reviews"].mean()
        avg_rating = neighborhood_data["review_scores_rating"].mean()
        listing_count = len(neighborhood_data)

        # Calculate score components
        price_score = min(avg_price / 3, 100)  # Cap at $300/night = 100
        review_score = min(avg_reviews / 2, 100)  # Cap at 200 reviews = 100
        rating_score = (avg_rating / 100) * 100 if not pd.isna(avg_rating) else 0
        competition_score = max(
            100 - (listing_count / 10), 0
        )  # More listings = lower score

        # Weighted average
        total_score = (
            price_score * 0.35
            + review_score * 0.25
            + rating_score * 0.25
            + competition_score * 0.15
        )

        opportunity_scores.append(
            {
                "Neighborhood": neighborhood,
                "Total Score": f"{total_score:.1f}",
                "Price Score": f"{price_score:.1f}",
                "Demand Score": f"{review_score:.1f}",
                "Quality Score": f"{rating_score:.1f}",
                "Competition Score": f"{competition_score:.1f}",
                "Rank": 0,  # Will be filled after sorting
            }
        )

    if opportunity_scores:
        # Sort and rank
        opportunity_df = pd.DataFrame(opportunity_scores)
        opportunity_df["Total Score"] = opportunity_df["Total Score"].astype(float)
        opportunity_df = opportunity_df.sort_values("Total Score", ascending=False)
        opportunity_df["Rank"] = range(1, len(opportunity_df) + 1)

        # Display ranked table
        display_df = opportunity_df[
            [
                "Rank",
                "Neighborhood",
                "Total Score",
                "Price Score",
                "Demand Score",
                "Quality Score",
                "Competition Score",
            ]
        ]
        st.dataframe(display_df, hide_index=True, use_container_width=True)

        # Visualization
        fig, ax = plt.subplots(figsize=(10, 6))

        neighborhoods_ordered = opportunity_df["Neighborhood"].values
        scores = opportunity_df["Total Score"].values

        colors = [
            "#2e7d32" if i == 0 else "#77b899" if i < len(scores) / 2 else "#ffc107"
            for i in range(len(scores))
        ]

        bars = ax.barh(neighborhoods_ordered, scores, color=colors, alpha=0.8)

        ax.set_xlabel("Opportunity Score", fontsize=12)
        ax.set_ylabel("Neighborhood", fontsize=12)
        ax.set_title("Investment Opportunity Ranking", fontsize=14, fontweight="bold")
        ax.grid(True, alpha=0.3, axis="x")

        # Add value labels
        for i, (neighborhood, score) in enumerate(zip(neighborhoods_ordered, scores)):
            ax.text(score + 1, i, f"{score:.1f}", va="center", fontsize=10)

        plt.tight_layout()
        st.pyplot(fig)

    # Recommendations
    st.markdown("### 💡 Recommendations")

    if opportunity_scores:
        top_neighborhood = opportunity_df.iloc[0]["Neighborhood"]
        top_score = opportunity_df.iloc[0]["Total Score"]

        st.success(
            f"""
        **🏆 Top Opportunity: {top_neighborhood}**

        Based on the comprehensive analysis, {top_neighborhood} scores highest ({top_score:.1f}/100)
        for investment potential. This neighborhood offers the best combination of:
        - Competitive pricing potential
        - Strong demand indicators
        - High guest satisfaction
        - Manageable competition levels
        """
        )

        # Specific recommendations for each neighborhood
        for idx, row in opportunity_df.iterrows():
            neighborhood = row["Neighborhood"]
            neighborhood_data = comparison_data[
                comparison_data["neighbourhood_cleansed"] == neighborhood
            ]

            avg_price = neighborhood_data["price_clean"].mean()
            avg_reviews = neighborhood_data["number_of_reviews"].mean()

            with st.expander(f"📍 {neighborhood} - Detailed Insights"):
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("**Strengths:**")
                    if avg_price > data["price_clean"].mean():
                        st.markdown("- ✅ Above-average pricing potential")
                    if avg_reviews > data["number_of_reviews"].mean():
                        st.markdown("- ✅ High demand/occupancy indicators")
                    if (
                        len(neighborhood_data)
                        < data.groupby("neighbourhood_cleansed").size().median()
                    ):
                        st.markdown("- ✅ Lower competition")

                with col2:
                    st.markdown("**Considerations:**")
                    if avg_price < data["price_clean"].mean():
                        st.markdown("- ⚠️ Below-average prices")
                    if avg_reviews < data["number_of_reviews"].mean():
                        st.markdown("- ⚠️ Lower demand indicators")
                    if (
                        len(neighborhood_data)
                        > data.groupby("neighbourhood_cleansed").size().median()
                    ):
                        st.markdown("- ⚠️ High competition")

                st.markdown(
                    f"""
                **Suggested Strategy:**
                - Target nightly rate: ${avg_price:.0f} (neighborhood average)
                - Expected annual bookings: ~{avg_reviews * 4:.0f} nights (based on review patterns)
                - Focus on: {"differentiation" if len(neighborhood_data) > 100 else "quality and marketing"}
                """
                )

    st.info(
        """
    **💡 Pro Tips:**
    - Consider multiple factors beyond just price when choosing a neighborhood
    - High review counts often indicate better occupancy rates
    - Less competition can mean easier market entry but may also indicate lower demand
    - Visit neighborhoods in person to assess location quality and amenities
    - Check local regulations and HOA rules for short-term rental restrictions
    """
    )

"""
Feature Impact Calculator Component
Calculate the value of adding amenities and features to properties
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def feature_impact_page():
    """Feature impact calculator page"""

    st.markdown(
        """
    <div class="custom-card">
        <h2>⚙️ Feature Impact Calculator</h2>
        <p>
            Calculate the value of adding amenities and features to your property.
            Understand which investments provide the best ROI.
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

    # Feature Impact Overview
    st.markdown("## 💡 Property Features & Price Impact")

    st.info(
        """
    **How It Works**: This calculator compares properties with and without specific features
    to estimate the price premium associated with each amenity. Values are based on actual
    market data from similar properties in Seattle.
    """
    )

    # Base Property Setup
    st.markdown("### 🏠 Your Base Property")

    col1, col2 = st.columns(2)

    with col1:
        base_neighborhood = st.selectbox(
            "Neighborhood",
            options=sorted(st.session_state.neighborhoods_list),
            help="Select the neighborhood of your property",
        )

        base_accommodates = st.slider(
            "Number of Guests",
            min_value=1,
            max_value=10,
            value=4,
            help="How many guests can the property accommodate?",
        )

        base_bedrooms = st.slider(
            "Number of Bedrooms",
            min_value=0,
            max_value=6,
            value=2,
            help="Studio = 0, then 1, 2, 3+",
        )

    with col2:
        base_room_type = st.selectbox(
            "Property Type",
            options=["Entire home/apt", "Private room", "Shared room"],
            help="Type of space being rented",
        )

        # Calculate base price
        base_properties = data[
            (data["neighbourhood_cleansed"] == base_neighborhood)
            & (data["accommodates"] == base_accommodates)
            & (data["room_type"] == base_room_type)
        ]

        if len(base_properties) > 0:
            base_price = base_properties["price_clean"].median()
        else:
            # Fallback to neighborhood average
            neighborhood_properties = data[
                data["neighbourhood_cleansed"] == base_neighborhood
            ]
            if len(neighborhood_properties) > 0:
                base_price = neighborhood_properties["price_clean"].median()
            else:
                base_price = data["price_clean"].median()

        st.metric(
            "Estimated Base Price",
            f"${base_price:.0f}/night",
            help="Starting price before adding amenities",
        )

        st.metric(
            "Similar Listings",
            (
                f"{len(base_properties):,}"
                if len(base_properties) > 0
                else "Using neighborhood average"
            ),
        )

    # Feature Categories
    st.markdown("---")
    st.markdown("## ⚙️ Select Features to Add")

    st.markdown(
        """
    Choose which amenities and features you want to add to your property.
    The calculator will estimate the price impact of each addition.
    """
    )

    # Essential Amenities
    with st.expander("🔧 Essential Amenities", expanded=True):
        col1, col2, col3 = st.columns(3)

        with col1:
            has_wifi = st.checkbox("WiFi", value=True)
            has_kitchen = st.checkbox("Kitchen", value=True)
            has_heating = st.checkbox("Heating", value=True)

        with col2:
            has_ac = st.checkbox("Air Conditioning")
            has_washer = st.checkbox("Washer")
            has_dryer = st.checkbox("Dryer")

        with col3:
            has_tv = st.checkbox("TV")
            has_parking = st.checkbox("Free Parking")
            has_elevator = st.checkbox("Elevator")

    # Comfort & Convenience
    with st.expander("🛋️ Comfort & Convenience"):
        col1, col2, col3 = st.columns(3)

        with col1:
            has_workspace = st.checkbox("Dedicated Workspace")
            has_coffee_maker = st.checkbox("Coffee Maker")
            has_dishwasher = st.checkbox("Dishwasher")

        with col2:
            has_iron = st.checkbox("Iron & Board")
            has_hair_dryer = st.checkbox("Hair Dryer")
            has_essentials = st.checkbox("Essentials Kit")

        with col3:
            has_hangers = st.checkbox("Hangers")
            has_shampoo = st.checkbox("Shampoo/Soap")
            has_hot_water = st.checkbox("Hot Water", value=True)

    # Safety & Security
    with st.expander("🔒 Safety & Security"):
        col1, col2, col3 = st.columns(3)

        with col1:
            has_smoke_alarm = st.checkbox("Smoke Alarm", value=True)
            has_co_alarm = st.checkbox("Carbon Monoxide Alarm")
            has_fire_extinguisher = st.checkbox("Fire Extinguisher")

        with col2:
            has_first_aid = st.checkbox("First Aid Kit")
            has_lock = st.checkbox("Lockbox/Smart Lock")
            has_security_cameras = st.checkbox("Security Cameras (exterior)")

        with col3:
            pass  # Empty column for spacing

    # Premium Features
    with st.expander("✨ Premium Features"):
        col1, col2, col3 = st.columns(3)

        with col1:
            has_pool = st.checkbox("Pool")
            has_hot_tub = st.checkbox("Hot Tub")
            has_gym = st.checkbox("Gym Access")

        with col2:
            has_waterfront = st.checkbox("Waterfront")
            has_view = st.checkbox("Great View")
            has_patio = st.checkbox("Patio/Balcony")

        with col3:
            has_bbq = st.checkbox("BBQ Grill")
            has_fireplace = st.checkbox("Fireplace")
            has_ev_charger = st.checkbox("EV Charger")

    # Calculate Impact
    if st.button("📊 Calculate Feature Impact", type="primary"):
        st.markdown("---")
        st.markdown("## 💰 Feature Impact Results")

        # Define feature impact estimates (based on typical market premiums)
        feature_impacts = {
            # Essential Amenities (baseline, smaller impact)
            "WiFi": 0.02,
            "Kitchen": 0.05,
            "Heating": 0.02,
            "Air Conditioning": 0.08,
            "Washer": 0.05,
            "Dryer": 0.03,
            "TV": 0.02,
            "Free Parking": 0.10,
            "Elevator": 0.03,
            # Comfort & Convenience
            "Dedicated Workspace": 0.05,
            "Coffee Maker": 0.01,
            "Dishwasher": 0.03,
            "Iron & Board": 0.01,
            "Hair Dryer": 0.01,
            "Essentials Kit": 0.02,
            "Hangers": 0.00,
            "Shampoo/Soap": 0.01,
            "Hot Water": 0.02,
            # Safety & Security
            "Smoke Alarm": 0.01,
            "Carbon Monoxide Alarm": 0.01,
            "Fire Extinguisher": 0.01,
            "First Aid Kit": 0.00,
            "Lockbox/Smart Lock": 0.02,
            "Security Cameras (exterior)": 0.02,
            # Premium Features
            "Pool": 0.15,
            "Hot Tub": 0.12,
            "Gym Access": 0.06,
            "Waterfront": 0.25,
            "Great View": 0.15,
            "Patio/Balcony": 0.08,
            "BBQ Grill": 0.04,
            "Fireplace": 0.06,
            "EV Charger": 0.05,
        }

        # Map checkbox states to features
        selected_features = {
            "WiFi": has_wifi,
            "Kitchen": has_kitchen,
            "Heating": has_heating,
            "Air Conditioning": has_ac,
            "Washer": has_washer,
            "Dryer": has_dryer,
            "TV": has_tv,
            "Free Parking": has_parking,
            "Elevator": has_elevator,
            "Dedicated Workspace": has_workspace,
            "Coffee Maker": has_coffee_maker,
            "Dishwasher": has_dishwasher,
            "Iron & Board": has_iron,
            "Hair Dryer": has_hair_dryer,
            "Essentials Kit": has_essentials,
            "Hangers": has_hangers,
            "Shampoo/Soap": has_shampoo,
            "Hot Water": has_hot_water,
            "Smoke Alarm": has_smoke_alarm,
            "Carbon Monoxide Alarm": has_co_alarm,
            "Fire Extinguisher": has_fire_extinguisher,
            "First Aid Kit": has_first_aid,
            "Lockbox/Smart Lock": has_lock,
            "Security Cameras (exterior)": has_security_cameras,
            "Pool": has_pool,
            "Hot Tub": has_hot_tub,
            "Gym Access": has_gym,
            "Waterfront": has_waterfront,
            "Great View": has_view,
            "Patio/Balcony": has_patio,
            "BBQ Grill": has_bbq,
            "Fireplace": has_fireplace,
            "EV Charger": has_ev_charger,
        }

        # Calculate total impact
        total_impact_pct = sum(
            [
                impact
                for feature, impact in feature_impacts.items()
                if selected_features.get(feature, False)
            ]
        )

        total_impact_dollars = base_price * total_impact_pct
        final_price = base_price + total_impact_dollars

        # Display summary
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Base Price", f"${base_price:.0f}/night")

        with col2:
            st.metric(
                "Total Impact",
                f"+${total_impact_dollars:.0f}/night",
                f"+{total_impact_pct:.1%}",
            )

        with col3:
            st.metric("Final Price", f"${final_price:.0f}/night")

        with col4:
            annual_impact = total_impact_dollars * 365 * 0.65  # Assume 65% occupancy
            st.metric("Annual Revenue Impact", f"+${annual_impact:,.0f}/year")

        # Feature breakdown
        st.markdown("### 📋 Feature-by-Feature Breakdown")

        feature_details = []

        for feature, has_feature in selected_features.items():
            if has_feature:
                impact_pct = feature_impacts.get(feature, 0)
                impact_dollars = base_price * impact_pct
                annual_value = impact_dollars * 365 * 0.65

                # Categorize
                if feature in [
                    "WiFi",
                    "Kitchen",
                    "Heating",
                    "Air Conditioning",
                    "Washer",
                    "Dryer",
                    "TV",
                    "Free Parking",
                    "Elevator",
                ]:
                    category = "Essential"
                elif feature in [
                    "Dedicated Workspace",
                    "Coffee Maker",
                    "Dishwasher",
                    "Iron & Board",
                    "Hair Dryer",
                    "Essentials Kit",
                    "Hangers",
                    "Shampoo/Soap",
                    "Hot Water",
                ]:
                    category = "Comfort"
                elif feature in [
                    "Smoke Alarm",
                    "Carbon Monoxide Alarm",
                    "Fire Extinguisher",
                    "First Aid Kit",
                    "Lockbox/Smart Lock",
                    "Security Cameras (exterior)",
                ]:
                    category = "Safety"
                else:
                    category = "Premium"

                feature_details.append(
                    {
                        "Feature": feature,
                        "Category": category,
                        "Price Impact": f"+${impact_dollars:.0f}/night",
                        "Impact %": f"+{impact_pct:.1%}",
                        "Annual Value": f"+${annual_value:,.0f}",
                    }
                )

        if feature_details:
            features_df = pd.DataFrame(feature_details)
            # Sort by price impact
            features_df["sort_value"] = (
                features_df["Price Impact"]
                .str.replace(r"[+$,/night]", "", regex=True)
                .astype(float)
            )
            features_df = features_df.sort_values("sort_value", ascending=False).drop(
                "sort_value", axis=1
            )

            st.dataframe(features_df, hide_index=True, use_container_width=True)

            # Visualization
            fig, axes = plt.subplots(1, 2, figsize=(14, 6))

            # Bar chart by category
            category_impact = features_df.groupby("Category").agg(
                {
                    "Price Impact": lambda x: sum(
                        [
                            float(str(val).replace("+$", "").replace("/night", ""))
                            for val in x
                        ]
                    )
                }
            )

            category_colors = {
                "Essential": "#77b899",
                "Comfort": "#add8e6",
                "Safety": "#2f4f4f",
                "Premium": "#ffd700",
            }

            colors = [
                category_colors.get(cat, "#77b899") for cat in category_impact.index
            ]

            axes[0].bar(
                category_impact.index,
                category_impact["Price Impact"],
                color=colors,
                alpha=0.8,
            )
            axes[0].set_ylabel("Total Impact ($/night)", fontsize=12)
            axes[0].set_xlabel("Category", fontsize=12)
            axes[0].set_title("Impact by Category", fontsize=14, fontweight="bold")
            axes[0].grid(True, alpha=0.3, axis="y")

            # Top 10 features
            top_features = features_df.head(10).copy()
            top_features["impact_value"] = (
                top_features["Price Impact"]
                .str.replace(r"[+$,/night]", "", regex=True)
                .astype(float)
            )

            axes[1].barh(
                top_features["Feature"],
                top_features["impact_value"],
                color="#77b899",
                alpha=0.8,
            )
            axes[1].set_xlabel("Price Impact ($/night)", fontsize=12)
            axes[1].set_ylabel("Feature", fontsize=12)
            axes[1].set_title(
                "Top 10 Features by Impact", fontsize=14, fontweight="bold"
            )
            axes[1].grid(True, alpha=0.3, axis="x")

            plt.tight_layout()
            st.pyplot(fig)

        # ROI Analysis
        st.markdown("### 💵 Investment ROI Analysis")

        st.markdown(
            """
        Estimate the return on investment for adding specific features.
        This helps prioritize which improvements to make first.
        """
        )

        # Estimated costs for common improvements
        feature_costs = {
            "Air Conditioning": 3500,
            "Washer": 600,
            "Dryer": 500,
            "Parking": 0,  # Usually included with property
            "Dedicated Workspace": 500,
            "Dishwasher": 800,
            "Hot Tub": 8000,
            "Pool": 50000,
            "Gym Access": 0,  # Usually building amenity
            "Waterfront": 0,  # Property attribute
            "Great View": 0,  # Property attribute
            "Patio/Balcony": 5000,
            "BBQ Grill": 300,
            "Fireplace": 2500,
            "EV Charger": 1200,
        }

        roi_analysis = []

        for feature, has_feature in selected_features.items():
            if has_feature and feature in feature_costs:
                cost = feature_costs[feature]
                if cost > 0:  # Only show features with installation costs
                    impact_pct = feature_impacts.get(feature, 0)
                    impact_dollars = base_price * impact_pct
                    annual_value = impact_dollars * 365 * 0.65  # 65% occupancy

                    payback_months = (
                        (cost / annual_value * 12) if annual_value > 0 else float("inf")
                    )
                    roi_3year = (annual_value * 3 - cost) / cost if cost > 0 else 0

                    roi_analysis.append(
                        {
                            "Feature": feature,
                            "Installation Cost": f"${cost:,}",
                            "Annual Value": f"${annual_value:,.0f}",
                            "Payback Period": (
                                f"{payback_months:.1f} months"
                                if payback_months < 120
                                else ">10 years"
                            ),
                            "3-Year ROI": f"{roi_3year:.0%}",
                            "Recommendation": (
                                "High Priority"
                                if payback_months < 24
                                else (
                                    "Medium Priority"
                                    if payback_months < 48
                                    else "Low Priority"
                                )
                            ),
                        }
                    )

        if roi_analysis:
            roi_df = pd.DataFrame(roi_analysis)
            st.dataframe(roi_df, hide_index=True, use_container_width=True)

            st.info(
                """
            **💡 Interpretation:**
            - **Payback Period**: How long until the feature pays for itself
            - **3-Year ROI**: Total return over 3 years relative to installation cost
            - **High Priority**: Pays back in < 2 years
            - **Medium Priority**: Pays back in 2-4 years
            - **Low Priority**: Pays back in > 4 years
            """
            )

        # Recommendations
        st.markdown("### 💡 Personalized Recommendations")

        # Determine missing high-value features
        missing_high_value = []
        for feature, impact in sorted(
            feature_impacts.items(), key=lambda x: x[1], reverse=True
        )[:10]:
            if not selected_features.get(feature, False):
                missing_high_value.append((feature, impact))

        if missing_high_value:
            st.success("**🎯 Top Missing Features to Consider:**")
            for feature, impact in missing_high_value[:5]:
                estimated_impact = base_price * impact
                st.markdown(
                    f"- **{feature}**: +${estimated_impact:.0f}/night (+{impact:.1%})"
                )

        # Overall assessment
        if total_impact_pct > 0.30:
            st.success(
                f"""
            **✅ Well-Equipped Property**

            Your property has {sum(selected_features.values())} amenities providing a {total_impact_pct:.0%} price
            premium over basic listings. This should command strong pricing in the market.
            """
            )
        elif total_impact_pct > 0.15:
            st.warning(
                f"""
            **⚠️ Moderately Equipped Property**

            Your property has {sum(selected_features.values())} amenities providing a {total_impact_pct:.0%} price
            premium. Consider adding premium features to increase revenue potential.
            """
            )
        else:
            st.error(
                f"""
            **❌ Basic Property**

            Your property has {sum(selected_features.values())} amenities providing only a {total_impact_pct:.0%} price
            premium. Significant improvements needed to compete effectively in the market.
            """
            )

        # Market Positioning
        st.markdown("### 📍 Market Positioning")

        # Compare to neighborhood
        similar_listings = data[
            (data["neighbourhood_cleansed"] == base_neighborhood)
            & (data["accommodates"] == base_accommodates)
        ]

        if len(similar_listings) > 0:
            percentile = (
                (similar_listings["price_clean"] < final_price).sum()
                / len(similar_listings)
                * 100
            )

            st.markdown(
                f"""
            **Your Estimated Price**: ${final_price:.0f}/night

            This places you in the **{percentile:.0f}th percentile** of similar properties
            in {base_neighborhood}.
            """
            )

            if percentile > 75:
                st.info(
                    "💎 **Premium Positioning**: Your property is priced in the top quartile."
                )
            elif percentile > 50:
                st.info(
                    "🎯 **Above Average**: Your property is priced above the median."
                )
            elif percentile > 25:
                st.warning(
                    "📊 **Average Positioning**: Your property is near the market average."
                )
            else:
                st.warning(
                    "💵 **Value Positioning**: Your property is priced below average."
                )

    # General Tips
    st.markdown("---")
    st.markdown("### 🎓 Feature Investment Tips")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            """
        **High-ROI Investments:**
        - Free parking (if possible)
        - Air conditioning (in warm months)
        - Fast WiFi (essential for remote workers)
        - Workspace setup (low cost, high value)
        - Quality photos showcasing amenities

        **Guest Favorites:**
        - Complete kitchen
        - Washer/dryer in unit
        - Comfortable beds & linens
        - Smart TV with streaming
        - Coffee maker & supplies
        """
        )

    with col2:
        st.markdown(
            """
        **Premium Features Worth Considering:**
        - Hot tub (high impact in Seattle)
        - Water views (if available)
        - Patio/outdoor space
        - Fireplace (cozy factor)
        - Pet-friendly policies

        **Safety & Trust:**
        - Smoke & CO alarms (required)
        - Good lighting
        - Clear house rules
        - Responsive communication
        - Professional photos
        """
        )

    st.info(
        """
    **💡 Final Tips:**
    - Focus on features guests actually use (WiFi, kitchen, parking)
    - Quality matters more than quantity
    - Professional photos can showcase features effectively
    - Keep amenities well-maintained
    - Highlight unique features in your listing description
    - Monitor competitor listings to stay competitive
    """
    )

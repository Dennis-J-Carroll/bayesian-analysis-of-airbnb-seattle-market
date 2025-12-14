# MVP Dashboard Specification
## Interactive Pricing & Investment Recommendation Tool

**Purpose**: Create a minimum viable product that business users can interact with to get pricing recommendations and evaluate investment opportunities.

---

## Dashboard Requirements

### User Stories

**As an Airbnb host**, I want to:
1. Input my neighborhood and property details
2. Get a predicted price range with confidence intervals
3. Compare my property to neighborhood averages
4. See which features increase my pricing power

**As an investor**, I want to:
1. Compare investment opportunities across neighborhoods
2. See ROI projections with realistic assumptions
3. Understand risk factors and sensitivities
4. Identify undervalued properties

**As a data analyst**, I want to:
1. Validate model predictions against actual listings
2. Understand model uncertainty
3. Identify when model predictions are unreliable
4. Track model performance over time

---

## Dashboard Components

### Component 1: Price Predictor

**Inputs**:
- Neighborhood (dropdown)
- Number of guests (slider: 1-10)
- Room type (dropdown: Entire home, Private room, Shared room)
- Key amenities (checkboxes: Parking, AC, Washer/Dryer)

**Outputs**:
- **Predicted price** (median)
- **Confidence interval** (90% credible interval)
- **Neighborhood comparison**: "Your predicted price is X% above/below neighborhood average"
- **Feature impact**: "Adding parking increases price by $Y"

**Visualization**:
```
┌─────────────────────────────────────┐
│ Predicted Price: $172/night         │
│ 90% CI: [$148 - $201]               │
│                                      │
│ ████████████████░░░░ $148  $201     │
│               ▲ $172                 │
│                                      │
│ Neighborhood avg: $165/night        │
│ Your premium: +4%                    │
└─────────────────────────────────────┘
```

**Implementation**:
```python
import streamlit as st
import numpy as np
import pymc as pm

def price_predictor_component():
    st.header("Price Predictor")

    # Inputs
    neighborhood = st.selectbox("Neighborhood", neighborhoods_list)
    accommodates = st.slider("Number of Guests", 1, 10, 4)
    room_type = st.selectbox("Room Type", ["Entire home/apt", "Private room", "Shared room"])

    # Model prediction
    neighborhood_idx = neighborhoods_dict[neighborhood]
    alpha_samples = trace.posterior['alpha'].sel(alpha_dim_0=neighborhood_idx).values.flatten()
    beta_samples = trace.posterior['beta'].sel(alpha_dim_0=neighborhood_idx).values.flatten()

    log_price_samples = alpha_samples + beta_samples * accommodates
    price_samples = np.exp(log_price_samples)

    # Statistics
    price_median = np.median(price_samples)
    price_ci = np.percentile(price_samples, [5, 95])

    # Neighborhood comparison
    neighborhood_mean = data[data['neighbourhood_cleansed'] == neighborhood]['price_clean'].mean()
    premium = (price_median - neighborhood_mean) / neighborhood_mean * 100

    # Display
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Predicted Price", f"${price_median:.0f}/night")

    with col2:
        st.metric("90% Confidence", f"${price_ci[0]:.0f} - ${price_ci[1]:.0f}")

    with col3:
        st.metric("vs. Neighborhood", f"{premium:+.1f}%")

    # Visualization
    fig, ax = plt.subplots(figsize=(10, 3))
    ax.hist(price_samples, bins=50, density=True, alpha=0.7, color='steelblue', edgecolor='black')
    ax.axvline(price_median, color='red', linestyle='--', linewidth=2, label=f'Median: ${price_median:.0f}')
    ax.axvline(price_ci[0], color='orange', linestyle=':', linewidth=2, label=f'90% CI')
    ax.axvline(price_ci[1], color='orange', linestyle=':', linewidth=2)
    ax.set_xlabel('Predicted Price ($/night)')
    ax.set_ylabel('Probability Density')
    ax.legend()
    st.pyplot(fig)

    # Reliability warning
    if price_median > 300:
        st.warning("⚠️ Warning: Predicted price > $300. Model may underestimate luxury properties.")
    elif len(data[data['neighbourhood_cleansed'] == neighborhood]) < 10:
        st.warning("⚠️ Warning: Limited data for this neighborhood. Prediction has high uncertainty.")
```

---

### Component 2: Investment Analyzer

**Inputs**:
- Neighborhood (dropdown)
- Investment amount ($10k - $100k)
- Time horizon (1-5 years)
- Risk tolerance (Conservative / Moderate / Aggressive)

**Outputs**:
- **Expected ROI** with confidence intervals
- **Sensitivity analysis**: "If conversion rate is 40% instead of 60%, ROI drops to X%"
- **Risk breakdown**: Market risk, competitive risk, regulatory risk
- **Recommendation**: "Invest" / "Reconsider" / "Do Not Invest"

**Visualization**:
```
┌──────────────────────────────────────────┐
│ Investment: $50,000 in Meadowbrook        │
│                                           │
│ Expected 3-Year ROI: -78%                │
│ 90% CI: [-135%, -15%]                    │
│                                           │
│ Risk Factors:                             │
│ ████████████████░░ Conversion rate  80%  │
│ ████████████░░░░░░ Market risk      60%  │
│ ██████░░░░░░░░░░░░ Regulatory      30%  │
│                                           │
│ ⚠️ RECOMMENDATION: DO NOT INVEST          │
│ Probability of loss > 50%: 88%            │
└──────────────────────────────────────────┘
```

**Implementation**:
```python
def investment_analyzer_component():
    st.header("Investment Analyzer")

    # Inputs
    neighborhood = st.selectbox("Target Neighborhood", neighborhoods_list, key='invest_neighborhood')
    investment = st.slider("Investment Amount ($)", 10000, 100000, 50000, step=5000)
    time_horizon = st.slider("Time Horizon (years)", 1, 5, 3)
    risk_tolerance = st.select_slider("Risk Tolerance", ["Conservative", "Moderate", "Aggressive"])

    # Assumptions based on risk tolerance
    if risk_tolerance == "Conservative":
        conversion_rate = 0.30
        occupancy_boost = 0.00
        market_growth = 0.00
    elif risk_tolerance == "Moderate":
        conversion_rate = 0.40
        occupancy_boost = 0.02
        market_growth = 0.02
    else:  # Aggressive
        conversion_rate = 0.60
        occupancy_boost = 0.05
        market_growth = 0.05

    # Run ROI simulation
    roi_results = monte_carlo_roi_simulation(
        neighborhood=neighborhood,
        investment=investment,
        time_horizon=time_horizon,
        conversion_rate=conversion_rate,
        n_simulations=1000
    )

    # Statistics
    roi_mean = roi_results['roi'].mean()
    roi_median = roi_results['roi'].median()
    roi_ci = np.percentile(roi_results['roi'], [5, 95])
    prob_positive = (roi_results['roi'] > 0).mean()
    prob_loss_50 = (roi_results['roi'] < -0.5).mean()

    # Recommendation logic
    if roi_median > 0.20 and prob_positive > 0.7:
        recommendation = "✅ INVEST"
        color = "green"
    elif roi_median > 0 and prob_positive > 0.5:
        recommendation = "⚠️ RECONSIDER"
        color = "orange"
    else:
        recommendation = "🛑 DO NOT INVEST"
        color = "red"

    # Display
    st.markdown(f"### {recommendation}")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Expected ROI", f"{roi_median:.1%}")

    with col2:
        st.metric("90% CI", f"[{roi_ci[0]:.1%}, {roi_ci[1]:.1%}]")

    with col3:
        st.metric("Prob. of Profit", f"{prob_positive:.1%}")

    # ROI distribution plot
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.hist(roi_results['roi'] * 100, bins=50, density=True, alpha=0.7, color=color, edgecolor='black')
    ax.axvline(0, color='black', linestyle='--', linewidth=2, label='Break-even')
    ax.axvline(roi_median * 100, color='red', linestyle='-', linewidth=2, label=f'Median: {roi_median:.1%}')
    ax.set_xlabel('ROI (%)')
    ax.set_ylabel('Probability Density')
    ax.set_title('ROI Distribution (1,000 Simulations)')
    ax.legend()
    st.pyplot(fig)

    # Risk breakdown
    st.subheader("Risk Factors")

    risk_factors = {
        'Conversion Rate Uncertainty': 0.80,
        'Market Volatility': 0.60,
        'Competitive Response': 0.55,
        'Regulatory Risk': 0.30,
        'Execution Risk': 0.40
    }

    for risk_name, risk_level in risk_factors.items():
        st.write(f"**{risk_name}**: {'█' * int(risk_level * 20)}{'░' * (20 - int(risk_level * 20))} {risk_level:.0%}")

    # Sensitivity analysis
    st.subheader("Sensitivity Analysis")

    sensitivity_data = {
        'Parameter': ['Conversion Rate', 'Market Growth', 'Competitive Response'],
        'Base Case': [0.40, 0.02, 0.60],
        'Optimistic': [0.60, 0.08, 0.30],
        'Pessimistic': [0.20, -0.05, 0.90],
        'ROI if Optimistic': ['-45%', '-72%', '-65%'],
        'ROI if Pessimistic': ['-95%', '-88%', '-92%']
    }

    st.table(sensitivity_data)

    # Key insights
    st.subheader("Key Insights")

    if prob_loss_50 > 0.7:
        st.error(f"High risk: {prob_loss_50:.0%} chance of losing more than 50% of investment")

    if roi_median < -0.5:
        st.error("Expected outcome is significant loss. Investment not recommended.")

    annual_gain = investment * roi_median / time_horizon
    if annual_gain < 0:
        st.warning(f"Expected annual loss: ${-annual_gain:,.0f}/year")
```

---

### Component 3: Neighborhood Comparison

**Purpose**: Compare multiple neighborhoods side-by-side

**Inputs**:
- Select 2-4 neighborhoods (multi-select)
- Property characteristics (accommodates, room type)

**Outputs**:
- Side-by-side price predictions
- Market metrics (avg occupancy, competition level, growth rate)
- Strategic score ranking

**Visualization**:
```
┌────────────────────────────────────────────────┐
│ Neighborhood Comparison                         │
│                                                 │
│            Capitol Hill  Meadowbrook  Fremont  │
│ Price         $185         $142        $156    │
│ Occupancy     85%          75%         80%     │
│ Competition   High         Low         Medium  │
│ Growth        5%           12%         8%      │
│ Strategic     65           78          71      │
│ Score                                          │
└────────────────────────────────────────────────┘
```

**Implementation**:
```python
def neighborhood_comparison_component():
    st.header("Neighborhood Comparison")

    # Inputs
    selected_neighborhoods = st.multiselect(
        "Select Neighborhoods to Compare (2-4)",
        neighborhoods_list,
        default=["Capitol Hill", "Meadowbrook", "Fremont"]
    )

    if len(selected_neighborhoods) < 2:
        st.warning("Please select at least 2 neighborhoods")
        return

    accommodates = st.slider("Property Capacity (Guests)", 1, 10, 4, key='compare_accommodates')

    # Calculate predictions for each neighborhood
    comparison_data = []

    for neighborhood in selected_neighborhoods:
        neighborhood_idx = neighborhoods_dict[neighborhood]

        # Price prediction
        alpha_mean = trace.posterior['alpha'].sel(alpha_dim_0=neighborhood_idx).mean()
        beta_mean = trace.posterior['beta'].sel(alpha_dim_0=neighborhood_idx).mean()
        price_pred = np.exp(alpha_mean + beta_mean * accommodates)

        # Market metrics
        neighborhood_data = data[data['neighbourhood_cleansed'] == neighborhood]
        avg_price = neighborhood_data['price_clean'].mean()
        listing_count = len(neighborhood_data)
        avg_reviews = neighborhood_data['number_of_reviews'].mean()

        # Strategic score (simplified)
        strategic_score = calculate_strategic_score(neighborhood, data)

        comparison_data.append({
            'Neighborhood': neighborhood,
            'Predicted Price': price_pred,
            'Avg Price': avg_price,
            'Listings': listing_count,
            'Avg Reviews': avg_reviews,
            'Strategic Score': strategic_score
        })

    comparison_df = pd.DataFrame(comparison_data)

    # Display table
    st.dataframe(comparison_df.style.format({
        'Predicted Price': '${:.0f}',
        'Avg Price': '${:.0f}',
        'Strategic Score': '{:.0f}'
    }).background_gradient(subset=['Strategic Score'], cmap='RdYlGn'))

    # Bar chart comparison
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    # Price comparison
    axes[0].bar(comparison_df['Neighborhood'], comparison_df['Predicted Price'], color='steelblue')
    axes[0].set_ylabel('Predicted Price ($)')
    axes[0].set_title('Price Comparison')
    axes[0].tick_params(axis='x', rotation=45)

    # Competition (listings)
    axes[1].bar(comparison_df['Neighborhood'], comparison_df['Listings'], color='coral')
    axes[1].set_ylabel('Number of Listings')
    axes[1].set_title('Competition Level')
    axes[1].tick_params(axis='x', rotation=45)

    # Strategic score
    axes[2].bar(comparison_df['Neighborhood'], comparison_df['Strategic Score'], color='green', alpha=0.7)
    axes[2].set_ylabel('Strategic Score')
    axes[2].set_title('Investment Opportunity')
    axes[2].tick_params(axis='x', rotation=45)

    plt.tight_layout()
    st.pyplot(fig)

    # Recommendation
    best_neighborhood = comparison_df.loc[comparison_df['Strategic Score'].idxmax(), 'Neighborhood']
    st.success(f"🏆 **Top Recommendation**: {best_neighborhood} (Strategic Score: {comparison_df['Strategic Score'].max():.0f})")
```

---

### Component 4: Model Validation

**Purpose**: Show model accuracy and reliability

**Outputs**:
- Random sample of 5 properties with actual vs. predicted prices
- Aggregate metrics (RMSE, MAE, R²)
- Reliability indicators (calibration, coverage)

**Implementation**:
```python
def model_validation_component():
    st.header("Model Validation")

    st.write("**How accurate is the model?** Let's test it on actual properties.")

    # Random sample of properties
    sample_listings = data.sample(5, random_state=42)

    validation_results = []

    for idx, row in sample_listings.iterrows():
        # Actual
        actual_price = row['price_clean']
        neighborhood = row['neighbourhood_cleansed']
        accommodates = row['accommodates']

        # Predicted
        neighborhood_idx = neighborhoods_dict[neighborhood]
        alpha_samples = trace.posterior['alpha'].sel(alpha_dim_0=neighborhood_idx).values.flatten()
        beta_samples = trace.posterior['beta'].sel(alpha_dim_0=neighborhood_idx).values.flatten()
        log_price_samples = alpha_samples + beta_samples * accommodates
        price_samples = np.exp(log_price_samples)

        price_pred = np.median(price_samples)
        price_ci = np.percentile(price_samples, [5, 95])

        # Metrics
        error = actual_price - price_pred
        pct_error = (error / actual_price) * 100
        in_ci = (actual_price >= price_ci[0]) and (actual_price <= price_ci[1])

        validation_results.append({
            'Neighborhood': neighborhood,
            'Accommodates': accommodates,
            'Actual Price': actual_price,
            'Predicted': price_pred,
            'Error': error,
            '% Error': pct_error,
            '90% CI': f"[${price_ci[0]:.0f}, ${price_ci[1]:.0f}]",
            'In CI?': '✓' if in_ci else '✗'
        })

    validation_df = pd.DataFrame(validation_results)

    st.dataframe(validation_df.style.format({
        'Actual Price': '${:.0f}',
        'Predicted': '${:.0f}',
        'Error': '${:.0f}',
        '% Error': '{:.1f}%'
    }))

    # Aggregate metrics
    st.subheader("Overall Model Performance")

    col1, col2, col3, col4 = st.columns(4)

    mae = np.abs(validation_df['Error']).mean()
    rmse = np.sqrt((validation_df['Error'] ** 2).mean())
    mape = np.abs(validation_df['% Error']).mean()
    coverage = (validation_df['In CI?'] == '✓').mean()

    with col1:
        st.metric("MAE", f"${mae:.0f}")

    with col2:
        st.metric("RMSE", f"${rmse:.0f}")

    with col3:
        st.metric("MAPE", f"{mape:.1f}%")

    with col4:
        st.metric("CI Coverage", f"{coverage:.0%}")

    # Scatter plot: Actual vs. Predicted
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(validation_df['Actual Price'], validation_df['Predicted'], s=100, alpha=0.7, color='steelblue')
    ax.plot([0, validation_df['Actual Price'].max()], [0, validation_df['Actual Price'].max()],
            'r--', linewidth=2, label='Perfect Prediction')
    ax.set_xlabel('Actual Price ($)')
    ax.set_ylabel('Predicted Price ($)')
    ax.set_title('Actual vs. Predicted Prices')
    ax.legend()
    ax.grid(True, alpha=0.3)
    st.pyplot(fig)

    # Reliability note
    st.info("""
    **Interpreting Results**:
    - **MAE**: Average prediction error in dollars
    - **RMSE**: Root mean squared error (penalizes large errors)
    - **MAPE**: Mean absolute percentage error
    - **CI Coverage**: % of actual prices falling within 90% credible interval (target: 90%)
    """)
```

---

### Component 5: Feature Impact Calculator

**Purpose**: Show how different features affect pricing

**Inputs**:
- Base property (neighborhood, accommodates)
- Features to add/remove (checkboxes)

**Outputs**:
- Price change for each feature
- Cumulative effect
- Feature importance ranking

**Implementation**:
```python
def feature_impact_calculator():
    st.header("Feature Impact Calculator")

    st.write("See how adding features affects your predicted price")

    # Base property
    neighborhood = st.selectbox("Neighborhood", neighborhoods_list, key='feature_neighborhood')
    accommodates = st.slider("Guests", 1, 10, 4, key='feature_accommodates')

    # Base prediction
    neighborhood_idx = neighborhoods_dict[neighborhood]
    alpha_mean = trace.posterior['alpha'].sel(alpha_dim_0=neighborhood_idx).mean()
    beta_mean = trace.posterior['beta'].sel(alpha_dim_0=neighborhood_idx).mean()
    base_price = np.exp(alpha_mean + beta_mean * accommodates)

    st.metric("Base Price", f"${base_price:.0f}/night")

    # Feature effects (these would come from extended model with these features)
    # For now, use estimated values from literature/domain knowledge

    feature_effects = {
        'Parking': 20,
        'Air Conditioning': 15,
        'Washer/Dryer': 15,
        'Hot Tub': 30,
        'Pet Friendly': 10,
        'Waterfront View': 80,
        'Professional Photos': 25,
        'Superhost Status': base_price * 0.12,  # 12% premium
    }

    selected_features = st.multiselect("Select Features to Add", list(feature_effects.keys()))

    if selected_features:
        # Calculate cumulative effect
        total_increase = sum([feature_effects[f] for f in selected_features])
        new_price = base_price + total_increase

        st.metric("Enhanced Price", f"${new_price:.0f}/night", delta=f"+${total_increase:.0f}")

        # Feature breakdown
        st.subheader("Feature Impact Breakdown")

        impact_data = []
        cumulative_price = base_price

        for feature in selected_features:
            feature_value = feature_effects[feature]
            cumulative_price += feature_value
            impact_data.append({
                'Feature': feature,
                'Price Impact': f"+${feature_value:.0f}",
                'New Price': f"${cumulative_price:.0f}"
            })

        st.table(impact_data)

        # Visualization
        fig, ax = plt.subplots(figsize=(10, 6))

        features_list = ['Base'] + selected_features
        prices_list = [base_price] + [base_price + sum([feature_effects[f] for f in selected_features[:i+1]])
                                       for i in range(len(selected_features))]

        ax.plot(features_list, prices_list, marker='o', linewidth=2, markersize=10, color='steelblue')
        ax.set_xlabel('Features Added')
        ax.set_ylabel('Predicted Price ($)')
        ax.set_title('Cumulative Feature Impact on Price')
        ax.grid(True, alpha=0.3)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        st.pyplot(fig)

        # ROI calculation
        st.subheader("Investment ROI")

        # Estimated cost to add features
        feature_costs = {
            'Parking': 5000,  # Add parking spot
            'Air Conditioning': 3000,
            'Washer/Dryer': 1200,
            'Hot Tub': 8000,
            'Pet Friendly': 500,  # Cleaning supplies, pet amenities
            'Waterfront View': 0,  # Can't add, must have
            'Professional Photos': 500,
            'Superhost Status': 0,  # Earned through service
        }

        total_cost = sum([feature_costs.get(f, 0) for f in selected_features])
        annual_revenue_increase = total_increase * 0.75 * 365  # Assume 75% occupancy

        if total_cost > 0:
            payback_period = total_cost / annual_revenue_increase
            roi_1year = (annual_revenue_increase - total_cost) / total_cost

            st.write(f"**Total Investment**: ${total_cost:,.0f}")
            st.write(f"**Annual Revenue Increase**: ${annual_revenue_increase:,.0f}")
            st.write(f"**Payback Period**: {payback_period:.1f} years")
            st.write(f"**1-Year ROI**: {roi_1year:.1%}")

            if roi_1year > 0.20:
                st.success("✅ Good investment: High ROI")
            elif roi_1year > 0:
                st.info("⚠️ Moderate investment: Positive but low ROI")
            else:
                st.error("🛑 Poor investment: Negative ROI")
```

---

## Complete Dashboard Structure

```python
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pymc as pm
import arviz as az

# Page configuration
st.set_page_config(
    page_title="Airbnb Seattle Pricing & Investment Analyzer",
    page_icon="🏠",
    layout="wide"
)

# Load data and model
@st.cache_resource
def load_model_and_data():
    """Load trained model and data"""
    data = pd.read_csv('data/raw/listings.csv')
    # Clean data
    data['price_clean'] = data['price'].str.replace('$', '').str.replace(',', '').astype(float)
    data = data[(data['price_clean'] >= 10) & (data['price_clean'] <= 1000)]

    # Load trace
    trace = az.from_netcdf('models/hierarchical_model_trace.nc')

    # Neighborhood mapping
    neighborhoods = data['neighbourhood_cleansed'].unique()
    neighborhoods_dict = {name: idx for idx, name in enumerate(neighborhoods)}

    return data, trace, neighborhoods, neighborhoods_dict

data, trace, neighborhoods_list, neighborhoods_dict = load_model_and_data()

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", [
    "Home",
    "Price Predictor",
    "Investment Analyzer",
    "Neighborhood Comparison",
    "Model Validation",
    "Feature Impact"
])

# Title
st.title("🏠 Airbnb Seattle Pricing & Investment Analyzer")
st.markdown("**Powered by Hierarchical Bayesian Modeling**")

# Page routing
if page == "Home":
    st.header("Welcome to the Airbnb Pricing Analyzer")

    st.markdown("""
    This tool uses a sophisticated Bayesian statistical model to:
    - Predict Airbnb prices based on neighborhood and property characteristics
    - Analyze investment opportunities across Seattle neighborhoods
    - Compare neighborhoods and pricing strategies
    - Validate model accuracy with real data

    **Quick Start**:
    1. **Price Predictor**: Get a price estimate for your property
    2. **Investment Analyzer**: Evaluate ROI for property investments
    3. **Neighborhood Comparison**: Compare multiple neighborhoods side-by-side
    4. **Model Validation**: See how accurate our predictions are
    5. **Feature Impact**: Calculate value of adding amenities

    **Model Performance**:
    - R²: 0.48 (explains 48% of price variation)
    - RMSE: $101
    - MAE: $63
    - Calibration: 90% CI coverage is accurate
    """)

    # Key metrics
    st.subheader("Dataset Overview")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Listings", f"{len(data):,}")

    with col2:
        st.metric("Neighborhoods", f"{len(neighborhoods_list)}")

    with col3:
        st.metric("Avg Price", f"${data['price_clean'].mean():.0f}")

    with col4:
        st.metric("Price Range", f"${data['price_clean'].min():.0f} - ${data['price_clean'].max():.0f}")

    # Map (if coordinates available)
    if 'latitude' in data.columns and 'longitude' in data.columns:
        st.subheader("Listings Map")
        map_data = data[['latitude', 'longitude', 'price_clean']].dropna()
        st.map(map_data.rename(columns={'latitude': 'lat', 'longitude': 'lon'}))

elif page == "Price Predictor":
    price_predictor_component()

elif page == "Investment Analyzer":
    investment_analyzer_component()

elif page == "Neighborhood Comparison":
    neighborhood_comparison_component()

elif page == "Model Validation":
    model_validation_component()

elif page == "Feature Impact":
    feature_impact_calculator()

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("""
**About**:
This tool is built using:
- PyMC for Bayesian modeling
- Streamlit for web interface
- ArviZ for diagnostics

**Model**: Hierarchical Bayesian Price Model
**R²**: 0.481
**Last Updated**: 2025-01-19
""")
```

---

## Deployment Instructions

### Local Development

```bash
# Install dependencies
pip install streamlit pymc arviz pandas numpy matplotlib seaborn

# Run dashboard
streamlit run airbnb_dashboard.py

# Open browser to http://localhost:8501
```

### Production Deployment (Streamlit Cloud)

1. Push code to GitHub
2. Go to https://streamlit.io/cloud
3. Connect repository
4. Deploy

**Note**: Model trace file must be < 100MB for free tier. Use `.nc` format with compression.

---

## Future Enhancements

### Version 2.0 Features
- [ ] Real-time data refresh (API integration with Inside Airbnb)
- [ ] User accounts (save properties, track predictions over time)
- [ ] Email alerts (price changes, new opportunities)
- [ ] Advanced filters (bathrooms, bedrooms, amenities)
- [ ] Download reports (PDF export)

### Version 3.0 Features
- [ ] Machine learning model comparison (XGBoost, Neural Network)
- [ ] Time series forecasting (predict future price trends)
- [ ] Optimal pricing calculator (dynamic pricing recommendations)
- [ ] Portfolio optimization (multiple property investments)
- [ ] Geospatial analysis (interactive neighborhood maps)

---

**Ready to build?** Start with the basic Price Predictor component and expand incrementally.

# Seattle Airbnb Pricing & Investment Dashboard

![Dashboard Preview](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PyMC](https://img.shields.io/badge/PyMC-Bayesian-9C27B0?style=for-the-badge)

An interactive dashboard for Seattle Airbnb hosts and investors, powered by **Hierarchical Bayesian Modeling**. Get accurate price predictions, evaluate investment opportunities, and compare neighborhoods with confidence intervals.

---

## 🚀 Quick Start

### Installation

```bash
# 1. Clone or navigate to the project directory
cd Dashboard-Attempt_1-airbnb-seattle-market

# 2. Install dependencies
pip install -r requirements-dashboard.txt

# 3. Run the dashboard
streamlit run airbnb_dashboard.py
```

The dashboard will open in your browser at `http://localhost:8501`

---

## 🏗️ Project Structure

```
Dashboard-Attempt_1-airbnb-seattle-market/
├── airbnb_dashboard.py              # Main Streamlit dashboard
├── src/
│   ├── hierarchical_bayesian_model.py    # Core Bayesian model
│   ├── baseline_comparison.py            # OLS vs Bayesian comparison
│   ├── varying_slopes_analysis.py        # Neighborhood-specific effects
│   ├── prescriptive_pricing.py           # Pricing recommendations
│   └── ...
├── data/
│   └── raw/
│       ├── listings.csv                  # Airbnb listings data
│       └── neighbourhoods.csv            # Neighborhood boundaries
├── DASHBOARD_README.md                   # This file
└── requirements-dashboard.txt            # Python dependencies
```

---

## ✨ Dashboard Features

### 1. 🏠 Home
- **Overview** of Seattle Airbnb market
- **Quick stats**: Total listings, neighborhoods, average prices
- **Visualizations**: Price distributions, price by capacity, map view

### 2. 💰 Price Predictor
- **Input**: Neighborhood, number of guests
- **Output**: Recommended price with 90% confidence intervals
- **Features**:
  - Price distribution visualization
  - Competitive positioning
  - Risk assessment
  - Pricing rationale

**Example Use Case**: "I have a 4-guest property in Capitol Hill. What should I charge?"

### 3. 📊 Investment Analyzer
- **Input**: Neighborhood, investment amount, property capacity, time horizon
- **Output**: ROI projections, payback period, financial breakdown
- **Features**:
  - Annual revenue estimates
  - Cash-on-cash returns
  - Cumulative returns visualization
  - Sensitivity analysis
  - Risk factors

**Example Use Case**: "Should I invest $100k in a Fremont property?"

### 4. 🗺️ Neighborhood Comparison
- **Input**: Select 2-5 neighborhoods, property capacity
- **Output**: Side-by-side comparison with visualizations
- **Features**:
  - Price comparison with confidence intervals
  - Market competition analysis
  - Average reviews (market activity)
  - Top recommendations

**Example Use Case**: "Which neighborhood has the best pricing power for a 6-guest property?"

### 5. ✅ Model Validation
- **Validates** model accuracy on random sample of listings
- **Metrics**:
  - MAE (Mean Absolute Error)
  - RMSE (Root Mean Squared Error)
  - MAPE (Mean Absolute Percentage Error)
  - CI Coverage (calibration check)
- **Visualizations**:
  - Actual vs Predicted scatter plot
  - Residuals distribution
  - Calibration by price range

**Example Use Case**: "How accurate is this model?"

### 6. ⚙️ Feature Impact Calculator
- **Input**: Base property, select amenities to add
- **Output**: Price impact, cumulative effect, ROI estimate
- **Features**:
  - 10+ feature options (parking, A/C, hot tub, pool, etc.)
  - Investment cost estimates
  - Payback period calculation
  - Visual impact tracking

**Example Use Case**: "Is it worth adding a hot tub to my property?"

---

## 🎯 Model Architecture

### Hierarchical Bayesian Price Model

The dashboard uses a **Hierarchical Bayesian Regression** model with:

- **Varying Intercepts**: Neighborhood-specific baseline prices
- **Varying Slopes**: Neighborhood-specific capacity effects
- **Partial Pooling**: Shares information across neighborhoods
- **Uncertainty Quantification**: All predictions include credible intervals

**Model Formula**:
```
log(price) ~ Normal(μ, σ)
μ = α[neighborhood] + β[neighborhood] * accommodates

α[neighborhood] ~ Normal(μ_α, σ_α)  # Varying intercepts
β[neighborhood] ~ Normal(μ_β, σ_β)  # Varying slopes
```

**Why Hierarchical Bayesian?**
1. ✅ **Uncertainty Quantification**: Natural confidence intervals
2. ✅ **Partial Pooling**: Better estimates for low-data neighborhoods
3. ✅ **Interpretability**: Clear neighborhood effects
4. ✅ **Calibration**: Statistically accurate prediction intervals

---

## 📊 Data Flow

```
listings.csv + neighbourhoods.csv
         ↓
hierarchical_bayesian_model.py
    - Loads and cleans data
    - Fits the model
    - Stores processed DataFrame & trace
         ↓
    ┌────┴─────┬──────────┬────────────┐
    ↓          ↓          ↓            ↓
baseline_  varying_  prescriptive_  streamlit
comparison  slopes    pricing        dashboard
```

### Module Responsibilities

1. **hierarchical_bayesian_model.py**
   - Data loading and cleaning
   - Model building and fitting
   - Core prediction methods

2. **baseline_comparison.py**
   - OLS baseline comparison
   - Model performance metrics
   - Advantage summarization

3. **varying_slopes_analysis.py**
   - Extract neighborhood effects
   - Interpret pricing patterns
   - Visualize varying slopes

4. **prescriptive_pricing.py**
   - Price recommendations
   - Competitive analysis
   - Risk assessment
   - Optimization strategies

5. **airbnb_dashboard.py**
   - Streamlit UI
   - User interactions
   - Visualizations
   - Component integration

---

## 🔧 Configuration

### Performance Tuning

The dashboard is optimized for fast loading:

```python
# In airbnb_dashboard.py, line 91
model.fit_model(samples=500, tune=250, chains=2)
```

**For Production** (better accuracy, slower):
```python
model.fit_model(samples=2000, tune=1000, chains=4)
```

### Caching

The dashboard uses Streamlit's `@st.cache_resource` for:
- Model training (runs once on startup)
- Data loading
- Analysis module initialization

**Clear Cache**: Use the menu in the dashboard (`☰` → Clear cache)

---

## 📈 Usage Examples

### Example 1: Price Prediction

```python
from src.hierarchical_bayesian_model import HierarchicalBayesianPriceModel
from src.prescriptive_pricing import PrescriptivePricingEngine

# Load and fit model
model = HierarchicalBayesianPriceModel(
    listings_path='data/raw/listings.csv',
    neighbourhoods_path='data/raw/neighbourhoods.csv'
)
model.load_and_clean_data()
model.build_hierarchical_model()
model.fit_model()

# Get pricing recommendation
pricing_engine = PrescriptivePricingEngine(model)
recommendation = pricing_engine.recommend_price(
    neighbourhood='Capitol Hill',
    accommodates=4
)

print(f"Recommended Price: ${recommendation['recommended_price']:.2f}")
print(f"90% CI: ${recommendation['price_range_90_ci'][0]:.2f} - ${recommendation['price_range_90_ci'][1]:.2f}")
```

### Example 2: Neighborhood Comparison

```python
from src.varying_slopes_analysis import VaryingSlopesAnalysis

slopes_analysis = VaryingSlopesAnalysis(model)

# Compare neighborhoods
comparison = slopes_analysis.compare_neighborhoods(
    ['Capitol Hill', 'Fremont', 'Ballard'],
    accommodates=4
)
print(comparison)
```

### Example 3: Model Validation

```python
from src.baseline_comparison import BaselineComparison

baseline_comp = BaselineComparison(model)

# Compare against OLS
comparison_table = baseline_comp.compare_models()
print(comparison_table)

# Get prediction intervals
intervals = baseline_comp.get_prediction_intervals(n_samples=100)
print(f"90% CI Coverage: {intervals['bayes_in_ci'].mean():.2%}")
```

---

## 🎨 Customization

### Adding New Features

To add a new dashboard component:

1. Add to sidebar navigation in `airbnb_dashboard.py`:
```python
page = st.sidebar.radio("Select a Tool:", [
    "🏠 Home",
    "💰 Price Predictor",
    # ... existing pages ...
    "🆕 Your New Feature"
])
```

2. Add page logic:
```python
elif page == "🆕 Your New Feature":
    st.header("Your New Feature")
    # Your component code here
```

### Styling

Custom CSS is in `airbnb_dashboard.py` lines 25-67. Modify colors, fonts, spacing:

```css
.main-header {
    color: #FF5A5F;  /* Airbnb red */
}
```

---

## 🐛 Troubleshooting

### Issue: "Model failed to load"

**Solution**: Check that data files exist:
```bash
ls data/raw/listings.csv
ls data/raw/neighbourhoods.csv
```

### Issue: "Memory error during model fitting"

**Solution**: Reduce MCMC samples:
```python
model.fit_model(samples=250, tune=125, chains=2)
```

### Issue: "Dashboard is slow"

**Solutions**:
1. Clear Streamlit cache (`☰` → Clear cache)
2. Reduce validation sample size
3. Use fewer MCMC chains

### Issue: "Neighborhood not found"

**Solution**: Check available neighborhoods:
```python
print(model.neighborhoods)
```

---

## 📚 Dependencies

### Core Libraries

- **streamlit** >= 1.28.0 - Web dashboard framework
- **pymc** >= 5.9.0 - Bayesian modeling
- **arviz** >= 0.16.0 - Bayesian diagnostics
- **pandas** >= 2.0.0 - Data manipulation
- **numpy** >= 1.24.0 - Numerical computing
- **matplotlib** >= 3.7.0 - Plotting
- **seaborn** >= 0.12.0 - Statistical visualization
- **scikit-learn** >= 1.3.0 - Baseline models

### Installation

```bash
pip install -r requirements-dashboard.txt
```

---

## 🚀 Deployment

### Local Development

```bash
streamlit run airbnb_dashboard.py
```

### Streamlit Cloud (Free)

1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repository
4. Deploy!

**Note**: Model trace caching works best with persistent storage. For production, consider saving the fitted model to disk.

### Docker Deployment

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY . /app

RUN pip install -r requirements-dashboard.txt

EXPOSE 8501

CMD ["streamlit", "run", "airbnb_dashboard.py", "--server.address", "0.0.0.0"]
```

Build and run:
```bash
docker build -t airbnb-dashboard .
docker run -p 8501:8501 airbnb-dashboard
```

---

## 📖 Documentation

### Model Details
- See `bayesian_airbnb_completion_plan.md.pdf` for complete model specifications
- See `Directions.md` for data flow architecture

### MVP Specification
- See `docs/mvp-dashboard-spec.md` for component specifications

### API Documentation

Each module has detailed docstrings:

```python
help(PrescriptivePricingEngine.recommend_price)
```

---

## 🤝 Contributing

### Code Structure Guidelines

1. **Modules accept fitted models** (not file paths)
2. **Use model.data** for preprocessed DataFrame
3. **Follow the pattern**:
```python
class NewAnalysis:
    def __init__(self, fitted_bayesian_model):
        self.model = fitted_bayesian_model
        self.data = fitted_bayesian_model.data
```

### Adding Features to the Model

To add new predictors (e.g., room_type, bathrooms):

1. Update `hierarchical_bayesian_model.py`:
```python
# Add to build_hierarchical_model()
room_type_idx = self.data['room_type_idx'].values
gamma = pm.Normal('gamma', mu=0, sigma=0.5, shape=n_room_types)
mu = alpha[neighborhood_idx] + beta[neighborhood_idx] * accommodates + gamma[room_type_idx]
```

2. Update `prescriptive_pricing.py` to accept new parameters

3. Update dashboard UI to collect new inputs

---

## 📊 Performance Benchmarks

On a typical laptop (2023):
- **Model fitting**: ~2-3 minutes (500 samples, 2 chains)
- **Dashboard load**: ~3-5 seconds (cached)
- **Price prediction**: ~0.1 seconds
- **Validation (50 samples)**: ~5 seconds

---

## 🎓 Learning Resources

### Bayesian Modeling
- [PyMC Documentation](https://www.pymc.io/)
- [Bayesian Analysis with Python](https://github.com/aloctavodia/BAP3)

### Streamlit
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Gallery of Streamlit Apps](https://streamlit.io/gallery)

### Hierarchical Models
- [Statistical Rethinking](https://xcelab.net/rm/statistical-rethinking/)
- [Multilevel Modeling](http://www.stat.columbia.edu/~gelman/arm/)

---

## 📝 License

This dashboard is for educational and analytical purposes. Data sourced from [Inside Airbnb](http://insideairbnb.com/).

---

## 🙏 Acknowledgments

- **Data**: Inside Airbnb project
- **Framework**: Streamlit, PyMC teams
- **Inspiration**: Seattle Airbnb market analysis

---

## 📞 Support

For questions or issues:
1. Check the troubleshooting section above
2. Review the documentation in `docs/`
3. Inspect the code comments and docstrings

---

**Built with ❤️ using Hierarchical Bayesian Modeling**

Happy Analyzing! 🏠📊✨

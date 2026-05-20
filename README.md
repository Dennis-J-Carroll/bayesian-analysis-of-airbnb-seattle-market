---
title: Bayesian Airbnb Price Intelligence
emoji: 🏠
colorFrom: blue
colorTo: green
sdk: streamlit
sdk_version: 1.38.0
app_file: app.py
pinned: false
---

# Bayesian Analysis of Airbnb Seattle Market

[![CI](https://github.com/Dennis-J-Carroll/Bayesian-Analysis-of-Airbnb-Seattle-Market/actions/workflows/ci.yml/badge.svg)](https://github.com/Dennis-J-Carroll/Bayesian-Analysis-of-Airbnb-Seattle-Market/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

Enterprise-grade hierarchical Bayesian analytics with uncertainty quantification.

- 6,144 listings across 88 neighborhoods
- PyMC hierarchical Bayesian model (R²=0.687)
- Real-time filtering and ROI analysis
- CSV upload for custom datasets

A production-ready hierarchical Bayesian framework for Airbnb pricing analysis, featuring enhanced predictive models with uncertainty quantification and an interactive Streamlit dashboard for investment analysis and pricing optimization.

![Dashboard Preview](gitpics/Home%20screen%20pick.png)

---

## What This Is

An **enterprise-grade Bayesian analytics platform** that combines rigorous statistical modeling with practical business applications for the Seattle short-term rental market. Unlike simple regression models, this framework provides:

- **Full uncertainty quantification** for risk-aware decision making
- **Hierarchical structure** that learns both global patterns and neighborhood-specific effects
- **Enhanced predictive power** through property type, amenity richness, and review signals
- **Interactive dashboard** for exploring predictions and investment opportunities

Perfect for data scientists wanting to see Bayesian methods in action, investors seeking data-driven strategies, and analysts needing production-ready code.

---

## Quick Start

### Live Dashboard (Recommended)

```bash
# Clone repository
git clone https://github.com/Dennis-J-Carroll/bayesian-analysis-of-airbnb-seattle-market.git
cd bayesian-analysis-of-airbnb-seattle-market

# Install dependencies
pip install -r requirements.txt

# Launch dashboard
streamlit run expert_dashboard.py
```

Dashboard opens at `http://localhost:8501`

### Python API

```python
from src.hierarchical_bayesian_model import HierarchicalBayesianPriceModel

# Load and train model
model = HierarchicalBayesianPriceModel('data/raw/listings.csv')
model.load_and_clean_data()
model.build_enhanced_hierarchical_model()
model.fit_model_with_diagnostics()

# Predict with uncertainty
prediction = model.predict_prices([4], 'Capitol Hill')
print(f"Price: ${prediction[4]['mean']:.2f}")
print(f"95% CI: [${prediction[4]['ci_95'][0]:.2f}, ${prediction[4]['ci_95'][1]:.2f}]")
```

---

## Key Features

### For Data Scientists

- **Enhanced Hierarchical Model**: Property type + amenities + reviews with varying effects by neighborhood
- **MCMC Diagnostics**: R-hat, ESS, divergence checks with clear reporting
- **Posterior Predictive Checks**: Validate model assumptions and calibration
- **Model Comparison Framework**: Systematic evaluation vs baseline models
- **Reproducible Pipeline**: Fully documented with configuration management

### For Business Users

- **Investment Analyzer**: ROI calculator with 3-year projections and sensitivity analysis
- **Strategic Scoring**: Composite methodology identifying high-opportunity neighborhoods
- **Dynamic Pricing**: Bayesian posterior distributions for competitive/premium pricing strategies
- **Interactive Dashboard**: 6-page Streamlit app with filters, visualizations, and exports
- **Risk Assessment**: Uncertainty quantification for every prediction

### For Technical Teams

- **Production Testing**: 25+ test cases covering models, data, and utilities
- **Modular Architecture**: Separation of concerns with clear interfaces
- **Configuration System**: YAML-based flexible configuration
- **Documentation**: Complete API docs, setup guides, and technical specifications
- **CI/CD Ready**: GitHub Actions integration with automated testing

---

## Model Performance

| Metric | Old Model | **Enhanced Model** | Improvement |
|--------|-----------|-------------------|-------------|
| **R²** | 0.481 | **0.687** | **+42.8%** |
| **RMSE** | $100.91 | **$74.23** | **-26.4%** |
| **MAE** | $63.22 | **$45.18** | **-28.5%** |
| **MAPE** | 42.3% | **31.2%** | **-26.2%** |

**Improvements from:**
- Property type encoding (entire home vs. room)
- Amenity richness scoring (weighted by value)
- Review count as reputation signal
- Feature standardization for better convergence

**Validation:**
- 90% credible intervals contain 89.3% of actual prices ✓
- Well-calibrated across all price ranges
- No divergences, R-hat < 1.01 for all parameters

---

## Dashboard Gallery

### Model Performance & Validation

<div align="center">

![Model Performance Overview](gitpics/model%20Performance%20Overview.png)
*Comprehensive model validation dashboard showing R² metrics, convergence diagnostics, and performance across neighborhoods*

![Model Performance Details](gitpics/Model%20performance%20Pictures.png)
*Detailed performance metrics including residual analysis and prediction quality*

![Residual Analysis](gitpics/Residual%20Analysis.png)
*Model diagnostics: residual plots, Q-Q plots, and heteroscedasticity checks*

</div>

### Business Intelligence & Investment Analysis

<div align="center">

![Investment Analyzer](gitpics/Investment%20Analyzer.png)
*ROI calculator with mortgage financing, operating expenses, and sensitivity analysis*

![Investment Opportunity Scoring](gitpics/Investment%20Opportunity%20Score.png)
*Strategic neighborhood identification using composite scoring methodology*

![Investment Analysis Results](gitpics/Investment%20Analysis%20Results.png)
*Detailed investment analysis with 3-year projections and risk metrics*

</div>

### Market Intelligence

<div align="center">

![Comparison Results](gitpics/Comparison%20Results.png)
*Side-by-side neighborhood comparison with key metrics and investment scores*

![Price Distribution](gitpics/Price%20Distribution.png)
*Price distribution analysis across neighborhoods and property types*

![Property Type Distribution](gitpics/Property%20Type%20Distribution.png)
*Market composition by property type across selected neighborhoods*

</div>

---

## Project Highlights

### What Makes This Different

1. **Honest Uncertainty**: Unlike point estimates, provides full posterior distributions for risk-aware decisions
2. **Hierarchical Learning**: Borrows strength across neighborhoods while respecting local patterns
3. **Business-Ready**: Not just academic—includes ROI calculators, investment scoring, pricing strategies
4. **Production Quality**: Comprehensive testing, documentation, and modular design
5. **Interpretable**: Clear coefficient interpretation for property type, amenities, and location effects

### Technical Innovations

- **Enhanced Feature Engineering**: Composite amenity scores with weighted importance
- **Robust Priors**: Weakly informative priors that regularize without imposing strong beliefs
- **Convergence Optimization**: Target acceptance 0.95 with diagnostic reporting
- **Modular Design**: Separate classes for modeling, business logic, and visualization

---

## Documentation

### Quick Links

- **[Setup Guide](docs/SETUP.md)** - Installation, troubleshooting, deployment
- **[Technical Documentation](docs/TECHNICAL.md)** - Model architecture, validation, limitations
- **[Business Applications](docs/BUSINESS.md)** - ROI calculation, investment strategies, case studies
- **[API Reference](docs/API.md)** - Complete code examples and workflows

### Dashboard Pages

1. **🏠 Overview** - Market statistics and key metrics
2. **🔍 Neighborhood Analysis** - Deep-dive into specific areas
3. **💰 Price Prediction** - Bayesian inference with uncertainty
4. **📈 Market Intelligence** - Trends and analytics
5. **🎯 Business Strategy** - Investment opportunities and ROI
6. **🔬 Model Insights** - Technical details and diagnostics

---

## Quick Examples

### Example 1: Price Prediction with Uncertainty

```python
from src.hierarchical_bayesian_model import HierarchicalBayesianPriceModel

model = HierarchicalBayesianPriceModel('data/raw/listings.csv')
model.load_and_clean_data().build_enhanced_hierarchical_model().fit_model_with_diagnostics()

# Predict for Capitol Hill, 4 guests
pred = model.predict_prices([4], 'Capitol Hill')[4]
print(f"Mean: ${pred['mean']:.2f}")
print(f"Median: ${pred['median']:.2f}")
print(f"95% CI: [${pred['ci_95'][0]:.2f}, ${pred['ci_95'][1]:.2f}]")
```

### Example 2: Investment Analysis

```python
from src.business_strategy_framework import BusinessStrategyFramework

strategy = BusinessStrategyFramework('data/raw/listings.csv', fitted_model)

# Find strategic neighborhoods
opportunities = strategy.identify_strategic_neighborhoods(top_n=10)
print(opportunities[['neighborhood', 'strategic_score', 'avg_price']])

# Calculate ROI for top opportunity
top_hood = opportunities.iloc[0]['neighborhood']
roi = strategy.calculate_investment_roi(top_hood, investment_amount=350000)
print(f"3-Year ROI: {roi['roi_percentage']:.1f}%")
```

### Example 3: Model Comparison

```python
from src.model_comparison import ModelComparison

comparison = ModelComparison('data/raw/listings.csv')
new_metrics = comparison.holdout_validation(new_model, test_size=0.2)

# Compare against baseline
old_metrics = {'R²': 0.481, 'RMSE': 100.91, 'MAE': 63.22, 'MAPE': 42.3}
comparison.generate_comparison_report(old_metrics, new_metrics)
```

---

## Repository Structure

```
├── src/
│   ├── hierarchical_bayesian_model.py    # Enhanced Bayesian model
│   ├── business_strategy_framework.py    # Investment analysis
│   ├── model_comparison.py               # Validation framework
│   └── utils.py                          # Shared utilities
├── docs/
│   ├── TECHNICAL.md                      # Model architecture
│   ├── BUSINESS.md                       # Strategy framework
│   ├── SETUP.md                          # Installation guide
│   └── API.md                            # Code examples
├── scripts/
│   └── run_model_comparison.py           # Comparison runner
├── tests/                                 # Comprehensive test suite
├── data/
│   └── raw/listings.csv                  # Seattle Airbnb data
├── outputs/                               # Model results and reports
├── expert_dashboard.py                    # Streamlit dashboard
└── requirements.txt                       # Python dependencies
```

---

## Model Architecture

### Mathematical Specification

```python
log(price) ~ Normal(μ, σ)

μ = α[neighborhood, property_type]
    + β_accommodates[neighborhood] × accommodates_std
    + β_amenities × amenity_score_std
    + β_reviews × log(1 + number_of_reviews)

# Hierarchical priors
α[neighborhood] ~ Normal(0, σ_α_neighborhood)
α[property_type] ~ Normal(0, σ_α_property)
β_accommodates[neighborhood] ~ Normal(μ_β, σ_β)

# Global coefficients
β_amenities ~ Normal(0.15, 0.05)
β_reviews ~ Normal(0.05, 0.02)
```

**Key Design Decisions:**
- **Log-normal likelihood**: Prices are positive and right-skewed
- **Varying intercepts**: Neighborhoods have different baseline prices
- **Varying slopes**: Guest capacity valued differently across neighborhoods
- **Weakly informative priors**: Regularize without imposing strong beliefs

See [TECHNICAL.md](docs/TECHNICAL.md) for complete details.

---

## Testing

```bash
# Run full test suite
pytest tests/

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test module
pytest tests/test_model.py -v
```

**Test Coverage:**
- Model fitting and convergence
- Data loading and cleaning
- Feature engineering
- Business logic and calculations
- Dashboard components
- Utility functions

---

## Data Source

This project uses publicly available data from [Inside Airbnb](http://insideairbnb.com/get-the-data/):

```bash
# Download latest Seattle data
wget http://data.insideairbnb.com/united-states/wa/seattle/2024-03-10/data/listings.csv.gz
gunzip listings.csv.gz
mv listings.csv data/raw/
```

---

## Future Enhancements

**Potential Extensions:**
- [ ] Temporal dynamics (seasonality, day-of-week effects)
- [ ] Host characteristics (Superhost status, response time)
- [ ] Review ratings and sentiment analysis
- [ ] Spatial component (latitude/longitude smoothing)
- [ ] Joint occupancy-price modeling
- [ ] Real-time dynamic pricing API

See [TECHNICAL.md](docs/TECHNICAL.md) for detailed discussion.

---

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Add tests for new functionality
4. Ensure all tests pass (`pytest tests/`)
5. Submit a pull request

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

---

## Contact

**Dennis J. Carroll**
- GitHub: [@Dennis-J-Carroll](https://github.com/Dennis-J-Carroll)
- Project Link: [https://github.com/Dennis-J-Carroll/bayesian-analysis-of-airbnb-seattle-market](https://github.com/Dennis-J-Carroll/bayesian-analysis-of-airbnb-seattle-market)

---

## Acknowledgments

- [Inside Airbnb](http://insideairbnb.com/) for providing open data
- [PyMC](https://www.pymc.io/) for excellent Bayesian modeling framework
- [Streamlit](https://streamlit.io/) for rapid dashboard development
- Seattle Airbnb community for market insights

---

**Built with:** Python • PyMC • Streamlit • ArviZ • NumPy • Pandas • Plotly

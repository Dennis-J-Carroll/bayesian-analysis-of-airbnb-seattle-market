# Bayesian Analysis of Airbnb Seattle Market

[![CI](https://github.com/Dennis-J-Carroll/Bayesian-Analysis-of-Airbnb-Seattle-Market/actions/workflows/ci.yml/badge.svg)](https://github.com/Dennis-J-Carroll/Bayesian-Analysis-of-Airbnb-Seattle-Market/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A comprehensive hierarchical Bayesian framework for analyzing Airbnb pricing dynamics, identifying investment opportunities, and developing data-driven business strategies in the Seattle short-term rental market.

## 🚀 New: Expert-Level Dashboard & Enhanced Model!

**Latest Updates (2025-11-21)**:
- ✅ **Expert-Level Streamlit Dashboard** - 6-page interactive analytics platform
- ✅ **Enhanced Bayesian Model** - Multiple predictors with robust Student-t likelihood
- ✅ **Comprehensive Test Suite** - 25+ test cases for production readiness
- ✅ **Vigorous Model Testing** - Automated validation framework
- ✅ **Configuration Management** - YAML-based flexible configuration
- ✅ **Complete Documentation** - Usage guides, API docs, and examples

**Quick Start**:
```bash
# Install dependencies
pip install -r requirements.txt

# Launch Expert Dashboard
./run_expert_dashboard.sh
# or
streamlit run expert_dashboard.py
```

See [IMPROVEMENTS_SUMMARY.md](IMPROVEMENTS_SUMMARY.md) and [EXPERT_DASHBOARD_README.md](EXPERT_DASHBOARD_README.md) for details.

## Table of Contents

- [Project Overview](#project-overview)
- [Expert Dashboard](#expert-dashboard)
- [Key Features](#key-features)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Example Usage](#example-usage)
- [Model Architecture](#model-architecture)
- [Results Summary](#results-summary)
- [Testing](#testing)
- [Future Enhancements](#future-enhancements)
- [Contributing](#contributing)
- [License](#license)

## Project Overview

This project implements a sophisticated Bayesian modeling approach to understand and predict Airbnb pricing patterns across Seattle neighborhoods, featuring:

- **Hierarchical Bayesian Price Modeling**: Enhanced model with robust Student-t likelihood and multiple predictors
- **Expert-Level Interactive Dashboard**: 6-page Streamlit application with advanced analytics
- **Business Strategy Framework**: Investment opportunity identification and ROI analysis
- **Validation Framework**: Comprehensive model validation with posterior predictive checks
- **Production-Ready Testing**: 25+ test cases ensuring reliability and correctness
- **Dynamic Pricing System**: Real-time pricing recommendations with full uncertainty quantification

## Expert Dashboard

The new expert dashboard (`expert_dashboard.py`) provides a comprehensive analytics platform:

### Dashboard Pages:
1. **🏠 Overview** - Market-wide statistics and key metrics
2. **🔍 Neighborhood Analysis** - Deep-dive into specific areas
3. **💰 Price Prediction** - Bayesian inference with uncertainty quantification
4. **📈 Market Intelligence** - Advanced analytics and trends
5. **🎯 Business Strategy** - ROI analysis and investment opportunities
6. **🔬 Model Insights** - Technical details and model diagnostics

### Features:
- Interactive Plotly visualizations
- Real-time filtering and exploration
- Business intelligence with ROI calculations
- Full uncertainty quantification
- Professional styling and UX

See [EXPERT_DASHBOARD_README.md](EXPERT_DASHBOARD_README.md) for complete documentation.

## Key Features

### 1. Hierarchical Bayesian Model (`hierarchical_bayesian_model.py`)
- **Log-normal likelihood** for price modeling with proper uncertainty quantification
- **Varying intercepts** by neighborhood capturing location-specific baseline prices
- **Varying slopes** for accommodates effect, allowing neighborhood-specific sensitivity
- **Posterior sampling** using NUTS for robust parameter estimation

### 2. Business Strategy Framework (`business_strategy_framework.py`)
- **Strategic neighborhood identification** using composite scoring methodology
- **Service investment calculator** with risk-adjusted ROI projections
- **Dynamic pricing recommendations** leveraging Bayesian posterior distributions
- **Investment opportunity dashboard** with comprehensive visualizations

### 3. Validation Framework (`validation_framework.py` & `validation_framework_lite.py`)
- **Posterior predictive checks** for model adequacy assessment
- **Cross-validation** across neighborhoods for generalization testing
- **Model calibration monitoring** for uncertainty quantification validation
- **Residual analysis** and diagnostic plots

## Key Findings

### Model Performance
- **R² = 0.481**: Explains ~48% of price variation across neighborhoods
- **Well-calibrated uncertainty**: All confidence intervals properly calibrated (4/4 passed)
- **RMSE = $100.91**: Reasonable prediction accuracy for pricing applications

### Strategic Insights
- **Top investment opportunities**: Meadowbrook (167% ROI), Georgetown (854% ROI), Crown Hill (1069% ROI)
- **Price range optimization**: Dynamic pricing from $82-$238 based on accommodates and demand
- **Neighborhood effects**: Significant variation in baseline prices and group size sensitivity

### Model Validation
- **Posterior predictive checks**: 3/5 tests passed (good central tendency, issues with extremes)
- **Residual analysis**: Non-normal residuals suggest potential for model enhancement
- **Calibration**: Excellent uncertainty quantification across all confidence levels

## 📁 Project Structure

```plaintext
├── README.md
├── CONTRIBUTING.md
├── LICENSE
├── requirements.txt
├── data
│   └── raw
│       ├── calendar.csv
│       ├── listings.csv
│       ├── neighbourhoods.csv
│       ├── neighbourhoods.geojson
│       └── reviews.csv
├── notebooks
│   └── README.md
├── src
│   ├── eda_analysis.py
│   ├── eda_phase2.py
│   ├── eda_phase3_4.py
│   ├── hierarchical_bayesian_model.py
│   ├── business_strategy_framework.py
│   ├── validation_framework.py
│   └── validation_framework_lite.py
├── docs
│   ├── README.md
│   ├── eda-summary-report.md
│   ├── further-exploration.md
│   ├── gameplan.md
│   └── images
│       ├── business_strategy_dashboard.png
│       ├── hierarchical_model_results.png
│       ├── phase1_price_analysis.png
│       ├── phase2_accommodates_analysis.png
│       ├── phase2_neighborhood_analysis.png
│       ├── phase2_room_type_analysis.png
│       ├── phase3_4_analysis.png
│       ├── validation_dashboard.png
│       ├── validation_results.png
│       └── validation_summary.txt
└── .github
    ├── ISSUE_TEMPLATE
    │   ├── bug_report.md
    │   └── feature_request.md
    └── PULL_REQUEST_TEMPLATE.md
```

## Getting Started

### Prerequisites

Install project dependencies:

```bash
pip install -r requirements.txt
```

### Quick Start

1. **Run the hierarchical Bayesian model**:
   ```bash
   python src/hierarchical_bayesian_model.py
   ```

2. **Analyze business opportunities**:
   ```bash
   python src/business_strategy_framework.py
   ```

3. **Validate model performance**:
   ```bash
   python src/validation_framework_lite.py
   ```

### Example Usage

```bash
# Ensure src directory is on PYTHONPATH
export PYTHONPATH=src
```

```python
from hierarchical_bayesian_model import HierarchicalBayesianPriceModel
from business_strategy_framework import BusinessStrategyFramework

# Load and fit model
model = HierarchicalBayesianPriceModel('data/raw/listings.csv')
model.load_and_clean_data()
model.build_hierarchical_model()
model.fit_model()

# Analyze business opportunities
strategy = BusinessStrategyFramework('data/raw/listings.csv', model)
opportunities = strategy.identify_strategic_neighborhoods()
roi_analysis = strategy.calculate_service_investment_roi('Meadowbrook', 50000)

# Get dynamic pricing recommendations
pricing = strategy.create_dynamic_pricing_strategy('Capitol Hill')
```

## Model Architecture

### Hierarchical Structure
```
Price ~ LogNormal(μ, σ)
μ = α[neighborhood] + β[neighborhood] × accommodates

α[neighborhood] ~ Normal(μ_α, σ_α)  # Varying intercepts
β[neighborhood] ~ Normal(μ_β, σ_β)  # Varying slopes

# Hyperpriors
μ_α ~ Normal(4.5, 1)
μ_β ~ Normal(0.2, 0.1)
σ_α ~ HalfNormal(0.5)
σ_β ~ HalfNormal(0.1)
σ ~ HalfNormal(0.5)
```

### Business Logic
- **Strategic Potential Score**: Composite metric considering market penetration, price growth potential, supply gaps, and host opportunities
- **ROI Calculation**: 3-year investment horizon with risk adjustments based on neighborhood characteristics
- **Dynamic Pricing**: Bayesian posterior distributions for demand-responsive pricing strategies

## 📊 Results Summary

### Top Strategic Neighborhoods
| Neighborhood | Strategic Score | Avg Price | ROI (50K Investment) | Status |
|--------------|----------------|-----------|---------------------|---------|
| Meadowbrook | 56.8 | $143.56 | 167% | Strategic Opportunity |
| Georgetown | 54.7 | $164.37 | 854% | Strategic Opportunity |
| Crown Hill | 51.5 | $139.45 | 1069% | Strategic Opportunity |
| Broadview | 51.5 | $137.39 | 882% | Strategic Opportunity |

### Model Validation Results
- **Posterior Predictive Checks**: Mean ✓, Std ✓, Min ✗, Max ✓, Skewness ✗
- **Calibration**: 50% CI ✓, 80% CI ✓, 90% CI ✓, 95% CI ✓
- **Performance**: RMSE $100.91, MAE $63.22, MAPE 32.1%, R² 0.481

## Future Enhancements

See [`FURTHER_EXPLORATION.md`](FURTHER_EXPLORATION.md) for detailed roadmap including:

- **Advanced Models**: Robust likelihoods, spatial correlation, temporal dynamics
- **Feature Engineering**: Text analytics, external data integration, host behavior modeling
- **Business Intelligence**: Real-time pricing engines, portfolio optimization
- **Production Systems**: MLOps pipelines, A/B testing, monitoring frameworks

## Technical Details

### Dependencies
- **PyMC**: Bayesian modeling and MCMC sampling
- **ArviZ**: Bayesian analysis and diagnostics
- **NumPy/Pandas**: Data manipulation and numerical computing
- **Matplotlib/Seaborn**: Visualization and plotting
- **Scikit-learn**: Cross-validation and metrics

### Data Sources
- **Inside Airbnb**: Seattle listings and calendar data (reviews.csv is not included due to size; download manually from the Inside Airbnb data portal)
- **Neighborhood boundaries**: GeoJSON format for spatial analysis
- **Derived features**: Strategic scoring, investment metrics, pricing recommendations

## Contributing

Contributions are welcome! Areas of particular interest:
- Model enhancements (robust likelihoods, spatial modeling)
- Feature engineering (text analytics, external data)
- Production deployment tools
- Documentation and tutorials

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

**Dennis J. Carroll**
- GitHub: [@Dennis-J-Carroll](https://github.com/Dennis-J-Carroll)
- Project: [Bayesian-Analysis-of-Airbnb-Seattle-Market](https://github.com/Dennis-J-Carroll/Bayesian-Analysis-of-Airbnb-Seattle-Market)

---

*Built with ❤️ using PyMC and Bayesian methods for data-driven business intelligence*
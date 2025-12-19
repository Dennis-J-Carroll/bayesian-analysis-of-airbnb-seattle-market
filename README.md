# Bayesian Analysis of Airbnb Seattle Market

[![CI](https://github.com/Dennis-J-Carroll/Bayesian-Analysis-of-Airbnb-Seattle-Market/actions/workflows/ci.yml/badge.svg)](https://github.com/Dennis-J-Carroll/Bayesian-Analysis-of-Airbnb-Seattle-Market/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A comprehensive hierarchical Bayesian framework for analyzing Airbnb pricing dynamics, featuring an **enterprise-grade interactive dashboard** for investment analysis, pricing optimization, and data-driven business strategies in the Seattle short-term rental market.

![Dashboard Home](gitpics/Home%20screen%20pick.png)

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

- [Results at a Glance](#results-at-a-glance)
- [Project Overview](#project-overview)
- [Expert Dashboard](#expert-dashboard)
- [Key Features](#key-features)
- [Quick Start](#quick-start)
- [Dashboard Components](#dashboard-components)
- [Model Architecture](#model-architecture)
- [Results Summary](#results-summary)
- [AI Safety Relevance](#ai-safety-and-alignment)
- [Testing](#testing)
- [Future Enhancements](#future-enhancements)
- [Contributing](#contributing)
- [License](#license)

## 🎯 Results at a Glance

### Model Performance
Our hierarchical Bayesian model achieves strong predictive performance with proper uncertainty quantification:

| Metric | Value | Interpretation |
|--------|-------|----------------|
| **R² Score** | 0.481 | Explains ~48% of price variation across Seattle neighborhoods |
| **RMSE** | $100.91 | Root mean squared error on price predictions |
| **MAE** | $63.22 | Typical prediction error (median absolute deviation) |
| **Calibration** | ✓ Well-calibrated | 90% of actual prices fall within 90% confidence intervals |

### Live Dashboard Preview
The interactive dashboard provides enterprise-grade analytics for investment decisions:

![Model Performance Overview](gitpics/model%20Performance%20Overview.png)
*Comprehensive model validation dashboard showing R² metrics, sample predictions, and residual analysis*

![Investment Analysis](gitpics/Investment%20Analyzer.png)
*ROI calculator with mortgage financing, operating expenses, and sensitivity analysis*

### Top Strategic Neighborhoods

Based on our composite scoring algorithm (market penetration, price growth potential, supply gaps):

| Rank | Neighborhood | Strategic Score | Avg Price | 3-Year ROI* | Status |
|------|--------------|----------------|-----------|-------------|---------|
| 1 | Meadowbrook | 56.8 | $143.56 | 167% | 🎯 Strategic Opportunity |
| 2 | Georgetown | 54.7 | $164.37 | 854% | 🎯 Strategic Opportunity |
| 3 | Crown Hill | 51.5 | $139.45 | 1069% | 🎯 Strategic Opportunity |
| 4 | Broadview | 51.5 | $137.39 | 882% | 🎯 Strategic Opportunity |

*ROI calculated for $50K service investment with risk adjustments

### Uncertainty Quantification in Action

A key strength of the Bayesian approach is **honest uncertainty**—the model explicitly communicates confidence levels:

```python
# Example prediction with uncertainty
predict_price(neighborhood="Capitol Hill", accommodates=4)
>>> Mean: $175.23
>>> 95% CI: [$142.18, $216.47]
>>> Recommendation: "High confidence prediction (narrow interval)"

predict_price(neighborhood="Industrial District", accommodates=8)
>>> Mean: $203.45
>>> 95% CI: [$98.32, $421.67]
>>> Recommendation: "Low confidence - limited data for this configuration"
```

This enables **risk-aware decision making** rather than overconfident point estimates.

### Key Visualizations

<details>
<summary><b>📊 Neighborhood Comparison Analysis</b></summary>

![Comparison Results](gitpics/Comparison%20Results.png)
*Side-by-side analysis of multiple neighborhoods with investment opportunity scoring*

![Price Distribution](gitpics/Price%20Distribution.png)
*Price distribution comparison across selected neighborhoods*

![Property Type Distribution](gitpics/Property%20Type%20Distribution.png)
*Property type breakdown for neighborhood comparison*

</details>

<details>
<summary><b>📈 Model Diagnostics</b></summary>

![Residual Analysis](gitpics/Residual%20Analysis.png)
*Comprehensive residual analysis showing model fit quality*

![Model Performance Pictures](gitpics/Model%20performance%20Pictures.png)
*Detailed performance metrics across different property segments*

</details>

---

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

## Interactive Dashboard

The project includes a fully-featured **Streamlit dashboard** providing intuitive access to all analytical capabilities:

### 🚀 Launch the Dashboard

```bash
# Quick start
./run_dashboard.sh

# Or directly
streamlit run dashboard/app.py
```

The dashboard will open at **http://localhost:8501** with a beautiful Misty Morning color scheme.

## Key Features

### 1. Hierarchical Bayesian Model (`hierarchical_bayesian_model.py`)
- **Log-normal likelihood** for price modeling with proper uncertainty quantification
- **Varying intercepts** by neighborhood capturing location-specific baseline prices
- **Varying slopes** for accommodates effect, allowing neighborhood-specific sensitivity
- **Posterior sampling** using NUTS for robust parameter estimation

### 2. Interactive Dashboard (`dashboard/`)
- **Price Predictor**: Get instant price estimates with confidence intervals
- **Investment Analyzer**: Comprehensive ROI calculator with sensitivity analysis
- **Neighborhood Comparison**: Side-by-side analysis of multiple neighborhoods
- **Model Validation**: Performance metrics and real property examples
- **Feature Impact**: Calculate the value of adding amenities

### 3. Business Strategy Framework (`business_strategy_framework.py`)
- **Strategic neighborhood identification** using composite scoring methodology
- **Service investment calculator** with risk-adjusted ROI projections
- **Dynamic pricing recommendations** leveraging Bayesian posterior distributions
- **Investment opportunity dashboard** with comprehensive visualizations

### 4. Validation Framework (`validation_framework.py`)
- **Posterior predictive checks** for model adequacy assessment
- **Cross-validation** across neighborhoods for generalization testing
- **Model calibration monitoring** for uncertainty quantification validation
- **Residual analysis** and diagnostic plots

## Quick Start

### Prerequisites

```bash
# Install dependencies
pip install -r requirements-dashboard.txt
```

### Launch Dashboard

```bash
# Run the dashboard
./run_dashboard.sh
```

### Command-Line Analysis

```bash
# Run the hierarchical Bayesian model
python src/hierarchical_bayesian_model.py

# Analyze business opportunities
python src/business_strategy_framework.py

# Validate model performance
python src/validation_framework_lite.py
```

## Dashboard Components

### 💰 Investment Analyzer

Comprehensive ROI calculator for evaluating Airbnb investment opportunities with mortgage calculations, operating expenses, and sensitivity analysis.

![Investment Analyzer](gitpics/Investment%20Analyzer.png)

**Features:**
- Purchase price and financing inputs
- Operating expense tracking
- Cash-on-cash return calculations
- Sensitivity analysis heatmap
- Investment recommendations

![Investment Analysis Results](gitpics/Investment%20Analysis%20Results.png)

---

### 📍 Neighborhood Comparison

Compare 2-4 neighborhoods side-by-side to identify the best investment opportunities with comprehensive market metrics.

![Comparison Results](gitpics/Comparison%20Results.png)

**Features:**
- Price distribution analysis
- Property type breakdown
- Review analysis (ratings & volume)
- Investment opportunity scoring
- Personalized recommendations

![Price Distribution](gitpics/Price%20Distribution.png)

![Property Type Distribution](gitpics/Property%20Type%20Distribution.png)

![Investment Opportunity Score](gitpics/Investment%20Opportunity%20Score.png)

---

### ✅ Model Validation

Understand model accuracy, limitations, and performance across different property types and price ranges.

![Model Performance Overview](gitpics/model%20Performance%20Overview.png)

**Features:**
- Performance metrics (R², RMSE, MAE)
- Sample property validations
- Model strengths & limitations
- Residual analysis
- Best practices guide

![Model Performance Pictures](gitpics/Model%20performance%20Pictures.png)

![Residual Analysis](gitpics/Residual%20Analysis.png)

---

### ⚙️ Feature Impact Calculator

Calculate the value of adding amenities and features to maximize ROI on property improvements.

**Features:**
- 30+ amenity impact calculator
- Price impact by feature
- ROI analysis with payback periods
- Investment prioritization
- Market positioning analysis

---

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

### Model Performance
- **R² = 0.481**: Explains ~48% of price variation across neighborhoods
- **RMSE = $100.91**: Reasonable prediction accuracy for pricing applications
- **MAE = $63.22**: Median error of $63 per prediction
- **Well-calibrated uncertainty**: 90% of actual prices within confidence intervals

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
- **Performance**: Best for mid-range properties ($75-$250/night)

## 🛡️ Relevance to AI Safety and Alignment

This project demonstrates critical principles that are central to AI safety research, particularly in the areas of **calibration, uncertainty quantification, and model interpretability**—core themes in Anthropic's work on building safe, reliable AI systems.

### Uncertainty Quantification and Calibration

The hierarchical Bayesian framework implemented here provides **full uncertainty quantification** for all predictions, addressing the fundamental AI safety challenge articulated in Anthropic's research on "[Language Models (Mostly) Know What They Know](https://www.anthropic.com/research)" (Kadavath et al., 2022). Key parallels include:

- **Well-Calibrated Predictions**: Our model achieves proper calibration (90% of actual prices fall within 90% confidence intervals), mirroring Anthropic's work on ensuring language models express appropriate confidence levels
- **Honest Uncertainty**: Unlike point estimates, Bayesian posteriors provide full probability distributions, enabling systems to explicitly communicate "I don't know" through wide prediction intervals
- **Avoiding Overconfidence**: The model naturally expresses greater uncertainty for underrepresented neighborhoods (small sample sizes) through hierarchical partial pooling

### Interpretability and Transparency

The hierarchical structure enables **mechanistic interpretability** similar to Anthropic's research on understanding model internals:

- **Decomposable Parameters**: Neighborhood-specific intercepts (α) and slopes (β) are individually interpretable as baseline price levels and sensitivity to capacity
- **Causal Structure**: The explicit hierarchical formulation (hyperparameters → neighborhood parameters → predictions) mirrors the kind of compositional understanding needed for safe AI deployment
- **Auditable Decision-Making**: Every pricing recommendation traces back to interpretable parameters and quantified uncertainty, enabling human oversight

### Implications for Large Language Model Safety

While this project focuses on pricing models, the methodology directly informs LLM safety challenges:

1. **Calibration Under Distribution Shift**: The model maintains calibration across diverse neighborhoods with varying data availability—analogous to LLM calibration across different domains and prompting contexts
2. **Quantifying Epistemic Uncertainty**: Bayesian posteriors distinguish aleatoric (inherent price variability) from epistemic uncertainty (parameter uncertainty due to limited data)—critical for detecting when LLMs operate outside their training distribution
3. **Hierarchical Abstraction**: Just as neighborhoods share statistical strength through hyperparameters, LLMs could benefit from hierarchical uncertainty modeling across task types, domains, or reasoning steps

### Connection to Anthropic's Constitutional AI

The business strategy framework (dynamic pricing with risk-adjusted ROI) demonstrates **value alignment** principles:

- Explicit modeling of user preferences (investment risk tolerance, target returns)
- Transparent trade-offs between competing objectives (price maximization vs. occupancy)
- Uncertainty-aware recommendations that avoid overconfident or misleading guidance

### Practical Takeaways for AI Safety Practitioners

This repository offers a concrete, accessible demonstration of:

- **Production-ready calibration**: 25+ test suite ensuring prediction interval validity (analogous to LLM safety evaluations)
- **Human-in-the-loop design**: Dashboard interface enables users to explore uncertainty and override model recommendations
- **Failure mode analysis**: Explicit documentation of model limitations (poor performance on luxury properties, absence of seasonal patterns)

For researchers working on AI safety, this project provides a **working reference implementation** of uncertainty quantification best practices that scale from pricing models to frontier AI systems.

## 📁 Project Structure

```plaintext
├── README.md
├── CONTRIBUTING.md
├── LICENSE
├── requirements.txt
├── requirements-dashboard.txt
├── run_dashboard.sh
├── data
│   └── raw
│       ├── calendar.csv
│       ├── listings.csv
│       ├── neighbourhoods.csv
│       ├── neighbourhoods.geojson
│       └── reviews.csv
├── dashboard
│   ├── app.py                          # Main dashboard application
│   ├── components
│   │   ├── price_predictor.py         # Price prediction interface
│   │   ├── investment_analyzer.py     # ROI calculator
│   │   ├── neighborhood_comparison.py # Neighborhood analysis
│   │   ├── model_validation.py        # Model performance metrics
│   │   └── feature_impact.py          # Amenity impact calculator
│   └── utils
│       ├── data_loader.py             # Data loading utilities
│       └── styling.py                 # Misty Morning theme
├── gitpics                             # Dashboard screenshots
│   ├── Home screen pick.png
│   ├── Investment Analyzer.png
│   ├── Investment Analysis Results.png
│   ├── Comparison Results.png
│   ├── Investment Opportunity Score.png
│   ├── model Performance Overview.png
│   ├── Price Distribution.png
│   ├── Property Type Distribution.png
│   └── Residual Analysis.png
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
│       └── [analysis visualizations]
├── .streamlit
│   └── config.toml                    # Streamlit theme configuration
└── .github
    ├── ISSUE_TEMPLATE
    └── workflows
        └── ci.yml
```

## Example Usage

### Dashboard Usage

Simply launch the dashboard and use the sidebar navigation to explore different tools:

```bash
./run_dashboard.sh
```

### Programmatic Usage

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

## Future Enhancements

See [`FURTHER_EXPLORATION.md`](FURTHER_EXPLORATION.md) for detailed roadmap including:

- **Advanced Models**: Robust likelihoods, spatial correlation, temporal dynamics
- **Feature Engineering**: Text analytics, external data integration, host behavior modeling
- **Business Intelligence**: Real-time pricing engines, portfolio optimization
- **Production Systems**: MLOps pipelines, A/B testing, monitoring frameworks
- **Dashboard Enhancements**: Real-time data integration, user authentication, export capabilities

## Technical Details

### Dependencies
- **PyMC**: Bayesian modeling and MCMC sampling
- **Streamlit**: Interactive dashboard framework
- **ArviZ**: Bayesian analysis and diagnostics
- **NumPy/Pandas**: Data manipulation and numerical computing
- **Matplotlib/Seaborn**: Visualization and plotting
- **Scikit-learn**: Cross-validation and metrics

### Data Sources
- **Inside Airbnb**: Seattle listings and calendar data
- **Neighborhood boundaries**: GeoJSON format for spatial analysis
- **Derived features**: Strategic scoring, investment metrics, pricing recommendations

### Dashboard Theme
- **Misty Morning**: Custom color palette with dark teal (#2f4f4f), sage green (#77b899), and cream (#f5f5dc)
- **Responsive Design**: Mobile-friendly layouts and adaptive components
- **Accessibility**: High-contrast text and clear visual hierarchy

## Contributing

Contributions are welcome! Areas of particular interest:
- Dashboard enhancements and new visualizations
- Model improvements (robust likelihoods, spatial modeling)
- Feature engineering (text analytics, external data)
- Production deployment tools
- Documentation and tutorials

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

**Dennis J. Carroll**
- GitHub: [@Dennis-J-Carroll](https://github.com/Dennis-J-Carroll)
- Project: [Bayesian-Analysis-of-Airbnb-Seattle-Market](https://github.com/Dennis-J-Carroll/Bayesian-Analysis-of-Airbnb-Seattle-Market)

---

*Built with ❤️ using PyMC, Streamlit, and Bayesian methods for data-driven business intelligence*

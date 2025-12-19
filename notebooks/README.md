# Jupyter Notebooks

This directory contains comprehensive Jupyter notebooks documenting the complete analytical workflow for the Bayesian Airbnb pricing analysis.

## 📚 Notebook Sequence

### 01-data-exploration-and-cleaning.ipynb
**Data Preparation and Quality Assessment**

- Load raw Seattle Airbnb data
- Handle missing values and outliers
- Initial price distribution analysis
- Neighborhood-level aggregation
- Export cleaned dataset for modeling

**Key Outputs:** `data/processed/listings_clean.csv`

---

### 02-exploratory-data-analysis.ipynb
**Statistical Analysis and Modeling Justification**

- Log-normality assessment of prices
- Neighborhood effect analysis
- Accommodates vs. price relationship
- Varying slopes investigation (justification for hierarchical model)
- Property type and feature correlation analysis

**Key Insights:**
- Price distribution is approximately log-normal ✓
- Significant variation in baseline prices across neighborhoods ✓
- Accommodates effect varies by neighborhood (varying slopes) ✓

---

### 03-hierarchical-bayesian-model.ipynb
**Bayesian Model Implementation**

- Build hierarchical model with varying intercepts and slopes
- MCMC sampling using PyMC NUTS sampler
- Convergence diagnostics (R-hat, ESS)
- Posterior analysis and parameter interpretation
- Neighborhood-level effect estimation
- Predictions with full uncertainty quantification

**Key Outputs:**
- `outputs/hierarchical_model_trace.nc` - Posterior samples
- `outputs/neighborhood_parameters.csv` - Estimated parameters
- `outputs/neighborhood_map.csv` - Neighborhood index mapping

**Model Performance:**
- Converged chains (R̂ < 1.01) ✓
- Effective sample size > 1000 ✓
- Interpretable neighborhood-specific parameters ✓

---

### 04-model-validation-and-results.ipynb
**Comprehensive Model Validation**

- Performance metrics (R², RMSE, MAE)
- Residual analysis and diagnostics
- Calibration assessment (prediction interval coverage)
- Posterior predictive checks
- Business-relevant prediction examples
- Final validation report

**Key Results:**
- R² ≈ 0.48 (explains 48% of price variation)
- RMSE ≈ $101, MAE ≈ $63
- Well-calibrated uncertainty (90% CI coverage ≈ 90%) ✓
- Production-ready for deployment ✓

---

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Launch Jupyter
jupyter notebook

# Or use JupyterLab
jupyter lab
```

## 📊 Expected Workflow

1. **Start with notebook 01** - Clean and prepare the data
2. **Run notebook 02** - Understand patterns and justify modeling approach
3. **Execute notebook 03** - Build and fit the Bayesian model (⚠️ takes ~10-15 minutes)
4. **Complete with notebook 04** - Validate performance and generate reports

## ⚙️ Technical Requirements

- **Python**: 3.9+
- **Key Libraries**: PyMC 5.2+, ArviZ, Pandas, NumPy, Matplotlib, Seaborn
- **Computational**: Bayesian sampling is CPU-intensive; recommend 4+ cores
- **Memory**: ~4GB RAM for full dataset

## 📝 Notes

- All notebooks include detailed markdown explanations and interpretations
- Code cells are designed to run sequentially (top to bottom)
- Visualizations use consistent styling for professional presentation
- Outputs are saved to `data/processed/` and `outputs/` directories
- Random seeds are set for reproducibility (RANDOM_SEED=42)

## 🔗 Integration with Main Project

These notebooks complement the production Python modules in `src/`:
- `src/hierarchical_bayesian_model.py` - Production model implementation
- `src/validation_framework.py` - Automated validation suite
- `src/business_strategy_framework.py` - Business intelligence layer
- `dashboard/` - Interactive Streamlit application

The notebooks provide **exploratory analysis and validation**, while the `src/` modules enable **production deployment** and the dashboard offers **end-user access**.
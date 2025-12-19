# API Documentation

## Core Classes

### HierarchicalBayesianPriceModel

Main class for Bayesian price modeling with hierarchical structure.

#### Constructor

```python
from src.hierarchical_bayesian_model import HierarchicalBayesianPriceModel

model = HierarchicalBayesianPriceModel(
    listings_path='data/raw/listings.csv',
    neighbourhoods_path=None  # Optional
)
```

**Parameters:**
- `listings_path` (str): Path to listings CSV file
- `neighbourhoods_path` (str, optional): Path to neighborhoods geojson (not currently used)

**Returns:** Model instance

---

#### Methods

##### `load_and_clean_data()`

Load and preprocess Airbnb listings data with feature engineering.

```python
model.load_and_clean_data()
```

**Returns:** `self` (for method chaining)

**Side effects:**
- Loads CSV data
- Cleans price column
- Adds property type encoding
- Calculates amenity scores
- Standardizes features
- Sets `model.data` DataFrame

**Example:**
```python
model = HierarchicalBayesianPriceModel('data/raw/listings.csv')
model.load_and_clean_data()

print(f"Loaded {len(model.data)} listings")
print(f"Neighborhoods: {model.n_neighborhoods}")
```

---

##### `build_enhanced_hierarchical_model()`

Construct the enhanced hierarchical Bayesian model with PyMC.

```python
model.build_enhanced_hierarchical_model()
```

**Returns:** `self` (for method chaining)

**Side effects:**
- Creates PyMC model structure
- Sets `model.model` attribute
- Defines priors and likelihood

**Example:**
```python
model.load_and_clean_data()
model.build_enhanced_hierarchical_model()
```

---

##### `fit_model_with_diagnostics(draws, tune, chains)`

Fit model using MCMC with comprehensive diagnostics.

```python
model.fit_model_with_diagnostics(
    draws=2000,
    tune=1000,
    chains=4
)
```

**Parameters:**
- `draws` (int): Number of samples per chain (default: 2000)
- `tune` (int): Number of warmup/tuning samples (default: 1000)
- `chains` (int): Number of independent MCMC chains (default: 4)

**Returns:** `self` (for method chaining)

**Side effects:**
- Runs MCMC sampling (takes 10-15 minutes)
- Sets `model.trace` with InferenceData
- Prints convergence diagnostics

**Example:**
```python
model.load_and_clean_data() \
     .build_enhanced_hierarchical_model() \
     .fit_model_with_diagnostics(draws=2000, tune=1000, chains=4)
```

---

##### `predict_prices(accommodates_values, neighborhood_name)`

Predict prices for given accommodates values in a neighborhood.

```python
predictions = model.predict_prices(
    accommodates_values=[2, 4, 6],
    neighborhood_name='Capitol Hill'
)
```

**Parameters:**
- `accommodates_values` (list): List of guest counts to predict for
- `neighborhood_name` (str): Name of neighborhood

**Returns:** Dictionary with predictions for each accommodates value
```python
{
    2: {
        'mean': 125.50,
        'median': 123.00,
        'ci_95': [95.00, 160.00],
        'with_uncertainty_ci': [85.00, 175.00]
    },
    4: { ... },
    ...
}
```

**Example:**
```python
predictions = model.predict_prices([2, 4, 6], 'Fremont')
for acc, pred in predictions.items():
    print(f"{acc} guests: ${pred['mean']:.2f} "
          f"(95% CI: ${pred['ci_95'][0]:.2f}-${pred['ci_95'][1]:.2f})")
```

---

##### `compare_neighborhoods(accommodates)`

Compare predicted prices across all neighborhoods.

```python
comparison = model.compare_neighborhoods(accommodates=4)
```

**Parameters:**
- `accommodates` (int): Number of guests for comparison (default: 4)

**Returns:** DataFrame with columns:
- `neighborhood`: Neighborhood name
- `mean_price`: Mean predicted price
- `median_price`: Median predicted price
- `ci_95_lower`: Lower 95% credible interval
- `ci_95_upper`: Upper 95% credible interval

**Example:**
```python
comparison = model.compare_neighborhoods(accommodates=4)
print(comparison.head(10))  # Top 10 most expensive neighborhoods
```

---

### BusinessStrategyFramework

Business intelligence and investment analysis framework.

#### Constructor

```python
from src.business_strategy_framework import BusinessStrategyFramework

strategy = BusinessStrategyFramework(
    data_path='data/raw/listings.csv',
    model=fitted_model  # Already fitted HierarchicalBayesianPriceModel
)
```

**Parameters:**
- `data_path` (str): Path to listings CSV
- `model` (HierarchicalBayesianPriceModel): Fitted model instance

---

#### Methods

##### `identify_strategic_neighborhoods(top_n)`

Identify neighborhoods with highest investment opportunity scores.

```python
opportunities = strategy.identify_strategic_neighborhoods(top_n=10)
```

**Parameters:**
- `top_n` (int): Number of top neighborhoods to return (default: 10)

**Returns:** DataFrame with columns:
- `neighborhood`: Neighborhood name
- `strategic_score`: Composite score (0-100)
- `market_penetration`: Market maturity score
- `price_growth_potential`: Underpricing opportunity
- `supply_gap`: Demand vs supply gap
- `host_opportunity`: Ease of entry score

**Example:**
```python
opportunities = strategy.identify_strategic_neighborhoods(top_n=5)
print(opportunities[['neighborhood', 'strategic_score']])
```

---

##### `calculate_investment_roi(neighborhood, investment_amount)`

Calculate 3-year ROI for investment in a neighborhood.

```python
roi = strategy.calculate_investment_roi(
    neighborhood='Fremont',
    investment_amount=350000
)
```

**Parameters:**
- `neighborhood` (str): Neighborhood name
- `investment_amount` (float): Initial investment ($)

**Returns:** Dictionary with:
```python
{
    'roi_percentage': 167.5,
    'annual_revenue': 34000,
    'annual_noi': 22100,
    'three_year_profit': 66300,
    'predicted_daily_rate': 145
}
```

**Example:**
```python
roi = strategy.calculate_investment_roi('Ballard', 400000)
print(f"3-Year ROI: {roi['roi_percentage']:.1f}%")
print(f"Annual NOI: ${roi['annual_noi']:,.0f}")
```

---

## Complete Workflows

### Workflow 1: Train and Save Model

```python
from src.hierarchical_bayesian_model import HierarchicalBayesianPriceModel
import arviz as az

# Initialize and train
model = HierarchicalBayesianPriceModel('data/raw/listings.csv')
model.load_and_clean_data()
model.build_enhanced_hierarchical_model()
model.fit_model_with_diagnostics(draws=2000, tune=1000, chains=4)

# Save trace for later use
az.to_netcdf(model.trace, 'outputs/model_trace.nc')
print("✓ Model saved to outputs/model_trace.nc")
```

---

### Workflow 2: Load Pre-trained Model

```python
from src.hierarchical_bayesian_model import HierarchicalBayesianPriceModel
import arviz as az

# Initialize (no fitting needed)
model = HierarchicalBayesianPriceModel('data/raw/listings.csv')
model.load_and_clean_data()
model.build_enhanced_hierarchical_model()

# Load pre-trained trace
model.trace = az.from_netcdf('outputs/model_trace.nc')
print("✓ Model loaded from saved trace")

# Now ready for predictions
predictions = model.predict_prices([2, 4, 6], 'Capitol Hill')
```

---

### Workflow 3: Batch Predictions

```python
import pandas as pd

# Define scenarios
scenarios = [
    {'neighborhood': 'Capitol Hill', 'accommodates': 2, 'amenity_score': 8.0},
    {'neighborhood': 'Fremont', 'accommodates': 4, 'amenity_score': 12.0},
    {'neighborhood': 'Ballard', 'accommodates': 6, 'amenity_score': 15.0},
    {'neighborhood': 'Queen Anne', 'accommodates': 4, 'amenity_score': 10.0},
]

results = []
for scenario in scenarios:
    # Note: Simplified - would need to call appropriate prediction method
    pred = model.predict_prices(
        [scenario['accommodates']],
        scenario['neighborhood']
    )[scenario['accommodates']]

    results.append({
        'neighborhood': scenario['neighborhood'],
        'accommodates': scenario['accommodates'],
        'amenity_score': scenario['amenity_score'],
        'predicted_price': pred['mean'],
        'ci_low': pred['ci_95'][0],
        'ci_high': pred['ci_95'][1]
    })

df_results = pd.DataFrame(results)
print(df_results)
```

---

### Workflow 4: Investment Analysis

```python
from src.hierarchical_bayesian_model import HierarchicalBayesianPriceModel
from src.business_strategy_framework import BusinessStrategyFramework

# Load and fit model
model = HierarchicalBayesianPriceModel('data/raw/listings.csv')
model.load_and_clean_data()
model.build_enhanced_hierarchical_model()
model.fit_model_with_diagnostics()

# Initialize strategy framework
strategy = BusinessStrategyFramework('data/raw/listings.csv', model)

# Find strategic neighborhoods
opportunities = strategy.identify_strategic_neighborhoods(top_n=10)
print("\nTop Strategic Neighborhoods:")
print(opportunities[['neighborhood', 'strategic_score']])

# Analyze ROI for top neighborhood
top_neighborhood = opportunities.iloc[0]['neighborhood']
roi = strategy.calculate_investment_roi(top_neighborhood, investment_amount=350000)

print(f"\nROI Analysis for {top_neighborhood}:")
print(f"  3-Year ROI: {roi['roi_percentage']:.1f}%")
print(f"  Annual Revenue: ${roi['annual_revenue']:,.0f}")
print(f"  Annual NOI: ${roi['annual_noi']:,.0f}")
```

---

### Workflow 5: Model Comparison

```python
from src.model_comparison import ModelComparison
from src.hierarchical_bayesian_model import HierarchicalBayesianPriceModel

# Old model metrics (from basic model)
old_metrics = {
    'R²': 0.481,
    'RMSE': 100.91,
    'MAE': 63.22,
    'MAPE': 42.3
}

# Test new model with holdout validation
comparison = ModelComparison('data/raw/listings.csv')
new_model = HierarchicalBayesianPriceModel('data/raw/listings.csv')

print("Running holdout validation (this will take 15-20 minutes)...")
new_metrics = comparison.holdout_validation(new_model, test_size=0.2)

# Generate comparison report
comparison.generate_comparison_report(old_metrics, new_metrics)
```

---

### Workflow 6: Dynamic Pricing Strategy

```python
import numpy as np

# Get posterior samples for a listing
neighborhood_idx = model.neighborhood_lookup['Capitol Hill']
property_type = 1  # Entire home
accommodates_std = (4 - model.data['accommodates'].mean()) / model.data['accommodates'].std()
amenity_score_std = (12.0 - model.data['amenity_score'].mean()) / model.data['amenity_score'].std()
log_reviews = np.log1p(50)

# Extract posterior samples
alpha_neighborhood = model.trace.posterior['α_neighborhood'].values[:, :, neighborhood_idx].flatten()
alpha_property = model.trace.posterior['α_property'].values[:, :, property_type].flatten()
beta_accommodates = model.trace.posterior['β_accommodates'].values[:, :, neighborhood_idx].flatten()
beta_amenities = model.trace.posterior['β_amenities'].values.flatten()
beta_reviews = model.trace.posterior['β_reviews'].values.flatten()
mu_alpha = model.trace.posterior['μ_α'].values.flatten()

# Compute log price posterior
log_price_samples = (
    mu_alpha +
    alpha_neighborhood +
    alpha_property +
    beta_accommodates * accommodates_std +
    beta_amenities * amenity_score_std +
    beta_reviews * log_reviews
)

# Convert to price scale
price_samples = np.exp(log_price_samples)

# Pricing strategies
pricing = {
    'competitive': np.percentile(price_samples, 25),
    'median': np.percentile(price_samples, 50),
    'premium': np.percentile(price_samples, 75),
    'luxury': np.percentile(price_samples, 90)
}

print("Dynamic Pricing Strategies:")
for strategy, price in pricing.items():
    print(f"  {strategy.capitalize()}: ${price:.2f}/night")
```

---

## Advanced Usage

### Custom Prior Specifications

```python
import pymc as pm

# Modify priors before building model
class CustomModel(HierarchicalBayesianPriceModel):
    def build_enhanced_hierarchical_model(self):
        # ... (copy existing code, modify priors)

        # Example: Stronger prior on amenities
        β_amenities = pm.Normal('β_amenities', mu=0.20, sigma=0.03)  # Tighter prior

        # Continue with rest of model...
```

### Model Diagnostics Visualization

```python
import arviz as az
import matplotlib.pyplot as plt

# Trace plots
az.plot_trace(model.trace, var_names=['μ_α', 'β_amenities', 'β_reviews'])
plt.tight_layout()
plt.savefig('outputs/trace_plots.png')

# Posterior distributions
az.plot_posterior(model.trace, var_names=['β_amenities', 'β_reviews'])
plt.savefig('outputs/posterior_distributions.png')

# Forest plot (compare coefficients)
az.plot_forest(model.trace, var_names=['β_amenities', 'β_reviews'])
plt.savefig('outputs/coefficient_comparison.png')
```

### Posterior Predictive Checks

```python
import arviz as az

# Generate posterior predictive samples
with model.model:
    posterior_predictive = pm.sample_posterior_predictive(
        model.trace,
        random_seed=42
    )

# Compare observed vs predicted
az.plot_ppc(model.trace, num_pp_samples=100)
plt.savefig('outputs/posterior_predictive_check.png')
```

---

## Error Handling

### Graceful Degradation

```python
try:
    model = HierarchicalBayesianPriceModel('data/raw/listings.csv')
    model.load_and_clean_data()
    model.build_enhanced_hierarchical_model()
    model.fit_model_with_diagnostics()
except FileNotFoundError:
    print("Error: listings.csv not found. Download data first.")
except ValueError as e:
    print(f"Data error: {e}")
    print("Check that CSV has required columns.")
except Exception as e:
    print(f"Model fitting failed: {e}")
    print("Try reducing draws/chains or using variational inference.")
```

### Validation

```python
# Validate model convergence
import arviz as az

rhat = az.rhat(model.trace)
max_rhat = float(rhat.max())

if max_rhat > 1.01:
    print(f"⚠ Warning: Max R-hat = {max_rhat:.4f}")
    print("Chains may not have converged. Consider:")
    print("  1. Increase tune iterations")
    print("  2. Increase target_accept to 0.99")
    print("  3. Check for divergences")
else:
    print(f"✓ All chains converged (max R-hat = {max_rhat:.4f})")
```

---

For technical details, see [TECHNICAL.md](TECHNICAL.md)
For business use cases, see [BUSINESS.md](BUSINESS.md)
For setup instructions, see [SETUP.md](SETUP.md)

"""
Model Comparison Runner
Compares old vs enhanced model performance
"""

from src.hierarchical_bayesian_model import HierarchicalBayesianPriceModel
from src.model_comparison import ModelComparison

# Note: This assumes you have old model results saved
# If not, we'll document what the old metrics were

print("="*70)
print("RUNNING MODEL COMPARISON")
print("="*70)

# Old model metrics (from previous runs with basic model)
old_metrics = {
    'R²': 0.481,
    'RMSE': 100.91,
    'MAE': 63.22,
    'MAPE': 42.3
}

print("\n⏳ Testing new enhanced model...")

# New model
comparison = ModelComparison('data/raw/listings.csv')
new_model = HierarchicalBayesianPriceModel('data/raw/listings.csv')

new_metrics = comparison.holdout_validation(new_model)

# Generate report
comparison.generate_comparison_report(old_metrics, new_metrics)

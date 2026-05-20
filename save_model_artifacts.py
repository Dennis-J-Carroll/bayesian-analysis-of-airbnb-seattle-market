# save_model_artifacts.py
from src.hierarchical_bayesian_model import HierarchicalBayesianPriceModel
import arviz as az
import os


print("⏳ Fitting model locally...")
model = HierarchicalBayesianPriceModel("data/raw/listings.csv")
model.load_and_clean_data()
model.build_hierarchical_model()
model.fit_model()

print("💾 Saving model traces...")
az.to_netcdf(model.trace, "outputs/model_trace.nc")

print("✅ Model artifacts saved to outputs/model_trace.nc")
print(f"   File size: {os.path.getsize('outputs/model_trace.nc') / 1024 / 1024:.1f} MB")

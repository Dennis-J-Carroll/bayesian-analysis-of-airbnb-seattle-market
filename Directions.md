## Extra Directions  ##


data Flow::



listings.csv + neighbourhoods.csv
         ↓
hierarchical_bayesian_model.py (existing)
    - Loads and cleans data
    - Fits the model
    - Stores processed DataFrame
         ↓
    ┌────┴─────┬──────────┬────────────┐
    ↓          ↓          ↓            ↓
baseline_  varying_  prescriptive_  streamlit
comparison  slopes    pricing        dashboard



How the New Scripts Should Be Modified
Here's the corrected pattern for each new script:
1. Baseline Comparison (CORRECTED)


# src/baseline_comparison.py

class BaselineComparison:
    """Compare hierarchical Bayesian model against OLS baseline"""
    
    def __init__(self, bayesian_model):
        """
        Args:
            bayesian_model: Your existing HierarchicalBayesianPriceModel instance
                           (already has data loaded in .data attribute)
        """
        self.bayes_model = bayesian_model
        self.data = bayesian_model.data  # Use the already-loaded data
        
    def fit_ols_baseline(self):
        """Fit simple OLS with neighborhood dummies"""
        # Use the pre-processed data from your model
        X = pd.get_dummies(
            self.data[['accommodates', 'reviews_sc', 'room_type', 'neighbourhood_cleansed']], 
            columns=['room_type', 'neighbourhood_cleansed'],
            drop_first=True
        )
        y = self.data['log_price']  # Your model already computed this
        
        # ... rest of the code stays the same
        
        
        # src/varying_slopes_analysis.py







-----------------------------------------------------------------------------------------------------------------------

 Varying Slopes Analysis (CORRECTED) ::
 
 
 
 
 









class VaryingSlopesAnalysis:
    """Extract and interpret neighborhood-specific accommodates effects"""
    
    def __init__(self, fitted_model):
        """
        Args:
            fitted_model: Your existing HierarchicalBayesianPriceModel instance
                         (already fitted, with data loaded)
        """
        self.model = fitted_model
        self.data = fitted_model.data  # Use the already-loaded data
        
    def extract_neighborhood_effects(self):
        """Get varying slopes and intercepts by neighborhood"""
        
        # Your model stores posterior samples - extract them
        # (Exact method depends on how you stored the PyMC results)
        trace = self.model.trace  # or however you stored it
        
        # Extract varying effects
        # If using PyMC3/PyMC:
        alpha = trace.posterior['alpha'].mean(dim=['chain', 'draw']).values
        beta = trace.posterior['beta'].mean(dim=['chain', 'draw']).values
        
        # Map to neighborhood names
        neighbourhood_names = self.data['neighbourhood_cleansed'].unique()
        
        # ... rest of the code
        
      
      
      
      
-------------------------------------------------------------------------------------------------------------




Prescriptive Pricing (CORRECTED)::





# src/prescriptive_pricing.py

class PrescriptivePricingEngine:
    """Convert statistical model into actionable pricing recommendations"""
    
    def __init__(self, bayesian_model, varying_slopes_analysis):
        """
        Args:
            bayesian_model: Your fitted HierarchicalBayesianPriceModel
            varying_slopes_analysis: VaryingSlopesAnalysis instance
        """
        self.model = bayesian_model
        self.slopes = varying_slopes_analysis
        self.data = bayesian_model.data  # Use the already-loaded data
        
    def recommend_price(self, neighbourhood, accommodates, reviews, room_type):
        """Generate price recommendation with uncertainty bands"""
        
        # Use your model's posterior to generate predictions
        # Exact method depends on your PyMC implementation
        
        # Example if you have a predict method:
        posterior_samples = self.model.predict_new_observation(
            neighbourhood=neighbourhood,
            accommodates=accommodates,
            reviews=reviews,
            room_type=room_type,
            n_samples=10000
        )
        
        # ... rest of the code
        
        
        
        
----------------------------------------------------------------------------------------------------------


Usage pattern (How it fits together)::





# main_analysis.py or jupyter notebook

from src.hierarchical_bayesian_model import HierarchicalBayesianPriceModel
from src.baseline_comparison import BaselineComparison
from src.varying_slopes_analysis import VaryingSlopesAnalysis
from src.prescriptive_pricing import PrescriptivePricingEngine

# 1. Load data ONCE using your existing model
model = HierarchicalBayesianPriceModel(
    listings_path='data/raw/listings.csv',
    neighbourhoods_path='data/raw/neighbourhoods.csv'  # optional
)

# 2. Process data ONCE
model.load_and_clean_data()

# 3. Fit the model ONCE
model.build_hierarchical_model()
model.fit_model()

# 4. Now pass the FITTED MODEL to the new analysis classes
# They'll use model.data internally, no re-loading

baseline_comp = BaselineComparison(model)
ols_results = baseline_comp.fit_ols_baseline()
comparison_table = baseline_comp.compare_models()

slopes_analysis = VaryingSlopesAnalysis(model)
neighborhood_effects = slopes_analysis.extract_neighborhood_effects()
insights = slopes_analysis.interpret_patterns(neighborhood_effects)

pricing_engine = PrescriptivePricingEngine(model, slopes_analysis)
recommendation = pricing_engine.recommend_price(
    neighbourhood='Capitol Hill',
    accommodates=4,
    reviews=50,
    room_type='Entire home/apt'
)

print(recommendation['rationale'])






--The Key Insight--
The scripts I wrote in the plan are templates. You need to adapt them to:

Accept your fitted model as input (not file paths)
Use model.data for the processed DataFrame
Use model.trace or model.posterior for posterior samples (depending on how you stored PyMC results)

The pattern is always:
class NewAnalysis:
    def __init__(self, fitted_bayesian_model):
        self.model = fitted_bayesian_model
        self.data = fitted_bayesian_model.data  # Already loaded and cleaned

"""
Model Comparison Framework
Compare old vs new model performance with comprehensive metrics
"""

import numpy as np
import pandas as pd
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from sklearn.model_selection import KFold
import matplotlib.pyplot as plt
import seaborn as sns


class ModelComparison:
    """Compare old vs new model performance"""

    def __init__(self, data_path):
        self.data_path = data_path
        self.data = pd.read_csv(data_path)

    def compute_metrics(self, y_true, y_pred):
        """Compute regression metrics"""
        return {
            'R²': r2_score(y_true, y_pred),
            'RMSE': np.sqrt(mean_squared_error(y_true, y_pred)),
            'MAE': mean_absolute_error(y_true, y_pred),
            'MAPE': np.mean(np.abs((y_true - y_pred) / y_true)) * 100
        }

    def holdout_validation(self, model, test_size=0.2):
        """Single train/test split validation"""
        from sklearn.model_selection import train_test_split

        train_data, test_data = train_test_split(
            self.data, test_size=test_size, random_state=42
        )

        # Fit on training data
        model.load_and_clean_data()
        model.data = train_data
        model.build_enhanced_hierarchical_model()
        model.fit_model_with_diagnostics(draws=1000, tune=500, chains=2)

        # Predict on test data
        y_true = test_data['price'].values
        predictions = []

        for idx, row in test_data.iterrows():
            pred = model.predict_price(
                neighborhood=row['neighbourhood_cleansed'],
                property_type=row['property_type_idx'],
                accommodates=row['accommodates'],
                amenity_score=row['amenity_score'],
                n_reviews=row['number_of_reviews']
            )
            predictions.append(pred['mean'])

        y_pred = np.array(predictions)

        return self.compute_metrics(y_true, y_pred)

    def generate_comparison_report(self, old_metrics, new_metrics):
        """Generate formatted comparison report"""

        print("\n" + "="*70)
        print("MODEL PERFORMANCE COMPARISON")
        print("="*70)

        print("\n📊 OLD MODEL (accommodates only)")
        print("-"*70)
        for metric, value in old_metrics.items():
            print(f"  {metric:8s}: {value:.4f}")

        print("\n📊 NEW MODEL (property type + amenities + reviews)")
        print("-"*70)
        for metric, value in new_metrics.items():
            print(f"  {metric:8s}: {value:.4f}")

        print("\n📈 IMPROVEMENT")
        print("-"*70)
        for metric in old_metrics.keys():
            old_val = old_metrics[metric]
            new_val = new_metrics[metric]

            if metric == 'R²':
                improvement = new_val - old_val
                pct_improvement = (improvement / old_val) * 100
                print(f"  {metric:8s}: +{improvement:.4f} ({pct_improvement:+.1f}%)")
            else:
                improvement = ((old_val - new_val) / old_val) * 100
                print(f"  {metric:8s}: {improvement:+.1f}% reduction")

        print("\n" + "="*70)

        # Save to file
        with open('outputs/model_comparison_report.txt', 'w') as f:
            f.write("MODEL PERFORMANCE COMPARISON\n")
            f.write("="*70 + "\n\n")
            f.write("OLD MODEL\n")
            f.write("-"*70 + "\n")
            for metric, value in old_metrics.items():
                f.write(f"{metric:8s}: {value:.4f}\n")
            f.write("\nNEW MODEL\n")
            f.write("-"*70 + "\n")
            for metric, value in new_metrics.items():
                f.write(f"{metric:8s}: {value:.4f}\n")

        print("\n✅ Report saved to: outputs/model_comparison_report.txt")

        return old_metrics, new_metrics

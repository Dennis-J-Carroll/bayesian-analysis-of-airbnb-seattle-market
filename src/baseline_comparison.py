"""
Baseline Comparison Module
Compare hierarchical Bayesian model against OLS baseline
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
import warnings

warnings.filterwarnings("ignore")


class BaselineComparison:
    """Compare hierarchical Bayesian model against OLS baseline"""

    def __init__(self, bayesian_model):
        """
        Args:
            bayesian_model: Your existing HierarchicalBayesianPriceModel instance
                           (already has data loaded in .data attribute)
        """
        self.bayes_model = bayesian_model
        self.data = bayesian_model.data
        self.ols_model = None
        self.X = None
        self.y = None

    def fit_ols_baseline(self):
        """Fit simple OLS with neighborhood dummies"""
        # Use the pre-processed data from your model
        X = pd.get_dummies(
            self.data[["accommodates", "neighbourhood_cleansed"]],
            columns=["neighbourhood_cleansed"],
            drop_first=True,
        )
        y = self.data["log_price"]

        # Fit OLS
        self.ols_model = LinearRegression()
        self.ols_model.fit(X, y)
        self.X = X
        self.y = y

        # Get predictions
        y_pred = self.ols_model.predict(X)

        # Calculate metrics
        r2 = r2_score(y, y_pred)
        mae = mean_absolute_error(y, y_pred)
        rmse = np.sqrt(mean_squared_error(y, y_pred))

        print("\n=== OLS Baseline Results ===")
        print(f"R²: {r2:.4f}")
        print(f"MAE (log scale): {mae:.4f}")
        print(f"RMSE (log scale): {rmse:.4f}")

        return {
            "model": self.ols_model,
            "r2": r2,
            "mae": mae,
            "rmse": rmse,
            "predictions": y_pred,
        }

    def compare_models(self):
        """Compare Bayesian and OLS models"""
        if self.ols_model is None:
            print("OLS model not fitted yet. Running fit_ols_baseline()...")
            self.fit_ols_baseline()

        # OLS predictions (already on log scale)
        ols_pred = self.ols_model.predict(self.X)

        # Bayesian predictions (get posterior means)
        alpha_samples = self.bayes_model.trace.posterior["alpha"].values.reshape(
            -1, self.bayes_model.n_neighborhoods
        )
        beta_samples = self.bayes_model.trace.posterior["beta"].values.reshape(
            -1, self.bayes_model.n_neighborhoods
        )

        alpha_mean = alpha_samples.mean(axis=0)
        beta_mean = beta_samples.mean(axis=0)

        accommodates = self.data["accommodates"].values
        neighborhood_idx = self.data["neighborhood_idx"].values

        bayes_pred = (
            alpha_mean[neighborhood_idx] + beta_mean[neighborhood_idx] * accommodates
        )

        # Calculate metrics for both
        y_true = self.data["log_price"].values

        # Bayesian metrics
        bayes_r2 = r2_score(y_true, bayes_pred)
        bayes_mae = mean_absolute_error(y_true, bayes_pred)
        bayes_rmse = np.sqrt(mean_squared_error(y_true, bayes_pred))

        # OLS metrics
        ols_r2 = r2_score(y_true, ols_pred)
        ols_mae = mean_absolute_error(y_true, ols_pred)
        ols_rmse = np.sqrt(mean_squared_error(y_true, ols_pred))

        # Create comparison table
        comparison = pd.DataFrame(
            {
                "Metric": ["R²", "MAE (log)", "RMSE (log)", "MAE ($)", "RMSE ($)"],
                "OLS Baseline": [
                    ols_r2,
                    ols_mae,
                    ols_rmse,
                    np.exp(ols_mae),
                    np.exp(ols_rmse),
                ],
                "Hierarchical Bayes": [
                    bayes_r2,
                    bayes_mae,
                    bayes_rmse,
                    np.exp(bayes_mae),
                    np.exp(bayes_rmse),
                ],
            }
        )

        comparison["Difference"] = (
            comparison["Hierarchical Bayes"] - comparison["OLS Baseline"]
        )
        comparison["% Improvement"] = (
            (comparison["Hierarchical Bayes"] - comparison["OLS Baseline"])
            / comparison["OLS Baseline"]
            * 100
        )

        print("\n=== Model Comparison ===")
        print(comparison.to_string(index=False))

        return comparison

    def get_prediction_intervals(self, n_samples=100):
        """
        Compare prediction intervals
        Bayesian model provides natural uncertainty quantification
        OLS requires bootstrapping for comparable intervals
        """
        # Sample random observations
        sample_idx = np.random.choice(len(self.data), n_samples, replace=False)
        sample_data = self.data.iloc[sample_idx]

        results = []

        for idx, row in sample_data.iterrows():
            neighborhood = row["neighbourhood_cleansed"]
            accommodates = row["accommodates"]
            actual_price = row["price_clean"]

            # Bayesian prediction with uncertainty
            neighborhood_idx = self.bayes_model.neighborhood_lookup[neighborhood]

            alpha_samples = self.bayes_model.trace.posterior["alpha"].values.reshape(
                -1, self.bayes_model.n_neighborhoods
            )[:, neighborhood_idx]
            beta_samples = self.bayes_model.trace.posterior["beta"].values.reshape(
                -1, self.bayes_model.n_neighborhoods
            )[:, neighborhood_idx]

            log_price_pred = alpha_samples + beta_samples * accommodates
            price_pred = np.exp(log_price_pred)

            bayes_median = np.median(price_pred)
            bayes_ci = np.percentile(price_pred, [5, 95])

            # OLS prediction (point estimate only)
            X_new = pd.get_dummies(
                pd.DataFrame(
                    {
                        "accommodates": [accommodates],
                        "neighbourhood_cleansed": [neighborhood],
                    }
                ),
                columns=["neighbourhood_cleansed"],
                drop_first=True,
            )

            # Ensure all columns from training are present
            for col in self.X.columns:
                if col not in X_new.columns:
                    X_new[col] = 0
            X_new = X_new[self.X.columns]

            ols_log_pred = self.ols_model.predict(X_new)[0]
            ols_pred = np.exp(ols_log_pred)

            results.append(
                {
                    "neighborhood": neighborhood,
                    "accommodates": accommodates,
                    "actual": actual_price,
                    "bayes_median": bayes_median,
                    "bayes_ci_lower": bayes_ci[0],
                    "bayes_ci_upper": bayes_ci[1],
                    "ols_pred": ols_pred,
                    "bayes_in_ci": (actual_price >= bayes_ci[0])
                    and (actual_price <= bayes_ci[1]),
                }
            )

        results_df = pd.DataFrame(results)

        # Calculate coverage
        coverage = results_df["bayes_in_ci"].mean()
        print(f"\nBayesian 90% CI Coverage: {coverage:.2%} (target: 90%)")

        return results_df

    def summarize_advantages(self):
        """Summarize key advantages of hierarchical model"""
        comparison = self.compare_models()

        print("\n=== Key Advantages of Hierarchical Bayesian Model ===")

        advantages = []

        # Uncertainty quantification
        advantages.append(
            "1. UNCERTAINTY QUANTIFICATION: Provides natural credible intervals for predictions"
        )

        # Partial pooling
        advantages.append(
            "2. PARTIAL POOLING: Shares information across neighborhoods, improving estimates for low-data neighborhoods"
        )

        # Interpretability
        advantages.append(
            "3. INTERPRETABILITY: Separate neighborhood effects (varying intercepts and slopes)"
        )

        # Regularization
        r2_diff = comparison.loc[comparison["Metric"] == "R²", "Difference"].values[0]
        if r2_diff > 0:
            advantages.append(
                f"4. BETTER FIT: R² improvement of {r2_diff:.4f} over OLS baseline"
            )

        # Coverage
        pred_intervals = self.get_prediction_intervals(n_samples=50)
        coverage = pred_intervals["bayes_in_ci"].mean()
        advantages.append(
            f"5. CALIBRATED PREDICTIONS: {coverage:.1%} of actual prices fall within 90% credible intervals"
        )

        for adv in advantages:
            print(f"  {adv}")

        return advantages

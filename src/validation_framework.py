"""
Comprehensive Validation Framework for Hierarchical Bayesian Price Model
- Posterior predictive checks
- Cross-validation across neighborhoods  
- Model calibration monitoring
- Performance metrics and diagnostics
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pymc as pm
import arviz as az
from scipy import stats
from sklearn.model_selection import KFold, GroupKFold
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from hierarchical_bayesian_model import HierarchicalBayesianPriceModel
import warnings

warnings.filterwarnings("ignore")


class ValidationFramework:
    def __init__(self, data_path, hierarchical_model=None):
        """Initialize validation framework with data and model."""
        self.data_path = data_path
        self.hierarchical_model = hierarchical_model
        self.validation_results = {}
        self.cv_results = {}
        self.calibration_history = []

    def load_validation_data(self):
        """Load and prepare data for validation."""
        if self.hierarchical_model is None:
            self.hierarchical_model = HierarchicalBayesianPriceModel(self.data_path)
            self.hierarchical_model.load_and_clean_data()

        return self.hierarchical_model.data

    def posterior_predictive_checks(self, n_samples=1000):
        """Comprehensive posterior predictive checks."""

        if self.hierarchical_model is None or self.hierarchical_model.trace is None:
            print("Loading and fitting model for validation...")
            self.hierarchical_model = HierarchicalBayesianPriceModel(self.data_path)
            self.hierarchical_model.load_and_clean_data()
            self.hierarchical_model.build_hierarchical_model()
            self.hierarchical_model.fit_model(samples=1000, tune=500, chains=2)

        data = self.hierarchical_model.data
        observed_log_prices = np.log(data["price_clean"].values)
        accommodates = data["accommodates"].values
        neighborhood_idx = data["neighborhood_idx"].values

        # Extract posterior samples
        alpha_samples = self.hierarchical_model.trace.posterior["alpha"].values.reshape(
            -1, self.hierarchical_model.n_neighborhoods
        )
        beta_samples = self.hierarchical_model.trace.posterior["beta"].values.reshape(
            -1, self.hierarchical_model.n_neighborhoods
        )
        sigma_samples = self.hierarchical_model.trace.posterior[
            "sigma"
        ].values.flatten()

        # Generate posterior predictive samples
        n_obs = len(observed_log_prices)
        n_posterior_samples = min(n_samples, len(alpha_samples))

        posterior_predictions = []

        for i in range(n_posterior_samples):
            # Predict mean log price
            predicted_mean = (
                alpha_samples[i][neighborhood_idx]
                + beta_samples[i][neighborhood_idx] * accommodates
            )

            # Add residual noise
            predicted_log_prices = np.random.normal(
                predicted_mean, sigma_samples[i % len(sigma_samples)]
            )
            posterior_predictions.append(predicted_log_prices)

        posterior_predictions = np.array(posterior_predictions)

        # Calculate test statistics for observed and predicted data
        test_stats = self._calculate_test_statistics(
            observed_log_prices, posterior_predictions
        )

        # Store results
        self.validation_results["posterior_predictive"] = {
            "observed_log_prices": observed_log_prices,
            "posterior_predictions": posterior_predictions,
            "test_statistics": test_stats,
            "accommodates": accommodates,
            "neighborhood_idx": neighborhood_idx,
        }

        return test_stats

    def _calculate_test_statistics(self, observed, predicted_samples):
        """Calculate various test statistics for posterior predictive checks."""

        test_stats = {}

        # For each posterior sample, calculate test statistics
        predicted_stats = []
        for pred_sample in predicted_samples:
            stats_sample = {
                "mean": np.mean(pred_sample),
                "std": np.std(pred_sample),
                "min": np.min(pred_sample),
                "max": np.max(pred_sample),
                "q25": np.percentile(pred_sample, 25),
                "q75": np.percentile(pred_sample, 75),
                "skewness": stats.skew(pred_sample),
                "kurtosis": stats.kurtosis(pred_sample),
            }
            predicted_stats.append(stats_sample)

        # Convert to arrays for easier analysis
        predicted_stats_df = pd.DataFrame(predicted_stats)

        # Calculate observed statistics
        observed_stats = {
            "mean": np.mean(observed),
            "std": np.std(observed),
            "min": np.min(observed),
            "max": np.max(observed),
            "q25": np.percentile(observed, 25),
            "q75": np.percentile(observed, 75),
            "skewness": stats.skew(observed),
            "kurtosis": stats.kurtosis(observed),
        }

        # Calculate p-values (proportion of predicted stats more extreme than observed)
        p_values = {}
        for stat in observed_stats.keys():
            if stat in ["min"]:
                p_values[stat] = np.mean(
                    predicted_stats_df[stat] <= observed_stats[stat]
                )
            elif stat in ["max"]:
                p_values[stat] = np.mean(
                    predicted_stats_df[stat] >= observed_stats[stat]
                )
            else:
                # Two-sided test
                obs_val = observed_stats[stat]
                pred_vals = predicted_stats_df[stat].values
                p_values[stat] = 2 * min(
                    np.mean(pred_vals <= obs_val), np.mean(pred_vals >= obs_val)
                )

        test_stats = {
            "observed": observed_stats,
            "predicted_distribution": predicted_stats_df,
            "p_values": p_values,
        }

        return test_stats

    def cross_validate_neighborhoods(self, n_folds=5, test_neighborhoods=None):
        """Cross-validate model performance across neighborhoods."""

        data = self.load_validation_data()

        # Prepare data
        log_prices = np.log(data["price_clean"].values)
        accommodates = data["accommodates"].values
        neighborhoods = data["neighbourhood_cleansed"].values

        # Create neighborhood-based cross-validation splits
        unique_neighborhoods = data["neighbourhood_cleansed"].unique()

        if test_neighborhoods is not None:
            # Use specific neighborhoods as test sets
            cv_splits = []
            for test_neighborhood in test_neighborhoods:
                train_mask = neighborhoods != test_neighborhood
                test_mask = neighborhoods == test_neighborhood
                if np.sum(test_mask) > 0:  # Only include if test set exists
                    cv_splits.append((np.where(train_mask)[0], np.where(test_mask)[0]))
        else:
            # Random neighborhood splits
            np.random.seed(42)
            neighborhoods_shuffled = np.random.permutation(unique_neighborhoods)
            neighborhood_folds = np.array_split(neighborhoods_shuffled, n_folds)

            cv_splits = []
            for fold_neighborhoods in neighborhood_folds:
                test_mask = np.isin(neighborhoods, fold_neighborhoods)
                train_mask = ~test_mask
                if np.sum(test_mask) > 0:  # Only include if test set exists
                    cv_splits.append((np.where(train_mask)[0], np.where(test_mask)[0]))

        cv_results = []

        for fold_idx, (train_idx, test_idx) in enumerate(cv_splits):
            print(f"Processing fold {fold_idx + 1}/{len(cv_splits)}...")

            # Create training and test datasets
            train_data = data.iloc[train_idx].copy()
            test_data = data.iloc[test_idx].copy()

            # Create temporary model for this fold
            fold_model = HierarchicalBayesianPriceModel(None)
            fold_model.data = train_data

            # Update neighborhood mappings for training data
            train_neighborhoods = train_data["neighbourhood_cleansed"].unique()
            neighborhood_lookup = {
                name: idx for idx, name in enumerate(train_neighborhoods)
            }
            train_data["neighborhood_idx"] = train_data["neighbourhood_cleansed"].map(
                neighborhood_lookup
            )
            fold_model.neighborhoods = train_neighborhoods
            fold_model.n_neighborhoods = len(train_neighborhoods)
            fold_model.data = train_data

            try:
                # Build and fit model on training data
                fold_model.build_hierarchical_model()
                fold_model.fit_model(samples=500, tune=250, chains=2)

                # Make predictions on test data
                test_neighborhoods_in_train = test_data["neighbourhood_cleansed"].isin(
                    train_neighborhoods
                )

                if np.sum(test_neighborhoods_in_train) > 0:
                    # Only predict for neighborhoods seen in training
                    test_subset = test_data[test_neighborhoods_in_train]
                    test_neighborhood_idx = test_subset["neighbourhood_cleansed"].map(
                        neighborhood_lookup
                    )

                    # Extract posterior means for prediction
                    alpha_mean = (
                        fold_model.trace.posterior["alpha"]
                        .values.reshape(-1, fold_model.n_neighborhoods)
                        .mean(axis=0)
                    )
                    beta_mean = (
                        fold_model.trace.posterior["beta"]
                        .values.reshape(-1, fold_model.n_neighborhoods)
                        .mean(axis=0)
                    )

                    # Predict log prices
                    predicted_log_prices = (
                        alpha_mean[test_neighborhood_idx]
                        + beta_mean[test_neighborhood_idx] * test_subset["accommodates"]
                    )
                    predicted_prices = np.exp(predicted_log_prices)

                    # Calculate metrics
                    actual_prices = test_subset["price_clean"].values
                    actual_log_prices = np.log(actual_prices)

                    metrics = {
                        "fold": fold_idx,
                        "n_train": len(train_idx),
                        "n_test": len(test_subset),
                        "test_neighborhoods": list(
                            test_subset["neighbourhood_cleansed"].unique()
                        ),
                        "rmse": np.sqrt(
                            mean_squared_error(actual_prices, predicted_prices)
                        ),
                        "mae": mean_absolute_error(actual_prices, predicted_prices),
                        "mape": np.mean(
                            np.abs((actual_prices - predicted_prices) / actual_prices)
                        )
                        * 100,
                        "r2": r2_score(actual_prices, predicted_prices),
                        "log_rmse": np.sqrt(
                            mean_squared_error(actual_log_prices, predicted_log_prices)
                        ),
                        "log_mae": mean_absolute_error(
                            actual_log_prices, predicted_log_prices
                        ),
                    }

                    cv_results.append(metrics)

            except Exception as e:
                print(f"Error in fold {fold_idx}: {str(e)}")
                continue

        # Store and summarize results
        self.cv_results = pd.DataFrame(cv_results)

        if not self.cv_results.empty:
            summary_stats = {
                "mean_rmse": self.cv_results["rmse"].mean(),
                "std_rmse": self.cv_results["rmse"].std(),
                "mean_mae": self.cv_results["mae"].mean(),
                "std_mae": self.cv_results["mae"].std(),
                "mean_mape": self.cv_results["mape"].mean(),
                "std_mape": self.cv_results["mape"].std(),
                "mean_r2": self.cv_results["r2"].mean(),
                "std_r2": self.cv_results["r2"].std(),
            }

            self.validation_results["cross_validation"] = {
                "fold_results": self.cv_results,
                "summary": summary_stats,
            }

        return self.cv_results

    def monitor_model_calibration(self, confidence_levels=[0.5, 0.8, 0.9, 0.95]):
        """Monitor model calibration using prediction intervals."""

        if "posterior_predictive" not in self.validation_results:
            self.posterior_predictive_checks()

        observed = self.validation_results["posterior_predictive"][
            "observed_log_prices"
        ]
        predictions = self.validation_results["posterior_predictive"][
            "posterior_predictions"
        ]

        calibration_results = {}

        for confidence_level in confidence_levels:
            alpha = 1 - confidence_level
            lower_percentile = (alpha / 2) * 100
            upper_percentile = (1 - alpha / 2) * 100

            # Calculate prediction intervals
            pred_lower = np.percentile(predictions, lower_percentile, axis=0)
            pred_upper = np.percentile(predictions, upper_percentile, axis=0)

            # Check coverage
            coverage = np.mean((observed >= pred_lower) & (observed <= pred_upper))

            # Calculate interval widths
            interval_widths = pred_upper - pred_lower
            avg_width = np.mean(interval_widths)

            calibration_results[confidence_level] = {
                "expected_coverage": confidence_level,
                "actual_coverage": coverage,
                "coverage_error": abs(coverage - confidence_level),
                "average_interval_width": avg_width,
                "well_calibrated": abs(coverage - confidence_level) < 0.05,  # Within 5%
            }

        # Overall calibration score
        calibration_errors = [
            result["coverage_error"] for result in calibration_results.values()
        ]
        overall_calibration_score = 1 - np.mean(calibration_errors)  # Higher is better

        self.validation_results["calibration"] = {
            "by_confidence_level": calibration_results,
            "overall_score": overall_calibration_score,
        }

        # Store in history for monitoring over time
        self.calibration_history.append(
            {
                "timestamp": pd.Timestamp.now(),
                "calibration_results": calibration_results,
                "overall_score": overall_calibration_score,
            }
        )

        return calibration_results

    def residual_analysis(self):
        """Comprehensive residual analysis."""

        if self.hierarchical_model is None or self.hierarchical_model.trace is None:
            print("Model not available for residual analysis")
            return None

        data = self.hierarchical_model.data
        observed_log_prices = np.log(data["price_clean"].values)
        accommodates = data["accommodates"].values
        neighborhood_idx = data["neighborhood_idx"].values

        # Get posterior means for residual calculation
        alpha_mean = (
            self.hierarchical_model.trace.posterior["alpha"]
            .values.reshape(-1, self.hierarchical_model.n_neighborhoods)
            .mean(axis=0)
        )
        beta_mean = (
            self.hierarchical_model.trace.posterior["beta"]
            .values.reshape(-1, self.hierarchical_model.n_neighborhoods)
            .mean(axis=0)
        )

        # Calculate fitted values and residuals
        fitted_log_prices = (
            alpha_mean[neighborhood_idx] + beta_mean[neighborhood_idx] * accommodates
        )
        residuals = observed_log_prices - fitted_log_prices

        # Standardized residuals
        sigma_mean = (
            self.hierarchical_model.trace.posterior["sigma"].values.flatten().mean()
        )
        standardized_residuals = residuals / sigma_mean

        # Residual analysis by neighborhood
        residual_by_neighborhood = {}
        for i, neighborhood in enumerate(self.hierarchical_model.neighborhoods):
            mask = neighborhood_idx == i
            if np.sum(mask) > 0:
                residual_by_neighborhood[neighborhood] = {
                    "residuals": residuals[mask],
                    "mean_residual": np.mean(residuals[mask]),
                    "std_residual": np.std(residuals[mask]),
                    "n_observations": np.sum(mask),
                }

        residual_results = {
            "residuals": residuals,
            "standardized_residuals": standardized_residuals,
            "fitted_values": fitted_log_prices,
            "by_neighborhood": residual_by_neighborhood,
            "overall_stats": {
                "mean_residual": np.mean(residuals),
                "std_residual": np.std(residuals),
                "jarque_bera_stat": stats.jarque_bera(residuals)[0],
                "jarque_bera_pvalue": stats.jarque_bera(residuals)[1],
                "durbin_watson": self._durbin_watson(residuals),
            },
        }

        self.validation_results["residuals"] = residual_results
        return residual_results

    def _durbin_watson(self, residuals):
        """Calculate Durbin-Watson statistic for autocorrelation."""
        diff_residuals = np.diff(residuals)
        return np.sum(diff_residuals**2) / np.sum(residuals**2)

    def create_validation_dashboard(self):
        """Create comprehensive validation dashboard."""

        fig, axes = plt.subplots(3, 3, figsize=(20, 15))

        # 1. Posterior Predictive Check - Summary Statistics
        if "posterior_predictive" in self.validation_results:
            test_stats = self.validation_results["posterior_predictive"][
                "test_statistics"
            ]

            stats_to_plot = ["mean", "std", "skewness", "kurtosis"]
            for i, stat in enumerate(stats_to_plot):
                ax = axes[0, i] if i < 2 else axes[1, i - 2]

                pred_dist = test_stats["predicted_distribution"][stat]
                obs_val = test_stats["observed"][stat]
                p_val = test_stats["p_values"][stat]

                ax.hist(pred_dist, bins=30, alpha=0.7, density=True, label="Predicted")
                ax.axvline(
                    obs_val,
                    color="red",
                    linestyle="--",
                    linewidth=2,
                    label=f"Observed (p={p_val:.3f})",
                )
                ax.set_title(f"PPC: {stat.title()}")
                ax.set_xlabel(stat.title())
                ax.set_ylabel("Density")
                ax.legend()

        # 2. Cross-Validation Results
        if not self.cv_results.empty:
            # RMSE across folds
            axes[0, 2].bar(
                range(len(self.cv_results)), self.cv_results["rmse"], alpha=0.7
            )
            axes[0, 2].set_title("RMSE Across CV Folds")
            axes[0, 2].set_xlabel("Fold")
            axes[0, 2].set_ylabel("RMSE ($)")

            # R² across folds
            axes[1, 2].bar(
                range(len(self.cv_results)),
                self.cv_results["r2"],
                alpha=0.7,
                color="green",
            )
            axes[1, 2].set_title("R² Across CV Folds")
            axes[1, 2].set_xlabel("Fold")
            axes[1, 2].set_ylabel("R²")
            axes[1, 2].axhline(y=0.5, color="red", linestyle="--", alpha=0.5)

        # 3. Model Calibration
        if "calibration" in self.validation_results:
            calib_results = self.validation_results["calibration"][
                "by_confidence_level"
            ]

            confidence_levels = list(calib_results.keys())
            expected_coverage = confidence_levels
            actual_coverage = [
                calib_results[cl]["actual_coverage"] for cl in confidence_levels
            ]

            axes[2, 0].plot(
                expected_coverage, expected_coverage, "k--", label="Perfect Calibration"
            )
            axes[2, 0].plot(
                expected_coverage, actual_coverage, "ro-", label="Actual Calibration"
            )
            axes[2, 0].set_xlabel("Expected Coverage")
            axes[2, 0].set_ylabel("Actual Coverage")
            axes[2, 0].set_title("Model Calibration")
            axes[2, 0].legend()
            axes[2, 0].grid(True, alpha=0.3)

        # 4. Residual Analysis
        if "residuals" in self.validation_results:
            residuals = self.validation_results["residuals"]["standardized_residuals"]
            fitted_values = self.validation_results["residuals"]["fitted_values"]

            # Residuals vs Fitted
            axes[2, 1].scatter(fitted_values, residuals, alpha=0.6, s=20)
            axes[2, 1].axhline(y=0, color="red", linestyle="--", alpha=0.5)
            axes[2, 1].set_xlabel("Fitted Log Prices")
            axes[2, 1].set_ylabel("Standardized Residuals")
            axes[2, 1].set_title("Residuals vs Fitted")

            # Q-Q plot for residuals
            stats.probplot(residuals, dist="norm", plot=axes[2, 2])
            axes[2, 2].set_title("Q-Q Plot: Residuals")

        plt.tight_layout()
        plt.savefig(
            "/home/dennisjcarroll/Desktop/Bayesian Profolio piece/validation_dashboard.png",
            dpi=300,
            bbox_inches="tight",
        )
        print("Validation dashboard saved as 'validation_dashboard.png'")

        plt.show()

    def generate_validation_report(self):
        """Generate comprehensive validation report."""

        report = "=== MODEL VALIDATION REPORT ===\n\n"

        # Posterior Predictive Checks
        if "posterior_predictive" in self.validation_results:
            report += "1. POSTERIOR PREDICTIVE CHECKS\n"
            report += "-" * 35 + "\n"

            p_values = self.validation_results["posterior_predictive"][
                "test_statistics"
            ]["p_values"]

            for stat, p_val in p_values.items():
                status = "PASS" if p_val > 0.05 else "FAIL"
                report += f"{stat.upper():15}: p-value = {p_val:.4f} [{status}]\n"

            failed_tests = sum(1 for p in p_values.values() if p <= 0.05)
            report += f"\nSummary: {len(p_values) - failed_tests}/{len(p_values)} tests passed\n\n"

        # Cross-Validation Results
        if "cross_validation" in self.validation_results:
            report += "2. CROSS-VALIDATION PERFORMANCE\n"
            report += "-" * 35 + "\n"

            summary = self.validation_results["cross_validation"]["summary"]

            report += (
                f"RMSE:        {summary['mean_rmse']:.2f} ± {summary['std_rmse']:.2f}\n"
            )
            report += (
                f"MAE:         {summary['mean_mae']:.2f} ± {summary['std_mae']:.2f}\n"
            )
            report += f"MAPE:        {summary['mean_mape']:.1f}% ± {summary['std_mape']:.1f}%\n"
            report += (
                f"R²:          {summary['mean_r2']:.3f} ± {summary['std_r2']:.3f}\n\n"
            )

        # Model Calibration
        if "calibration" in self.validation_results:
            report += "3. MODEL CALIBRATION\n"
            report += "-" * 35 + "\n"

            calib_results = self.validation_results["calibration"][
                "by_confidence_level"
            ]
            overall_score = self.validation_results["calibration"]["overall_score"]

            for confidence, results in calib_results.items():
                status = (
                    "WELL CALIBRATED" if results["well_calibrated"] else "MISCALIBRATED"
                )
                report += f"{int(confidence*100)}% CI: Expected={confidence:.2f}, Actual={results['actual_coverage']:.3f} [{status}]\n"

            report += f"\nOverall Calibration Score: {overall_score:.3f}/1.0\n\n"

        # Residual Analysis
        if "residuals" in self.validation_results:
            report += "4. RESIDUAL ANALYSIS\n"
            report += "-" * 35 + "\n"

            residual_stats = self.validation_results["residuals"]["overall_stats"]

            report += f"Mean Residual:     {residual_stats['mean_residual']:.6f}\n"
            report += f"Residual Std:      {residual_stats['std_residual']:.4f}\n"
            report += f"Jarque-Bera p:     {residual_stats['jarque_bera_pvalue']:.4f}\n"
            report += f"Durbin-Watson:     {residual_stats['durbin_watson']:.4f}\n"

            # Normality test
            jb_status = (
                "NORMAL"
                if residual_stats["jarque_bera_pvalue"] > 0.05
                else "NON-NORMAL"
            )
            report += f"Residual Normality: {jb_status}\n\n"

        return report


def main():
    """Main execution function for validation framework."""

    print("=== MODEL VALIDATION FRAMEWORK ===\n")

    # Initialize validation framework
    validator = ValidationFramework(
        "/home/dennisjcarroll/Desktop/Bayesian Profolio piece/listings.csv"
    )

    # 1. Posterior Predictive Checks
    print("1. Running posterior predictive checks...")
    ppc_results = validator.posterior_predictive_checks(n_samples=500)

    # 2. Cross-Validation
    print("\n2. Running cross-validation across neighborhoods...")
    cv_results = validator.cross_validate_neighborhoods(n_folds=3)  # Reduced for speed

    # 3. Model Calibration
    print("\n3. Monitoring model calibration...")
    calibration_results = validator.monitor_model_calibration()

    # 4. Residual Analysis
    print("\n4. Conducting residual analysis...")
    residual_results = validator.residual_analysis()

    # 5. Create Dashboard
    print("\n5. Creating validation dashboard...")
    validator.create_validation_dashboard()

    # 6. Generate Report
    print("\n6. Generating validation report...")
    report = validator.generate_validation_report()
    print("\n" + report)

    # Save report to file
    with open(
        "/home/dennisjcarroll/Desktop/Bayesian Profolio piece/validation_report.txt",
        "w",
    ) as f:
        f.write(report)
    print("Validation report saved to 'validation_report.txt'")

    return validator


if __name__ == "__main__":
    validation_framework = main()

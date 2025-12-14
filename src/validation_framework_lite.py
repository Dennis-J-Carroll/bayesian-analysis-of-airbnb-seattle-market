"""
Lite Validation Framework for Hierarchical Bayesian Price Model
- Focused on key validation metrics
- Optimized for performance
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from hierarchical_bayesian_model import HierarchicalBayesianPriceModel
import warnings

warnings.filterwarnings("ignore")


class ValidationFrameworkLite:
    def __init__(self, hierarchical_model):
        """Initialize with fitted hierarchical model."""
        self.hierarchical_model = hierarchical_model
        self.validation_results = {}

    def posterior_predictive_checks(self, n_samples=200):
        """Streamlined posterior predictive checks."""

        data = self.hierarchical_model.data
        observed_log_prices = np.log(data["price_clean"].values)
        accommodates = data["accommodates"].values
        neighborhood_idx = data["neighborhood_idx"].values

        # Extract posterior samples (use fewer samples for speed)
        alpha_samples = self.hierarchical_model.trace.posterior["alpha"].values.reshape(
            -1, self.hierarchical_model.n_neighborhoods
        )[:n_samples]
        beta_samples = self.hierarchical_model.trace.posterior["beta"].values.reshape(
            -1, self.hierarchical_model.n_neighborhoods
        )[:n_samples]
        sigma_samples = self.hierarchical_model.trace.posterior[
            "sigma"
        ].values.flatten()[:n_samples]

        # Generate posterior predictive samples
        posterior_predictions = []

        for i in range(n_samples):
            predicted_mean = (
                alpha_samples[i][neighborhood_idx]
                + beta_samples[i][neighborhood_idx] * accommodates
            )
            predicted_log_prices = np.random.normal(predicted_mean, sigma_samples[i])
            posterior_predictions.append(predicted_log_prices)

        posterior_predictions = np.array(posterior_predictions)

        # Key test statistics
        observed_stats = {
            "mean": np.mean(observed_log_prices),
            "std": np.std(observed_log_prices),
            "min": np.min(observed_log_prices),
            "max": np.max(observed_log_prices),
            "skewness": stats.skew(observed_log_prices),
        }

        predicted_stats = {
            "mean": [np.mean(pred) for pred in posterior_predictions],
            "std": [np.std(pred) for pred in posterior_predictions],
            "min": [np.min(pred) for pred in posterior_predictions],
            "max": [np.max(pred) for pred in posterior_predictions],
            "skewness": [stats.skew(pred) for pred in posterior_predictions],
        }

        # Calculate p-values
        p_values = {}
        for stat in observed_stats.keys():
            if stat == "min":
                p_values[stat] = np.mean(
                    np.array(predicted_stats[stat]) <= observed_stats[stat]
                )
            elif stat == "max":
                p_values[stat] = np.mean(
                    np.array(predicted_stats[stat]) >= observed_stats[stat]
                )
            else:
                obs_val = observed_stats[stat]
                pred_vals = np.array(predicted_stats[stat])
                p_values[stat] = 2 * min(
                    np.mean(pred_vals <= obs_val), np.mean(pred_vals >= obs_val)
                )

        self.validation_results["ppc"] = {
            "observed": observed_stats,
            "predicted": predicted_stats,
            "p_values": p_values,
            "posterior_predictions": posterior_predictions,
            "observed_log_prices": observed_log_prices,
        }

        return p_values

    def simple_holdout_validation(self, test_size=0.2):
        """Simple holdout validation instead of full cross-validation."""

        data = self.hierarchical_model.data
        n = len(data)

        # Random split
        np.random.seed(42)
        test_indices = np.random.choice(n, size=int(n * test_size), replace=False)
        train_indices = np.setdiff1d(np.arange(n), test_indices)

        test_data = data.iloc[test_indices]

        # Get posterior means for prediction
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

        # Predict on test set
        test_neighborhood_idx = test_data["neighborhood_idx"].values
        predicted_log_prices = (
            alpha_mean[test_neighborhood_idx]
            + beta_mean[test_neighborhood_idx] * test_data["accommodates"]
        )
        predicted_prices = np.exp(predicted_log_prices)

        actual_prices = test_data["price_clean"].values
        actual_log_prices = np.log(actual_prices)

        # Calculate metrics
        from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

        metrics = {
            "rmse": np.sqrt(mean_squared_error(actual_prices, predicted_prices)),
            "mae": mean_absolute_error(actual_prices, predicted_prices),
            "mape": np.mean(np.abs((actual_prices - predicted_prices) / actual_prices))
            * 100,
            "r2": r2_score(actual_prices, predicted_prices),
            "log_rmse": np.sqrt(
                mean_squared_error(actual_log_prices, predicted_log_prices)
            ),
        }

        self.validation_results["holdout"] = {
            "metrics": metrics,
            "predicted_prices": predicted_prices,
            "actual_prices": actual_prices,
            "test_size": len(test_data),
        }

        return metrics

    def calibration_check(self):
        """Quick calibration check using prediction intervals."""

        if "ppc" not in self.validation_results:
            self.posterior_predictive_checks()

        observed = self.validation_results["ppc"]["observed_log_prices"]
        predictions = self.validation_results["ppc"]["posterior_predictions"]

        confidence_levels = [0.5, 0.8, 0.9, 0.95]
        calibration_results = {}

        for confidence_level in confidence_levels:
            alpha = 1 - confidence_level
            lower_percentile = (alpha / 2) * 100
            upper_percentile = (1 - alpha / 2) * 100

            pred_lower = np.percentile(predictions, lower_percentile, axis=0)
            pred_upper = np.percentile(predictions, upper_percentile, axis=0)

            coverage = np.mean((observed >= pred_lower) & (observed <= pred_upper))

            calibration_results[confidence_level] = {
                "expected": confidence_level,
                "actual": coverage,
                "well_calibrated": abs(coverage - confidence_level) < 0.05,
            }

        self.validation_results["calibration"] = calibration_results
        return calibration_results

    def residual_analysis(self):
        """Basic residual analysis."""

        data = self.hierarchical_model.data
        observed_log_prices = np.log(data["price_clean"].values)
        accommodates = data["accommodates"].values
        neighborhood_idx = data["neighborhood_idx"].values

        # Get fitted values
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

        fitted_log_prices = (
            alpha_mean[neighborhood_idx] + beta_mean[neighborhood_idx] * accommodates
        )
        residuals = observed_log_prices - fitted_log_prices

        # Basic statistics
        residual_stats = {
            "mean": np.mean(residuals),
            "std": np.std(residuals),
            "jarque_bera_pvalue": stats.jarque_bera(residuals)[1],
            "shapiro_pvalue": stats.shapiro(residuals[: min(5000, len(residuals))])[
                1
            ],  # Shapiro limited to 5000
        }

        self.validation_results["residuals"] = {
            "residuals": residuals,
            "fitted": fitted_log_prices,
            "stats": residual_stats,
        }

        return residual_stats

    def create_validation_plots(self):
        """Create essential validation plots."""

        fig, axes = plt.subplots(2, 3, figsize=(18, 12))

        # 1. Posterior Predictive Check - Mean
        if "ppc" in self.validation_results:
            ppc = self.validation_results["ppc"]

            pred_means = ppc["predicted"]["mean"]
            obs_mean = ppc["observed"]["mean"]
            p_val = ppc["p_values"]["mean"]

            axes[0, 0].hist(
                pred_means, bins=30, alpha=0.7, density=True, label="Predicted"
            )
            axes[0, 0].axvline(
                obs_mean,
                color="red",
                linestyle="--",
                linewidth=2,
                label=f"Observed (p={p_val:.3f})",
            )
            axes[0, 0].set_title("PPC: Mean Log Price")
            axes[0, 0].legend()

            # 2. PPC - Standard Deviation
            pred_stds = ppc["predicted"]["std"]
            obs_std = ppc["observed"]["std"]
            p_val_std = ppc["p_values"]["std"]

            axes[0, 1].hist(
                pred_stds, bins=30, alpha=0.7, density=True, label="Predicted"
            )
            axes[0, 1].axvline(
                obs_std,
                color="red",
                linestyle="--",
                linewidth=2,
                label=f"Observed (p={p_val_std:.3f})",
            )
            axes[0, 1].set_title("PPC: Std Dev Log Price")
            axes[0, 1].legend()

        # 3. Holdout Validation
        if "holdout" in self.validation_results:
            holdout = self.validation_results["holdout"]

            axes[0, 2].scatter(
                holdout["actual_prices"], holdout["predicted_prices"], alpha=0.6
            )
            min_price = min(
                holdout["actual_prices"].min(), holdout["predicted_prices"].min()
            )
            max_price = max(
                holdout["actual_prices"].max(), holdout["predicted_prices"].max()
            )
            axes[0, 2].plot([min_price, max_price], [min_price, max_price], "r--")
            axes[0, 2].set_xlabel("Actual Prices ($)")
            axes[0, 2].set_ylabel("Predicted Prices ($)")
            axes[0, 2].set_title(
                f'Holdout Validation (R²={holdout["metrics"]["r2"]:.3f})'
            )

        # 4. Model Calibration
        if "calibration" in self.validation_results:
            calib = self.validation_results["calibration"]

            confidence_levels = list(calib.keys())
            expected = confidence_levels
            actual = [calib[cl]["actual"] for cl in confidence_levels]

            axes[1, 0].plot(expected, expected, "k--", label="Perfect Calibration")
            axes[1, 0].plot(expected, actual, "ro-", label="Actual")
            axes[1, 0].set_xlabel("Expected Coverage")
            axes[1, 0].set_ylabel("Actual Coverage")
            axes[1, 0].set_title("Model Calibration")
            axes[1, 0].legend()
            axes[1, 0].grid(True, alpha=0.3)

        # 5. Residuals vs Fitted
        if "residuals" in self.validation_results:
            residuals_data = self.validation_results["residuals"]

            axes[1, 1].scatter(
                residuals_data["fitted"], residuals_data["residuals"], alpha=0.6, s=20
            )
            axes[1, 1].axhline(y=0, color="red", linestyle="--", alpha=0.5)
            axes[1, 1].set_xlabel("Fitted Log Prices")
            axes[1, 1].set_ylabel("Residuals")
            axes[1, 1].set_title("Residuals vs Fitted")

            # 6. Q-Q Plot
            stats.probplot(residuals_data["residuals"], dist="norm", plot=axes[1, 2])
            axes[1, 2].set_title("Q-Q Plot: Residuals")

        plt.tight_layout()
        plt.savefig(
            "/home/dennisjcarroll/Desktop/Bayesian Profolio piece/validation_results.png",
            dpi=300,
            bbox_inches="tight",
        )
        print("Validation plots saved as 'validation_results.png'")

        plt.show()

    def validation_summary(self):
        """Generate validation summary report."""

        report = "=== MODEL VALIDATION SUMMARY ===\n\n"

        # Posterior Predictive Checks
        if "ppc" in self.validation_results:
            report += "1. POSTERIOR PREDICTIVE CHECKS\n"
            report += "-" * 35 + "\n"

            p_values = self.validation_results["ppc"]["p_values"]

            for stat, p_val in p_values.items():
                status = "PASS" if p_val > 0.05 else "FAIL"
                report += f"{stat.upper():12}: p-value = {p_val:.4f} [{status}]\n"

            failed_tests = sum(1 for p in p_values.values() if p <= 0.05)
            report += f"\nSummary: {len(p_values) - failed_tests}/{len(p_values)} tests passed\n\n"

        # Holdout Validation
        if "holdout" in self.validation_results:
            report += "2. HOLDOUT VALIDATION\n"
            report += "-" * 35 + "\n"

            metrics = self.validation_results["holdout"]["metrics"]

            report += f"RMSE:        ${metrics['rmse']:.2f}\n"
            report += f"MAE:         ${metrics['mae']:.2f}\n"
            report += f"MAPE:        {metrics['mape']:.1f}%\n"
            report += f"R²:          {metrics['r2']:.3f}\n"
            report += f"Log RMSE:    {metrics['log_rmse']:.4f}\n\n"

        # Calibration
        if "calibration" in self.validation_results:
            report += "3. MODEL CALIBRATION\n"
            report += "-" * 35 + "\n"

            calib = self.validation_results["calibration"]

            for confidence, results in calib.items():
                status = (
                    "WELL CALIBRATED" if results["well_calibrated"] else "MISCALIBRATED"
                )
                report += f"{int(confidence*100)}% CI: Expected={confidence:.2f}, Actual={results['actual']:.3f} [{status}]\n"

            well_calibrated_count = sum(
                1 for r in calib.values() if r["well_calibrated"]
            )
            report += f"\nCalibration Score: {well_calibrated_count}/{len(calib)} intervals well calibrated\n\n"

        # Residuals
        if "residuals" in self.validation_results:
            report += "4. RESIDUAL ANALYSIS\n"
            report += "-" * 35 + "\n"

            stats_data = self.validation_results["residuals"]["stats"]

            report += f"Mean Residual:     {stats_data['mean']:.6f}\n"
            report += f"Residual Std:      {stats_data['std']:.4f}\n"
            report += f"Jarque-Bera p:     {stats_data['jarque_bera_pvalue']:.4f}\n"
            report += f"Shapiro-Wilk p:    {stats_data['shapiro_pvalue']:.4f}\n"

            normality_status = (
                "NORMAL" if stats_data["jarque_bera_pvalue"] > 0.05 else "NON-NORMAL"
            )
            report += f"Residual Normality: {normality_status}\n\n"

        return report


def main():
    """Main execution for lite validation framework."""

    print("=== LITE VALIDATION FRAMEWORK ===\n")

    # Load and fit model
    print("Loading and fitting hierarchical model...")
    model = HierarchicalBayesianPriceModel(
        "/home/dennisjcarroll/Desktop/Bayesian Profolio piece/listings.csv"
    )
    model.load_and_clean_data()
    model.build_hierarchical_model()
    model.fit_model(samples=1000, tune=500, chains=2)

    # Initialize validation
    validator = ValidationFrameworkLite(model)

    # Run validation checks
    print("1. Running posterior predictive checks...")
    ppc_results = validator.posterior_predictive_checks(n_samples=100)

    print("2. Running holdout validation...")
    holdout_results = validator.simple_holdout_validation()

    print("3. Checking model calibration...")
    calibration_results = validator.calibration_check()

    print("4. Analyzing residuals...")
    residual_results = validator.residual_analysis()

    print("5. Creating validation plots...")
    validator.create_validation_plots()

    print("6. Generating summary report...")
    report = validator.validation_summary()
    print("\n" + report)

    # Save report
    with open(
        "/home/dennisjcarroll/Desktop/Bayesian Profolio piece/validation_summary.txt",
        "w",
    ) as f:
        f.write(report)
    print("Validation summary saved to 'validation_summary.txt'")

    return validator


if __name__ == "__main__":
    validation_framework = main()

"""
Hierarchical Bayesian Model for Airbnb Price Analysis
Features:
- Log-normal likelihood for price modeling
- Varying intercepts by neighborhood
- Varying slopes for accommodates by neighborhood
"""

import pandas as pd
import numpy as np
import pymc as pm
import arviz as az
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import lognorm
import warnings

warnings.filterwarnings("ignore")


class HierarchicalBayesianPriceModel:
    def __init__(self, listings_path, neighbourhoods_path=None):
        """Initialize the model with Airbnb listings data."""
        self.listings_path = listings_path
        self.neighbourhoods_path = neighbourhoods_path
        self.data = None
        self.model = None
        self.trace = None
        self.neighborhoods = None
        self.n_neighborhoods = None
        self.neighborhood_lookup = None
        self.scalers = None  # For feature standardization

    def _add_property_type_feature(self, df):
        """Add property type as categorical feature"""
        property_type_map = {
            "Private room": 0,
            "Entire home/apt": 1,
            "Shared room": 2,
            "Hotel room": 3,
        }
        df["property_type_idx"] = df["room_type"].map(property_type_map)
        df["property_type_idx"].fillna(1, inplace=True)  # Default to entire home
        return df

    def _calculate_amenity_score(self, df):
        """Calculate composite amenity score from key features"""

        # Parse amenities (handle different formats)
        def parse_amenities(amenity_str):
            if pd.isna(amenity_str):
                return []
            # Remove brackets and quotes, split by comma
            amenity_str = (
                str(amenity_str)
                .replace("[", "")
                .replace("]", "")
                .replace('"', "")
                .replace("'", "")
            )
            return [a.strip().lower() for a in amenity_str.split(",")]

        df["amenity_list"] = df["amenities"].apply(parse_amenities)

        # High-value amenities with impact weights
        amenity_weights = {
            "wifi": 1.0,
            "kitchen": 2.0,
            "free parking": 2.0,
            "parking": 1.5,
            "air conditioning": 1.5,
            "washer": 1.5,
            "dryer": 1.5,
            "hot tub": 3.0,
            "pool": 3.0,
            "gym": 2.0,
            "elevator": 1.0,
            "dishwasher": 1.0,
            "heating": 1.0,
            "tv": 0.5,
        }

        def calculate_score(amenity_list):
            score = 0
            for amenity, weight in amenity_weights.items():
                if any(amenity in a for a in amenity_list):
                    score += weight
            return score

        return df["amenity_list"].apply(calculate_score)

    def _standardize_features(self, df):
        """Standardize continuous features for better MCMC convergence"""
        from sklearn.preprocessing import StandardScaler

        # Standardize accommodates
        scaler_accommodates = StandardScaler()
        df["accommodates_std"] = scaler_accommodates.fit_transform(df[["accommodates"]])

        # Standardize amenity score
        scaler_amenities = StandardScaler()
        df["amenity_score_std"] = scaler_amenities.fit_transform(df[["amenity_score"]])

        # Store scalers for inverse transform during prediction
        self.scalers = {
            "accommodates": scaler_accommodates,
            "amenity_score": scaler_amenities,
        }

        return df

    def load_and_clean_data(self):
        """Enhanced data loading with new features"""
        # Load data
        df = pd.read_csv(self.listings_path)

        # Clean price column (remove $ and convert to float)
        df["price_clean"] = (
            df["price"].str.replace("$", "").str.replace(",", "").astype(float)
        )

        # Remove rows with missing price or accommodates
        df = df.dropna(subset=["price_clean", "accommodates", "neighbourhood_cleansed"])

        # Filter out extreme outliers (prices < $10 or > $1000)
        df = df[(df["price_clean"] >= 10) & (df["price_clean"] <= 1000)]

        # Create neighborhood index for modeling
        neighborhoods = df["neighbourhood_cleansed"].unique()
        neighborhood_lookup = {name: idx for idx, name in enumerate(neighborhoods)}
        df["neighborhood_idx"] = df["neighbourhood_cleansed"].map(neighborhood_lookup)

        # Store log_price for easier access
        df["log_price"] = np.log(df["price_clean"])

        # NEW: Add property type
        df = self._add_property_type_feature(df)

        # NEW: Add amenity score (handle missing amenities column gracefully)
        if "amenities" in df.columns:
            df["amenity_score"] = self._calculate_amenity_score(df)
        else:
            print("Warning: 'amenities' column not found. Setting amenity_score to 0.")
            df["amenity_score"] = 0

        # Ensure number_of_reviews exists
        if "number_of_reviews" not in df.columns:
            print("Warning: 'number_of_reviews' column not found. Setting to 0.")
            df["number_of_reviews"] = 0

        # NEW: Standardize features
        df = self._standardize_features(df)

        self.data = df
        self.neighborhoods = neighborhoods
        self.n_neighborhoods = len(neighborhoods)
        self.neighborhood_lookup = neighborhood_lookup

        print(
            f"Data loaded: {len(df)} listings across {self.n_neighborhoods} neighborhoods"
        )
        print(
            f"Price range: ${df['price_clean'].min():.2f} - ${df['price_clean'].max():.2f}"
        )
        print(
            f"Accommodates range: {df['accommodates'].min()} - {df['accommodates'].max()}"
        )
        print(
            f"Amenity score range: {df['amenity_score'].min():.2f} - {df['amenity_score'].max():.2f}"
        )

        return self

    def build_hierarchical_model(self):
        """Build the hierarchical Bayesian model with log-normal likelihood."""

        # Extract modeling data
        log_price = np.log(self.data["price_clean"].values)
        accommodates = self.data["accommodates"].values
        neighborhood_idx = self.data["neighborhood_idx"].values

        with pm.Model() as model:
            # Hyperpriors for varying intercepts
            mu_alpha = pm.Normal(
                "mu_alpha", mu=4.5, sigma=1
            )  # Grand mean for log price
            sigma_alpha = pm.HalfNormal(
                "sigma_alpha", sigma=0.5
            )  # Variation across neighborhoods

            # Hyperpriors for varying slopes
            mu_beta = pm.Normal(
                "mu_beta", mu=0.2, sigma=0.1
            )  # Grand mean for accommodates effect
            sigma_beta = pm.HalfNormal(
                "sigma_beta", sigma=0.1
            )  # Variation across neighborhoods

            # Varying intercepts by neighborhood
            alpha = pm.Normal(
                "alpha", mu=mu_alpha, sigma=sigma_alpha, shape=self.n_neighborhoods
            )

            # Varying slopes for accommodates by neighborhood
            beta = pm.Normal(
                "beta", mu=mu_beta, sigma=sigma_beta, shape=self.n_neighborhoods
            )

            # Linear predictor for log price
            mu = alpha[neighborhood_idx] + beta[neighborhood_idx] * accommodates

            # Log-normal likelihood (equivalent to normal on log scale)
            sigma = pm.HalfNormal("sigma", sigma=0.5)  # Residual standard deviation

            # Observed log prices
            log_price_obs = pm.Normal(
                "log_price_obs", mu=mu, sigma=sigma, observed=log_price
            )

        self.model = model
        return model

    def fit_model(self, samples=2000, tune=1000, chains=4):
        """Fit the hierarchical Bayesian model using MCMC."""

        with self.model:
            # Sample from posterior
            self.trace = pm.sample(
                draws=samples,
                tune=tune,
                chains=chains,
                return_inferencedata=True,
                random_seed=42,
            )

            # Add posterior predictive samples
            self.trace.extend(pm.sample_posterior_predictive(self.trace))

        print(f"Model fitted with {samples} samples across {chains} chains")
        return self.trace

    def build_enhanced_hierarchical_model(self):
        """
        Enhanced hierarchical model with property type and amenities

        log(price) ~ Normal(μ, σ)
        μ = α[neighborhood, property_type] + β_accommodates[neighborhood] × accommodates
            + β_amenities × amenity_score + β_reviews × log(1 + reviews)
        """

        # Prepare indices
        neighborhood_idx = self.data["neighborhood_idx"].values
        property_type_idx = self.data["property_type_idx"].values.astype(int)
        n_neighborhoods = self.n_neighborhoods
        n_property_types = 4

        # Prepare predictors
        accommodates = self.data["accommodates_std"].values
        amenity_score = self.data["amenity_score_std"].values
        log_reviews = np.log1p(self.data["number_of_reviews"].fillna(0).values)

        # Target
        log_price = np.log(self.data["price_clean"].values)

        with pm.Model() as hierarchical_model:

            # === Hyperpriors ===
            μ_α = pm.Normal("μ_α", mu=4.5, sigma=1.0)
            σ_α_neighborhood = pm.HalfNormal("σ_α_neighborhood", sigma=0.3)
            σ_α_property = pm.HalfNormal("σ_α_property", sigma=0.5)

            μ_β_accommodates = pm.Normal("μ_β_accommodates", mu=0.2, sigma=0.1)
            σ_β_accommodates = pm.HalfNormal("σ_β_accommodates", sigma=0.1)

            # === Varying Effects ===
            α_neighborhood = pm.Normal(
                "α_neighborhood", mu=0, sigma=σ_α_neighborhood, shape=n_neighborhoods
            )

            α_property = pm.Normal(
                "α_property", mu=0, sigma=σ_α_property, shape=n_property_types
            )

            β_accommodates = pm.Normal(
                "β_accommodates",
                mu=μ_β_accommodates,
                sigma=σ_β_accommodates,
                shape=n_neighborhoods,
            )

            # === Global Coefficients ===
            β_amenities = pm.Normal("β_amenities", mu=0.15, sigma=0.05)
            β_reviews = pm.Normal("β_reviews", mu=0.05, sigma=0.02)

            # === Likelihood ===
            μ = (
                μ_α
                + α_neighborhood[neighborhood_idx]
                + α_property[property_type_idx]
                + β_accommodates[neighborhood_idx] * accommodates
                + β_amenities * amenity_score
                + β_reviews * log_reviews
            )

            σ = pm.HalfNormal("σ", sigma=0.5)

            log_price_obs = pm.Normal(
                "log_price_obs", mu=μ, sigma=σ, observed=log_price
            )

            self.model = hierarchical_model
            self.property_type_idx = property_type_idx

        return self

    def fit_model_with_diagnostics(self, draws=2000, tune=1000, chains=4):
        """Fit model with comprehensive diagnostics"""

        print("\n" + "=" * 60)
        print("FITTING ENHANCED BAYESIAN MODEL")
        print("=" * 60)

        with self.model:
            print("\n⏳ Sampling (this may take 10-15 minutes)...")
            self.trace = pm.sample(
                draws=draws,
                tune=tune,
                chains=chains,
                target_accept=0.95,
                return_inferencedata=True,
                random_seed=42,
            )

            print("\n⏳ Generating posterior predictive samples...")
            self.trace.extend(pm.sample_posterior_predictive(self.trace))

        # Diagnostic checks
        print("\n" + "=" * 60)
        print("CONVERGENCE DIAGNOSTICS")
        print("=" * 60)

        r_hat = az.rhat(self.trace)
        max_rhat = float(r_hat.max())
        print(f"Max R-hat: {max_rhat:.4f} {'✓' if max_rhat < 1.01 else '✗ WARNING'}")

        ess = az.ess(self.trace)
        min_ess = float(ess.min())
        print(f"Min ESS: {min_ess:.0f} {'✓' if min_ess > 400 else '✗ WARNING'}")

        divergences = self.trace.sample_stats.diverging.sum().values
        print(f"Divergences: {divergences} {'✓' if divergences == 0 else '✗ WARNING'}")

        print("\n" + "=" * 60)

        return self

    def model_diagnostics(self):
        """Generate model diagnostics and convergence checks."""

        # Print summary statistics
        print("\n=== Model Summary ===")
        print(
            az.summary(
                self.trace,
                var_names=["mu_alpha", "mu_beta", "sigma_alpha", "sigma_beta", "sigma"],
            )
        )

        # Check R-hat values for convergence
        rhat = az.rhat(self.trace)
        rhat_values = rhat.to_array().values
        max_rhat = float(np.nanmax(rhat_values))
        print(f"\nMax R-hat: {max_rhat:.4f}")
        if max_rhat < 1.01:
            print("✓ All chains converged (R-hat < 1.01)")
        else:
            print("⚠ Some parameters may not have converged")

        # Effective sample size
        ess = az.ess(self.trace)
        ess_values = ess.to_array().values
        min_ess = float(np.nanmin(ess_values))
        print(f"Min ESS: {min_ess:.0f}")

        return rhat, ess

    def plot_results(self, save_plots=True):
        """Generate comprehensive plots of model results."""

        fig, axes = plt.subplots(2, 3, figsize=(18, 12))

        # Generate standalone diagnostic plots first (not part of main subplot)
        print("Generating diagnostic plots...")
        try:
            trace_fig = az.plot_trace(
                self.trace, var_names=["mu_alpha", "mu_beta", "sigma"]
            )
            if hasattr(trace_fig, "savefig"):
                trace_fig.savefig(
                    "/home/dennisjcarroll/Desktop/Bayesian Profolio piece/trace_plots.png",
                    dpi=150,
                    bbox_inches="tight",
                )
            plt.close("all")
        except:
            print("Trace plots generation skipped")

        # Create new plots on the manual subplots
        # Plot varying intercepts by neighborhood
        alpha_samples = self.trace.posterior["alpha"].values.reshape(
            -1, self.n_neighborhoods
        )
        alpha_mean = alpha_samples.mean(axis=0)
        alpha_ci = np.percentile(alpha_samples, [2.5, 97.5], axis=0)

        neighborhood_order = np.argsort(alpha_mean)
        axes[0, 0].errorbar(
            range(len(alpha_mean)),
            alpha_mean[neighborhood_order],
            yerr=[
                alpha_mean[neighborhood_order] - alpha_ci[0][neighborhood_order],
                alpha_ci[1][neighborhood_order] - alpha_mean[neighborhood_order],
            ],
            fmt="o",
            capsize=3,
        )
        axes[0, 0].set_title("Varying Intercepts by Neighborhood")
        axes[0, 0].set_xlabel("Neighborhood (ordered by intercept)")
        axes[0, 0].set_ylabel("Log Price Intercept")

        # Plot varying slopes by neighborhood
        beta_samples = self.trace.posterior["beta"].values.reshape(
            -1, self.n_neighborhoods
        )
        beta_mean = beta_samples.mean(axis=0)
        beta_ci = np.percentile(beta_samples, [2.5, 97.5], axis=0)

        axes[0, 1].errorbar(
            range(len(beta_mean)),
            beta_mean,
            yerr=[beta_mean - beta_ci[0], beta_ci[1] - beta_mean],
            fmt="s",
            capsize=3,
            color="red",
        )
        axes[0, 1].set_title("Varying Slopes for Accommodates")
        axes[0, 1].set_xlabel("Neighborhood")
        axes[0, 1].set_ylabel("Accommodates Effect")
        axes[0, 1].axhline(y=0, color="black", linestyle="--", alpha=0.5)

        # Plot posterior distributions
        mu_alpha_samples = self.trace.posterior["mu_alpha"].values.flatten()
        mu_beta_samples = self.trace.posterior["mu_beta"].values.flatten()
        sigma_samples = self.trace.posterior["sigma"].values.flatten()

        axes[0, 2].hist(mu_alpha_samples, bins=30, alpha=0.7, density=True)
        axes[0, 2].set_title("Posterior: Grand Mean Intercept")
        axes[0, 2].set_xlabel("mu_alpha")

        axes[1, 0].hist(mu_beta_samples, bins=30, alpha=0.7, density=True, color="red")
        axes[1, 0].set_title("Posterior: Grand Mean Slope")
        axes[1, 0].set_xlabel("mu_beta")

        axes[1, 1].hist(sigma_samples, bins=30, alpha=0.7, density=True, color="green")
        axes[1, 1].set_title("Posterior: Residual SD")
        axes[1, 1].set_xlabel("sigma")

        # Predicted vs observed prices
        observed_log_price = np.log(self.data["price_clean"].values)
        accommodates = self.data["accommodates"].values
        neighborhood_idx = self.data["neighborhood_idx"].values

        # Get posterior means for prediction
        alpha_mean_all = alpha_samples.mean(axis=0)
        beta_mean_all = beta_samples.mean(axis=0)

        predicted_log_price = (
            alpha_mean_all[neighborhood_idx]
            + beta_mean_all[neighborhood_idx] * accommodates
        )

        axes[1, 2].scatter(predicted_log_price, observed_log_price, alpha=0.5)
        axes[1, 2].plot(
            [observed_log_price.min(), observed_log_price.max()],
            [observed_log_price.min(), observed_log_price.max()],
            "r--",
        )
        axes[1, 2].set_title("Predicted vs Observed Log Price")
        axes[1, 2].set_xlabel("Predicted Log Price")
        axes[1, 2].set_ylabel("Observed Log Price")

        plt.tight_layout()

        if save_plots:
            plt.savefig(
                "/home/dennisjcarroll/Desktop/Bayesian Profolio piece/hierarchical_model_results.png",
                dpi=300,
                bbox_inches="tight",
            )
            print("Plot saved as 'hierarchical_model_results.png'")

        plt.show()

    def predict_prices(self, accommodates_values, neighborhood_name):
        """Predict prices for given accommodates values in a specific neighborhood."""

        if neighborhood_name not in self.data["neighbourhood_cleansed"].values:
            print(f"Neighborhood '{neighborhood_name}' not found in data")
            return None

        neighborhood_idx = self.data[
            self.data["neighbourhood_cleansed"] == neighborhood_name
        ]["neighborhood_idx"].iloc[0]

        # Extract posterior samples
        alpha_samples = self.trace.posterior["alpha"].values.reshape(
            -1, self.n_neighborhoods
        )[:, neighborhood_idx]
        beta_samples = self.trace.posterior["beta"].values.reshape(
            -1, self.n_neighborhoods
        )[:, neighborhood_idx]
        sigma_samples = self.trace.posterior["sigma"].values.flatten()

        predictions = {}

        for acc in accommodates_values:
            # Predict log price
            log_price_pred = alpha_samples + beta_samples * acc

            # Convert to price scale (exp of log price)
            price_pred = np.exp(log_price_pred)

            # Add uncertainty from residual variance
            price_with_uncertainty = np.random.lognormal(log_price_pred, sigma_samples)

            predictions[acc] = {
                "mean": price_pred.mean(),
                "median": np.median(price_pred),
                "ci_95": np.percentile(price_pred, [2.5, 97.5]),
                "with_uncertainty_ci": np.percentile(
                    price_with_uncertainty, [2.5, 97.5]
                ),
            }

        return predictions

    def compare_neighborhoods(self, accommodates=4):
        """Compare predicted prices across neighborhoods for a given accommodates value."""

        # Extract posterior samples
        alpha_samples = self.trace.posterior["alpha"].values.reshape(
            -1, self.n_neighborhoods
        )
        beta_samples = self.trace.posterior["beta"].values.reshape(
            -1, self.n_neighborhoods
        )

        # Predict for each neighborhood
        log_prices = alpha_samples + beta_samples * accommodates
        prices = np.exp(log_prices)

        # Calculate summary statistics
        neighborhood_summary = []
        for i, neighborhood in enumerate(self.neighborhoods):
            neighborhood_summary.append(
                {
                    "neighborhood": neighborhood,
                    "mean_price": prices[:, i].mean(),
                    "median_price": np.median(prices[:, i]),
                    "ci_95_lower": np.percentile(prices[:, i], 2.5),
                    "ci_95_upper": np.percentile(prices[:, i], 97.5),
                }
            )

        # Convert to DataFrame and sort by mean price
        summary_df = pd.DataFrame(neighborhood_summary)
        summary_df = summary_df.sort_values("mean_price", ascending=False)

        return summary_df


def main():
    """Main execution function."""

    # Initialize model
    model = HierarchicalBayesianPriceModel(
        "/home/dennisjcarroll/Desktop/Bayesian Profolio piece/listings.csv"
    )

    # Load and clean data
    data = model.load_and_clean_data()

    # Build model
    bayesian_model = model.build_hierarchical_model()

    # Fit model
    trace = model.fit_model(
        samples=1000, tune=500, chains=2
    )  # Reduced for faster execution

    # Model diagnostics
    model.model_diagnostics()

    # Generate plots
    model.plot_results()

    # Example predictions
    print("\n=== Example Predictions ===")
    predictions = model.predict_prices([2, 4, 6], "Capitol Hill")
    if predictions:
        for acc, pred in predictions.items():
            print(
                f"Accommodates {acc}: ${pred['mean']:.2f} (95% CI: ${pred['ci_95'][0]:.2f}-${pred['ci_95'][1]:.2f})"
            )

    # Neighborhood comparison
    print("\n=== Top 10 Most Expensive Neighborhoods (4 guests) ===")
    comparison = model.compare_neighborhoods(accommodates=4)
    print(
        comparison.head(10)[
            ["neighborhood", "mean_price", "ci_95_lower", "ci_95_upper"]
        ]
    )

    return model


if __name__ == "__main__":
    model = main()

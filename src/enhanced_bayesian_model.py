"""
Enhanced Hierarchical Bayesian Model for Airbnb Price Analysis

Improvements over basic model:
- Multiple predictors (room_type, reviews, availability)
- Robust likelihood (Student-t distribution)
- Configurable parameters
- Better logging and diagnostics
- Cross-validation support
- Posterior predictive checks
"""

import pandas as pd
import numpy as np
import pymc as pm
import arviz as az
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from sklearn.model_selection import KFold
from sklearn.preprocessing import StandardScaler
import yaml
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import warnings

warnings.filterwarnings("ignore")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EnhancedBayesianPriceModel:
    """Enhanced hierarchical Bayesian model for Airbnb pricing with robust features."""

    def __init__(self, config_path: str = "config.yaml"):
        """Initialize model with configuration."""
        self.config = self._load_config(config_path)
        self.data = None
        self.model = None
        self.trace = None
        self.scaler = StandardScaler()

        logger.info("Enhanced Bayesian Price Model initialized")

    def _load_config(self, config_path: str) -> dict:
        """Load configuration from YAML file."""
        if Path(config_path).exists():
            with open(config_path, "r") as f:
                return yaml.safe_load(f)
        else:
            logger.warning(f"Config file {config_path} not found, using defaults")
            return self._default_config()

    def _default_config(self) -> dict:
        """Return default configuration."""
        return {
            "data": {
                "listings": "data/raw/listings.csv",
                "min_price": 10,
                "max_price": 1000,
            },
            "model": {
                "mcmc_samples": 2000,
                "mcmc_tune": 1000,
                "mcmc_chains": 4,
                "random_seed": 42,
                "use_room_type": True,
                "use_reviews": True,
                "use_availability": True,
            },
        }

    def load_and_clean_data(self, data_path: Optional[str] = None) -> pd.DataFrame:
        """Load and preprocess Airbnb data with enhanced features."""
        if data_path is None:
            data_path = self.config["data"]["listings"]

        logger.info(f"Loading data from {data_path}")
        df = pd.read_csv(data_path)

        # Clean price
        df["price_clean"] = (
            df["price"].str.replace("$", "").str.replace(",", "").astype(float)
        )

        # Remove missing values
        required_cols = ["price_clean", "accommodates", "neighbourhood_cleansed"]
        df = df.dropna(subset=required_cols)

        # Filter outliers
        min_price = self.config["data"].get("min_price", 10)
        max_price = self.config["data"].get("max_price", 1000)
        df = df[(df["price_clean"] >= min_price) & (df["price_clean"] <= max_price)]

        # Create neighborhood index
        neighborhoods = sorted(df["neighbourhood_cleansed"].unique())
        neighborhood_lookup = {name: idx for idx, name in enumerate(neighborhoods)}
        df["neighborhood_idx"] = df["neighbourhood_cleansed"].map(neighborhood_lookup)

        # Add room type encoding if enabled
        if self.config["model"].get("use_room_type", True):
            df["is_entire_home"] = (df["room_type"] == "Entire home/apt").astype(int)
            df["is_private_room"] = (df["room_type"] == "Private room").astype(int)
        else:
            df["is_entire_home"] = 0
            df["is_private_room"] = 0

        # Add review features if enabled
        if self.config["model"].get("use_reviews", True):
            df["log_reviews"] = np.log1p(df["number_of_reviews"].fillna(0))
            df["review_score"] = (
                df["review_scores_rating"].fillna(df["review_scores_rating"].median())
                / 100
            )
        else:
            df["log_reviews"] = 0
            df["review_score"] = 0

        # Add availability feature if enabled
        if self.config["model"].get("use_availability", True):
            df["availability_ratio"] = df["availability_365"].fillna(0) / 365
        else:
            df["availability_ratio"] = 0

        # Standardize continuous features
        continuous_features = [
            "accommodates",
            "log_reviews",
            "review_score",
            "availability_ratio",
        ]
        df[continuous_features] = self.scaler.fit_transform(df[continuous_features])

        self.data = df
        self.neighborhoods = neighborhoods
        self.n_neighborhoods = len(neighborhoods)

        logger.info(
            f"Data loaded: {len(df)} listings across {self.n_neighborhoods} neighborhoods"
        )
        logger.info(
            f"Price range: ${df['price_clean'].min():.2f} - ${df['price_clean'].max():.2f}"
        )
        logger.info(f"Features: accommodates, room_type, reviews, availability")

        return df

    def build_enhanced_model(self, use_robust_likelihood: bool = True) -> pm.Model:
        """
        Build enhanced hierarchical model with multiple predictors.

        Args:
            use_robust_likelihood: If True, use Student-t distribution for robustness

        Returns:
            PyMC model object
        """
        logger.info("Building enhanced hierarchical Bayesian model")

        # Extract features
        log_price = np.log(self.data["price_clean"].values)
        accommodates = self.data["accommodates"].values
        neighborhood_idx = self.data["neighborhood_idx"].values
        is_entire_home = self.data["is_entire_home"].values
        is_private_room = self.data["is_private_room"].values
        log_reviews = self.data["log_reviews"].values
        review_score = self.data["review_score"].values
        availability = self.data["availability_ratio"].values

        with pm.Model() as model:
            # =================================================================
            # HIERARCHICAL STRUCTURE: Varying intercepts and slopes
            # =================================================================

            # Grand means
            mu_alpha = pm.Normal("mu_alpha", mu=4.5, sigma=1)
            mu_beta_acc = pm.Normal("mu_beta_acc", mu=0.2, sigma=0.1)

            # Standard deviations across neighborhoods
            sigma_alpha = pm.HalfNormal("sigma_alpha", sigma=0.5)
            sigma_beta_acc = pm.HalfNormal("sigma_beta_acc", sigma=0.1)

            # Varying intercepts and slopes by neighborhood
            alpha = pm.Normal(
                "alpha", mu=mu_alpha, sigma=sigma_alpha, shape=self.n_neighborhoods
            )
            beta_acc = pm.Normal(
                "beta_acc",
                mu=mu_beta_acc,
                sigma=sigma_beta_acc,
                shape=self.n_neighborhoods,
            )

            # =================================================================
            # FIXED EFFECTS: Common across all neighborhoods
            # =================================================================

            # Room type effects
            beta_entire = pm.Normal("beta_entire", mu=0.3, sigma=0.2)
            beta_private = pm.Normal("beta_private", mu=0.1, sigma=0.2)

            # Review effects
            beta_reviews = pm.Normal("beta_reviews", mu=0.1, sigma=0.1)
            beta_score = pm.Normal("beta_score", mu=0.2, sigma=0.1)

            # Availability effect
            beta_availability = pm.Normal("beta_availability", mu=-0.1, sigma=0.1)

            # =================================================================
            # LINEAR PREDICTOR
            # =================================================================

            mu = (
                alpha[neighborhood_idx]
                + beta_acc[neighborhood_idx] * accommodates
                + beta_entire * is_entire_home
                + beta_private * is_private_room
                + beta_reviews * log_reviews
                + beta_score * review_score
                + beta_availability * availability
            )

            # =================================================================
            # LIKELIHOOD
            # =================================================================

            if use_robust_likelihood:
                # Robust Student-t likelihood (handles outliers better)
                nu = pm.Exponential("nu", lam=1 / 10)  # Degrees of freedom
                sigma = pm.HalfNormal("sigma", sigma=0.5)

                log_price_obs = pm.StudentT(
                    "log_price_obs", nu=nu, mu=mu, sigma=sigma, observed=log_price
                )
                logger.info("Using robust Student-t likelihood")
            else:
                # Standard normal likelihood
                sigma = pm.HalfNormal("sigma", sigma=0.5)

                log_price_obs = pm.Normal(
                    "log_price_obs", mu=mu, sigma=sigma, observed=log_price
                )
                logger.info("Using normal likelihood")

        self.model = model
        logger.info("Model built successfully")
        return model

    def fit_model(
        self,
        samples: Optional[int] = None,
        tune: Optional[int] = None,
        chains: Optional[int] = None,
    ) -> az.InferenceData:
        """Fit the model using MCMC sampling."""

        # Use config defaults if not specified
        samples = samples or self.config["model"].get("mcmc_samples", 2000)
        tune = tune or self.config["model"].get("mcmc_tune", 1000)
        chains = chains or self.config["model"].get("mcmc_chains", 4)
        seed = self.config["model"].get("random_seed", 42)

        logger.info(f"Fitting model: {samples} samples, {tune} tuning, {chains} chains")

        with self.model:
            self.trace = pm.sample(
                draws=samples,
                tune=tune,
                chains=chains,
                return_inferencedata=True,
                random_seed=seed,
                target_accept=0.95,  # Higher acceptance for better convergence
            )

            # Add posterior predictive samples
            logger.info("Generating posterior predictive samples")
            self.trace.extend(pm.sample_posterior_predictive(self.trace))

        logger.info("Model fitting complete")
        return self.trace

    def model_diagnostics(self) -> Dict:
        """Comprehensive model diagnostics."""
        logger.info("Running model diagnostics")

        diagnostics = {}

        # Convergence diagnostics
        rhat = az.rhat(self.trace)
        ess = az.ess(self.trace)

        rhat_values = rhat.to_array().values
        ess_values = ess.to_array().values

        diagnostics["max_rhat"] = float(np.nanmax(rhat_values))
        diagnostics["min_ess"] = float(np.nanmin(ess_values))

        # Summary statistics
        summary = az.summary(
            self.trace,
            var_names=[
                "mu_alpha",
                "mu_beta_acc",
                "beta_entire",
                "beta_private",
                "beta_reviews",
                "beta_score",
                "beta_availability",
                "sigma",
            ],
        )

        diagnostics["summary"] = summary

        # Posterior predictive checks
        ppc_data = self.trace.posterior_predictive["log_price_obs"].values
        observed_data = np.log(self.data["price_clean"].values)

        diagnostics["ppc_mean_diff"] = abs(ppc_data.mean() - observed_data.mean())
        diagnostics["ppc_std_diff"] = abs(ppc_data.std() - observed_data.std())

        # Print diagnostics
        print("\n=== MODEL DIAGNOSTICS ===")
        print(f"Max R-hat: {diagnostics['max_rhat']:.4f}")
        if diagnostics["max_rhat"] < 1.01:
            print("✓ Excellent convergence (R-hat < 1.01)")
        elif diagnostics["max_rhat"] < 1.05:
            print("✓ Good convergence (R-hat < 1.05)")
        else:
            print("⚠ Convergence issues (R-hat > 1.05)")

        print(f"Min ESS: {diagnostics['min_ess']:.0f}")
        if diagnostics["min_ess"] > 1000:
            print("✓ Excellent effective sample size")
        elif diagnostics["min_ess"] > 400:
            print("✓ Good effective sample size")
        else:
            print("⚠ Low effective sample size")

        print("\n=== PARAMETER ESTIMATES ===")
        print(summary)

        return diagnostics

    def cross_validate(self, n_folds: int = 5) -> pd.DataFrame:
        """Perform cross-validation to assess model performance."""
        logger.info(f"Running {n_folds}-fold cross-validation")

        kf = KFold(n_splits=n_folds, shuffle=True, random_seed=42)
        cv_results = []

        for fold, (train_idx, test_idx) in enumerate(kf.split(self.data)):
            logger.info(f"Fold {fold + 1}/{n_folds}")

            # Split data
            train_data = self.data.iloc[train_idx].copy()
            test_data = self.data.iloc[test_idx].copy()

            # Temporarily replace data
            original_data = self.data
            self.data = train_data

            # Build and fit model
            self.build_enhanced_model()
            self.fit_model(samples=500, tune=500, chains=2)  # Faster for CV

            # Make predictions on test set
            test_predictions = self._predict_on_data(test_data)

            # Calculate metrics
            test_actual = np.log(test_data["price_clean"].values)
            rmse = np.sqrt(np.mean((test_predictions - test_actual) ** 2))
            mae = np.mean(np.abs(test_predictions - test_actual))
            r2 = 1 - np.sum((test_actual - test_predictions) ** 2) / np.sum(
                (test_actual - test_actual.mean()) ** 2
            )

            cv_results.append({"fold": fold + 1, "rmse": rmse, "mae": mae, "r2": r2})

            # Restore original data
            self.data = original_data

        cv_df = pd.DataFrame(cv_results)
        logger.info(
            f"CV Results: RMSE={cv_df['rmse'].mean():.4f}, R²={cv_df['r2'].mean():.4f}"
        )

        return cv_df

    def _predict_on_data(self, data: pd.DataFrame) -> np.ndarray:
        """Make predictions on new data."""
        # Extract posterior means
        alpha_mean = self.trace.posterior["alpha"].mean(dim=["chain", "draw"]).values
        beta_acc_mean = (
            self.trace.posterior["beta_acc"].mean(dim=["chain", "draw"]).values
        )
        beta_entire_mean = self.trace.posterior["beta_entire"].mean().values
        beta_private_mean = self.trace.posterior["beta_private"].mean().values
        beta_reviews_mean = self.trace.posterior["beta_reviews"].mean().values
        beta_score_mean = self.trace.posterior["beta_score"].mean().values
        beta_availability_mean = self.trace.posterior["beta_availability"].mean().values

        # Make predictions
        neighborhood_idx = data["neighborhood_idx"].values
        predictions = (
            alpha_mean[neighborhood_idx]
            + beta_acc_mean[neighborhood_idx] * data["accommodates"].values
            + beta_entire_mean * data["is_entire_home"].values
            + beta_private_mean * data["is_private_room"].values
            + beta_reviews_mean * data["log_reviews"].values
            + beta_score_mean * data["review_score"].values
            + beta_availability_mean * data["availability_ratio"].values
        )

        return predictions

    def predict_price(
        self,
        neighborhood: str,
        accommodates: int,
        room_type: str = "Entire home/apt",
        n_reviews: int = 10,
        review_score: float = 90,
        availability: int = 200,
    ) -> Dict:
        """
        Predict price with uncertainty for specific listing characteristics.

        Args:
            neighborhood: Neighborhood name
            accommodates: Number of guests
            room_type: Type of room
            n_reviews: Number of reviews
            review_score: Review score (0-100)
            availability: Days available per year

        Returns:
            Dictionary with price predictions and uncertainty
        """
        if neighborhood not in self.neighborhoods:
            logger.error(f"Neighborhood '{neighborhood}' not found")
            return None

        # Get neighborhood index
        neighborhood_idx = self.neighborhoods.index(neighborhood)

        # Encode features (need to standardize like training data)
        is_entire = 1 if room_type == "Entire home/apt" else 0
        is_private = 1 if room_type == "Private room" else 0

        # Standardize features using fitted scaler
        features = np.array(
            [
                [
                    accommodates,
                    np.log1p(n_reviews),
                    review_score / 100,
                    availability / 365,
                ]
            ]
        )
        features_scaled = self.scaler.transform(features)[0]

        # Extract posterior samples
        alpha_samples = self.trace.posterior["alpha"].values.reshape(
            -1, self.n_neighborhoods
        )[:, neighborhood_idx]
        beta_acc_samples = self.trace.posterior["beta_acc"].values.reshape(
            -1, self.n_neighborhoods
        )[:, neighborhood_idx]
        beta_entire_samples = self.trace.posterior["beta_entire"].values.flatten()
        beta_private_samples = self.trace.posterior["beta_private"].values.flatten()
        beta_reviews_samples = self.trace.posterior["beta_reviews"].values.flatten()
        beta_score_samples = self.trace.posterior["beta_score"].values.flatten()
        beta_availability_samples = self.trace.posterior[
            "beta_availability"
        ].values.flatten()

        # Predict log price
        log_price_pred = (
            alpha_samples
            + beta_acc_samples * features_scaled[0]
            + beta_entire_samples * is_entire
            + beta_private_samples * is_private
            + beta_reviews_samples * features_scaled[1]
            + beta_score_samples * features_scaled[2]
            + beta_availability_samples * features_scaled[3]
        )

        # Convert to price scale
        price_pred = np.exp(log_price_pred)

        return {
            "mean": price_pred.mean(),
            "median": np.median(price_pred),
            "std": price_pred.std(),
            "ci_50": np.percentile(price_pred, [25, 75]),
            "ci_80": np.percentile(price_pred, [10, 90]),
            "ci_95": np.percentile(price_pred, [2.5, 97.5]),
            "min": price_pred.min(),
            "max": price_pred.max(),
        }

    def get_feature_importance(self) -> pd.DataFrame:
        """Analyze feature importance based on posterior distributions."""
        logger.info("Calculating feature importance")

        features = [
            "beta_acc",
            "beta_entire",
            "beta_private",
            "beta_reviews",
            "beta_score",
            "beta_availability",
        ]

        importance = []
        for feat in features:
            if feat in self.trace.posterior:
                samples = self.trace.posterior[feat].values.flatten()
                importance.append(
                    {
                        "feature": feat.replace("beta_", ""),
                        "mean": samples.mean(),
                        "std": samples.std(),
                        "ci_95_lower": np.percentile(samples, 2.5),
                        "ci_95_upper": np.percentile(samples, 97.5),
                        "prob_positive": (samples > 0).mean(),
                    }
                )

        return pd.DataFrame(importance).sort_values("mean", key=abs, ascending=False)


def main():
    """Example usage of enhanced model."""
    model = EnhancedBayesianPriceModel("config.yaml")

    # Load data
    model.load_and_clean_data()

    # Build and fit model
    model.build_enhanced_model(use_robust_likelihood=True)
    model.fit_model(samples=1000, tune=1000, chains=2)

    # Diagnostics
    diagnostics = model.model_diagnostics()

    # Feature importance
    importance = model.get_feature_importance()
    print("\n=== FEATURE IMPORTANCE ===")
    print(importance)

    # Example prediction
    prediction = model.predict_price(
        neighborhood="Capitol Hill",
        accommodates=4,
        room_type="Entire home/apt",
        n_reviews=25,
        review_score=95,
        availability=300,
    )

    if prediction:
        print("\n=== PRICE PREDICTION ===")
        print(f"Predicted price: ${prediction['mean']:.2f}")
        print(f"95% CI: ${prediction['ci_95'][0]:.2f} - ${prediction['ci_95'][1]:.2f}")

    return model


if __name__ == "__main__":
    model = main()

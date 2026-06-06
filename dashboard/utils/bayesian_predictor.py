# dashboard/utils/bayesian_predictor.py
"""Real Bayesian predictions from PyMC posterior samples."""
import numpy as np


def standardize_feature(value: float, mean: float, std: float) -> float:
    """Standardize feature to match training scale.

    Args:
        value: Raw feature value
        mean: Training data mean
        std: Training data std

    Returns:
        Standardized value
    """
    return (value - mean) / std


def predict_price(
    inputs: dict, posterior_samples: dict, scaler_params: dict, n_samples: int = 500
) -> dict:
    """Generate price predictions from PyMC posterior samples.

    Args:
        inputs: Dict with accommodates, bedrooms, bathrooms, beds
        posterior_samples: Dict of posterior arrays (intercept, beta_*, etc.)
        scaler_params: Dict with *_mean and *_std from training data
        n_samples: Number of posterior samples to use

    Returns:
        Dict with median, ci_lower, ci_upper, samples

    Note:
        Uses real MCMC posterior samples, not np.random.normal.
        Posterior already includes uncertainty — no manual noise added.
    """
    # Standardize inputs using TRAINING data stats (not current data)
    accommodates_std = standardize_feature(
        inputs["accommodates"],
        scaler_params["accommodates_mean"],
        scaler_params["accommodates_std"],
    )

    # Generate predictions from posterior samples
    # Each sample represents one plausible parameter setting
    intercept = posterior_samples["intercept"][:n_samples]
    beta_accommodates = posterior_samples["beta_accommodates"][:n_samples]

    # Log-scale predictions
    log_price_samples = intercept + beta_accommodates * accommodates_std

    # TODO(Phase 5): Add bedroom, bathroom, room_type effects
    # log_price_samples += beta_bedrooms * bedrooms_std
    # log_price_samples += beta_bathrooms * bathrooms_std

    # Exponentiate to get prices (model predicts log(price))
    price_samples = np.exp(log_price_samples)

    # Compute credible interval
    median = np.median(price_samples)
    ci_lower = np.percentile(price_samples, 2.5)
    ci_upper = np.percentile(price_samples, 97.5)

    return {
        "median": median,
        "ci_lower": ci_lower,
        "ci_upper": ci_upper,
        "samples": price_samples,
    }


def predict_from_idata(inputs: dict, idata, scaler_params: dict) -> dict:
    """Wrapper to predict from InferenceData object.

    Args:
        inputs: Feature dict
        idata: PyMC InferenceData with posterior
        scaler_params: Training data statistics

    Returns:
        Dict with median, ci_lower, ci_upper, samples
    """
    import arviz as az  # lazy — only needed when real model is used

    # Extract posterior samples as numpy arrays
    # Model is hierarchical - use global means (mu_alpha, mu_beta)
    posterior_samples = {
        "intercept": idata.posterior["mu_alpha"].values.flatten(),
        "beta_accommodates": idata.posterior["mu_beta"].values.flatten(),
    }

    return predict_price(inputs, posterior_samples, scaler_params)

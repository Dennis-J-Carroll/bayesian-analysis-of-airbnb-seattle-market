"""
Comprehensive test suite for the Hierarchical Bayesian Model.

Tests cover:
- Data loading and preprocessing
- Model building and structure
- Prediction functionality
- Edge cases and error handling
"""

import pytest
import pandas as pd
import numpy as np
import pymc as pm
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from hierarchical_bayesian_model import HierarchicalBayesianPriceModel


class TestDataLoading:
    """Test data loading and preprocessing."""

    def test_load_data_file_exists(self, sample_data_path):
        """Test that data file loads successfully."""
        model = HierarchicalBayesianPriceModel(sample_data_path)
        df = model.load_and_clean_data()

        assert df is not None
        assert len(df) > 0
        assert model.data is not None

    def test_price_cleaning(self, sample_data_path):
        """Test that prices are properly cleaned and converted."""
        model = HierarchicalBayesianPriceModel(sample_data_path)
        df = model.load_and_clean_data()

        # Check price_clean exists and is numeric
        assert "price_clean" in df.columns
        assert pd.api.types.is_numeric_dtype(df["price_clean"])

        # Check no NaN values in price_clean
        assert df["price_clean"].notna().all()

        # Check all prices are positive
        assert (df["price_clean"] > 0).all()

    def test_outlier_filtering(self, sample_data_path):
        """Test that outliers are properly filtered."""
        model = HierarchicalBayesianPriceModel(sample_data_path)
        df = model.load_and_clean_data()

        # Check price bounds
        assert df["price_clean"].min() >= 10
        assert df["price_clean"].max() <= 1000

    def test_neighborhood_indexing(self, sample_data_path):
        """Test that neighborhoods are properly indexed."""
        model = HierarchicalBayesianPriceModel(sample_data_path)
        df = model.load_and_clean_data()

        # Check neighborhood_idx exists
        assert "neighborhood_idx" in df.columns

        # Check neighborhood_idx is continuous from 0 to n-1
        assert df["neighborhood_idx"].min() == 0
        assert df["neighborhood_idx"].max() == model.n_neighborhoods - 1

        # Check no missing neighborhoods
        assert len(model.neighborhoods) == model.n_neighborhoods

    def test_required_columns_present(self, sample_data_path):
        """Test that all required columns are present after cleaning."""
        model = HierarchicalBayesianPriceModel(sample_data_path)
        df = model.load_and_clean_data()

        required_columns = [
            "price_clean",
            "accommodates",
            "neighbourhood_cleansed",
            "neighborhood_idx",
        ]
        for col in required_columns:
            assert col in df.columns, f"Missing required column: {col}"


class TestModelBuilding:
    """Test model construction and structure."""

    def test_model_creation(self, fitted_model):
        """Test that model is created successfully."""
        model = fitted_model
        assert model.model is not None
        assert isinstance(model.model, pm.Model)

    def test_model_parameters(self, fitted_model):
        """Test that model has all required parameters."""
        model = fitted_model

        required_params = [
            "mu_alpha",
            "mu_beta",
            "sigma_alpha",
            "sigma_beta",
            "alpha",
            "beta",
            "sigma",
            "log_price_obs",
        ]

        for param in required_params:
            assert param in model.model.named_vars, f"Missing parameter: {param}"

    def test_hierarchical_structure(self, fitted_model):
        """Test that hierarchical structure is correct."""
        model = fitted_model

        # Check that alpha and beta have correct shape
        alpha_shape = model.model["alpha"].eval().shape
        beta_shape = model.model["beta"].eval().shape

        assert alpha_shape == (model.n_neighborhoods,)
        assert beta_shape == (model.n_neighborhoods,)

    def test_prior_distributions(self, fitted_model):
        """Test that priors are correctly specified."""
        model = fitted_model

        # Check that hyperpriors exist
        assert "mu_alpha" in model.model.named_vars
        assert "mu_beta" in model.model.named_vars
        assert "sigma_alpha" in model.model.named_vars
        assert "sigma_beta" in model.model.named_vars


class TestModelFitting:
    """Test model fitting and MCMC sampling."""

    def test_trace_exists(self, fitted_model):
        """Test that trace is created after fitting."""
        model = fitted_model
        assert model.trace is not None

    def test_convergence_diagnostics(self, fitted_model):
        """Test that convergence diagnostics can be computed."""
        model = fitted_model
        rhat, ess = model.model_diagnostics()

        assert rhat is not None
        assert ess is not None

    def test_posterior_samples(self, fitted_model):
        """Test that posterior samples have correct shape."""
        model = fitted_model

        # Check posterior samples exist
        assert "posterior" in model.trace.groups()

        # Check sample dimensions
        posterior = model.trace.posterior
        assert "chain" in posterior.dims
        assert "draw" in posterior.dims


class TestPredictions:
    """Test prediction functionality."""

    def test_predict_prices_valid_neighborhood(self, fitted_model):
        """Test predictions for a valid neighborhood."""
        model = fitted_model
        neighborhood = model.neighborhoods[0]

        predictions = model.predict_prices([2, 4, 6], neighborhood)

        assert predictions is not None
        assert len(predictions) == 3

        for acc in [2, 4, 6]:
            assert acc in predictions
            assert "mean" in predictions[acc]
            assert "median" in predictions[acc]
            assert "ci_95" in predictions[acc]
            assert predictions[acc]["mean"] > 0

    def test_predict_prices_invalid_neighborhood(self, fitted_model):
        """Test predictions for invalid neighborhood."""
        model = fitted_model
        predictions = model.predict_prices([4], "InvalidNeighborhood")

        assert predictions is None

    def test_prediction_uncertainty(self, fitted_model):
        """Test that predictions include uncertainty."""
        model = fitted_model
        neighborhood = model.neighborhoods[0]

        predictions = model.predict_prices([4], neighborhood)
        pred = predictions[4]

        # Check that CI bounds are different from mean
        assert pred["ci_95"][0] < pred["mean"]
        assert pred["ci_95"][1] > pred["mean"]

        # Check that CI is reasonable (not too wide or narrow)
        ci_width = pred["ci_95"][1] - pred["ci_95"][0]
        assert ci_width > 0
        assert ci_width < pred["mean"] * 5  # CI shouldn't be more than 5x the mean

    def test_accommodates_effect(self, fitted_model):
        """Test that predictions increase with accommodates."""
        model = fitted_model
        neighborhood = model.neighborhoods[0]

        predictions = model.predict_prices([2, 4, 6], neighborhood)

        # Prices should generally increase with accommodates
        # (allowing for some uncertainty in Bayesian predictions)
        mean_2 = predictions[2]["mean"]
        mean_4 = predictions[4]["mean"]
        mean_6 = predictions[6]["mean"]

        # At least the trend should be upward on average
        assert mean_6 > mean_2


class TestNeighborhoodComparison:
    """Test neighborhood comparison functionality."""

    def test_compare_neighborhoods(self, fitted_model):
        """Test neighborhood comparison."""
        model = fitted_model
        comparison = model.compare_neighborhoods(accommodates=4)

        assert comparison is not None
        assert isinstance(comparison, pd.DataFrame)
        assert len(comparison) == model.n_neighborhoods

    def test_comparison_columns(self, fitted_model):
        """Test that comparison has all required columns."""
        model = fitted_model
        comparison = model.compare_neighborhoods(accommodates=4)

        required_cols = [
            "neighborhood",
            "mean_price",
            "median_price",
            "ci_95_lower",
            "ci_95_upper",
        ]
        for col in required_cols:
            assert col in comparison.columns

    def test_comparison_sorted(self, fitted_model):
        """Test that comparison is sorted by mean price."""
        model = fitted_model
        comparison = model.compare_neighborhoods(accommodates=4)

        # Should be sorted descending
        assert (comparison["mean_price"].diff().dropna() <= 0).all()

    def test_comparison_prices_positive(self, fitted_model):
        """Test that all predicted prices are positive."""
        model = fitted_model
        comparison = model.compare_neighborhoods(accommodates=4)

        assert (comparison["mean_price"] > 0).all()
        assert (comparison["ci_95_lower"] > 0).all()
        assert (comparison["ci_95_upper"] > 0).all()


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_single_accommodates_prediction(self, fitted_model):
        """Test prediction with minimum accommodates value."""
        model = fitted_model
        neighborhood = model.neighborhoods[0]

        predictions = model.predict_prices([1], neighborhood)
        assert predictions is not None
        assert 1 in predictions

    def test_large_accommodates_prediction(self, fitted_model):
        """Test prediction with large accommodates value."""
        model = fitted_model
        neighborhood = model.neighborhoods[0]

        # Use max from data
        max_acc = int(model.data["accommodates"].max())
        predictions = model.predict_prices([max_acc], neighborhood)

        assert predictions is not None
        assert max_acc in predictions

    def test_empty_accommodates_list(self, fitted_model):
        """Test prediction with empty accommodates list."""
        model = fitted_model
        neighborhood = model.neighborhoods[0]

        predictions = model.predict_prices([], neighborhood)
        assert predictions == {}


# ===== Fixtures =====


@pytest.fixture(scope="session")
def sample_data_path():
    """Provide path to sample data."""
    return "/home/user/bayesian-analysis-of-airbnb-seattle-market/data/raw/listings.csv"


@pytest.fixture(scope="session")
def fitted_model(sample_data_path):
    """Provide a fitted model for testing (cached for efficiency)."""
    model = HierarchicalBayesianPriceModel(sample_data_path)
    model.load_and_clean_data()
    model.build_hierarchical_model()

    # Use minimal sampling for testing speed
    model.fit_model(samples=100, tune=100, chains=2)

    return model


@pytest.fixture
def sample_predictions(fitted_model):
    """Provide sample predictions for testing."""
    neighborhood = fitted_model.neighborhoods[0]
    return fitted_model.predict_prices([2, 4, 6], neighborhood)


# ===== Integration Tests =====


class TestIntegration:
    """Integration tests for full workflow."""

    def test_full_pipeline(self, sample_data_path):
        """Test complete pipeline from data to predictions."""
        # Initialize
        model = HierarchicalBayesianPriceModel(sample_data_path)

        # Load data
        df = model.load_and_clean_data()
        assert len(df) > 0

        # Build model
        bayesian_model = model.build_hierarchical_model()
        assert bayesian_model is not None

        # Fit model (minimal for speed)
        trace = model.fit_model(samples=100, tune=100, chains=2)
        assert trace is not None

        # Make predictions
        neighborhood = model.neighborhoods[0]
        predictions = model.predict_prices([4], neighborhood)
        assert predictions is not None

        # Compare neighborhoods
        comparison = model.compare_neighborhoods(accommodates=4)
        assert len(comparison) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

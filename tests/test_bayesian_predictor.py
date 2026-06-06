# tests/test_bayesian_predictor.py
import numpy as np


def test_predict_price_with_mock_posterior():
    """Test price prediction with mock posterior samples."""
    from dashboard.utils.bayesian_predictor import predict_price

    # Mock inputs
    inputs = {"accommodates": 2, "bedrooms": 1, "bathrooms": 1, "beds": 1}

    # Mock posterior samples (500 draws)
    mock_posterior = {
        "intercept": np.random.normal(5, 0.1, 500),
        "beta_accommodates": np.random.normal(0.3, 0.05, 500),
    }

    result = predict_price(
        inputs,
        mock_posterior,
        scaler_params={"accommodates_mean": 3, "accommodates_std": 2},
    )

    assert "median" in result
    assert "ci_lower" in result
    assert "ci_upper" in result
    assert "samples" in result
    assert len(result["samples"]) == 500

# tests/test_model_loader.py
def test_load_trained_model():
    """Test loading PyMC model from InferenceData."""
    from dashboard.utils.model_loader import load_trained_model

    # Should return InferenceData or None if file doesn't exist
    idata = load_trained_model()

    # In test environment, file may not exist
    assert idata is None or hasattr(idata, "posterior")


def test_load_scaler_params():
    """Test loading scaler parameters."""
    from dashboard.utils.model_loader import load_scaler_params

    params = load_scaler_params()

    assert isinstance(params, dict)
    # Should have training data statistics
    assert "accommodates_mean" in params
    assert "accommodates_std" in params

# tests/test_validators.py
import pandas as pd
import pytest


def test_validate_schema_success():
    """Test schema validation with all required columns."""
    from dashboard.utils.validators import validate_schema

    df = pd.DataFrame(
        {
            "price": [100, 200],
            "neighbourhood_cleansed": ["A", "B"],
            "room_type": ["Entire home/apt", "Private room"],
            "accommodates": [2, 4],
            "bedrooms": [1, 2],
            "bathrooms": [1, 1.5],
            "beds": [1, 2],
            "availability_365": [100, 200],
            "review_scores_rating": [4.5, 4.8],
        }
    )

    # Should not raise
    warnings = validate_schema(df)
    assert isinstance(warnings, list)


def test_validate_schema_missing_column():
    """Test schema validation with missing required column."""
    from dashboard.utils.validators import validate_schema
    from dashboard.utils.exceptions import ColumnMappingError

    df = pd.DataFrame({"price": [100, 200], "neighbourhood_cleansed": ["A", "B"]})

    with pytest.raises(ColumnMappingError) as exc_info:
        validate_schema(df)

    assert "room_type" in str(exc_info.value)


def test_validate_data_quality():
    """Test data quality checks."""
    from dashboard.utils.validators import validate_data_quality

    # Create dataframe with at least 10 rows (minimum required)
    df = pd.DataFrame(
        {
            "price": [
                100,
                -50,
                999999,
                150,
                200,
                180,
                220,
                190,
                210,
                205,
            ],  # Negative value in row 2
            "accommodates": [2, 0, 4, 2, 3, 4, 2, 3, 4, 2],  # Zero value in row 2
            "bedrooms": [1, None, 2, 1, 2, 1, 2, 1, 2, 1],  # Missing value in row 2
        }
    )

    warnings = validate_data_quality(df)

    assert len(warnings) > 0
    assert any("below" in w.lower() for w in warnings)

# tests/test_schema_detector.py
import pandas as pd


def test_detect_mapping_exact_match():
    """Test schema detection with exact column names."""
    from dashboard.utils.schema_detector import detect_mapping

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

    renamed_df = detect_mapping(df)

    # Should keep standard names
    assert "price" in renamed_df.columns
    assert "neighbourhood_cleansed" in renamed_df.columns


def test_detect_mapping_fuzzy_match():
    """Test schema detection with fuzzy column names."""
    from dashboard.utils.schema_detector import detect_mapping

    df = pd.DataFrame(
        {
            "Price per Night": [100, 200],
            "Neighborhood": ["A", "B"],
            "Room Type": ["Entire home/apt", "Private room"],
            "Max Guests": [2, 4],
            "Bedrooms": [1, 2],
            "Bathrooms": [1, 1.5],
            "Beds": [1, 2],
            "Available Days": [100, 200],
            "Rating": [4.5, 4.8],
        }
    )

    renamed_df = detect_mapping(df)

    # Should rename to standard names
    assert "price" in renamed_df.columns
    assert "neighbourhood_cleansed" in renamed_df.columns
    assert "accommodates" in renamed_df.columns

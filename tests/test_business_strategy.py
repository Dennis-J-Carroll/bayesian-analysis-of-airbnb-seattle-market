# tests/test_business_strategy.py
import pandas as pd
import inspect


def _make_df():
    return pd.DataFrame(
        {
            "price": [100, 150, 200, 80, 300, 120, 400, 90, 250, 175] * 6,
            "neighbourhood_cleansed": (
                [
                    "Capitol Hill",
                    "Ballard",
                    "Fremont",
                    "Queen Anne",
                    "Belltown",
                    "SoDo",
                    "Pioneer Square",
                    "Magnolia",
                    "Eastlake",
                    "Wallingford",
                ]
                * 6
            ),
            "room_type": (
                [
                    "Entire home/apt",
                    "Private room",
                    "Entire home/apt",
                    "Shared room",
                    "Entire home/apt",
                    "Private room",
                    "Entire home/apt",
                    "Private room",
                    "Entire home/apt",
                    "Private room",
                ]
                * 6
            ),
            "accommodates": [2, 1, 4, 1, 3, 2, 6, 1, 3, 2] * 6,
            "bedrooms": [1, 1, 2, 0, 2, 1, 3, 0, 2, 1] * 6,
            "availability_365": [100, 200, 150, 300, 90, 180, 120, 250, 60, 200] * 6,
        }
    )


def test_business_strategy_renders_without_error():
    """render() runs end-to-end without exceptions."""
    import streamlit as st

    st.session_state["default_df"] = _make_df()
    st.session_state["data_source"] = "default"
    st.session_state["theme"] = "modern_neutral"

    from dashboard.pages import business_strategy
    import importlib

    importlib.reload(business_strategy)
    business_strategy.render()


def test_business_strategy_no_stub_text():
    """render() no longer contains placeholder stub text."""
    from dashboard.pages import business_strategy

    source = inspect.getsource(business_strategy.render)
    assert "extracted from monolith" not in source
    assert "2.6×" not in source


def test_compute_revenue_potential():
    """_compute_revenue_potential returns DataFrame with expected columns."""
    from dashboard.pages.business_strategy import _compute_revenue_potential

    df = _make_df()
    result = _compute_revenue_potential(df)
    assert "neighbourhood_cleansed" in result.columns
    assert "revenue_potential" in result.columns
    assert "occupied_days" in result.columns
    assert len(result) == 10
    assert (result["occupied_days"] >= 0).all()


def test_compute_room_type_multipliers():
    """_compute_room_type_multipliers returns multipliers relative to median."""
    from dashboard.pages.business_strategy import _compute_room_type_multipliers

    df = _make_df()
    result = _compute_room_type_multipliers(df)
    assert "room_type" in result.columns
    assert "multiplier" in result.columns
    assert (result["multiplier"] > 0).all()


def test_business_strategy_dark_theme():
    """render() works with deep_forest (dark) theme."""
    import streamlit as st

    st.session_state["default_df"] = _make_df()
    st.session_state["data_source"] = "default"
    st.session_state["theme"] = "deep_forest"

    from dashboard.pages import business_strategy
    import importlib

    importlib.reload(business_strategy)
    business_strategy.render()

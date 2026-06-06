# tests/test_market_intel.py
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
            "review_scores_rating": [4.5, 4.8, 4.2, 4.0, 4.9, 4.3, 4.7, 3.9, 4.6, 4.1]
            * 6,
        }
    )


def test_market_intel_renders_without_error():
    """render() runs without exceptions given valid data."""
    import streamlit as st

    st.session_state["default_df"] = _make_df()
    st.session_state["data_source"] = "default"
    st.session_state["theme"] = "modern_neutral"

    from dashboard.pages import market_intel
    import importlib

    importlib.reload(market_intel)
    market_intel.render()


def test_market_intel_no_placeholder_info():
    """render() no longer contains 'Task 2.7' placeholder."""
    from dashboard.pages import market_intel

    source = inspect.getsource(market_intel.render)
    assert "Task 2.7" not in source
    assert "extracted" not in source.lower()


def test_market_intel_has_four_fragment_sections():
    """Module exports four @st.fragment-decorated section functions."""
    from dashboard.pages import market_intel

    fragments = [
        "_price_distribution_section",
        "_neighborhood_section",
        "_room_type_section",
        "_availability_section",
    ]
    for name in fragments:
        assert hasattr(market_intel, name), f"Missing fragment: {name}"
        assert callable(getattr(market_intel, name)), f"Not callable: {name}"


def test_market_intel_dark_theme():
    """render() works with deep_forest (dark) theme."""
    import streamlit as st

    st.session_state["default_df"] = _make_df()
    st.session_state["data_source"] = "default"
    st.session_state["theme"] = "deep_forest"

    from dashboard.pages import market_intel
    import importlib

    importlib.reload(market_intel)
    market_intel.render()

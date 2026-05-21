# tests/test_kpi_cards.py
import pandas as pd
import pytest


def test_render_market_kpis_with_default_data():
    """Test KPI cards render with Seattle data."""
    from dashboard.components.kpi_cards import render_market_kpis

    df = pd.DataFrame(
        {
            "price": [100, 200, 300],
            "neighbourhood_cleansed": ["Capitol Hill", "Ballard", "Capitol Hill"],
            "availability_365": [100, 200, 300],
        }
    )

    # Should not raise
    render_market_kpis(df)


def test_render_market_kpis_with_empty_df():
    """Test KPI cards handle empty dataframe."""
    from dashboard.components.kpi_cards import render_market_kpis

    df = pd.DataFrame(columns=["price", "neighbourhood_cleansed", "availability_365"])

    # Should not raise
    render_market_kpis(df)

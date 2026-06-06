# tests/test_charts.py
import pandas as pd
import plotly.graph_objects as go


def test_price_distribution_chart():
    """Test price distribution returns Plotly figure."""
    from dashboard.components.charts import price_distribution

    df = pd.DataFrame({"price": [100, 200, 300, 400]})

    fig = price_distribution(df, theme_name="modern_neutral")

    assert isinstance(fig, go.Figure)
    assert len(fig.data) > 0


def test_top_neighborhoods_chart():
    """Test top neighborhoods bar chart."""
    from dashboard.components.charts import top_neighborhoods

    df = pd.DataFrame(
        {
            "neighbourhood_cleansed": [
                "Capitol Hill",
                "Ballard",
                "Capitol Hill",
                "Fremont",
            ],
            "price": [100, 200, 150, 80],
        }
    )

    fig = top_neighborhoods(df, top_n=3, theme_name="modern_neutral")

    assert isinstance(fig, go.Figure)
    assert len(fig.data) > 0

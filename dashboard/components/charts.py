# dashboard/components/charts.py
"""Plotly chart components with theme awareness."""
import pandas as pd
import plotly.graph_objects as go
from ..utils.styling import get_chart_template, get_chart_palette


def price_distribution(
    df: pd.DataFrame, theme_name: str = "modern_neutral"
) -> go.Figure:
    """Create price distribution histogram.

    Args:
        df: Market data with price column
        theme_name: Theme name from themes.yaml

    Returns:
        Plotly figure
    """
    template = get_chart_template(theme_name)
    palette = get_chart_palette(theme_name)

    fig = go.Figure()
    fig.add_trace(
        go.Histogram(
            x=df["price"], nbinsx=50, marker_color=palette[0], name="Price Distribution"
        )
    )

    fig.update_layout(
        title="Price Distribution",
        xaxis_title="Price ($)",
        yaxis_title="Count",
        template=template,
        showlegend=False,
    )

    return fig


def top_neighborhoods(
    df: pd.DataFrame, top_n: int = 10, theme_name: str = "modern_neutral"
) -> go.Figure:
    """Create top neighborhoods bar chart by average price.

    Args:
        df: Market data with neighbourhood_cleansed and price columns
        top_n: Number of top neighborhoods to show
        theme_name: Theme name from themes.yaml

    Returns:
        Plotly figure
    """
    template = get_chart_template(theme_name)
    palette = get_chart_palette(theme_name)

    neighborhood_prices = (
        df.groupby("neighbourhood_cleansed")["price"]
        .mean()
        .sort_values(ascending=False)
        .head(top_n)
    )

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=neighborhood_prices.values,
            y=neighborhood_prices.index,
            orientation="h",
            marker_color=palette[1],
            name="Avg Price",
        )
    )

    fig.update_layout(
        title=f"Top {top_n} Neighborhoods by Avg Price",
        xaxis_title="Average Price ($)",
        yaxis_title="Neighborhood",
        template=template,
        showlegend=False,
    )

    return fig


def room_type_comparison(
    df: pd.DataFrame, theme_name: str = "modern_neutral"
) -> go.Figure:
    """Create room type comparison bar chart.

    Args:
        df: Market data with room_type and price columns
        theme_name: Theme name from themes.yaml

    Returns:
        Plotly figure
    """
    template = get_chart_template(theme_name)
    palette = get_chart_palette(theme_name)

    room_stats = (
        df.groupby("room_type")["price"]
        .agg(["mean", "count"])
        .sort_values("mean", ascending=False)
    )

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=room_stats.index,
            y=room_stats["mean"],
            text=room_stats["count"],
            texttemplate="n=%{text}",
            marker_color=palette[2],
            name="Avg Price",
        )
    )

    fig.update_layout(
        title="Average Price by Room Type",
        xaxis_title="Room Type",
        yaxis_title="Average Price ($)",
        template=template,
        showlegend=False,
    )

    return fig

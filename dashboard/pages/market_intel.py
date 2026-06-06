# dashboard/pages/market_intel.py
"""Market intelligence and trends."""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from ..utils.session_manager import AppState
from ..utils.styling import get_chart_template, get_chart_palette
from ..components.charts import (
    price_distribution,
    top_neighborhoods,
    room_type_comparison,
)


@st.fragment
def _price_distribution_section(df: pd.DataFrame, theme: str):
    """Price distribution chart section — reruns independently."""
    col_title, col_info = st.columns([6, 1])
    with col_title:
        st.subheader("Price Distribution")
    with col_info:
        with st.popover("ℹ️"):
            st.markdown(
                "Distribution of nightly prices across all listings. "
                "Tail outliers are filtered for clarity (99th percentile)."
            )

    # Filter outliers for cleaner visualization
    p99 = df["price"].quantile(0.99)
    df_filtered = df[df["price"] <= p99]

    st.plotly_chart(
        price_distribution(df_filtered, theme_name=theme), use_container_width=True
    )


@st.fragment
def _neighborhood_section(df: pd.DataFrame, theme: str):
    """Top neighborhoods chart section — reruns independently."""
    col_title, col_info = st.columns([6, 1])
    with col_title:
        st.subheader("Top Neighborhoods by Avg Price")
    with col_info:
        with st.popover("ℹ️"):
            st.markdown(
                "Average nightly price per neighborhood. "
                "Only neighborhoods with ≥5 listings shown."
            )

    # Filter neighborhoods with enough listings
    counts = df["neighbourhood_cleansed"].value_counts()
    valid = counts[counts >= 5].index.tolist()
    df_filtered = df[df["neighbourhood_cleansed"].isin(valid)]

    top_n = st.slider(
        "Show top N neighborhoods", min_value=5, max_value=20, value=10, key="mi_top_n"
    )
    st.plotly_chart(
        top_neighborhoods(df_filtered, top_n=top_n, theme_name=theme),
        use_container_width=True,
    )


@st.fragment
def _room_type_section(df: pd.DataFrame, theme: str):
    """Room type comparison section — reruns independently."""
    col_title, col_info = st.columns([6, 1])
    with col_title:
        st.subheader("Room Type Breakdown")
    with col_info:
        with st.popover("ℹ️"):
            st.markdown("Average price and listing count per room type.")

    col_chart, col_table = st.columns(2)
    with col_chart:
        st.plotly_chart(
            room_type_comparison(df, theme_name=theme), use_container_width=True
        )
    with col_table:
        room_stats = (
            df.groupby("room_type")["price"]
            .agg(["mean", "median", "count"])
            .rename(
                columns={"mean": "Avg ($)", "median": "Median ($)", "count": "Listings"}
            )
            .round(0)
            .astype({"Listings": int})
        )
        st.dataframe(room_stats, use_container_width=True)


@st.fragment
def _availability_section(df: pd.DataFrame, theme: str):
    """Availability vs price scatter — reruns independently."""
    col_title, col_info = st.columns([6, 1])
    with col_title:
        st.subheader("Price vs Availability")
    with col_info:
        with st.popover("ℹ️"):
            st.markdown(
                "Scatter of nightly price vs days available per year. "
                "Color-coded by room type. Reveals pricing strategy patterns."
            )

    template = get_chart_template(theme)
    palette = get_chart_palette(theme)

    room_types = sorted(df["room_type"].dropna().unique())
    fig = go.Figure()
    for i, rt in enumerate(room_types):
        subset = df[df["room_type"] == rt]
        subset = subset.sample(min(len(subset), 500), random_state=42)
        fig.add_trace(
            go.Scatter(
                x=subset["availability_365"],
                y=subset["price"],
                mode="markers",
                name=rt,
                marker=dict(color=palette[i % len(palette)], size=5, opacity=0.55),
            )
        )

    fig.update_layout(
        xaxis_title="Availability (days/year)",
        yaxis_title="Price ($/night)",
        template=template,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    st.plotly_chart(fig, use_container_width=True)


def render():
    """Render market intelligence page."""
    st.title("Market Intelligence")

    df = AppState.get_active_df()
    theme = st.session_state.get(AppState.THEME, "modern_neutral")

    _price_distribution_section(df, theme)
    st.markdown("---")
    _neighborhood_section(df, theme)
    st.markdown("---")
    _room_type_section(df, theme)
    st.markdown("---")
    _availability_section(df, theme)

# dashboard/pages/neighborhood.py
"""Neighborhood comparison page."""
import streamlit as st
from ..utils.session_manager import AppState
from ..components.charts import price_distribution


def render():
    """Render neighborhood analysis page."""
    st.title("Neighborhood Analysis")
    df = AppState.get_active_df()
    theme = st.session_state.get(AppState.THEME, "modern_neutral")

    neighborhoods = sorted(df["neighbourhood_cleansed"].unique())
    selected = st.selectbox("Select Neighborhood", neighborhoods)

    subset = df[df["neighbourhood_cleansed"] == selected]

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Listings", len(subset))
        st.metric("Avg Price", f"${subset['price'].mean():.0f}")
    with col2:
        st.metric("Median Price", f"${subset['price'].median():.0f}")
        st.metric(
            "Price Range",
            f"${subset['price'].min():.0f} - ${subset['price'].max():.0f}",
        )

    st.subheader(f"Price Distribution - {selected}")
    fig = price_distribution(subset, theme_name=theme)
    st.plotly_chart(fig, use_container_width=True)

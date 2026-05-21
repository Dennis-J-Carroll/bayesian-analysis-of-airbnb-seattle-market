# dashboard/pages/overview.py
"""Market overview page - KPIs, distributions, top neighborhoods."""
import streamlit as st
from ..utils.session_manager import AppState
from ..components.kpi_cards import render_market_kpis
from ..components.charts import (
    price_distribution,
    top_neighborhoods,
    room_type_comparison,
)


def render():
    """Render market overview page."""
    st.title("Seattle Airbnb Market Overview")

    df = AppState.get_active_df()
    theme = st.session_state.get(AppState.THEME, "modern_neutral")

    render_market_kpis(df)

    st.subheader("Price Distribution")
    fig = price_distribution(df, theme_name=theme)
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Top Neighborhoods")
        fig = top_neighborhoods(df, top_n=10, theme_name=theme)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Room Type Comparison")
        fig = room_type_comparison(df, theme_name=theme)
        st.plotly_chart(fig, use_container_width=True)

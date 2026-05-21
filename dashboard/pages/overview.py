# dashboard/pages/overview.py
"""Market overview page - KPIs, distributions, top neighborhoods."""
import streamlit as st
from ..utils.session_manager import AppState
from ..components.kpi_cards import render_market_kpis


def render():
    """Render market overview page."""
    st.title("Seattle Airbnb Market Overview")

    df = AppState.get_active_df()

    # Use component instead of inline metrics
    render_market_kpis(df)

    st.info("Overview page with KPI component — charts in Task 2.7")

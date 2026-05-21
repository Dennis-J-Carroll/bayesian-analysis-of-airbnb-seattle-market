# dashboard/pages/overview.py
"""Market overview page - KPIs, distributions, top neighborhoods."""
import streamlit as st
import pandas as pd
from ..utils.session_manager import AppState


def render():
    """Render market overview page."""
    st.title("Seattle Airbnb Market Overview")

    df = AppState.get_active_df()

    # Placeholder metrics until Task 2.6 builds components
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Listings", f"{len(df):,}")
    with col2:
        avg_price = df["price"].mean()
        st.metric("Avg Price", f"${avg_price:.0f}")
    with col3:
        neighborhoods = df["neighbourhood_cleansed"].nunique()
        st.metric("Neighborhoods", neighborhoods)
    with col4:
        occupancy = df["availability_365"].dropna().mean()
        st.metric("Avg Availability", f"{occupancy:.0f} days")

    st.info("Overview page extracted from monolith — components in Task 2.6")

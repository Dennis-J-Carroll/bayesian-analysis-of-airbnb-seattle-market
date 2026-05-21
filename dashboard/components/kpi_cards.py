# dashboard/components/kpi_cards.py
"""Market KPI cards component."""
import streamlit as st
import pandas as pd


def render_market_kpis(df: pd.DataFrame):
    """Render 4-column KPI card grid.

    Args:
        df: Market data with price, neighbourhood_cleansed, availability_365 columns
    """
    if df.empty:
        st.warning("No data available for KPIs")
        return

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
        if pd.isna(occupancy):
            occupancy = 0
        st.metric("Avg Availability", f"{occupancy:.0f} days")

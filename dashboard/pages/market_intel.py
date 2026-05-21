# dashboard/pages/market_intel.py
"""Market intelligence and trends."""
import streamlit as st
from ..utils.session_manager import AppState


def render():
    """Render market intelligence page."""
    st.title("Market Intelligence")
    df = AppState.get_active_df()

    st.subheader("Price Distribution by Room Type")
    room_types = df.groupby("room_type")["price"].agg(["mean", "median", "count"])
    st.dataframe(room_types)

    st.info("Market intel page extracted — charts in Task 2.7")

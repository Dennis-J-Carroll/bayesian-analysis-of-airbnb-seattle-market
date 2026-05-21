# dashboard/pages/prediction.py
"""Price prediction page (Phase 4 will add real Bayesian)."""
import streamlit as st


def render():
    """Render price prediction page."""
    st.title("Price Prediction")
    st.info(
        "Phase 4 will replace this with real Bayesian predictions from PyMC posterior"
    )

    col1, col2 = st.columns(2)
    with col1:
        accommodates = st.slider("Accommodates", 1, 16, 2)
        bedrooms = st.slider("Bedrooms", 0, 10, 1)
    with col2:
        bathrooms = st.slider("Bathrooms", 0, 8, 1)
        beds = st.slider("Beds", 0, 16, 1)

    st.button("Predict Price (Coming in Phase 4)")

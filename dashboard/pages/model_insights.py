# dashboard/pages/model_insights.py
"""Bayesian model insights (Phase 4 will add real posteriors)."""
import streamlit as st


def render():
    """Render model insights page."""
    st.title("Model Insights")
    st.info(
        "Phase 4 will add real posterior distributions, convergence diagnostics, feature importance"
    )

    st.subheader("Model Architecture")
    st.write("• Bayesian hierarchical model with neighborhood effects")
    st.write("• PyMC probabilistic programming")
    st.write("• MCMC sampling with NUTS")

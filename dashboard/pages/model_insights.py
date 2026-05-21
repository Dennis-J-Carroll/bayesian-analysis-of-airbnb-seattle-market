# dashboard/pages/model_insights.py
"""Bayesian model insights with posterior diagnostics."""
import streamlit as st
import plotly.graph_objects as go
import arviz as az
from ..utils.model_loader import load_trained_model
from ..utils.styling import get_chart_template, get_chart_palette
from ..utils.session_manager import AppState


def render():
    """Render model insights page with real posteriors."""
    st.title("Model Insights")

    idata = load_trained_model()

    if idata is None:
        st.warning(
            "Trained model not found. Run training script to generate `models/trained_model.nc`"
        )
        return

    theme = st.session_state.get(AppState.THEME, "modern_neutral")
    template = get_chart_template(theme)
    palette = get_chart_palette(theme)

    # Model architecture info
    st.subheader("Model Architecture")
    st.write("• Bayesian hierarchical linear regression")
    st.write("• PyMC probabilistic programming")
    st.write("• MCMC sampling with NUTS")
    st.write(
        f"• Posterior samples: {len(idata.posterior.chain) * len(idata.posterior.draw)}"
    )

    # Convergence diagnostics
    st.subheader("Convergence Diagnostics")

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "R-hat (intercept)",
            f"{az.rhat(idata, var_names=['intercept']).to_array().values[0]:.3f}",
        )
        st.caption("R-hat < 1.01 indicates good convergence")

    with col2:
        ess = az.ess(idata, var_names=["intercept"]).to_array().values[0]
        st.metric("Effective Sample Size", f"{ess:.0f}")
        st.caption("Higher is better (>1000 ideal)")

    # Posterior distributions
    st.subheader("Posterior Distributions")

    # Intercept posterior
    intercept_samples = idata.posterior["intercept"].values.flatten()

    fig = go.Figure()
    fig.add_trace(
        go.Histogram(
            x=intercept_samples, nbinsx=50, marker_color=palette[0], name="Intercept"
        )
    )

    fig.update_layout(
        title="Posterior: Intercept (Log-Price Baseline)",
        xaxis_title="Log(Price)",
        yaxis_title="Frequency",
        template=template,
        showlegend=False,
    )

    st.plotly_chart(fig, use_container_width=True)

    # Beta accommodates posterior
    if "beta_accommodates" in idata.posterior:
        beta_samples = idata.posterior["beta_accommodates"].values.flatten()

        fig = go.Figure()
        fig.add_trace(
            go.Histogram(
                x=beta_samples,
                nbinsx=50,
                marker_color=palette[1],
                name="Beta Accommodates",
            )
        )

        fig.update_layout(
            title="Posterior: Accommodates Effect",
            xaxis_title="Coefficient",
            yaxis_title="Frequency",
            template=template,
            showlegend=False,
        )

        st.plotly_chart(fig, use_container_width=True)

        median_effect = beta_samples.median()
        st.info(
            f"Each additional guest increases log-price by {median_effect:.3f} (median estimate)"
        )

    # Feature importance (TODO: expand in Phase 5)
    st.subheader("Feature Importance")
    st.info(
        "TODO(Phase 5): Add bedroom, bathroom, room_type effects and relative importance"
    )

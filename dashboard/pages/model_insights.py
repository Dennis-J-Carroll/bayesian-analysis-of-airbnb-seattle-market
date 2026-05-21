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
        rhat_val = float(az.rhat(idata, var_names=["mu_alpha"])["mu_alpha"].values)
        st.metric("R-hat (mu_alpha)", f"{rhat_val:.3f}")
        st.caption("R-hat < 1.01 indicates good convergence")

    with col2:
        ess_val = float(az.ess(idata, var_names=["mu_alpha"])["mu_alpha"].values)
        st.metric("Effective Sample Size", f"{ess_val:.0f}")
        st.caption("Higher is better (>1000 ideal)")

    # Posterior distributions
    st.subheader("Posterior Distributions (Global Means)")

    # Intercept posterior (mu_alpha)
    intercept_samples = idata.posterior["mu_alpha"].values.flatten()

    fig = go.Figure()
    fig.add_trace(
        go.Histogram(
            x=intercept_samples, nbinsx=50, marker_color=palette[0], name="mu_alpha"
        )
    )

    fig.update_layout(
        title="Posterior: Global Intercept (mu_alpha)",
        xaxis_title="Log(Price) Baseline",
        yaxis_title="Frequency",
        template=template,
        showlegend=False,
    )

    st.plotly_chart(fig, use_container_width=True)

    # Beta accommodates posterior (mu_beta)
    if "mu_beta" in idata.posterior:
        beta_samples = idata.posterior["mu_beta"].values.flatten()

        fig = go.Figure()
        fig.add_trace(
            go.Histogram(
                x=beta_samples,
                nbinsx=50,
                marker_color=palette[1],
                name="mu_beta",
            )
        )

        fig.update_layout(
            title="Posterior: Global Accommodates Effect (mu_beta)",
            xaxis_title="Coefficient",
            yaxis_title="Frequency",
            template=template,
            showlegend=False,
        )

        st.plotly_chart(fig, use_container_width=True)

        median_effect = float(beta_samples.mean())
        st.info(
            f"Each additional guest increases log-price by {median_effect:.3f} (mean estimate)"
        )

    # Feature importance (TODO: expand in Phase 5)
    st.subheader("Feature Importance")
    st.info(
        "TODO(Phase 5): Add bedroom, bathroom, room_type effects and relative importance"
    )

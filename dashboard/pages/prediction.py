# dashboard/pages/prediction.py
"""Price prediction page with real Bayesian inference."""
import streamlit as st
import plotly.graph_objects as go
from ..utils.model_loader import load_trained_model, load_scaler_params
from ..utils.bayesian_predictor import predict_from_idata
from ..utils.styling import get_chart_template, get_chart_palette
from ..utils.session_manager import AppState


def render():
    """Render price prediction page with real PyMC predictions."""
    st.title("Price Prediction")

    # Load model
    idata = load_trained_model()

    if idata is None:
        st.warning(
            "Trained model not found. Run training script to generate `models/trained_model.nc`"
        )
        st.info(
            "Placeholder UI shown below. Real predictions coming after model training."
        )

    # Input form
    col1, col2 = st.columns(2)

    with col1:
        accommodates = st.slider(
            "Accommodates", 1, 16, 2, help="Maximum number of guests"
        )
        bedrooms = st.slider("Bedrooms", 0, 10, 1)

    with col2:
        bathrooms = st.slider("Bathrooms", 0.0, 8.0, 1.0, step=0.5)
        beds = st.slider("Beds", 0, 16, 1)

    if st.button("Predict Price", type="primary"):
        if idata is None:
            st.error("Cannot predict: model not loaded")
        else:
            with st.spinner("Running Bayesian inference..."):
                inputs = {
                    "accommodates": accommodates,
                    "bedrooms": bedrooms,
                    "bathrooms": bathrooms,
                    "beds": beds,
                }

                scaler_params = load_scaler_params()
                result = predict_from_idata(inputs, idata, scaler_params)

            # Display prediction
            st.success(f"Predicted Price: **${result['median']:.0f}** per night")

            st.info(
                f"95% Credible Interval: ${result['ci_lower']:.0f} - ${result['ci_upper']:.0f}"
            )

            # Posterior distribution plot
            theme = st.session_state.get(AppState.THEME, "modern_neutral")
            template = get_chart_template(theme)
            palette = get_chart_palette(theme)

            fig = go.Figure()
            fig.add_trace(
                go.Histogram(
                    x=result["samples"],
                    nbinsx=50,
                    marker_color=palette[0],
                    name="Posterior Predictive",
                )
            )

            fig.add_vline(
                x=result["median"],
                line_dash="dash",
                line_color=palette[1],
                annotation_text="Median",
                annotation_position="top",
            )

            fig.update_layout(
                title="Posterior Predictive Distribution",
                xaxis_title="Price ($)",
                yaxis_title="Frequency",
                template=template,
                showlegend=False,
            )

            st.plotly_chart(fig, use_container_width=True)

            st.caption(
                "This distribution represents uncertainty in the prediction based on the Bayesian model's posterior samples."
            )

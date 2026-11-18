"""Predict: the Live Specimen and a plain-language reading guide."""

import streamlit as st

from dashboard.components.specimen import render_specimen
from dashboard.utils.artifacts import load_artifacts
from dashboard.utils.posterior import N_DRAWS
from dashboard.utils.session_manager import AppState


def render() -> None:
    art = load_artifacts()
    st.title("Predict a nightly price")
    render_specimen(art, AppState.theme())

    diag = art.diagnostics
    total_draws = diag["n_chains"] * diag["n_draws"]
    st.markdown(
        f"**What you're looking at.** The big number is the model's best guess "
        f"(the median) for one listing at this guest count in the chosen "
        f"neighborhood. The range beside it is where 94% of single listings "
        f"are expected to fall, so it is wide on purpose: it includes the "
        f"ordinary listing-to-listing scatter. Neighborhoods with few listings "
        f"lean toward the citywide pattern (partial pooling), which keeps "
        f"thin data from producing wild estimates. The curves and numbers are "
        f"computed from a seeded {N_DRAWS:,}-draw sample of the "
        f"{total_draws:,} posterior draws. Details are under **How the model works** in the sidebar."
    )

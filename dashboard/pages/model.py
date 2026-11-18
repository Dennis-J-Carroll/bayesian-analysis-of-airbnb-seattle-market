"""How the model works: the specification, its priors, and what it learned."""

import math

import streamlit as st

from dashboard.components.charts import hyper_hist
from dashboard.components.readouts import Readout, render_readouts
from dashboard.utils.artifacts import load_artifacts
from dashboard.utils.session_manager import AppState

CHART_CONFIG = {"displayModeBar": False}

# (artifact key, display label, plain-language reading builder)
HYPERS = [
    ("mu_alpha", "mu_alpha", "mu_alpha"),
    ("sigma_alpha", "sigma_alpha", "sigma_alpha"),
    ("mu_beta", "mu_beta", "mu_beta"),
    ("sigma_beta", "sigma_beta", "sigma_beta"),
    ("sigma", "sigma", "sigma"),
]


def _spread_range(log_sd: float) -> str:
    """One log-scale standard deviation as a below-to-above percent range."""
    return f"{1 - math.exp(-log_sd):.0%} below to {math.expm1(log_sd):.0%} above"


def _reading(key: str, mean: float) -> str:
    return {
        "mu_alpha": (
            "The citywide baseline for log price when the guest count is zero. "
            "It is an anchor for the model, not a real listing."
        ),
        "sigma_alpha": (
            "How much neighborhood baselines differ from each other. A typical "
            f"neighborhood sits about {_spread_range(mean)} the city "
            "baseline (one standard deviation, roughly two thirds of "
            "neighborhoods)."
        ),
        "mu_beta": (
            "The citywide rise in log price for each extra guest. The next "
            "section turns it into a percent."
        ),
        "sigma_beta": (
            "How much the per-guest slope differs between neighborhoods. A "
            "small value means neighborhoods price extra guests alike."
        ),
        "sigma": (
            "Listing-to-listing scatter that no neighborhood or guest count "
            f"explains: about {_spread_range(mean)} the typical price (one "
            "standard deviation, roughly two thirds of listings)."
        ),
    }[key]


def render() -> None:
    art = load_artifacts()
    theme = AppState.theme()
    hyper = art.hyper
    n_nbhd = len(art.neighborhoods["neighborhoods"])

    st.title("How the model works")

    st.markdown(
        "The model predicts the log of a listing's nightly price. Working in "
        "logs means a change in a feature moves price by a percentage rather "
        "than a fixed number of dollars, which matches how prices behave."
    )
    st.markdown(
        f"Each of the {n_nbhd} neighborhoods gets its own intercept (its "
        "baseline price) and its own slope (how much each extra guest adds). "
        "A neighborhood's log price is that intercept plus the slope times the "
        "number of guests the listing accommodates."
    )
    st.markdown(
        "Neighborhoods with few listings would give wild estimates on their "
        "own. Partial pooling fixes that: every intercept and slope is drawn "
        "from a shared citywide distribution, so thin neighborhoods are pulled "
        "toward the city while well-measured ones keep their own signal."
    )

    st.subheader("Notation")
    st.latex(
        r"\log(\mathrm{price}_i) \sim \mathrm{Normal}" r"\left(\mu_i,\ \sigma\right)"
    )
    st.latex(r"\mu_i = \alpha_{n[i]} + \beta_{n[i]} \cdot \mathrm{guests}_i")
    st.latex(r"\alpha_{n} \sim \mathrm{Normal}(\mu_\alpha,\ \sigma_\alpha)")
    st.latex(r"\beta_{n} \sim \mathrm{Normal}(\mu_\beta,\ \sigma_\beta)")
    st.caption(
        "Listing i sits in neighborhood n[i]. The five parameters below are "
        "the citywide hyperparameters; their priors are:"
    )
    st.latex(
        r"""\begin{aligned}
        \mu_\alpha \sim \mathrm{N}(4.5,\ 1) \qquad
        & \sigma_\alpha \sim \mathrm{HalfNormal}(0.5) \\
        \mu_\beta \sim \mathrm{N}(0.2,\ 0.1) \qquad
        & \sigma_\beta \sim \mathrm{HalfNormal}(0.1) \\
        \sigma \sim \mathrm{HalfNormal}(0.5) &
        \end{aligned}"""
    )

    st.subheader("What the data says about the hyperparameters")
    st.caption(
        "Each cell shows the posterior mean, its 94% interval (the band in the "
        "chart, equal-tailed), and a plain reading. Values are on the log scale."
    )
    cells = []
    for start in range(0, len(HYPERS), 3):
        cells += st.columns(3)[: len(HYPERS[start : start + 3])]
    for cell, (key, label, _) in zip(cells, HYPERS):
        s = hyper[key]
        with cell:
            render_readouts(
                [
                    Readout(
                        label,
                        f"{s['mean']:.3f}",
                        f"94% interval {s['lo']:.3f} to {s['hi']:.3f}",
                        f"hyper-{key}",
                    )
                ],
                theme,
            )
            st.caption(_reading(key, s["mean"]))
            st.plotly_chart(
                hyper_hist(s, label, theme),
                use_container_width=True,
                config=CHART_CONFIG,
                theme=None,
                key=f"hyper_{key}",
            )

    st.subheader("What one more guest does to the price")
    pg = hyper["pct_per_guest"]
    render_readouts(
        [
            Readout(
                "Per extra guest",
                f"+{pg['median']:.1f}%",
                f"94% interval {pg['lo']:.1f}% to {pg['hi']:.1f}%",
                "per-guest",
            )
        ],
        theme,
    )
    st.caption(
        "The citywide slope, converted from log units to a percentage: with "
        "everything else equal, each extra guest a listing sleeps is "
        "associated with a price about this much higher, compounding per "
        "guest. It is an association in listing data, not a causal claim."
    )

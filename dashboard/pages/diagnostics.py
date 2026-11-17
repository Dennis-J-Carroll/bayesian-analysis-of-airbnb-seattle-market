"""Diagnostics: convergence and calibration evidence for the fitted model."""

import html

import streamlit as st

from dashboard.components.charts import ppc_plot, rank_plot
from dashboard.components.readouts import Readout, render_readouts
from dashboard.theme import MONO_FONT, TOKENS
from dashboard.utils.artifacts import load_artifacts
from dashboard.utils.session_manager import AppState

CHART_CONFIG = {"displayModeBar": False}
RANK_PARAMS = ["mu_alpha", "sigma_alpha", "mu_beta", "sigma_beta", "sigma"]


def _worst(per_param: dict, field: str, pick) -> str:
    return pick(per_param, key=lambda p: per_param[p][field])


def render() -> None:
    art = load_artifacts()
    theme = AppState.theme()
    d = art.diagnostics
    total = d["n_chains"] * d["n_draws"]
    worst_rhat = _worst(d["per_param"], "rhat", max)
    worst_ess = _worst(d["per_param"], "ess_bulk", min)

    st.title("Diagnostics")
    st.caption(
        f"{d['n_chains']} chains of {d['n_draws']:,} draws each "
        f"({total:,} draws in all), checked on every parameter, including the "
        f"{len(art.neighborhoods['neighborhoods'])} neighborhood intercepts "
        "and slopes."
    )

    render_readouts(
        [
            Readout(
                "Max R-hat",
                f"{d['max_rhat']:.3f}",
                f"Chains agree when this is near 1.00; below 1.01 is the usual bar "
                f"(worst: {worst_rhat}).",
                "max-rhat",
            ),
            Readout(
                "Min bulk ESS",
                f"{d['min_ess_bulk']:,.0f}",
                f"Effective independent draws out of {total:,}; a few hundred is "
                f"a common minimum (worst: {worst_ess}).",
                "min-ess",
            ),
            Readout(
                "Min tail ESS",
                f"{d['min_ess_tail']:,.0f}",
                "The same count for the distribution tails (5% and 95%), which "
                "matter most for interval ends.",
                "min-tail-ess",
            ),
            Readout(
                "Divergences",
                f"{d['divergences']}",
                "Sampler warnings of a bad region; zero means none.",
                "divergences",
            ),
            Readout(
                "Coverage (in-sample)",
                f"{d['coverage_94_in_sample']:.1%}",
                "Share of listings inside their 94% interval, on the data the "
                "model saw. Not out-of-sample validation.",
                "coverage",
            ),
        ],
        theme,
    )

    st.subheader("Do the chains agree?")
    st.caption(
        "Rank plots: each chain's draws are ranked among all chains together. "
        "If the chains explore the same distribution, every chain's bars are "
        "flat along the dashed expected count. A tilt or a hump would flag "
        "trouble."
    )
    for name in RANK_PARAMS:
        st.plotly_chart(
            rank_plot(d["rank"][name], name, theme),
            use_container_width=True,
            config=CHART_CONFIG,
            key=f"rank_{name}",
        )

    st.subheader("Does the model reproduce the data?")
    fig = ppc_plot(d["ppc"], theme)
    st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)
    st.caption(
        "Posterior predictive check: bars are the observed price counts, the "
        "band is where simulated listings from the fitted model land (94%). "
        "Observed bars inside the band mean the model reproduces the overall "
        "price shape. It uses the same data the model was fitted on, so it is "
        "an in-sample check. " + fig.layout.meta["note"].replace("$", "\\$")
    )

    st.subheader("Every parameter")
    t = TOKENS[theme]
    rows = "".join(
        f"<tr><td>{html.escape(name)}</td><td>{v['rhat']:.3f}</td>"
        f"<td>{v['ess_bulk']:,.0f}</td><td>{v['ess_tail']:,.0f}</td></tr>"
        for name, v in d["per_param"].items()
    )
    css = (
        f".pp{{width:100%;border-collapse:collapse;font-family:{MONO_FONT};"
        f"font-size:13px;color:{t['ink']};font-variant-numeric:tabular-nums;}}"
        f".pp th{{text-align:left;font-weight:400;font-size:11px;letter-spacing:0.06em;"
        f"text-transform:uppercase;color:{t['muted']};border-bottom:1px solid {t['ink']};padding:6px 8px 6px 0;}}"
        f".pp td{{border-bottom:1px solid {t['rule']};padding:6px 8px 6px 0;}}"
    )
    st.markdown(
        f"<style>{css}</style><table class='pp'><thead><tr><th>Parameter</th>"
        f"<th>R-hat</th><th>Bulk ESS</th><th>Tail ESS</th></tr></thead>"
        f"<tbody>{rows}</tbody></table>",
        unsafe_allow_html=True,
    )

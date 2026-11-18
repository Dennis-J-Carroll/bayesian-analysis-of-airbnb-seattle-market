"""How the model works page, run through Streamlit's AppTest."""

import re

import pytest
from streamlit.testing.v1 import AppTest

from dashboard.utils.artifacts import load_artifacts


def _page():
    from dashboard.pages import model
    from dashboard.theme import apply_theme
    from dashboard.utils.session_manager import AppState

    AppState.init()
    apply_theme(AppState.theme())
    model.render()


def _run(theme="light"):
    at = AppTest.from_function(_page, default_timeout=60)
    at.session_state["theme"] = theme
    at.run()
    assert not at.exception, at.exception
    return at


def _text(at):
    return " ".join(m.value for m in at.markdown) + " ".join(
        c.value for c in at.caption
    )


@pytest.mark.parametrize("theme", ["light", "dark"])
def test_renders(theme):
    _run(theme)


def test_latex_blocks_cover_notation_and_priors():
    at = _run()
    latex = " ".join(x.value for x in at.latex)
    assert r"\alpha_{n" in latex
    assert r"\sigma" in latex
    for prior in (
        r"\mu_\alpha \sim \mathrm{N}(4.5,\ 1)",
        r"\sigma_\alpha \sim \mathrm{HalfNormal}(0.5)",
        r"\mu_\beta \sim \mathrm{N}(0.2,\ 0.1)",
        r"\sigma_\beta \sim \mathrm{HalfNormal}(0.1)",
        r"\sigma \sim \mathrm{HalfNormal}(0.5)",
    ):
        assert prior in latex


def test_per_guest_effect_from_artifact():
    at = _run()
    text = _text(at)
    pg = load_artifacts().hyper["pct_per_guest"]
    m = re.search(r"per-guest\">\+(\d+\.\d)%<", text)
    assert m and float(m.group(1)) == round(pg["median"], 1)
    assert f"{pg['lo']:.1f}%" in text and f"{pg['hi']:.1f}%" in text
    assert "94% interval" in text


def test_five_hyperparameter_cells():
    at = _run()
    text = _text(at)
    for key in ("mu_alpha", "mu_beta", "sigma_alpha", "sigma_beta", "sigma"):
        assert f'hyper-{key}"' in text
    assert len(at.get("plotly_chart")) == 5


def test_no_unescaped_dollar_pairs_in_prose():
    at = _run()
    for m in at.markdown:
        if "<style>" in m.value:
            continue
        assert len(re.findall(r"(?<!\\)\$", m.value)) < 2, m.value


def test_sigma_readouts_state_both_sides_from_artifact():
    import math

    at = _run()
    text = _text(at)
    h = load_artifacts().hyper
    for key in ("sigma", "sigma_alpha"):
        m = h[key]["mean"]
        assert f"{1 - math.exp(-m):.0%} below to {math.expm1(m):.0%} above" in text
    assert "either way" not in text and "above or below" not in text

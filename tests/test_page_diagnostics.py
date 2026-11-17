"""Diagnostics page, run through Streamlit's AppTest."""

import re

import pytest
from streamlit.testing.v1 import AppTest

from dashboard.utils.artifacts import load_artifacts


def _page():
    from dashboard.pages import diagnostics
    from dashboard.theme import apply_theme
    from dashboard.utils.session_manager import AppState

    AppState.init()
    apply_theme(AppState.theme())
    diagnostics.render()


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


def test_readouts_match_artifact():
    at = _run()
    text = _text(at)
    d = load_artifacts().diagnostics
    assert f'max-rhat">{d["max_rhat"]:.3f}<' in text
    assert f'min-ess">{d["min_ess_bulk"]:,.0f}<' in text
    assert f'divergences">{d["divergences"]}<' in text
    assert f'coverage">{d["coverage_94_in_sample"]:.1%}<' in text
    assert "in-sample" in text
    assert f"{d['n_chains']} chains" in text


def test_rank_plots_and_ppc():
    at = _run()
    charts = at.get("plotly_chart")
    assert len(charts) == 6  # 5 rank plots + PPC


def test_ppc_caption_states_outside_share_from_data():
    at = _run()
    text = _text(at)
    m = re.search(r"(\d+\.\d)% of replicated listings", text)
    assert m
    assert 0.0 < float(m.group(1)) < 2.0


def test_no_unescaped_dollar_pairs_in_prose():
    at = _run()
    for el in list(at.markdown) + list(at.caption):
        if "<style>" in el.value:
            continue
        assert len(re.findall(r"(?<!\\)\$", el.value)) < 2, el.value

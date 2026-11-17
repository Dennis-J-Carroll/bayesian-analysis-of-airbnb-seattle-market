"""Shared Plotly chart builders: one visual language with the Live Specimen."""

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from dashboard.components import charts
from dashboard.theme import TOKENS

ART = Path(__file__).resolve().parents[1] / "outputs" / "app_artifacts"
THEMES = ["light", "dark"]


@pytest.fixture(scope="module")
def nb():
    return json.loads((ART / "neighborhoods.json").read_text())


@pytest.fixture(scope="module")
def hyper():
    return json.loads((ART / "hyper.json").read_text())


@pytest.fixture(scope="module")
def diag():
    return json.loads((ART / "diagnostics.json").read_text())


def _all_figures(nb, hyper, diag, theme, guests=4):
    ns = nb["neighborhoods"]
    return {
        "forest": charts.forest_plot(ns, guests, "Broadway", theme, 150.0),
        "shrinkage": charts.shrinkage_plot(ns, guests, theme, 150.0),
        "price": charts.price_histogram(
            pd.Series([50.0, 80.0, 120.0, 300.0, np.nan]), theme, "Price per night"
        ),
        "hyper": charts.hyper_hist(hyper["mu_beta"], "mu_beta", theme),
        "rank": charts.rank_plot(diag["rank"]["mu_beta"], "mu_beta", theme),
        "ppc": charts.ppc_plot(diag["ppc"], theme),
    }


@pytest.mark.parametrize("theme", THEMES)
def test_every_builder_uses_theme_template(nb, hyper, diag, theme):
    t = TOKENS[theme]
    for name, fig in _all_figures(nb, hyper, diag, theme).items():
        lay = fig.layout
        assert lay.template.layout.font.color == t["ink"], name
        assert "JetBrains Mono" in lay.template.layout.font.family, name
        assert lay.paper_bgcolor == t["ground"], name
        assert lay.plot_bgcolor == t["ground"], name
        assert lay.title.text in (None, ""), name
        assert lay.xaxis.tickfont.size >= 11, name
        assert lay.yaxis.tickfont.size >= 11, name


def test_forest_selected_in_accent(nb):
    ns = nb["neighborhoods"]
    accent = TOKENS["light"]["accent"]
    fig = charts.forest_plot(ns, 3, "Broadway", "light")
    selected = [t for t in fig.data if t.marker.color == accent]
    assert len(selected) == 1 and list(selected[0].y) == ["Broadway"]
    others = [t for t in fig.data if t.marker.color != accent]
    assert others and sum(len(t.y) for t in others) == len(ns) - 1
    line_colors = [s.line.color for s in fig.layout.shapes if s.line.color == accent]
    assert len(line_colors) == 1  # only the selected interval


def test_forest_sorted_by_median(nb):
    ns = nb["neighborhoods"]
    fig = charts.forest_plot(ns, 2, "Broadway", "light")
    xs = [x for t in fig.data for x in t.x]
    by_name = {n["name"]: n["typical"]["median"][1] for n in ns}
    ys = [y for t in fig.data for y in t.y]
    order = fig.layout.yaxis.categoryarray
    assert [by_name[y] for y in order] == sorted(by_name.values())
    assert len(xs) == len(ys) == len(ns)


@pytest.mark.parametrize("guests", [1, 4, 11, 16])
def test_shrinkage_omits_null_raw(nb, guests):
    ns = nb["neighborhoods"]
    expected = sum(1 for n in ns if n["raw_median_by_guests"][str(guests)] is None)
    fig = charts.shrinkage_plot(ns, guests, "light")
    assert fig.layout.meta["omitted"] == expected
    plotted = sum(len(t.x) for t in fig.data if t.mode == "markers")
    assert plotted == len(ns) - expected


def _flat(value):
    if isinstance(value, dict):
        for v in value.values():
            yield from _flat(v)
    elif isinstance(value, (list, tuple, np.ndarray)):
        for v in value:
            yield from _flat(v)
    else:
        yield value


@pytest.mark.parametrize("theme", THEMES)
def test_no_nan_in_figure_data(nb, hyper, diag, theme):
    industrial = [n for n in nb["neighborhoods"] if n["name"] == "Industrial District"]
    assert industrial and None in industrial[0]["raw_median_by_guests"].values()
    ns = industrial + nb["neighborhoods"][:3]
    figs = _all_figures(nb, hyper, diag, theme)
    for g in (1, 5, 16):
        figs[f"forest{g}"] = charts.forest_plot(ns, g, "Industrial District", theme)
        figs[f"shrink{g}"] = charts.shrinkage_plot(ns, g, theme)
    for name, fig in figs.items():
        for trace in fig.data:
            for v in _flat(trace.to_plotly_json()):
                assert v is not None, name
                if isinstance(v, (float, np.floating)):
                    assert np.isfinite(v), name


def _is_step(trace):
    return trace.type == "scatter" and trace.line.shape == "hv"


def test_hyper_hist_is_uniform_step_outline(hyper):
    s = hyper["mu_alpha"]
    fig = charts.hyper_hist(s, "mu_alpha", "light")
    step = fig.data[0]
    assert _is_step(step) and step.fill in (None, "none")
    n = len(s["hist"]["counts"])
    width = (s["hist"]["edges"][-1] - s["hist"]["edges"][0]) / n
    edges = s["hist"]["edges"][0] + width * np.arange(n + 1)
    assert np.allclose(step.x[1:-1], edges)  # uniform, despite rounded edges
    assert list(step.y[1:-2]) == list(s["hist"]["counts"])


@pytest.mark.parametrize("theme", THEMES)
def test_histograms_are_ink_outlines_not_gray_fills(nb, hyper, diag, theme):
    ink = TOKENS[theme]["ink"]
    for name, fig in _all_figures(nb, hyper, diag, theme).items():
        assert not [t for t in fig.data if t.type == "bar"], name
    for name in ("price", "hyper", "rank", "ppc"):
        fig = _all_figures(nb, hyper, diag, theme)[name]
        steps = [t for t in fig.data if _is_step(t)]
        assert steps and all(t.line.color == ink for t in steps), name


def test_rank_plot_one_panel_per_chain(diag):
    fig = charts.rank_plot(diag["rank"]["mu_beta"], "mu_beta", "light")
    steps = [t for t in fig.data if _is_step(t)]
    assert len(steps) == 4
    assert [list(t.y[1:-2]) for t in steps] == [
        list(r) for r in diag["rank"]["mu_beta"]
    ]


def test_rank_plot_annotation_uses_actual_bin_count(diag):
    rank = [[5] * 12 for _ in range(4)]
    fig = charts.rank_plot(rank, "mu_beta", "light")
    texts = " ".join(a.text for a in fig.layout.annotations)
    assert "12 bins" in texts and "20 bins" not in texts


def test_ppc_notes_mass_outside_range(diag):
    fig = charts.ppc_plot(diag["ppc"], "light")
    p = diag["ppc"]
    outside = 1 - sum(p["rep_mean"]) / sum(p["observed"])
    assert outside > 0.005
    assert fig.layout.meta["outside_share"] == pytest.approx(outside)
    assert "outside" in fig.layout.meta["note"]


def test_price_histogram_spans_zero_to_1000_and_counts_all_in_range():
    prices = pd.Series([0.0, 10.0, 24.9, 25.0, 999.0, 1000.0, 50.0, np.nan])
    fig = charts.price_histogram(prices, "light", "Price")
    step = fig.data[0]
    assert _is_step(step) and step.fill in (None, "none")
    assert step.x[0] == 0 and step.x[-1] == 1000  # bins tile $0 to $1,000
    counts = list(step.y[1:-2])
    assert len(counts) == 40
    assert sum(counts) == 7  # every in-range price counted once, NaN dropped
    assert step.y[0] == 0 and step.y[-1] == 0  # outline closes on the baseline


@pytest.mark.parametrize("theme", THEMES)
def test_forest_range_holds_every_interval_and_no_title(nb, theme):
    ns = nb["neighborhoods"]
    fig = charts.forest_plot(ns, 4, "Broadway", theme, 150.0)
    lo, hi = fig.layout.xaxis.range
    assert 10**lo <= min(n["typical"]["lo"][3] for n in ns)
    assert 10**hi >= max(n["typical"]["hi"][3] for n in ns)
    assert fig.layout.title.text == ""
    rows = {s.y0 for s in fig.layout.shapes if isinstance(s.y0, str)}
    assert len(rows) == 88  # one interval line per neighborhood row


def test_forest_y_range_has_no_dead_band(nb):
    ns = nb["neighborhoods"]
    fig = charts.forest_plot(ns, 4, "Broadway", "light", 150.0)
    assert list(fig.layout.yaxis.range) == [-0.5, len(ns) - 0.5]
    assert fig.layout.height == 17 * len(ns)

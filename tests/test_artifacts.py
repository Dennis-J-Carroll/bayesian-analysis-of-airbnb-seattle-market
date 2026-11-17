"""Tests on the committed app artifacts (no trace needed)."""

import json
from pathlib import Path

import numpy as np
import pytest

from dashboard.utils import posterior as P
from dashboard.utils.artifacts import (
    ARTIFACT_DIR,
    load_artifacts,
    neighborhood_by_name,
)


@pytest.fixture(scope="module")
def art():
    return load_artifacts(ARTIFACT_DIR)


@pytest.fixture(scope="module")
def draws():
    return P.load_draws(ARTIFACT_DIR / "draws.npz")


def test_artifacts_load_and_have_88_neighborhoods(art):
    assert len(art.neighborhoods["neighborhoods"]) == 88
    assert art.neighborhoods["guests"] == list(range(1, 17))
    assert [n["index"] for n in art.neighborhoods["neighborhoods"]] == list(range(88))


@pytest.mark.parametrize(
    "name,g",
    [
        ("Broadway", 2),
        ("Holly Park", 16),
        ("Industrial District", 1),
        ("South Lake Union", 4),
    ],
)
def test_neighborhood_numbers_match_draws(art, draws, name, g):
    n = neighborhood_by_name(art, name)
    idx, k = n["index"], g - 1
    lo, hi = P.interval(P.typical_price(draws, idx, g))
    med = float(np.median(P.typical_price(draws, idx, g)))
    assert n["typical"]["median"][k] == pytest.approx(med, abs=0.01)
    assert n["typical"]["lo"][k] == pytest.approx(lo, abs=0.01)
    assert n["typical"]["hi"][k] == pytest.approx(hi, abs=0.01)
    q = P.predictive_quantiles(draws, idx, g)
    for key, v in q.items():
        assert n["predictive"][key][k] == pytest.approx(v, abs=0.01)


def test_known_values(art):
    b = neighborhood_by_name(art, "Broadway")
    assert 160 <= b["typical"]["median"][1] <= 168
    assert 75 <= b["predictive"]["q03"][1] <= 86
    assert 330 <= b["predictive"]["q97"][1] <= 356
    h = neighborhood_by_name(art, "Holly Park")
    assert h["n_listings"] == 2
    assert h["raw_median_by_guests"]["2"] == 59.0
    assert 95 <= h["typical"]["median"][1] <= 110


def test_curves_shape_and_peak(art):
    dens = np.array(art.curves["density"])
    assert dens.shape == (88, 16, 64)
    assert len(art.curves["grid"]) == 64
    assert np.allclose(dens.max(axis=2), 1.0)


def test_cleaning_report_counts(art):
    c = art.cleaning
    got = tuple(
        c[k]
        for k in (
            "rows_raw",
            "missing_price",
            "missing_other",
            "below_min",
            "above_max",
            "rows_kept",
        )
    )
    assert got == (6862, 635, 0, 0, 83, 6144)
    assert c["above_max_hotel_rooms"] == 29
    assert c["above_max_10k_plus"] == 37
    assert c["scraped_from"] == "2025-06-21"
    assert c["scraped_to"] == "2025-06-30"


def test_total_size_under_2mb():
    total = sum(p.stat().st_size for p in Path(ARTIFACT_DIR).iterdir() if p.is_file())
    assert total < 2 * 1024 * 1024


def _raise(token):
    raise ValueError(f"non-finite JSON constant: {token}")


def test_no_nan_in_json():
    for p in Path(ARTIFACT_DIR).glob("*.json"):
        json.loads(p.read_text(), parse_constant=_raise)


def test_raw_median_null_when_no_listings_at_size(art):
    ind = neighborhood_by_name(art, "Industrial District")
    vals = ind["raw_median_by_guests"]
    assert any(v is None for v in vals.values())
    assert all(v is None or v == v for v in vals.values())
    assert vals["1"] is not None or ind["max_guests_observed"] >= 1


def test_diagnostics_shape(art):
    d = art.diagnostics
    assert d["n_chains"] == 4 and d["n_draws"] == 2000
    assert len(d["ppc"]["observed"]) == 40
    assert len(d["ppc"]["edges"]) == 41
    assert all(len(r) == 4 and len(r[0]) == 20 for r in d["rank"].values())
    assert 0.8 <= d["coverage_94_in_sample"] <= 1.0
    assert set(art.hyper) >= {"mu_alpha", "mu_beta", "sigma", "pct_per_guest"}

"""Tests for dashboard.utils.posterior (the single source of prediction math)."""

import numpy as np
import pytest

from dashboard.utils.posterior import (
    PRICE_GRID,
    Draws,
    city_typical_price,
    interval,
    load_draws,
    predictive_density,
    predictive_quantiles,
    predictive_samples,
    save_draws,
    typical_price,
)

S = 2000
N_HOODS = 3
GUESTS = 2


@pytest.fixture(scope="module")
def draws() -> Draws:
    rng = np.random.default_rng(7)
    alpha_loc = np.array([4.2, 4.6, 5.0])
    beta_loc = np.array([0.15, 0.10, 0.20])
    return Draws(
        alpha=alpha_loc + 0.02 * rng.standard_normal((S, N_HOODS)),
        beta=beta_loc + 0.01 * rng.standard_normal((S, N_HOODS)),
        sigma=0.4 + 0.01 * np.abs(rng.standard_normal(S)),
        mu_alpha=4.6 + 0.02 * rng.standard_normal(S),
        mu_beta=0.15 + 0.01 * rng.standard_normal(S),
        source_index=np.arange(S, dtype=np.int64) * 2,
    )


def test_typical_price_matches_formula(draws):
    for i in range(N_HOODS):
        expected = np.exp(draws.alpha[:, i] + draws.beta[:, i] * GUESTS)
        np.testing.assert_allclose(typical_price(draws, i, GUESTS), expected)


def test_city_typical_price_matches_formula(draws):
    expected = np.exp(draws.mu_alpha + draws.mu_beta * GUESTS)
    np.testing.assert_allclose(city_typical_price(draws, GUESTS), expected)


def test_predictive_wider_than_typical(draws):
    for i in range(N_HOODS):
        t_lo, t_hi = interval(typical_price(draws, i, GUESTS))
        p_lo, p_hi = interval(predictive_samples(draws, i, GUESTS))
        assert p_lo < t_lo
        assert p_hi > t_hi


def test_predictive_median_close_to_typical_median(draws):
    for i in range(N_HOODS):
        typical_median = np.median(typical_price(draws, i, GUESTS))
        predictive_median = np.median(predictive_samples(draws, i, GUESTS))
        assert predictive_median == pytest.approx(typical_median, rel=0.03)


def test_predictive_samples_shape(draws):
    assert predictive_samples(draws, 0, GUESTS).shape == (S * 8,)
    assert predictive_samples(draws, 0, GUESTS, per_draw=3).shape == (S * 3,)


def test_quantiles_monotone(draws):
    for i in range(N_HOODS):
        q = predictive_quantiles(draws, i, GUESTS)
        assert list(q) == ["q03", "q25", "q50", "q75", "q97"]
        assert q["q03"] < q["q25"] < q["q50"] < q["q75"] < q["q97"]


def test_density_peak_is_one_and_peaks_near_mode(draws):
    step = PRICE_GRID[1] / PRICE_GRID[0]
    for i in range(N_HOODS):
        density = predictive_density(draws, i, GUESTS)
        assert density.shape == PRICE_GRID.shape
        assert density.max() == 1.0
        mu = np.median(draws.alpha[:, i] + draws.beta[:, i] * GUESTS)
        sigma = np.median(draws.sigma)
        mode = np.exp(mu - sigma**2)
        peak = PRICE_GRID[np.argmax(density)]
        assert max(peak / mode, mode / peak) <= step


def test_predictive_is_deterministic(draws):
    np.testing.assert_array_equal(
        predictive_samples(draws, 1, GUESTS), predictive_samples(draws, 1, GUESTS)
    )
    assert predictive_quantiles(draws, 1, GUESTS) == predictive_quantiles(
        draws, 1, GUESTS
    )


def test_predictive_differs_by_pair(draws):
    assert not np.array_equal(
        predictive_samples(draws, 0, GUESTS), predictive_samples(draws, 1, GUESTS)
    )


def test_save_load_roundtrip(draws, tmp_path):
    path = tmp_path / "draws.npz"
    save_draws(draws, path)
    loaded = load_draws(path)
    for name in ("alpha", "beta", "sigma", "mu_alpha", "mu_beta"):
        np.testing.assert_allclose(
            getattr(loaded, name), getattr(draws, name), rtol=1e-6
        )
        assert getattr(loaded, name).dtype == np.float32
    np.testing.assert_array_equal(loaded.source_index, draws.source_index)
    assert loaded.source_index.dtype == np.int64

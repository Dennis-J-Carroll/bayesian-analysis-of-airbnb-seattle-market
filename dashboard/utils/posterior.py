"""Prediction math for the hierarchical price model.

Model: log(price) ~ Normal(alpha[n] + beta[n] * guests, sigma), with the raw
guest count. This module is the single source of prediction math: the artifact
builder and the runtime app both call it. It depends on numpy only.
"""

from dataclasses import dataclass
from pathlib import Path

import numpy as np

SEED = 20251220
N_DRAWS = 1000
GUESTS = tuple(range(1, 17))
PRICE_GRID = np.geomspace(20, 1000, 64)
CI = (0.03, 0.97)

_PARAM_FIELDS = ("alpha", "beta", "sigma", "mu_alpha", "mu_beta")


@dataclass(frozen=True)
class Draws:
    alpha: np.ndarray  # (S, n_neighborhoods)
    beta: np.ndarray  # (S, n_neighborhoods)
    sigma: np.ndarray  # (S,)
    mu_alpha: np.ndarray  # (S,)
    mu_beta: np.ndarray  # (S,)
    source_index: np.ndarray  # (S,) flat chain*draw index into the full trace


def save_draws(d: Draws, path: Path) -> None:
    """Write draws to a compressed npz: float32 parameters, int64 source index."""
    arrays = {
        name: np.asarray(getattr(d, name), dtype=np.float32) for name in _PARAM_FIELDS
    }
    arrays["source_index"] = np.asarray(d.source_index, dtype=np.int64)
    np.savez_compressed(path, **arrays)


def load_draws(path: Path) -> Draws:
    with np.load(path) as data:
        return Draws(**{name: data[name] for name in (*_PARAM_FIELDS, "source_index")})


def typical_price(d: Draws, idx: int, guests: int) -> np.ndarray:
    """Posterior draws of the typical price exp(alpha + beta * guests), shape (S,)."""
    return np.exp(d.alpha[:, idx] + d.beta[:, idx] * guests)


def city_typical_price(d: Draws, guests: int) -> np.ndarray:
    """Posterior draws of the city-level typical price, shape (S,)."""
    return np.exp(d.mu_alpha + d.mu_beta * guests)


def interval(samples: np.ndarray) -> tuple[float, float]:
    """Equal-tailed 94% interval (3rd and 97th percentiles)."""
    lo, hi = np.quantile(samples, CI)
    return float(lo), float(hi)


def predictive_samples(
    d: Draws, idx: int, guests: int, per_draw: int = 8
) -> np.ndarray:
    """Single-listing price draws including sigma noise, shape (S * per_draw,).

    Deterministic per (idx, guests) pair.
    """
    rng = np.random.default_rng(SEED + 1000 * idx + guests)
    mu = d.alpha[:, idx] + d.beta[:, idx] * guests
    z = rng.standard_normal((mu.shape[0], per_draw))
    return np.exp(mu[:, None] + d.sigma[:, None] * z).ravel()


def predictive_quantiles(d: Draws, idx: int, guests: int) -> dict[str, float]:
    samples = predictive_samples(d, idx, guests)
    qs = np.quantile(samples, [0.03, 0.25, 0.50, 0.75, 0.97])
    return dict(zip(("q03", "q25", "q50", "q75", "q97"), (float(q) for q in qs)))


def predictive_density(
    d: Draws, idx: int, guests: int, grid: np.ndarray = PRICE_GRID
) -> np.ndarray:
    """Mean log-normal pdf over draws on a price grid, scaled so the peak is 1.

    For shape display only; the scale is not a probability density.
    """
    mu = (d.alpha[:, idx] + d.beta[:, idx] * guests)[:, None].astype(np.float64)
    sigma = d.sigma[:, None].astype(np.float64)
    x = np.asarray(grid, dtype=np.float64)[None, :]
    pdf = np.exp(-((np.log(x) - mu) ** 2) / (2 * sigma**2)) / (
        x * sigma * np.sqrt(2 * np.pi)
    )
    density = pdf.mean(axis=0)
    return density / density.max()

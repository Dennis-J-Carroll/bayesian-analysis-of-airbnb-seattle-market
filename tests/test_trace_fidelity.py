"""Fidelity of committed artifacts against the real LFS posterior trace."""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent
TRACE = ROOT / "outputs" / "model_trace.nc"
ART = ROOT / "outputs" / "app_artifacts"

pytestmark = [
    pytest.mark.trace,
    pytest.mark.skipif(
        not TRACE.exists() or TRACE.stat().st_size < 1_000_000,
        reason="model_trace.nc missing or is an LFS pointer",
    ),
]

sys.path.insert(0, str(ROOT / "scripts"))

from dashboard.utils import posterior as P  # noqa: E402
from dashboard.utils.data_loader import (  # noqa: E402
    LISTINGS_PATH,
    clean_listings,
    neighborhood_order,
)


@pytest.fixture(scope="module")
def idata():
    import arviz as az

    return az.from_netcdf(TRACE)


def test_cleaned_data_reproduces_observed_data(idata):
    clean, _ = clean_listings(pd.read_csv(LISTINGS_PATH))
    observed = idata.observed_data["log_price_obs"].values
    price = clean["price"].to_numpy()
    # The trace's logs differ from np.log of the cleaned prices by at most one
    # float64 ulp (measured: 8.9e-16), so compare to 1e-12 and exactly in
    # price space.
    np.testing.assert_allclose(np.log(price), observed, rtol=0, atol=1e-12)
    assert np.array_equal(np.round(np.exp(observed), 6), price)
    assert len(neighborhood_order(clean)) == idata.posterior["alpha"].shape[-1]


def _residuals(idata, clean, names):
    a = idata.posterior["alpha"].mean(("chain", "draw")).values
    b = idata.posterior["beta"].mean(("chain", "draw")).values
    pos = {n: i for i, n in enumerate(names)}
    idx = clean["neighbourhood_cleansed"].map(pos).to_numpy()
    g = clean["accommodates"].to_numpy()
    return np.log(clean["price"].to_numpy()) - (a[idx] + b[idx] * g)


def test_neighborhood_index_order_matches_trace(idata):
    clean, _ = clean_listings(pd.read_csv(LISTINGS_PATH))
    names = neighborhood_order(clean)
    res = _residuals(idata, clean, names)

    def per_nb(r):
        return np.abs(pd.Series(r).groupby(clean["neighbourhood_cleansed"]).mean())

    # Mean absolute per-neighborhood residual; measured 0.015 when aligned.
    assert per_nb(res).mean() < 0.05
    # Negative control: alphabetical order (measured 0.26) must fail the bound.
    wrong = _residuals(idata, clean, sorted(names))
    assert per_nb(wrong).mean() > 0.05
    # Raw accommodates: residual SD matches posterior sigma within 5%
    # (standardized accommodates would give about 0.459 vs sigma 0.38).
    sigma = float(idata.posterior["sigma"].mean())
    assert abs(res.std() / sigma - 1) < 0.05


def test_draws_are_faithful_subsample(idata):
    d = P.load_draws(ART / "draws.npz")
    post = idata.posterior.stack(s=("chain", "draw"))
    # stack order is chain-major, matching flat index chain*n_draw + draw
    src = d.source_index
    assert np.array_equal(np.sort(src), src) and len(set(src.tolist())) == len(src)
    for name in ("alpha", "beta"):
        full = post[name].transpose("s", ...).values
        assert np.array_equal(d.__dict__[name], full[src].astype(np.float32))
    for name in ("sigma", "mu_alpha", "mu_beta"):
        full = post[name].values
        assert np.array_equal(d.__dict__[name], full[src].astype(np.float32))


def test_rebuild_is_byte_identical(tmp_path):
    from build_artifacts import build

    build(TRACE, LISTINGS_PATH, tmp_path)
    for p in sorted(ART.glob("*.json")):
        assert (tmp_path / p.name).read_bytes() == p.read_bytes(), p.name
    a, b = P.load_draws(ART / "draws.npz"), P.load_draws(tmp_path / "draws.npz")
    for name in ("alpha", "beta", "sigma", "mu_alpha", "mu_beta", "source_index"):
        assert np.array_equal(getattr(a, name), getattr(b, name)), name
    assert sorted(x.name for x in tmp_path.iterdir()) == sorted(
        x.name for x in ART.iterdir()
    )

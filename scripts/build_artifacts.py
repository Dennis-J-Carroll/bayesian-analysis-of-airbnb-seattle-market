"""Build the small committed artifacts the deployed app reads.

Usage: venv/bin/python scripts/build_artifacts.py
Reads the full posterior trace and the raw listings; writes draws.npz and
five JSON files. Every interval is equal-tailed 94% (3rd/97th percentile).
"""

import json
import sys
from dataclasses import asdict
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dashboard.utils import posterior as P  # noqa: E402
from dashboard.utils.data_loader import (  # noqa: E402
    LISTINGS_PATH,
    clean_listings,
    neighborhood_order,
)

HYPER_PARAMS = ("mu_alpha", "mu_beta", "sigma_alpha", "sigma_beta", "sigma")
PPC_BINS = 40
PPC_REPS = 200
RANK_BINS = 20
HIST_BINS = 30


def _flat(arr: np.ndarray) -> np.ndarray:
    """(chain, draw, ...) -> (chain*draw, ...), flat index = chain*n_draw + draw."""
    return arr.reshape(arr.shape[0] * arr.shape[1], *arr.shape[2:])


def subsample_draws(idata, n: int = P.N_DRAWS, seed: int = P.SEED) -> P.Draws:
    post = idata.posterior
    total = post.sizes["chain"] * post.sizes["draw"]
    idx = np.sort(np.random.default_rng(seed).choice(total, n, replace=False))
    get = lambda name: _flat(post[name].values)[idx]  # noqa: E731
    return P.Draws(
        alpha=get("alpha"),
        beta=get("beta"),
        sigma=get("sigma"),
        mu_alpha=get("mu_alpha"),
        mu_beta=get("mu_beta"),
        source_index=idx.astype(np.int64),
    )


def _write_json(path: Path, obj) -> None:
    path.write_text(json.dumps(obj, sort_keys=True, separators=(",", ":")))


def _r(x, nd):
    return np.round(np.asarray(x, dtype=float), nd).tolist()


def _neighborhoods(draws: P.Draws, clean: pd.DataFrame, names: list[str]) -> dict:
    guests = P.GUESTS

    def typical(samples_fn):
        med, lo, hi = [], [], []
        for g in guests:
            s = samples_fn(g)
            l, h = P.interval(s)
            med.append(float(np.median(s)))
            lo.append(l)
            hi.append(h)
        return {"median": _r(med, 2), "lo": _r(lo, 2), "hi": _r(hi, 2)}

    out = []
    for i, name in enumerate(names):
        sub = clean[clean["neighbourhood_cleansed"] == name]
        by_g = {}
        for g in guests:
            p = sub.loc[sub["accommodates"] == g, "price"]
            by_g[str(g)] = round(float(p.median()), 2) if len(p) else None
        q = [P.predictive_quantiles(draws, i, g) for g in guests]
        out.append(
            {
                "name": name,
                "index": i,
                "n_listings": int(len(sub)),
                "max_guests_observed": int(sub["accommodates"].max()),
                "raw_median": round(float(sub["price"].median()), 2),
                "raw_median_by_guests": by_g,
                "typical": typical(lambda g, i=i: P.typical_price(draws, i, g)),
                "predictive": {
                    k: _r([x[k] for x in q], 2)
                    for k in ("q03", "q25", "q50", "q75", "q97")
                },
            }
        )
    return {
        "guests": list(guests),
        "city": {"typical": typical(lambda g: P.city_typical_price(draws, g))},
        "neighborhoods": out,
    }


def _curves(draws: P.Draws, n_nb: int) -> dict:
    dens = [
        [_r(P.predictive_density(draws, i, g), 3) for g in P.GUESTS]
        for i in range(n_nb)
    ]
    return {
        "grid": _r(P.PRICE_GRID, 2),
        "guests": list(P.GUESTS),
        "density": dens,
    }


def _hyper(post) -> dict:
    out = {}
    for name in HYPER_PARAMS:
        v = _flat(post[name].values)
        lo, hi = P.interval(v)
        counts, edges = np.histogram(v, bins=HIST_BINS)
        out[name] = {
            "mean": round(float(v.mean()), 4),
            "lo": round(lo, 4),
            "hi": round(hi, 4),
            "hist": {"edges": _r(edges, 4), "counts": counts.tolist()},
        }
    pct = 100 * (np.exp(_flat(post["mu_beta"].values)) - 1)
    lo, hi = P.interval(pct)
    out["pct_per_guest"] = {
        "median": round(float(np.median(pct)), 2),
        "lo": round(lo, 2),
        "hi": round(hi, 2),
    }
    return out


def _rank_counts(post, name: str) -> list[list[int]]:
    v = post[name].values  # (chain, draw)
    n_chain = v.shape[0]
    ranks = np.argsort(np.argsort(v.ravel(), kind="stable"), kind="stable")
    bins = (ranks * RANK_BINS // ranks.size).reshape(n_chain, -1)
    return [np.bincount(b, minlength=RANK_BINS).tolist() for b in bins]


def _diagnostics(idata, draws, clean, names) -> dict:
    import arviz as az

    post = idata.posterior
    rhat = az.rhat(post)
    bulk = az.ess(post, method="bulk")
    tail = az.ess(post, method="tail")
    per = {}
    for name in post.data_vars:
        per[name] = {
            "rhat": round(float(rhat[name].max()), 4),
            "ess_bulk": round(float(bulk[name].min()), 1),
            "ess_tail": round(float(tail[name].min()), 1),
        }
    obs = idata.observed_data["log_price_obs"].values
    edges = np.linspace(obs.min(), obs.max(), PPC_BINS + 1)
    observed = np.histogram(obs, bins=edges)[0]
    ppc = _flat(idata.posterior_predictive["log_price_obs"].values)
    pick = np.random.default_rng(P.SEED).choice(ppc.shape[0], PPC_REPS, replace=False)
    counts = np.array([np.histogram(ppc[j], bins=edges)[0] for j in pick])
    lo, hi = np.quantile(counts, P.CI, axis=0)

    idx_of = {n: i for i, n in enumerate(names)}
    cache, inside = {}, 0
    for nb, g, price in zip(
        clean["neighbourhood_cleansed"], clean["accommodates"], clean["price"]
    ):
        key = (idx_of[nb], int(g))
        if key not in cache:
            cache[key] = P.predictive_quantiles(draws, *key)
        q = cache[key]
        inside += q["q03"] <= price <= q["q97"]

    return {
        "n_chains": int(post.sizes["chain"]),
        "n_draws": int(post.sizes["draw"]),
        "max_rhat": max(v["rhat"] for v in per.values()),
        "min_ess_bulk": min(v["ess_bulk"] for v in per.values()),
        "min_ess_tail": min(v["ess_tail"] for v in per.values()),
        "divergences": int(idata.sample_stats["diverging"].sum()),
        "per_param": per,
        "rank": {n: _rank_counts(post, n) for n in HYPER_PARAMS},
        "ppc": {
            "edges": _r(edges, 4),
            "observed": observed.tolist(),
            "rep_mean": _r(counts.mean(axis=0), 2),
            "rep_lo": _r(lo, 2),
            "rep_hi": _r(hi, 2),
        },
        "coverage_94_in_sample": round(inside / len(clean), 4),
    }


def build(trace_path: Path, listings_path: Path, out_dir: Path) -> None:
    import arviz as az

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    raw = pd.read_csv(listings_path)
    clean, report = clean_listings(raw)
    names = neighborhood_order(clean)

    idata = az.from_netcdf(trace_path)
    P.save_draws(subsample_draws(idata), out_dir / "draws.npz")
    draws = P.load_draws(out_dir / "draws.npz")  # float32 round trip

    _write_json(out_dir / "neighborhoods.json", _neighborhoods(draws, clean, names))
    _write_json(out_dir / "curves.json", _curves(draws, len(names)))
    _write_json(out_dir / "hyper.json", _hyper(idata.posterior))
    _write_json(out_dir / "diagnostics.json", _diagnostics(idata, draws, clean, names))
    scraped = pd.to_datetime(raw["last_scraped"])
    _write_json(
        out_dir / "cleaning.json",
        {
            **asdict(report),
            "scraped_from": scraped.min().strftime("%Y-%m-%d"),
            "scraped_to": scraped.max().strftime("%Y-%m-%d"),
        },
    )


if __name__ == "__main__":
    build(
        ROOT / "outputs" / "model_trace.nc",
        LISTINGS_PATH,
        ROOT / "outputs" / "app_artifacts",
    )

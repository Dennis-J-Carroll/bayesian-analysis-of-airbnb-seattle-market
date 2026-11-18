"""Plotly chart builders on the Live Specimen visual language.

Marks match the Predict page: ink hairline curves, a light ink fill for 94%
bands, dashed strokes where a neighborhood has fewer than 10 listings, hollow
dots for raw medians, and vermilion only for the selection. Histograms are
ink step outlines closed on the baseline, never flat gray bars. Figures carry no
title and no legend unless two series need one; pages supply the headings.
"""

from __future__ import annotations

import math

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from dashboard.components.specimen import _per_log  # R17: one definition
from dashboard.theme import MONO_FONT, TOKENS, plotly_template

SPARSE_BELOW = 10
_MONO = MONO_FONT.replace("'", "")
_PRICE_TICKS = [25, 50, 75, 100, 150, 200, 300, 400, 600, 800, 1600]


def _money(v: float) -> str:
    return f"${v:,.0f}"


def _base(fig: go.Figure, theme: str, height: int) -> go.Figure:
    """Apply the shared template, ground backgrounds and the no-title rule."""
    t = TOKENS[theme]
    fig.update_layout(
        template=plotly_template(theme),
        paper_bgcolor=t["ground"],
        plot_bgcolor=t["ground"],
        title=dict(text=""),
        showlegend=False,
        height=height,
        margin=dict(l=8, r=8, t=12, b=8),
    )
    for axis in (fig.update_xaxes, fig.update_yaxes):
        axis(
            tickfont=dict(family=_MONO, size=11, color=t["ink"]),
            showgrid=False,
            zeroline=False,
            automargin=True,
        )
    return fig


def _step(edges, counts) -> tuple[list[float], list[float]]:
    """Outline of a histogram for a `line_shape="hv"` trace.

    Returns x = [e0, e0..en, en] and y = [0, c0..c(n-1), c(n-1), 0]: the
    outline rises from the baseline at the first edge, steps across every
    bin and drops back at the last edge. Bin counts are `y[1:-2]`.
    """
    edges = [float(e) for e in edges]
    counts = [float(c) for c in counts]
    x = [edges[0], *edges, edges[-1]]
    y = [0.0, *counts, counts[-1], 0.0]
    return x, y


def _step_trace(edges, counts, color: str, width: float = 1, **kw) -> go.Scatter:
    x, y = _step(edges, counts)
    return go.Scatter(
        x=x,
        y=y,
        mode="lines",
        line=dict(color=color, width=width, shape="hv"),
        **kw,
    )


def _line(fig, x0, y0, x1, y1, color, width=1, dash=None, **kw):
    fig.add_shape(
        type="line",
        x0=x0,
        y0=y0,
        x1=x1,
        y1=y1,
        line=dict(color=color, width=width, dash=dash),
        layer="below",
        **kw,
    )


def forest_plot(
    nbhds: list[dict],
    guests: int,
    selected: str,
    theme: str,
    city_median: float | None = None,
) -> go.Figure:
    """94% typical-price intervals and median dots at `guests`, sorted by median.

    Intervals are drawn as shapes so sparse neighborhoods (n < 10) can be dashed.
    `city_median` is the city-wide typical price at `guests` (artifact
    `city.typical.median[guests - 1]`); the vertical rule is omitted when None.
    """
    t = TOKENS[theme]
    i = guests - 1
    rows = sorted(nbhds, key=lambda n: n["typical"]["median"][i])
    names = [n["name"] for n in rows]
    fig = go.Figure()

    def dots(group: list[dict], color: str, size: int) -> None:
        if not group:
            return
        fig.add_trace(
            go.Scatter(
                x=[n["typical"]["median"][i] for n in group],
                y=[n["name"] for n in group],
                mode="markers",
                marker=dict(color=color, size=size, line=dict(width=0)),
                customdata=[
                    [n["typical"]["lo"][i], n["typical"]["hi"][i], n["n_listings"]]
                    for n in group
                ],
                hovertemplate=(
                    "%{y}<br>typical $%{x:,.0f}<br>94%% range $%{customdata[0]:,.0f}"
                    " to $%{customdata[1]:,.0f}<br>n=%{customdata[2]}<extra></extra>"
                ),
            )
        )

    dots([n for n in rows if n["name"] != selected], t["ink"], 5)
    dots([n for n in rows if n["name"] == selected], t["accent"], 8)

    for n in rows:
        chosen = n["name"] == selected
        _line(
            fig,
            n["typical"]["lo"][i],
            n["name"],
            n["typical"]["hi"][i],
            n["name"],
            t["accent"] if chosen else t["ink"],
            width=1.5 if chosen else 1,
            dash="dash" if n["n_listings"] < SPARSE_BELOW else None,
            xref="x",
            yref="y",
        )

    if city_median is not None:
        fig.add_vline(x=city_median, line=dict(color=t["muted"], width=1))
    _base(fig, theme, 17 * len(rows))
    # Shapes do not count toward autorange, so pad the range to hold every interval.
    lo_all = min(n["typical"]["lo"][i] for n in rows)
    hi_all = max(n["typical"]["hi"][i] for n in rows)
    fig.update_xaxes(
        type="log",
        range=[math.log10(lo_all * 0.9), math.log10(hi_all * 1.1)],
        tickvals=_PRICE_TICKS,
        ticktext=[_money(v) for v in _PRICE_TICKS],
        showgrid=True,
        gridcolor=t["rule"],
    )
    fig.update_yaxes(
        type="category",
        categoryorder="array",
        categoryarray=names,
        range=[-0.5, len(rows) - 0.5],  # first category is at the bottom
        tickfont=dict(family=_MONO, size=11, color=t["ink"]),
    )
    return fig


def shrinkage_plot(
    nbhds: list[dict],
    guests: int,
    theme: str,
    city_median: float | None = None,
) -> go.Figure:
    """Raw median (x) against model typical median (y), marker area ~ listings.

    Points above/below the identity line were pulled toward the city by pooling.
    Neighborhoods with no raw median at `guests` are omitted and counted in
    `layout.meta["omitted"]`. `city_median` draws the horizontal city line.
    """
    t = TOKENS[theme]
    i = guests - 1
    kept = [n for n in nbhds if n["raw_median_by_guests"].get(str(guests)) is not None]
    omitted = len(nbhds) - len(kept)
    raw = [float(n["raw_median_by_guests"][str(guests)]) for n in kept]
    model = [n["typical"]["median"][i] for n in kept]

    fig = go.Figure()
    if kept:
        lo = min(raw + model) * 0.85
        hi = max(raw + model) * 1.15
        fig.add_trace(
            go.Scatter(
                x=[lo, hi],
                y=[lo, hi],
                mode="lines",
                line=dict(color=t["ink"], width=1),
                hoverinfo="skip",
            )
        )
    if city_median is not None and kept:
        fig.add_trace(
            go.Scatter(
                x=[lo, hi],
                y=[city_median, city_median],
                mode="lines",
                line=dict(color=t["muted"], width=1),
                hoverinfo="skip",
            )
        )
    fig.add_trace(
        go.Scatter(
            x=raw,
            y=model,
            mode="markers",
            marker=dict(
                color=t["ground"],
                size=[max(5.0, 1.6 * math.sqrt(n["n_listings"])) for n in kept],
                line=dict(color=t["ink"], width=1),
            ),
            customdata=[[n["name"], n["n_listings"]] for n in kept],
            hovertemplate=(
                "%{customdata[0]}<br>raw median $%{x:,.0f}<br>model typical "
                "$%{y:,.0f}<br>n=%{customdata[1]}<extra></extra>"
            ),
        )
    )
    _base(fig, theme, 520)
    fig.update_xaxes(
        type="log",
        tickvals=_PRICE_TICKS,
        ticktext=[_money(v) for v in _PRICE_TICKS],
        title_text="Raw median price of listings",
    )
    fig.update_yaxes(
        type="log",
        tickvals=_PRICE_TICKS,
        ticktext=[_money(v) for v in _PRICE_TICKS],
        title_text="Model typical price",
        showgrid=True,
        gridcolor=t["rule"],
    )
    fig.update_layout(meta={"omitted": omitted})
    return fig


def price_histogram(prices: pd.Series, theme: str, title: str) -> go.Figure:
    """Distribution of nightly prices; `title` labels the x axis, not the figure."""
    t = TOKENS[theme]
    values = pd.to_numeric(prices, errors="coerce").dropna().to_numpy(dtype=float)
    counts, edges = np.histogram(values, bins=np.arange(0, 1001, 25))
    fig = go.Figure(
        _step_trace(
            edges,
            counts,
            t["ink"],
            hovertemplate="from $%{x:,.0f}<br>%{y:,} listings<extra></extra>",
        )
    )
    _base(fig, theme, 320)
    fig.update_xaxes(title_text=title, tickprefix="$")
    fig.update_yaxes(showgrid=True, gridcolor=t["rule"], title_text="Listings")
    return fig


def hyper_hist(summary: dict, label: str, theme: str) -> go.Figure:
    """Posterior histogram of one parameter, as an ink step outline, with its
    94% band and mean.

    Steps use uniform edges taken from the first and last stored edge: the
    stored edges are rounded to 4 decimals and look uneven bin to bin.
    """
    t = TOKENS[theme]
    edges = summary["hist"]["edges"]
    counts = summary["hist"]["counts"]
    n = len(counts)
    width = (edges[-1] - edges[0]) / n
    uniform = [edges[0] + width * k for k in range(n + 1)]
    fig = go.Figure(
        _step_trace(uniform, counts, t["ink"], hovertemplate="%{x:.4f}<extra></extra>")
    )
    fig.add_vrect(
        x0=summary["lo"],
        x1=summary["hi"],
        fillcolor=t["ink"],
        opacity=0.1,
        line_width=0,
        layer="below",
    )
    centre = summary.get("mean", summary.get("median"))
    if centre is not None:
        fig.add_vline(x=centre, line=dict(color=t["ink"], width=1.5))
    _base(fig, theme, 260)
    fig.update_xaxes(title_text=label)
    fig.update_yaxes(visible=False)
    return fig


def rank_plot(rank: list[list[int]], label: str, theme: str) -> go.Figure:
    """Rank histograms as step outlines, one panel per chain. A flat outline
    on the dashed expected count means the chains agree; a tilt or hump
    signals poor mixing."""
    t = TOKENS[theme]
    n_chains = len(rank)
    expected = float(np.mean(rank))
    top = float(max(max(r) for r in rank)) * 1.15
    fig = make_subplots(
        rows=1,
        cols=n_chains,
        shared_yaxes=True,
        horizontal_spacing=0.02,
        subplot_titles=[f"chain {c + 1}" for c in range(n_chains)],
    )
    for c, counts in enumerate(rank, start=1):
        fig.add_trace(
            _step_trace(
                [k - 0.5 for k in range(len(counts) + 1)],
                counts,
                t["ink"],
                hovertemplate="%{y} draws<extra></extra>",
            ),
            row=1,
            col=c,
        )
        fig.add_trace(
            go.Scatter(
                x=[-0.5, len(counts) - 0.5],
                y=[expected, expected],
                mode="lines",
                line=dict(color=t["muted"], width=1, dash="dash"),
                hoverinfo="skip",
            ),
            row=1,
            col=c,
        )
    _base(fig, theme, 240)
    fig.update_xaxes(showticklabels=False)
    fig.update_yaxes(range=[0, top])
    fig.update_yaxes(showgrid=True, gridcolor=t["rule"], row=1, col=1)
    fig.update_annotations(font=dict(family=_MONO, size=11, color=t["muted"]))
    fig.add_annotation(
        text=f"{label}<br>rank among all chains, {len(rank[0])} bins",
        xref="paper",
        yref="paper",
        x=0.5,
        y=-0.12,
        yanchor="top",
        showarrow=False,
        font=dict(family=_MONO, size=11, color=t["muted"]),
    )
    fig.update_layout(margin=dict(l=8, r=8, t=28, b=60))
    return fig


def ppc_plot(ppc: dict, theme: str) -> go.Figure:
    """Observed log-price counts against the replicated 94% band and mean.

    Replicated draws that land outside the binned $10 to $1,000 range are not
    drawn; their share is reported in `layout.meta` so the page can caption it.
    """
    t = TOKENS[theme]
    edges = np.asarray(ppc["edges"], dtype=float)
    centers = (edges[:-1] + edges[1:]) / 2
    observed = np.asarray(ppc["observed"], dtype=float)
    outside = max(0.0, 1 - float(np.sum(ppc["rep_mean"])) / float(observed.sum()))

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=centers,
            y=ppc["rep_hi"],
            mode="lines",
            line=dict(width=0),
            showlegend=False,
            hoverinfo="skip",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=centers,
            y=ppc["rep_lo"],
            mode="lines",
            line=dict(width=0),
            fill="tonexty",
            fillcolor=_rgba(t["ink"], 0.18),
            name="Replicated, 94% band",
            hoverinfo="skip",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=centers,
            y=ppc["rep_mean"],
            mode="lines",
            line=dict(color=t["muted"], width=1, dash="dot"),
            name="Replicated mean",
            hovertemplate="replicated mean %{y:,.0f}<extra></extra>",
        )
    )
    fig.add_trace(
        _step_trace(
            edges,
            observed,
            t["ink"],
            width=1.25,
            name="Observed listings",
            hovertemplate="observed %{y:,.0f}<extra></extra>",
        )
    )
    ticks = [10, 25, 50, 100, 200, 400, 800]
    _base(fig, theme, 340)
    fig.update_xaxes(
        tickvals=[math.log(v) for v in ticks],
        ticktext=[_money(v) for v in ticks],
        title_text="Nightly price, log scale",
    )
    fig.update_yaxes(showgrid=True, gridcolor=t["rule"], title_text="Listings")
    fig.update_layout(
        showlegend=True,
        legend=dict(
            orientation="h",
            y=1.08,
            x=0,
            font=dict(family=_MONO, size=11, color=t["ink"]),
        ),
        margin=dict(l=8, r=8, t=36, b=8),
        meta={
            "outside_share": outside,
            "note": (
                f"{outside:.1%} of replicated listings fall outside the plotted "
                "$10 to $1,000 range and are not drawn."
            ),
        },
    )
    return fig


def _rgba(hex_color: str, alpha: float) -> str:
    h = hex_color.lstrip("#")
    r, g, b = (int(h[k : k + 2], 16) for k in (0, 2, 4))
    return f"rgba({r},{g},{b},{alpha})"


# Raw listing prices are binned on the same log axis as the curve: 16 bins a
# decade from $10 (the training floor) to $1,000 (the ceiling).
_LEAD_EDGES = np.geomspace(10, 1000, 33)
_LEAD_TICKS = [10, 20, 50, 100, 200, 500, 1000]


def neighborhood_lead(
    nbhd: dict,
    density_row: list,
    grid: list,
    prices: pd.Series,
    guests: int,
    theme: str,
    city_median: float | None = None,
) -> go.Figure:
    """One neighborhood at `guests`, drawn the way a specimen cell is.

    The ink curve is the predictive density of one listing per log-dollar
    (R17), peak 1, with its 94% band filled beneath it; dashed and thinner
    when the neighborhood has fewer than 10 listings. The listings that
    actually sleep `guests` are a muted step outline on the same log bins,
    scaled to the same peak, with a hollow dot at their raw median on the
    baseline. A muted vertical marks the city's typical price.
    """
    t = TOKENS[theme]
    i = guests - 1
    xs = [float(x) for x in grid]
    ys = [float(y) for y in _per_log(density_row, xs)]
    sparse = nbhd["n_listings"] < SPARSE_BELOW
    lo, hi = nbhd["predictive"]["q03"][i], nbhd["predictive"]["q97"][i]
    fig = go.Figure()

    # 94% band: the curve between lo and hi, interpolated at both ends.
    log_x = np.log(xs)
    inner = [(x, y) for x, y in zip(xs, ys) if lo < x < hi]
    band_x = [lo, *(x for x, _ in inner), hi]
    band_y = [
        float(np.interp(math.log(lo), log_x, ys)),
        *(y for _, y in inner),
        float(np.interp(math.log(hi), log_x, ys)),
    ]
    fig.add_trace(
        go.Scatter(
            x=band_x,
            y=band_y,
            name="band",
            mode="lines",
            line=dict(width=0),
            fill="tozeroy",
            fillcolor=_rgba(t["ink"], 0.1),
            hoverinfo="skip",
        )
    )

    values = pd.to_numeric(prices, errors="coerce").dropna().to_numpy(dtype=float)
    if values.size:
        counts, edges = np.histogram(values, bins=_LEAD_EDGES)
        top = float(counts.max())
        x, y = _step(edges, counts / top)
        _, raw_counts = _step(edges, counts)
        fig.add_trace(
            go.Scatter(
                x=x,
                y=y,
                name="listings",
                mode="lines",
                line=dict(color=t["muted"], width=1, shape="hv"),
                customdata=[[int(c)] for c in raw_counts],
                hovertemplate="from $%{x:,.0f}<br>%{customdata[0]} listings"
                "<extra></extra>",
            )
        )

    fig.add_trace(
        go.Scatter(
            x=xs,
            y=ys,
            name="curve",
            mode="lines",
            line=dict(
                color=t["ink"],
                width=1 if sparse else 1.5,
                dash="dash" if sparse else "solid",
            ),
            hoverinfo="skip",
        )
    )

    if city_median is not None:
        _line(fig, city_median, 0, city_median, 1.06, t["muted"], xref="x", yref="y")
        fig.add_annotation(
            x=math.log10(city_median),
            y=1.06,
            xref="x",
            yref="y",
            text=f"city {_money(city_median)}",
            showarrow=False,
            xanchor="right",
            yanchor="bottom",
            font=dict(family=_MONO, size=11, color=t["muted"]),
        )

    raw = nbhd["raw_median_by_guests"].get(str(guests))
    if raw is not None and values.size:
        fig.add_trace(
            go.Scatter(
                x=[float(raw)],
                y=[0.0],
                name="raw median",
                mode="markers",
                marker=dict(
                    color=t["ground"], size=9, line=dict(color=t["ink"], width=1.25)
                ),
                cliponaxis=False,
                hovertemplate="raw median $%{x:,.0f}<extra></extra>",
            )
        )

    _base(fig, theme, 280)
    fig.update_xaxes(
        type="log",
        range=[1.0, 3.0],
        tickvals=_LEAD_TICKS,
        ticktext=[_money(v) for v in _LEAD_TICKS],
        showline=True,
        linecolor=t["ink"],
        linewidth=1,
        title_text=f"Nightly price at {guests} guests, log scale",
        title_font=dict(family=_MONO, size=11, color=t["muted"]),
    )
    fig.update_yaxes(visible=False, range=[-0.06, 1.12])
    fig.update_layout(margin=dict(l=8, r=8, t=8, b=8), hovermode="closest")
    return fig

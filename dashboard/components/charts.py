"""Plotly chart builders on the Live Specimen visual language.

Marks match the Predict page: ink hairline curves, a light ink fill for 94%
bands, dashed strokes where a neighborhood has fewer than 10 listings, hollow
dots for raw medians, and vermilion only for the selection. Figures carry no
title and no legend unless two series need one; pages supply the headings.
"""

from __future__ import annotations

import math

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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
    centers = (edges[:-1] + edges[1:]) / 2
    fig = go.Figure(
        go.Bar(
            x=centers,
            y=counts,
            width=float(edges[1] - edges[0]),
            marker=dict(
                color=t["ink"],
                opacity=0.12,
                line=dict(color=t["ink"], width=1),
            ),
            hovertemplate="$%{x:,.0f}<br>%{y:,} listings<extra></extra>",
        )
    )
    _base(fig, theme, 320)
    fig.update_xaxes(title_text=title, tickprefix="$")
    fig.update_yaxes(showgrid=True, gridcolor=t["rule"], title_text="Listings")
    return fig


def hyper_hist(summary: dict, label: str, theme: str) -> go.Figure:
    """Posterior histogram of one parameter with its 94% band and mean.

    Bars sit at bin centers with one width taken from the first and last edge:
    the stored edges are rounded to 4 decimals and look uneven bin to bin.
    """
    t = TOKENS[theme]
    edges = summary["hist"]["edges"]
    counts = summary["hist"]["counts"]
    n = len(counts)
    width = (edges[-1] - edges[0]) / n
    centers = [edges[0] + width * (k + 0.5) for k in range(n)]
    fig = go.Figure(
        go.Bar(
            x=centers,
            y=counts,
            width=width,
            marker=dict(color=t["ink"], opacity=0.3, line=dict(width=0)),
            hovertemplate="%{x:.4f}<extra></extra>",
        )
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
    """Rank histograms, one panel per chain. Flat bars at the dashed expected
    count mean the chains agree; a tilt or hump signals poor mixing."""
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
            go.Bar(
                x=list(range(len(counts))),
                y=counts,
                marker=dict(color=t["ink"], opacity=0.3, line=dict(width=0)),
                hovertemplate="rank bin %{x}<br>%{y} draws<extra></extra>",
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
        text=f"{label}: rank of each draw among all chains, 20 bins",
        xref="paper",
        yref="paper",
        x=0.5,
        y=-0.08,
        showarrow=False,
        font=dict(family=_MONO, size=11, color=t["muted"]),
    )
    fig.update_layout(margin=dict(l=8, r=8, t=28, b=36))
    return fig


def ppc_plot(ppc: dict, theme: str) -> go.Figure:
    """Observed log-price counts against the replicated 94% band and mean.

    Replicated draws that land outside the binned $10 to $1,000 range are not
    drawn; their share is reported in `layout.meta` so the page can caption it.
    """
    t = TOKENS[theme]
    edges = np.asarray(ppc["edges"], dtype=float)
    centers = (edges[:-1] + edges[1:]) / 2
    width = float((edges[-1] - edges[0]) / len(centers))
    observed = np.asarray(ppc["observed"], dtype=float)
    outside = max(0.0, 1 - float(np.sum(ppc["rep_mean"])) / float(observed.sum()))

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=centers,
            y=observed,
            width=width,
            name="Observed listings",
            marker=dict(color=t["ink"], opacity=0.12, line=dict(width=0)),
            hovertemplate="observed %{y:,.0f}<extra></extra>",
        )
    )
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
            line=dict(color=t["ink"], width=1),
            name="Replicated mean",
            hovertemplate="replicated mean %{y:,.0f}<extra></extra>",
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
        legend=dict(orientation="h", y=1.08, x=0, font=dict(family=_MONO, size=11)),
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

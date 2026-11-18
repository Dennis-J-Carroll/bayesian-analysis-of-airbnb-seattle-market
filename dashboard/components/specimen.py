"""Live Specimen: the app's first screen.

One guest-count slider redraws the posterior price curve of all 88 Seattle
neighborhoods at once. Rendered through streamlit.components.v1.html, so the
iframe gets the theme tokens injected as CSS custom properties and the whole
payload embedded as JSON. The HTML is complete before any script runs: the
initial readouts and every initial curve are drawn here, in Python; the inline
script only redraws on input, with the same formulas.
"""

import html
import json
import math
from pathlib import Path

import streamlit.components.v1 as components

from dashboard.theme import FONTS_URL, TOKENS
from dashboard.utils.artifacts import Artifacts, neighborhood_by_name

TEMPLATE_PATH = Path(__file__).with_name("specimen_template.html")

# Cells keep one layout while the slider moves: priciest first by the median
# price of one listing at this guest count, the same number each cell shows.
ORDER_GUESTS = 2

# Curve box, in SVG user units. TOP leaves room so a peak is never clipped.
WIDTH, HEIGHT, TOP = 100, 44, 2

# components.html does not size itself to its content, so the height is fixed.
# 1390 shows the whole grid, worst-case extrapolation note included, when the
# iframe is about 940px wide (a 1440px viewport in wide layout). Narrower
# iframes wrap the cells into more rows and the grid scrolls inside the frame;
# the component then shows a scroll hint (measured worst case: 1380px).
DEFAULT_HEIGHT = 1390

# Fewer listings than this: the curve is drawn tentatively (thin, dashed, no
# band fill), so partial pooling toward the city reads at a glance.
SPARSE_BELOW = 10

MISSING = "—"
MINUS = "−"
EN_DASH = "–"


def specimen_payload(
    art: Artifacts, theme: str, initial: str = "Broadway", initial_guests: int = 2
) -> dict:
    """Everything the component needs, in fixed cell order. Copies, never
    references, the cached artifact lists."""
    tokens = dict(TOKENS[theme])
    neighborhood_by_name(art, initial)
    guest_values = list(art.neighborhoods["guests"])
    if initial_guests not in guest_values:
        raise ValueError(f"initial_guests must be one of {guest_values}")

    k = guest_values.index(ORDER_GUESTS)
    ordered = sorted(
        art.neighborhoods["neighborhoods"],
        key=lambda n: (-n["predictive"]["q50"][k], n["index"]),
    )
    density = art.curves["density"]
    grid = list(art.curves["grid"])
    cells = [
        {
            "name": n["name"],
            "index": n["index"],
            "n_listings": n["n_listings"],
            "max_guests_observed": n["max_guests_observed"],
            "predictive": {q: list(n["predictive"][q]) for q in ("q03", "q50", "q97")},
            "typical": {q: list(n["typical"][q]) for q in ("median", "lo", "hi")},
            "density": [_per_log(row, grid) for row in density[n["index"]]],
            "raw": [n["raw_median_by_guests"].get(str(g)) for g in guest_values],
        }
        for n in ordered
    ]
    return {
        "theme": theme,
        "tokens": tokens,
        "selected": initial,
        "guests": initial_guests,
        "guest_values": guest_values,
        "order_guests": ORDER_GUESTS,
        "sparse_below": SPARSE_BELOW,
        "grid": list(art.curves["grid"]),
        "city_median": list(art.neighborhoods["city"]["typical"]["median"]),
        "cells": cells,
    }


def _per_log(row: list, grid: list) -> list[float]:
    """Stored curves are per-dollar densities. On the log price axis the
    honest shape is density per log-dollar (pdf x price), whose peak sits at
    the median rather than the lower mode. Rescaled to peak 1 and rounded to 2 decimals, the precision
    a 44px-tall curve can show, to keep the payload small."""
    scaled = [0.0 if _missing(d) else d * x for d, x in zip(row, grid)]
    top = max(scaled) or 1.0
    out = [round(v / top, 2) for v in scaled]
    # Whole values (most of the tails are 0) serialise as "0", not "0.0".
    return [int(v) if v == int(v) else v for v in out]


# Formatting. Mirrored exactly by fmtDollars / fmtNum in the template script,
# so server-rendered and redrawn states read the same.


def _missing(value) -> bool:
    return value is None or (isinstance(value, float) and math.isnan(value))


def _dollars(value) -> str:
    """Whole dollars with thousands separators; an em dash when missing."""
    if _missing(value):
        return MISSING
    return f"${math.floor(value + 0.5):,}"


def _span(lo, hi) -> str:
    if _missing(lo) or _missing(hi):
        return MISSING
    return f"{_dollars(lo)} {EN_DASH} {_dollars(hi)}"


def _num(value: float) -> str:
    """One decimal, half-up (non-negative input)."""
    tenths = math.floor(value * 10 + 0.5)
    return f"{tenths // 10}.{tenths % 10}"


def _x_positions(grid: list) -> list[float]:
    lo, hi = math.log(grid[0]), math.log(grid[-1])
    return [(math.log(p) - lo) / (hi - lo) * WIDTH for p in grid]


def _curve_d(xs: list[float], dens: list) -> str:
    """Closed-at-the-baseline path: M, the 64 grid points, back to baseline.
    Same command structure for every curve so `d` transitions interpolate."""
    base = _num(HEIGHT)
    parts = [f"M{_num(xs[0])},{base}"]
    for x, d in zip(xs, dens):
        d = 0.0 if _missing(d) else min(max(d, 0.0), 1.0)
        parts.append(f"L{_num(x)},{_num(TOP + (1 - d) * (HEIGHT - TOP))}")
    parts.append(f"L{_num(xs[-1])},{base}")
    return " ".join(parts)


def _price_x(price, grid: list) -> str:
    if _missing(price):
        return _num(-10)
    lo, hi = math.log(grid[0]), math.log(grid[-1])
    x = (math.log(price) - lo) / (hi - lo) * WIDTH
    return _num(min(max(x, 0.0), WIDTH))


def _premium(value, city) -> tuple[str, bool]:
    """Typical price against the city's, as "+38%" or "−21%" (half-up)."""
    if _missing(value) or _missing(city) or not city:
        return MISSING, False
    pct = math.floor((value / city - 1) * 100 + 0.5)
    if pct > 0:
        return f"+{pct}%", True
    return (f"{MINUS}{-pct}%" if pct < 0 else "0%"), False


def _band(pred: dict, gi: int, grid: list) -> tuple[str, str]:
    """Clip rect (x, width) covering the single-listing 94% range."""
    lo = float(_price_x(pred["q03"][gi], grid))
    hi = float(_price_x(pred["q97"][gi], grid))
    if _missing(pred["q03"][gi]) or _missing(pred["q97"][gi]):
        lo, hi = 0.0, 0.0
    return _num(lo), _num(max(hi - lo, 0.0))


def _guests_label(g: int) -> str:
    return f"{g} guest" if g == 1 else f"{g} guests"


def _extrapolation_text(cell: dict) -> str:
    return (
        f"Beyond the largest {cell['name']} listing in the data "
        f"({cell['max_guests_observed']} guests): extrapolated."
    )


def _cells_html(payload: dict, g: int, selected: str) -> str:
    xs = _x_positions(payload["grid"])
    gi = payload["guest_values"].index(g)
    city_x = _price_x(payload["city_median"][gi], payload["grid"])
    city = payload["city_median"][gi]
    out = []
    for c in payload["cells"]:
        is_sel = c["name"] == selected
        beyond = g > c["max_guests_observed"]
        sparse = c["n_listings"] < payload["sparse_below"]
        name = html.escape(c["name"])
        classes = "cell beyond" if beyond else "cell"
        d = _curve_d(xs, c["density"][gi])
        band_x, band_w = _band(c["predictive"], gi, payload["grid"])
        raw = c["raw"][gi]
        raw_attr = "" if not _missing(raw) else " hidden"
        raw_x = _price_x(raw, payload["grid"]) if not _missing(raw) else "0.0"
        prem, up = _premium(c["typical"]["median"][gi], city)
        out.append(
            f'<button type="button" class="{classes}" '
            f'data-testid="specimen-cell-{c["index"]}" data-index="{c["index"]}" '
            f'data-selected="{"true" if is_sel else "false"}" '
            f'data-sparse="{"true" if sparse else "false"}" '
            f'aria-pressed="{"true" if is_sel else "false"}" title="{name}">'
            f'<span class="plot">'
            f'<svg viewBox="0 0 {WIDTH} {HEIGHT}" preserveAspectRatio="none" '
            f'aria-hidden="true" focusable="false">'
            f'<clipPath id="fill-{c["index"]}"><rect class="clip" x="{band_x}" '
            f'y="0" width="{band_w}" height="{HEIGHT}"/></clipPath>'
            f'<line class="city" x1="{city_x}" x2="{city_x}" y1="0" y2="{HEIGHT}"/>'
            f'<path class="fill" clip-path="url(#fill-{c["index"]})" d="{d}"/>'
            f'<path class="curve" data-testid="curve" d="{d}"/>'
            f"</svg>"
            f'<span class="raw" data-testid="raw-dot" style="left:{raw_x}%"'
            f"{raw_attr}></span>"
            f"</span>"
            f'<span class="nm">{name}</span>'
            f'<span class="row">'
            f'<span class="md">{_dollars(c["predictive"]["q50"][gi])}</span>'
            f'<span class="pc{" up" if up else ""}">{prem}</span>'
            f'<span class="n">n={c["n_listings"]}</span>'
            f"</span>"
            f"</button>"
        )
    return "\n".join(out)


def _ticks_html(guest_values: list, g: int) -> str:
    n = len(guest_values) - 1
    return "".join(
        f'<span class="{"on" if v == g else ""}" '
        f'style="left:{(i / n) * 100:.4f}%">{v}</span>'
        for i, v in enumerate(guest_values)
    )


def _seen_width(cell: dict, guest_values: list) -> str:
    lo, hi = guest_values[0], guest_values[-1]
    seen = min(max(cell["max_guests_observed"], lo), hi)
    return f"{(seen - lo) / (hi - lo) * 100:.4f}%"


def specimen_html(payload: dict) -> str:
    """Self-contained HTML document for the component iframe."""
    g = payload["guests"]
    gi = payload["guest_values"].index(g)
    selected = payload["selected"]
    cell = next(c for c in payload["cells"] if c["name"] == selected)
    pred, typ = cell["predictive"], cell["typical"]
    beyond = g > cell["max_guests_observed"]

    tokens_css = " ".join(f"--{k}: {v};" for k, v in payload["tokens"].items())
    options = "".join(
        f'<option value="{html.escape(n)}"{" selected" if n == selected else ""}>'
        f"{html.escape(n)}</option>"
        for n in sorted(c["name"] for c in payload["cells"])
    )
    data = json.dumps(payload, separators=(",", ":"), allow_nan=False)
    data = data.replace("</", "<\\/")

    replacements = {
        "__FONTS_URL__": html.escape(FONTS_URL),
        "__TOKENS__": tokens_css,
        "__SCHEME__": "dark" if payload["theme"] == "dark" else "light",
        "__NAME__": html.escape(selected),
        "__GUESTS_LABEL__": _guests_label(g),
        "__PRICE__": _dollars(pred["q50"][gi]),
        "__RANGE__": _span(pred["q03"][gi], pred["q97"][gi]),
        "__TYPICAL__": _span(typ["lo"][gi], typ["hi"][gi]),
        "__EXTRAP_ATTR__": "" if beyond else " hidden",
        "__EXTRAP_TEXT__": html.escape(_extrapolation_text(cell)) if beyond else "",
        "__OPTIONS__": options,
        "__GUEST_COUNT__": str(g),
        "__MIN__": str(payload["guest_values"][0]),
        "__MAX__": str(payload["guest_values"][-1]),
        "__SEEN__": _seen_width(cell, payload["guest_values"]),
        "__TICKS__": _ticks_html(payload["guest_values"], g),
        "__COUNT__": str(len(payload["cells"])),
        "__ORDER_GUESTS__": _guests_label(payload["order_guests"]),
        "__CELLS__": _cells_html(payload, g, selected),
        "__PAYLOAD__": data,
    }
    page = TEMPLATE_PATH.read_text(encoding="utf-8")
    for marker, value in replacements.items():
        page = page.replace(marker, value)
    return page


def render_specimen(art: Artifacts, theme: str, height: int = DEFAULT_HEIGHT) -> None:
    """Render the Live Specimen hero into the current Streamlit page."""
    components.html(
        specimen_html(specimen_payload(art, theme)), height=height, scrolling=False
    )

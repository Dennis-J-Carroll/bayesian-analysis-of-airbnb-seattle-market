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

# Cells keep one layout while the slider moves: cheapest to priciest typical
# price at this guest count.
ORDER_GUESTS = 2

# Curve box, in SVG user units. TOP leaves room so a peak is never clipped.
WIDTH, HEIGHT, TOP = 100, 44, 2

MISSING = "—"
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
        key=lambda n: (n["typical"]["median"][k], n["index"]),
    )
    density = art.curves["density"]
    cells = [
        {
            "name": n["name"],
            "index": n["index"],
            "n_listings": n["n_listings"],
            "max_guests_observed": n["max_guests_observed"],
            "predictive": {q: list(n["predictive"][q]) for q in ("q03", "q50", "q97")},
            "typical": {q: list(n["typical"][q]) for q in ("median", "lo", "hi")},
            "density": [list(row) for row in density[n["index"]]],
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
        "grid": list(art.curves["grid"]),
        "city_median": list(art.neighborhoods["city"]["typical"]["median"]),
        "cells": cells,
    }


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
    out = []
    for c in payload["cells"]:
        is_sel = c["name"] == selected
        beyond = g > c["max_guests_observed"]
        name = html.escape(c["name"])
        classes = "cell beyond" if beyond else "cell"
        out.append(
            f'<button type="button" class="{classes}" '
            f'data-testid="specimen-cell-{c["index"]}" data-index="{c["index"]}" '
            f'data-selected="{"true" if is_sel else "false"}" '
            f'aria-pressed="{"true" if is_sel else "false"}" title="{name}">'
            f'<svg viewBox="0 0 {WIDTH} {HEIGHT}" preserveAspectRatio="none" '
            f'aria-hidden="true" focusable="false">'
            f'<line class="city" x1="{city_x}" x2="{city_x}" y1="0" y2="{HEIGHT}"/>'
            f'<path class="curve" data-testid="curve" '
            f'd="{_curve_d(xs, c["density"][gi])}"/>'
            f"</svg>"
            f'<span class="nm">{name}</span>'
            f'<span class="md">{_dollars(c["predictive"]["q50"][gi])}</span>'
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


def render_specimen(art: Artifacts, theme: str, height: int = 980) -> None:
    """Render the Live Specimen hero into the current Streamlit page."""
    components.html(
        specimen_html(specimen_payload(art, theme)), height=height, scrolling=False
    )

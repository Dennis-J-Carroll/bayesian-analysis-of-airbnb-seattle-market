"""Data notes: where the data came from, every cleaning step with counts, what
the model cannot say, and a small descriptive CSV upload (never refit)."""

import html
from typing import BinaryIO

import pandas as pd
import streamlit as st

from dashboard.components.charts import price_histogram
from dashboard.components.readouts import Readout, render_readouts
from dashboard.theme import MONO_FONT, TOKENS
from dashboard.utils.artifacts import load_artifacts
from dashboard.utils.csv_handler import MAX_FILE_SIZE_MB
from dashboard.utils.data_loader import parse_price
from dashboard.utils.schema_detector import detect_mapping, load_column_aliases
from dashboard.utils.session_manager import AppState

CHART_CONFIG = {"displayModeBar": False}
SOURCE_URL = "http://insideairbnb.com/get-the-data/"
HIST_MAX = 1000  # price_histogram bins run from $0 to $1,000
DOLLAR = "&#36;"  # a bare dollar sign in markdown can start LaTeX


def summarize_upload(file: BinaryIO, filename: str) -> dict:
    """Describe an uploaded CSV: row count and the distribution of its prices.

    Never raises. Returns {"ok": True, "rows", "median_price", "prices",
    "warnings"} or {"ok": False, "error"}. Only the price column is used, and
    nothing here touches the fitted model.

    The strict `process_upload` validators are deliberately not applied: they
    demand room_type and numeric prices, which would reject the very listing
    exports (prices like "$1,234.00") this page is meant to describe. Column
    names are still matched through the shared schema detector.
    """
    try:
        file.seek(0, 2)
        size_mb = file.tell() / 1024 / 1024
        file.seek(0)
        if size_mb > MAX_FILE_SIZE_MB:
            return {
                "ok": False,
                "error": f"File is {size_mb:.1f} MB; the limit is {MAX_FILE_SIZE_MB} MB.",
            }
        df = detect_mapping(pd.read_csv(file))
        if "price" not in df.columns:
            names = ", ".join(load_column_aliases()["price"])
            return {
                "ok": False,
                "error": f"No price column found. Name one of: {names}.",
            }
        parsed = parse_price(df["price"])
        prices = parsed.dropna().reset_index(drop=True)
        if prices.empty:
            return {"ok": False, "error": "The price column has no readable prices."}
    except Exception as exc:  # any parse failure becomes a message, never a crash
        return {
            "ok": False,
            "error": f"Could not read {filename or 'this file'} as a CSV ({type(exc).__name__}).",
        }

    warnings = []
    unreadable = int(parsed.isna().sum())
    if unreadable:
        warnings.append(f"{unreadable} rows have no readable price and are left out.")
    outside = int(((prices < 0) | (prices > HIST_MAX)).sum())
    if outside:
        warnings.append(
            f"{outside} prices fall outside $0 to ${HIST_MAX:,} and are not drawn "
            "in the histogram (they still count toward the median)."
        )
    return {
        "ok": True,
        "rows": int(len(df)),
        "median_price": float(prices.median()),
        "prices": prices,
        "warnings": warnings,
    }


def _cleaning_rows(c: dict) -> list[tuple[str, str, str]]:
    """(step, removed, remaining) for each cleaning step, all from the artifact."""
    left = c["rows_raw"]
    rows = [("Raw listings in the file", "", f"{left:,}")]
    steps = [
        ("Missing price", c["missing_price"]),
        ("Missing guests or neighborhood", c["missing_other"]),
        (f"Price under {DOLLAR}10", c["below_min"]),
        (f"Price over {DOLLAR}1,000", c["above_max"]),
    ]
    for label, n in steps:
        left -= n
        rows.append((label, f"{n:,}", f"{left:,}"))
    assert left == c["rows_kept"], "cleaning steps must add up to rows_kept"
    return rows


def _table(theme: str) -> str:
    t = TOKENS[theme]
    c = load_artifacts().cleaning
    body = "".join(
        f"<tr><td>{label}</td><td class='n'>{removed}</td><td class='n'>{left}</td></tr>"
        for label, removed, left in _cleaning_rows(c)
    )
    css = (
        f".stMarkdown table.cl{{width:100%;border-collapse:collapse;font-family:{MONO_FONT};"
        f"font-size:13px;color:{t['ink']};font-variant-numeric:tabular-nums;border:0;}}"
        f".stMarkdown table.cl th{{text-align:left;font-weight:400;font-size:11px;letter-spacing:0.06em;"
        f"text-transform:uppercase;color:{t['muted']};border:0;border-bottom:1px solid {t['ink']};padding:6px 8px 6px 0;}}"
        f".stMarkdown table.cl td{{border:0;border-bottom:1px solid {t['rule']};padding:6px 8px 6px 0;}}"
        f".stMarkdown table.cl .n{{text-align:right;}}"
    )
    return (
        f"<style>{css}</style><table class='cl'><thead><tr><th>Step</th>"
        f"<th class='n'>Rows removed</th><th class='n'>Rows remaining</th></tr></thead>"
        f"<tbody>{body}</tbody></table>"
    )


def _upload_section(theme: str) -> None:
    st.subheader("Look at your own listings")
    st.markdown(
        "Upload a CSV with a price column to see its row count, median price and "
        "price histogram. This is descriptive only: the model is not refit on "
        "uploads, and nothing you upload is stored."
    )
    t = TOKENS[theme]
    st.markdown(
        "<style>"
        f'[data-testid="stFileUploaderDropzone"]{{background:{t["ground"]};'
        f'border:1px dashed {t["muted"]};border-radius:2px;color:{t["ink"]};}}'
        f'[data-testid="stFileUploaderDropzone"] *{{color:{t["ink"]};}}'
        f'[data-testid="stFileUploaderDropzone"] small{{color:{t["muted"]};}}'
        f'[data-testid="stFileUploaderDropzone"] button{{background:{t["ground"]};'
        f'border:1px solid {t["ink"]};border-radius:2px;}}'
        "</style>",
        unsafe_allow_html=True,
    )
    file = st.file_uploader("CSV file", type=["csv"], key="data_notes_upload")
    if file is None:
        return
    out = summarize_upload(file, file.name)
    if not out["ok"]:
        st.markdown(f"**Could not use this file.** {html.escape(out['error'])}")
        return
    render_readouts(
        [
            Readout("Rows", f"{out['rows']:,}", "In the uploaded file.", "up-rows"),
            Readout(
                "Median price",
                f"${out['median_price']:,.0f}",
                "Per night, from the readable prices.",
                "up-median",
            ),
        ],
        theme,
    )
    st.plotly_chart(
        price_histogram(out["prices"], theme, "Your uploaded nightly price"),
        use_container_width=True,
        config=CHART_CONFIG,
        key="upload_hist",
    )
    for w in out["warnings"]:
        st.caption(w.replace("$", "\\$"))


def render() -> None:
    art = load_artifacts()
    theme = AppState.theme()
    c = art.cleaning

    st.title("Data notes")
    st.caption(
        "Where the listings came from, what was removed and why, and what the "
        "model cannot tell you."
    )

    st.subheader("Source")
    st.markdown(
        f"Listings come from [Inside Airbnb]({SOURCE_URL}), scraped "
        f"{c['scraped_from']} to {c['scraped_to']} (Seattle), and are used under "
        "its CC BY 4.0 license. Inside Airbnb is an independent project and is "
        "not affiliated with Airbnb."
    )
    render_readouts(
        [
            Readout(
                "Listings scraped", f"{c['rows_raw']:,}", "Rows in the file.", "raw"
            ),
            Readout(
                "Listings modeled",
                f"{c['rows_kept']:,}",
                "After the cleaning steps below.",
                "kept",
            ),
        ],
        theme,
    )

    st.subheader("Cleaning, step by step")
    st.markdown(_table(theme), unsafe_allow_html=True)
    st.caption(
        "Rows with a listed price are kept only if the price is between "
        "\\$10 and \\$1,000, the range the model was fitted on."
    )

    st.subheader("What this cannot tell you")
    st.markdown(
        "- The price is the listed price, not booked price: it is what hosts "
        "ask, not what guests paid.\n"
        "- The data is one snapshot of about ten days in June 2025. It says "
        "nothing about other seasons, events or changes over time.\n"
        "- The guest count is the only listing feature in the model, besides "
        "the neighborhood. Bedrooms, room type, reviews and amenities are "
        "left out, so a typical price is not a price for any one listing.\n"
        f"- {c['above_max']:,} listings above \\$1,000 were removed, so the "
        "model says nothing about the luxury end. "
        f"{c['above_max_hotel_rooms']:,} of them are hotel-room listings and "
        f"{c['above_max_10k_plus']:,} are priced at \\$10,000 or more "
        "(\\$40,000 to \\$50,000 a night), which look like placeholders.\n"
        "- Neighborhoods with few listings have wide intervals; the model "
        "pulls them toward the city line rather than trusting a handful of "
        "prices.\n"
        "- Coverage checks use the same data the model was fitted on."
    )

    _upload_section(theme)

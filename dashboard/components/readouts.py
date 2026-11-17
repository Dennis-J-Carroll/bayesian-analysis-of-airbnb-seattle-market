"""Mono readouts on the Live Specimen look: tracked uppercase label, Archivo
display numeral, a hairline rule above. Shared by pages that need a row of
numbers; Streamlit's metric tiles are not used."""

import html
from dataclasses import dataclass

import streamlit as st

from dashboard.theme import DISPLAY_FONT, MONO_FONT, TOKENS

MISSING = "—"


@dataclass(frozen=True)
class Readout:
    label: str
    value: str
    sub: str = ""
    key: str = ""  # becomes a CSS class on the value, so tests and CSS can find it
    quiet: bool = False  # small mono value, for text such as "no listings at this size"


def readout_html(items: list[Readout], theme: str) -> str:
    """One self-contained HTML string (no blank lines, so Markdown leaves it alone)."""
    t = TOKENS[theme]
    css = (
        f".rd-row{{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));"
        f"gap:0 24px;margin:4px 0 12px;font-family:{MONO_FONT};}}"
        f".rd{{border-top:1px solid {t['ink']};padding:8px 0 4px;}}"
        f".rd-lab{{font-size:11px;letter-spacing:0.06em;text-transform:uppercase;color:{t['muted']};}}"
        f".rd-val{{font-family:{DISPLAY_FONT};font-weight:800;font-size:clamp(34px,5vw,56px);"
        f"line-height:1.05;letter-spacing:-0.02em;font-variant-numeric:tabular-nums;color:{t['ink']};}}"
        f".rd-val.quiet{{font-family:{MONO_FONT};font-weight:400;font-size:13px;line-height:1.3;"
        f"padding:12px 0 8px;letter-spacing:0;}}"
        f".rd-sub{{font-size:11px;font-variant-numeric:tabular-nums;color:{t['muted']};min-height:15px;}}"
    )
    cells = "".join(
        f'<div class="rd"><div class="rd-lab">{html.escape(r.label)}</div>'
        f'<div class="rd-val {html.escape(r.key)}{" quiet" if r.quiet else ""}">'
        f"{html.escape(r.value)}</div>"
        f'<div class="rd-sub">{html.escape(r.sub)}</div></div>'
        for r in items
    )
    return f'<style>{css}</style><div class="rd-row">{cells}</div>'


def render_readouts(items: list[Readout], theme: str) -> None:
    st.markdown(readout_html(items, theme), unsafe_allow_html=True)

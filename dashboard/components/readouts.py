"""Mono readouts on the Live Specimen look.

`readout_html` is a row of tracked uppercase labels over Archivo display
numerals, a hairline rule above each. `readout_line` folds a few numbers into
one mono line under an ink rule, for pages whose lead is a chart, not tiles.
Streamlit's metric tiles are not used."""

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


@dataclass(frozen=True)
class Fact:
    """One clause of a readout line: `before` VALUE `after`."""

    value: str
    before: str = ""
    after: str = ""
    key: str = ""  # CSS class on the value, so tests and CSS can find it


def readout_line_html(facts: list[Fact], theme: str) -> str:
    """One mono line of facts; values in ink, words in muted. A div, not a
    paragraph, so the prose measure does not wrap it early."""
    t = TOKENS[theme]
    css = (
        f".rl{{display:flex;flex-wrap:wrap;gap:4px 28px;margin:2px 0 4px;"
        f"padding-top:10px;border-top:1px solid {t['ink']};font-family:{MONO_FONT};"
        f"font-size:13px;line-height:1.5;color:{t['muted']};font-variant-numeric:tabular-nums;}}"
        f".rl b{{font-weight:600;color:{t['ink']};}}"
    )

    def clause(f: Fact) -> str:
        before = f"{html.escape(f.before)} " if f.before else ""
        after = f" {html.escape(f.after)}" if f.after else ""
        return (
            f'<span>{before}<b class="{html.escape(f.key)}">{html.escape(f.value)}</b>'
            f"{after}</span>"
        )

    return (
        f'<style>{css}</style><div class="rl">{"".join(clause(f) for f in facts)}</div>'
    )


def render_readout_line(facts: list[Fact], theme: str) -> None:
    st.markdown(readout_line_html(facts, theme), unsafe_allow_html=True)

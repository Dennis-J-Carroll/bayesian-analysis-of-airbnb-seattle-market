"""Tests for the Live Specimen theme tokens, app CSS and Plotly template."""

import re

import pytest

from dashboard.theme import FONTS_URL, TOKENS, css, plotly_template

THEMES = ["light", "dark"]
TOKEN_NAMES = {"ground", "ink", "accent", "muted", "rule"}


def test_tokens_have_both_themes_and_all_names():
    assert set(TOKENS) == {"light", "dark"}
    for theme in THEMES:
        assert set(TOKENS[theme]) == TOKEN_NAMES


def test_fonts_url_loads_archivo_and_jetbrains_mono():
    assert FONTS_URL.startswith("https://fonts.googleapis.com/")
    assert "Archivo:wght@400;800" in FONTS_URL
    assert "JetBrains+Mono:wght@400;600" in FONTS_URL


@pytest.mark.parametrize("theme", THEMES)
def test_css_never_targets_all_st_classes(theme):
    # This selector restyled Streamlit's icon font and broke every icon.
    assert '[class*="st-"]' not in css(theme)


@pytest.mark.parametrize("theme", THEMES)
def test_css_has_no_banned_effects(theme):
    text = css(theme).lower()
    assert "backdrop-filter" not in text
    assert "gradient" not in text
    for chunk in text.split("box-shadow")[1:]:
        value = chunk.split(";")[0].strip(" :")
        assert value.startswith("none"), f"box-shadow other than none: {value}"


@pytest.mark.parametrize("theme", THEMES)
def test_css_uses_tokens(theme):
    text = css(theme)
    for name, value in TOKENS[theme].items():
        assert value in text, f"{name} {value} missing from {theme} css"


@pytest.mark.parametrize("theme", THEMES)
def test_css_keeps_header_and_hides_footer(theme):
    # Hiding the header would also hide the sidebar toggle.
    text = css(theme)
    rules = re.findall(r"([^{}]+)\{([^{}]*)\}", text)
    hidden = [sel for sel, body in rules if re.search(r"display:\s*none", body)]
    assert any("footer" in sel for sel in hidden)
    assert any("stMainMenu" in sel for sel in hidden)
    assert not any("stHeader" in sel or "header" in sel.split(",") for sel in hidden)


@pytest.mark.parametrize("theme", THEMES)
def test_css_does_not_box_every_block(theme):
    # Streamlit 1.38 wraps every vertical block in this element, bordered or not.
    assert "stVerticalBlockBorderWrapper" not in css(theme)


@pytest.mark.parametrize("theme", THEMES)
def test_css_sets_ink_on_body_text_and_header_controls(theme):
    # config.toml is light; without these, dark text and icons are ink on ink.
    rules = re.findall(r"([^{}]+)\{([^{}]*)\}", css(theme))
    ink = TOKENS[theme]["ink"]
    inked = " ".join(sel for sel, body in rules if f"color: {ink}" in body)
    for selector in ("p", ".stMarkdown", '[data-testid="stHeader"] button'):
        assert selector in inked, selector


def test_dark_tokens_differ():
    assert TOKENS["dark"]["ground"] != TOKENS["light"]["ground"]
    assert TOKENS["dark"]["ink"] != TOKENS["light"]["ink"]


@pytest.mark.parametrize("theme", THEMES)
def test_plotly_template_fonts_and_ground(theme):
    layout = plotly_template(theme).layout
    ground = TOKENS[theme]["ground"]
    assert layout.paper_bgcolor == ground
    assert layout.plot_bgcolor == ground
    assert layout.font.family.startswith("JetBrains Mono")
    assert layout.xaxis.gridcolor == TOKENS[theme]["rule"]
    assert list(layout.colorway) == [TOKENS[theme]["ink"], TOKENS[theme]["muted"]]

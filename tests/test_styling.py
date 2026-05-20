# tests/test_styling.py
import pytest
from pathlib import Path
from dashboard.utils.styling import (
    load_theme_config,
    get_chart_template,
    get_chart_palette,
)


def test_load_theme_config_returns_dict():
    """load_theme_config() returns theme dict."""
    theme = load_theme_config("modern_neutral")
    assert isinstance(theme, dict)
    assert "colors" in theme
    assert "chart" in theme


def test_modern_neutral_theme_structure():
    """Modern Neutral has required structure."""
    theme = load_theme_config("modern_neutral")
    assert theme["is_dark"] == False
    assert theme["colors"]["bg_primary"] == "#ffffff"
    assert theme["colors"]["accent"] == "#77b899"
    assert theme["chart"]["template"] == "plotly_white"
    assert isinstance(theme["chart"]["palette"], list)


def test_deep_forest_theme_structure():
    """Deep Forest has required structure."""
    theme = load_theme_config("deep_forest")
    assert theme["is_dark"] == True
    assert theme["colors"]["bg_primary"] == "#1a1a2e"
    assert theme["chart"]["template"] == "plotly_dark"


def test_get_chart_template():
    """get_chart_template() returns correct template."""
    assert get_chart_template("modern_neutral") == "plotly_white"
    assert get_chart_template("deep_forest") == "plotly_dark"


def test_get_chart_palette():
    """get_chart_palette() returns color list."""
    palette = get_chart_palette("modern_neutral")
    assert isinstance(palette, list)
    assert len(palette) == 5
    assert palette[0] == "#77b899"  # Sage green first

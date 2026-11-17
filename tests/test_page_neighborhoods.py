"""Neighborhoods page, run through Streamlit's AppTest."""

import re

import pytest
from streamlit.testing.v1 import AppTest

from dashboard.utils.artifacts import load_artifacts, neighborhood_by_name


def _page():
    from dashboard.pages import neighborhoods
    from dashboard.theme import apply_theme
    from dashboard.utils.session_manager import AppState

    AppState.init()
    apply_theme(AppState.theme())
    neighborhoods.render()


def _run(name="Broadway", guests=2, theme="light"):
    at = AppTest.from_function(_page, default_timeout=60)
    at.session_state["theme"] = theme
    at.run()
    assert not at.exception, at.exception
    if name != "Broadway":
        at.selectbox[0].select(name).run()
    if guests != 2:
        at.slider[0].set_value(guests).run()
    assert not at.exception, at.exception
    return at


def _text(at):
    return " ".join(m.value for m in at.markdown) + " ".join(
        c.value for c in at.caption
    )


@pytest.mark.parametrize("theme", ["light", "dark"])
def test_default_renders(theme):
    at = _run(theme=theme)
    assert at.selectbox[0].value == "Broadway"
    assert at.slider[0].value == 2


def test_broadway_readouts():
    at = _run()
    text = _text(at)
    assert ">359<" in text
    art = load_artifacts()
    typical = neighborhood_by_name(art, "Broadway")["typical"]["median"][1]
    shown = int(re.search(r"typical-price\">\$(\d+)<", text).group(1))
    assert abs(shown - 164) <= 4
    assert abs(shown - typical) <= 1
    assert re.search(r"\d\.\d\dx", text)
    assert "nan" not in text.lower().replace("neighborhood", "")


def test_premium_is_ratio_to_city():
    at = _run()
    art = load_artifacts()
    broadway = neighborhood_by_name(art, "Broadway")["typical"]["median"][1]
    city = art.neighborhoods["city"]["typical"]["median"][1]
    assert f"{broadway / city:.2f}x" in _text(at)


def test_sparse_neighborhood_has_no_nan():
    at = _run("Industrial District")
    text = _text(at)
    assert ">1<" in text
    assert "no listings at this size" in text
    assert "nan" not in text.lower().replace("neighborhood", "")
    assert "None" not in text


def test_shrinkage_caption_formats_holly_park_from_artifacts():
    at = _run()
    art = load_artifacts()
    holly = neighborhood_by_name(art, "Holly Park")
    caption = " ".join(c.value for c in at.caption) + " ".join(
        m.value for m in at.markdown
    )
    caption = caption.replace("\\$", "$")
    assert "Holly Park" in caption
    assert f"{holly['n_listings']} listings" in caption
    assert f"${holly['raw_median_by_guests']['2']:,.0f}" in caption
    assert f"${holly['typical']['median'][1]:,.0f}" in caption
    omitted = sum(
        1
        for n in art.neighborhoods["neighborhoods"]
        if n["raw_median_by_guests"].get("2") is None
    )
    assert f"{omitted} neighborhoods" in caption


def test_holly_park_without_raw_median_omits_raw_number():
    at = _run(guests=3)
    art = load_artifacts()
    holly = neighborhood_by_name(art, "Holly Park")
    assert holly["raw_median_by_guests"]["3"] is None
    text = _text(at)
    assert "Holly Park" in text
    assert "None" not in text and "nan" not in text.lower().replace("neighborhood", "")

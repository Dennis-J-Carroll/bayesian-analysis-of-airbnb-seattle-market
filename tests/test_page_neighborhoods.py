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


def test_lead_is_the_selected_curve_not_a_tile_row():
    at = _run()
    text = _text(at)
    assert "rd-row" not in text  # no KPI tile row
    first = at.get("plotly_chart")[0]
    import json as _json

    fig = _json.loads(first.proto.spec)
    names = [t.get("name") for t in fig["data"]]
    assert {"curve", "band", "listings", "raw median"} <= set(names)


def test_readout_line_carries_listings_median_and_ratio_from_artifacts():
    at = _run(guests=4)
    art = load_artifacts()
    b = neighborhood_by_name(art, "Broadway")
    city = art.neighborhoods["city"]["typical"]["median"][3]
    text = _text(at)
    assert f">{b['n_listings']}<" in text
    assert f"raw-median\">${b['raw_median_by_guests']['4']:,.0f}<" in text
    assert f"{b['typical']['median'][3] / city:.2f}x" in text
    lo, hi = b["predictive"]["q03"][3], b["predictive"]["q97"][3]
    assert f"${lo:,.0f}" in text and f"${hi:,.0f}" in text


@pytest.mark.parametrize("guests", [2, 7, 16])
def test_guest_control_has_specimen_readout_and_tick_row(guests):
    at = _run(guests=guests)
    text = " ".join(m.value for m in at.markdown)
    assert f'class="g-out">{guests}<' in text  # large readout of the value
    ticks = re.findall(
        r'<span( class="on")? style="left:[\d.]+%(?:;transform:[^"]+)?">(\d+)</span>',
        text,
    )
    assert [int(v) for _, v in ticks] == list(range(1, 17))
    assert [int(v) for on, v in ticks if on] == [guests]  # only the current one
    assert at.slider[0].value == guests


def test_guest_control_styling_is_scoped_to_this_slider():
    at = _run()
    text = " ".join(m.value for m in at.markdown)
    # Hiding the stock value and end labels must touch only this slider.
    hidden = [
        sel
        for sel, body in re.findall(r"([^{}]+)\{([^{}]*)\}", text)
        if "display:none" in body.replace(" ", "") and "stSlider" in sel
    ]
    assert hidden
    for sel in hidden:
        parts = [x for x in sel.split(",") if "stSlider" in x]
        assert all(".st-key-nbhd_guests" in x for x in parts), sel
    from dashboard.theme import TOKENS

    head = text[text.index("g-head") :]
    assert TOKENS["light"]["accent"] not in head.split("</div>")[0]


def test_last_guest_tick_is_right_aligned_not_centred():
    from dashboard.pages.neighborhoods import _guest_ticks_html

    html = _guest_ticks_html(2)
    last = html.split("<span")[-1]
    assert "translateX(-100%)" in last and last.endswith(">16</span></div>")
    assert html.count("translateX(-100%)") == 1


def test_shrinkage_caption_mentions_slope_borrowing():
    caption = " ".join(c.value for c in _run().caption)
    assert "pulled mostly toward the citywide line" in caption
    assert "slope also borrows from the neighborhood's other listing sizes" in caption

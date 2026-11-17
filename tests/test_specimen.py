"""Tests for the Live Specimen hero component (payload and rendered HTML)."""

import re
from urllib.parse import urlparse

import pytest

from dashboard.components.specimen import specimen_html, specimen_payload
from dashboard.theme import TOKENS
from dashboard.utils.artifacts import ARTIFACT_DIR, load_artifacts, neighborhood_by_name

HOOKS = [
    "specimen-select",
    "specimen-slider",
    "specimen-guests",
    "specimen-price",
    "specimen-range",
    "specimen-typical",
    "specimen-extrapolation",
]


@pytest.fixture(scope="module")
def art():
    return load_artifacts(ARTIFACT_DIR)


@pytest.fixture(scope="module")
def light_html(art):
    return specimen_html(specimen_payload(art, "light"))


def _text(html: str, testid: str) -> str:
    match = re.search(rf'data-testid="{testid}"[^>]*>([^<]*)<', html)
    assert match, f"no element with data-testid={testid}"
    return match.group(1).strip()


def _dollars(value: float) -> str:
    return f"${int(value + 0.5):,}"


def test_payload_has_all_neighborhoods_in_fixed_order(art):
    payload = specimen_payload(art, "light")
    cells = payload["cells"]
    assert len(cells) == 88
    assert {c["index"] for c in cells} == set(range(88))
    at_two = [c["typical"]["median"][1] for c in cells]
    assert at_two == sorted(at_two)
    assert payload["selected"] == "Broadway"
    assert payload["guests"] == 2


def test_payload_order_does_not_depend_on_initial_guests(art):
    a = [c["index"] for c in specimen_payload(art, "light")["cells"]]
    b = [c["index"] for c in specimen_payload(art, "light", "Fremont", 9)["cells"]]
    assert a == b


def test_payload_marks_extrapolation_limits(art):
    cells = specimen_payload(art, "light")["cells"]
    assert all("max_guests_observed" in c for c in cells)
    holly = next(c for c in cells if c["name"] == "Holly Park")
    assert holly["max_guests_observed"] == 4


def test_payload_rejects_unknown_inputs(art):
    with pytest.raises(KeyError):
        specimen_payload(art, "sepia")
    with pytest.raises(KeyError):
        specimen_payload(art, "light", "Atlantis")
    with pytest.raises(ValueError):
        specimen_payload(art, "light", "Broadway", 17)


def test_html_is_self_contained(light_html):
    assert "<script src=" not in light_html
    hosts = {
        urlparse(u).netloc for u in re.findall(r"https?://[^\s\"'()<>]+", light_html)
    }
    assert hosts <= {"fonts.googleapis.com", "fonts.gstatic.com"}


def test_html_contains_testids(light_html):
    for hook in HOOKS:
        assert f'data-testid="{hook}"' in light_html, hook
    for index in range(88):
        assert f'data-testid="specimen-cell-{index}"' in light_html
    assert light_html.count('data-testid="curve"') == 88
    assert len(re.findall(r'<button[^>]*data-selected="true"', light_html)) == 1
    assert re.search(r'<select[^>]*data-testid="specimen-select"', light_html)
    assert re.search(
        r'<input[^>]*type="range"[^>]*min="1"[^>]*max="16"[^>]*data-testid="specimen-slider"',
        light_html,
    )


def test_select_lists_names_alphabetically(art, light_html):
    select = re.search(r'data-testid="specimen-select".*?</select>', light_html, re.S)
    names = re.findall(r"<option[^>]*>([^<]*)</option>", select.group(0))
    expected = sorted(n["name"] for n in art.neighborhoods["neighborhoods"])
    assert names == expected


def test_selected_cell_is_broadway(art, light_html):
    broadway = neighborhood_by_name(art, "Broadway")["index"]
    assert re.search(
        rf'data-testid="specimen-cell-{broadway}"[^>]*data-selected="true"', light_html
    )


def test_html_dark_uses_dark_tokens(art):
    html = specimen_html(specimen_payload(art, "dark"))
    assert f"--ground: {TOKENS['dark']['ground']}" in html
    assert TOKENS["dark"]["ground"] == "#111111"
    assert "#FBFBFA" not in html.upper()


def test_html_has_no_emoji(light_html):
    for ch in light_html:
        cp = ord(ch)
        assert not (0x1F000 <= cp <= 0x1FAFF or 0x2600 <= cp <= 0x27BF), hex(cp)


def test_initial_readout_values(art, light_html):
    broadway = neighborhood_by_name(art, "Broadway")
    pred = broadway["predictive"]
    typ = broadway["typical"]
    price = int(_text(light_html, "specimen-price").lstrip("$").replace(",", ""))
    assert abs(price - 164) <= 4
    assert _text(light_html, "specimen-price") == _dollars(pred["q50"][1])
    assert _text(light_html, "specimen-guests") == "2"
    rng = _text(light_html, "specimen-range")
    assert rng == f"{_dollars(pred['q03'][1])} – {_dollars(pred['q97'][1])}"
    assert _text(light_html, "specimen-typical") == (
        f"{_dollars(typ['lo'][1])} – {_dollars(typ['hi'][1])}"
    )
    assert re.search(r'data-testid="specimen-extrapolation"[^>]*hidden', light_html)


def test_initial_paths_are_server_rendered(art, light_html):
    paths = re.findall(r'<path[^>]*data-testid="curve"[^>]*d="([^"]+)"', light_html)
    paths += re.findall(r'<path[^>]*d="([^"]+)"[^>]*data-testid="curve"', light_html)
    assert len(paths) == 88
    for d in paths:
        assert d.startswith("M")
        assert d.count("L") == 65  # M, 64 grid points, back to the baseline


def test_extrapolation_note_rendered_when_beyond_data(art):
    html = specimen_html(specimen_payload(art, "light", "Holly Park", 16))
    assert _text(html, "specimen-extrapolation") == (
        "Beyond the largest Holly Park listing in the data (4 guests): extrapolated."
    )
    assert not re.search(r'data-testid="specimen-extrapolation"[^>]*hidden', html)


def test_missing_value_renders_em_dash(art):
    payload = specimen_payload(art, "light")
    cell = next(c for c in payload["cells"] if c["name"] == "Broadway")
    cell["predictive"] = {
        k: [None] * 16 if k == "q50" else v for k, v in cell["predictive"].items()
    }
    html = specimen_html(payload)
    assert _text(html, "specimen-price") == "—"
    markup = html.split("<body>")[1].split("<script")[0]
    assert "NaN" not in markup and "None" not in markup
    broadway = neighborhood_by_name(art, "Broadway")["index"]
    cell_html = re.search(
        rf'data-testid="specimen-cell-{broadway}".*?</button>', markup, re.S
    ).group(0)
    assert '<span class="md">—</span>' in cell_html

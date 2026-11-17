"""Data notes page and its descriptive upload helper."""

import io
import re

import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest

from dashboard.utils.artifacts import load_artifacts

FIXTURE = "tests/fixtures/listings_small.csv"


def _page():
    from dashboard.pages import data_notes
    from dashboard.theme import apply_theme
    from dashboard.utils.session_manager import AppState

    AppState.init()
    apply_theme(AppState.theme())
    data_notes.render()


def _run(theme="light"):
    at = AppTest.from_function(_page, default_timeout=60)
    at.session_state["theme"] = theme
    at.run()
    assert not at.exception, at.exception
    return at


def _text(at):
    return " ".join(m.value for m in at.markdown) + " ".join(
        c.value for c in at.caption
    )


@pytest.mark.parametrize("theme", ["light", "dark"])
def test_renders(theme):
    _run(theme)


def test_source_and_dates():
    text = _text(_run())
    assert "Inside Airbnb" in text
    assert "http://insideairbnb.com/get-the-data/" in text
    assert "CC BY 4.0" in text
    assert "2025-06-21" in text and "2025-06-30" in text


def test_cleaning_table_matches_artifact():
    c = load_artifacts().cleaning
    text = _text(_run())
    for n in (c["rows_raw"], c["missing_price"], c["above_max"], c["rows_kept"]):
        assert f"{n:,}" in text
    after_price = c["rows_raw"] - c["missing_price"] - c["missing_other"]
    assert f"{after_price:,}" in text
    assert "6,862" in text and "635" in text and "6,227" in text
    assert "83" in text and "6,144" in text


def test_limitations_and_no_refit_statement():
    text = _text(_run())
    assert "listed price, not booked price" in text
    assert "guest count is the only listing feature in the model" in text
    assert "not refit" in text


def test_no_unescaped_dollar_pairs_in_prose():
    at = _run()
    for el in list(at.markdown) + list(at.caption):
        if "<style>" in el.value:
            continue
        assert len(re.findall(r"(?<!\\)\$", el.value)) < 2, el.value


def _summarize(content, name="x.csv"):
    from dashboard.pages.data_notes import summarize_upload

    raw = content if isinstance(content, bytes) else content.encode()
    return summarize_upload(io.BytesIO(raw), name)


def test_upload_dollar_strings_give_numeric_median():
    csv = 'price,accommodates\n"$1,234.00",2\n$100.00,2\n$300.00,3\n'
    out = _summarize(csv)
    assert out["ok"] is True
    assert out["rows"] == 3
    assert out["median_price"] == 300.0
    assert isinstance(out["prices"], pd.Series)
    assert out["prices"].dtype == float


def test_upload_fixture_file():
    with open(FIXTURE, "rb") as f:
        out = _summarize(f.read())
    assert out["ok"] is True
    assert out["rows"] == 10
    assert out["prices"].notna().all()
    assert len(out["prices"]) == 9  # one row has no price
    assert any("price" in w for w in out["warnings"])


def test_upload_without_price_column_is_an_error():
    out = _summarize("accommodates,neighbourhood_cleansed\n2,A\n3,B\n")
    assert out["ok"] is False
    assert isinstance(out["error"], str) and out["error"]


def test_upload_random_bytes_never_raise():
    out = _summarize(bytes(range(256)) * 8)
    assert out["ok"] is False
    assert out["error"]


def test_upload_empty_and_all_unparseable_prices():
    assert _summarize("")["ok"] is False
    assert _summarize("price\nabc\ndef\n")["ok"] is False

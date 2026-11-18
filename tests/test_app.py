"""App shell and Predict page, run through Streamlit's AppTest."""

import re

import pytest
from streamlit.testing.v1 import AppTest

import app
from dashboard.pages import predict

EMOJI = re.compile("[\U0001f000-\U0001faff☀-➿←-⇿⬀-⯿]")


def _predict_page():
    from dashboard.pages import predict
    from dashboard.theme import apply_theme
    from dashboard.utils.session_manager import AppState

    AppState.init()
    apply_theme(AppState.theme())
    predict.render()


@pytest.mark.parametrize("theme", ["light", "dark"])
def test_app_runs_without_exception(theme):
    at = AppTest.from_function(_predict_page, default_timeout=60)
    at.session_state["theme"] = theme
    at.run()
    assert not at.exception, at.exception


@pytest.mark.parametrize("theme", ["light", "dark"])
def test_shell_runs_without_exception(theme):
    at = AppTest.from_file("app.py", default_timeout=60)
    at.session_state["theme"] = theme
    at.run()
    assert not at.exception, at.exception
    assert any("Predict a nightly price" in t.value for t in at.title)


def test_dark_toggle_sets_theme():
    at = AppTest.from_file("app.py", default_timeout=60).run()
    assert at.session_state["theme"] == "light"
    at.sidebar.toggle[0].set_value(True).run()
    assert not at.exception, at.exception
    assert at.session_state["theme"] == "dark"


def test_nav_titles_have_no_emoji_and_match_pages():
    titles = [t for t, _, _ in app.PAGES]
    assert titles == [
        "Predict",
        "Neighborhoods",
        "How the model works",
        "Diagnostics",
        "Data notes",
    ]
    assert [p for _, p, _ in app.PAGES] == [
        "predict",
        "neighborhoods",
        "model",
        "diagnostics",
        "data-notes",
    ]
    for title, path, fn in app.PAGES:
        assert not EMOJI.search(title), title
        assert callable(fn)
    assert app.PAGES[0][2] is predict.render


@pytest.mark.parametrize("name", [t for t, _, _ in app.PAGES])
def test_every_page_renders_without_exception(name):
    at = AppTest.from_function(_run_page, args=(name,), default_timeout=60).run()
    assert not at.exception, at.exception


def _run_page(name):
    import app

    from dashboard.theme import apply_theme
    from dashboard.utils.session_manager import AppState

    AppState.init()
    apply_theme(AppState.theme())
    dict((t, fn) for t, _, fn in app.PAGES)[name]()


def test_predict_page_renders_component_and_explainer():
    at = AppTest.from_function(_predict_page, default_timeout=60).run()
    assert not at.exception, at.exception
    assert any("Predict a nightly price" in t.value for t in at.title)
    text = " ".join(m.value for m in at.markdown).lower()
    assert "what you're looking at" in text
    assert "how the model works" in text
    assert "partial pooling" in text
    # Counts come from the artifacts: 4 chains x 2,000 draws, 1,000-draw sample.
    assert "8,000" in text and "1,000" in text
    assert (
        "computed from a seeded 1,000-draw sample of the 8,000 posterior draws" in text
    )


def _named_page(module_name):
    import importlib

    from dashboard.theme import apply_theme
    from dashboard.utils.session_manager import AppState

    AppState.init()
    apply_theme(AppState.theme())
    importlib.import_module(f"dashboard.pages.{module_name}").render()


@pytest.mark.parametrize("module_name", ["neighborhoods", "model", "diagnostics"])
def test_plotly_charts_keep_their_own_template(module_name):
    # theme="streamlit" overrides plotly_template (gray #808495 axis titles).
    at = AppTest.from_function(_named_page, args=(module_name,), default_timeout=60)
    at.run()
    assert not at.exception, at.exception
    charts = at.get("plotly_chart")
    assert charts, module_name
    assert all(c.proto.theme == "" for c in charts), [c.proto.theme for c in charts]


def test_every_plotly_chart_call_passes_theme_none():
    # Covers charts AppTest cannot reach, such as the upload histogram.
    from pathlib import Path

    pages = Path(__file__).resolve().parents[1] / "dashboard" / "pages"
    for path in pages.glob("*.py"):
        text = path.read_text()
        calls = text.split("st.plotly_chart(")[1:]
        for call in calls:
            depth, end = 1, 0
            for end, ch in enumerate(call):
                depth += {"(": 1, ")": -1}.get(ch, 0)
                if depth == 0:
                    break
            assert "theme=None" in call[:end], f"{path.name}: {call[:end]}"

"""Browser end-to-end tests: the real app in Chromium, as a visitor sees it."""

import re
import time

import pytest

from dashboard.components.specimen import specimen_html, specimen_payload
from dashboard.theme import TOKENS
from dashboard.utils.artifacts import ARTIFACT_DIR, load_artifacts

pytestmark = pytest.mark.e2e

ROUTES = ["/", "/neighborhoods", "/model", "/diagnostics", "/data-notes"]
FRAME = "iframe[title='st.iframe'], iframe"
EMOJI = re.compile(
    "[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F000-\U0001F2FF"
    "\U00002B00-\U00002BFF\U0000FE0F\U0000200D]"
)

READOUTS = """() => {
  const t = id => document.querySelector(`[data-testid="${id}"]`);
  const note = t('specimen-extrapolation');
  return {
    price: t('specimen-price').textContent,
    range: t('specimen-range').textContent,
    typical: t('specimen-typical').textContent,
    guests: t('specimen-guests').textContent,
    note: note.textContent, noteHidden: note.hidden,
    select: t('specimen-select').value, slider: t('specimen-slider').value,
    cells: [...document.querySelectorAll('.cell')].map(el => [
      el.getAttribute('data-index'), el.getAttribute('data-selected'),
      el.querySelector('.curve').getAttribute('d'),
      el.querySelector('.md').textContent, el.querySelector('.pc').textContent]),
  };
}"""


@pytest.fixture()
def page(browser, app_url):
    ctx = browser.new_context(viewport={"width": 1440, "height": 900})
    pg = ctx.new_page()
    pg.errors = []
    pg.bad_responses = []
    pg.on("console", lambda m: m.type == "error" and pg.errors.append(m.text))
    pg.on("pageerror", lambda e: pg.errors.append(str(e)))
    pg.on(
        "response",
        lambda r: r.status >= 400 and pg.bad_responses.append((r.status, r.url)),
    )
    try:
        yield pg
    finally:
        ctx.close()


def open_specimen(page, app_url, path="/"):
    page.goto(app_url + path)
    page.wait_for_selector(FRAME, timeout=30000)
    frame = page.frame_locator(FRAME).first
    frame.locator("[data-testid=specimen-slider]").wait_for(timeout=30000)
    return frame


def set_slider(frame, value):
    frame.locator("[data-testid=specimen-slider]").fill(str(value))


def curves(frame):
    return frame.locator("[data-testid=curve]").evaluate_all(
        "els => els.map(e => e.getAttribute('d'))"
    )


def test_slider_moves_every_curve(page, app_url):
    frame = open_specimen(page, app_url)
    before = curves(frame)
    price_before = frame.locator("[data-testid=specimen-price]").inner_text()
    assert len(before) == 88
    set_slider(frame, 6)
    after = curves(frame)
    assert len(after) == len(before)
    assert all(a != b for a, b in zip(after, before)), "a curve did not move"
    assert frame.locator("[data-testid=specimen-guests]").inner_text().strip() == "6"
    assert frame.locator("[data-testid=specimen-price]").inner_text() != price_before


def test_select_and_click_change_selection(page, app_url):
    frame = open_specimen(page, app_url)
    frame.locator("[data-testid=specimen-select]").select_option("Fremont")
    selected = frame.locator("[data-testid^=specimen-cell-][data-selected=true]")
    assert selected.count() == 1
    fremont_idx = selected.get_attribute("data-index")
    other = frame.locator(
        f"[data-testid^=specimen-cell-]:not([data-index='{fremont_idx}'])"
    ).first
    other_idx = other.get_attribute("data-index")
    other.click()
    selected = frame.locator("[data-testid^=specimen-cell-][data-selected=true]")
    assert selected.count() == 1
    assert selected.get_attribute("data-index") == other_idx
    assert frame.locator("[data-testid=specimen-select]").input_value() != "Fremont"


def test_extrapolation_note(page, app_url):
    frame = open_specimen(page, app_url)
    note = frame.locator("[data-testid=specimen-extrapolation]")
    frame.locator("[data-testid=specimen-select]").select_option("Holly Park")
    set_slider(frame, 16)
    assert note.is_visible()
    set_slider(frame, 2)
    assert note.is_hidden()


@pytest.mark.parametrize("path", ROUTES)
def test_pages_load_without_errors(page, app_url, path):
    page.goto(app_url + path)
    page.wait_for_selector("h1", timeout=30000)
    page.wait_for_timeout(1500)
    assert page.locator("[data-testid=stException]").count() == 0
    # On a deep link the Streamlit frontend probes "<page>/_stcore/..." as a
    # possible base path before falling back to "/": expected 404s, and the
    # browser logs each as a generic "Failed to load resource" console error.
    probes = {
        (404, f"{app_url}{path}/_stcore/{name}")
        for name in ("health", "host-config")
        if path != "/"
    }
    assert set(page.bad_responses) <= probes, page.bad_responses
    generic = "Failed to load resource: the server responded with a status of 404"
    real_errors = [e for e in page.errors if not e.startswith(generic)]
    assert real_errors == []
    assert len(page.errors) - len(real_errors) <= len(page.bad_responses)
    assert page.get_by_text("Page not found").count() == 0


@pytest.mark.parametrize("path", ROUTES)
def test_no_emoji_in_rendered_text(page, app_url, path):
    page.goto(app_url + path)
    page.wait_for_selector("h1", timeout=30000)
    page.wait_for_timeout(1000)
    text = page.inner_text("body")
    assert not EMOJI.findall(text)
    if path == "/":
        frame = page.frame_locator(FRAME).first
        assert not EMOJI.findall(frame.locator("body").inner_text())


def test_phone_width_no_horizontal_scroll(browser, app_url):
    ctx = browser.new_context(viewport={"width": 390, "height": 844})
    try:
        pg = ctx.new_page()
        frame = open_specimen(pg, app_url)
        assert pg.evaluate("document.documentElement.scrollWidth") <= 390
        slider = frame.locator("[data-testid=specimen-slider]")
        assert slider.is_visible()
        before = slider.input_value()
        box = slider.bounding_box()
        pg.mouse.move(box["x"] + 4, box["y"] + box["height"] / 2)
        pg.mouse.down()
        pg.mouse.move(box["x"] + box["width"] - 4, box["y"] + box["height"] / 2)
        pg.mouse.up()
        assert slider.input_value() != before, "slider did not drag"
    finally:
        ctx.close()


@pytest.mark.xfail(strict=True, reason="phone grid clipped — see task-11-report")
def test_phone_grid_bottom_is_reachable(browser, app_url):
    ctx = browser.new_context(viewport={"width": 390, "height": 844})
    try:
        pg = ctx.new_page()
        frame = open_specimen(pg, app_url)
        frame.locator("[data-testid^=specimen-cell-]").last.wait_for()
        # The iframe has a fixed height and no page-level scroll for its
        # content, so the last cell must end inside the frame's viewport.
        gap = frame.locator("[data-testid^=specimen-cell-]").last.evaluate(
            "el => window.innerHeight - el.getBoundingClientRect().bottom"
        )
        assert gap >= 0, f"last cell is clipped by {-gap:.0f}px"
    finally:
        ctx.close()


def test_dark_toggle_switches_component(page, app_url):
    frame = open_specimen(page, app_url)

    def ground():
        return (
            page.frame_locator(FRAME)
            .first.locator("body")
            .evaluate("el => getComputedStyle(el).backgroundColor")
        )

    def rgb(hex_):
        h = hex_.lstrip("#")
        return "rgb(%d, %d, %d)" % tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))

    assert ground() == rgb(TOKENS["light"]["ground"])
    page.get_by_text("Dark", exact=True).click()
    deadline = time.monotonic() + 20
    seen = None
    while time.monotonic() < deadline:
        try:
            seen = ground()
        except Exception:  # iframe is replaced while the app reruns
            seen = None
        if seen == rgb(TOKENS["dark"]["ground"]):
            break
        page.wait_for_timeout(250)
    assert seen == rgb(TOKENS["dark"]["ground"])


@pytest.mark.xfail(
    strict=True,
    reason="Streamlit 1.38 sends page_not_found to the first session of a fresh "
    "server (PagesManager starts on the V1 strategy) — see task-11-report",
)
def test_cold_deep_link_has_no_page_not_found(browser, cold_app_url):
    ctx = browser.new_context(viewport={"width": 1440, "height": 900})
    try:
        pg = ctx.new_page()
        pg.goto(cold_app_url + "/model")
        pg.wait_for_selector("h1", timeout=30000)
        pg.wait_for_timeout(2000)
        assert pg.get_by_text("Page not found").count() == 0
        assert pg.locator("[role=dialog]").count() == 0
        assert pg.locator("h1").first.inner_text().strip() != ""
    finally:
        ctx.close()


@pytest.fixture(scope="module")
def artifacts():
    return load_artifacts(ARTIFACT_DIR)


@pytest.mark.parametrize(
    "name,guests",
    [
        (n, g)
        for n in ("Broadway", "Holly Park", "Industrial District")
        for g in (1, 5, 16)
    ],
)
def test_js_matches_python_render(browser, artifacts, name, guests):
    """Redrawing in the browser must equal the server-side render of that state."""
    ctx = browser.new_context()
    try:
        live, ref = ctx.new_page(), ctx.new_page()
        live.set_content(specimen_html(specimen_payload(artifacts, "light")))
        live.select_option("[data-testid=specimen-select]", name)
        live.fill("[data-testid=specimen-slider]", str(guests))
        ref.set_content(
            specimen_html(specimen_payload(artifacts, "light", name, guests))
        )
        got, exp = live.evaluate(READOUTS), ref.evaluate(READOUTS)
        assert got["cells"] == exp["cells"]
        got.pop("cells"), exp.pop("cells")
        assert got == exp
    finally:
        ctx.close()

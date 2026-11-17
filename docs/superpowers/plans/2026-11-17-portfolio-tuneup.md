# Portfolio Tune-Up Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the Seattle Airbnb Streamlit app into an honest, tested portfolio piece: real hierarchical-model predictions, one data rule, five pages in the Live Specimen visual world, real tests and a CI that can fail.

**Architecture:** A build script turns the 377 MB PyMC trace into small committed artifacts (a 1,000-draw subsample plus JSON summaries). The deployed app reads only those artifacts and the listings CSV, so it needs no PyMC. The Predict page's hero is a self-contained HTML/SVG/JS component fed precomputed curves; the other pages are native Streamlit + Plotly on one shared token module.

**Tech Stack:** Python 3.11 (`venv/`), Streamlit 1.38, pandas 2.1, numpy 1.26, Plotly 5.18; model side PyMC 5.10.3, ArviZ 0.17; pytest, `streamlit.testing.v1.AppTest`, Playwright (Chromium); black via pre-commit; GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-11-17-portfolio-tuneup-design.md`. Also read `PRODUCT.md` and the visual direction contract `.impeccable/surfaces/app-py.md`; the chosen sketch is `.impeccable/mocks/decision/challenger-specimen.html`, the quality bar `.impeccable/ref/specimen-hero.png` and `.impeccable/ref/specimen-board.png`.

## Global Constraints

- Branch `feat/portfolio-tuneup` off `master`. Every commit message ends with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. Never commit `venv/`.
- Run everything through the venv: `venv/bin/python -m pytest ...`, `venv/bin/python -m streamlit ...`.
- No emoji characters anywhere in UI strings, page titles, nav, messages, README or docs touched by this work.
- Data rule (training rule): parse `$1,234.00` to float; drop rows missing `price`, `accommodates` or `neighbourhood_cleansed`; keep `10 <= price <= 1000`. On `data/raw/listings.csv`: 6,862 rows → 635 missing price → 6,227 → 83 over $1,000, 0 under $10 → 6,144 kept.
- Neighborhood index = order of first appearance (`Series.unique()`) of `neighbourhood_cleansed` in the cleaned data. 88 neighborhoods.
- Model: `log(price) ~ Normal(alpha[n] + beta[n] * accommodates, sigma)` with raw (unstandardized) `accommodates`. "Typical price" = `exp(alpha + beta*g)`; "single listing" predictive draws include `sigma`. Intervals are equal-tailed 94% (3rd and 97th percentiles).
- Constants (in `dashboard/utils/posterior.py`): `SEED = 20251220`, `N_DRAWS = 1000`, `GUESTS = tuple(range(1, 17))`, `PRICE_GRID = np.geomspace(20, 1000, 64)`, `CI = (0.03, 0.97)`.
- Committed artifacts live in `outputs/app_artifacts/`, total under 2 MB, byte-identical on rebuild.
- Visual tokens: light `ground #FBFBFA`, `ink #111111`, `accent #D6452B`, `muted #8A8A85`, `rule #D8D8D6`; dark `ground #111111`, `ink #ECEBE6`, `accent #D6452B` (same as light, per spec), `muted #9A9CA0`, `rule #2A2B2E`. Fonts: Archivo (display numerals, weights 400/800), JetBrains Mono (labels, readouts, ticks). 1px rules, radius ≤ 2px, no shadows, glass, blur or gradients. Accent only for the selected neighborhood, the slider and the primary action.
- Streamlit Cloud entry is `expert_dashboard.py` (keep as shim importing `app.main`).

## Review Focus

1. **Guest count beyond what a neighborhood's data covers** (e.g. Holly Park at 16 guests; its listings hold 2 and 4): still renders, but the readout says the value is extrapolated. Test in Task 5.
2. **Neighborhood with no listings at the chosen guest count, or only one listing overall** (Industrial District, 1 listing): no NaN or `$nan` on screen; raw comparisons show "no listings at this size". Tests in Tasks 3 and 8.
3. **Malformed upload** (no `price` column, non-CSV bytes, price strings with `$` and commas): the upload section shows a readable error or cleans prices; nothing else on the page breaks. Test in Task 10.
4. **Dark theme**: the hero component and every chart switch tokens, nothing stays dark-on-dark. Tests in Tasks 4 and 5.
5. **Phone width (390px)**: the 88-cell grid reflows, no horizontal page scroll, slider usable. Test in Task 11.

---

### Task 1: Branch, honest test harness, requirements split

**Files:**
- Create: `pytest.ini`, `requirements-model.txt`, `requirements-dev.txt`
- Modify: `requirements.txt`, `tests/conftest.py` (rewrite), `tests/test_hierarchical_model.py` (markers only)
- Delete: `requirements-cloud.txt`, `requirements-dashboard.txt`, `packages.txt`, `tests/test_pages.py`, `tests/test_app_router.py`, `tests/test_market_intel.py`, `tests/test_business_strategy.py`, `tests/test_charts.py`, `tests/test_kpi_cards.py`, `tests/test_styling.py`, `tests/test_model_loader.py`, `tests/test_bayesian_predictor.py`, `tests/test_session_manager.py` (all test code this plan replaces; they only pass against MagicMocks)

**Interfaces:**
- Produces: pytest markers `slow` (fits a PyMC model), `trace` (needs the real LFS trace), `e2e` (needs a browser and a running app). Fixture `repo_root() -> pathlib.Path` in `tests/conftest.py`.

- [ ] **Step 1:** `git checkout master && git pull --ff-only && git checkout -b feat/portfolio-tuneup`. Commit the already-written `PRODUCT.md`, `docs/superpowers/specs/2026-11-17-portfolio-tuneup-design.md`, this plan, and `.impeccable/` (surfaces, mocks, ref) as the first commit `docs: product record, design spec and plan for portfolio tune-up`. Add `.impeccable/live/` and `.impeccable/review/` to `.gitignore` only if those directories appear later.
- [ ] **Step 2:** Write `requirements.txt` (app runtime only): `streamlit==1.38.0`, `pandas==2.1.4`, `numpy==1.26.2`, `plotly==5.18.0`, `pyyaml==6.0.1`. `requirements-model.txt`: `-r requirements.txt`, `pymc==5.10.3`, `arviz==0.17.0`, `xarray==2023.12.0`, `netCDF4==1.6.5`, `h5py>=3.10.0`, `scipy==1.11.4`. `requirements-dev.txt`: `-r requirements-model.txt`, `pytest==8.3.3`, `playwright==1.47.0`, `black==23.7.0`. Install: `uv pip install --python venv/bin/python -r requirements-dev.txt && venv/bin/python -m playwright install chromium`.
- [ ] **Step 3:** `pytest.ini`: `testpaths = tests`, register the three markers, `addopts = -m "not slow and not trace and not e2e"` (CI jobs select markers explicitly with `-m`).
- [ ] **Step 4:** Rewrite `tests/conftest.py` with no mocks of `streamlit`, `arviz` or anything else: only `sys.path` insertion of the repo root and the `repo_root` fixture. Delete the obsolete test files listed above. Mark the fitting tests in `tests/test_hierarchical_model.py` (every test using `fitted_model`, plus `test_full_pipeline`) with `@pytest.mark.slow`.
- [ ] **Step 5:** Run `venv/bin/python -m pytest -q`. Expected: `test_csv_handler`, `test_schema_detector`, `test_validators`, `test_exceptions` and the non-slow data tests in `test_hierarchical_model.py` pass; nothing errors at collection. Run `venv/bin/python -m pytest -m slow -q -x` once and record the result (pass or the exact failure) in the commit message body; do not fix the research model here.
- [ ] **Step 6:** Commit `test: remove mock-only tests, add markers, split requirements`.

### Task 2: One data rule

**Files:**
- Modify: `dashboard/utils/data_loader.py` (rewrite; the old synthetic-trace code goes)
- Test: `tests/test_data_loader.py`, fixture `tests/fixtures/listings_small.csv`

**Interfaces:**
- Produces, in `dashboard/utils/data_loader.py`:
  - `PRICE_MIN: float = 10.0`, `PRICE_MAX: float = 1000.0`, `LISTINGS_PATH: Path` (`data/raw/listings.csv`)
  - `@dataclass(frozen=True) class CleaningReport: rows_raw: int; missing_price: int; missing_other: int; below_min: int; above_max: int; rows_kept: int`
  - `parse_price(s: pd.Series) -> pd.Series` (float, NaN where unparseable)
  - `clean_listings(raw: pd.DataFrame) -> tuple[pd.DataFrame, CleaningReport]`: returns rows in original order, index reset, `price` as float
  - `neighborhood_order(clean: pd.DataFrame) -> list[str]`
  - `load_listings(path: Path = LISTINGS_PATH) -> pd.DataFrame`: `@st.cache_data`, returns cleaned frame

- [ ] **Step 1: Write failing tests.** Fixture CSV with 10 rows covering `"$1,234.00"`, `"$45.00"`, empty price, `"$9.00"`, `"$50,000.00"`, a missing neighbourhood, two neighborhoods in a known first-appearance order.
  - `test_parse_price_handles_currency_strings`: `parse_price(pd.Series(["$1,234.00", "$45.00", None, "abc"]))` equals `[1234.0, 45.0, nan, nan]`.
  - `test_clean_listings_counts_each_step`: on the fixture, the report fields equal the hand-counted values and `rows_raw - missing_price - missing_other - below_min - above_max == rows_kept`.
  - `test_clean_listings_real_file_counts`: on `data/raw/listings.csv`, report is `CleaningReport(6862, 635, 0, 0, 83, 6144)`.
  - `test_neighborhood_order_is_first_appearance`: fixture order is preserved, not sorted; on the real file the list has 88 names.
- [ ] **Step 2:** Run `venv/bin/python -m pytest tests/test_data_loader.py -v`; expect ImportError/FAIL.
- [ ] **Step 3:** Implement the interfaces above. `missing_other` counts rows with a price but missing `accommodates` or `neighbourhood_cleansed`.
- [ ] **Step 4:** Rerun; expect PASS.
- [ ] **Step 5:** Commit `feat: single data-cleaning rule matching model training`.

### Task 3: Posterior math

**Files:**
- Create: `dashboard/utils/posterior.py`
- Test: `tests/test_posterior.py`

**Interfaces:**
- Produces, in `dashboard/utils/posterior.py`: constants from Global Constraints, plus
  - `@dataclass(frozen=True) class Draws: alpha: np.ndarray  # (S, 88); beta: np.ndarray  # (S, 88); sigma: np.ndarray  # (S,); mu_alpha: np.ndarray; mu_beta: np.ndarray  # (S,); source_index: np.ndarray  # (S,) flat chain*draw index into the full trace`
  - `save_draws(d: Draws, path: Path) -> None` / `load_draws(path: Path) -> Draws` (`np.savez_compressed`, float32 for parameters)
  - `typical_price(d: Draws, idx: int, guests: int) -> np.ndarray` (S,)
  - `city_typical_price(d: Draws, guests: int) -> np.ndarray` (S,) from `mu_alpha`, `mu_beta`
  - `interval(samples: np.ndarray) -> tuple[float, float]` (3rd, 97th percentile)
  - `predictive_samples(d: Draws, idx: int, guests: int, per_draw: int = 8) -> np.ndarray` (S*per_draw,), using `np.random.default_rng(SEED + 1000*idx + guests)` so results are deterministic per pair
  - `predictive_quantiles(d: Draws, idx: int, guests: int) -> dict[str, float]` keys `q03 q25 q50 q75 q97`
  - `predictive_density(d: Draws, idx: int, guests: int, grid: np.ndarray = PRICE_GRID) -> np.ndarray` (64,): mean over draws of the log-normal pdf in price space, divided by its maximum (peak = 1; the curve is for shape display only)

- [ ] **Step 1: Write failing tests** on a synthetic `Draws` (S=2000, 3 neighborhoods, known alpha/beta/sigma):
  - `test_typical_price_matches_formula`: equals `np.exp(alpha[:, i] + beta[:, i] * g)`.
  - `test_predictive_wider_than_typical`: for each neighborhood, the predictive interval contains the typical interval and is strictly wider.
  - `test_predictive_median_close_to_typical_median`: within 3%.
  - `test_quantiles_monotone`: `q03 < q25 < q50 < q75 < q97`.
  - `test_density_peak_is_one_and_peaks_near_mode`: max is 1.0; argmax grid value within one grid step of `exp(median_mu - sigma^2)`.
  - `test_predictive_is_deterministic`: two calls give identical arrays.
  - `test_save_load_roundtrip`: arrays equal after save/load (float32 tolerance 1e-6 relative).
- [ ] **Step 2:** Run `venv/bin/python -m pytest tests/test_posterior.py -v`; expect FAIL.
- [ ] **Step 3:** Implement. Density: evaluate `lognorm.pdf` with numpy directly (no scipy at runtime): `exp(-(ln x - mu)^2 / (2 s^2)) / (x s sqrt(2π))`, vectorized over draws and grid.
- [ ] **Step 4:** Rerun; expect PASS.
- [ ] **Step 5:** Commit `feat: posterior prediction math with predictive noise`.

### Task 4: Artifact build, committed artifacts, fidelity tests

**Files:**
- Create: `scripts/build_artifacts.py`, `dashboard/utils/artifacts.py`, `outputs/app_artifacts/{draws.npz,neighborhoods.json,curves.json,hyper.json,diagnostics.json,cleaning.json}`
- Test: `tests/test_artifacts.py` (runs in CI), `tests/test_trace_fidelity.py` (marker `trace`)
- Delete: `models/scaler_params.json`, `dashboard/utils/bayesian_predictor.py`, `dashboard/utils/model_loader.py`

**Interfaces:**
- Consumes: Task 2 `clean_listings`, `neighborhood_order`, `LISTINGS_PATH`; Task 3 everything.
- Produces:
  - `scripts/build_artifacts.py`: `subsample_draws(idata, n: int = N_DRAWS, seed: int = SEED) -> Draws`; `build(trace_path: Path, listings_path: Path, out_dir: Path) -> None`; CLI `venv/bin/python scripts/build_artifacts.py` with defaults `outputs/model_trace.nc`, `data/raw/listings.csv`, `outputs/app_artifacts`.
  - `dashboard/utils/artifacts.py`: `ARTIFACT_DIR: Path`; `@dataclass(frozen=True) class Artifacts: neighborhoods: dict; curves: dict; hyper: dict; diagnostics: dict; cleaning: dict`; `load_artifacts(directory: Path = ARTIFACT_DIR) -> Artifacts` (`@st.cache_resource`); `neighborhood_by_name(art: Artifacts, name: str) -> dict`.
  - JSON shapes (dollar values rounded to 2 decimals, densities to 3):
    - `neighborhoods.json`: `{"guests": [1..16], "city": {"typical": {"median": [16], "lo": [16], "hi": [16]}}, "neighborhoods": [{"name", "index", "n_listings", "max_guests_observed", "raw_median", "raw_median_by_guests": {"1": float|null, ...}, "typical": {"median": [16], "lo": [16], "hi": [16]}, "predictive": {"q03": [16], "q25": [16], "q50": [16], "q75": [16], "q97": [16]}}]}`, list in neighborhood-index order.
    - `curves.json`: `{"grid": [64], "guests": [16], "density": [[[64] x 16] x 88]}`.
    - `hyper.json`: for `mu_alpha mu_beta sigma_alpha sigma_beta sigma`: `{"mean", "lo", "hi", "hist": {"edges": [31], "counts": [30]}}` from the full posterior; plus `"pct_per_guest": {"median", "lo", "hi"}` = `100 * (exp(mu_beta) - 1)`.
    - `diagnostics.json`: `{"n_chains", "n_draws", "max_rhat", "min_ess_bulk", "min_ess_tail", "divergences", "per_param": {name: {"rhat", "ess_bulk", "ess_tail"}}, "rank": {name: [[counts per bin] per chain]}, "ppc": {"edges", "observed", "rep_mean", "rep_lo", "rep_hi"}, "coverage_94_in_sample": float}`; R-hat/ESS/divergences/rank from the full trace (ArviZ), PPC from `posterior_predictive.log_price_obs` (40 bins on log price, 200 seeded replicate draws), coverage from `draws.npz` over all 6,144 listings.
    - `cleaning.json`: `dataclasses.asdict(CleaningReport)` plus `"scraped_from": "2025-06-21", "scraped_to": "2025-06-30"` (computed from `last_scraped`).

- [ ] **Step 1: Write failing tests.**
  - `tests/test_artifacts.py` (no trace needed): `test_artifacts_load_and_have_88_neighborhoods`; `test_neighborhood_numbers_match_draws` (for pairs Broadway g=2, Holly Park g=16, Industrial District g=1, South Lake Union g=4: JSON typical median/lo/hi and predictive quantiles equal `posterior.py` recomputed from `draws.npz` within $0.01); `test_known_values` (Broadway g=2 typical median in [$160, $168], predictive q03 in [$75, $86], q97 in [$330, $356]; Holly Park `n_listings == 2`, `raw_median_by_guests["2"] == 59.0`, typical median at g=2 in [$95, $110]); `test_curves_shape_and_peak` (88×16×64, each max == 1.0); `test_cleaning_report_counts` (6862, 635, 0, 0, 83, 6144); `test_total_size_under_2mb`; `test_no_nan_in_json` (parse with `json.loads(..., parse_constant=raise)`); `test_raw_median_null_when_no_listings_at_size` (Industrial District has nulls for sizes it lacks, never NaN).
  - `tests/test_trace_fidelity.py`, all `@pytest.mark.trace`, module skipped when `outputs/model_trace.nc` is under 1 MB (LFS pointer): `test_cleaned_data_reproduces_observed_data` (log of cleaned prices equals `observed_data.log_price_obs` exactly; neighborhood index order from `neighborhood_order`); `test_draws_are_faithful_subsample` (`draws.npz` arrays equal the full posterior at `source_index`); `test_rebuild_is_byte_identical` (build into `tmp_path`, compare every file's bytes to the committed ones).
- [ ] **Step 2:** Run both test files; expect FAIL (no artifacts).
- [ ] **Step 3:** Implement the build script and loader. JSON written with `sort_keys=True, separators=(",", ":")` for byte stability.
- [ ] **Step 4:** Run `venv/bin/python scripts/build_artifacts.py`, then `venv/bin/python -m pytest tests/test_artifacts.py -v` and `venv/bin/python -m pytest -m trace -v`. Expect PASS. Check `du -sh outputs/app_artifacts` < 2 MB.
- [ ] **Step 5:** Commit `feat: precomputed model artifacts and fidelity tests` (include the artifacts).

### Task 5: Theme tokens and the Live Specimen component

**Files:**
- Create: `dashboard/theme.py`, `dashboard/components/specimen.py`, `dashboard/components/specimen_template.html`
- Modify: `.streamlit/config.toml` (theme: `base="light"`, `primaryColor="#D6452B"`, `backgroundColor="#FBFBFA"`, `secondaryBackgroundColor="#F0F0EE"`, `textColor="#111111"`, `font="sans serif"`)
- Delete: `dashboard/utils/styling.py`, `dashboard/config/themes.yaml`, `dashboard/CONTRAST_IMPROVEMENTS.md`
- Test: `tests/test_theme.py`, `tests/test_specimen.py`

**Interfaces:**
- Consumes: Task 4 `Artifacts`, `load_artifacts`.
- Produces:
  - `dashboard/theme.py`: `TOKENS: dict[str, dict[str, str]]` (keys `light`, `dark`; token names `ground ink accent muted rule`), `FONTS_URL: str` (Google Fonts Archivo 400;800 + JetBrains Mono 400;600), `css(theme: str) -> str`, `apply_theme(theme: str) -> None` (one `st.markdown(..., unsafe_allow_html=True)`), `plotly_template(theme: str) -> plotly.graph_objects.layout.Template` (fonts, ground as paper and plot background, gridlines in `rule`, colorway `[ink, muted]`; charts apply `accent` explicitly, only to the selection).
  - `dashboard/components/specimen.py`: `specimen_payload(art: Artifacts, theme: str, initial: str = "Broadway", initial_guests: int = 2) -> dict`; `specimen_html(payload: dict) -> str`; `render_specimen(art: Artifacts, theme: str, height: int = 980) -> None` (calls `streamlit.components.v1.html(..., height=height, scrolling=False)`).
  - Component DOM hooks (`data-testid`): `specimen-select` (native `<select>` of 88 names, alphabetical), `specimen-slider` (`<input type="range" min=1 max=16>`), `specimen-guests` (current guest number), `specimen-price` (giant median, from predictive `q50`), `specimen-range` (single-listing 94% range `q03`–`q97`), `specimen-typical` (typical price 94% credible interval), `specimen-extrapolation` (present only when guests > `max_guests_observed`; text: `Beyond the largest {name} listing in the data ({max} guests): extrapolated.`), `specimen-cell-{index}` per neighborhood, each containing an SVG `path` with `data-testid="curve"`; the selected cell has `data-selected="true"`.

- [ ] **Step 1: Write failing tests.**
  - `test_theme.py`: `test_css_never_targets_all_st_classes` (`'[class*="st-"]'` not in `css(t)` for both themes: this selector broke Streamlit's icon font); `test_css_has_no_banned_effects` (no `backdrop-filter`, `gradient`, `box-shadow` other than `none`); `test_css_uses_tokens` (each token hex appears); `test_dark_tokens_differ` (`TOKENS["dark"]["ground"] != TOKENS["light"]["ground"]`); `test_plotly_template_fonts_and_ground` (paper/plot bgcolor == ground, font family starts with `JetBrains Mono`).
  - `test_specimen.py`: `test_payload_has_all_neighborhoods_in_fixed_order` (88 cells ordered by typical median at 2 guests ascending; Broadway selected, guests 2); `test_payload_marks_extrapolation_limits` (each entry carries `max_guests_observed`; Holly Park's is 4); `test_html_is_self_contained` (no `<script src=`, no external URLs except `fonts.googleapis.com`/`fonts.gstatic.com`); `test_html_contains_testids` (every hook above); `test_html_dark_uses_dark_tokens` (`specimen_html(specimen_payload(art, "dark"))` contains `#111111` as ground and not `#FBFBFA`); `test_html_has_no_emoji` (no char in emoji ranges `U+1F000–U+1FAFF`, `U+2600–U+27BF`); `test_initial_readout_values` (rendered HTML's server-side initial text shows `$164` ± $4 for Broadway and the matching range).
- [ ] **Step 2:** Run both; expect FAIL.
- [ ] **Step 3:** Implement `theme.py`. CSS rules: load fonts; app ground/ink from tokens; headings Archivo; body, labels, captions, metric labels, sidebar nav JetBrains Mono uppercase tracked 0.06em at 11-12px; font-family applied only to text selectors (`h1..h6, p, label, li, .stMarkdown, [data-testid="stMetricLabel"], [data-testid="stSidebarNav"] span`); 1px `rule` borders; radius ≤ 2px on inputs/buttons; do not hide Streamlit's header (keeps the sidebar toggle working); hide footer and main menu only.
- [ ] **Step 4:** Implement the component to match `.impeccable/mocks/decision/challenger-specimen.html` and the quality bar: top band with label, giant Archivo 800 price (clamp 64px–150px), range and typical lines in mono; slider at right with 1–16 tick readout and the accent knob; neighborhood select beside it; grid `repeat(auto-fill, minmax(112px, 1fr))` of cells (curve SVG 100×44 on a shared log-price x scale, mono name, mono median); clicking a cell selects it. JS (inline, no libraries) recomputes from the embedded payload on `input` events: swaps each cell's path `d` for the current guest count, updates readouts, toggles extrapolation note. Transition on path `d` 120ms, disabled under `prefers-reduced-motion`. Tokens injected as CSS custom properties.
- [ ] **Step 5:** Rerun tests; expect PASS.
- [ ] **Step 6:** Commit `feat: specimen theme tokens and live hero component`.

### Task 6: App shell, session state, Predict page; remove the old app

**Files:**
- Modify: `app.py` (rewrite), `dashboard/utils/session_manager.py` (shrink), `expert_dashboard.py` (unchanged shim; verify)
- Create: `dashboard/pages/predict.py`
- Delete: `dashboard/pages/{overview,market_intel,business_strategy,prediction,model_insights,neighborhood}.py`, `dashboard/components/{investment_analyzer,feature_impact,model_validation,neighborhood_comparison,price_predictor,kpi_cards}.py`
- Test: `tests/test_app.py`

**Interfaces:**
- Consumes: Task 4 `load_artifacts`; Task 5 `apply_theme`, `render_specimen`.
- Produces:
  - `session_manager.py`: `class AppState` with only `THEME = "theme"` and `init() -> None` (default `"light"`), `theme() -> str`.
  - `app.py`: `PAGES: list[tuple[str, str, Callable]]` = `[("Predict", "predict", predict.render), ("Neighborhoods", "neighborhoods", neighborhoods.render), ("How the model works", "model", model.render), ("Diagnostics", "diagnostics", diagnostics.render), ("Data notes", "data-notes", data_notes.render)]`; `main() -> None` builds `st.navigation` from `PAGES` with `st.Page(fn, title=..., url_path=..., default=(i == 0))`, no icons; sidebar: brand line "SEATTLE / BAYES" and caption "Hierarchical price model, 88 neighborhoods", a `st.toggle("Dark")`, link to the GitHub repo. Pages not yet built in this task render a one-line placeholder (replaced in Tasks 8-10).
  - Every page module exposes `render() -> None`.
- [ ] **Step 1: Write failing tests** with `AppTest.from_file("app.py")` and `AppTest.from_function` per page: `test_app_runs_without_exception` (both themes: set `at.session_state["theme"]`); `test_nav_titles_have_no_emoji_and_match_pages`; `test_predict_page_renders_component_and_explainer` (no exception; markdown contains "what you're looking at"; a link/text pointing to "How the model works").
- [ ] **Step 2:** Run; expect FAIL.
- [ ] **Step 3:** Implement. `predict.render()`: page title "Predict a nightly price", `render_specimen(load_artifacts(), AppState.theme())`, then a short plain-language explainer (3-4 sentences: what the big number is, what the range means, why small neighborhoods lean toward the city, that every curve comes from 8,000 posterior draws summarized by a 1,000-draw sample). Delete the listed files; `grep -rn` for imports of deleted modules returns nothing.
- [ ] **Step 4:** Rerun the whole fast suite; expect PASS. Start `venv/bin/python -m streamlit run app.py --server.port 8599 --server.headless true`, open http://localhost:8599, drag the slider, confirm cells move and readouts change; screenshot for your own check.
- [ ] **Step 5:** Commit `feat: new app shell and live Predict page; remove old pages`.

### Task 7: Shared chart builders

**Files:**
- Modify: `dashboard/components/charts.py` (rewrite)
- Test: `tests/test_charts.py` (new)

**Interfaces:**
- Consumes: Task 5 `plotly_template`, `TOKENS`; Task 4 artifact dicts.
- Produces (all return `plotly.graph_objects.Figure`, all take `theme: str` last):
  - `forest_plot(nbhds: list[dict], guests: int, selected: str, theme)`: horizontal intervals (typical lo–hi) and median dots, sorted by median, selected in accent, city typical median as a vertical rule.
  - `shrinkage_plot(nbhds: list[dict], guests: int, theme)`: x = raw median at `guests`, y = model typical median, marker size ∝ `sqrt(n_listings)`, identity line, horizontal city line; neighborhoods with null raw median omitted; returns figure with `layout.meta = {"omitted": int}`.
  - `price_histogram(prices: pd.Series, theme, title: str)`
  - `hyper_hist(summary: dict, label: str, theme)`
  - `rank_plot(rank: list[list[int]], label: str, theme)`
  - `ppc_plot(ppc: dict, theme)`
- [ ] **Step 1: Write failing tests:** each builder returns a figure whose `layout.template` fonts match the theme; `test_forest_selected_in_accent` (the selected trace/marker color == `TOKENS[theme]["accent"]`, all others not); `test_shrinkage_omits_null_raw` (omitted count equals neighborhoods with null raw median at that guest count); `test_no_nan_in_figure_data` for Industrial District inputs.
- [ ] **Step 2:** Run; FAIL. **Step 3:** Implement. **Step 4:** Run; PASS.
- [ ] **Step 5:** Commit `feat: chart builders on shared specimen template`.

### Task 8: Neighborhoods page

**Files:**
- Create: `dashboard/pages/neighborhoods.py`
- Test: `tests/test_page_neighborhoods.py`

**Interfaces:**
- Consumes: Task 2 `load_listings`; Task 4 `load_artifacts`, `neighborhood_by_name`; Task 7 `forest_plot`, `shrinkage_plot`, `price_histogram`.

- [ ] **Step 1: Write failing AppTest tests:** default renders without exception with guests 2 and Broadway; detail readouts show listing count `359`, model typical at 2 guests (`$164` ± 4), premium vs city as `N.NNx`; selecting "Industrial District" shows `1` listing and the text "no listings at this size" for sizes it lacks, never `nan`; the shrinkage caption names how many neighborhoods were omitted and mentions Holly Park (2 listings, raw $59, model about $102).
- [ ] **Step 2:** Run; FAIL.
- [ ] **Step 3:** Implement: controls row (neighborhood select, guests slider 1-16); forest plot; shrinkage plot with a two-sentence caption on partial pooling; detail section with mono readouts and the cleaned price histogram for the neighborhood.
- [ ] **Step 4:** Run; PASS. **Step 5:** Commit `feat: Neighborhoods page with forest and shrinkage plots`.

### Task 9: How the model works, and Diagnostics

**Files:**
- Create: `dashboard/pages/model.py`, `dashboard/pages/diagnostics.py`
- Test: `tests/test_page_model.py`, `tests/test_page_diagnostics.py`

**Interfaces:**
- Consumes: Task 4 `load_artifacts`; Task 7 `hyper_hist`, `rank_plot`, `ppc_plot`.

- [ ] **Step 1: Write failing AppTest tests.** Model page: renders `st.latex` blocks containing `\alpha_{n}` and `\sigma`; shows the per-guest effect as `+X.X%` with its interval where X equals `hyper.json` `pct_per_guest.median` to one decimal (about 17.5); five hyperparameter cells present. Diagnostics page: shows max R-hat formatted to 3 decimals equal to `diagnostics.json` (about 1.003), min bulk ESS, divergences `0`, in-sample coverage as a percent with the words "in-sample"; rank plots for 5 parameters; a PPC chart; no exception in dark theme.
- [ ] **Step 2:** Run; FAIL.
- [ ] **Step 3:** Implement. Model page order: plain-language summary (3 short paragraphs: log price, neighborhood intercepts and slopes, partial pooling), notation via `st.latex` (likelihood, linear predictor, hierarchy, priors exactly as in `src/hierarchical_bayesian_model.py::build_hierarchical_model`: `mu_alpha ~ N(4.5, 1)`, `sigma_alpha ~ HalfNormal(0.5)`, `mu_beta ~ N(0.2, 0.1)`, `sigma_beta ~ HalfNormal(0.1)`, `sigma ~ HalfNormal(0.5)`), hyperparameter cells, per-guest effect. Diagnostics: a readout band (large Archivo numerals with mono labels, not Streamlit metric tiles), each with a one-line reading for non-specialists, then rank plots, then PPC with a caption.
- [ ] **Step 4:** Run; PASS. **Step 5:** Commit `feat: model explanation and diagnostics pages`.

### Task 10: Data notes with upload

**Files:**
- Create: `dashboard/pages/data_notes.py`
- Delete: `dashboard/pages/upload.py`
- Keep: `dashboard/utils/{csv_handler,schema_detector,validators,exceptions}.py`, `dashboard/config/column_aliases.yaml`
- Test: `tests/test_page_data_notes.py`

**Interfaces:**
- Consumes: Task 4 `load_artifacts` (`cleaning`); `csv_handler.process_upload(file, filename) -> dict`; Task 2 `parse_price`; Task 7 `price_histogram`.

- [ ] **Step 1: Write failing tests:** page shows source "Inside Airbnb", scrape dates 2025-06-21 to 2025-06-30, a cleaning table with 6,862 / 635 / 6,227 / 83 / 6,144; limitations list contains "listed price, not booked price" and "guest count is the only listing feature in the model". Upload section (call the page's helper `summarize_upload(file, filename) -> dict` directly): a CSV whose prices are `"$1,234.00"` strings yields numeric median; a CSV without a price column yields `{"ok": False, "error": <non-empty str>}`; random bytes yield `ok False`; the page text states the model is not refit on uploads.
- [ ] **Step 2:** Run; FAIL.
- [ ] **Step 3:** Implement `summarize_upload(file, filename) -> dict` (`{"ok": True, "rows": int, "median_price": float, "prices": pd.Series, "warnings": list[str]}` or `{"ok": False, "error": str}`) using `process_upload` then `parse_price`, and the page.
- [ ] **Step 4:** Run; PASS. **Step 5:** Commit `feat: Data notes page with descriptive upload`.

### Task 11: Browser end-to-end tests

**Files:**
- Create: `tests/e2e/test_app_e2e.py`, `tests/e2e/conftest.py`

**Interfaces:**
- Consumes: Task 5 `data-testid` hooks; Task 6 URL paths.
- Produces: session fixture `app_url` that starts `venv/bin/python -m streamlit run app.py --server.port 8765 --server.headless true` (use `sys.executable`), waits for `/_stcore/health` == `ok` (60 s timeout), yields `http://localhost:8765`, terminates on teardown.

- [ ] **Step 1: Write the tests** (all `@pytest.mark.e2e`, Playwright sync API, frame via `page.frame_locator("iframe[title='st.iframe']")` or the first iframe containing `[data-testid=specimen-slider]`):
  - `test_slider_moves_every_curve`: record all `curve` `d` attributes; set slider to 6 (`fill` then dispatch `input`); every `d` changed; `specimen-guests` shows 6; `specimen-price` text changed.
  - `test_select_and_click_change_selection`: choose "Fremont" in `specimen-select`, its cell has `data-selected="true"`; click another cell, selection moves.
  - `test_extrapolation_note`: select Holly Park, slider 16, `specimen-extrapolation` visible; slider 2, hidden.
  - `test_pages_load_without_errors`: visit `/`, `/neighborhoods`, `/model`, `/diagnostics`, `/data-notes`; no `[data-testid=stException]`; zero console errors.
  - `test_no_emoji_in_rendered_text`: page `inner_text` of each route has no char in the emoji ranges.
  - `test_phone_width_no_horizontal_scroll`: viewport 390×844, `/`: `document.documentElement.scrollWidth <= 390`; slider visible and draggable.
  - `test_dark_toggle_switches_component`: toggle "Dark"; the component's computed background equals the dark ground.
- [ ] **Step 2:** Run `venv/bin/python -m pytest -m e2e -v`; fix failures in the owning code (component or page), not by weakening tests.
- [ ] **Step 3:** Commit `test: browser end-to-end tests for the live specimen and pages`.

### Task 12: CI that can fail

**Files:**
- Modify: `.github/workflows/ci.yml`, `.pre-commit-config.yaml` (black rev stays 23.7.0; drop excludes for deleted files)

- [ ] **Step 1:** Rewrite the workflow: triggers push/PR on `master` and `main`; `actions/checkout@v4` (default `lfs: false`), `actions/setup-python@v5` with `python-version: "3.11"` and pip cache. Jobs: `lint` (pre-commit run --all-files); `test` (install `requirements-dev.txt`, `python -m pytest -q`); `model` (same install, `python -m pytest -m slow -q`); `e2e` (same install, `python -m playwright install --with-deps chromium`, `python -m pytest -m e2e -q`). No `|| echo`, no `continue-on-error`.
- [ ] **Step 2:** Run locally exactly what each job runs: `venv/bin/pre-commit run --all-files` (install pre-commit into the venv if absent), `venv/bin/python -m pytest -q`, `-m slow`, `-m e2e`. All pass, or for `slow`, the plan's Task 1 recorded result is fixed or the failing research test is reported to Dennis before proceeding (do not delete it).
- [ ] **Step 3:** Confirm the workflow has no `|| echo`, `|| true` or `continue-on-error` (`grep -nE '\|\| (echo|true)|continue-on-error' .github/workflows/ci.yml` returns nothing). The first PR run in Task 15 is the live proof.
- [ ] **Step 4:** Commit `ci: python 3.11, real failures, model and e2e jobs`.

### Task 13: README, docs and screenshots

**Files:**
- Modify: `README.md` (rewrite), `QUICKSTART.md` (update commands), `dashboard/README.md` (short, current), `notebooks/README.md` only if it states model numbers
- Delete: `dashboard/DEPLOYMENT.md` (content folded into README "Deploy" section)
- Create: `gitpics/predict.png`, `gitpics/neighborhoods.png`, `gitpics/diagnostics.png` (captured from the running app at 1440×900, device scale factor 2)

- [ ] **Step 1:** Write README: one-paragraph what and why; live link; screenshot; "The model" (formula, priors, 6,144 listings, 88 neighborhoods, 4×2000 draws); "Verified numbers" table populated only from artifacts (max R-hat, min ESS, divergences, in-sample 94% coverage, per-guest effect) plus a sentence that these regenerate with `scripts/build_artifacts.py`; "Data" (cleaning steps with counts); "Run locally" (`python3.11 -m venv venv`, install `requirements.txt` to run, `requirements-dev.txt` to test, `streamlit run app.py`); "Tests" (marker meanings and commands); "Rebuild artifacts" (needs `git lfs pull`); "Deploy" (Streamlit Cloud, `expert_dashboard.py`, branch `master`, Python 3.11/3.12). Remove HF front matter, badges that point at wrong-case URLs (fix to the real repo path), "enterprise-grade", "production-ready", the R² table, and every emoji.
- [ ] **Step 2:** Verification: `grep -nP "[\x{1F000}-\x{1FAFF}\x{2600}-\x{27BF}]" README.md QUICKSTART.md dashboard/README.md` returns nothing; every number in the README appears in an artifact JSON (check by hand against `outputs/app_artifacts/*.json`).
- [ ] **Step 3:** Commit `docs: honest README with verified numbers and new screenshots`.

### Task 14: Impeccable finish

**Files:**
- Create: `DESIGN.md`, `.impeccable/design.json` (by the documenter), `.impeccable/review/desktop.png`, `.impeccable/review/mobile.png`

- [ ] **Step 1:** Run `/home/dennisjcarroll/.claude/skills/impeccable/scripts/impeccable detect --json` on `app.py dashboard/` and fix mechanical findings.
- [ ] **Step 2:** One batched capture round of every page at 1440 wide and 390 wide, light and dark, with motion settled; open each file and confirm it shows what its name claims.
- [ ] **Step 3:** Spawn `impeccable-finish-reviewer` with: the original request (portfolio for recruiters, show Bayesian skills, remove emojis, fix flat look), confirmed answers from the spec's "Decided by Dennis", artifact path `app.py`, the screenshot paths, the direction contract `.impeccable/surfaces/app-py.md`, remaining detector findings, the chosen sketch `.impeccable/mocks/decision/challenger-specimen.html` as the critique reference, and `.impeccable/ref/specimen-*.png` as the quality bar. Act on its disposition (`recapture`, `rebuild`, `fix`, `ship`), rerunning the fast tests and e2e after any fix.
- [ ] **Step 4:** Spawn `impeccable-documenter` with project root, `app.py`, the direction contract, `PRODUCT.md`, and write boundary `DESIGN.md` + `.impeccable/design.json`. Verify both exist and carry tokens.
- [ ] **Step 5:** Commit `docs: DESIGN.md from the finished build`.

### Task 15: Push and open the PR

- [ ] **Step 1:** Full local verification: `venv/bin/python -m pytest -q`, `-m trace`, `-m slow`, `-m e2e`, pre-commit. Paste outputs into the PR body's Testing section.
- [ ] **Step 2:** `git push -u origin feat/portfolio-tuneup` (retry network errors up to 4 times with backoff).
- [ ] **Step 3:** `gh pr create --base master` titled `Portfolio tune-up: honest predictions, Live Specimen redesign, real tests`. Body: summary, what changed per page, before/after screenshots, the corrected claims, testing output, and the note that merging redeploys Streamlit Cloud. End with `🤖 Generated with [Claude Code](https://claude.com/claude-code)`.
- [ ] **Step 4:** Report the PR URL and the first CI run's result to Dennis. Do not merge.

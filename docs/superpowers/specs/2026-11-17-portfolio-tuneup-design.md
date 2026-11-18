# Portfolio Tune-Up: Design

Date: 2026-11-17
Status: awaiting Dennis's approval
Related: `PRODUCT.md` (product truth), `.impeccable/surfaces/app-py.md` (visual direction contract)

## Intent

This Streamlit app is Dennis's portfolio piece for data-science hiring. Today it looks flat (default Streamlit plus glass CSS and emojis) and it is not honestly tested: the prediction page ignores most of its inputs, outlier prices distort every chart, and CI reports green no matter what. The goal is a dashboard that (a) makes a recruiter understand "this person can build and explain a hierarchical Bayesian model" within a minute and (b) holds up when a technical reviewer opens the code, the model and the tests.

## Goals

1. **Model at work, first.** The opening page shows a real nightly price with its uncertainty, driven by the real trained model, and lets the visitor drag guest count to watch all 88 neighborhoods move at once.
2. **Every number is true.** Predictions use the actual hierarchical model (neighborhood intercept and slope, raw guest count, observation noise). README and in-app numbers match what the repo reproduces.
3. **One consistent data rule** across every page, stated on a Data notes page.
4. **New visual world:** Live Specimen (see direction contract). No emojis anywhere.
5. **Real tests and honest CI:** tests that would fail if the app or model were wrong; CI that fails when they do.
6. **Lighter deploy:** the deployed app does not need PyMC.

## Non-goals

- Retraining the model or building the larger "enhanced" model (property type, amenities, reviews). Possible later; out of scope.
- Changing the research code in `src/` beyond what tests need.
- Investment/ROI advice features.

## Anti-goals (failure even if it works)

- A generic SaaS dashboard (KPI tile row, glass, gradients, soft cards).
- A plain default-Streamlit look.
- Any number on screen or in the README that the repo cannot reproduce.
- Controls that do nothing.

## Constraints

- Deploy target: Streamlit Community Cloud, which launches `expert_dashboard.py` (keep it as the entry shim). Hugging Face Spaces front matter in README is dropped.
- Trained trace `outputs/model_trace.nc` (4 chains x 2000 draws) is the source of truth. Verified: its `observed_data` equals `log(price)` for the 6,144 listings that remain after the cleaning rule below, in `unique()` order of `neighbourhood_cleansed`. That order defines neighborhood indices.
- The model (`src/hierarchical_bayesian_model.py::build_hierarchical_model`): `log(price) ~ Normal(alpha[n] + beta[n] * accommodates, sigma)`, raw (unstandardized) accommodates, `alpha ~ Normal(mu_alpha, sigma_alpha)`, `beta ~ Normal(mu_beta, sigma_beta)`.
- Data: Inside Airbnb Seattle listings scraped 2025-06-21 to 2025-06-30; 6,862 rows; 635 missing price; 83 priced over $1,000 including placeholder prices up to $50,034; accommodates 1-16.
- Python: local venv `venv/` (Python 3.11). Streamlit Cloud deploys from `master` (confirmed by Dennis). Work happens on feature branch `feat/portfolio-tuneup` off `master`, ends with the branch pushed and a PR opened for Dennis to review; nothing merges or deploys without him. CI triggers already cover `master`.

## Approaches considered

How to deliver the signature interaction (drag guests, all 88 neighborhood curves move live) inside Streamlit, which reruns the whole script on every widget change:

- **A. Custom HTML/SVG component for the hero, native Streamlit elsewhere (chosen).** Python precomputes curves for every neighborhood x guest count; a self-contained component (`st.components.v1.html`, inline JS/SVG, no build step) renders the giant readout, slider and 88-cell grid and redraws instantly on drag. Other pages are native Streamlit + Plotly. Trade-off: some JavaScript, and the component needs browser-level tests.
- **B. Plotly animation frames.** No custom JS, but the slider steps rather than follows the drag and an 88-panel Plotly grid is heavy and hard to style.
- **C. Plain Streamlit slider.** Simplest; every change reruns and redraws, losing the live effect.

Dennis chose A.

## Design

### 1. Precomputed model artifacts

New script `scripts/build_artifacts.py` (runs in the full venv with arviz) reads the trace and listings and writes `outputs/app_artifacts/`:

- `neighborhoods.json`: for each of 88 neighborhoods: name, index, listing count, raw median price (cleaned data), and for guests 1-16: posterior median of the typical price `exp(alpha + beta*g)` with its 94% credible interval, and posterior predictive quantiles (3, 25, 50, 75, 97 percent) for a single listing, which include `sigma`.
- `curves.json`: for each neighborhood x guests 1-16, the posterior predictive density on a fixed price grid (about 64 points, log-spaced $20-$1,000), computed by averaging log-normal densities over a seeded subsample of draws, normalized. Rounded to keep the file small (target under 1 MB).
- `hyper.json`: posterior summaries for `mu_alpha`, `mu_beta`, `sigma_alpha`, `sigma_beta`, `sigma` (mean, 94% HDI, a histogram for small plots), plus the derived "each extra guest raises price by about X%" from `exp(mu_beta) - 1`.
- `diagnostics.json`: max R-hat and min bulk/tail ESS across all parameters, per-hyperparameter R-hat/ESS, divergence count, rank-plot data for hyperparameters, a posterior predictive check summary (observed vs replicated log-price histograms from the trace's `posterior_predictive` group), and in-sample 94% predictive interval coverage, labeled in-sample.
- `cleaning.json`: the counts at each data-cleaning step (see section 3).

The deployed app reads only these JSON files plus the listings CSV. Deterministic: fixed seed, so regenerating gives byte-identical output.

Requirements split: `requirements.txt` becomes the app runtime only (streamlit, pandas, numpy, plotly, pyyaml) for Streamlit Cloud; new `requirements-model.txt` holds pymc, arviz, xarray, netCDF/h5 for training, artifact building and model tests. Versions pinned to what is verified working in the venv.

### 2. Prediction correctness

Replace `dashboard/utils/bayesian_predictor.py` logic and `models/scaler_params.json` usage: predictions come from the artifacts (the hero) and from a small pure-numpy function `predict(neighborhood, guests)` that reproduces the artifact numbers from posterior draws (used by tests to cross-check). No standardization (the model used raw accommodates). Inputs the model does not use (bedrooms, bathrooms, beds) are removed. Two intervals are shown and named plainly: "typical price for this kind of listing" (credible interval of the mean) and "range for a single listing" (posterior predictive, includes noise). Guest counts above a neighborhood's observed maximum are flagged as extrapolation in the hero readout.

`scaler_params.json` and the old global-means predictor are deleted.

### 3. One data rule

Single function in `dashboard/utils/data_loader.py` used by every page, identical to the training rule: parse `$1,234.00` to float, drop rows missing price, accommodates or neighborhood, keep $10-$1,000. The Data notes page reports each step's count (6,862 rows; minus 635 missing price leaves 6,227; minus 83 priced over $1,000, including the $40,000-$50,000 placeholder hotel listings, leaves 6,144; none under $10) and why.

### 4. Pages (tightened from seven)

Navigation is a text-only rail, no icons or emojis:

1. **Predict** (default route). The Live Specimen hero component: neighborhood select, guest slider (1-16), giant median price, single-listing 94% range, typical-price interval, and the 88-cell grid of predictive curves with the selected neighborhood in vermilion. Below the component: a short plain-language "what you're looking at" for recruiters and a link onward to the model page.
2. **Neighborhoods.** All 88 posterior medians with 94% intervals at the chosen guest count, sorted (forest plot, styled in the world). A shrinkage plot: raw median vs model estimate, sized by listing count, showing small neighborhoods pulled toward the city (Holly Park: 2 listings, raw $59, model about $102). A per-neighborhood detail: listing count, observed price distribution (cleaned), premium vs city. Replaces the old Neighborhood, Market Intelligence and Business Strategy pages' useful parts.
3. **How the model works.** The model in plain words, then in notation (`st.latex`): likelihood, priors, hierarchy, why log price, what partial pooling buys. Hyperparameter posteriors as small specimen cells. Effect of one extra guest.
4. **Diagnostics.** R-hat, ESS, divergences, rank plots, posterior predictive check, in-sample calibration, each with a one-line reading for non-specialists.
5. **Data notes.** Source, scrape dates, cleaning steps with counts, known limitations (one city, one snapshot, listed price not booked price, guest count is the only listing feature in the model). Contains the CSV upload as a small "explore your own city's listings" section, descriptive only, stating the model is not refit on uploads.

Deleted: `market_intel.py`, `business_strategy.py`, `overview.py` (content absorbed), old `prediction.py`/`model_insights.py`/`neighborhood.py`/`upload.py` rewritten, and unused components never imported by any page (`investment_analyzer.py`, `feature_impact.py`, `model_validation.py`, `neighborhood_comparison.py`, `price_predictor.py`, about 2,600 lines). `src/` research scripts stay.

### 5. Visual world (summary; the contract governs)

Paper #FBFBFA ground, ink #111, one vermilion accent #D6452B reserved for the selected neighborhood and the slider, muted #8A8A85 labels, 1px hairline rules, no shadows/glass/gradients, radius 2px or less. Archivo for display numerals at large scale, JetBrains Mono for labels, readouts and ticks. One Plotly template built from the same tokens for every chart. A dark variant (ink ground, paper text, same accent) via a plain "Dark" toggle. The global font override is scoped so Streamlit's icon font renders (fixes the stray "keyb" text). Built to the selected sketch `.impeccable/mocks/decision/challenger-specimen.html` and the quality bar images in `.impeccable/ref/`.

### 6. Tests

Replace the MagicMock-everything `tests/conftest.py`:

- **Model fidelity (needs model requirements):** rebuilding the cleaned data reproduces the trace's `observed_data` exactly (guards the neighborhood index mapping); artifact numbers equal a direct numpy computation from the trace for sampled neighborhood/guest pairs; predictive intervals are wider than mean intervals; quantiles monotone; densities normalized; artifact build is deterministic.
- **Data rule:** cleaning on a small fixture CSV gives the expected counts; every page's data comes from the one function.
- **Pages:** `streamlit.testing.v1.AppTest` runs each page headless and asserts no exception and the key content present (price readout, 88 neighborhoods, diagnostics values), in light and dark.
- **Component (browser):** Playwright opens the running app, drags the guest slider, and asserts the readout and the curve paths change, the selected cell is vermilion, and there are no console errors. Also checks no emoji characters appear in the rendered page.
- **Existing `tests/test_hierarchical_model.py`:** made importable (it was broken by the arviz mock); the slow fitting tests are marked `slow` and run in a separate CI job.

### 7. CI

`.github/workflows/ci.yml`: Python 3.11, actions updated to current major versions, the `|| echo "No tests found"` removed. Jobs: lint (pre-commit/black), fast tests (app runtime + artifact consumers), model tests (model requirements, includes slow), e2e (Playwright against `streamlit run`). Any failure fails the run.

### 8. README and repo hygiene

Rewrite README to describe the deployed model honestly: what it is, the verified numbers (listing counts, diagnostics, in-sample coverage), screenshots of the new app, how to run, how to rebuild artifacts. Remove "enterprise-grade", "production-ready", the unreproduced R² 0.687 table, and emojis. Fix the Quick Start command and the HF front matter.

## Decided by Dennis

- Audience: both recruiters and technical reviewers, layered.
- Show what is real; fix predictions; correct README claims.
- Deploy on Streamlit Community Cloud.
- First screen: model at work.
- Tighten pages to the story; Business Strategy dropped or folded; Upload kept small.
- Avoid: generic SaaS look and too-plain look.
- Visual world: Live Specimen.
- Build approach A.
- Venv created by Claude.
- Deploy branch `master`; this round ends at branch + PR.

## Calls made after the builder check (Claude's, correct if wrong)

- **Artifacts are committed** to git under `outputs/app_artifacts/` (Streamlit Cloud cannot run the PyMC build). Size budget about 2 MB total.
- **The full trace stays out of CI.** `outputs/model_trace.nc` is 377 MB in Git LFS; pulling it on every CI run would burn the free LFS bandwidth. `build_artifacts.py` therefore saves the seeded draw subsample it uses (about 1,000 draws of `alpha`, `beta`, `sigma`, float32) as `outputs/app_artifacts/draws.npz`. CI tests check every JSON artifact against `draws.npz` exactly. A local-only test (skipped when the trace is an LFS pointer) checks `draws.npz` is a faithful subsample of the full trace and that the cleaned data reproduces `observed_data`.
- **Dark toggle** is a plain text toggle labeled "Dark", no emoji. The hero component receives the active theme tokens as a parameter when it is rendered, so it follows the toggle on rerun.
- **Component testing:** the component exposes stable `data-testid` hooks; Playwright reaches it through `frame_locator`. Playwright (Chromium) is a CI dependency and the e2e job runs on every push and PR.
- **Requirements:** `requirements.txt` is the slim runtime file Streamlit Cloud reads; `requirements-model.txt` for model work; `requirements-cloud.txt`, `requirements-dashboard.txt` and `packages.txt` are deleted. Pins chosen to install on Python 3.11 and 3.12.
- **Upload path:** `schema_detector`, `csv_handler` and `validators` stay (they serve the upload section) and get real tests; `session_manager` shrinks to what remains (active data, theme).
- **Styling:** `dashboard/utils/styling.py`, `dashboard/config/themes.yaml` and the glass CSS in `app.py` are replaced wholesale by one token module that feeds both the CSS and the Plotly template. No existing styling behavior is preserved.

## Left to the builder

- Exact component markup, file layout under `dashboard/`, chart details within the world's rules.
- Curve grid resolution and rounding, as long as artifacts stay under about 1 MB and curves look smooth.
- Whether old tests that only check `hasattr` are deleted or rewritten.
- Mobile layout of the 88-cell grid (fewer columns, same order).

## Open

- Root-level personal files (`Data_Science_Portfolio_Transformation_Blueprint (1).docx`, `bayesian_airbnb_completion_plan.md.pdf`, `Favorite_UI_Theme.png`, empty `airbnb_dashboard.py`, a duplicate `calendar.csv`) are untouched unless Dennis says otherwise.
- Finish: per the direction contract, the build ends with the impeccable finish review, its verdict, and a DESIGN.md.

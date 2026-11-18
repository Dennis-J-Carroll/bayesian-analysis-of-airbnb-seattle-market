# Quick start

Python 3.11 is the supported version.

```bash
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

The app opens at http://localhost:8501. It reads the committed files in `outputs/app_artifacts/`; no model fitting happens at startup.

## Pages

- Predict: pick a neighborhood and guest count, see the median nightly price, a 94% interval for the typical price and for a single listing, and all 88 neighborhoods at once.
- Neighborhoods: one neighborhood in detail, against the city.
- How the model works: the specification and priors.
- Diagnostics: R-hat, effective sample size, divergences, in-sample coverage.
- Data notes: how listings were cleaned, plus a small CSV upload summary.

## Tests

```bash
pip install -r requirements-dev.txt
python -m pytest -q
```

Extra suites: `-m slow` (fits PyMC), `-m trace` (needs `git lfs pull`), `-m e2e` (needs `python -m playwright install chromium`).

## Rebuild the artifacts

```bash
git lfs pull
pip install -r requirements-model.txt
python scripts/build_artifacts.py
```

## Troubleshooting

- `ModuleNotFoundError`: install the right requirements file (see above) inside the venv.
- Port in use: `streamlit run app.py --server.port 8502`.
- Tables fail to render with a pyarrow/NumPy error: use the pins in `requirements.txt` (NumPy 1.26, pyarrow 17).

See README.md for the model and the verified numbers.

# dashboard/

Code behind the Streamlit app (`app.py` at the repo root is the shell).

- `pages/`: one module per page (`predict`, `neighborhoods`, `model`, `diagnostics`, `data_notes`), each with a `render()` function.
- `components/`: the specimen grid (`specimen.py`, `specimen_template.html`), Plotly charts, readouts.
- `utils/`: `artifacts.py` (loads `outputs/app_artifacts/`), `posterior.py` (constants and interval math), CSV upload helpers (`schema_detector.py`, `csv_handler.py`, `data_loader.py`), `session_manager.py`.
- `theme.py`: color and type tokens that feed both the CSS and the Plotly template.

Run from the repo root: `streamlit run app.py`. See the top-level README.md for the model, tests and deploy notes.

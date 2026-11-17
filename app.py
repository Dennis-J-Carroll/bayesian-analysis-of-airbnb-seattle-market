"""Seattle Airbnb, Bayesian price model: app shell and navigation.

Entry points: `streamlit run app.py` or, on Streamlit Cloud, expert_dashboard.py.
"""

from typing import Callable

import streamlit as st

from dashboard.pages import data_notes, diagnostics, model, neighborhoods, predict
from dashboard.theme import apply_theme
from dashboard.utils.session_manager import AppState

REPO_URL = (
    "https://github.com/Dennis-J-Carroll/bayesian-analysis-of-airbnb-seattle-market"
)

PAGES: list[tuple[str, str, Callable[[], None]]] = [
    ("Predict", "predict", predict.render),
    ("Neighborhoods", "neighborhoods", neighborhoods.render),
    ("How the model works", "model", model.render),
    ("Diagnostics", "diagnostics", diagnostics.render),
    ("Data notes", "data-notes", data_notes.render),
]


def main() -> None:
    st.set_page_config(layout="wide", page_title="Seattle Airbnb, Bayesian price model")
    AppState.init()
    with st.sidebar:
        st.markdown("**SEATTLE / BAYES**")
        st.caption("Hierarchical price model, 88 neighborhoods")
        # Seed the widget from the stored theme once; afterwards the widget
        # owns its value (a changing `value=` argument would reset it).
        st.session_state.setdefault("dark_toggle", AppState.theme() == "dark")
        dark = st.toggle("Dark", key="dark_toggle")
        st.session_state[AppState.THEME] = "dark" if dark else "light"
        st.markdown(f"[Source on GitHub]({REPO_URL})")
    apply_theme(AppState.theme())

    pages = [
        st.Page(fn, title=title, url_path=path, default=(i == 0))
        for i, (title, path, fn) in enumerate(PAGES)
    ]
    st.navigation(pages).run()


if __name__ == "__main__":
    main()

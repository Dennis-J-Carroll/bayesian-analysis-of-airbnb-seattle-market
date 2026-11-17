"""Session state: the only thing that persists across reruns is the theme."""

import streamlit as st


class AppState:
    """Session state keys and accessors."""

    THEME = "theme"  # "light" | "dark"

    @staticmethod
    def init() -> None:
        """Set defaults without overwriting what is already there."""
        if AppState.THEME not in st.session_state:
            st.session_state[AppState.THEME] = "light"

    @staticmethod
    def theme() -> str:
        return st.session_state.get(AppState.THEME, "light")

"""Type-safe session state management."""
from dataclasses import dataclass
from typing import Optional
import streamlit as st
import pandas as pd


@dataclass
class AppState:
    """Type-safe session state keys."""

    DATA_SOURCE: str = "data_source"  # "default" | "uploaded"
    UPLOADED_DF: str = "uploaded_df"
    COLUMN_MAP: str = "column_map"
    MODEL: str = "model"
    THEME: str = "theme"  # "modern_neutral" | "deep_forest"
    CURRENT_PAGE: str = "current_page"
    UPLOAD_VALIDATED: str = "upload_validated"

    @staticmethod
    def init():
        """Initialize session state with defaults."""
        defaults = {
            AppState.DATA_SOURCE: "default",
            AppState.THEME: "modern_neutral",
            AppState.CURRENT_PAGE: "overview",
            AppState.UPLOAD_VALIDATED: False,
        }
        for key, val in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = val

    @staticmethod
    def get_active_df() -> pd.DataFrame:
        """Get currently active DataFrame (uploaded or default)."""
        if st.session_state.get(AppState.DATA_SOURCE) == "uploaded":
            uploaded = st.session_state.get(AppState.UPLOADED_DF)
            if uploaded is not None:
                return uploaded
            # Fallback if corrupted
            st.session_state[AppState.DATA_SOURCE] = "default"
        return st.session_state["default_df"]

    @staticmethod
    def reset_to_default():
        """Clear uploaded data, reset to default dataset."""
        for key in [AppState.UPLOADED_DF, AppState.COLUMN_MAP]:
            st.session_state.pop(key, None)
        st.session_state[AppState.DATA_SOURCE] = "default"
        st.rerun()

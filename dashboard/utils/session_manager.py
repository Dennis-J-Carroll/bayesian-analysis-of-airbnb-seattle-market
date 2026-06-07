"""Type-safe session state management."""
from dataclasses import dataclass
from pathlib import Path
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
        if "default_df" not in st.session_state:
            st.session_state["default_df"] = load_default_data()

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


def load_default_data() -> pd.DataFrame:
    """Load default Seattle Airbnb dataset.

    Returns:
        Seattle listing data with required columns
    """
    root = Path(__file__).parent.parent.parent
    data_path = root / "data" / "seattle_listings.csv"
    if not data_path.exists():
        data_path = root / "data" / "raw" / "listings.csv"

    if not data_path.exists():
        # Fallback: generate minimal synthetic data for development
        return pd.DataFrame(
            {
                "price": [100, 150, 200] * 100,
                "neighbourhood_cleansed": ["Capitol Hill", "Ballard", "Fremont"] * 100,
                "room_type": ["Entire home/apt", "Private room", "Shared room"] * 100,
                "accommodates": [2, 4, 1] * 100,
                "bedrooms": [1, 2, 0] * 100,
                "bathrooms": [1, 1.5, 1] * 100,
                "beds": [1, 2, 1] * 100,
                "availability_365": [100, 200, 50] * 100,
                "review_scores_rating": [4.5, 4.8, 4.2] * 100,
            }
        )

    df = pd.read_csv(data_path)
    if "price" in df.columns and df["price"].dtype == object:
        df["price"] = pd.to_numeric(
            df["price"].str.replace(r"[\$,]", "", regex=True), errors="coerce"
        )
    return df[df["price"].notna()].reset_index(drop=True)

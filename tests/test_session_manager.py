# tests/test_session_manager.py
import pytest
import pandas as pd
from unittest.mock import MagicMock
from dashboard.utils.session_manager import AppState


def test_appstate_keys_are_strings():
    """All AppState keys are string constants."""
    assert isinstance(AppState.DATA_SOURCE, str)
    assert isinstance(AppState.UPLOADED_DF, str)
    assert isinstance(AppState.THEME, str)


def test_appstate_init_sets_defaults(monkeypatch):
    """init() sets default values in session_state."""
    mock_st = MagicMock()
    mock_st.session_state = {}
    monkeypatch.setattr("dashboard.utils.session_manager.st", mock_st)

    AppState.init()

    assert mock_st.session_state[AppState.DATA_SOURCE] == "default"
    assert mock_st.session_state[AppState.THEME] == "modern_neutral"
    assert mock_st.session_state[AppState.UPLOAD_VALIDATED] == False


def test_get_active_df_returns_uploaded_when_set(monkeypatch):
    """get_active_df() returns uploaded df when DATA_SOURCE='uploaded'."""
    mock_st = MagicMock()
    test_df = pd.DataFrame({"price": [100, 200]})
    mock_st.session_state = {
        AppState.DATA_SOURCE: "uploaded",
        AppState.UPLOADED_DF: test_df,
        "default_df": pd.DataFrame({"price": [999]}),
    }
    monkeypatch.setattr("dashboard.utils.session_manager.st", mock_st)

    result = AppState.get_active_df()

    assert result.equals(test_df)


def test_get_active_df_returns_default_when_no_upload(monkeypatch):
    """get_active_df() returns default df when no upload."""
    mock_st = MagicMock()
    default_df = pd.DataFrame({"price": [999]})
    mock_st.session_state = {AppState.DATA_SOURCE: "default", "default_df": default_df}
    monkeypatch.setattr("dashboard.utils.session_manager.st", mock_st)

    result = AppState.get_active_df()

    assert result.equals(default_df)


def test_get_active_df_handles_corrupted_upload(monkeypatch):
    """get_active_df() falls back to default if uploaded df is None."""
    mock_st = MagicMock()
    default_df = pd.DataFrame({"price": [999]})
    mock_st.session_state = {
        AppState.DATA_SOURCE: "uploaded",
        AppState.UPLOADED_DF: None,  # Corrupted state
        "default_df": default_df,
    }
    monkeypatch.setattr("dashboard.utils.session_manager.st", mock_st)

    result = AppState.get_active_df()

    # Should reset to default and return default_df
    assert mock_st.session_state[AppState.DATA_SOURCE] == "default"
    assert result.equals(default_df)


def test_reset_to_default(monkeypatch):
    """reset_to_default() clears upload state and triggers rerun."""
    mock_st = MagicMock()
    mock_st.session_state = {
        AppState.DATA_SOURCE: "uploaded",
        AppState.UPLOADED_DF: pd.DataFrame({"price": [100]}),
        AppState.COLUMN_MAP: {"some": "map"},
    }
    monkeypatch.setattr("dashboard.utils.session_manager.st", mock_st)

    AppState.reset_to_default()

    # Verify upload keys removed
    assert AppState.UPLOADED_DF not in mock_st.session_state
    assert AppState.COLUMN_MAP not in mock_st.session_state
    # Verify DATA_SOURCE set to default
    assert mock_st.session_state[AppState.DATA_SOURCE] == "default"
    # Verify rerun called
    mock_st.rerun.assert_called_once()

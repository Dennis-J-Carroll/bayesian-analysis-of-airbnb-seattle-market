"""Pytest configuration: mock Streamlit UI primitives so unit tests run
outside of a real Streamlit session without needing 'toml' or a ScriptRunContext.
Also mocks arviz so tests pass on system Python where arviz/pymc are absent.
"""
import sys
from unittest.mock import MagicMock

# Mock arviz before any dashboard imports so lazy imports also succeed.
if "arviz" not in sys.modules:
    _az_mock = MagicMock()
    # InferenceData mock: has a .posterior attribute
    _idata_mock = MagicMock()
    _idata_mock.posterior = MagicMock()
    _az_mock.from_netcdf.return_value = _idata_mock
    sys.modules["arviz"] = _az_mock

import streamlit as st


class _MockCol:
    """Column mock that supports 'with col:' syntax and st.* attribute calls."""

    def __enter__(self):
        return self

    def __exit__(self, *_):
        pass

    def __getattr__(self, name):
        return MagicMock()


def _mock_columns(spec):
    n = spec if isinstance(spec, int) else len(spec)
    return [_MockCol() for _ in range(n)]


st.columns = _mock_columns
st.metric = MagicMock()
st.warning = MagicMock()
st.error = MagicMock()
st.info = MagicMock()
st.success = MagicMock()
st.plotly_chart = MagicMock()
st.dataframe = MagicMock()
st.markdown = MagicMock()
st.title = MagicMock()
st.subheader = MagicMock()
st.write = MagicMock()
st.pyplot = MagicMock()
st.selectbox = MagicMock(return_value="Capitol Hill")
st.multiselect = MagicMock(return_value=[])
st.slider = MagicMock(return_value=1)
st.number_input = MagicMock(return_value=1)
st.text_input = MagicMock(return_value="")
st.button = MagicMock(return_value=False)
st.file_uploader = MagicMock(return_value=None)
st.expander = MagicMock()
st.tabs = MagicMock(return_value=[_MockCol() for _ in range(3)])
st.cache_resource = lambda f: f
st.cache_data = lambda f: f
st.session_state = {}
st.rerun = MagicMock()
st.stop = MagicMock()
st.toggle = MagicMock(return_value=False)
st.status = MagicMock()
st.popover = MagicMock()
st.fragment = lambda f=None, **kw: (f if f is not None else lambda fn: fn)

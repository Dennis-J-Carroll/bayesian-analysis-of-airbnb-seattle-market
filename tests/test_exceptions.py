# tests/test_exceptions.py
import pytest
from dashboard.utils.exceptions import (
    DashboardException,
    ValidationError,
    ColumnMappingError,
    InsufficientDataError,
    ModelLoadError,
    PredictionError,
)


def test_exception_hierarchy():
    """All exceptions inherit from DashboardException."""
    assert issubclass(ValidationError, DashboardException)
    assert issubclass(ColumnMappingError, ValidationError)
    assert issubclass(InsufficientDataError, ValidationError)
    assert issubclass(ModelLoadError, DashboardException)
    assert issubclass(PredictionError, DashboardException)


def test_column_mapping_error_stores_missing():
    """ColumnMappingError stores missing column list."""
    missing = ["price", "neighborhood"]
    err = ColumnMappingError(missing)
    assert err.missing_columns == missing
    assert "price" in str(err)
    assert "neighborhood" in str(err)


def test_insufficient_data_error_stores_counts():
    """InsufficientDataError stores row counts."""
    err = InsufficientDataError(rows=30, min_required=50)
    assert err.rows == 30
    assert err.min_required == 50
    assert "30" in str(err)
    assert "50" in str(err)

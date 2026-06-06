"""Custom exception hierarchy for dashboard errors."""


class DashboardException(Exception):
    """Base exception for all dashboard errors."""

    pass


class ValidationError(DashboardException):
    """Data validation failed."""

    pass


class ColumnMappingError(ValidationError):
    """Required column not found or mapping failed."""

    def __init__(self, missing_columns: list[str]):
        self.missing_columns = missing_columns
        super().__init__(f"Missing required columns: {', '.join(missing_columns)}")


class InsufficientDataError(ValidationError):
    """Dataset too small for analysis."""

    def __init__(self, rows: int, min_required: int = 50):
        self.rows = rows
        self.min_required = min_required
        super().__init__(f"Dataset has {rows} rows, minimum {min_required} required")


class ModelLoadError(DashboardException):
    """PyMC model failed to load."""

    pass


class PredictionError(DashboardException):
    """Prediction generation failed."""

    pass

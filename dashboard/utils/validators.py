# dashboard/utils/validators.py
"""Data validation for uploaded CSVs."""
import pandas as pd
import yaml
from pathlib import Path
from .exceptions import ColumnMappingError, InsufficientDataError, ValidationError


def load_validation_rules() -> dict:
    """Load validation rules from YAML.

    Returns:
        Dict with required_columns, bounds, etc.
    """
    config_path = Path(__file__).parent.parent / "config" / "column_aliases.yaml"
    with open(config_path) as f:
        config = yaml.safe_load(f)
        return config["validation_rules"]


def validate_schema(df: pd.DataFrame) -> list[str]:
    """Validate dataframe has required columns.

    Args:
        df: Dataframe with standard column names (after schema detection)

    Returns:
        List of warnings for missing optional columns

    Raises:
        ColumnMappingError: If required columns are missing
    """
    rules = load_validation_rules()
    required = set(rules["required_columns"])
    optional = set(rules.get("optional_columns", []))

    present = set(df.columns)
    missing_required = required - present

    if missing_required:
        raise ColumnMappingError(list(missing_required))

    missing_optional = optional - present
    warnings = []
    if missing_optional:
        warnings.append(f"Missing optional columns: {', '.join(missing_optional)}")

    return warnings


def validate_data_quality(df: pd.DataFrame) -> list[str]:
    """Validate data quality (types, bounds, missing values).

    Args:
        df: Dataframe with standard column names

    Returns:
        List of warnings for quality issues

    Raises:
        InsufficientDataError: If dataframe has too few rows
        ValidationError: If critical quality issues found
    """
    rules = load_validation_rules()
    warnings = []

    # Minimum row count
    min_rows = 10
    if len(df) < min_rows:
        raise InsufficientDataError(len(df), min_rows)

    # Type validation
    numeric_cols = rules.get("numeric_columns", [])
    integer_cols = rules.get("integer_columns", [])

    for col in numeric_cols:
        if col not in df.columns:
            continue

        if not pd.api.types.is_numeric_dtype(df[col]):
            raise ValidationError(
                f"Column '{col}' must be numeric, got {df[col].dtype}"
            )

    for col in integer_cols:
        if col not in df.columns:
            continue

        # Check if values are integer-like (allow NaN)
        non_null = df[col].dropna()
        if len(non_null) > 0 and not all(non_null == non_null.astype(int)):
            warnings.append(f"Column '{col}' expected integers, found decimal values")

    # Bounds validation
    bounds = rules.get("bounds", {})
    for col, limits in bounds.items():
        if col not in df.columns:
            continue

        non_null = df[col].dropna()
        if len(non_null) == 0:
            continue

        min_val = limits.get("min")
        max_val = limits.get("max")

        if min_val is not None:
            below_min = (non_null < min_val).sum()
            if below_min > 0:
                warnings.append(f"{col}: {below_min} values below minimum ({min_val})")

        if max_val is not None:
            above_max = (non_null > max_val).sum()
            if above_max > 0:
                warnings.append(f"{col}: {above_max} values above maximum ({max_val})")

    # Missing value check
    for col in df.columns:
        missing_pct = df[col].isna().mean() * 100
        if missing_pct > 50:
            warnings.append(f"{col}: {missing_pct:.0f}% missing values")

    return warnings

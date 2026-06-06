# dashboard/utils/csv_handler.py
"""CSV upload processing pipeline."""
import pandas as pd
from typing import BinaryIO, TextIO
from .schema_detector import detect_mapping
from .validators import validate_schema, validate_data_quality
from .exceptions import ColumnMappingError, InsufficientDataError, ValidationError

MAX_FILE_SIZE_MB = 100


def process_upload(file: BinaryIO | TextIO, filename: str) -> dict:
    """Process uploaded CSV file through validation pipeline.

    Args:
        file: Uploaded file object (from st.file_uploader)
        filename: Original filename

    Returns:
        Dict with:
        - success: bool
        - df: pd.DataFrame (if success)
        - warnings: list[str] (if success)
        - error: str (if failure)
        - error_type: str (if failure) - "schema", "quality", "size", "format"
    """
    try:
        # Check file size
        file.seek(0, 2)  # Seek to end
        size_bytes = file.tell()
        file.seek(0)  # Reset to start

        max_bytes = MAX_FILE_SIZE_MB * 1024 * 1024
        if size_bytes > max_bytes:
            return {
                "success": False,
                "error": f"File too large ({size_bytes / 1024 / 1024:.1f}MB). Maximum is {MAX_FILE_SIZE_MB}MB.",
                "error_type": "size",
            }

        # Read CSV
        df = pd.read_csv(file)

        # Schema detection
        df = detect_mapping(df)

        # Schema validation
        schema_warnings = validate_schema(df)

        # Data quality validation
        quality_warnings = validate_data_quality(df)

        warnings = schema_warnings + quality_warnings

        return {"success": True, "df": df, "warnings": warnings}

    except ColumnMappingError as e:
        return {
            "success": False,
            "error": f"Missing required columns: {', '.join(e.missing_columns)}",
            "error_type": "schema",
        }

    except InsufficientDataError as e:
        return {
            "success": False,
            "error": f"Not enough data: {e.rows} rows (need at least {e.min_required})",
            "error_type": "quality",
        }

    except ValidationError as e:
        return {"success": False, "error": str(e), "error_type": "quality"}

    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to parse CSV: {str(e)}",
            "error_type": "format",
        }

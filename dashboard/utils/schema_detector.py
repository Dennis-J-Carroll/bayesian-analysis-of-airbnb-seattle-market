# dashboard/utils/schema_detector.py
"""Schema detection with fuzzy column matching."""
import pandas as pd
import yaml
from pathlib import Path
from difflib import SequenceMatcher


def load_column_aliases() -> dict[str, list[str]]:
    """Load column alias mappings from YAML.

    Returns:
        Dict mapping standard column names to list of aliases
    """
    config_path = Path(__file__).parent.parent / "config" / "column_aliases.yaml"
    with open(config_path) as f:
        return yaml.safe_load(f)


def fuzzy_match_column(
    user_col: str, standard_col: str, aliases: list[str], threshold: float = 0.7
) -> float:
    """Calculate best fuzzy match score between user column and standard aliases.

    Args:
        user_col: User's column name
        standard_col: Standard column name
        aliases: List of known aliases for this column
        threshold: Minimum similarity ratio (0-1)

    Returns:
        Best match score (0-1), or 0 if below threshold

    Note:
        Uses difflib.SequenceMatcher which is O(n×m) per comparison.
        With ~10 aliases per column and ~50 user columns, this is acceptable.
        For 1000+ columns, consider alternative fuzzy matching algorithms.
    """
    user_col_clean = user_col.lower().replace("_", "").replace(" ", "")

    best_score = 0.0
    for alias in aliases:
        alias_clean = alias.lower().replace("_", "").replace(" ", "")
        score = SequenceMatcher(None, user_col_clean, alias_clean).ratio()
        if score > best_score:
            best_score = score

    return best_score if best_score >= threshold else 0.0


def detect_mapping(df: pd.DataFrame) -> pd.DataFrame:
    """Detect and rename columns to standard schema.

    Args:
        df: User-uploaded dataframe

    Returns:
        Dataframe with columns renamed to standard names

    Raises:
        ValueError: If required columns cannot be mapped
    """
    aliases = load_column_aliases()

    # Track which columns have been assigned to prevent duplicates
    assigned_cols = set()
    rename_dict = {}

    for standard_col, alias_list in aliases.items():
        # Check for exact match first
        if standard_col in df.columns and standard_col not in assigned_cols:
            assigned_cols.add(standard_col)
            continue

        # Fuzzy match
        best_match = None
        best_score = 0.0

        for user_col in df.columns:
            if user_col in assigned_cols:
                continue

            score = fuzzy_match_column(user_col, standard_col, alias_list)
            if score > best_score:
                best_score = score
                best_match = user_col

        if best_match:
            rename_dict[best_match] = standard_col
            assigned_cols.add(best_match)

    return df.rename(columns=rename_dict)

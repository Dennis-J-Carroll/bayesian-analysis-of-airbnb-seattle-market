"""
Single data-cleaning rule for the dashboard.

The rule matches src/hierarchical_bayesian_model.py (load_and_clean_data):
drop rows with no price, drop rows missing accommodates or neighbourhood,
then keep prices in [PRICE_MIN, PRICE_MAX].
"""

from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import streamlit as st

PRICE_MIN: float = 10.0
PRICE_MAX: float = 1000.0
LISTINGS_PATH: Path = (
    Path(__file__).resolve().parents[2] / "data" / "raw" / "listings.csv"
)


@dataclass(frozen=True)
class CleaningReport:
    rows_raw: int
    missing_price: int
    missing_other: int
    below_min: int
    above_max: int
    rows_kept: int


def parse_price(s: pd.Series) -> pd.Series:
    """Parse strings like "$1,234.00" to float; NaN where unparseable."""
    text = s.astype("string").str.replace(r"[$,]", "", regex=True)
    return pd.to_numeric(text, errors="coerce").astype(float)


def clean_listings(raw: pd.DataFrame) -> tuple[pd.DataFrame, CleaningReport]:
    """Apply the training cleaning rule; return cleaned rows and step counts."""
    df = raw.copy()
    df["price"] = parse_price(df["price"])

    has_price = df["price"].notna()
    missing_price = int((~has_price).sum())
    df = df[has_price]

    has_other = df[["accommodates", "neighbourhood_cleansed"]].notna().all(axis=1)
    missing_other = int((~has_other).sum())
    df = df[has_other]

    below_min = int((df["price"] < PRICE_MIN).sum())
    above_max = int((df["price"] > PRICE_MAX).sum())
    df = df[(df["price"] >= PRICE_MIN) & (df["price"] <= PRICE_MAX)]

    df = df.reset_index(drop=True)
    report = CleaningReport(
        rows_raw=len(raw),
        missing_price=missing_price,
        missing_other=missing_other,
        below_min=below_min,
        above_max=above_max,
        rows_kept=len(df),
    )
    return df, report


def neighborhood_order(clean: pd.DataFrame) -> list[str]:
    """Neighborhood names in order of first appearance (matches training index)."""
    return list(clean["neighbourhood_cleansed"].unique())


@st.cache_data
def load_listings(path: Path = LISTINGS_PATH) -> pd.DataFrame:
    """Read the listings CSV and return the cleaned frame."""
    clean, _ = clean_listings(pd.read_csv(path))
    return clean

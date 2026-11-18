import numpy as np
import pandas as pd

from dashboard.utils.data_loader import (
    LISTINGS_PATH,
    CleaningReport,
    clean_listings,
    neighborhood_order,
    parse_price,
)


def _fixture(repo_root):
    return pd.read_csv(repo_root / "tests" / "fixtures" / "listings_small.csv")


def test_parse_price_handles_currency_strings():
    out = parse_price(pd.Series(["$1,234.00", "$45.00", None, "abc"]))
    expected = np.array([1234.0, 45.0, np.nan, np.nan])
    np.testing.assert_array_equal(out.to_numpy(), expected)


def test_clean_listings_counts_each_step(repo_root):
    clean, report = clean_listings(_fixture(repo_root))
    assert report == CleaningReport(
        rows_raw=10,
        missing_price=1,
        missing_other=2,
        below_min=1,
        above_max=2,
        rows_kept=4,
    )
    assert (
        report.rows_raw
        - report.missing_price
        - report.missing_other
        - report.below_min
        - report.above_max
        == report.rows_kept
    )
    assert list(clean["id"]) == [2, 7, 9, 10]
    assert list(clean.index) == [0, 1, 2, 3]
    assert clean["price"].dtype == float


def test_clean_listings_real_file_counts():
    _, report = clean_listings(pd.read_csv(LISTINGS_PATH))
    assert report == CleaningReport(6862, 635, 0, 0, 83, 6144)


def test_neighborhood_order_is_first_appearance(repo_root):
    clean, _ = clean_listings(_fixture(repo_root))
    assert neighborhood_order(clean) == ["Zeta Hood", "Alpha Hood"]


def test_neighborhood_order_real_file_has_88_names():
    clean, _ = clean_listings(pd.read_csv(LISTINGS_PATH))
    assert len(neighborhood_order(clean)) == 88

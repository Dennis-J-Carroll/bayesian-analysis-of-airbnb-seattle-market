"""pyarrow must import under the pinned NumPy 1.26 (it crashes st.dataframe otherwise)."""

import pandas as pd


def test_pyarrow_imports_and_converts():
    import pyarrow

    table = pyarrow.Table.from_pandas(pd.DataFrame({"a": [1, 2], "b": ["x", "y"]}))
    assert table.num_rows == 2

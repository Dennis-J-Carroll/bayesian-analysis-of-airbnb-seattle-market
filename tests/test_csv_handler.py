# tests/test_csv_handler.py
import pandas as pd
from io import StringIO


def test_process_upload_success():
    """Test successful CSV processing."""
    from dashboard.utils.csv_handler import process_upload

    csv_content = """Price,Neighborhood,Room Type,Max Guests,Bedrooms,Bathrooms,Beds,Available Days,Rating
100,Capitol Hill,Entire home/apt,2,1,1,1,100,4.5
200,Ballard,Private room,4,2,1.5,2,200,4.8
150,Fremont,Entire home/apt,3,1,1,1,150,4.6
180,Wallingford,Private room,2,1,1,1,120,4.7
220,Green Lake,Entire home/apt,4,2,1.5,2,180,4.9
190,University District,Private room,2,1,1,1,140,4.5
210,Capitol Hill,Entire home/apt,3,1,1,1,160,4.8
170,Ballard,Private room,2,1,1,1,130,4.6
230,Fremont,Entire home/apt,4,2,1.5,2,190,4.9
200,Wallingford,Private room,3,1,1,1,150,4.7
"""

    file = StringIO(csv_content)

    result = process_upload(file, "test.csv")

    assert result["success"] is True
    assert isinstance(result["df"], pd.DataFrame)
    assert "price" in result["df"].columns
    assert len(result["warnings"]) >= 0


def test_process_upload_missing_columns():
    """Test CSV processing with missing required columns."""
    from dashboard.utils.csv_handler import process_upload

    csv_content = """Price,Neighborhood
100,Capitol Hill
200,Ballard
"""

    file = StringIO(csv_content)

    result = process_upload(file, "test.csv")

    assert result["success"] is False
    assert "error" in result
    assert "room_type" in result["error"].lower()

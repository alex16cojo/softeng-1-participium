from __future__ import annotations

from datetime import datetime
from participium.core.utils import utcnow
from participium.core.utils import parse_date
from participium.core.utils import build_csv
import pytest


def test_utcnow():
    date = utcnow()
    assert isinstance(date, datetime)


def test_parse_data():
    date_str = "2024-05-10T14:30:00"
    null_str = ""
    invalid_str = "28//03/2015"

    date = parse_date(date_str)

    assert date == datetime(2024, 5, 10, 14, 30, 0)
    assert parse_date(null_str) is None

    with pytest.raises(ValueError):
        parse_date(invalid_str)


def test_build_csv():
    rows = [
        {"id": 1, "name": "Mario", "username": "rossi"},
        {"id": 2, "name": "Luigi", "username": "bianchi"},
    ]

    result = build_csv(rows, ["id", "name", "username"])

    assert "id,name,username" in result
    assert "1,Mario,rossi" in result
    assert "2,Luigi,bianchi" in result

    result_empty = build_csv([], ["id", "name", "username"])

    assert result_empty == "id,name,username\r\n"

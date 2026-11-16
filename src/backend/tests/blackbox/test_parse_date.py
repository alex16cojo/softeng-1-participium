from __future__ import annotations

import pytest

from datetime import datetime
from participium.core.utils import parse_date

VALID_ISO_DATE = "2026-04-21"
INVALID_FORMAT_DATE = "21-04-2026"

@pytest.fixture
def seed_parse_date_data() -> None:
    pass


# TC-1: Input valido (ISO-8601)
@pytest.mark.skip(reason="Disabled.")
def test_parse_date_tc1(seed_parse_date_data: None) -> None:
    result = parse_date(VALID_ISO_DATE)
    assert isinstance(result, datetime)
    assert result.year == 2026
    assert result.month == 4
    assert result.day == 21


# TC-2: Input malformato
@pytest.mark.skip(reason="Disabled.")
def test_parse_date_tc2(seed_parse_date_data: None) -> None:
    with pytest.raises(ValueError):
        parse_date(INVALID_FORMAT_DATE)


# TC-3: Input stringa non valida
@pytest.mark.skip(reason="Disabled.")
def test_parse_date_tc5(seed_parse_date_data: None) -> None:
    value = "data"
    with pytest.raises(ValueError):
        parse_date(value)


# TC-4: Input None
@pytest.mark.skip(reason="Disabled.")
def test_parse_date_tc3(seed_parse_date_data: None) -> None:
    value = None
    assert parse_date(value) is None


# TC-5: Input stringa vuota
@pytest.mark.skip(reason="Disabled.")
def test_parse_date_tc4(seed_parse_date_data: None) -> None:
    value = ""
    assert parse_date(value) is None
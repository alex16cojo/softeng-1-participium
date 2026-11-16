from __future__ import annotations

import pytest
from io import BytesIO
from werkzeug.datastructures import FileStorage

from participium.core.exceptions import ValidationError
from participium.models.user import User
from participium.models.report import Report
from participium.services.report_service import ReportService

VALID_USER = User(
    id=101,
    username="mario.rossi",
    first_name="Mario",
    last_name="Rossi",
    email="m.rossi@email.com",
    password_hash="HASHED_PASSWORD_MARIO",
    is_active=True,
    is_email_verified=True,
)

PHOTO_1 = FileStorage(stream=BytesIO(b""), filename="f1.jpg", content_type="image/jpeg")
PHOTO_2 = FileStorage(stream=BytesIO(b""), filename="f2.jpg", content_type="image/jpeg")
PHOTO_3 = FileStorage(stream=BytesIO(b""), filename="f3.jpg", content_type="image/jpeg")
PHOTO_4 = FileStorage(stream=BytesIO(b""), filename="f4.jpg", content_type="image/jpeg")
PHOTO_EMPTY_NAME = FileStorage(stream=BytesIO(b""), filename="")

TRE_FOTO = [PHOTO_1, PHOTO_2, PHOTO_3]
UNA_FOTO = [PHOTO_1]


@pytest.fixture
def seed_create_report_data() -> None:
    pass


@pytest.mark.skip(reason="Disabled.")
@pytest.mark.parametrize(
    "category_id, title, description, latitude, longitude, photos, is_anonymous, expected",
    [
        # Casi di successo
        (1, "Fuga", "abc", 47.1, 7.5, TRE_FOTO, False, "Success"),  # TC-1
        ("1", "Fuga", "abc", "47.1", "7.5", UNA_FOTO, True, "Success"),  # TC-2

        # Errori su category_id
        ("", "Fuga", "abc", 47.1, 7.5, TRE_FOTO, False, ValidationError),  # TC-3
        ("categoria1", "Fuga", "abc", 47.1, 7.5, TRE_FOTO, False, ValidationError),  # TC-4
        (None, "Fuga", "abc", 47.1, 7.5, TRE_FOTO, False, ValidationError),  # TC-5
        (2, "Fuga", "abc", 47.1, 7.5, TRE_FOTO, False, ValidationError),  # TC-6
        (3, "Fuga", "abc", 47.1, 7.5, TRE_FOTO, False, ValidationError),  # TC-7

        # Errori su title/description
        (1, "", "abc", 47.1, 7.5, TRE_FOTO, False, ValidationError),  # TC-8
        (1, None, "abc", 47.1, 7.5, TRE_FOTO, False, ValidationError),  # TC-9
        (1, "Fuga", "", 47.1, 7.5, TRE_FOTO, False, ValidationError),  # TC-10
        (1, "Fuga", None, 47.1, 7.5, TRE_FOTO, False, ValidationError),  # TC-11

        # Errori su latitude/longitude
        (1, "Fuga", "abc", "", 7.5, TRE_FOTO, False, ValidationError),  # TC-12
        (1, "Fuga", "abc", "lat", 7.5, TRE_FOTO, False, ValidationError),  # TC-13
        (1, "Fuga", "abc", None, 7.5, TRE_FOTO, False, ValidationError),  # TC-14
        (1, "Fuga", "abc", 47.1, "", TRE_FOTO, False, ValidationError),  # TC-15
        (1, "Fuga", "abc", 47.1, "long", TRE_FOTO, False, ValidationError),  # TC-16
        (1, "Fuga", "abc", 47.1, None, TRE_FOTO, False, ValidationError),  # TC-17

        # Errori su photos
        (1, "Fuga", "abc", 47.1, 7.5, [], False, ValidationError),  # TC-18
        (1, "Fuga", "abc", 47.1, 7.5, [PHOTO_EMPTY_NAME], False, ValidationError),  # TC-19
        (1, "Fuga", "abc", 47.1, 7.5, [PHOTO_1, PHOTO_2, PHOTO_3, PHOTO_4], False, ValidationError),  # TC-20
    ]
)
def test_create_report_all_in_one(seed_create_report_data: None, category_id, title, description, latitude, longitude, photos, is_anonymous, expected) -> None:
    report_service = ReportService()

    if expected == "Success":
        result = report_service.create_report(
            reporter=VALID_USER,
            category_id=category_id,
            title=title,
            description=description,
            latitude=latitude,
            longitude=longitude,
            photos=photos,
            is_anonymous=is_anonymous
        )

        assert isinstance(result, Report)
        assert result.reporter == VALID_USER
        assert int(result.category_id) == 1
        assert result.title == "Fuga"
        assert result.description == "abc"
        assert float(result.latitude) == 47.1
        assert float(result.longitude) == 7.5
        assert len(result.photos) == len(photos)
        assert result.is_anonymous == is_anonymous

    else:
        with pytest.raises(expected):
            report_service.create_report(
                reporter=VALID_USER,
                category_id=category_id,
                title=title,
                description=description,
                latitude=latitude,
                longitude=longitude,
                photos=photos,
                is_anonymous=is_anonymous
            )
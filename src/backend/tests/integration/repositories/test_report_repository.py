from __future__ import annotations

from datetime import datetime

import pytest

from participium.database import close_connection, create_all, get_session, open_connection
from participium.models.enums import ReportStatus, Role
from participium.models.report import Report, ReportFollower, ReportPhoto, ReportStatusHistory
from participium.models.user import User
from participium.repositories.report_repository import ReportRepository


def _user(user_id, username):
    return User(id=user_id, username=username, first_name=username, last_name="test",
                email=f"{username}@mail.com", password_hash="pass")


def _report(report_id, title, status, category_id, reporter_id):
    r = Report(id=report_id, title=title, description="desc", latitude=1.0, longitude=1.0, is_anonymous=False,
               status=status, rejection_reason=None, reporter_id=reporter_id, category_id=category_id)
    return r


def _photo(photo_id, report_id):
    return ReportPhoto(id=photo_id, report_id=report_id, file_path=f"/tmp/{photo_id}.jpg",
                       original_filename=f"{photo_id}.jpg", content_type="image/jpeg")


def _status_entry(entry_id, report_id, previous_status, new_status, changed_by_id):
    return ReportStatusHistory(id=entry_id, report_id=report_id, previous_status=previous_status,
                               new_status=new_status, note="note", changed_by_id=changed_by_id)


def _follower(follower_id, report_id, user_id):
    return ReportFollower(id=follower_id, report_id=report_id, user_id=user_id)


@pytest.fixture
def init_session(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite+pysqlite:///:memory:")
    open_connection()
    create_all()
    session = get_session()
    yield session
    close_connection()


@pytest.fixture
def populate_db(init_session):
    u1 = _user(1, "alessia")
    u2 = _user(2, "roberto")

    r1 = _report(1, "report1", ReportStatus.PENDING_APPROVAL, 1, 1)
    r2 = _report(2, "report2", ReportStatus.ASSIGNED, 1, 1)
    r3 = _report(3, "report3", ReportStatus.RESOLVED, 2, 2)

    r1.created_at = datetime(2025, 1, 1)
    r2.created_at = datetime(2025, 2, 1)
    r3.created_at = datetime(2025, 3, 1)

    init_session.add_all([u1, u2, r1, r2, r3])
    init_session.commit()

    return init_session


@pytest.fixture
def init_repository(populate_db):
    return ReportRepository(populate_db)


@pytest.mark.integration
def test_report_add(init_repository):
    repository = init_repository

    report = _report(4, "new_report", ReportStatus.PENDING_APPROVAL, 1, 1)

    repository.add(report)
    repository.session.commit()

    saved = repository.get_by_id(4)

    assert saved is not None
    assert saved.title == "new_report"


@pytest.mark.integration
def test_report_add_photo(init_repository):
    repository = init_repository

    photo = _photo(1, 1)

    repository.add_photo(photo)
    repository.session.commit()

    report = repository.get_by_id(1)

    assert len(report.photos) == 1
    assert report.photos[0].file_path == "/tmp/1.jpg"


@pytest.mark.integration
def test_report_add_status_entry(init_repository):
    repository = init_repository

    entry = _status_entry(1, 1, ReportStatus.PENDING_APPROVAL, ReportStatus.ASSIGNED, 1)

    repository.add_status_entry(entry)
    repository.session.commit()

    report = repository.get_by_id(1)

    assert len(report.status_history) == 1
    assert report.status_history[0].new_status == ReportStatus.ASSIGNED
    assert report.status_history[0].changed_by.id == 1


@pytest.mark.integration
def test_report_add_follower(init_repository):
    repository = init_repository

    follower = _follower(1, 1, 2)

    repository.add_follower(follower)
    repository.session.commit()

    saved = repository.get_follower(1, 2)

    assert saved is not None
    assert saved.report_id == 1
    assert saved.user_id == 2


@pytest.mark.integration
def test_report_remove_follower(init_repository):
    repository = init_repository

    follower = _follower(1, 1, 2)

    repository.add_follower(follower)
    repository.session.commit()

    repository.remove_follower(follower)
    repository.session.commit()

    result = repository.get_follower(1, 2)

    assert result is None
    
    
@pytest.mark.integration
def test_report_get_follower(init_repository):
    repository = init_repository

    repository.add_follower(_follower(1, 2, 1))
    repository.session.commit()

    follower1 = repository.get_follower(2, 1)
    follower2 = repository.get_follower(2, 99)

    assert follower1 is not None
    assert follower1.user_id == 1
    assert follower2 is None


@pytest.mark.integration
def test_report_list_followers(init_repository):
    repository = init_repository

    repository.add_follower(_follower(1, 1, 1))
    repository.add_follower(_follower(2, 1, 2))
    repository.session.commit()

    followers = repository.list_followers(1)

    ids = [f.user_id for f in followers]

    assert set(ids) == {1, 2}
    

@pytest.mark.integration
def test_report_get_by_id(init_repository):
    repository = init_repository

    report1 = repository.get_by_id(1)
    report2 = repository.get_by_id(99)

    assert report1.title == "report1"
    assert report2 is None


@pytest.mark.integration
def test_report_list_all(init_repository):
    repository = init_repository

    reports = repository.list_all()

    ids = [r.id for r in reports]

    assert ids == [3, 2, 1]


@pytest.mark.integration
def test_report_list_reports_by_category(init_repository):
    repository = init_repository

    reports = repository.list_reports(category_id=1)

    ids = [r.id for r in reports]

    assert ids == [2, 1]


@pytest.mark.integration
def test_report_list_reports_by_status(init_repository):
    repository = init_repository

    reports = repository.list_reports(status=ReportStatus.ASSIGNED)

    assert len(reports) == 1
    assert reports[0].id == 2


@pytest.mark.integration
def test_report_list_reports_by_date(init_repository):
    repository = init_repository

    reports = repository.list_reports(date_from=datetime(2025, 2, 1), date_to=datetime(2025, 3, 1), sort="asc")

    ids = [r.id for r in reports]

    assert ids == [2, 3]


@pytest.mark.integration
def test_report_list_reports_sort_asc(init_repository):
    repository = init_repository

    reports = repository.list_reports(sort="asc")

    ids = [r.id for r in reports]

    assert ids == [1, 2, 3]


@pytest.mark.integration
def test_report_list_user_reports(init_repository):
    repository = init_repository

    reports = repository.list_user_reports(1)

    ids = [r.id for r in reports]

    assert ids == [2, 1]


@pytest.mark.integration
def test_report_list_pending(init_repository):
    repository = init_repository

    reports = repository.list_pending()

    assert len(reports) == 1
    assert reports[0].id == 1


@pytest.mark.integration
def test_report_list_for_category(init_repository):
    repository = init_repository

    reports = repository.list_for_category(1)

    ids = [r.id for r in reports]

    assert ids == [2]


@pytest.mark.integration
def test_report_list_operator_reports_operator(init_repository):
    repository = init_repository

    reports = repository.list_operator_reports(Role.OPERATOR, 1)

    ids = [r.id for r in reports]

    assert ids == [2]


@pytest.mark.integration
def test_report_list_operator_reports_admin(init_repository):
    repository = init_repository

    reports = repository.list_operator_reports(Role.ADMIN)

    ids = [r.id for r in reports]

    assert set(ids) == {3, 2}


@pytest.mark.integration
def test_report_list_reports_public_only(init_repository):
    repository = init_repository

    reports = repository.list_reports(public_only=True)

    ids = [r.id for r in reports]

    assert set(ids) == {2, 3}


@pytest.mark.integration
def test_report_list_pending_with_category(init_repository):
    repository = init_repository

    reports = repository.list_pending(category_id=1)

    assert len(reports) == 1
    assert reports[0].id == 1


@pytest.mark.integration
def test_report_list_pending_with_dates(init_repository):
    repository = init_repository

    reports = repository.list_pending(
        date_from=datetime(2024, 12, 1),
        date_to=datetime(2025, 1, 15),
    )

    assert len(reports) == 1
    assert reports[0].id == 1


@pytest.mark.integration
def test_report_list_for_category_none(init_repository):
    repository = init_repository

    reports = repository.list_for_category(None)

    ids = [r.id for r in reports]

    assert set(ids) == {2, 3}
from __future__ import annotations

from datetime import datetime

import pytest

from participium.database import close_connection, create_all, get_session, open_connection
from participium.models.message import Message
from participium.models.report import Report
from participium.models.user import User
from participium.repositories.message_repository import MessageRepository


def _user(user_id, username):
    return User(id=user_id, username=username, first_name=username, last_name="test", email=f"{username}@mail.com", password_hash="pass")


def _report(report_id):
    return Report(id=report_id, title=f"report{report_id}", description="desc", latitude=1.0, longitude=1.0, is_anonymous=False, reporter_id=1, category_id=1)


def _message(message_id, report_id, sender_id, recipient_id, body):
    return Message(id=message_id, report_id=report_id, sender_id=sender_id, recipient_id=recipient_id, body=body)


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
    u1 = _user(1, "matteo")
    u2 = _user(2, "giovanni")
    r1 = _report(1)
    r2 = _report(2)

    m1 = _message(1, 1, 1, 2, "first")
    m2 = _message(2, 1, 2, 1, "second")
    m3 = _message(3, 2, 1, 2, "other")

    m1.created_at = datetime(2025, 1, 1)
    m2.created_at = datetime(2025, 2, 1)
    m3.created_at = datetime(2025, 3, 1)

    init_session.add_all([u1, u2, r1, r2, m1, m2, m3])
    init_session.commit()

    return init_session


@pytest.fixture
def init_repository(populate_db):
    return MessageRepository(populate_db)


@pytest.mark.integration
def test_message_add(init_repository):
    repository = init_repository

    message = _message(4, 1, 1, 2, "new message")

    repository.add(message)
    repository.session.commit()

    messages = repository.list_for_report(1)

    bodies = [m.body for m in messages]

    assert "new message" in bodies


@pytest.mark.integration
def test_message_list_for_report(init_repository):
    repository = init_repository

    messages = repository.list_for_report(1)

    ids = [m.id for m in messages]

    assert ids == [1, 2]


@pytest.mark.integration
def test_message_list_for_report_empty(init_repository):
    repository = init_repository

    messages = repository.list_for_report(999)

    assert messages == []
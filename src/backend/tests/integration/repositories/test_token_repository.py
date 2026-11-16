from __future__ import annotations

import pytest

from participium.database import close_connection, create_all, get_session, open_connection
from participium.models.user import User
from participium.models.token import EmailVerificationToken
from participium.repositories.token_repository import TokenRepository
from datetime import datetime, timedelta


def _user(user_id: int, username: str, first_name: str, last_name: str, email: str, password_hash: str) -> User:
    return User(
        id=user_id,
        username=username,
        first_name=first_name,
        last_name=last_name,
        email=email,
        password_hash=password_hash,
    )


def _token(token_id: int, user_id: int, token: str, expires_at: datetime, is_used: bool = False) -> EmailVerificationToken:
    return EmailVerificationToken(
        id=token_id,
        user_id=user_id,
        token=token,
        expires_at=expires_at,
        is_used=is_used,
    )


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

    init_session.add(_user(1, "mario.rossi", "Mario", "Rossi", "mario@gmail.com", "pass123!"))
    init_session.add(_user(2, "giada.bianchi", "Giada", "Bianchi", "giada@gmail.com", "pass456!"))
    init_session.add(_token(1, 1, "token-abc", datetime.now() + timedelta(days=1)))
    init_session.add(_token(2, 1, "token-def", datetime.now() + timedelta(days=2), is_used=True))
    init_session.add(_token(3, 2, "token-xyz", datetime.now() + timedelta(days=1)))
    init_session.commit()

    return init_session


@pytest.fixture
def init_repository(populate_db):
    return TokenRepository(populate_db)


@pytest.mark.integration
def test_token_add(init_repository):
    repository = init_repository

    new_token = _token(4, 1, "new-token", datetime.now() + timedelta(days=3))

    repository.add(new_token)
    repository.session.commit()

    saved = repository.get_by_token("new-token")

    assert saved is not None
    assert saved.token == "new-token"
    assert saved.user_id == 1


@pytest.mark.integration
def test_get_by_token(init_repository):
    repository = init_repository

    token1 = repository.get_by_token("token-abc")
    token2 = repository.get_by_token("does-not-exist")

    assert token1 is not None
    assert token1.user_id == 1
    assert token1.is_used is False

    assert token2 is None


@pytest.mark.integration
def test_list_for_user(init_repository):
    repository = init_repository

    tokens_user1 = repository.list_for_user(1)
    tokens_user2 = repository.list_for_user(2)
    tokens_user3 = repository.list_for_user(999)

    token_strings_user1 = [t.token for t in tokens_user1]

    assert set(token_strings_user1) == {"token-abc", "token-def"}

    assert len(tokens_user2) == 1
    assert tokens_user2[0].token == "token-xyz"

    assert tokens_user3 == []

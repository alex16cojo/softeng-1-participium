from __future__ import annotations

import pytest

from participium.database import close_connection, create_all, get_session, open_connection
from participium.models.user import User
from participium.repositories.user_repository import UserRepository


def _user(user_id: int, username: str, first_name: str, last_name: str, email: str, password_hash: str) -> User:
    return User(
        id=user_id,
        username=username,
        first_name=first_name,
        last_name=last_name,
        email=email,
        password_hash=password_hash,
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
    init_session.add(_user(1, "mario.rossi", "mario", "rossi", "mario@gmail.com", "passw123!"))
    init_session.add(_user(2, "giada.bianchi", "giada", "bianchi", "giada@gmail.com", "passw123!"))
    init_session.add(_user(3, "luigi.verdi", "luigi", "verdi", "luigi@gmail.com", "passw333!"))

    init_session.commit()

    return init_session


@pytest.fixture
def init_repository(populate_db):
    return UserRepository(populate_db)


@pytest.mark.integration
def test_user_list_all(init_repository):
    repository = init_repository

    users = repository.list_all()
    usernames = [user.username for user in users]

    assert set(usernames) == {"mario.rossi", "giada.bianchi", "luigi.verdi"}


@pytest.mark.integration
def test_user_get_by_id(init_repository):
    repository = init_repository

    user1 = repository.get_by_id(1)
    user2 = repository.get_by_id(5)

    assert user1.username == "mario.rossi"
    assert user2 is None


@pytest.mark.integration
def test_user_get_by_email(init_repository):
    repository = init_repository

    user1 = repository.get_by_email("giada@gmail.com")
    user2 = repository.get_by_email("email")

    assert user1.username == "giada.bianchi"
    assert user2 is None


@pytest.mark.integration
def test_user_get_by_username(init_repository):
    repository = init_repository

    user1 = repository.get_by_username("luigi.verdi")
    user2 = repository.get_by_username("luca")

    assert user1.id == 3
    assert user2 is None


@pytest.mark.integration
def test_user_get_by_username_or_email(init_repository):
    repository = init_repository

    user1 = repository.get_by_username_or_email("mario.rossi")
    user2 = repository.get_by_username_or_email("giada@gmail.com")
    user3 = repository.get_by_username_or_email("giada")

    assert user1.id == 1
    assert user2.id == 2
    assert user3 is None


@pytest.mark.integration
def test_user_add(init_repository):
    repository = init_repository

    repository.add(_user(6, "maria.verdi", "maria", "verdi", "maria@gmail.com", "password333!"))
    repository.session.commit()

    user1 = repository.get_by_id(6)

    assert user1.username == "maria.verdi"


@pytest.mark.integration
def test_user_delete(init_repository):
    repository = init_repository

    user_del = repository.get_by_id(3)
    repository.delete(user_del)
    repository.session.commit()

    users = repository.list_all()
    usernames = [user.username for user in users]

    assert set(usernames) == {"mario.rossi", "giada.bianchi"}


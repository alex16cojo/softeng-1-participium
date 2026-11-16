from __future__ import annotations

import pytest

from participium.database import close_connection, create_all, get_session, open_connection
from participium.models.category import Category
from participium.repositories.category_repository import CategoryRepository


def _category(category_id, name, is_active=True):
    return Category(id=category_id, name=name, is_active=is_active)


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
    init_session.add(_category(1, "Ambiente", True))
    init_session.add(_category(2, "Traffico", True))
    init_session.add(_category(3, "Illuminazione", False))
    init_session.commit()
    return init_session


@pytest.fixture
def init_repository(populate_db):
    return CategoryRepository(populate_db)


@pytest.mark.integration
def test_category_add(init_repository):
    repository = init_repository

    repository.add(_category(4, "Rifiuti"))
    repository.session.commit()

    category = repository.get_by_id(4)

    assert category.name == "Rifiuti"


@pytest.mark.integration
def test_category_get_by_id(init_repository):
    repository = init_repository

    category1 = repository.get_by_id(1)
    category2 = repository.get_by_id(99)

    assert category1.name == "Ambiente"
    assert category2 is None


@pytest.mark.integration
def test_category_get_by_name(init_repository):
    repository = init_repository

    category1 = repository.get_by_name("Traffico")
    category2 = repository.get_by_name("NonEsiste")

    assert category1.id == 2
    assert category2 is None


@pytest.mark.integration
def test_category_list_all(init_repository):
    repository = init_repository

    categories = repository.list_all()
    names = [category.name for category in categories]

    assert names == ["Ambiente", "Illuminazione", "Traffico"]


@pytest.mark.integration
def test_category_list_all_active_only(init_repository):
    repository = init_repository

    categories = repository.list_all(active_only=True)
    names = [category.name for category in categories]

    assert names == ["Ambiente", "Traffico"]
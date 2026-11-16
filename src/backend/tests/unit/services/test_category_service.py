from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from participium.core.exceptions import NotFoundError, ValidationError
from participium.models.category import Category
from participium.services.category_service import CategoryService


# -------------------------
# Fixtures
# -------------------------

@pytest.fixture
def make_service():
    def _make():
        return CategoryService(
            session=MagicMock(),
            category_repository=MagicMock(),
        )

    return _make


@pytest.fixture
def sample_category():
    return Category(
        id=1,
        name="Infrastructure",
        is_active=True,
    )


# -------------------------
# Tests: list_categories
# -------------------------

def test_list_categories_default(make_service):
    service = make_service()

    service.list_categories()

    service.category_repository.list_all.assert_called_once_with(active_only=False)


def test_list_categories_active_only(make_service):
    service = make_service()

    service.list_categories(active_only=True)

    service.category_repository.list_all.assert_called_once_with(active_only=True)


# -------------------------
# Tests: get_category
# -------------------------

def test_get_category_success(make_service, sample_category):
    service = make_service()
    service.category_repository.get_by_id.return_value = sample_category

    category = service.get_category(1)

    assert category == sample_category


def test_get_category_not_found(make_service):
    service = make_service()
    service.category_repository.get_by_id.return_value = None

    with pytest.raises(NotFoundError):
        service.get_category(999)


# -------------------------
# Tests: create_category
# -------------------------

def test_create_category_empty_name(make_service):
    service = make_service()

    with pytest.raises(ValidationError):
        service.create_category("   ")


def test_create_category_duplicate_name(make_service):
    service = make_service()
    service.category_repository.get_by_name.return_value = True

    with pytest.raises(ValidationError):
        service.create_category("Roads")


def test_create_category_success(make_service):
    service = make_service()

    created_category = Category(
        id=1,
        name="Roads",
        is_active=True,
    )

    service.category_repository.get_by_name.return_value = None
    service.category_repository.add.return_value = created_category

    category = service.create_category("Roads")

    assert category == created_category

    service.category_repository.add.assert_called_once()
    service.session.commit.assert_called_once()


def test_create_category_strips_name(make_service):
    service = make_service()

    created_category = Category(
        id=1,
        name="Environment",
        is_active=True,
    )

    service.category_repository.get_by_name.return_value = None
    service.category_repository.add.return_value = created_category

    service.create_category("  Environment  ")

    added_category = service.category_repository.add.call_args[0][0]

    assert added_category.name == "Environment"
    assert added_category.is_active is True


# -------------------------
# Tests: update_category
# -------------------------

def test_update_category_name_success(make_service, sample_category):
    service = make_service()

    service.category_repository.get_by_id.return_value = sample_category
    service.category_repository.get_by_name.return_value = None

    updated = service.update_category(1, name="Mobility")

    assert updated.name == "Mobility"

    service.session.commit.assert_called_once()


def test_update_category_name_strips_spaces(make_service, sample_category):
    service = make_service()

    service.category_repository.get_by_id.return_value = sample_category
    service.category_repository.get_by_name.return_value = None

    updated = service.update_category(1, name="  Transport  ")

    assert updated.name == "Transport"


def test_update_category_duplicate_name(make_service, sample_category):
    service = make_service()

    duplicate = Category(
        id=2,
        name="Environment",
        is_active=True,
    )

    service.category_repository.get_by_id.return_value = sample_category
    service.category_repository.get_by_name.return_value = duplicate

    with pytest.raises(ValidationError):
        service.update_category(1, name="Environment")


def test_update_category_same_name_same_entity_allowed(make_service, sample_category):
    service = make_service()

    service.category_repository.get_by_id.return_value = sample_category
    service.category_repository.get_by_name.return_value = sample_category

    updated = service.update_category(1, name="Infrastructure")

    assert updated == sample_category


def test_update_category_is_active(make_service, sample_category):
    service = make_service()

    service.category_repository.get_by_id.return_value = sample_category

    updated = service.update_category(1, is_active=False)

    assert updated.is_active is False

    service.session.commit.assert_called_once()


def test_update_category_not_found(make_service):
    service = make_service()

    service.category_repository.get_by_id.return_value = None

    with pytest.raises(NotFoundError):
        service.update_category(1, name="Updated")
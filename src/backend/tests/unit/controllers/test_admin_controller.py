import pytest
from unittest.mock import Mock

from participium.controllers.admin_controller import AdminController


@pytest.fixture
def controller_bundle():
    category_service = Mock()
    user_service = Mock()
    statistics_service = Mock()

    controller = AdminController(
        category_service=category_service,
        user_service=user_service,
        statistics_service=statistics_service,
    )

    return {
        "controller": controller,
        "category_service": category_service,
        "user_service": user_service,
        "statistics_service": statistics_service,
    }


@pytest.mark.unit
def test_list_categories_default(controller_bundle):
    controller = controller_bundle["controller"]
    category_service = controller_bundle["category_service"]

    categories = [Mock(), Mock()]
    category_service.list_categories.return_value = categories

    result = controller.list_categories()

    category_service.list_categories.assert_called_once_with(active_only=False)
    assert result == categories


@pytest.mark.unit
def test_list_categories_active_only(controller_bundle):
    controller = controller_bundle["controller"]
    category_service = controller_bundle["category_service"]

    categories = [Mock()]
    category_service.list_categories.return_value = categories

    result = controller.list_categories(active_only=True)

    category_service.list_categories.assert_called_once_with(active_only=True)
    assert result == categories


@pytest.mark.unit
def test_create_category(controller_bundle):
    controller = controller_bundle["controller"]
    category_service = controller_bundle["category_service"]

    category_name = "Strade"
    category = Mock()
    category_service.create_category.return_value = category

    result = controller.create_category(category_name)

    category_service.create_category.assert_called_once_with(category_name)
    assert result == category


@pytest.mark.unit
def test_update_category(controller_bundle):
    controller = controller_bundle["controller"]
    category_service = controller_bundle["category_service"]

    category_id = 5
    payload = {"name": "Strade", "is_active": True}
    category = Mock()
    category_service.update_category.return_value = category

    result = controller.update_category(category_id, payload)

    category_service.update_category.assert_called_once_with(category_id, name="Strade", is_active=True)
    assert result == category


@pytest.mark.unit
def test_list_users(controller_bundle):
    controller = controller_bundle["controller"]
    user_service = controller_bundle["user_service"]

    users = [Mock(), Mock()]
    user_service.list_users.return_value = users

    result = controller.list_users()

    user_service.list_users.assert_called_once()
    assert result == users


@pytest.mark.unit
def test_create_user(controller_bundle):
    controller = controller_bundle["controller"]
    user_service = controller_bundle["user_service"]

    payload = {"email": "admin@example.com", "password": "password123"}
    user = Mock()
    user_service.create_user.return_value = user

    result = controller.create_user(payload)

    user_service.create_user.assert_called_once_with(payload)
    assert result == user


@pytest.mark.unit
def test_update_user(controller_bundle):
    controller = controller_bundle["controller"]
    user_service = controller_bundle["user_service"]

    user_id = 10
    payload = {"first_name": "Mario"}
    user = Mock()
    user_service.update_user.return_value = user

    result = controller.update_user(user_id, payload)

    user_service.update_user.assert_called_once_with(user_id, payload)
    assert result == user


@pytest.mark.unit
def test_admin_statistics(controller_bundle):
    controller = controller_bundle["controller"]
    statistics_service = controller_bundle["statistics_service"]

    stats = {
        "reports_by_status": {"total": 100},
        "reports_by_type": {"total": 50}
    }
    statistics_service.admin_statistics.return_value = stats

    result = controller.admin_statistics()

    statistics_service.admin_statistics.assert_called_once()
    assert result == stats

import pytest

from unittest.mock import Mock
from participium.controllers.user_controller import UserController


@pytest.fixture
def controller_bundle():
    user_service = Mock()
    notification_service = Mock()

    controller = UserController(
        user_service=user_service,
        notification_service=notification_service
    )

    return {
        "controller": controller,
        "user_service": user_service,
        "notification_service": notification_service,
    }


@pytest.mark.unit
def test_update_profile(controller_bundle):
    controller = controller_bundle["controller"]
    user_service = controller_bundle["user_service"]

    user = Mock()

    controller.update_profile(user=user, username="mario.rossi", first_name="Mario",
                              last_name="Rossi", email_notifications_enabled=True, profile_picture=None)

    user_service.update_profile.assert_called_once_with(user=user, username="mario.rossi", first_name="Mario",
                            last_name="Rossi", email_notifications_enabled=True, profile_picture=None)


@pytest.mark.unit
def test_delete_account(controller_bundle):
    controller = controller_bundle["controller"]
    user_service = controller_bundle["user_service"]

    user = Mock()

    controller.delete_account(user)

    user_service.delete_account.assert_called_once_with(user)


@pytest.mark.unit
def test_list_users(controller_bundle):
    controller = controller_bundle["controller"]
    user_service = controller_bundle["user_service"]

    expected = ["u1", "u2"]
    user_service.list_users.return_value = expected

    result = controller.list_users()

    user_service.list_users.assert_called_once()
    assert result == expected


@pytest.mark.unit
def test_create_user(controller_bundle):
    controller = controller_bundle["controller"]
    user_service = controller_bundle["user_service"]

    payload = {"username": "mario"}

    controller.create_user(payload)

    user_service.create_user.assert_called_once_with(payload)


@pytest.mark.unit
def test_update_user(controller_bundle):
    controller = controller_bundle["controller"]
    user_service = controller_bundle["user_service"]

    user_id = 1
    payload = {"username": "mario"}

    controller.update_user(user_id, payload)

    user_service.update_user.assert_called_once_with(user_id, payload)


@pytest.mark.unit
def test_list_notifications(controller_bundle):
    controller = controller_bundle["controller"]
    notification_service = controller_bundle["notification_service"]

    user_id = 1

    controller.list_notifications(user_id)

    notification_service.list_notifications.assert_called_once_with(user_id)


@pytest.mark.unit
def test_get_notification_for_user(controller_bundle):
    controller = controller_bundle["controller"]
    notification_service = controller_bundle["notification_service"]

    user_id = 1
    notification_id = 13

    controller.get_notification_for_user(user_id, notification_id)

    notification_service.get_user_notification.assert_called_once_with(user_id, notification_id)


@pytest.mark.unit
def test_mark_notification_as_read(controller_bundle):
    controller = controller_bundle["controller"]
    notification_service = controller_bundle["notification_service"]

    notification_id = 22

    controller.mark_notification_as_read(notification_id)

    notification_service.mark_as_read.assert_called_once_with(notification_id)




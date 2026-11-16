import pytest
from unittest.mock import Mock

from participium.controllers.auth_controller import AuthController


@pytest.fixture
def controller_bundle():
    auth_service = Mock()

    controller = AuthController(auth_service=auth_service)

    return {
        "controller": controller,
        "auth_service": auth_service,
    }


@pytest.mark.unit
def test_register_default(controller_bundle):
    controller = controller_bundle["controller"]
    auth_service = controller_bundle["auth_service"]

    payload = {"email": "nuovo@example.com", "password": "password123"}
    user = Mock()
    auth_service.register_user.return_value = (user, None)

    result = controller.register(payload)

    auth_service.register_user.assert_called_once_with(payload, None)
    assert result == (user, None)


@pytest.mark.unit
def test_register_with_url(controller_bundle):
    controller = controller_bundle["controller"]
    auth_service = controller_bundle["auth_service"]

    payload = {"email": "nuovo@example.com", "password": "password123"}
    user = Mock()
    verification_base_url = "http://localhost:5173/verify"
    verification_url = "http://localhost:5173/verify/token123"
    auth_service.register_user.return_value = (user, verification_url)

    result = controller.register(payload=payload, verification_base_url=verification_base_url)

    auth_service.register_user.assert_called_once_with(payload, verification_base_url)
    assert result == (user, verification_url)


@pytest.mark.unit
def test_verify_email(controller_bundle):
    controller = controller_bundle["controller"]
    auth_service = controller_bundle["auth_service"]

    token_value = "token123"
    user = Mock()
    auth_service.verify_email.return_value = user

    result = controller.verify_email(token_value)

    auth_service.verify_email.assert_called_once_with(token_value)
    assert result == user


@pytest.mark.unit
def test_login(controller_bundle):
    controller = controller_bundle["controller"]
    auth_service = controller_bundle["auth_service"]

    identifier = "user@example.com"
    password = "password123"
    user = Mock()
    auth_service.authenticate.return_value = user

    result = controller.login(identifier, password)

    auth_service.authenticate.assert_called_once_with(identifier, password)
    assert result == user

from __future__ import annotations

import pytest
from unittest.mock import MagicMock, patch

from participium.services.auth_service import AuthService
from datetime import timedelta
from participium.core.exceptions import ValidationError, AuthenticationError
from participium.models.user import User
from participium.models.token import EmailVerificationToken
from participium.core.utils import utcnow


# -------------------------
# Fixtures
# -------------------------

@pytest.fixture
def make_service():
    def _make():
        return AuthService(
            session=MagicMock(),
            user_repository=MagicMock(),
            token_repository=MagicMock(),
            email_gateway=MagicMock(),
        )
    return _make


@pytest.fixture
def valid_payload():
    return {
        "username": "maria.rossi",
        "first_name": "Maria",
        "last_name": "Rossi",
        "email": "maria.rossi@example.com",
        "password": "password123",
    }


# -------------------------
# Tests: validation errors
# -------------------------

def test_register_user_missing_fields(make_service):
    service = make_service()

    payload = {
        "username": "maria.rossi"
    }

    with pytest.raises(ValidationError):
        service.register_user(payload)


def test_register_user_username_taken(make_service, valid_payload):
    service = make_service()
    service.user_repository.get_by_username.return_value = True

    with pytest.raises(ValidationError):
        service.register_user(valid_payload)


def test_register_user_email_taken(make_service, valid_payload):
    service = make_service()
    service.user_repository.get_by_username.return_value = None
    service.user_repository.get_by_email.return_value = True

    with pytest.raises(ValidationError):
        service.register_user(valid_payload)


# -------------------------
# Tests: success cases
# -------------------------

@patch("participium.services.auth_service.generate_token", return_value="TOKEN123")
@patch("participium.services.auth_service.hash_password", return_value="HASHED")
def test_register_user_success_no_email(mock_hash, mock_token, make_service, valid_payload):
    service = make_service()
    service.user_repository.get_by_username.return_value = None
    service.user_repository.get_by_email.return_value = None

    user, url = service.register_user(valid_payload)

    assert user.username == valid_payload["username"]
    assert user.email == valid_payload["email"].lower()
    assert user.is_email_verified is False
    assert url is None

    service.user_repository.add.assert_called_once()
    service.token_repository.add.assert_called_once()
    service.session.commit.assert_called_once()
    service.email_gateway.send.assert_not_called()


@patch("participium.services.auth_service.generate_token", return_value="TOKEN123")
@patch("participium.services.auth_service.hash_password", return_value="HASHED")
def test_register_user_success_with_email(mock_hash, mock_token, make_service, valid_payload):
    service = make_service()
    service.user_repository.get_by_username.return_value = None
    service.user_repository.get_by_email.return_value = None

    base_url = "https://example.com/verify"

    user, url = service.register_user(valid_payload, base_url)

    assert url == f"{base_url}/TOKEN123"
    service.email_gateway.send.assert_called_once()


# -------------------------
# Tests: data normalization
# -------------------------

@patch("participium.services.auth_service.generate_token", return_value="TOKEN123")
@patch("participium.services.auth_service.hash_password", return_value="HASHED")
def test_register_user_strips_and_lowercase(mock_hash, mock_token, make_service):
    service = make_service()
    service.user_repository.get_by_username.return_value = None
    service.user_repository.get_by_email.return_value = None

    payload = {
        "username": "  mario  ",
        "first_name": " Mario ",
        "last_name": " Rossi ",
        "email": " TEST@EXAMPLE.COM ",
        "password": "pass",
    }

    user, _ = service.register_user(payload)

    assert user.username == "mario"
    assert user.first_name == "Mario"
    assert user.last_name == "Rossi"
    assert user.email == "test@example.com"


def test_verify_email_invalid_token(make_service):
    service = make_service()
    service.token_repository.get_by_token.return_value = None

    with pytest.raises(ValidationError, match="invalid"):
        service.verify_email("NOTOKEN")


def test_verify_email_already_used(make_service):
    service = make_service()
    token = MagicMock(is_used=True)
    service.token_repository.get_by_token.return_value = token

    with pytest.raises(ValidationError, match="invalid"):
        service.verify_email("ABC123")


def test_verify_email_expired(make_service):
    service = make_service()
    user = MagicMock()
    token = MagicMock(
        is_used=False,
        expires_at=utcnow() - timedelta(seconds=1),
        user=user,
    )
    service.token_repository.get_by_token.return_value = token

    with pytest.raises(ValidationError, match="expired"):
        service.verify_email("ABC123")



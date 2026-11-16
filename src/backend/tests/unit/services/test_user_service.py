from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from participium.core.exceptions import NotFoundError, ValidationError
from participium.models.enums import Role
from participium.models.user import User
from participium.services.user_service import UserService


# -------------------------
# Fixtures
# -------------------------

@pytest.fixture
def make_service():
    def _make():
        return UserService(
            session=MagicMock(),
            user_repository=MagicMock(),
            category_repository=MagicMock(),
            token_repository=MagicMock(),
            notification_repository=MagicMock(),
            storage_service=MagicMock(),
        )

    return _make


@pytest.fixture
def user():
    return User(
        id=1,
        username="mario",
        first_name="Mario",
        last_name="Rossi",
        email="mario@example.com",
        role=Role.CITIZEN,
        email_notifications_enabled=True,
    )


@pytest.fixture
def category():
    category = MagicMock()
    category.id = 10
    category.is_active = True
    return category


# -------------------------
# update_profile
# -------------------------

def test_update_profile_success(make_service, user):
    service = make_service()
    service.user_repository.get_by_username.return_value = None

    picture = MagicMock()
    picture.filename = "avatar.jpg"

    service.storage_service.save.return_value = "uploads/avatar.jpg"

    updated = service.update_profile(
        user=user,
        username=" mario2 ",
        first_name=" Mario ",
        last_name=" Rossi ",
        email_notifications_enabled=False,
        profile_picture=picture,
    )

    assert updated.username == "mario2"
    assert updated.first_name == "Mario"
    assert updated.last_name == "Rossi"
    assert updated.email_notifications_enabled is False
    assert updated.profile_picture_path == "uploads/avatar.jpg"

    service.session.commit.assert_called_once()


def test_update_profile_duplicate_username(make_service, user):
    service = make_service()

    service.user_repository.get_by_username.return_value = True

    with pytest.raises(ValidationError):
        service.update_profile(user, username="taken")


def test_update_profile_no_changes(make_service, user):
    service = make_service()

    updated = service.update_profile(user)

    assert updated is user
    assert updated.username == "mario"
    assert updated.first_name == "Mario"
    assert updated.last_name == "Rossi"
    assert updated.email_notifications_enabled is True
    assert updated.profile_picture_path is None

    service.session.commit.assert_called_once()


# -------------------------
# get_user
# -------------------------

def test_get_user_not_found(make_service):
    service = make_service()

    service.user_repository.get_by_id.return_value = None

    with pytest.raises(NotFoundError):
        service.get_user(1)


def test_list_users(make_service):
    service = make_service()
    sample_user = User(
        id=2,
        username="luigi",
        first_name="Luigi",
        last_name="Verdi",
        email="luigi@example.com",
        role=Role.CITIZEN,
        email_notifications_enabled=True,
    )
    service.user_repository.list_all.return_value = [sample_user]

    result = service.list_users()

    assert result == [sample_user]
    service.user_repository.list_all.assert_called_once()


# -------------------------
# create_user
# -------------------------

@pytest.mark.parametrize(
    ("payload", "error"),
    [
        (
            {"username": ""},
            "Missing required fields",
        ),
        (
            {"username": "taken"},
            "Username already in use.",
        ),
    ],
)
def test_create_user_validation(make_service, category, payload, error):
    service = make_service()

    valid_payload = {
        "username": "mario",
        "first_name": "Mario",
        "last_name": "Rossi",
        "email": "mario@example.com",
        "password": "password",
        "role": Role.CITIZEN.value,
    }

    valid_payload.update(payload)

    if payload.get("username") == "taken":
        service.user_repository.get_by_username.return_value = True

    with pytest.raises(ValidationError, match=error):
        service.create_user(valid_payload)


@patch("participium.services.user_service.hash_password", return_value="HASHED")
def test_create_user_success(mock_hash, make_service):
    service = make_service()

    service.user_repository.get_by_username.return_value = None
    service.user_repository.get_by_email.return_value = None

    payload = {
        "username": " mario ",
        "first_name": " Mario ",
        "last_name": " Rossi ",
        "email": " TEST@EXAMPLE.COM ",
        "password": "password",
        "role": Role.CITIZEN.value,
    }

    user = service.create_user(payload)

    assert user.username == "mario"
    assert user.email == "test@example.com"
    assert user.password_hash == "HASHED"

    service.user_repository.add.assert_called_once()
    service.session.commit.assert_called_once()



def test_create_user_duplicate_email(make_service):
    service = make_service()
    service.user_repository.get_by_username.return_value = None
    service.user_repository.get_by_email.return_value = True

    payload = {
        "username": "mario", "first_name": "M", "last_name": "R",
        "email": "mario@example.com", "password": "pw", "role": "CITIZEN"
    }
    with pytest.raises(ValidationError, match="Email already in use."):
        service.create_user(payload)


def test_create_operator_success(make_service, category):
    service = make_service()
    service.user_repository.get_by_username.return_value = None
    service.user_repository.get_by_email.return_value = None
    service.category_repository.get_by_id.return_value = category

    payload = {
        "username": "operatore1",
        "first_name": "Op",
        "last_name": "Uno",
        "email": "op@test.com",
        "password": "password",
        "role": Role.OPERATOR.value,
        "category_id": 10
    }

    op = service.create_user(payload)
    assert op.role == Role.OPERATOR
    assert op.category_id == 10

# -------------------------
# update_user
# -------------------------

def test_update_user_success(make_service, user):
    service = make_service()

    service.user_repository.get_by_id.return_value = user
    service.user_repository.get_by_username.return_value = None
    service.user_repository.get_by_email.return_value = None

    updated = service.update_user(
        1,
        {
            "username": " mario2 ",
            "is_active": False,
        },
    )

    assert updated.username == "mario2"
    assert updated.is_active is False

    service.session.commit.assert_called_once()


def test_update_user_duplicate_email(make_service, user):
    service = make_service()

    service.user_repository.get_by_id.return_value = user
    service.user_repository.get_by_email.return_value = True

    with pytest.raises(ValidationError):
        service.update_user(
            1,
            {
                "email": "taken@example.com",
            },
        )


def test_update_user_change_role_to_operator(make_service, user, category):
    service = make_service()
    service.user_repository.get_by_id.return_value = user
    service.category_repository.get_by_id.return_value = category

    updated = service.update_user(user.id, {
        "role": Role.OPERATOR.value,
        "category_id": 10
    })

    assert updated.role == Role.OPERATOR
    assert updated.category_id == 10

# -------------------------
# _parse_role
# -------------------------

def test_parse_role():
    assert UserService._parse_role(Role.ADMIN.value) == Role.ADMIN


def test_parse_role_invalid():
    with pytest.raises(ValidationError):
        UserService._parse_role("INVALID")


# -------------------------
# _resolve_operator_category
# -------------------------

def test_resolve_operator_category_success(make_service, category):
    service = make_service()

    service.category_repository.get_by_id.return_value = category

    result = service._resolve_operator_category(
        Role.OPERATOR,
        10,
    )

    assert result == category


@pytest.mark.parametrize(
    ("category_id", "error"),
    [
        (None, "Operator category is required."),
        ("bad", "A valid active category is required for operators."),
    ],
)
def test_resolve_operator_category_validation(
    make_service,
    category_id,
    error,
):
    service = make_service()

    with pytest.raises(ValidationError, match=error):
        service._resolve_operator_category(Role.OPERATOR, category_id)


def test_resolve_operator_category_inactive(make_service, category):
    service = make_service()
    category.is_active = False
    service.category_repository.get_by_id.return_value = category

    with pytest.raises(ValidationError, match="A valid active category is required for operators."):
        service._resolve_operator_category(Role.OPERATOR, 10)


# -------------------------
# delete_account
# -------------------------

def test_delete_account_full_cleanup(make_service, user):
    service = make_service()
    user.id = 5

    report_mock = MagicMock()
    follower_mock = MagicMock()

    message_mock = MagicMock()
    message_mock.sender_id = 5
    message_mock.recipient_id = 5

    history_mock = MagicMock()

    service.session.scalars.side_effect = [
        [report_mock],
        [follower_mock],
        [message_mock],
        [history_mock]
    ]

    service.notification_repository.list_for_user.return_value = [MagicMock()]
    service.token_repository.list_for_user.return_value = [MagicMock()]

    service.delete_account(user)

    assert report_mock.reporter_id is None
    assert message_mock.sender_id is None
    assert message_mock.recipient_id is None
    assert history_mock.changed_by_id is None

    service.user_repository.delete.assert_called_once_with(user)
    service.session.commit.assert_called_once()


def test_delete_account_message_not_related(make_service, user):
    service = make_service()
    user.id = 5

    unrelated_message = MagicMock()
    unrelated_message.sender_id = 0
    unrelated_message.recipient_id = 0

    service.session.scalars.side_effect = [[], [], [unrelated_message], []]
    service.notification_repository.list_for_user.return_value = []
    service.token_repository.list_for_user.return_value = []

    service.delete_account(user)

    assert unrelated_message.sender_id == 0
    assert unrelated_message.recipient_id == 0
    service.session.commit.assert_called_once()



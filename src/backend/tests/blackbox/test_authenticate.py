from __future__ import annotations

import pytest

from participium.core.exceptions import AuthenticationError
from participium.models.user import User
from participium.services.auth_service import AuthService

WRONG_PASSWORD = "sbagliata"

ACTIVE_VERIFIED_USER = User(
    id=101,
    username="mario.rossi",
    first_name="Mario",
    last_name="Rossi",
    email="m.rossi@email.com",
    password_hash="HASHED_PASSWORD_MARIO",
    is_active=True,
    is_email_verified=True,
)

INACTIVE_VERIFIED_USER = User(
    id=102,
    username="paolo.bianchi",
    first_name="Paolo",
    last_name="Bianchi",
    email="paolo.bianchi@email.com",
    password_hash="HASHED_PASSWORD_PAOLO",
    is_active=False,
    is_email_verified=True,
)

ACTIVE_UNVERIFIED_USER = User(
    id=103,
    username="luca.verdi",
    first_name="Luca",
    last_name="Verdi",
    email="luca.verdi@email.com",
    password_hash="HASHED_PASSWORD_LUCA",
    is_active=True,
    is_email_verified=False,
)


@pytest.fixture
def seed_authenticate_data() -> None:
    pass


# TC-1: Successo con Username
@pytest.mark.skip(reason="Disabled.")
def test_authenticate_success_username(seed_authenticate_data: None) -> None:
    auth_service = AuthService()

    authenticated_user = auth_service.authenticate(
        identifier="mario.rossi",
        password="MarioR$"
    )

    assert isinstance(authenticated_user, User)
    assert authenticated_user.id == ACTIVE_VERIFIED_USER.id
    assert authenticated_user.username == ACTIVE_VERIFIED_USER.username


# TC-2: Successo con Email
@pytest.mark.skip(reason="Disabled.")
def test_authenticate_success_email(seed_authenticate_data: None) -> None:
    auth_service = AuthService()

    authenticated_user = auth_service.authenticate(
        identifier="m.rossi@email.com",
        password="MarioR$"
    )

    assert isinstance(authenticated_user, User)
    assert authenticated_user.id == ACTIVE_VERIFIED_USER.id
    assert authenticated_user.email == ACTIVE_VERIFIED_USER.email


# TC-3 - TC-4: Identifier non valido
@pytest.mark.skip(reason="Disabled.")
def test_authenticate_invalid_identifiers(seed_authenticate_data: None) -> None:
    auth_service = AuthService()

    with pytest.raises(AuthenticationError):
        auth_service.authenticate(identifier="mario.ro", password="MarioR$")

    with pytest.raises(AuthenticationError):
        auth_service.authenticate(identifier="", password="MarioR$")


# TC-5 - TC-6: Password non valida
@pytest.mark.skip(reason="Disabled.")
def test_authenticate_invalid_password(seed_authenticate_data: None) -> None:
    auth_service = AuthService()

    with pytest.raises(AuthenticationError):
        auth_service.authenticate(identifier="mario.rossi", password=WRONG_PASSWORD)

    with pytest.raises(AuthenticationError):
        auth_service.authenticate(identifier="mario.rossi", password="")


# TC-5: Utente inattivo
@pytest.mark.skip(reason="Disabled.")
def test_authenticate_inactive_user(seed_authenticate_data: None) -> None:
    auth_service = AuthService()

    with pytest.raises(AuthenticationError):
        auth_service.authenticate(identifier="paolo.bianchi", password="PaoloB$")


# TC-6: Email non verificata
@pytest.mark.skip(reason="Disabled.")
def test_authenticate_unverified_email(seed_authenticate_data: None) -> None:
    auth_service = AuthService()

    with pytest.raises(AuthenticationError):
        auth_service.authenticate(identifier="luca.verdi", password="LucaV$")
from __future__ import annotations

import pytest
from werkzeug.datastructures import FileStorage
from io import BytesIO

from participium.core.exceptions import ValidationError
from participium.models.user import User
from participium.services.user_service import UserService


EXISTING_USER = User(
    id=1,
    username="mario.rossi",
    first_name="Mario",
    last_name="Rossi",
    email_notifications_enabled=True
)

OTHER_USER = User(
    id=2,
    username="username.occupato",
    first_name="Paolo",
    last_name="Bianchi"
)

@pytest.fixture
def seed_user_data() -> None:
    """Non implementato."""
    pass

# TC-1: Aggiornamento completo con successo
@pytest.mark.skip(reason="In progress.")
def test_update_profile_full_success(seed_user_data: None) -> None:
    service = UserService()
    fake_photo = FileStorage(stream=BytesIO(b"fake image content"), filename="profile.jpg")
    
    updated_user = service.update_profile(
        user=EXISTING_USER,
        username="mario.nuovo",
        first_name="Mariolino",
        last_name="Rossini",
        email_notifications_enabled=False,
        profile_picture=fake_photo
    )
    assert updated_user.username == "mario.nuovo"
    assert updated_user.first_name == "Mariolino"
    assert updated_user.email_notifications_enabled is False

# TC-2: ValidationError - Username già esistente
@pytest.mark.skip(reason="In progress.")
def test_update_profile_error_duplicate_username(seed_user_data: None) -> None:
    service = UserService()
    
    with pytest.raises(ValidationError):
        service.update_profile(
            user=EXISTING_USER,
            username="username.occupato"
        )

# TC-3: Aggiornamento parziale (first_name)
@pytest.mark.skip(reason="In progress.")
def test_update_profile_partial_update(seed_user_data: None) -> None:
    service = UserService()
    
    updated_user = service.update_profile(
        user=EXISTING_USER,
        first_name="Luigi"
    )    
    assert updated_user.first_name == "Luigi"
    assert updated_user.username == EXISTING_USER.username

# TC-4: Cambio preferenze notifiche
@pytest.mark.skip(reason="In progress.")
def test_update_profile_toggle_notifications(seed_user_data: None) -> None:
    service = UserService()
    
    updated_user = service.update_profile(
        user=EXISTING_USER,
        email_notifications_enabled=False
    )
    assert updated_user.email_notifications_enabled is False

# TC-5: Nessun parametro fornito
@pytest.mark.skip(reason="In progress.")
def test_update_profile_no_changes(seed_user_data: None) -> None:
    service = UserService()
    
    updated_user = service.update_profile(user=EXISTING_USER)
    
    assert updated_user.username == EXISTING_USER.username
    assert updated_user.first_name == EXISTING_USER.first_name
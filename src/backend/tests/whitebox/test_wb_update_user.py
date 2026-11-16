import pytest
from unittest.mock import MagicMock, patch
from participium.services.user_service import UserService
from participium.core.exceptions import ValidationError
from participium.models.enums import Role

@pytest.fixture
def mock_deps():
    return {
        "session": MagicMock(),
        "user_repo": MagicMock(),
        "cat_repo": MagicMock()
    }

@pytest.fixture
def service(mock_deps):
    s = UserService(
        session=mock_deps["session"],
        user_repository=mock_deps["user_repo"],
        category_repository=mock_deps["cat_repo"]
    )
    s.get_user = MagicMock()
    s._parse_role = MagicMock()
    s._resolve_operator_category = MagicMock()
    return s

def test_update_user_username_duplicate(service, mock_deps):
    user = MagicMock(username="old_name")
    service.get_user.return_value = user
    mock_deps["user_repo"].get_by_username.return_value = MagicMock()
    
    payload = {"username": "new_name"}
    with pytest.raises(ValidationError, match="Username already in use."):
        service.update_user(1, payload)

def test_update_user_email_duplicate(service, mock_deps):
    user = MagicMock(username="same", email="old@test.it")
    service.get_user.return_value = user
    mock_deps["user_repo"].get_by_username.return_value = None
    mock_deps["user_repo"].get_by_email.return_value = MagicMock()
    
    payload = {"username": "same", "email": "taken@test.it"}
    
    with pytest.raises(ValidationError, match="Email already in use."):
        service.update_user(1, payload)

def test_update_user_success_full(service, mock_deps):
    user = MagicMock(username="old", role=Role.CITIZEN)
    service.get_user.return_value = user
    service._parse_role.return_value = Role.OPERATOR
    service._resolve_operator_category.return_value = MagicMock(id=50)
    
    mock_deps["user_repo"].get_by_username.return_value = None
    mock_deps["user_repo"].get_by_email.return_value = None

    payload = {
        "username": "  new_user  ",
        "first_name": "Mario",
        "role": "OPERATOR",
        "category_id": 50,
        "is_active": False
    }
    result = service.update_user(1, payload)
    
    assert user.username == "new_user"
    assert user.first_name == "Mario"
    assert user.role == Role.OPERATOR
    assert user.category_id == 50
    assert user.is_active is False
    mock_deps["session"].commit.assert_called_once()

def test_update_user_partial_skipping_logic(service, mock_deps):
    user = MagicMock(username="old", role=Role.ADMIN, category_id=1)
    service.get_user.return_value = user
    mock_deps["user_repo"].get_by_username.return_value = None

    payload = {"email_notifications_enabled": True}
    
    service.update_user(1, payload)
    
    assert user.email_notifications_enabled is True
    service._parse_role.assert_not_called()
    mock_deps["session"].commit.assert_called_once()
from __future__ import annotations

import pytest
from participium.core.security import verify_password

VALID_PASSWORD = "Ciao1234?"
CORRECT_HASH = "$2b$12$KIXvH15G6.U6U9.2VfM6u.xX6Y7E8Z9A1B2C3D4E5F6G7H8I9J0K" # Esempio di hash bcrypt
WRONG_PASSWORD = "IDontKnowThePassword"

@pytest.fixture
def security_setup() -> None:
    """Non strettamente necessario."""
    pass

# TC-1: Corrispondenza esatta
@pytest.mark.skip(reason="In progress.")
def test_verify_password_success(security_setup: None) -> None:
    result = verify_password(VALID_PASSWORD, CORRECT_HASH)
    assert result is True

# TC-2: Password errata
@pytest.mark.skip(reason="In progress.")
def test_verify_password_wrong_password(security_setup: None) -> None:
    result = verify_password(WRONG_PASSWORD, CORRECT_HASH)
    assert result is False

# TC-3: Case Sensitivity
@pytest.mark.skip(reason="In progress.")
def test_verify_password_case_sensitive(security_setup: None) -> None:
    result = verify_password(VALID_PASSWORD.lower(), CORRECT_HASH)
    assert result is False

# TC-4: Stringhe vuote - Campo password
@pytest.mark.skip(reason="In progress.")
def test_verify_password_empty_inputs(security_setup: None) -> None:
    assert verify_password("", CORRECT_HASH) is False

# TC-5: Stringhe vuote - Campo password_hash
@pytest.mark.skip(reason="In progress.")
def test_verify_password_hash_empty_inputs(security_setup: None) -> None:
    assert verify_password(VALID_PASSWORD, "") is False

# TC-6: Hash malformato
@pytest.mark.skip(reason="In progress.")
def test_verify_password_malformed_hash(security_setup: None) -> None:
    result = verify_password(VALID_PASSWORD, "not_a_real_hash")
    assert result is False

# TC-7: Password con spazi
@pytest.mark.skip(reason="In progress.")
def test_verify_password_spaces(security_setup: None) -> None:
    space_password = " "
    space_hash = "$2b$12$some_hash_for_space"
    pass
from datetime import datetime, timezone
from jose import jwt
from app.services.auth import (
    ALGORITHM,
    SECRET_KEY,
    create_access_token,
    hash_password,
    verify_password,
)


def test_hash_password_differs_from_plaintext():
    hashed = hash_password("mypassword123")
    assert hashed != "mypassword123"


def test_hash_password_is_salted():
    hashed_a = hash_password("mypassword123")
    hashed_b = hash_password("mypassword123")
    assert hashed_a != hashed_b


def test_verify_password_succeeds_with_correct_password():
    hashed = hash_password("mypassword123")
    assert verify_password("mypassword123", hashed) is True


def test_verify_password_fails_with_wrong_password():
    hashed = hash_password("mypassword123")
    assert verify_password("wrongpassword", hashed) is False


def test_verify_password_handles_passwords_over_bcrypt_limit():
    long_password = "a" * 100
    hashed = hash_password(long_password)
    assert verify_password(long_password, hashed) is True


def test_create_access_token_encodes_expected_payload():
    token = create_access_token({"sub": "patient@example.com"})
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["sub"] == "patient@example.com"


def test_create_access_token_sets_future_expiration():
    token = create_access_token({"sub": "patient@example.com"})
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
    assert exp > datetime.now(timezone.utc)

def _register_payload(email="patient@example.com"):
    return {
        "email": email,
        "password": "securepassword123",
        "full_name": "Test Patient",
        "role": "patient",
    }


def test_register_creates_new_user(client):
    response = client.post("/api/v1/auth/register", json=_register_payload())
    assert response.status_code == 201
    assert response.json()["message"] == "User registered successfully"


def test_register_rejects_duplicate_email(client):
    payload = _register_payload()
    client.post("/api/v1/auth/register", json=payload)
    response = client.post("/api/v1/auth/register", json=payload)

    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"


def test_login_succeeds_with_correct_credentials(client):
    client.post("/api/v1/auth/register", json=_register_payload())

    response = client.post("/api/v1/auth/login", json={
        "email": "patient@example.com",
        "password": "securepassword123",
    })

    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_fails_with_wrong_password(client):
    client.post("/api/v1/auth/register", json=_register_payload())

    response = client.post("/api/v1/auth/login", json={
        "email": "patient@example.com",
        "password": "wrongpassword",
    })

    assert response.status_code == 401


def test_login_fails_for_nonexistent_user(client):
    response = client.post("/api/v1/auth/login", json={
        "email": "ghost@example.com",
        "password": "whatever123",
    })

    assert response.status_code == 401

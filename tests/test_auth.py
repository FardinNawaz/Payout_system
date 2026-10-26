import bcrypt
from models import User,APICLIENT
from conftest import TestingSessionLocal

def test_login_with_valid_credentials(client):
    db=TestingSessionLocal()

    password="Testpassword@123"

    try:
        user=User(
            name="login the user",
            email="login_test@example.com",
            password_hash=bcrypt.hashpw(
                password.encode(),bcrypt.gensalt()).decode(),
            role="USER"
        )
        db.add(user)
        db.commit()
    finally:
        db.close()

    response=client.post(
        "/api/v1/auth/login",
        json={
            "email":"login_test@example.com",
            "password":password
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Login successful"
    assert data["access_token"] 
    assert data["token_type"] == "bearer"
    assert data["has_api_key"] is False


def test_login_with_api(client):
    db=TestingSessionLocal()
    password="TestPassword123"
    try:
        user=User(
            name="API Client User",
            email="api_client_test@example.com",
            password_hash=bcrypt.hashpw(
                password.encode(),
                bcrypt.gensalt()
            ).decode(),
            role="USER"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        api_client=APICLIENT(
            user_id=user.user_id,
            api_key="test_api_key_123",
            api_secret="test_api_secret_123",
            webhook_url="https://example.com/webhook",
            webhook_secret="test_webhook_secret_123"
        )
        db.add(api_client)
        db.commit()
    finally:
        db.close()

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "api_client_test@example.com",
            "password": password
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Login successful"
    assert data["access_token"]
    assert data["token_type"] == "bearer"
    assert data["has_api_key"] is True

def test_login_with_wrong_password(client):
    db = TestingSessionLocal()

    password = "CorrectPassword123"

    try:
        user = User(
            name="Wrong Password User",
            email="wrong_password@example.com",
            password_hash=bcrypt.hashpw(
                password.encode(),
                bcrypt.gensalt()
            ).decode(),
            role="USER"
        )

        db.add(user)
        db.commit()

    finally:
        db.close()

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "wrong_password@example.com",
            "password": "WrongPassword123"
        }
    )

    assert response.status_code == 401
    assert response.json()["message"] == "Invalid Email or Password"


def test_login_with_nonexistent_email(client):
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "unknown_user@example.com",
            "password": "TestPassword123"
        }
    )

    assert response.status_code == 401
    assert response.json()["message"] == "Invalid Email or Password"

def test_login_with_invalid_email(client):
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "invalid-email",
            "password": "TestPassword123"
        }
    )

    assert response.status_code == 400
    assert response.json()["message"] == "Invalid request data"

def test_login_without_password(client):
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "login_test@example.com"
        }
    )

    assert response.status_code == 400
    assert response.json()["message"] == "Invalid request data"


def test_logout_successfully(client):
    response = client.post(
        "/api/v1/auth/logout"
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Logout successful"
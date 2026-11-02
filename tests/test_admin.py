import jwt
from models import User
from routes.auth.auth import SECRET_KEY
from conftest import TestingSessionLocal
def test_create_user_withour_token(client):
    response=client.post(
        "/api/v1/admin/users",
        json={
            "name":"Test user",
            "email":"testuser@example.com",
            "password":"Testpassword123",
            "role":"USER"
        }

    )
    assert response.status_code == 401
    assert response.json()["message"] == "Access token is required"

def test_create_user_with_invalid_token(client):
    response = client.post(
        "/api/v1/admin/users",
        headers={"access-token": "invalid_token_123"},
        json={
            "name": "Test User",
            "email": "invaliduser@example.com",
            "password": "TestPassword123",
            "role": "USER"
        }
    )

    assert response.status_code == 401
    assert response.json()["message"] == "Invalid token"

def test_create_user_with_user_role(client):
    db=TestingSessionLocal()
    try:
        user=User(
            name="Normal User",
            email="normaluser@example.com",
            password_hash="Normal@123",
            role="USER"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        token=jwt.encode(
            {"email":user.email},
            SECRET_KEY,
            algorithm="HS256"
        )
    finally:
        db.close()

    response=client.post(
        "/api/v1/admin/users",
        headers={"access-token": token},
        json={
            "name": "Another User",
            "email": "anotheruser@example.com",
            "password": "TestPassword123",
            "role": "USER"
        }
    )
    assert response.status_code == 403
    assert response.json()["message"] == "Only admin can add users"


def test_create_user_with_admin_role(client):
    db=TestingSessionLocal()
    try:
        admin=User(
            name="Test admin",
            email="testadmin@example.com",
            password_hash="Testadmin@123",
            role="ADMIN"
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)

        token=jwt.encode(
            {"email":admin.email},
            SECRET_KEY,
            algorithm="HS256"
        )

    finally:
        db.close()

    response=client.post(
        "/api/v1/admin/users",
        headers={"access-token": token},
        json={
            "name": "New Test User",
            "email": "newuser@example.com",
            "password": "TestPassword123",
            "role": "USER"
        }
    )

    assert response.status_code == 200
    assert response.json()["message"] == "User created successfully"
    assert response.json()["created_by"] == "testadmin@example.com"
    assert response.json()["user"]["name"] == "New Test User"
    assert response.json()["user"]["email"] == "newuser@example.com"
    assert response.json()["user"]["role"] == "USER"



def test_create_user_with_duplicate_email(client):
    db=TestingSessionLocal()
    try:
        admin=User(
            name="Test Admin",
            email="duplicate_test_admin@example.com",
            password_hash="Testadmin@123",
            role="ADMIN"
        )

        existing_user=User(
            name="Existing user",
            email="duplicate@example.com",
            password_hash="Exiixtinguser@123",
            role="USER"
        )
        db.add_all([admin,existing_user])
        db.commit()
        token=jwt.encode(
            {"email":admin.email},
            SECRET_KEY,
            algorithm="HS256"
        )
    finally:
        db.close()

    response=client.post(
        "/api/v1/admin/users",
        headers={"access-token":token},
        json={
            "name": "Another User",
            "email": "duplicate@example.com",
            "password": "TestPassword123",
            "role": "USER"
        }

    )

    assert response.status_code == 409
    assert response.json()["message"] == "Email already exists"


def test_create_user_with_invalid_email(client):
    response=client.post(
        "/api/v1/admin/users",
        headers={"access-token":"dummy_token"},
        json={
            "name": "Test User",
            "email": "invalid-email",
            "password": "TestPassword123",
            "role": "USER"
        }
    )

    assert response.status_code == 400
    assert response.json()["message"] == "Invalid request data"

def test_create_user_with_invalid_role(client):
    response = client.post(
        "/api/v1/admin/users",
        headers={"access-token": "dummy_token"},
        json={
            "name": "Test User",
            "email": "invalidrole@example.com",
            "password": "TestPassword123",
            "role": "MANAGER"
        }
    )

    assert response.status_code == 400
    assert response.json()["message"] == "Invalid request data"

def test_create_user_with_short_password(client):
    response = client.post(
        "/api/v1/admin/users",
        headers={"access-token": "dummy_token"},
        json={
            "name": "Test User",
            "email": "shortpassword@example.com",
            "password": "Test12",
            "role": "USER"
        }
    )

    assert response.status_code == 400
    assert response.json()["message"] == "Invalid request data"


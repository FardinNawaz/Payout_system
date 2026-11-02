import jwt
import bcrypt
from models import User
from conftest import TestingSessionLocal
from routes.auth.auth import SECRET_KEY

def test_add_document_successfully(client):
    db=TestingSessionLocal()
    email="document_test@example.com"

    try:
        user=User(
            name="Document Test User",
        email=email,
        password_hash=bcrypt.hashpw(
            b"TestPassword123",
            bcrypt.gensalt()
        ).decode(),
        role="USER"
        )
        db.add(user)
        db.commit()
    finally:
        db.close()

    access_token=jwt.encode(
        {
            "email":email,
            "role":"USER"
        },
        SECRET_KEY,
        algorithm="HS256"
    )
    response=client.post(
        "/api/v1/user/document",
        headers={
            "access-token":access_token
        },
        json={
                "document_name": "AADHAAR",
                "document_number": "123456789012",
                "document_pic_url": "https://example.com/aadhaar.jpg"
            
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["message"] == "Document added successfully"
    assert data["data"]["document_id"]
    assert data["data"]["user_id"]
    assert data["data"]["document_name"] == "AADHAAR"

def test_add_document_with_invalid_token(client):
    response=client.post(
        "api/v1/user/document",
        headers={
            "access-token":"Invalid_token_123"
        },
        json={
            "document_name": "AADHAAR",
            "document_number": "123456789012",
            "document_pic_url": "https://example.com/aadhaar.jpg"
        }
    )
    assert response.status_code == 401
    assert response.json()["message"] == "Invalid token"


def test_add_document_user_not_found(client):

    access_token=jwt.encode(
            {
                "email":"unknown_user@example.com",
                "role":"USER"
            },
            SECRET_KEY,
            algorithm="HS256"
        )


    response=client.post(
        "api/v1/user/document",
        headers={
            "access-token":access_token
        },
        json={
            "document_name": "AADHAAR",
            "document_number": "123456789012",
            "document_pic_url": "https://example.com/aadhaar.jpg"
        }
    )
    assert response.status_code == 401
    assert response.json()["message"] == "User not found"

def test_admin_cannot_add_document(client):
    db=TestingSessionLocal()
    email="admin_document@example.com"

    try:
        user=User(
            name="Admin Test User",
        email=email,
        password_hash=bcrypt.hashpw(
            b"TestPassword123",
            bcrypt.gensalt()
        ).decode(),
        role="ADMIN"
        )
        db.add(user)
        db.commit()
    finally:
        db.close()

    access_token=jwt.encode(
        {
            "email":email,
            "role":"ADMIN"
        },
        SECRET_KEY,
        algorithm="HS256"
    )
    response=client.post(
        "/api/v1/user/document",
        headers={
            "access-token":access_token
        },
        json={
                "document_name": "AADHAAR",
                "document_number": "123456789012",
                "document_pic_url": "https://example.com/aadhaar.jpg"
            
        }
    )
    assert response.status_code == 403
    assert response.json()["message"]=="Only USER role can add documents"
    

def test_add_document_without_access_token(client):
    response = client.post(
        "/api/v1/user/document",
        json={
            "document_name": "AADHAAR",
            "document_number": "123456789012",
            "document_pic_url": "https://example.com/aadhaar.jpg"
        }
    )

    assert response.status_code == 400
    assert response.json()["message"] == "Invalid request data"



def test_add_document_with_invalid_document_name(client):
    response = client.post(
        "/api/v1/user/document",
        headers={
            "access-token": "dummy_token"
        },
        json={
            "document_name": "PASSPORT",
            "document_number": "123456789012",
            "document_pic_url": "https://example.com/document.jpg"
        }
    )

    assert response.status_code == 400
    assert response.json()["message"] == "Invalid request data"


def test_add_document_with_empty_document_number(client):
    response = client.post(
        "/api/v1/user/document",
        headers={
            "access-token": "dummy_token"
        },
        json={
            "document_name": "AADHAAR",
            "document_number": "",
            "document_pic_url": "https://example.com/aadhaar.jpg"
        }
    )

    assert response.status_code == 400
    assert response.json()["message"] == "Invalid request data"

def test_add_document_with_empty_picture_url(client):
    response = client.post(
        "/api/v1/user/document",
        headers={
            "access-token": "dummy_token"
        },
        json={
            "document_name": "AADHAAR",
            "document_number": "123456789012",
            "document_pic_url": ""
        }
    )

    assert response.status_code == 400
    assert response.json()["message"] == "Invalid request data"



def test_add_duplicate_document(client):
    db = TestingSessionLocal()
    email = "duplicate_document_test@example.com"

    try:
        user = User(
            name="Duplicate Document Test",
            email=email,
            password_hash=bcrypt.hashpw(
                b"TestPassword123",
                bcrypt.gensalt()
            ).decode(),
            role="USER"
        )
        db.add(user)
        db.commit()
    finally:
        db.close()

    access_token = jwt.encode(
        {
            "email": email,
            "role": "USER"
        },
        SECRET_KEY,
        algorithm="HS256"
    )

    document_data = {
        "document_name": "AADHAAR",
        "document_number": "123456789012",
        "document_pic_url": "https://example.com/aadhaar.jpg"
    }


    response1 = client.post(
        "/api/v1/user/document",
        headers={"access-token": access_token},
        json=document_data
    )

    assert response1.status_code == 201


    response2 = client.post(
        "/api/v1/user/document",
        headers={"access-token": access_token},
        json=document_data
    )

    assert response2.status_code == 409
    assert response2.json()["message"] == (
        "Document already registered or violates a database constraint"
    )

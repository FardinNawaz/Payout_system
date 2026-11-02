import jwt
import bcrypt

from models import User
from conftest import TestingSessionLocal
from routes.auth.auth import SECRET_KEY

def test_add_beneficiary_successfully(client):
    db = TestingSessionLocal()
    email = "beneficiary_test@example.com"

    try:
        user = User(
            name="Beneficiary Test User",
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

    response = client.post(
        "/api/v1/user/beneficiary",
        headers={
            "access-token": access_token
        },
        json={
            "beneficiary_name": "Rahul Sharma",
            "bank_accounts": [
                {
                    "bank_name": "HDFC Bank",
                    "account_number": "123456789012",
                    "ifsc_code": "HDFC0001234"
                }
            ],
            "upi_accounts": [
                {
                    "upi_id": "rahul@okaxis"
                }
            ]
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Beneficiary added successfully"
    assert data["data"]["beneficiary_id"]
    assert data["data"]["beneficiary_name"] == "Rahul Sharma"

    assert len(data["data"]["bank_accounts"]) == 1
    assert data["data"]["bank_accounts"][0]["bank_id"]
    assert data["data"]["bank_accounts"][0]["bank_name"] == "HDFC Bank"

    assert len(data["data"]["upi_accounts"]) == 1
    assert data["data"]["upi_accounts"][0]["upi_account_id"]
    assert data["data"]["upi_accounts"][0]["upi_id"] == "rahul@okaxis"


def test_add_beneficiary_with_invalid_token(client):
    response = client.post(
        "/api/v1/user/beneficiary",
        headers={
            "access-token": "invalid_token_123"
        },
        json={
            "beneficiary_name": "Rahul Sharma",
            "bank_accounts": [
                {
                    "bank_name": "HDFC Bank",
                    "account_number": "123456789012",
                    "ifsc_code": "HDFC0001234"
                }
            ],
            "upi_accounts": [
                {
                    "upi_id": "rahul@okaxis"
                }
            ]
        }
    )

    assert response.status_code == 401
    assert response.json()["message"] == "Invalid token"


def test_add_beneficiary_user_not_found(client):
    access_token = jwt.encode(
        {
            "email": "unknown_beneficiary@example.com",
            "role": "USER"
        },
        SECRET_KEY,
        algorithm="HS256"
    )

    response = client.post(
        "/api/v1/user/beneficiary",
        headers={
            "access-token": access_token
        },
        json={
            "beneficiary_name": "Rahul Sharma",
            "bank_accounts": [
                {
                    "bank_name": "HDFC Bank",
                    "account_number": "123456789012",
                    "ifsc_code": "HDFC0001234"
                }
            ],
            "upi_accounts": [
                {
                    "upi_id": "rahul@okaxis"
                }
            ]
        }
    )

    assert response.status_code == 401
    assert response.json()["message"] == "user not found"


def test_admin_cannot_add_beneficiary(client):
    db = TestingSessionLocal()
    email = "admin_beneficiary_test@example.com"

    try:
        user = User(
            name="Admin Beneficiary Test",
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

    access_token = jwt.encode(
        {
            "email": email,
            "role": "ADMIN"
        },
        SECRET_KEY,
        algorithm="HS256"
    )

    response = client.post(
        "/api/v1/user/beneficiary",
        headers={
            "access-token": access_token
        },
        json={
            "beneficiary_name": "Rahul Sharma",
            "bank_accounts": [
                {
                    "bank_name": "HDFC Bank",
                    "account_number": "123456789012",
                    "ifsc_code": "HDFC0001234"
                }
            ],
            "upi_accounts": [
                {
                    "upi_id": "rahul@okaxis"
                }
            ]
        }
    )

    assert response.status_code == 403
    assert response.json()["message"] == "Only user can add"



def test_add_beneficiary_without_access_token(client):
    response = client.post(
        "/api/v1/user/beneficiary",
        json={
            "beneficiary_name": "Rahul Sharma",
            "bank_accounts": [
                {
                    "bank_name": "HDFC Bank",
                    "account_number": "123456789012",
                    "ifsc_code": "HDFC0001234"
                }
            ],
            "upi_accounts": [
                {
                    "upi_id": "rahul@okaxis"
                }
            ]
        }
    )

    assert response.status_code == 400
    assert response.json()["message"] == "Invalid request data"



def test_add_beneficiary_token_without_email(client):
    access_token = jwt.encode(
        {
            "role": "USER"
        },
        SECRET_KEY,
        algorithm="HS256"
    )

    response = client.post(
        "/api/v1/user/beneficiary",
        headers={
            "access-token": access_token
        },
        json={
            "beneficiary_name": "Rahul Sharma",
            "bank_accounts": [
                {
                    "bank_name": "HDFC Bank",
                    "account_number": "123456789012",
                    "ifsc_code": "HDFC0001234"
                }
            ],
            "upi_accounts": [
                {
                    "upi_id": "rahul@okaxis"
                }
            ]
        }
    )

    assert response.status_code == 401
    assert response.json()["message"] == "Invalid token Payload"


def test_add_beneficiary_with_only_bank_account(client):
    db = TestingSessionLocal()
    email = "beneficiary_bank_only@example.com"

    try:
        user = User(
            name="Bank Only Test User",
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

    response = client.post(
        "/api/v1/user/beneficiary",
        headers={
            "access-token": access_token
        },
        json={
            "beneficiary_name": "Rahul Sharma",
            "bank_accounts": [
                {
                    "bank_name": "HDFC Bank",
                    "account_number": "987654321012",
                    "ifsc_code": "HDFC0001234"
                }
            ],
            "upi_accounts": []
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Beneficiary added successfully"
    assert data["data"]["beneficiary_id"]
    assert len(data["data"]["bank_accounts"]) == 1
    assert len(data["data"]["upi_accounts"]) == 0



def test_add_beneficiary_with_only_upi_account(client):
    db = TestingSessionLocal()
    email = "beneficiary_upi_only@example.com"

    try:
        user = User(
            name="UPI Only Test User",
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

    response = client.post(
        "/api/v1/user/beneficiary",
        headers={
            "access-token": access_token
        },
        json={
            "beneficiary_name": "Rahul Sharma",
            "bank_accounts": [],
            "upi_accounts": [
                {
                    "upi_id": "rahul@okaxis"
                }
            ]
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Beneficiary added successfully"
    assert data["data"]["beneficiary_id"]
    assert len(data["data"]["bank_accounts"]) == 0
    assert len(data["data"]["upi_accounts"]) == 1
    assert data["data"]["upi_accounts"][0]["upi_account_id"]
    assert data["data"]["upi_accounts"][0]["upi_id"] == "rahul@okaxis"



def test_add_beneficiary_with_duplicate_bank_account(client):
    db = TestingSessionLocal()
    email = "beneficiary_duplicate_bank@example.com"

    try:
        user = User(
            name="Duplicate Bank Test User",
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

    beneficiary_data = {
        "beneficiary_name": "Rahul Sharma",
        "bank_accounts": [
            {
                "bank_name": "HDFC Bank",
                "account_number": "123456789012",
                "ifsc_code": "HDFC0001234"
            }
        ],
        "upi_accounts": []
    }

   
    response1 = client.post(
        "/api/v1/user/beneficiary",
        headers={"access-token": access_token},
        json=beneficiary_data
    )

    assert response1.status_code == 200

   
    response2 = client.post(
        "/api/v1/user/beneficiary",
        headers={"access-token": access_token},
        json=beneficiary_data
    )

    assert response2.status_code == 409
    assert response2.json()["message"] == "Bank account already registered"



def test_add_beneficiary_with_duplicate_upi(client):
    db = TestingSessionLocal()
    email = "beneficiary_duplicate_upi@example.com"

    try:
        user = User(
            name="Duplicate UPI Test User",
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

    beneficiary_data = {
        "beneficiary_name": "Rahul Sharma",
        "bank_accounts": [],
        "upi_accounts": [
            {
                "upi_id": "rahul@okaxis"
            }
        ]
    }

    # First request: should succeed
    response1 = client.post(
        "/api/v1/user/beneficiary",
        headers={"access-token": access_token},
        json=beneficiary_data
    )

    assert response1.status_code == 200

    # Second request: same UPI ID, another beneficiary
    response2 = client.post(
        "/api/v1/user/beneficiary",
        headers={"access-token": access_token},
        json=beneficiary_data
    )

    assert response2.status_code == 409
    assert response2.json()["message"] == "UPI ID already registered"



def test_add_beneficiary_with_multiple_bank_accounts(client):
    db = TestingSessionLocal()
    email = "beneficiary_multi_bank@example.com"

    try:
        user = User(
            name="Multiple Bank Test User",
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

    response = client.post(
        "/api/v1/user/beneficiary",
        headers={"access-token": access_token},
        json={
            "beneficiary_name": "Rahul Sharma",
            "bank_accounts": [
                {
                    "bank_name": "HDFC Bank",
                    "account_number": "111122223333",
                    "ifsc_code": "HDFC0001234"
                },
                {
                    "bank_name": "State Bank of India",
                    "account_number": "444455556666",
                    "ifsc_code": "SBIN0001234"
                }
            ],
            "upi_accounts": []
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Beneficiary added successfully"
    assert len(data["data"]["bank_accounts"]) == 2
    assert len(data["data"]["upi_accounts"]) == 0

    for bank in data["data"]["bank_accounts"]:
        assert bank["bank_id"]


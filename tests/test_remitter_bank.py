import bcrypt
import jwt
from models import User
from conftest import TestingSessionLocal
from routes.auth.auth import SECRET_KEY


def test_add_payment_details(client):
    db=TestingSessionLocal()
    password="Testpassword123"
    email="remitter_test@example.com"

    try:
        user=User(
            name="Remitter Test User",
            email=email,
            password_hash=bcrypt.hashpw(
                password.encode(),bcrypt.gensalt()).decode(),
            role="USER"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    finally:
        db.close()

    access_token=jwt.encode(
        {
            "email":email,
            "role":"USER",
        },
        SECRET_KEY,
        algorithm="HS256"

    )

    response=client.post(
        "/api/v1/user/payment-details",
        headers={
            "access-token": access_token
        },
        json={
            "bank_accounts": [
                {
                    "bank_name": "State Bank of India",
                    "account_number": "123456789012",
                    "ifsc_code": "SBIN0001234"
                }
            ],
            "upi_accounts": [
                {
                    "upi_id": "testuser@okaxis"
                }
            ]
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["message"] == "Payment details added successfully"
    assert len(data["data"]["bank_accounts"]) == 1
    assert len(data["data"]["upi_accounts"]) == 1
    assert data["data"]["bank_accounts"][0]["bank_id"]
    assert data["data"]["upi_accounts"][0]["upi_account_id"]


def test_add_payment_detail_without_token(client):
    response=client.post(
        "/api/v1/user/payment-details",
        json={
            "bank_accounts":[
                {
                    "bank_name":"State bank of India",
                    "account_number":"12345678912",
                    "ifsc_code":"SBIN0001234"
                }
            ],
            "upi_accounts":[
                {
                    "upi_id":"testuser@okaxis"
                }
            ]
        }
    )

    assert response.status_code == 400
    assert response.json()["message"] == "Invalid request data"


def test_add_payment_detail_with_invalid_token(client):
    response=client.post(
        "/api/v1/user/payment-details",
        headers={
            "access-token":"invalid_token"
        },
        json={
            "bank_accounts": [
                {
                    "bank_name": "State Bank of India",
                    "account_number": "123456789012",
                    "ifsc_code": "SBIN0001234"
                }
            ],
            "upi_accounts": [
                {
                    "upi_id": "testuser@okaxis"
                }
            ]
        }
    )

    assert response.status_code == 401
    assert response.json()["message"] == "Invalid token"

def test_add_payment_detail_with_user_not_found(client):
    access_token=jwt.encode(
        {
            "email":"unknown_user@example",
            "role":"USER"
        },
        SECRET_KEY,
        algorithm="HS256"
    )

    response=client.post(
        "/api/v1/user/payment-details",
        headers={
            "access-token":access_token
        },
        json={
            "bank_accounts": [
                {
                    "bank_name": "State Bank of India",
                    "account_number": "123456789012",
                    "ifsc_code": "SBIN0001234"
                }
            ],
            "upi_accounts": [
                {
                    "upi_id": "testuser@okaxis"
                }
            ]
        }

    )

    assert response.status_code == 401
    assert response.json()["message"] == "User not found"

def test_add_payment_detail_with_admin_role(client):
    db=TestingSessionLocal()
    email="admin_remitter@example.com"
    try:
        user=User(
            name="Admin test",
            email=email,
            password_hash=bcrypt.hashpw(
                b"TestPassword@123",
                bcrypt.gensalt()).decode(),
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
        "/api/v1/user/payment-details",
        headers={
            "access-token":access_token
        },
        json={
            "bank_accounts": [
                {
                    "bank_name": "State Bank of India",
                    "account_number": "123456789012",
                    "ifsc_code": "SBIN0001234"
                }
            ],
            "upi_accounts": [
                {
                    "upi_id": "testuser@okaxis"
                }
            ]
        }
    )

    assert response.status_code == 403
    assert response.json()["message"] == ("Only USER role can add payment details")


def test_add_payment_details_with_invalid_account_details(client):
    db=TestingSessionLocal()
    email="invalid_bank_test@example.com"
    try:
        user=User(
            name="Invalid Bank Test User",
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
        db.close

    access_token = jwt.encode(
        {
            "email": email,
            "role": "USER"
        },
        SECRET_KEY,
        algorithm="HS256"
    )

    response=client.post(
        "/api/v1/user/payment-details",
        headers={
            "access-token": access_token
        },
        json={
            "bank_accounts": [
                {
                    "bank_name": "State Bank of India",
                    "account_number": "123ABC789",
                    "ifsc_code": "SBIN0001234"
                }
            ],
            "upi_accounts": [
                {
                    "upi_id": "testuser@okaxis"
                }
            ]
        }
    )
    assert response.status_code == 400
    assert response.json()["message"] == "Invalid request data"


def test_add_payment_details_with_invalid_ifsc_code(client):
    db=TestingSessionLocal()
    email="invalid_ifsc_test@example.com"
    try:
        user=User(
            name="Invalid ifsc code User",
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
        db.close

    access_token = jwt.encode(
        {
            "email": email,
            "role": "USER"
        },
        SECRET_KEY,
        algorithm="HS256"
    )

    response=client.post(
        "/api/v1/user/payment-details",
        headers={
            "access-token": access_token
        },
        json={
            "bank_accounts": [
                {
                    "bank_name": "State Bank of India",
                    "account_number": "123456789012",
                    "ifsc_code": "INVALID1234"
                }
            ],
            "upi_accounts": [
                {
                    "upi_id": "testuser@okaxis"
                }
            ]
        }
    )
    assert response.status_code == 400
    assert response.json()["message"] == "Invalid request data"


def test_add_payment_details_with_invalid_upi_id(client):
    email = "invalid_upi_test@example.com"

    db = TestingSessionLocal()

    try:
        user = User(
            name="Invalid UPI Test User",
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
        "/api/v1/user/payment-details",
        headers={
            "access-token": access_token
        },
        json={
            "bank_accounts": [],
            "upi_accounts": [
                {
                    "upi_id": "invalid-upi"
                }
            ]
        }
    )

    assert response.status_code == 400
    assert response.json()["message"] == "Invalid request data"


def test_add_payment_details_with_empty_accounts(client):
    response = client.post(
        "/api/v1/user/payment-details",
        headers={
            "access-token": "dummy_token"
        },
        json={
            "bank_accounts": [],
            "upi_accounts": []
        }
    )

    assert response.status_code == 400
    assert response.json()["message"] == "Invalid request data"

def test_add_duplicate_bank_account(client):
    email = "duplicate_bank_test@example.com"

    db = TestingSessionLocal()

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

    payment_details = {
        "bank_accounts": [
            {
                "bank_name": "State Bank of India",
                "account_number": "123456789012",
                "ifsc_code": "SBIN0001234"
            }
        ],
        "upi_accounts": []
    }

    response1 = client.post(
        "/api/v1/user/payment-details",
        headers={"access-token": access_token},
        json=payment_details
    )

    assert response1.status_code == 201

    response2 = client.post(
        "/api/v1/user/payment-details",
        headers={"access-token": access_token},
        json=payment_details
    )

    assert response2.status_code == 409
    assert response2.json()["message"] == (
        "One or more bank accounts or UPI IDs "
        "already exist or violate a database constraint")


def test_add_payment_details_with_missing_email_in_token(client):
    access_token = jwt.encode(
        {
            "role": "USER"
        },
        SECRET_KEY,
        algorithm="HS256"
    )

    response = client.post(
        "/api/v1/user/payment-details",
        headers={"access-token": access_token},
        json={
            "bank_accounts": [
                {
                    "bank_name": "State Bank of India",
                    "account_number": "123456789012",
                    "ifsc_code": "SBIN0001234"
                }
            ],
            "upi_accounts": []
        }
    )

    assert response.status_code == 401
    assert response.json()["message"] == "Invalid token payload"

def test_add_only_upi_account(client):
    db=TestingSessionLocal()
    email="only_upi@example.com"

    try:
        user=User(
            name="Only UPI Test User",
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
        "/api/v1/user/payment-details",
        headers={
            "access-token":access_token
        },
        json={
            "bank_accounts":[],
            "upi_accounts":[
                {
                    "upi_id":"onlyupitest@oaxis"
                }
            ]
        }
    )

    assert response.status_code==201
    data=response.json()
    assert data["message"]=="Payment details added successfully"
    assert len(data["data"]["bank_accounts"])==0
    assert len(data["data"]["upi_accounts"])==1
    assert data["data"]["upi_accounts"][0]["upi_account_id"]


def test_add_only_bank_account(client):
    email = "only_bank@example.com"

    db = TestingSessionLocal()

    user = User(
        name="Only Bank Test User",
        email=email,
        password_hash=bcrypt.hashpw(
            b"TestPassword123", bcrypt.gensalt()
        ).decode(),
        role="USER"
    )

    db.add(user)
    db.commit()
    db.close()

    access_token = jwt.encode(
        {"email": email, "role": "USER"},
        SECRET_KEY,
        algorithm="HS256"
    )

    payment_details = {
        "bank_accounts": [
            {
                "bank_name": "State Bank of India",
                "account_number": "987654321012",
                "ifsc_code": "SBIN0001234"
            }
        ],
        "upi_accounts": []
    }

    response = client.post(
        "/api/v1/user/payment-details",
        headers={"access-token": access_token},
        json=payment_details
    )

    assert response.status_code == 201

    data = response.json()

    assert data["message"] == "Payment details added successfully"
    assert len(data["data"]["bank_accounts"]) == 1
    assert len(data["data"]["upi_accounts"]) == 0
    assert data["data"]["bank_accounts"][0]["bank_id"]


def test_add_multiple_upi_accounts(client):
    email = "multiple_upi_test@example.com"

    db = TestingSessionLocal()

    user = User(
        name="Multiple UPI Test User",
        email=email,
        password_hash=bcrypt.hashpw(
            b"TestPassword123", bcrypt.gensalt()
        ).decode(),
        role="USER"
    )

    db.add(user)
    db.commit()
    db.close()

    access_token = jwt.encode(
        {"email": email, "role": "USER"},
        SECRET_KEY,
        algorithm="HS256"
    )

    payment_details = {
        "bank_accounts": [],
        "upi_accounts": [
            {"upi_id": "fardin1@okaxis"},
            {"upi_id": "fardin2@okaxis"},
            {"upi_id": "fardin3@okaxis"}
        ]
    }

    response = client.post(
        "/api/v1/user/payment-details",
        headers={"access-token": access_token},
        json=payment_details
    )

    assert response.status_code == 201

    data = response.json()

    assert data["message"] == "Payment details added successfully"
    assert len(data["data"]["bank_accounts"]) == 0
    assert len(data["data"]["upi_accounts"]) == 3

    for upi in data["data"]["upi_accounts"]:
        assert upi["upi_account_id"]




def test_add_multiple_bank_accounts(client):
    email = "multiple_bank_test@example.com"

    db = TestingSessionLocal()

    user = User(
        name="Multiple Bank Test User",
        email=email,
        password_hash=bcrypt.hashpw(
            b"TestPassword123", bcrypt.gensalt()
        ).decode(),
        role="USER"
    )

    db.add(user)
    db.commit()
    db.close()

    access_token = jwt.encode(
        {"email": email, "role": "USER"},
        SECRET_KEY,
        algorithm="HS256"
    )

    payment_details = {
        "bank_accounts": [
            {
                "bank_name": "State Bank of India",
                "account_number": "111122223333",
                "ifsc_code": "SBIN0001234"
            },
            {
                "bank_name": "HDFC Bank",
                "account_number": "444455556666",
                "ifsc_code": "HDFC0001234"
            }
        ],
        "upi_accounts": []
    }

    response = client.post(
        "/api/v1/user/payment-details",
        headers={"access-token": access_token},
        json=payment_details
    )

    assert response.status_code == 201

    data = response.json()

    assert data["message"] == "Payment details added successfully"
    assert len(data["data"]["bank_accounts"]) == 2
    assert len(data["data"]["upi_accounts"]) == 0

    for bank in data["data"]["bank_accounts"]:
        assert bank["bank_id"]


def test_add_bank_with_empty_name(client):
    payment_details = {
        "bank_accounts": [
            {
                "bank_name": "",
                "account_number": "123456789012",
                "ifsc_code": "SBIN0001234"
            }
        ],
        "upi_accounts": []
    }

    response = client.post(
        "/api/v1/user/payment-details",
        headers={"access-token": "dummy_token"},
        json=payment_details
    )

    assert response.status_code == 400
    assert response.json()["message"] == "Invalid request data"


def test_add_bank_with_short_account_number(client):
    payment_details = {
        "bank_accounts": [
            {
                "bank_name": "State Bank of India",
                "account_number": "1234",
                "ifsc_code": "SBIN0001234"
            }
        ],
        "upi_accounts": []
    }

    response = client.post(
        "/api/v1/user/payment-details",
        headers={"access-token": "dummy_token"},
        json=payment_details
    )

    assert response.status_code == 400
    assert response.json()["message"] == "Invalid request data"

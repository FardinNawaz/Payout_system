
import hashlib
import hmac
import time
import json
import requests

# Use your valid credentials locally
api_key = "lp+live_uwQBcLOyqaaRJEp9_aPSR9m_jszagOTh"
api_secret = "PckhfGP9JTOWCchS05Q6yWSw90_PbBGQ9VKddjvi-yCWjG1qBu_UNT1iyvrKsJnt"

base_url = "http://127.0.0.1:8000"
method = "POST"
path = "/api/v1/payouts"

payload = {
    "reference_id": "REF_TEST_20261023_002",
    "amount": "10.00",
    "currency": "INR",
    "payment_mode": "UPI",
    "sender_bank_id": None,
    "sender_upi_account_id": "14f101af-c7b5-4ffd-8c21-d1383b62524a",
    "beneficiary_id": "2a5a913b-649a-4d8a-be7d-3e5f0842c308",
    "beneficiary_bank_id": None,
    "beneficiary_upi_account_id": "31ffd4ed-6196-47b7-871e-bdf646892834"
}

# Generate the exact body that will be signed and sent
body = json.dumps(payload, separators=(",", ":"))
timestamp = str(int(time.time()))
message = timestamp + method + path + body

signature = hmac.new(
    api_secret.encode("utf-8"),
    message.encode("utf-8"),
    hashlib.sha256
).hexdigest()

headers = {
    "X-API-KEY": api_key,
    "X-TIMESTAMP": timestamp,
    "X-SIGNATURE": signature,
    "Content-Type": "application/json",
}

print("Sending signed payout request...")

try:
    response = requests.post(
        base_url + path,
        data=body,
        headers=headers,
        timeout=30
    )

    print("HTTP Status:", response.status_code)
    print("Response:", response.text)

except requests.RequestException as exc:
    print("Request failed:", exc)

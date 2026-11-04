import os
import httpx
from datetime import datetime, timezone
from decimal import Decimal

ESCROWSTACK_URL = os.getenv(
    "ESCROWSTACK_URL",
    "http://localhost:9000/escrowstack-payout/payout/v1/prod"
)
ESCROWSTACK_API_KEY = os.getenv(
    "ESCROWSTACK_API_KEY",
    "mock_api_key_3"
)
def send_bank_payout(
    payout,
    beneficiary,
    destination
):
    payload = {
        "payouts": [
            {
                "payout_ref": payout.payout_id,
                "amount": format(Decimal(payout.amount), ".2f"),
                "beneficiary": {
                    "name": beneficiary.name,
                    "account_no": destination.account_number,
                    "ifsc": destination.ifsc_code
                },
                "remarks": "Bank payout"
            }
        ],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "signature": "mock_signature"
    }

    headers = {
        "Content-Type": "application/json",
        "apikey": ESCROWSTACK_API_KEY
    }

    print("ESCROWSTACK URL:", ESCROWSTACK_URL)
    print("ESCROWSTACK PAYLOAD:", payload)

    try:
        
        response = httpx.post(
            ESCROWSTACK_URL,
            json=payload,
            headers=headers,
            timeout=15.0
        )

        response.raise_for_status()
        return response.json()

    except httpx.TimeoutException:
        raise Exception("EscrowStack request timed out")

    except httpx.HTTPStatusError as exc:
        raise Exception(
            f"EscrowStack returned HTTP {exc.response.status_code}: "
            f"{exc.response.text}"
        )

    except httpx.RequestError as exc:
        raise Exception(f"Unable to connect to EscrowStack: {exc}")

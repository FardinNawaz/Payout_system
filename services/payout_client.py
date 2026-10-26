
import hashlib
import hmac
import json
import os
import time

import requests


class PayoutClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.api_key = os.environ["PAYOUT_API_KEY"]
        self.api_secret = os.environ["PAYOUT_API_SECRET"]

    def request(self, method: str, path: str, payload: dict | None = None):
        timestamp = str(int(time.time()))

        # Use the exact JSON body that will be signed and sent.
        body = (
            json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
            if payload is not None
            else ""
        )

        message = timestamp + method.upper() + path + body

        signature = hmac.new(
            self.api_secret.encode("utf-8"),
            message.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

        headers = {
            "X-API-KEY": self.api_key,
            "X-TIMESTAMP": timestamp,
            "X-SIGNATURE": signature,
        }

        if payload is not None:
            headers["Content-Type"] = "application/json"

        response = requests.request(
            method=method.upper(),
            url=f"{self.base_url}{path}",
            headers=headers,
            data=body if payload is not None else None,
            timeout=30,
        )

        response.raise_for_status()
        return response.json()

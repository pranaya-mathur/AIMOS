"""
SMS Integration via Twilio.

Requires:
- TWILIO_ACCOUNT_SID
- TWILIO_AUTH_TOKEN
- TWILIO_FROM_NUMBER
"""

import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class SmsError(RuntimeError):
    pass

def send_sms(to_phone: str, body: str) -> dict:
    """
    Sends a plain text SMS to a recipient.
    If MOCK_TWILIO=1, generates a fake success response.
    """
    if os.getenv("MOCK_TWILIO") == "1":
        logger.info("[MOCK TWILIO] SMS to %s: %s", to_phone, body)
        return {"provider": "twilio", "status": "mock_success", "mock": True}

    try:
        from twilio.rest import Client
        
        account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        from_phone = os.getenv("TWILIO_FROM_NUMBER")

        if not all([account_sid, auth_token, from_phone]):
            raise SmsError("Missing Twilio credentials (ACCOUNT_SID, AUTH_TOKEN, FROM_NUMBER)")

        client = Client(account_sid, auth_token)
        message = client.messages.create(
            body=body,
            from_=from_phone,
            to=to_phone
        )
        
        logger.info("SMS successfully sent via Twilio. Status: %s", message.status)
        return {
            "provider": "twilio",
            "status": message.status,
            "sid": message.sid,
            "to": to_phone
        }
        
    except ImportError:
        logger.error("twilio library not installed")
        raise SmsError("twilio library is missing. Run pip install twilio")
    except Exception as e:
        logger.exception("Twilio SMS failed")
        raise SmsError(str(e))

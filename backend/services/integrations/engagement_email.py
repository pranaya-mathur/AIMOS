"""
Email Integration via SendGrid.

Requires:
- SENDGRID_API_KEY
- SENDGRID_FROM_EMAIL
"""

import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class EmailError(RuntimeError):
    pass

def send_email(to_email: str, subject: str, body: str) -> dict:
    """
    Sends a plain text email to a recipient.
    If MOCK_SENDGRID=1, generates a fake success response.
    """
    if os.getenv("MOCK_SENDGRID") == "1":
        logger.info("[MOCK SENDGRID] Email to %s: %s", to_email, subject)
        return {"provider": "sendgrid", "status": "mock_success", "mock": True}

    try:
        from sendgrid import SendGridAPIClient
        from sendgrid.helpers.mail import Mail
        
        api_key = os.getenv("SENDGRID_API_KEY")
        from_email = os.getenv("SENDGRID_FROM_EMAIL")

        if not api_key or not from_email:
            raise EmailError("Missing SendGrid credentials (SENDGRID_API_KEY, SENDGRID_FROM_EMAIL)")

        message = Mail(
            from_email=from_email,
            to_emails=to_email,
            subject=subject,
            plain_text_content=body
        )
        
        sg = SendGridAPIClient(api_key)
        response = sg.send(message)
        
        logger.info("Email successfully sent via SendGrid. Status: %s", response.status_code)
        return {
            "provider": "sendgrid",
            "status": response.status_code,
            "to": to_email,
            "subject": subject
        }
        
    except ImportError:
        logger.error("sendgrid library not installed")
        raise EmailError("sendgrid library is missing. Run pip install sendgrid")
    except Exception as e:
        logger.exception("SendGrid email failed")
        raise EmailError(str(e))

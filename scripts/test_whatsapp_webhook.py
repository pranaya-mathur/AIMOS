#!/usr/bin/env python3
import requests
import sys

def main():
    # Use localhost or specific URL from args if needed
    url = "http://localhost:8000/webhooks/whatsapp"
    
    # Standard Meta WhatsApp Cloud API payload structure
    # Ref: https://developers.facebook.com/docs/whatsapp/cloud-api/webhooks/payload-examples
    payload = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "WHATSAPP_BUSINESS_ACCOUNT_ID",
                "changes": [
                    {
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {
                                "display_phone_number": "15550000000",
                                "phone_number_id": "1234567890"
                            },
                            "contacts": [
                                {
                                    "profile": {
                                        "name": "John Doe"
                                    },
                                    "wa_id": "1234567890"
                                }
                            ],
                            "messages": [
                                {
                                    "from": "1234567890",
                                    "id": "wamid.HBgLMTIzNDU2Nzg5MAVFAitDRkUzMDAwMDAwMDAwAA==",
                                    "timestamp": "1670000000",
                                    "text": {
                                        "body": "Hello, I want to learn more about AIMOS!"
                                    },
                                    "type": "text"
                                }
                            ]
                        },
                        "field": "messages"
                    }
                ]
            }
        ]
    }
    
    print(f"Sending test WhatsApp message to {url}...")
    try:
        resp = requests.post(url, json=payload, timeout=5)
        print(f"Status Code: {resp.status_code}")
        try:
            print(f"Response: {resp.json()}")
        except Exception:
            print(f"Response Text: {resp.text}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

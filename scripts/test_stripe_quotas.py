#!/usr/bin/env python3
import requests
import json
import sys
import os

BASE_URL = "http://localhost:8000"

def get_user_quota(email):
    import subprocess
    cmd = f"docker-compose exec -T api python3 -c \"from db import SessionLocal; from models import User; db=SessionLocal(); u=db.query(User).filter(User.email == '{email}').first(); print(f'{{u.id}}|{{u.monthly_campaign_quota or 0}}|{{u.monthly_token_quota or 0}}'); db.close()\""
    try:
        res = subprocess.check_output(cmd, shell=True).decode().strip()
        uid, c, t = res.split("|")
        return uid, int(c), int(t)
    except Exception as e:
        print(f"Error getting user quota: {e}")
        return None, 0, 0

def main():
    print("--- TESTING STRIPE -> QUOTA SYNC ---")
    
    email = "aimos-dev@example.com"
    uid, initial_c, initial_t = get_user_quota(email)
    if not uid:
        print("ERROR: Dev user not found. Run db_init.py first.")
        return 1
        
    print(f"Initial Quotas for {email}: Campaigns={initial_c}, Tokens={initial_t}")

    # Simulating a PRO plan update
    # We use 'test_bypass' signature and 'test_bypass' secret in the API env
    payload = {
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "id": "cs_test_123",
                "metadata": {
                    "user_id": uid,
                    "price_id": "price_pro_plan"
                }
            }
        }
    }

    print("\nSending mock Stripe webhook (PRO PLAN)...")
    headers = {"stripe-signature": "test_bypass_sig"}
    resp = requests.post(f"{BASE_URL}/billing/stripe/webhook", json=payload, headers=headers)
    
    # Wait for processing
    print(f"Webhook response: {resp.status_code} {resp.text}")
    
    # Re-check quotas
    _, new_c, new_t = get_user_quota(email)
    print(f"New Quotas for {email}: Campaigns={new_c}, Tokens={new_t}")
    
    if new_c > initial_c or (new_c == 100 and initial_c != 100):
        print("✅ SUCCESS: Quotas updated correctly!")
    else:
        print("❌ FAILURE: Quotas not updated.")

    return 0

if __name__ == "__main__":
    main()

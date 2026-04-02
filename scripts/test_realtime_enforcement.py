#!/usr/bin/env python3
"""
Test script for real-time quota enforcement in LangGraph pipeline.
Sets a low token cap and verifies that the pipeline stops mid-walk.
"""
import time
import uuid
import subprocess
import requests

BASE_URL = "http://localhost:8000"

def get_user_id(email):
    cmd = f"docker-compose exec -T api python3 -c \"from db import SessionLocal; from models import User; db=SessionLocal(); u=db.query(User).filter(User.email == '{email}').first(); print(u.id); db.close()\""
    return subprocess.check_output(cmd, shell=True).decode().strip()

def set_user_quota(user_id, token_quota):
    cmd = f"docker-compose exec -T api python3 -c \"from db import SessionLocal; from models import User; db=SessionLocal(); u=db.query(User).filter(User.id == '{user_id}').first(); u.monthly_token_quota = {token_quota}; u.subscription_tier = 'free'; db.commit(); db.close()\""
    subprocess.run(cmd, shell=True)

def create_usage_event(user_id, tokens):
    # Simulate existing usage
    cmd = f"docker-compose exec -T api python3 -c \"from db import SessionLocal; from models import UsageEvent; import uuid; db=SessionLocal(); ev=UsageEvent(id=str(uuid.uuid4()), user_id='{user_id}', provider='openai', total_tokens={tokens}); db.add(ev); db.commit(); db.close()\""
    subprocess.run(cmd, shell=True)

def main():
    email = "aimos-dev@example.com"
    uid = get_user_id(email)
    print(f"Testing User: {email} ({uid})")

    # 1. Set very low quota
    print("\nSetting token quota to 5,000...")
    set_user_quota(uid, 5000)

    # 2. Add usage that almost hits the cap
    print("Adding 4,900 tokens of existing usage...")
    create_usage_event(uid, 4900)

    # 3. Create a campaign
    print("\nStarting campaign...")
    payload = {
        "name": "Quota Test Campaign",
        "input": {"business_goal": "Test real-time enforcement"}
    }
    resp = requests.post(f"{BASE_URL}/campaign/create", json=payload)
    if resp.status_code != 200:
        print(f"Error creating campaign: {resp.text}")
        return
    
    cid = resp.json()["campaign_id"]
    print(f"Campaign ID: {cid}")

    # 4. Wait and monitor status
    print("Waiting for pipeline to execute and hit quota...")
    for _ in range(20):
        time.sleep(5)
        resp = requests.get(f"{BASE_URL}/campaign/{cid}")
        status = resp.json()["status"]
        print(f"  Current status: {status}")
        if status == "failed":
            print("\n✅ SUCCESS: Campaign failed as expected due to quota enforcement!")
            return
        if status == "completed":
            print("\n❌ FAILURE: Campaign completed despite low quota!")
            return

    print("\n⌛ Timeout: Campaign still processing.")

if __name__ == "__main__":
    main()

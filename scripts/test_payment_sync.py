
import requests
import json
import time
import subprocess

BASE_URL = "http://localhost:8000"

def test_payment_sync():
    print("🚀 Starting Payment Sync Test (Final)...")
    
    # 1. Find a real User ID from the DB
    print("\n🔍 Fetching dev user...")
    get_user_py = """
import sys
sys.path.append('/app')
from db import SessionLocal
from models import User
db=SessionLocal()
u=db.query(User).filter(User.email == 'aimos-dev@example.com').first()
if u:
    print(u.id)
db.close()
"""
    try:
        user_id = subprocess.check_output(["docker-compose", "exec", "-T", "api", "python3", "-c", get_user_py]).decode().strip()
        if not user_id:
            print("❌ Dev user not found. Please run 'make seed' first.")
            return
        print(f"✅ Found Dev User: {user_id}")
    except Exception as e:
        print(f"❌ Could not query user: {e}")
        return

    # 2. Inject Campaign with valid user_id
    campaign_id = "test-sync-campaign-prod"
    print(f"\n1️⃣ Injecting campaign '{campaign_id}'...")
    
    py_code = f"""
import sys
sys.path.append('/app')
from db import SessionLocal
from models import Campaign
db=SessionLocal()
c=db.query(Campaign).filter(Campaign.id == '{campaign_id}').first()
if not c:
    c=Campaign(
        id='{campaign_id}', 
        user_id='{user_id}', 
        name='Live Sync Test', 
        status='pending_payment', 
        input={{"business_name": "Test", "goals": "Sync Test"}}
    )
    db.add(c)
    db.commit()
print('SUCCESS_DB')
db.close()
"""
    try:
        out = subprocess.check_output(["docker-compose", "exec", "-T", "api", "python3", "-c", py_code]).decode().strip()
        if "SUCCESS_DB" in out:
            print("✅ Ready for payment simulation.")
        else:
            print(f"❌ DB update error: {out}")
            return
    except Exception as e:
        print(f"❌ DB Injection failed: {e}")
        return

    # 3. Simulate Stripe Webhook
    print("\n2️⃣ Sending Mock Stripe Webhook (checkout.session.completed)...")
    webhook_payload = {
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "id": "cs_test_final",
                "metadata": {
                    "campaign_id": campaign_id
                }
            }
        }
    }
    
    # We bypass signature check using 'test_bypass' which is usually set in dev env
    response = requests.post(
        f"{BASE_URL}/billing/stripe/webhook",
        json=webhook_payload,
        headers={"stripe-signature": "test_bypass"} 
    )
    
    if response.status_code == 200:
        print(f"✅ Webhook processed. Response: {response.json()}")
    else:
        print(f"❌ Webhook failed! {response.status_code}: {response.text}")

    # 4. Final Verification
    print("\n3️⃣ Verifying change in DB...")
    py_verify = f"""
import sys
sys.path.append('/app')
from db import SessionLocal
from models import Campaign
db=SessionLocal()
c=db.query(Campaign).filter(Campaign.id == '{campaign_id}').first()
print(c.status)
db.close()
"""
    res = subprocess.check_output(["docker-compose", "exec", "-T", "api", "python3", "-c", py_verify]).decode().strip()
    
    if res == "paid":
        print(f"\n🎉 BOOM! Payment Sync Verified.")
        print(f"Campaign: {campaign_id}")
        print(f"Status Change: pending_payment ➔ {res} ✅")
    else:
        print(f"❌ Sync failed. Status: {res}")

if __name__ == "__main__":
    test_payment_sync()

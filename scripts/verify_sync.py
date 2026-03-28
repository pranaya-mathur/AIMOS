#!/usr/bin/env python3
import requests
import time
import sys

BASE_URL = "http://localhost:8000"

def check_db_rows(table_name):
    # Helper to check rows via a temporary debug check
    # In a real app we'd use a private admin endpoint
    import subprocess
    cmd = f"docker-compose exec -T api python3 -c \"from db import SessionLocal; from sqlalchemy import text; db=SessionLocal(); print(db.execute(text('SELECT count(*) FROM {table_name}')).fetchone()[0]); db.close()\""
    res = subprocess.check_output(cmd, shell=True).decode().strip()
    return int(res)

def main():
    print("--- STARTING END-TO-END VERIFICATION ---")
    
    # 1. Health Check
    resp = requests.get(f"{BASE_URL}/health/ready")
    if resp.status_code != 200:
        print("❌ API not ready")
        sys.exit(1)
    print("✅ API is ready")

    # 2. WhatsApp Inbound Test
    print("\nTesting WhatsApp Inbound...")
    initial_leads = check_db_rows("leads")
    initial_msgs = check_db_rows("conversation_messages")
    
    payload = {
        "object": "whatsapp_business_account",
        "entry": [{"changes": [{"value": {
            "messages": [{"from": "9876543210", "text": {"body": "Verifying sync!"}}],
            "contacts": [{"profile": {"name": "Sync Verifier"}}]
        }}]}]
    }
    requests.post(f"{BASE_URL}/webhooks/whatsapp", json=payload)
    
    print("Waiting for worker...")
    time.sleep(5)
    
    new_leads = check_db_rows("leads")
    new_msgs = check_db_rows("conversation_messages")
    
    if new_leads > initial_leads and new_msgs >= initial_msgs + 2:
        print("✅ WhatsApp Inbound: PASS (Lead created, Messages stored)")
    else:
        print(f"❌ WhatsApp Inbound: FAIL (Leads: {initial_leads}->{new_leads}, Msgs: {initial_msgs}->{new_msgs})")

    # 3. Optimization Loop Test
    print("\nTesting Optimization Loop...")
    initial_metrics = check_db_rows("campaign_metrics")
    
    # Create an active campaign
    c_resp = requests.post(f"{BASE_URL}/campaign/create", json={"name": "Sync Test", "input": {"test": "true"}})
    cid = c_resp.json()["campaign_id"]
    requests.patch(f"{BASE_URL}/campaign/{cid}", json={"status": "active"})
    
    # Trigger tick
    import subprocess
    subprocess.check_call(f"docker-compose exec -T api python3 -c \"from tasks import optimization_tick; optimization_tick.delay().get()\"", shell=True)
    
    new_metrics = check_db_rows("campaign_metrics")
    
    # Check campaign output
    campaign = requests.get(f"{BASE_URL}/campaign/{cid}").json()
    has_directives = "optimization_directives" in (campaign.get("output") or {})
    
    if new_metrics > initial_metrics and has_directives:
        print("✅ Optimization Loop: PASS (Metrics stored, Directives generated)")
    else:
        print(f"❌ Optimization Loop: FAIL (Metrics: {initial_metrics}->{new_metrics}, Directives: {has_directives})")

    print("\n--- VERIFICATION COMPLETE ---")

if __name__ == "__main__":
    main()

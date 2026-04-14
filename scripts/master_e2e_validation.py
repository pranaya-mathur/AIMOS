#!/usr/bin/env python3
import requests
import json
import time
import uuid
import sys

BASE_URL = "http://localhost:8000"
DEV_EMAIL = "aimos-dev@example.com"
DEV_PASS = "devpass123"

def print_step(msg):
    print(f"\n[E2E] {msg}...")

def get_token():
    resp = requests.post(f"{BASE_URL}/auth/login", json={"email": DEV_EMAIL, "password": DEV_PASS})
    if resp.status_code == 200:
        return resp.json().get("access_token")
    return None

def main():
    print("=== AIMOS ENTERPRISE MASTER E2E VALIDATION ===\n")
    
    token = get_token()
    if not token:
        print("❌ Auth failed. Ensure db_init.py was run.")
        sys.exit(1)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # PHASE 0: Pre-requisites (Onboarding & Brand)
    print_step("Phase 0: Environment Setup")
    onboarding_payload = {
        "name": "E2E Test Brand",
        "category": "Technology",
        "description": "Enterprise AI solutions for marketing automation.",
        "business_type": "SaaS",
        "industry": "Software",
        "marketing_goal": "leads"
    }
    # Create brand profile via upsert
    resp = requests.post(f"{BASE_URL}/brand", json=onboarding_payload, headers=headers)
    if resp.status_code == 200:
        print("✅ Brand Profile Created/Updated")
    else:
        print(f"❌ Brand Profile FAIL: {resp.status_code} {resp.text}")
        sys.exit(1)

    # PHASE 1: Governance & Whitelabeling (M5)
    print_step("Phase 1: Governance & Whitelabeling")
    whitelabel_payload = {
        "site_name": "E2E Validated Hub",
        "primary_color": "#ff0000",
        "logo_url": "https://example.com/logo.png"
    }
    # NOTE: If this fails with 403, it means the user org_id is missing in session
    resp = requests.patch(f"{BASE_URL}/org/config", json=whitelabel_payload, headers=headers)
    if resp.status_code == 200:
        print("✅ Whitelabel Update OK")
    else:
        print(f"❌ Whitelabel Update FAIL: {resp.status_code} {resp.text}")
        
    # Check Org Config
    resp = requests.get(f"{BASE_URL}/org/config", headers=headers)
    if resp.status_code == 200:
        print(f"✅ Org Config Retrieval OK (Site: {resp.json().get('site_name')})")

    # PHASE 2: Brand Engine (M2)
    print_step("Phase 2: AI Brand Engine")
    resp = requests.post(f"{BASE_URL}/brand/generate-kit", headers=headers)
    if resp.status_code == 200:
        print("✅ Brand Kit Generation SUCCESS")
        kit = resp.json()
        print(f"   Strategy: {kit.get('strategy', {}).get('brand_positioning', 'OK')[:50]}...")
    else:
        print(f"❌ Brand Kit Generation FAIL: {resp.status_code} {resp.text}")

    # PHASE 3: Campaign Lifecycle (M3)
    print_step("Phase 3: Campaign Lifecycle")
    campaign_payload = {
        "name": "E2E Master Campaign",
        "objective": "leads",
        "platform": "both",
        "total_budget": 5000,
        "input": {"brief": "E2E Validation of the full pipeline."}
    }
    resp = requests.post(f"{BASE_URL}/campaign/create", json=campaign_payload, headers=headers)
    if resp.status_code in (200, 201):
        task_id = resp.json().get("task_id")
        campaign_id = resp.json().get("campaign_id")
        print(f"✅ Campaign Created: {campaign_id}, Task: {task_id}")
        
        # Poll for completion
        print("   Polling for completion...")
        for _ in range(10): 
            jr = requests.get(f"{BASE_URL}/job/{task_id}", headers=headers)
            if jr.status_code == 200:
                js = jr.json()
                if js.get("status") == "SUCCESS":
                    print("✅ Campaign Pipeline SUCCESS")
                    break
                elif js.get("status") == "FAILURE":
                    print(f"❌ Campaign Pipeline FAILURE: {js.get('result')}")
                    break
            time.sleep(3)
    else:
        print(f"❌ Campaign Creation FAIL: {resp.status_code}")

    # PHASE 4: Sales Intelligence (M4)
    print_step("Phase 4: Sales Intelligence (Lead Scoring)")
    whatsapp_payload = {
        "object": "whatsapp_business_account",
        "entry": [{
            "changes": [{
                "value": {
                    "messages": [{
                        "from": "1234567890",
                        "text": {"body": "I want to buy the enterprise plan now. What is the pricing?"},
                        "type": "text"
                    }]
                }
            }]
        }]
    }
    resp = requests.post(f"{BASE_URL}/webhooks/whatsapp", json=whatsapp_payload)
    if resp.status_code == 200:
        print("✅ WhatsApp Inbound Simulated")
        time.sleep(4) # Wait for AI scoring
        
        leads_resp = requests.get(f"{BASE_URL}/leads", headers=headers)
        if leads_resp.status_code == 200:
            leads = leads_resp.json()
            high_intent_lead = next((l for l in leads if l.get("score", 0) > 60), None)
            if high_intent_lead:
                print(f"✅ Lead Scoring OK: Found high-intent lead (Score: {high_intent_lead['score']}, Intent: {high_intent_lead['intent']})")
            else:
                print(f"⚠️ Lead scoring: did not find high intent lead in {len(leads)} leads.")
        else:
            print(f"❌ Leads Retrieval FAIL: {leads_resp.status_code}")

    # PHASE 5: Analytics & Insights (M3)
    print_step("Phase 5: Analytics & Insights")
    resp = requests.get(f"{BASE_URL}/analytics/global", headers=headers)
    if resp.status_code == 200:
        summary = resp.json().get("summary", {})
        print(f"✅ Analytics Summary OK (ROI: {summary.get('roi', 0):.2%})")
    else:
        print(f"❌ Analytics Retrieval FAIL")

    print("\n=== E2E VALIDATION COMPLETE ===")

if __name__ == "__main__":
    main()

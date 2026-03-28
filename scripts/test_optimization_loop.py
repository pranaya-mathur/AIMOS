#!/usr/bin/env python3
import argparse
import sys
import os
import time
import httpx

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", default="http://localhost:8000")
    args = ap.parse_args()
    
    base = args.base_url.rstrip("/")
    
    # 1. Create a campaign
    print("Creating test campaign...")
    with httpx.Client(timeout=60.0) as client:
        # We assume AUTH_DISABLED=1 or we use the dev token if set
        headers = {}
        token = os.environ.get("AIMOS_E2E_TOKEN")
        if token:
            headers["Authorization"] = f"Bearer {token}"
            
        cr = client.post(
            f"{base}/campaign/create",
            json={"name": "Optimization Loop Test", "input": {"product": "AI Loop", "goal": "Scale"}},
            headers=headers
        )
        if cr.status_code not in (200, 201):
            print(f"Error creating campaign: {cr.text}")
            return 1
        
        campaign_id = cr.json()["campaign_id"]
        print(f"Campaign created: {campaign_id}")
        
        # 2. Force status to 'active' via PATCH
        # In a real flow, this happens after payment/launch. 
        # For this test, we skip straight to optimization.
        print("Setting campaign status to 'active'...")
        pr = client.patch(
            f"{base}/campaign/{campaign_id}",
            json={"status": "active"},
            headers=headers
        )
        if pr.status_code != 200:
            print(f"Error patching campaign: {pr.text}")
            return 1

        print("Campaign is now ACTIVE.")
        
        # 3. Trigger the optimization tick
        # Since we don't have a public endpoint for the Beat task, 
        # the user would usually wait for the hour.
        # FOR THIS TEST: We'll instruct the user to run it via docker exec 
        # OR we could add a temporary debug endpoint.
        print("\n--- NEXT STEPS ---")
        print("To verify the loop, run this command in your terminal:")
        print(f"docker-compose exec api python3 -c \"from tasks import optimization_tick; print(optimization_tick.delay().get())\"")
        print("\nThen, check the campaign output for 'optimization_directives':")
        print(f"curl -s {base}/campaign/{campaign_id} | jq '.output.optimization_directives'")

    return 0

if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
AIMOS PILOT SIMULATOR
Runs a full 12-agent enterprise campaign pipeline with real business data.
No public tunnel or Bubble connection required.
"""

import os
import sys
import time
import json
import httpx
import argparse

# ANSI Colors for terminal output
BLUE = "\033[94m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
END = "\033[0m"

AGENT_LIST = [
    "business_analyzer", "brand_builder", "content_studio", "campaign_builder",
    "social_media_manager", "lead_capture", "sales_agent", "customer_engagement",
    "analytics_engine", "optimization_engine", "growth_planner", "business_dashboard"
]

def main():
    parser = argparse.ArgumentParser(description="AIMOS Pilot Simulator")
    parser.add_argument("--product", default="Premium 3BHK Real Estate Noida", help="Service/Product name")
    parser.add_argument("--audience", default="Investors and 35-45yr High Net Worth Individuals", help="Target audience")
    parser.add_argument("--goal", default="Drive 100+ high-intent leads via Noida/Ggn ads", help="Campaign goal")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000", help="API URL")
    parser.add_argument("--vertical", default="Real_Estate", help="Industry vertical (Dental, SaaS, etc.)")
    args = parser.parse_args()

    print(f"\n{BOLD}{BLUE}🚀 AIMOS ENTERPRISE PILOT SIMULATOR{END}")
    print(f"{BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{END}")
    print(f"{BOLD}Product:{END}  {args.product}")
    print(f"{BOLD}Audience:{END} {args.audience}")
    print(f"{BOLD}Goal:{END}     {args.goal}")
    print(f"{BOLD}Vertical:{END} {args.vertical}")
    print(f"{BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{END}\n")

    client = httpx.Client(base_url=args.base_url, timeout=60.0)

    # 1. Auth (Try local dev defaults)
    try:
        login_res = client.post("/auth/login", json={"email": "aimos-dev@example.com", "password": "devpass123"})
        if login_res.status_code == 200:
            token = login_res.json()["access_token"]
            client.headers["Authorization"] = f"Bearer {token}"
            print(f"✅ {GREEN}Authenticated as aimos-dev@example.com{END}")
        else:
            print(f"⚠️  {YELLOW}Auth failed (optional in dev). Proceeding...{END}")
    except Exception as e:
        print(f"⚠️  {YELLOW}API not reachable at {args.base_url}. Ensure stack is running.{END}")
        return

    # 2. Create Campaign
    print(f"📦 {BOLD}Initializing 12-Agent Pipeline...{END}")
    payload = {
        "name": f"Pilot: {args.product}",
        "input": {
            "product": args.product,
            "audience": args.audience,
            "goal": args.goal,
            "industry_vertical": args.vertical
        }
    }
    
    try:
        create_res = client.post("/campaign/create", json=payload)
        if create_res.status_code not in (200, 201):
            print(f"❌ {RED}Failed to create campaign: {create_res.text}{END}")
            return
        
        task_id = create_res.json()["task_id"]
        campaign_id = create_res.json()["campaign_id"]
        print(f"✅ {GREEN}Campaign created (ID: {campaign_id}). Task: {task_id}{END}")
    except Exception as e:
        print(f"❌ {RED}Connection error: {e}{END}")
        return

    # 3. Polling with Progress
    print(f"\n{BOLD}🤖 AI Agents are working...{END}")
    
    last_agent_idx = -1
    start_time = time.time()
    
    while True:
        try:
            job_res = client.get(f"/job/{task_id}")
            if job_res.status_code != 200:
                print(f"⚠️  {YELLOW}Wait...{END}")
                time.sleep(2)
                continue
            
            data = job_res.json()
            status = data.get("status")
            
            if status == "SUCCESS":
                result = data.get("result", {})
                print(f"\n✨ {BOLD}{GREEN}PIPELINE COMPLETE!{END}")
                break
            elif status == "FAILURE":
                print(f"\n❌ {RED}Pipeline Failed: {data.get('result')}{END}")
                return
            
            # Show progress by counting finished agents in result state (if partially returned)
            # Since LangGraph state evolves, we can check the 'agent_outputs' dict
            partial_result = data.get("result")
            if partial_result and isinstance(partial_result, dict):
                outputs = partial_result.get("agent_outputs", {})
                for i, agent in enumerate(AGENT_LIST):
                    if agent in outputs and i > last_agent_idx:
                        print(f"   [{i+1}/12] ✅ {agent.replace('_', ' ').title()} finished.")
                        last_agent_idx = i
            
            sys.stdout.write(f"\r   ⏳ Processing... ({int(time.time() - start_time)}s)")
            sys.stdout.flush()
            time.sleep(2)
            
        except KeyboardInterrupt:
            print(f"\n🛑 {YELLOW}Simulation aborted by user.{END}")
            return
        except Exception as e:
            print(f"\n⚠️  {YELLOW}Polling error: {e}{END}")
            time.sleep(5)

    # 4. Final Output Display
    print(f"\n{BOLD}{BLUE}🏆 FINAL STRATEGY OUTPUT (JSON){END}")
    print(f"{BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{END}")
    
    # We clean up the result to match the user's "Desired Results" format exactly
    # Duration and Summary were added to the 'result' dict in tasks.py
    
    print(json.dumps(result, indent=2))
    print(f"{BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{END}")
    print(f"\n{BOLD}Summary:{END} {result.get('summary', 'N/A')}")
    print(f"{BOLD}Total Time:{END} {result.get('duration_ms', 0) / 1000:.2f}s")
    print(f"\n🚀 {BOLD}{GREEN}Simulator Finished. Ready to scale to AWS.{END}\n")

if __name__ == "__main__":
    main()

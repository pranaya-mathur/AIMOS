#!/usr/bin/env python3
import requests
import uuid

BASE_URL = "http://localhost:8000"

def test_analytics_api():
    print("Testing Analytics API...")
    # Using the dev user to check global stats
    resp = requests.get(f"{BASE_URL}/analytics/global", auth=("aimos-dev@example.com", "devpass123"))
    if resp.status_code == 200:
        print("✅ Analytics Global OK")
        print(resp.json())
    else:
        print(f"❌ Analytics Global FAIL: {resp.status_code}")

def test_usage_api():
    print("\nTesting Usage API...")
    resp = requests.get(f"{BASE_URL}/analytics/usage", auth=("aimos-dev@example.com", "devpass123"))
    if resp.status_code == 200:
        print("✅ Usage API OK")
        print(resp.json())
    else:
        print(f"❌ Usage API FAIL: {resp.status_code}")

def test_vertical_specialization():
    print("\nTesting Vertical Specialization (Dry Run Simulation)...")
    # This just ensures we can create a campaign with a vertical
    cid = str(uuid.uuid4())
    payload = {
        "name": "Real Estate Test",
        "input": {
            "industry_vertical": "Real Estate",
            "goals": "Sell 5 condos in Downtown"
        }
    }
    resp = requests.post(f"{BASE_URL}/campaign/create", json=payload, auth=("aimos-dev@example.com", "devpass123"))
    if resp.status_code == 200:
        print("✅ Specialized Campaign Creation OK")
        print(resp.json())
    else:
        print(f"❌ Specialized Campaign Creation FAIL: {resp.status_code}")

def main():
    print("=== AIMOS ENTERPRISE FEATURES VERIFICATION ===\n")
    test_analytics_api()
    test_usage_api()
    test_vertical_specialization()

if __name__ == "__main__":
    main()

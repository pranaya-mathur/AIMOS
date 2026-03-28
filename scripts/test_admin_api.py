import requests
import sys

BASE_URL = "http://localhost:8000"

def test_admin_flow():
    print("--- Testing Admin & Quota Flow ---")
    
    # 1. Register a test user
    test_user = {
        "email": "quota-test@example.com",
        "password": "password123",
        "full_name": "Quota Test User"
    }
    resp = requests.post(f"{BASE_URL}/auth/register", json=test_user)
    if resp.status_code == 409:
        print("User already exists, proceeding to login.")
    elif resp.status_code != 200:
        print(f"Failed to register: {resp.status_code} {resp.text}")
        sys.exit(1)
    else:
        print("User registered.")

    # 2. Login as regular user
    resp = requests.post(f"{BASE_URL}/auth/login", json={"email": test_user["email"], "password": test_user["password"]})
    user_token = resp.json()["access_token"]
    user_id = resp.json().get("user_id") # Note: login might not return user_id, let's see
    headers = {"Authorization": f"Bearer {user_token}"}
    
    # Get user info to get user_id if not in login
    if not user_id:
        me = requests.get(f"{BASE_URL}/auth/me", headers=headers).json()
        user_id = me["id"]

    # 3. Try to access admin (should fail)
    resp = requests.get(f"{BASE_URL}/admin/users", headers=headers)
    if resp.status_code == 403:
        print("PASS: Regular user blocked from admin.")
    else:
        print(f"FAIL: Regular user not blocked from admin (Status: {resp.status_code})")
        
    # 4. Login as Admin
    admin_creds = {"email": "aimos-dev@example.com", "password": "devpass123"}
    resp = requests.post(f"{BASE_URL}/auth/login", json=admin_creds)
    if resp.status_code != 200:
        print(f"Failed to login as admin: {resp.status_code} {resp.text}")
        sys.exit(1)
    admin_token = resp.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    print("Logged in as admin.")

    # 5. List users
    resp = requests.get(f"{BASE_URL}/admin/users", headers=admin_headers)
    users = resp.json()
    print(f"Admin found {len(users)} users.")

    # 6. Set user quota to 0
    update_data = {"monthly_campaign_quota": 0}
    resp = requests.patch(f"{BASE_URL}/admin/users/{user_id}", json=update_data, headers=admin_headers)
    if resp.status_code == 200:
        print(f"Successfully set quota to 0 for user {user_id}")
    else:
        print(f"Failed to set quota: {resp.status_code} {resp.text}")
        sys.exit(1)

    # 7. Try to create campaign as user (should fail with 429)
    campaign_data = {"name": "Test Campaign", "input": {"goal": "test"}}
    resp = requests.post(f"{BASE_URL}/campaign/create", json=campaign_data, headers=headers)
    if resp.status_code == 429:
        print("PASS: Campaign creation blocked by 0 quota.")
    else:
        print(f"FAIL: Campaign creation not blocked (Status: {resp.status_code})")
        print(resp.text)

    # 8. Reset quota to 5
    update_data = {"monthly_campaign_quota": 5}
    requests.patch(f"{BASE_URL}/admin/users/{user_id}", json=update_data, headers=admin_headers)
    print("Quota reset to 5.")

    # 9. Try to create campaign again (should succeed)
    resp = requests.post(f"{BASE_URL}/campaign/create", json=campaign_data, headers=headers)
    if resp.status_code == 200:
        print("PASS: Campaign creation allowed after quota reset.")
    else:
        print(f"FAIL: Campaign creation still failed (Status: {resp.status_code})")
        print(resp.text)

if __name__ == "__main__":
    test_admin_flow()

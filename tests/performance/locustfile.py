import time
from locust import HttpUser, task, between, events
import random
import uuid

# Configuration
TEST_CAMPAIGN_NAME = "Locust Performance Test"
TEST_VERTICAL = "SaaS"

class AimosUser(HttpUser):
    """
    Simulates a high-traffic AIMOS agency client using 
    the campaign creation and monitoring flow.
    """
    wait_time = between(1, 5)
    token = ""

    def on_start(self):
        """
        Setup: Login or use a bypass token for the test.
        (Note: For extreme performance testing, use a mock bypass 
        to test endpoint logic vs just the auth middleware).
        """
        # For simplicity, we assume auth_disabled=1 for local tests.
        # If it's 0, we'd do a login here.
        pass

    @task(3)
    def create_campaign(self):
        """
        Main stressor: Create new campaign rows.
        (Requires the worker to be running to successfully process).
        """
        payload = {
            "name": f"{TEST_CAMPAIGN_NAME} - {uuid.uuid4().hex[:6]}",
            "input": {
                "industry_vertical": random.choice(["SaaS", "Real Estate", "Dental"]),
                "goals": "Scale conversion to 5% with AI optimization."
            }
        }
        
        with self.client.post("/campaign/create", json=payload, catch_response=True) as response:
            if response.status_code == 200:
                # Track the task_id to poll later if needed
                task_id = response.json().get("task_id")
                # print(f"Created task: {task_id}")
            else:
                response.failure(f"Failed to create campaign: {response.text}")

    @task(5)
    def view_global_analytics(self):
        """
        Secondary stressor: Global analytics aggregation query.
        """
        self.client.get("/analytics/global")

    @task(2)
    def view_usage(self):
        """
        Usage metrics query.
        """
        self.client.get("/analytics/usage")

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    print("--- Starting AIMOS Performance Stress Test ---")

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    print("--- Performance Test Completed ---")

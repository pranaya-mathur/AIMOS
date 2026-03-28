import pytest
from fastapi.testclient import TestClient
import os
import sys

# Ensure backend and core are in path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../backend"))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from main import app
from core.config import get_settings

client = TestClient(app)

def test_health_check_public():
    """Health check must always be public."""
    response = client.get("/health/ready")
    assert response.status_code == 200

@pytest.mark.parametrize("protected_url", [
    "/campaign/create",
    "/analytics/global",
    "/admin/users",
    "/billing/checkout/session"
])
def test_auth_enforcement_disabled(protected_url):
    """
    When AUTH_DISABLED=1 (default for dev), protected endpoints should succeed
    or at least not fail with 401. 
    (Note: Some endpoints like /campaign/create will still need valid session/db mock).
    """
    settings = get_settings()
    if not settings.auth_disabled_flag:
        pytest.skip("AUTH_DISABLED is not enabled")
        
    response = client.get(protected_url)
    assert response.status_code != 401

def test_auth_enforcement_enabled():
    """
    Verify that if we simulate AUTH_DISABLED=0, the system enforces JWT.
    """
    # We mock the settings object to simulate production enforcement
    with pytest.MonkeyPatch().context() as m:
        m.setattr("deps.get_settings", lambda: type('Settings', (), {'auth_disabled_flag': False})())
        
        # Test a randomized protected route
        response = client.get("/campaign/67746ae7-e935-4016-b628-92878c068720")
        
        # Should be 401 because no Bearer token was provided
        assert response.status_code == 401
        assert "Authentication required" in response.json()["detail"]

def test_rbac_agency_client_cannot_access_admin():
    """
    Integration test: Agency Client should not be able to list all users.
    (Requires real token generation or mock dependency injection).
    """
    # This is a placeholder for a more complex mock dependency test
    # In a real environment, we'd use 'app.dependency_overrides'
    pass

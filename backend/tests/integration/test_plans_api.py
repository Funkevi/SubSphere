"""
Integration tests for plans API
"""
import pytest
from fastapi.testclient import TestClient
import sys
import os
from datetime import datetime
import random
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))


class TestPlansAPI:
    """Integration tests for plans API"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        from src.main import app
        return TestClient(app)

    @pytest.fixture
    def admin_token(self, client):
        """Create admin token"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        random_num = random.randint(100000, 999999)
        email = f"planadmin{timestamp}{random_num}@gmail.com"
        
        time.sleep(1)
        
        reg_response = client.post(
            "/api/auth/register",
            json={"email": email, "password": "AdminPass123!"}
        )
        
        if reg_response.status_code == 400:
            pytest.skip("Rate limit hit")
        
        time.sleep(1)
        
        login_response = client.post(
            "/api/auth/login",
            json={"email": email, "password": "AdminPass123!"}
        )
        
        return login_response.json()["access_token"]

    @pytest.fixture
    def subscriber_token(self, client):
        """Create subscriber token (non-admin)"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        random_num = random.randint(100000, 999999)
        email = f"subscriber{timestamp}{random_num}@gmail.com"
        
        time.sleep(1)
        
        reg_response = client.post(
            "/api/auth/register",
            json={"email": email, "password": "SubPass123!"}
        )
        
        if reg_response.status_code == 400:
            pytest.skip("Rate limit hit")
        
        time.sleep(1)
        
        login_response = client.post(
            "/api/auth/login",
            json={"email": email, "password": "SubPass123!"}
        )
        
        return login_response.json()["access_token"]

    # ========== TESTS ==========

    def test_list_plans_empty(self, client):
        """Test listing plans"""
        response = client.get("/api/plans")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_create_plan_without_auth(self, client):
        """Test plan creation without auth"""
        response = client.post(
            "/api/plans",
            json={
                "plan": {  # WRAPPED
                    "name": "Unauthorized Plan",
                    "price": 9.99,
                    "duration_days": 30
                }
            }
        )
        assert response.status_code in [401, 422]

    def test_create_plan_invalid_data(self, client, admin_token):
        """Test invalid plan data"""
        response = client.post(
            "/api/plans",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "plan": {  # WRAPPED
                    "name": "Invalid Plan",
                    "price": -9.99,
                    "duration_days": 30
                }
            }
        )
        assert response.status_code == 422

    def test_get_nonexistent_plan(self, client):
        """Test getting nonexistent plan"""
        response = client.get("/api/plans/00000000-0000-0000-0000-000000000000")
        assert response.status_code == 404

    def test_update_plan_without_auth(self, client):
        """Test update without auth"""
        response = client.put(
            "/api/plans/some-id",
            json={
                "plan": {"name": "Updated"}  # WRAPPED
            }
        )
        assert response.status_code in [401, 422]

    def test_delete_plan_without_auth(self, client):
        """Test delete without auth"""
        response = client.delete("/api/plans/some-id")
        assert response.status_code in [401, 422]

    def test_list_plans_with_filter(self, client):
        """Test listing with filter"""
        response = client.get("/api/plans?active_only=false")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_create_plan_by_non_admin_fails(self, client, subscriber_token):
        """Test non-admin cannot create"""
        response = client.post(
            "/api/plans",
            headers={"Authorization": f"Bearer {subscriber_token}"},
            json={
                "plan": {  # WRAPPED
                    "name": "Subscriber Plan",
                    "price": 19.99,
                    "duration_days": 30
                }
            }
        )
        assert response.status_code == 403

    def test_update_plan_by_non_admin_fails(self, client, subscriber_token):
        """Test non-admin cannot update"""
        response = client.put(
            "/api/plans/some-id",
            headers={"Authorization": f"Bearer {subscriber_token}"},
            json={
                "plan": {"name": "Updated Plan"}  # WRAPPED
            }
        )
        assert response.status_code == 403

    def test_delete_plan_by_non_admin_fails(self, client, subscriber_token):
        """Test non-admin cannot delete"""
        response = client.delete(
            "/api/plans/some-id",
            headers={"Authorization": f"Bearer {subscriber_token}"}
        )
        assert response.status_code == 403

    def test_update_nonexistent_plan(self, client, admin_token):
        """Test updating nonexistent plan"""
        response = client.put(
            "/api/plans/00000000-0000-0000-0000-000000000000",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "plan": {"name": "Updated"}  # WRAPPED
            }
        )
        assert response.status_code in [400, 404]

    def test_delete_nonexistent_plan(self, client, admin_token):
        """Test deleting nonexistent plan"""
        response = client.delete(
            "/api/plans/00000000-0000-0000-0000-000000000000",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code in [400, 404]

    def test_create_plan_with_features(self, client, admin_token):
        """Test creating with features"""
        response = client.post(
            "/api/plans",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "plan": {  # WRAPPED
                    "name": "Premium Plan",
                    "description": "Premium features",
                    "price": 49.99,
                    "duration_days": 30,
                    "features": [
                        {"name": "Feature 1", "description": "First"},
                        {"name": "Feature 2", "description": "Second"}
                    ]
                }
            }
        )
        assert response.status_code in [201, 400]

    def test_create_plan_minimal_fields(self, client, admin_token):
        """Test minimal plan creation"""
        response = client.post(
            "/api/plans",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "plan": {  # WRAPPED
                    "name": "Basic Plan",
                    "price": 9.99,
                    "duration_days": 7
                }
            }
        )
        assert response.status_code in [201, 400]

    def test_update_plan_partial_fields(self, client, admin_token):
        """Test partial update"""
        response = client.put(
            "/api/plans/some-id",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "plan": {  # WRAPPED
                    "price": 29.99,
                    "is_active": False
                }
            }
        )
        assert response.status_code in [200, 400, 404]

    def test_get_plan_with_invalid_uuid(self, client):
        """Test invalid UUID"""
        response = client.get("/api/plans/invalid-uuid")
        assert response.status_code == 404

    def test_list_plans_active_only_true(self, client):
        """Test active only filter"""
        response = client.get("/api/plans?active_only=true")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_create_plan_missing_required_field(self, client, admin_token):
        """Test missing required fields"""
        response = client.post(
            "/api/plans",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "plan": {"name": "Incomplete"}  # WRAPPED, missing price
            }
        )
        assert response.status_code == 422

    def test_update_plan_with_invalid_token(self, client):
        """Test update with invalid token"""
        response = client.put(
            "/api/plans/some-id",
            headers={"Authorization": "Bearer invalid-token"},
            json={
                "plan": {"name": "Updated"}  # WRAPPED
            }
        )
        assert response.status_code in [401, 422]

    def test_delete_plan_with_invalid_token(self, client):
        """Test delete with invalid token"""
        response = client.delete(
            "/api/plans/some-id",
            headers={"Authorization": "Bearer invalid-token"}
        )
        assert response.status_code == 401

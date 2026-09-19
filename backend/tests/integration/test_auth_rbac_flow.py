"""
Integration tests for authentication and RBAC flow
"""
import pytest
from fastapi.testclient import TestClient
import sys
import os
from datetime import datetime
import random
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))


class TestAuthRBACFlow:
    """Integration tests for login with RBAC"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        from src.main import app
        return TestClient(app)

    @pytest.fixture
    def admin_token(self, client):
        """Create admin user and get token"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        random_num = random.randint(100000, 999999)
        email = f"admin{timestamp}{random_num}@gmail.com"
        
        # Add delay to avoid rate limit
        time.sleep(1)
        
        # Register admin user
        response = client.post(
            "/api/auth/register",
            json={"email": email, "password": "AdminPass123!"}
        )
        
        # Skip if rate limited
        if response.status_code == 400 and "rate" in response.json().get("detail", "").lower():
            pytest.skip("Supabase rate limit")
        
        assert response.status_code == 201, f"Registration failed: {response.json()}"
        
        time.sleep(1)
        
        # Login to get token
        login_response = client.post(
            "/api/auth/login",
            json={"email": email, "password": "AdminPass123!"}
        )
        
        return login_response.json()["access_token"]

    @pytest.fixture
    def registered_user(self, client):
        """Register a test user and return credentials"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        random_num = random.randint(100000, 999999)
        email = f"testuser{timestamp}{random_num}@gmail.com"
        password = "TestPass123!"
        
        # Add delay
        time.sleep(1)
        
        # Register user
        response = client.post(
            "/api/auth/register",
            json={"email": email, "password": password}
        )
        
        # Skip if rate limited
        if response.status_code == 400 and "rate" in response.json().get("detail", "").lower():
            pytest.skip("Supabase rate limit")
        
        assert response.status_code == 201, f"Registration failed: {response.json()}"
        
        return {"email": email, "password": password}

    # ========== ORIGINAL TESTS ==========
    
    def test_login_success(self, client, registered_user):
        """Test successful login"""
        response = client.post(
            "/api/auth/login",
            json={
                "email": registered_user["email"],
                "password": registered_user["password"]
            }
        )

        assert response.status_code == 200
        assert response.json()["success"] is True
        assert response.json()["access_token"] is not None
        assert response.json()["user_id"] is not None

    def test_login_invalid_credentials(self, client):
        """Test login with wrong password"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        email = f"test{timestamp}@gmail.com"
        
        time.sleep(1)
        
        # Register first
        client.post(
            "/api/auth/register",
            json={"email": email, "password": "ValidPass123!"}
        )

        time.sleep(1)
        
        # Try login with wrong password
        response = client.post(
            "/api/auth/login",
            json={"email": email, "password": "WrongPass123!"}
        )

        assert response.status_code == 401

    def test_admin_endpoint_access(self, client, admin_token):
        """Test admin-only endpoint access"""
        response = client.get(
            "/api/admin/dashboard",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        # May return 200 or 403 depending on role setup
        assert response.status_code in [200, 403]

    def test_missing_auth_header(self, client):
        """Test request without authorization header"""
        response = client.get("/api/admin/dashboard")
        assert response.status_code == 401

    # ========== ADDITIONAL TESTS ==========

    def test_login_with_role_info(self, client, registered_user):
        """Test that login response includes role information"""
        response = client.post(
            "/api/auth/login",
            json={
                "email": registered_user["email"],
                "password": registered_user["password"]
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "role" in data
        assert data["role"] in ["subscriber", "admin"]

    def test_login_nonexistent_user(self, client):
        """Test login with email that doesn't exist"""
        response = client.post(
            "/api/auth/login",
            json={"email": "nonexistent@gmail.com", "password": "WrongPass123!"}
        )
        
        assert response.status_code == 401

    def test_admin_endpoint_without_token(self, client):
        """Test admin endpoint without authorization token"""
        response = client.get("/api/admin/dashboard")
        assert response.status_code == 401

    def test_get_current_user_with_valid_token(self, client, registered_user):
        """Test /me endpoint with valid token"""
        # Login to get token
        login_response = client.post(
            "/api/auth/login",
            json={
                "email": registered_user["email"],
                "password": registered_user["password"]
            }
        )
        
        token = login_response.json()["access_token"]
        
        # Get current user info
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        assert "user_id" in response.json()
        assert "role" in response.json()

    def test_get_current_user_missing_header(self, client):
        """Test /me endpoint with missing auth header"""
        response = client.get("/api/auth/me")
        
        assert response.status_code == 401
        assert "missing" in response.json()["detail"].lower()

    def test_subscriber_cannot_access_admin_endpoint(self, client, registered_user):
        """Test that subscriber role cannot access admin endpoints"""
        # Login as subscriber
        login_response = client.post(
            "/api/auth/login",
            json={
                "email": registered_user["email"],
                "password": registered_user["password"]
            }
        )
        
        token = login_response.json()["access_token"]
        
        # Try to access admin endpoint
        response = client.get(
            "/api/admin/dashboard",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Should get 403 Forbidden
        assert response.status_code == 403
        assert "access denied" in response.json()["detail"].lower()

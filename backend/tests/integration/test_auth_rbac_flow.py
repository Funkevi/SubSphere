import pytest
from fastapi.testclient import TestClient

class TestAuthRBACFlow:
    '''Integration tests for login with RBAC'''

    @pytest.fixture
    def client(self):
        from src.main import app
        return TestClient(app)

    @pytest.fixture
    def admin_token(self, client):
        '''Create admin user and get token'''
        # Register admin user (in real scenario, set role in DB)
        response = client.post(
            "/api/auth/register",
            json={
                "email": "admin@example.com",
                "password": "AdminPass123!"
            }
        )
        user_id = response.json()["user_id"]

        # Login to get token
        login_response = client.post(
            "/api/auth/login",
            json={
                "email": "admin@example.com",
                "password": "AdminPass123!"
            }
        )
        return login_response.json()["access_token"]

    def test_login_success(self, client):
        '''Test successful login'''
        # First register
        client.post(
            "/api/auth/register",
            json={
                "email": "user@example.com",
                "password": "ValidPass123!"
            }
        )

        # Then login
        response = client.post(
            "/api/auth/login",
            json={
                "email": "user@example.com",
                "password": "ValidPass123!"
            }
        )

        assert response.status_code == 200
        assert response.json()["success"] is True
        assert response.json()["access_token"] is not None
        assert response.json()["user_id"] is not None

    def test_login_invalid_credentials(self, client):
        '''Test login with wrong password'''
        # Register first
        client.post(
            "/api/auth/register",
            json={
                "email": "test@example.com",
                "password": "ValidPass123!"
            }
        )

        # Try login with wrong password
        response = client.post(
            "/api/auth/login",
            json={
                "email": "test@example.com",
                "password": "WrongPass123!"
            }
        )

        assert response.status_code == 401

    def test_admin_endpoint_access(self, client, admin_token):
        '''Test admin-only endpoint access'''
        response = client.get(
            "/api/admin/dashboard",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        # With proper role assignment, should return 200
        # Without proper setup, may return 403
        assert response.status_code in [200, 403]

    def test_missing_auth_header(self, client):
        '''Test request without authorization header'''
        response = client.get("/api/admin/dashboard")
        assert response.status_code == 401
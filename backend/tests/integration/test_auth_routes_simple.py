"""
Additional integration tests for auth routes (non-mocked simple tests)
"""
import pytest
from fastapi.testclient import TestClient
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))


class TestAuthRoutesSimple:
    """Simple tests for auth routes without complex mocking"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        from src.main import app
        return TestClient(app)

    # ===== VALIDATION TESTS (don't hit database) =====

    def test_register_invalid_email_various_formats(self, client):
        """Test various invalid email formats"""
        invalid_emails = [
            "notanemail",
            "@example.com",
            "user@",
            "user name@example.com",
            "user@@example.com",
            "",
            "user@.com",
            ".user@example.com",
        ]
        
        for email in invalid_emails:
            response = client.post(
                "/api/auth/register",
                json={"email": email, "password": "ValidPass123!"}
            )
            assert response.status_code in [400, 422], f"Failed for email: {email}"

    def test_register_invalid_password_various_cases(self, client):
        """Test various invalid passwords"""
        invalid_passwords = [
            "short",  # Too short
            "nouppercase123!",  # No uppercase
            "NOLOWERCASE123!",  # No lowercase
            "NoDigitPassword!",  # No digit
            "NoSpecial123",  # No special char
            "",  # Empty
        ]
        
        for password in invalid_passwords:
            response = client.post(
                "/api/auth/register",
                json={"email": "test@example.com", "password": password}
            )
            assert response.status_code in [400, 422], f"Failed for password: {password}"

    def test_login_invalid_email_format(self, client):
        """Test login with invalid email"""
        response = client.post(
            "/api/auth/login",
            json={"email": "bademail", "password": "Pass123!"}
        )
        assert response.status_code == 400

    def test_login_empty_email(self, client):
        """Test login with empty email"""
        response = client.post(
            "/api/auth/login",
            json={"email": "", "password": "Pass123!"}
        )
        assert response.status_code == 400

    def test_me_missing_auth_header(self, client):
        """Test /me without auth header"""
        response = client.get("/api/auth/me")
        assert response.status_code == 401

    def test_me_invalid_auth_format(self, client):
        """Test /me with invalid auth format"""
        invalid_headers = [
            "InvalidFormat",
            "Bearer",
            "Bearer ",
            "",
        ]
        
        for header in invalid_headers:
            response = client.get(
                "/api/auth/me",
                headers={"Authorization": header} if header else {}
            )
            assert response.status_code == 401

    def test_me_with_invalid_token(self, client):
        """Test /me with invalid JWT"""
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer invalid.token.here"}
        )
        assert response.status_code == 401

    def test_me_with_valid_token(self, client):
        """Test /me with valid JWT"""
        from src.auth.jwt_handler import JWTHandler
        
        token = JWTHandler.generate_token("test-user", "subscriber")
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == "test-user"
        assert data["role"] == "subscriber"

    def test_me_with_admin_token(self, client):
        """Test /me with admin JWT"""
        from src.auth.jwt_handler import JWTHandler
        
        token = JWTHandler.generate_token("admin-user", "admin")
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "admin"

    def test_me_with_expired_token(self, client):
        """Test /me with expired token"""
        import jwt
        from datetime import datetime, timedelta, timezone
        from src.config import settings
        
        expired_payload = {
            "user_id": "test-user",
            "role": "subscriber",
            "exp": datetime.now(timezone.utc) - timedelta(hours=1)
        }
        expired_token = jwt.encode(expired_payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
        
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {expired_token}"}
        )
        assert response.status_code == 401

    # ===== MISSING FIELD TESTS =====

    def test_register_missing_email_field(self, client):
        """Test registration without email"""
        response = client.post(
            "/api/auth/register",
            json={"password": "ValidPass123!"}
        )
        assert response.status_code == 422

    def test_register_missing_password_field(self, client):
        """Test registration without password"""
        response = client.post(
            "/api/auth/register",
            json={"email": "test@example.com"}
        )
        assert response.status_code == 422

    def test_login_missing_email_field(self, client):
        """Test login without email"""
        response = client.post(
            "/api/auth/login",
            json={"password": "ValidPass123!"}
        )
        assert response.status_code == 422

    def test_login_missing_password_field(self, client):
        """Test login without password"""
        response = client.post(
            "/api/auth/login",
            json={"email": "test@example.com"}
        )
        assert response.status_code == 422

    def test_register_empty_request_body(self, client):
        """Test registration with empty body"""
        response = client.post("/api/auth/register", json={})
        assert response.status_code == 422

    def test_login_empty_request_body(self, client):
        """Test login with empty body"""
        response = client.post("/api/auth/login", json={})
        assert response.status_code == 422

    # ===== ADDITIONAL VALIDATION EDGE CASES =====

    def test_register_null_email(self, client):
        """Test registration with null email"""
        response = client.post(
            "/api/auth/register",
            json={"email": None, "password": "ValidPass123!"}
        )
        assert response.status_code == 422

    def test_register_null_password(self, client):
        """Test registration with null password"""
        response = client.post(
            "/api/auth/register",
            json={"email": "test@example.com", "password": None}
        )
        assert response.status_code == 422

    def test_me_with_finance_token(self, client):
        """Test /me with finance role"""
        from src.auth.jwt_handler import JWTHandler
        
        token = JWTHandler.generate_token("finance-user", "finance")
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "finance"

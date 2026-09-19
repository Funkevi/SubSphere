"""
Extended integration tests for auth routes
"""
import pytest
from fastapi.testclient import TestClient
import sys
import os
from datetime import datetime
import random

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))


class TestAuthRoutesExtended:
    """Extended tests for auth routes coverage"""

    @pytest.fixture
    def client(self):
        from src.main import app
        return TestClient(app)

    def test_register_with_invalid_email_format(self, client):
        """Test registration with various invalid email formats"""
        invalid_emails = [
            "notanemail",
            "@example.com",
            "user@",
            "user @example.com",
            "user..name@example.com"
        ]
        
        for email in invalid_emails:
            response = client.post(
                "/api/auth/register",
                json={"email": email, "password": "ValidPass123!"}
            )
            assert response.status_code == 400

    def test_register_with_weak_passwords(self, client):
        """Test registration with various weak passwords"""
        weak_passwords = [
            "short",
            "nouppercase1!",
            "NOLOWERCASE1!",
            "NoDigits!",
            "NoSpecial123"
        ]
        
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        
        for password in weak_passwords:
            response = client.post(
                "/api/auth/register",
                json={
                    "email": f"user{random.randint(1000,9999)}@gmail.com",
                    "password": password
                }
            )
            assert response.status_code == 400

    def test_login_with_empty_credentials(self, client):
        """Test login with empty email/password"""
        response = client.post(
            "/api/auth/login",
            json={"email": "", "password": ""}
        )
        assert response.status_code == 400

    def test_login_with_invalid_email_format(self, client):
        """Test login with invalid email format"""
        response = client.post(
            "/api/auth/login",
            json={"email": "not-an-email", "password": "ValidPass123!"}
        )
        assert response.status_code == 400

    def test_me_endpoint_with_malformed_token(self, client):
        """Test /me endpoint with malformed authorization header"""
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": "NotBearerToken"}
        )
        assert response.status_code == 401

    def test_me_endpoint_with_invalid_token(self, client):
        """Test /me endpoint with invalid token"""
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer invalid-token"}
        )
        assert response.status_code == 401

    def test_register_missing_email(self, client):
        """Test registration without email field"""
        response = client.post(
            "/api/auth/register",
            json={"password": "ValidPass123!"}
        )
        assert response.status_code == 422  # Validation error

    def test_register_missing_password(self, client):
        """Test registration without password field"""
        response = client.post(
            "/api/auth/register",
            json={"email": "test@gmail.com"}
        )
        assert response.status_code == 422  # Validation error

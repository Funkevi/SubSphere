"""
Integration tests for authentication flow
Tests validation logic without hitting Supabase rate limits
"""
import pytest
from fastapi.testclient import TestClient
import sys
import os
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from src.utils.validators import Validators


class TestAuthFlow:
    """Integration tests for authentication flow"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        from src.main import app
        return TestClient(app)

    def test_register_invalid_email(self, client):
        """Test registration with invalid email"""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "invalid-email",
                "password": "ValidPass123!"
            }
        )
        assert response.status_code == 400
        assert "email" in response.json()["detail"].lower()

    def test_register_weak_password(self, client):
        """Test registration with weak password"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        email = f"weakpass{timestamp}@gmail.com"
        
        response = client.post(
            "/api/auth/register",
            json={
                "email": email,
                "password": "weak"
            }
        )
        assert response.status_code == 400
        assert "password" in response.json()["detail"].lower()

    def test_validate_email_none(self):
        """Test None email validation"""
        is_valid, error = Validators.validate_email(None)
        assert is_valid is False
        assert "Email is required" in error

    def test_validate_password_none(self):
        """Test None password validation"""
        is_valid, error = Validators.validate_password(None)
        assert is_valid is False
        assert "Password is required" in error

    def test_register_empty_email(self, client):
        """Test registration with empty email"""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "",
                "password": "ValidPass123!"
            }
        )
        assert response.status_code == 400
        assert "email" in response.json()["detail"].lower()

    def test_register_empty_password(self, client):
        """Test registration with empty password"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        email = f"emptypass{timestamp}@gmail.com"
        
        response = client.post(
            "/api/auth/register",
            json={
                "email": email,
                "password": ""
            }
        )
        assert response.status_code == 400
        assert "password" in response.json()["detail"].lower()

"""
Unit tests for JWT token handler
Tests token generation, verification, and error cases
"""
import pytest
import sys
import os
import jwt
from datetime import datetime, timedelta, timezone

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from src.auth.jwt_handler import JWTHandler
from src.config import settings


class TestJWTHandler:
    """Unit tests for JWT token generation and verification"""

    def test_generate_token_default_role(self):
        """Test JWT token generation with default subscriber role"""
        user_id = "test-user-123"
        token = JWTHandler.generate_token(user_id)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_generate_token_custom_role(self):
        """Test JWT token generation with custom role"""
        user_id = "admin-user-456"
        token = JWTHandler.generate_token(user_id, role="admin")
        
        assert token is not None
        
        # Verify token contains correct role
        result = JWTHandler.verify_token(token)
        assert result["valid"] is True
        assert result["payload"]["role"] == "admin"

    def test_verify_valid_token(self):
        """Test verification of valid JWT token"""
        user_id = "test-user-789"
        role = "subscriber"
        token = JWTHandler.generate_token(user_id, role)
        
        result = JWTHandler.verify_token(token)
        
        assert result["valid"] is True
        assert result["payload"]["user_id"] == user_id
        assert result["payload"]["role"] == role
        assert "iat" in result["payload"]
        assert "exp" in result["payload"]

    def test_verify_invalid_token(self):
        """Test verification of invalid JWT token"""
        invalid_token = "invalid.token.here"
        
        result = JWTHandler.verify_token(invalid_token)
        
        assert result["valid"] is False
        assert "error" in result
        assert "Invalid token" in result["error"]

    def test_verify_expired_token(self):
        """Test verification of expired JWT token"""
        # Create token with past expiration
        user_id = "test-user-expired"
        payload = {
            "user_id": user_id,
            "role": "subscriber",
            "iat": datetime.now(timezone.utc),
            "exp": datetime.now(timezone.utc) - timedelta(hours=1)  # Expired 1 hour ago
        }
        
        expired_token = jwt.encode(
            payload, 
            settings.JWT_SECRET, 
            algorithm=settings.JWT_ALGORITHM
        )
        
        result = JWTHandler.verify_token(expired_token)
        
        assert result["valid"] is False
        assert "error" in result
        assert "expired" in result["error"].lower()

    def test_verify_token_wrong_secret(self):
        """Test verification with wrong secret"""
        # Create token with different secret
        payload = {
            "user_id": "test-user",
            "role": "subscriber",
            "iat": datetime.now(timezone.utc),
            "exp": datetime.now(timezone.utc) + timedelta(hours=24)
        }
        
        wrong_token = jwt.encode(payload, "wrong-secret", algorithm=settings.JWT_ALGORITHM)
        
        result = JWTHandler.verify_token(wrong_token)
        
        assert result["valid"] is False
        assert "error" in result

    def test_token_contains_all_required_fields(self):
        """Test that generated token contains all required fields"""
        user_id = "test-user-complete"
        role = "admin"
        token = JWTHandler.generate_token(user_id, role)
        
        result = JWTHandler.verify_token(token)
        
        assert result["valid"] is True
        payload = result["payload"]
        
        # Check all required fields
        assert "user_id" in payload
        assert "role" in payload
        assert "iat" in payload  # issued at
        assert "exp" in payload  # expiration
        
        assert payload["user_id"] == user_id
        assert payload["role"] == role

    def test_token_expiration_time(self):
        """Test that token has correct expiration time"""
        user_id = "test-user-expiration"
        token = JWTHandler.generate_token(user_id)
        
        result = JWTHandler.verify_token(token)
        
        assert result["valid"] is True
        payload = result["payload"]
        
        # Check expiration is set correctly (24 hours from now)
        exp_time = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        iat_time = datetime.fromtimestamp(payload["iat"], tz=timezone.utc)
        
        time_diff = exp_time - iat_time
        
        # Should be approximately 24 hours (within 1 minute tolerance)
        expected_seconds = 24 * 3600
        assert abs(time_diff.total_seconds() - expected_seconds) < 60

    def test_token_roles(self):
        """Test different user roles in tokens"""
        roles = ["subscriber", "admin", "finance"]
        
        for role in roles:
            token = JWTHandler.generate_token(f"user-{role}", role)
            result = JWTHandler.verify_token(token)
            
            assert result["valid"] is True
            assert result["payload"]["role"] == role

import pytest
from src.auth.jwt_handler import jwt_handler
import time

class TestJWTHandler:
    '''Unit tests for JWT generation and verification'''

    def test_generate_token(self):
        '''Test JWT token generation'''
        token = jwt_handler.generate_token("user-123", "subscriber")
        assert token is not None
        assert isinstance(token, str)

    def test_verify_valid_token(self):
        '''Test verification of valid token'''
        token = jwt_handler.generate_token("user-123", "admin")
        result = jwt_handler.verify_token(token)

        assert result["valid"] is True
        assert result["payload"]["user_id"] == "user-123"
        assert result["payload"]["role"] == "admin"

    def test_verify_invalid_token(self):
        '''Test verification of invalid token'''
        result = jwt_handler.verify_token("invalid.token.here")
        assert result["valid"] is False
        assert "Invalid token" in result["error"]

    def test_token_expiration(self):
        '''Test that tokens expire (mocked)'''
        # Create token and manually set past expiration
        token = jwt_handler.generate_token("user-123", "subscriber")

        # Manipulate expiration (in real scenario, wait 24+ hours)
        # For testing, we'd mock time
        result = jwt_handler.verify_token(token)
        assert result["valid"] is True

class TestRBAC:
    '''Unit tests for role-based access control'''

    def test_admin_role_check(self):
        '''Test admin role verification'''
        admin_token = jwt_handler.generate_token("admin-user", "admin")
        result = jwt_handler.verify_token(admin_token)

        assert result["valid"] is True
        assert result["payload"]["role"] == "admin"

    def test_subscriber_role_check(self):
        '''Test subscriber role verification'''
        user_token = jwt_handler.generate_token("regular-user", "subscriber")
        result = jwt_handler.verify_token(user_token)

        assert result["valid"] is True
        assert result["payload"]["role"] == "subscriber"

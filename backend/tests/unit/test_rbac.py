"""
Unit tests for RBAC (Role-Based Access Control) middleware
"""
import pytest
from unittest.mock import MagicMock, AsyncMock
from fastapi import HTTPException
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from src.auth.rbac import require_role


class TestRBAC:
    """Tests for RBAC decorator"""

    def test_require_role_missing_authorization(self):
        """Test missing authorization header"""
        @require_role(["admin"])
        async def protected_endpoint():
            return {"message": "success"}
        
        with pytest.raises(HTTPException) as exc_info:
            import asyncio
            asyncio.run(protected_endpoint(authorization=None))
        
        assert exc_info.value.status_code == 401
        assert "Missing authorization header" in exc_info.value.detail

    def test_require_role_invalid_header_format_no_bearer(self):
        """Test authorization header without Bearer prefix"""
        @require_role(["admin"])
        async def protected_endpoint():
            return {"message": "success"}
        
        with pytest.raises(HTTPException) as exc_info:
            import asyncio
            asyncio.run(protected_endpoint(authorization="InvalidFormat"))
        
        assert exc_info.value.status_code == 401
        assert "Invalid authorization header format" in exc_info.value.detail

    def test_require_role_invalid_header_format_empty(self):
        """Test authorization header with Bearer but no token"""
        @require_role(["admin"])
        async def protected_endpoint():
            return {"message": "success"}
        
        with pytest.raises(HTTPException) as exc_info:
            import asyncio
            asyncio.run(protected_endpoint(authorization="Bearer"))
        
        assert exc_info.value.status_code == 401

    def test_require_role_invalid_token(self):
        """Test with invalid JWT token"""
        @require_role(["admin"])
        async def protected_endpoint():
            return {"message": "success"}
        
        with pytest.raises(HTTPException) as exc_info:
            import asyncio
            asyncio.run(protected_endpoint(authorization="Bearer invalid.token.here"))
        
        assert exc_info.value.status_code == 401
        assert "Invalid or expired token" in exc_info.value.detail

    def test_require_role_expired_token(self):
        """Test with expired JWT token"""
        import jwt
        from datetime import datetime, timedelta, timezone
        from src.config import settings
        
        expired_payload = {
            "user_id": "test-user",
            "role": "admin",
            "exp": datetime.now(timezone.utc) - timedelta(hours=1)
        }
        expired_token = jwt.encode(expired_payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
        
        @require_role(["admin"])
        async def protected_endpoint():
            return {"message": "success"}
        
        with pytest.raises(HTTPException) as exc_info:
            import asyncio
            asyncio.run(protected_endpoint(authorization=f"Bearer {expired_token}"))
        
        assert exc_info.value.status_code == 401
        assert "expired" in exc_info.value.detail.lower()

    def test_require_role_valid_admin_token(self):
        """Test with valid admin token"""
        from src.auth.jwt_handler import JWTHandler
        
        token = JWTHandler.generate_token("admin-123", "admin")
        
        @require_role(["admin"])
        async def protected_endpoint(current_user=None, token=None):
            return {"message": "success", "user": current_user}
        
        import asyncio
        result = asyncio.run(protected_endpoint(authorization=f"Bearer {token}"))
        
        assert result["message"] == "success"
        assert result["user"]["role"] == "admin"

    def test_require_role_valid_subscriber_token(self):
        """Test with valid subscriber token"""
        from src.auth.jwt_handler import JWTHandler
        
        token = JWTHandler.generate_token("subscriber-123", "subscriber")
        
        @require_role(["subscriber", "admin"])
        async def protected_endpoint(current_user=None, token=None):
            return {"message": "success", "user": current_user}
        
        import asyncio
        result = asyncio.run(protected_endpoint(authorization=f"Bearer {token}"))
        
        assert result["message"] == "success"
        assert result["user"]["role"] == "subscriber"

    def test_require_role_forbidden_wrong_role(self):
        """Test with valid token but wrong role"""
        from src.auth.jwt_handler import JWTHandler
        
        token = JWTHandler.generate_token("subscriber-123", "subscriber")
        
        @require_role(["admin"])  # Requires admin
        async def protected_endpoint():
            return {"message": "success"}
        
        with pytest.raises(HTTPException) as exc_info:
            import asyncio
            asyncio.run(protected_endpoint(authorization=f"Bearer {token}"))
        
        assert exc_info.value.status_code == 403
        assert "Access denied" in exc_info.value.detail
        assert "admin" in exc_info.value.detail

    def test_require_role_multiple_allowed_roles_subscriber(self):
        """Test with multiple allowed roles - subscriber access"""
        from src.auth.jwt_handler import JWTHandler
        
        token = JWTHandler.generate_token("subscriber-123", "subscriber")
        
        @require_role(["subscriber", "admin", "finance"])
        async def protected_endpoint(current_user=None, token=None):
            return {"message": "success", "role": current_user["role"]}
        
        import asyncio
        result = asyncio.run(protected_endpoint(authorization=f"Bearer {token}"))
        
        assert result["role"] == "subscriber"

    def test_require_role_multiple_allowed_roles_admin(self):
        """Test with multiple allowed roles - admin access"""
        from src.auth.jwt_handler import JWTHandler
        
        token = JWTHandler.generate_token("admin-123", "admin")
        
        @require_role(["subscriber", "admin"])
        async def protected_endpoint(current_user=None, token=None):
            return {"message": "success", "role": current_user["role"]}
        
        import asyncio
        result = asyncio.run(protected_endpoint(authorization=f"Bearer {token}"))
        
        assert result["role"] == "admin"

    def test_require_role_finance_role(self):
        """Test with finance role"""
        from src.auth.jwt_handler import JWTHandler
        
        token = JWTHandler.generate_token("finance-123", "finance")
        
        @require_role(["finance", "admin"])
        async def protected_endpoint(current_user=None, token=None):
            return {"message": "success", "role": current_user["role"]}
        
        import asyncio
        result = asyncio.run(protected_endpoint(authorization=f"Bearer {token}"))
        
        assert result["role"] == "finance"

    def test_require_role_current_user_injected(self):
        """Test that current_user is properly injected into kwargs"""
        from src.auth.jwt_handler import JWTHandler
        
        token = JWTHandler.generate_token("user-456", "subscriber")
        
        @require_role(["subscriber"])
        async def protected_endpoint(current_user=None, token=None):
            return {
                "user_id": current_user["user_id"],
                "role": current_user["role"],
                "token_provided": token is not None
            }
        
        import asyncio
        result = asyncio.run(protected_endpoint(authorization=f"Bearer {token}"))
        
        assert result["user_id"] == "user-456"
        assert result["role"] == "subscriber"
        assert result["token_provided"] is True

    def test_require_role_preserves_function_args(self):
        """Test that decorator preserves function arguments"""
        from src.auth.jwt_handler import JWTHandler
        
        token = JWTHandler.generate_token("user-789", "admin")
        
        @require_role(["admin"])
        async def protected_endpoint(item_id: str, current_user=None, token=None):
            return {
                "item_id": item_id,
                "user_id": current_user["user_id"]
            }
        
        import asyncio
        result = asyncio.run(protected_endpoint("item-123", authorization=f"Bearer {token}"))
        
        assert result["item_id"] == "item-123"
        assert result["user_id"] == "user-789"

    def test_require_role_single_role_requirement(self):
        """Test with single role requirement"""
        from src.auth.jwt_handler import JWTHandler
        
        token = JWTHandler.generate_token("admin-999", "admin")
        
        @require_role(["admin"])
        async def admin_only_endpoint(current_user=None, token=None):
            return {"status": "admin access granted"}
        
        import asyncio
        result = asyncio.run(admin_only_endpoint(authorization=f"Bearer {token}"))
        
        assert result["status"] == "admin access granted"

    def test_require_role_token_without_role(self):
        """Test token without role field"""
        import jwt
        from datetime import datetime, timedelta, timezone
        from src.config import settings
        
        # Create token without role
        payload = {
            "user_id": "test-user",
            "exp": datetime.now(timezone.utc) + timedelta(hours=1)
        }
        token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
        
        @require_role(["admin"])
        async def protected_endpoint():
            return {"message": "success"}
        
        with pytest.raises(HTTPException) as exc_info:
            import asyncio
            asyncio.run(protected_endpoint(authorization=f"Bearer {token}"))
        
        assert exc_info.value.status_code == 403

    def test_require_role_case_sensitive(self):
        """Test that role checking is case-sensitive"""
        from src.auth.jwt_handler import JWTHandler
        
        # Token with lowercase role
        token = JWTHandler.generate_token("user-111", "admin")
        
        # Require uppercase (should work since we generate lowercase)
        @require_role(["ADMIN"])  # Different case
        async def protected_endpoint():
            return {"message": "success"}
        
        with pytest.raises(HTTPException) as exc_info:
            import asyncio
            asyncio.run(protected_endpoint(authorization=f"Bearer {token}"))
        
        # Should fail because case doesn't match
        assert exc_info.value.status_code == 403

    def test_require_role_empty_allowed_roles(self):
        """Test with empty allowed roles list"""
        from src.auth.jwt_handler import JWTHandler
        
        token = JWTHandler.generate_token("user-222", "admin")
        
        @require_role([])  # No roles allowed
        async def protected_endpoint():
            return {"message": "success"}
        
        with pytest.raises(HTTPException) as exc_info:
            import asyncio
            asyncio.run(protected_endpoint(authorization=f"Bearer {token}"))
        
        assert exc_info.value.status_code == 403

    def test_require_role_malformed_jwt(self):
        """Test with malformed JWT (not proper format)"""
        @require_role(["admin"])
        async def protected_endpoint():
            return {"message": "success"}
        
        with pytest.raises(HTTPException) as exc_info:
            import asyncio
            asyncio.run(protected_endpoint(authorization="Bearer notajwt"))
        
        assert exc_info.value.status_code == 401

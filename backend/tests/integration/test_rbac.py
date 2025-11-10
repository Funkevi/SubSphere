import pytest
import sys, os
from unittest.mock import Mock

# Add src path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from src.auth.rbac import require_role
from src.auth.jwt_handler import JWTHandler
from fastapi import HTTPException


class TestRBAC:
    """Unit tests for Role-Based Access Control"""

    @pytest.mark.asyncio
    async def test_require_role_admin_with_admin_token(self):
        """Test that admin role is granted access to admin-only function"""
        admin_token = JWTHandler.generate_token("admin-user-1", "admin")
        
        @require_role(["admin"])
        async def admin_function(token: str, **kwargs):  # Added **kwargs
            return {"message": "Admin access granted"}
        
        try:
            result = await admin_function(token=admin_token)
            assert result["message"] == "Admin access granted"
        except HTTPException:
            pytest.fail("Admin should have access")

    @pytest.mark.asyncio
    async def test_require_role_subscriber_denied_admin_access(self):
        """Test that subscriber role is denied access to admin-only function"""
        subscriber_token = JWTHandler.generate_token("subscriber-user-1", "subscriber")
        
        @require_role(["admin"])
        async def admin_function(token: str, **kwargs):  # Added **kwargs
            return {"message": "Admin access"}
        
        with pytest.raises(HTTPException) as exc_info:
            await admin_function(token=subscriber_token)
        
        assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_require_role_multiple_allowed_roles(self):
        """Test function accessible by multiple roles"""
        admin_token = JWTHandler.generate_token("admin-user", "admin")
        
        @require_role(["admin", "finance"])
        async def restricted_function(token: str, **kwargs):  # Added **kwargs
            return {"message": "Access granted"}
        
        # Test with admin
        try:
            result = await restricted_function(token=admin_token)
            assert result["message"] == "Access granted"
        except HTTPException:
            pytest.fail("Admin should have access")
        
        # Test with finance
        finance_token = JWTHandler.generate_token("finance-user", "finance")
        
        try:
            result = await restricted_function(token=finance_token)
            assert result["message"] == "Access granted"
        except HTTPException:
            pytest.fail("Finance should have access")

    @pytest.mark.asyncio
    async def test_require_role_invalid_token(self):
        """Test that invalid token is rejected"""
        invalid_token = "invalid.token"
        
        @require_role(["admin"])
        async def admin_function(token: str, **kwargs):  # Added **kwargs
            return {"message": "Admin access"}
        
        with pytest.raises(HTTPException) as exc_info:
            await admin_function(token=invalid_token)
        
        assert exc_info.value.status_code == 401

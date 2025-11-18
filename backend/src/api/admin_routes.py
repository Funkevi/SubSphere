"""
Admin-only API routes
Protected by RBAC middleware
"""
from typing import Optional
from fastapi import APIRouter, Header
from src.auth.rbac import require_role

router = APIRouter(prefix="/api/admin", tags=["Admin"])


@router.get("/dashboard")
@require_role(["admin"])
async def admin_dashboard(_authorization: Optional[str] = Header(None), _token: str = None, current_user: dict = None):
    """
    Admin dashboard endpoint

    - Only accessible by admin role
    - Returns admin-specific data
    """
    return {
        "message": "Welcome to admin dashboard",
        "user_id": current_user["user_id"] if current_user else None,
        "role": current_user["role"] if current_user else None
    }


@router.get("/users")
@require_role(["admin"])
async def list_users(_authorization: Optional[str] = Header(None), _token: str = None, current_user: dict = None):
    """
    List all users (admin only)
    """
    return {
        "message": "List of all users",
        "admin_user": current_user["user_id"] if current_user else None
    }


@router.get("/stats")
@require_role(["admin", "finance"])
async def get_stats(_authorization: Optional[str] = Header(None), _token: str = None, current_user: dict = None):
    """
    Get system statistics

    - Accessible by admin and finance roles
    """
    return {
        "message": "System statistics",
        "accessible_by": ["admin", "finance"],
        "current_role": current_user["role"] if current_user else None
    }

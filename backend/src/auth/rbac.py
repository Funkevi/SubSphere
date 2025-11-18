"""
Role-Based Access Control (RBAC) middleware
Restricts access to endpoints based on user roles
"""
from functools import wraps
from typing import Optional
from fastapi import HTTPException, Header
from src.auth.jwt_handler import JWTHandler


def require_role(allowed_roles: list):
    """
    Decorator to restrict endpoint access by role

    Args:
        allowed_roles: List of roles that can access the endpoint

    Returns:
        Decorated function that checks user role before execution
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, authorization: Optional[str] = Header(None), **kwargs):
            # Check if authorization header exists
            if not authorization:
                raise HTTPException(
                    status_code=401,
                    detail="Missing authorization header"
                )

            # Extract token from "Bearer <token>"
            try:
                token = authorization.split(" ")[1]
            except IndexError as exc:
                raise HTTPException(
                    status_code=401,
                    detail="Invalid authorization header format. Use: Bearer <token>"
                ) from exc

            # Verify token
            result = JWTHandler.verify_token(token)

            if not result["valid"]:
                raise HTTPException(
                    status_code=401,
                    detail=f"Invalid or expired token: {result.get('error', 'Unknown error')}"
                )

            # Check role
            user_role = result["payload"].get("role")

            if user_role not in allowed_roles:
                raise HTTPException(
                    status_code=403,
                    detail=f"Access denied. Required roles: {', '.join(allowed_roles)}"
                )

            # Add current_user to kwargs
            kwargs["current_user"] = result["payload"]
            kwargs["token"] = token

            # Call the original function
            return await func(*args, **kwargs)

        return wrapper
    return decorator

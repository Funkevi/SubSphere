from functools import wraps
from fastapi import HTTPException, Depends
from src.auth.jwt_handler import jwt_handler

def require_role(required_roles: list):
    '''Decorator to enforce role-based access control'''
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Extract token from request (implementation depends on framework)
            token = kwargs.get("token") or args[0]

            token_result = jwt_handler.verify_token(token)
            if not token_result["valid"]:
                raise HTTPException(status_code=401, detail="Unauthorized")

            user_role = token_result["payload"].get("role")
            if user_role not in required_roles:
                raise HTTPException(status_code=403, detail="Forbidden - insufficient permissions")

            kwargs["current_user"] = token_result["payload"]
            return await func(*args, **kwargs)
        return wrapper
    return decorator


"""
JWT Token Handler
Handles generation and verification of JWT tokens for authentication
"""
from datetime import datetime, timedelta, timezone
import jwt
from src.config import settings


class JWTHandler:
    """Handler for JWT token operations"""

    @staticmethod
    def generate_token(user_id: str, role: str = "subscriber") -> str:
        """
        Generate JWT token for authenticated user

        Args:
            user_id: Unique user identifier
            role: User role (default: subscriber)

        Returns:
            str: Encoded JWT token
        """
        payload = {
            "user_id": user_id,
            "role": role,
            "iat": datetime.now(timezone.utc),
            "exp": datetime.now(timezone.utc) + timedelta(hours=settings.JWT_EXPIRATION_HOURS)
        }
        token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
        return token

    @staticmethod
    def verify_token(token: str) -> dict:
        """
        Verify JWT token and return payload

        Args:
            token: JWT token string

        Returns:
            dict: {"valid": bool, "payload": dict} or {"valid": False, "error": str}
        """
        try:
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
            return {"valid": True, "payload": payload}
        except jwt.ExpiredSignatureError:
            return {"valid": False, "error": "Token expired"}
        except jwt.InvalidTokenError:
            return {"valid": False, "error": "Invalid token"}


# Create singleton instance
jwt_handler = JWTHandler()

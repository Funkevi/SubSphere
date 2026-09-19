import re
import uuid
from src.config import settings


def validate_uuid(uuid_string: str) -> bool:
    """
    Validate if a string is a valid UUID format
    
    Args:
        uuid_string: String to validate as UUID
        
    Returns:
        bool: True if valid UUID, False otherwise
    """
    try:
        uuid.UUID(str(uuid_string))
        return True
    except (ValueError, AttributeError, TypeError):
        return False


class Validators:
    @staticmethod
    def validate_email(email: str) -> tuple[bool, str]:
        '''Validate email format'''
        if email is None or not email:  # Handle None
            return False, "Email is required"
        if not re.match(settings.EMAIL_REGEX, email):
            return False, "Invalid email format"
        return True, ""

    @staticmethod
    def validate_password(password: str) -> tuple[bool, str]:
        '''Validate password strength'''
        if password is None or not password:  # Handle None
            return False, "Password is required"

        if len(password) < settings.PASSWORD_MIN_LENGTH:
            return False, f"Password must be at least {settings.PASSWORD_MIN_LENGTH} characters"

        if settings.PASSWORD_REQUIRE_UPPERCASE and not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"

        if settings.PASSWORD_REQUIRE_LOWERCASE and not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"

        if settings.PASSWORD_REQUIRE_DIGIT and not re.search(r'\d', password):
            return False, "Password must contain at least one digit"

        if settings.PASSWORD_REQUIRE_SPECIAL and not re.search(r'[@$!%*?&]', password):
            return False, "Password must contain at least one special character (@$!%*?&)"

        return True, ""

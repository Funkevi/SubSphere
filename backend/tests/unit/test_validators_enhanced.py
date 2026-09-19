"""
Enhanced unit tests for validators
Focus on testing all validation branches
"""
import pytest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from src.utils.validators import Validators


class TestValidatorsEnhanced:
    """Enhanced tests for validators"""

    # ===== EMAIL VALIDATION TESTS =====

    def test_validate_email_valid_simple(self):
        """Test valid simple email"""
        is_valid, error = Validators.validate_email("test@example.com")
        assert is_valid is True
        assert error == ""

    def test_validate_email_valid_subdomain(self):
        """Test valid email with subdomain"""
        is_valid, error = Validators.validate_email("user@mail.example.com")
        assert is_valid is True
        assert error == ""

    def test_validate_email_valid_plus(self):
        """Test valid email with plus sign"""
        is_valid, error = Validators.validate_email("user+tag@example.com")
        assert is_valid is True
        assert error == ""

    def test_validate_email_valid_dot(self):
        """Test valid email with dots"""
        is_valid, error = Validators.validate_email("first.last@example.com")
        assert is_valid is True
        assert error == ""

    def test_validate_email_valid_numbers(self):
        """Test valid email with numbers"""
        is_valid, error = Validators.validate_email("user123@example456.com")
        assert is_valid is True
        assert error == ""

    def test_validate_email_invalid_no_at(self):
        """Test invalid email without @"""
        is_valid, error = Validators.validate_email("notanemail.com")
        assert is_valid is False
        assert "Invalid email format" in error

    def test_validate_email_invalid_no_domain(self):
        """Test invalid email without domain"""
        is_valid, error = Validators.validate_email("user@")
        assert is_valid is False
        assert "Invalid email format" in error

    def test_validate_email_invalid_no_local(self):
        """Test invalid email without local part"""
        is_valid, error = Validators.validate_email("@example.com")
        assert is_valid is False
        assert "Invalid email format" in error

    def test_validate_email_invalid_spaces(self):
        """Test invalid email with spaces"""
        is_valid, error = Validators.validate_email("user name@example.com")
        assert is_valid is False
        assert "Invalid email format" in error

    def test_validate_email_invalid_double_at(self):
        """Test invalid email with double @"""
        is_valid, error = Validators.validate_email("user@@example.com")
        assert is_valid is False
        assert "Invalid email format" in error

    def test_validate_email_none(self):
        """Test email validation with None"""
        is_valid, error = Validators.validate_email(None)
        assert is_valid is False
        assert "Email is required" in error

    def test_validate_email_empty_string(self):
        """Test email validation with empty string"""
        is_valid, error = Validators.validate_email("")
        assert is_valid is False
        assert "Email is required" in error

    def test_validate_email_whitespace_only(self):
        """Test email validation with whitespace"""
        is_valid, error = Validators.validate_email("   ")
        assert is_valid is False
        # Whitespace is truthy but invalid format
        assert "Invalid email format" in error

    def test_validate_email_valid_hyphen(self):
        """Test valid email with hyphen"""
        is_valid, error = Validators.validate_email("user-name@example-domain.com")
        assert is_valid is True

    def test_validate_email_valid_underscore(self):
        """Test valid email with underscore"""
        is_valid, error = Validators.validate_email("user_name@example.com")
        assert is_valid is True

    # ===== PASSWORD VALIDATION TESTS =====

    def test_validate_password_valid_all_requirements(self):
        """Test valid password with all requirements"""
        is_valid, error = Validators.validate_password("ValidPass123!")
        assert is_valid is True
        assert error == ""

    def test_validate_password_valid_min_length(self):
        """Test valid password at minimum length"""
        is_valid, error = Validators.validate_password("Pass123!")
        assert is_valid is True

    def test_validate_password_invalid_too_short(self):
        """Test password too short"""
        is_valid, error = Validators.validate_password("Short1!")
        assert is_valid is False
        assert "at least" in error.lower()
        assert "characters" in error.lower()

    def test_validate_password_invalid_no_uppercase(self):
        """Test password without uppercase"""
        is_valid, error = Validators.validate_password("nouppercase123!")
        assert is_valid is False
        assert "uppercase" in error.lower()

    def test_validate_password_invalid_no_lowercase(self):
        """Test password without lowercase"""
        is_valid, error = Validators.validate_password("NOLOWERCASE123!")
        assert is_valid is False
        assert "lowercase" in error.lower()

    def test_validate_password_invalid_no_digit(self):
        """Test password without digit"""
        is_valid, error = Validators.validate_password("NoDigitPass!")
        assert is_valid is False
        assert "digit" in error.lower()

    def test_validate_password_invalid_no_special(self):
        """Test password without special character"""
        is_valid, error = Validators.validate_password("NoSpecial123")
        assert is_valid is False
        assert "special character" in error.lower()

    def test_validate_password_none(self):
        """Test password validation with None"""
        is_valid, error = Validators.validate_password(None)
        assert is_valid is False
        assert "Password is required" in error

    def test_validate_password_empty_string(self):
        """Test password validation with empty string"""
        is_valid, error = Validators.validate_password("")
        assert is_valid is False
        assert "Password is required" in error

    def test_validate_password_valid_all_special_chars(self):
        """Test password with all allowed special characters"""
        special_chars = "@$!%*?&"
        for char in special_chars:
            is_valid, error = Validators.validate_password(f"ValidPass123{char}")
            assert is_valid is True, f"Failed for special char: {char}"

    def test_validate_password_invalid_wrong_special_char(self):
        """Test password with non-allowed special character"""
        is_valid, error = Validators.validate_password("ValidPass123#")
        assert is_valid is False
        assert "special character" in error.lower()

    def test_validate_password_valid_long_password(self):
        """Test very long valid password"""
        long_pass = "ValidPass123!" * 10
        is_valid, error = Validators.validate_password(long_pass)
        assert is_valid is True

    def test_validate_password_multiple_uppercase(self):
        """Test password with multiple uppercase letters"""
        is_valid, error = Validators.validate_password("VALID Pass123!")
        assert is_valid is True

    def test_validate_password_multiple_lowercase(self):
        """Test password with multiple lowercase letters"""
        is_valid, error = Validators.validate_password("ValidPASS123!")
        assert is_valid is True

    def test_validate_password_multiple_digits(self):
        """Test password with multiple digits"""
        is_valid, error = Validators.validate_password("ValidPass1234567!")
        assert is_valid is True

    def test_validate_password_multiple_special(self):
        """Test password with multiple special characters"""
        is_valid, error = Validators.validate_password("ValidPass123!@$")
        assert is_valid is True

    def test_validate_password_exact_min_length(self):
        """Test password at exactly minimum length"""
        # Assuming min length is 8 from settings
        is_valid, error = Validators.validate_password("Pass123!")
        assert is_valid is True

    def test_validate_password_one_char_too_short(self):
        """Test password one character too short"""
        is_valid, error = Validators.validate_password("Pas123!")
        assert is_valid is False
        assert "characters" in error.lower()

    def test_validate_password_whitespace_only(self):
        """Test password with only whitespace"""
        is_valid, error = Validators.validate_password("        ")
        assert is_valid is False
        # Will fail on no uppercase, lowercase, digit, or special

    def test_validate_password_with_spaces(self):
        """Test password with spaces (should still be valid if has requirements)"""
        is_valid, error = Validators.validate_password("Valid Pass 123!")
        assert is_valid is True

    def test_validate_password_only_uppercase_and_digit(self):
        """Test password missing lowercase and special"""
        is_valid, error = Validators.validate_password("ONLYUPPER123")
        assert is_valid is False

    def test_validate_password_only_lowercase_and_digit(self):
        """Test password missing uppercase and special"""
        is_valid, error = Validators.validate_password("onlylower123")
        assert is_valid is False

    def test_validate_password_unicode_characters(self):
        """Test password with unicode characters"""
        is_valid, error = Validators.validate_password("ValidPass123!ñ")
        # Unicode char is not a special char, but password is still valid
        assert is_valid is True

    def test_validate_password_at_symbol_special(self):
        """Test @ as special character"""
        is_valid, error = Validators.validate_password("ValidPass123@")
        assert is_valid is True

    def test_validate_password_dollar_special(self):
        """Test $ as special character"""
        is_valid, error = Validators.validate_password("ValidPass123$")
        assert is_valid is True

    def test_validate_password_exclamation_special(self):
        """Test ! as special character"""
        is_valid, error = Validators.validate_password("ValidPass123!")
        assert is_valid is True

    def test_validate_password_percent_special(self):
        """Test % as special character"""
        is_valid, error = Validators.validate_password("ValidPass123%")
        assert is_valid is True

    def test_validate_password_asterisk_special(self):
        """Test * as special character"""
        is_valid, error = Validators.validate_password("ValidPass123*")
        assert is_valid is True

    def test_validate_password_question_special(self):
        """Test ? as special character"""
        is_valid, error = Validators.validate_password("ValidPass123?")
        assert is_valid is True

    def test_validate_password_ampersand_special(self):
        """Test & as special character"""
        is_valid, error = Validators.validate_password("ValidPass123&")
        assert is_valid is True

    # ===== EDGE CASES =====

    def test_validate_email_very_long(self):
        """Test very long email"""
        long_local = "a" * 50
        is_valid, error = Validators.validate_email(f"{long_local}@example.com")
        assert is_valid is True

    def test_validate_email_tld_long(self):
        """Test email with long TLD"""
        is_valid, error = Validators.validate_email("user@example.museum")
        assert is_valid is True

    def test_validate_password_exactly_8_chars(self):
        """Test password with exactly 8 characters"""
        is_valid, error = Validators.validate_password("Pass123!")
        assert is_valid is True

    def test_validate_password_7_chars(self):
        """Test 7 character password (should fail)"""
        is_valid, error = Validators.validate_password("Pas12!A")
        assert is_valid is False

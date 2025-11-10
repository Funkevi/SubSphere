import pytest
from src.utils.validators import Validators
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))


class TestValidators:
    '''Unit tests for validation functions'''

    def test_validate_email_valid(self):
        '''Test valid email format'''
        is_valid, error = Validators.validate_email("user@gmail.com")  # Changed
        assert is_valid is True
        assert error == ""

    def test_validate_email_invalid_format(self):
        '''Test invalid email format'''
        is_valid, error = Validators.validate_email("invalid-email")
        assert is_valid is False
        assert "Invalid email format" in error

    def test_validate_email_empty(self):
        '''Test empty email'''
        is_valid, error = Validators.validate_email("")
        assert is_valid is False
        assert "Email is required" in error

    def test_validate_password_valid(self):
        '''Test valid password strength'''
        is_valid, error = Validators.validate_password("ValidPass123!")
        assert is_valid is True
        assert error == ""

    def test_validate_password_too_short(self):
        '''Test password too short'''
        is_valid, error = Validators.validate_password("Short1!")
        assert is_valid is False
        assert "at least 8 characters" in error

    def test_validate_password_no_uppercase(self):
        '''Test password missing uppercase'''
        is_valid, error = Validators.validate_password("validpass123!")
        assert is_valid is False
        assert "uppercase" in error

    def test_validate_password_no_digit(self):
        '''Test password missing digit'''
        is_valid, error = Validators.validate_password("ValidPass!")
        assert is_valid is False
        assert "digit" in error

    def test_validate_password_no_special(self):
        '''Test password missing special character'''
        is_valid, error = Validators.validate_password("ValidPass123")
        assert is_valid is False
        assert "special character" in error

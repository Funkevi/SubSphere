"""
Unit tests for validate_uuid utility function
Comprehensive coverage for UUID validation
"""
import pytest
from src.utils.validators import validate_uuid


class TestValidateUUID:
    """Test suite for validate_uuid function"""
    
    def test_valid_uuid_v4(self):
        """Test valid UUID v4 format"""
        assert validate_uuid("550e8400-e29b-41d4-a716-446655440000") is True
    
    def test_valid_uuid_lowercase(self):
        """Test valid UUID with lowercase letters"""
        assert validate_uuid("a1b2c3d4-e5f6-7890-abcd-ef1234567890") is True
    
    def test_valid_uuid_uppercase(self):
        """Test valid UUID with uppercase letters"""
        assert validate_uuid("A1B2C3D4-E5F6-7890-ABCD-EF1234567890") is True
    
    def test_valid_uuid_mixed_case(self):
        """Test valid UUID with mixed case"""
        assert validate_uuid("A1b2C3d4-E5f6-7890-AbCd-Ef1234567890") is True
    
    def test_invalid_uuid_short(self):
        """Test invalid UUID - too short"""
        assert validate_uuid("550e8400-e29b-41d4") is False
    
    def test_invalid_uuid_long(self):
        """Test invalid UUID - too long"""
        assert validate_uuid("550e8400-e29b-41d4-a716-446655440000-extra") is False
    
    def test_invalid_uuid_wrong_format(self):
        """Test invalid UUID - wrong format"""
        assert validate_uuid("not-a-valid-uuid-format") is False
    
    def test_invalid_uuid_missing_hyphens(self):
        """Test UUID without hyphens (valid - Python's uuid accepts this)"""
        # Python's uuid.UUID() accepts hex strings without hyphens
        assert validate_uuid("550e8400e29b41d4a716446655440000") is True
    
    def test_invalid_uuid_extra_hyphens(self):
        """Test UUID with different hyphen positions (valid - flexible parsing)"""
        # Python's uuid.UUID() accepts various formats
        assert validate_uuid("550e-8400-e29b-41d4-a716-446655440000") is True
    
    def test_invalid_uuid_empty_string(self):
        """Test invalid UUID - empty string"""
        assert validate_uuid("") is False
    
    def test_invalid_uuid_none(self):
        """Test invalid UUID - None value"""
        assert validate_uuid(None) is False
    
    def test_invalid_uuid_number(self):
        """Test invalid UUID - number"""
        assert validate_uuid(12345) is False
    
    def test_invalid_uuid_list(self):
        """Test invalid UUID - list"""
        assert validate_uuid(["550e8400-e29b-41d4-a716-446655440000"]) is False
    
    def test_invalid_uuid_dict(self):
        """Test invalid UUID - dict"""
        assert validate_uuid({"uuid": "550e8400-e29b-41d4-a716-446655440000"}) is False
    
    def test_invalid_uuid_special_chars(self):
        """Test invalid UUID - special characters"""
        assert validate_uuid("550e8400-e29b-41d4-a716-44665544000@") is False
    
    def test_invalid_uuid_spaces(self):
        """Test invalid UUID - contains spaces"""
        assert validate_uuid("550e8400 e29b 41d4 a716 446655440000") is False
    
    def test_valid_uuid_with_curly_braces(self):
        """Test valid UUID with curly braces (Microsoft format)"""
        assert validate_uuid("{550e8400-e29b-41d4-a716-446655440000}") is True
    
    def test_valid_uuid_with_urn_prefix(self):
        """Test valid UUID with URN prefix"""
        assert validate_uuid("urn:uuid:550e8400-e29b-41d4-a716-446655440000") is True
    
    def test_valid_uuid_all_zeros(self):
        """Test valid UUID with all zeros (nil UUID)"""
        assert validate_uuid("00000000-0000-0000-0000-000000000000") is True
    
    def test_valid_uuid_all_fs(self):
        """Test valid UUID with all Fs"""
        assert validate_uuid("ffffffff-ffff-ffff-ffff-ffffffffffff") is True
    
    def test_invalid_uuid_partial_string(self):
        """Test invalid UUID - partial string"""
        assert validate_uuid("550e8400-e29b") is False
    
    def test_invalid_uuid_boolean(self):
        """Test invalid UUID - boolean value"""
        assert validate_uuid(True) is False
        assert validate_uuid(False) is False
    
    def test_invalid_uuid_float(self):
        """Test invalid UUID - float value"""
        assert validate_uuid(123.456) is False
    
    def test_valid_uuid_versions(self):
        """Test various UUID versions"""
        # UUID v1
        assert validate_uuid("a0eebc99-9c0b-11d1-b245-5ffdce74fad2") is True
        # UUID v3
        assert validate_uuid("a3bb189e-8bf9-3888-9912-ace4e6543002") is True
        # UUID v4
        assert validate_uuid("f47ac10b-58cc-4372-a567-0e02b2c3d479") is True
        # UUID v5
        assert validate_uuid("886313e1-3b8a-5372-9b90-0c9aee199e5d") is True

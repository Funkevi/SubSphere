import pytest
import sys, os
from unittest.mock import Mock, AsyncMock, patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from src.auth.supabase_auth import SupabaseAuth


class TestSupabaseAuth:
    """Unit tests for Supabase authentication methods"""

    @pytest.fixture
    def auth_instance(self):
        """Create SupabaseAuth instance"""
        return SupabaseAuth()

    @pytest.mark.asyncio
    async def test_sign_up_success(self, auth_instance):
        """Test successful user signup"""
        with patch.object(auth_instance.client.auth, 'sign_up') as mock_signup:
            # Mock successful response
            mock_signup.return_value = Mock(
                user=Mock(id="user-123", email="test@gmail.com"),
                session=Mock(access_token="token-123")
            )
            
            result = await auth_instance.sign_up("test@gmail.com", "ValidPass123!")
            
            assert result["success"] is True
            assert result["user"].id == "user-123"

    @pytest.mark.asyncio
    async def test_sign_up_duplicate_email(self, auth_instance):
        """Test signup with duplicate email"""
        with patch.object(auth_instance.client.auth, 'sign_up') as mock_signup:
            # Mock duplicate email error
            mock_signup.side_effect = Exception("User already registered")
            
            result = await auth_instance.sign_up("duplicate@gmail.com", "ValidPass123!")
            
            assert result["success"] is False
            assert result["code"] == 409
            assert "already registered" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_sign_up_generic_error(self, auth_instance):
        """Test signup with generic error"""
        with patch.object(auth_instance.client.auth, 'sign_up') as mock_signup:
            # Mock generic error
            mock_signup.side_effect = Exception("Network error")
            
            result = await auth_instance.sign_up("test@gmail.com", "ValidPass123!")
            
            assert result["success"] is False
            assert result["code"] == 400

    @pytest.mark.asyncio
    async def test_sign_in_success(self, auth_instance):
        """Test successful user signin"""
        with patch.object(auth_instance.client.auth, 'sign_in_with_password') as mock_signin:
            # Mock successful login
            mock_signin.return_value = Mock(
                user=Mock(id="user-456", email="test@gmail.com"),
                session=Mock(access_token="token-456")
            )
            
            result = await auth_instance.sign_in("test@gmail.com", "ValidPass123!")
            
            assert result["success"] is True
            assert result["user"].id == "user-456"

    @pytest.mark.asyncio
    async def test_sign_in_invalid_credentials(self, auth_instance):
        """Test signin with invalid credentials"""
        with patch.object(auth_instance.client.auth, 'sign_in_with_password') as mock_signin:
            # Mock invalid credentials error
            mock_signin.side_effect = Exception("Invalid login credentials")
            
            result = await auth_instance.sign_in("test@gmail.com", "WrongPass!")
            
            assert result["success"] is False
            assert result["code"] == 401

    @pytest.mark.asyncio
    async def test_get_user_profile_success(self, auth_instance):
        """Test get user profile success"""
        with patch.object(auth_instance.service_client, 'table') as mock_table:
            # Mock successful profile retrieval
            mock_chain = Mock()
            mock_chain.select.return_value = mock_chain
            mock_chain.eq.return_value = mock_chain
            mock_chain.single.return_value = mock_chain
            mock_chain.execute.return_value = Mock(data={"user_id": "123", "role": "subscriber"})
            mock_table.return_value = mock_chain
            
            result = await auth_instance.get_user_profile("user-123")
            
            assert result["success"] is True
            assert result["profile"]["user_id"] == "123"

    @pytest.mark.asyncio
    async def test_get_user_profile_error(self, auth_instance):
        """Test get user profile with error"""
        with patch.object(auth_instance.service_client, 'table') as mock_table:
            # Mock error
            mock_chain = Mock()
            mock_chain.select.return_value = mock_chain
            mock_chain.eq.return_value = mock_chain
            mock_chain.single.return_value = mock_chain
            mock_chain.execute.side_effect = Exception("Profile not found")
            mock_table.return_value = mock_chain
            
            result = await auth_instance.get_user_profile("invalid-user")
            
            assert result["success"] is False
            assert "error" in result

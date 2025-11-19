"""
Unit tests for subscription routes with mocking
Story SIM-89: Trial Period Activation
Target: >85% code coverage
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


class TestActivateTrialEndpoint:
    """Test suite for POST /api/subscriptions/trial endpoint"""
    
    @patch('src.api.subscription_routes.supabase_auth')
    @patch('src.api.subscription_routes.validate_uuid')
    def test_activate_trial_success(self, mock_validate_uuid, mock_supabase):
        """Test successful trial activation (SIM-89, SIM-92, SIM-93, SIM-94)"""
        # Setup mocks
        mock_validate_uuid.return_value = True
        
        # Mock plan response
        mock_plan_response = Mock()
        mock_plan_response.data = {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "name": "Premium",
            "price": 29.99,
            "is_active": True
        }
        
        # Mock existing subscriptions (none)
        mock_existing_response = Mock()
        mock_existing_response.data = []
        
        # Mock insert response
        mock_insert_response = Mock()
        mock_insert_response.data = [{
            "id": "650e8400-e29b-41d4-a716-446655440000",
            "user_id": "user123",
            "plan_id": "550e8400-e29b-41d4-a716-446655440000",
            "status": "trial",
            "trial_start": "2025-11-19T09:00:00+00:00",
            "trial_end": "2025-12-03T09:00:00+00:00",
            "next_billing_date": "2025-12-04T09:00:00+00:00",
            "created_at": "2025-11-19T09:00:00+00:00"
        }]
        
        # Configure mock chain
        mock_table = Mock()
        mock_table.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.return_value = mock_plan_response
        mock_table.select.return_value.eq.return_value.eq.return_value.execute.return_value = mock_existing_response
        mock_table.insert.return_value.execute.return_value = mock_insert_response
        
        mock_supabase.service_client.table.return_value = mock_table
        
        # Make request with mock authentication
        with patch('src.auth.rbac.JWTHandler.verify_token') as mock_verify:
            mock_verify.return_value = {
                "valid": True,
                "payload": {"user_id": "user123", "role": "subscriber"}
            }
            
            response = client.post(
                "/api/subscriptions/trial",
                json={"plan_id": "550e8400-e29b-41d4-a716-446655440000"},
                headers={"Authorization": "Bearer fake_token"}
            )
        
        # Assertions
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "trial"
        assert data["plan_id"] == "550e8400-e29b-41d4-a716-446655440000"
        assert "trial_start" in data
        assert "trial_end" in data
        assert "next_billing_date" in data
    
    @patch('src.api.subscription_routes.validate_uuid')
    def test_activate_trial_invalid_uuid(self, mock_validate_uuid):
        """Test trial activation with invalid UUID format"""
        mock_validate_uuid.return_value = False
        
        with patch('src.auth.rbac.JWTHandler.verify_token') as mock_verify:
            mock_verify.return_value = {
                "valid": True,
                "payload": {"user_id": "user123", "role": "subscriber"}
            }
            
            response = client.post(
                "/api/subscriptions/trial",
                json={"plan_id": "invalid-uuid"},
                headers={"Authorization": "Bearer fake_token"}
            )
        
        assert response.status_code == 400
        assert "Invalid plan_id format" in response.json()["detail"]
    
    @patch('src.api.subscription_routes.supabase_auth')
    @patch('src.api.subscription_routes.validate_uuid')
    def test_activate_trial_plan_not_found(self, mock_validate_uuid, mock_supabase):
        """Test trial activation with non-existent plan"""
        mock_validate_uuid.return_value = True
        
        # Mock empty plan response
        mock_plan_response = Mock()
        mock_plan_response.data = None
        
        mock_table = Mock()
        mock_table.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.return_value = mock_plan_response
        mock_supabase.service_client.table.return_value = mock_table
        
        with patch('src.auth.rbac.JWTHandler.verify_token') as mock_verify:
            mock_verify.return_value = {
                "valid": True,
                "payload": {"user_id": "user123", "role": "subscriber"}
            }
            
            response = client.post(
                "/api/subscriptions/trial",
                json={"plan_id": "550e8400-e29b-41d4-a716-446655440000"},
                headers={"Authorization": "Bearer fake_token"}
            )
        
        assert response.status_code == 404
        assert "Plan not found or inactive" in response.json()["detail"]
    
    @patch('src.api.subscription_routes.supabase_auth')
    @patch('src.api.subscription_routes.validate_uuid')
    def test_activate_trial_duplicate_active_subscription(self, mock_validate_uuid, mock_supabase):
        """Test cannot create trial when active subscription exists"""
        mock_validate_uuid.return_value = True
        
        # Mock plan exists
        mock_plan_response = Mock()
        mock_plan_response.data = {"id": "plan123", "is_active": True}
        
        # Mock existing active subscription
        mock_existing_response = Mock()
        mock_existing_response.data = [{
            "id": "sub123",
            "status": "active",
            "plan_id": "plan123"
        }]
        
        mock_table = Mock()
        mock_table.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.return_value = mock_plan_response
        mock_table.select.return_value.eq.return_value.eq.return_value.execute.return_value = mock_existing_response
        mock_supabase.service_client.table.return_value = mock_table
        
        with patch('src.auth.rbac.JWTHandler.verify_token') as mock_verify:
            mock_verify.return_value = {
                "valid": True,
                "payload": {"user_id": "user123", "role": "subscriber"}
            }
            
            response = client.post(
                "/api/subscriptions/trial",
                json={"plan_id": "plan123"},
                headers={"Authorization": "Bearer fake_token"}
            )
        
        assert response.status_code == 400
        assert "already has active/trial subscription" in response.json()["detail"]
    
    @patch('src.api.subscription_routes.supabase_auth')
    @patch('src.api.subscription_routes.validate_uuid')
    def test_activate_trial_duplicate_trial_subscription(self, mock_validate_uuid, mock_supabase):
        """Test cannot create trial when trial subscription exists"""
        mock_validate_uuid.return_value = True
        
        # Mock plan exists
        mock_plan_response = Mock()
        mock_plan_response.data = {"id": "plan123", "is_active": True}
        
        # Mock existing trial subscription
        mock_existing_response = Mock()
        mock_existing_response.data = [{
            "id": "sub123",
            "status": "trial",
            "plan_id": "plan123"
        }]
        
        mock_table = Mock()
        mock_table.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.return_value = mock_plan_response
        mock_table.select.return_value.eq.return_value.eq.return_value.execute.return_value = mock_existing_response
        mock_supabase.service_client.table.return_value = mock_table
        
        with patch('src.auth.rbac.JWTHandler.verify_token') as mock_verify:
            mock_verify.return_value = {
                "valid": True,
                "payload": {"user_id": "user123", "role": "subscriber"}
            }
            
            response = client.post(
                "/api/subscriptions/trial",
                json={"plan_id": "plan123"},
                headers={"Authorization": "Bearer fake_token"}
            )
        
        assert response.status_code == 400
        assert "already has active/trial subscription" in response.json()["detail"]
    
    @patch('src.api.subscription_routes.supabase_auth')
    @patch('src.api.subscription_routes.validate_uuid')
    def test_activate_trial_database_insert_failure(self, mock_validate_uuid, mock_supabase):
        """Test trial activation when database insert fails"""
        mock_validate_uuid.return_value = True
        
        # Mock plan exists
        mock_plan_response = Mock()
        mock_plan_response.data = {"id": "plan123", "is_active": True}
        
        # Mock no existing subscriptions
        mock_existing_response = Mock()
        mock_existing_response.data = []
        
        # Mock failed insert
        mock_insert_response = Mock()
        mock_insert_response.data = None
        
        mock_table = Mock()
        mock_table.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.return_value = mock_plan_response
        mock_table.select.return_value.eq.return_value.eq.return_value.execute.return_value = mock_existing_response
        mock_table.insert.return_value.execute.return_value = mock_insert_response
        mock_supabase.service_client.table.return_value = mock_table
        
        with patch('src.auth.rbac.JWTHandler.verify_token') as mock_verify:
            mock_verify.return_value = {
                "valid": True,
                "payload": {"user_id": "user123", "role": "subscriber"}
            }
            
            response = client.post(
                "/api/subscriptions/trial",
                json={"plan_id": "plan123"},
                headers={"Authorization": "Bearer fake_token"}
            )
        
        assert response.status_code == 400
        assert "Failed to create trial subscription" in response.json()["detail"]
    
    @patch('src.api.subscription_routes.supabase_auth')
    @patch('src.api.subscription_routes.validate_uuid')
    def test_activate_trial_database_empty_response(self, mock_validate_uuid, mock_supabase):
        """Test trial activation when database returns empty list"""
        mock_validate_uuid.return_value = True
        
        # Mock plan exists
        mock_plan_response = Mock()
        mock_plan_response.data = {"id": "plan123", "is_active": True}
        
        # Mock no existing subscriptions
        mock_existing_response = Mock()
        mock_existing_response.data = []
        
        # Mock empty insert response
        mock_insert_response = Mock()
        mock_insert_response.data = []
        
        mock_table = Mock()
        mock_table.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.return_value = mock_plan_response
        mock_table.select.return_value.eq.return_value.eq.return_value.execute.return_value = mock_existing_response
        mock_table.insert.return_value.execute.return_value = mock_insert_response
        mock_supabase.service_client.table.return_value = mock_table
        
        with patch('src.auth.rbac.JWTHandler.verify_token') as mock_verify:
            mock_verify.return_value = {
                "valid": True,
                "payload": {"user_id": "user123", "role": "subscriber"}
            }
            
            response = client.post(
                "/api/subscriptions/trial",
                json={"plan_id": "plan123"},
                headers={"Authorization": "Bearer fake_token"}
            )
        
        assert response.status_code == 400
        assert "Failed to create trial subscription" in response.json()["detail"]
    
    def test_activate_trial_missing_authorization(self):
        """Test trial activation without authorization header"""
        response = client.post(
            "/api/subscriptions/trial",
            json={"plan_id": "550e8400-e29b-41d4-a716-446655440000"}
        )
        
        assert response.status_code == 401
        assert "Missing authorization header" in response.json()["detail"]
    
    @patch('src.api.subscription_routes.supabase_auth')
    @patch('src.api.subscription_routes.validate_uuid')
    def test_activate_trial_exception_handling(self, mock_validate_uuid, mock_supabase):
        """Test trial activation with unexpected exception"""
        mock_validate_uuid.return_value = True
        
        # Mock exception
        mock_supabase.service_client.table.side_effect = Exception("Database connection error")
        
        with patch('src.auth.rbac.JWTHandler.verify_token') as mock_verify:
            mock_verify.return_value = {
                "valid": True,
                "payload": {"user_id": "user123", "role": "subscriber"}
            }
            
            response = client.post(
                "/api/subscriptions/trial",
                json={"plan_id": "550e8400-e29b-41d4-a716-446655440000"},
                headers={"Authorization": "Bearer fake_token"}
            )
        
        assert response.status_code == 500
        assert "Error creating trial subscription" in response.json()["detail"]


class TestGetSubscriptionEndpoint:
    """Test suite for GET /api/subscriptions/{subscription_id} endpoint"""
    
    @patch('src.api.subscription_routes.supabase_auth')
    @patch('src.api.subscription_routes.validate_uuid')
    def test_get_subscription_success(self, mock_validate_uuid, mock_supabase):
        """Test successful subscription retrieval"""
        mock_validate_uuid.return_value = True
        
        mock_response = Mock()
        mock_response.data = {
            "id": "sub123",
            "user_id": "user123",
            "plan_id": "plan123",
            "status": "trial",
            "trial_start": "2025-11-19T09:00:00+00:00",
            "trial_end": "2025-12-03T09:00:00+00:00",
            "next_billing_date": "2025-12-04T09:00:00+00:00",
            "started_at": "2025-11-19T09:00:00+00:00",
            "expires_at": "2025-12-03T09:00:00+00:00",
            "created_at": "2025-11-19T09:00:00+00:00",
            "paused_at": None,
            "resumed_at": None,
            "cancelled_at": None,
            "updated_at": None
        }
        
        mock_table = Mock()
        mock_table.select.return_value.eq.return_value.single.return_value.execute.return_value = mock_response
        mock_supabase.service_client.table.return_value = mock_table
        
        with patch('src.auth.rbac.JWTHandler.verify_token') as mock_verify:
            mock_verify.return_value = {
                "valid": True,
                "payload": {"user_id": "user123", "role": "subscriber"}
            }
            
            response = client.get(
                "/api/subscriptions/sub123",
                headers={"Authorization": "Bearer fake_token"}
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "sub123"
        assert data["status"] == "trial"
    
    @patch('src.api.subscription_routes.validate_uuid')
    def test_get_subscription_invalid_uuid(self, mock_validate_uuid):
        """Test get subscription with invalid UUID"""
        mock_validate_uuid.return_value = False
        
        with patch('src.auth.rbac.JWTHandler.verify_token') as mock_verify:
            mock_verify.return_value = {
                "valid": True,
                "payload": {"user_id": "user123", "role": "subscriber"}
            }
            
            response = client.get(
                "/api/subscriptions/invalid-uuid",
                headers={"Authorization": "Bearer fake_token"}
            )
        
        assert response.status_code == 400
        assert "Invalid subscription_id format" in response.json()["detail"]
    
    @patch('src.api.subscription_routes.supabase_auth')
    @patch('src.api.subscription_routes.validate_uuid')
    def test_get_subscription_not_found(self, mock_validate_uuid, mock_supabase):
        """Test get non-existent subscription"""
        mock_validate_uuid.return_value = True
        
        mock_response = Mock()
        mock_response.data = None
        
        mock_table = Mock()
        mock_table.select.return_value.eq.return_value.single.return_value.execute.return_value = mock_response
        mock_supabase.service_client.table.return_value = mock_table
        
        with patch('src.auth.rbac.JWTHandler.verify_token') as mock_verify:
            mock_verify.return_value = {
                "valid": True,
                "payload": {"user_id": "user123", "role": "subscriber"}
            }
            
            response = client.get(
                "/api/subscriptions/sub123",
                headers={"Authorization": "Bearer fake_token"}
            )
        
        assert response.status_code == 404
        assert "Subscription not found" in response.json()["detail"]
    
    @patch('src.api.subscription_routes.supabase_auth')
    @patch('src.api.subscription_routes.validate_uuid')
    def test_get_subscription_access_denied(self, mock_validate_uuid, mock_supabase):
        """Test user cannot access another user's subscription"""
        mock_validate_uuid.return_value = True
        
        mock_response = Mock()
        mock_response.data = {
            "id": "sub123",
            "user_id": "other_user",  # Different user
            "status": "trial"
        }
        
        mock_table = Mock()
        mock_table.select.return_value.eq.return_value.single.return_value.execute.return_value = mock_response
        mock_supabase.service_client.table.return_value = mock_table
        
        with patch('src.auth.rbac.JWTHandler.verify_token') as mock_verify:
            mock_verify.return_value = {
                "valid": True,
                "payload": {"user_id": "user123", "role": "subscriber"}  # Not admin
            }
            
            response = client.get(
                "/api/subscriptions/sub123",
                headers={"Authorization": "Bearer fake_token"}
            )
        
        assert response.status_code == 403
        assert "Access denied" in response.json()["detail"]
    
    @patch('src.api.subscription_routes.supabase_auth')
    @patch('src.api.subscription_routes.validate_uuid')
    def test_get_subscription_admin_can_access_any(self, mock_validate_uuid, mock_supabase):
        """Test admin can access any user's subscription"""
        mock_validate_uuid.return_value = True
        
        mock_response = Mock()
        mock_response.data = {
            "id": "sub123",
            "user_id": "other_user",
            "plan_id": "plan123",
            "status": "trial",
            "trial_start": "2025-11-19T09:00:00+00:00",
            "trial_end": "2025-12-03T09:00:00+00:00",
            "next_billing_date": "2025-12-04T09:00:00+00:00",
            "started_at": "2025-11-19T09:00:00+00:00",
            "expires_at": "2025-12-03T09:00:00+00:00",
            "created_at": "2025-11-19T09:00:00+00:00",
            "paused_at": None,
            "resumed_at": None,
            "cancelled_at": None,
            "updated_at": None
        }
        
        mock_table = Mock()
        mock_table.select.return_value.eq.return_value.single.return_value.execute.return_value = mock_response
        mock_supabase.service_client.table.return_value = mock_table
        
        with patch('src.auth.rbac.JWTHandler.verify_token') as mock_verify:
            mock_verify.return_value = {
                "valid": True,
                "payload": {"user_id": "admin123", "role": "admin"}
            }
            
            response = client.get(
                "/api/subscriptions/sub123",
                headers={"Authorization": "Bearer fake_token"}
            )
        
        assert response.status_code == 200
        assert response.json()["user_id"] == "other_user"
    
    @patch('src.api.subscription_routes.supabase_auth')
    @patch('src.api.subscription_routes.validate_uuid')
    def test_get_subscription_exception(self, mock_validate_uuid, mock_supabase):
        """Test get subscription with unexpected exception"""
        mock_validate_uuid.return_value = True
        mock_supabase.service_client.table.side_effect = Exception("Database error")
        
        with patch('src.auth.rbac.JWTHandler.verify_token') as mock_verify:
            mock_verify.return_value = {
                "valid": True,
                "payload": {"user_id": "user123", "role": "subscriber"}
            }
            
            response = client.get(
                "/api/subscriptions/sub123",
                headers={"Authorization": "Bearer fake_token"}
            )
        
        assert response.status_code == 500
        assert "Error retrieving subscription" in response.json()["detail"]


class TestListSubscriptionsEndpoint:
    """Test suite for GET /api/subscriptions endpoint"""
    
    @patch('src.api.subscription_routes.supabase_auth')
    def test_list_subscriptions_success(self, mock_supabase):
        """Test successful subscriptions listing"""
        mock_data_response = Mock()
        mock_data_response.data = [
            {
                "id": "sub1",
                "user_id": "user123",
                "plan_id": "plan1",
                "status": "trial",
                "trial_start": "2025-11-19T09:00:00+00:00",
                "trial_end": "2025-12-03T09:00:00+00:00",
                "next_billing_date": "2025-12-04T09:00:00+00:00",
                "started_at": "2025-11-19T09:00:00+00:00",
                "expires_at": "2025-12-03T09:00:00+00:00",
                "created_at": "2025-11-19T09:00:00+00:00",
                "paused_at": None,
                "resumed_at": None,
                "cancelled_at": None,
                "updated_at": None
            }
        ]
        
        mock_count_response = Mock()
        mock_count_response.count = 1
        
        mock_table = Mock()
        mock_table.select.return_value.eq.return_value.order.return_value.range.return_value.execute.return_value = mock_data_response
        mock_table.select.return_value.eq.return_value.execute.return_value = mock_count_response
        mock_supabase.service_client.table.return_value = mock_table
        
        with patch('src.auth.rbac.JWTHandler.verify_token') as mock_verify:
            mock_verify.return_value = {
                "valid": True,
                "payload": {"user_id": "user123", "role": "subscriber"}
            }
            
            response = client.get(
                "/api/subscriptions",
                headers={"Authorization": "Bearer fake_token"}
            )
        
        assert response.status_code == 200
        data = response.json()
        assert "subscriptions" in data
        assert "total" in data
        assert data["total"] == 1
        assert len(data["subscriptions"]) == 1
    
    @patch('src.api.subscription_routes.supabase_auth')
    def test_list_subscriptions_with_status_filter(self, mock_supabase):
        """Test listing subscriptions with status filter"""
        mock_data_response = Mock()
        mock_data_response.data = []
        
        mock_count_response = Mock()
        mock_count_response.count = 0
        
        mock_table = Mock()
        mock_query = mock_table.select.return_value.eq.return_value
        mock_query.eq.return_value.order.return_value.range.return_value.execute.return_value = mock_data_response
        mock_query.eq.return_value.execute.return_value = mock_count_response
        mock_supabase.service_client.table.return_value = mock_table
        
        with patch('src.auth.rbac.JWTHandler.verify_token') as mock_verify:
            mock_verify.return_value = {
                "valid": True,
                "payload": {"user_id": "user123", "role": "subscriber"}
            }
            
            response = client.get(
                "/api/subscriptions?status=trial",
                headers={"Authorization": "Bearer fake_token"}
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert len(data["subscriptions"]) == 0
    
    @patch('src.api.subscription_routes.supabase_auth')
    def test_list_subscriptions_with_pagination(self, mock_supabase):
        """Test listing subscriptions with pagination"""
        mock_data_response = Mock()
        mock_data_response.data = []
        
        mock_count_response = Mock()
        mock_count_response.count = 0
        
        mock_table = Mock()
        mock_table.select.return_value.eq.return_value.order.return_value.range.return_value.execute.return_value = mock_data_response
        mock_table.select.return_value.eq.return_value.execute.return_value = mock_count_response
        mock_supabase.service_client.table.return_value = mock_table
        
        with patch('src.auth.rbac.JWTHandler.verify_token') as mock_verify:
            mock_verify.return_value = {
                "valid": True,
                "payload": {"user_id": "user123", "role": "subscriber"}
            }
            
            response = client.get(
                "/api/subscriptions?limit=5&offset=10",
                headers={"Authorization": "Bearer fake_token"}
            )
        
        assert response.status_code == 200
    
    @patch('src.api.subscription_routes.supabase_auth')
    def test_list_subscriptions_exception(self, mock_supabase):
        """Test listing subscriptions with exception"""
        mock_supabase.service_client.table.side_effect = Exception("Database error")
        
        with patch('src.auth.rbac.JWTHandler.verify_token') as mock_verify:
            mock_verify.return_value = {
                "valid": True,
                "payload": {"user_id": "user123", "role": "subscriber"}
            }
            
            response = client.get(
                "/api/subscriptions",
                headers={"Authorization": "Bearer fake_token"}
            )
        
        assert response.status_code == 500
        assert "Error listing subscriptions" in response.json()["detail"]


class TestGetUserSubscriptionsEndpoint:
    """Test suite for GET /api/subscriptions/user/{user_id} endpoint"""
    
    @patch('src.api.subscription_routes.supabase_auth')
    def test_get_user_subscriptions_success(self, mock_supabase):
        """Test successful user subscriptions retrieval"""
        mock_response = Mock()
        mock_response.data = [
            {
                "id": "sub1",
                "user_id": "user123",
                "plan_id": "plan1",
                "status": "trial",
                "subscription_plans": {
                    "name": "Premium",
                    "price": 29.99
                }
            }
        ]
        
        mock_table = Mock()
        mock_table.select.return_value.eq.return_value.order.return_value.execute.return_value = mock_response
        mock_supabase.service_client.table.return_value = mock_table
        
        with patch('src.auth.rbac.JWTHandler.verify_token') as mock_verify:
            mock_verify.return_value = {
                "valid": True,
                "payload": {"user_id": "admin123", "role": "admin"}
            }
            
            response = client.get(
                "/api/subscriptions/user/user123",
                headers={"Authorization": "Bearer fake_token"}
            )
        
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    @patch('src.api.subscription_routes.supabase_auth')
    def test_get_user_subscriptions_exception(self, mock_supabase):
        """Test get user subscriptions with exception"""
        mock_supabase.service_client.table.side_effect = Exception("Database error")
        
        with patch('src.auth.rbac.JWTHandler.verify_token') as mock_verify:
            mock_verify.return_value = {
                "valid": True,
                "payload": {"user_id": "admin123", "role": "admin"}
            }
            
            response = client.get(
                "/api/subscriptions/user/user123",
                headers={"Authorization": "Bearer fake_token"}
            )
        
        assert response.status_code == 400
        assert "Error fetching subscriptions" in response.json()["detail"]


class TestUpdateSubscriptionEndpoint:
    """Test suite for PUT /api/subscriptions/{subscription_id} endpoint"""
    
    @patch('src.api.subscription_routes.supabase_auth')
    def test_update_subscription_success(self, mock_supabase):
        """Test successful subscription update"""
        mock_response = Mock()
        mock_response.data = [{
            "id": "sub123",
            "user_id": "user123",
            "plan_id": "plan456",
            "status": "active"
        }]
        
        mock_table = Mock()
        mock_table.update.return_value.eq.return_value.execute.return_value = mock_response
        mock_supabase.service_client.table.return_value = mock_table
        
        with patch('src.auth.rbac.JWTHandler.verify_token') as mock_verify:
            mock_verify.return_value = {
                "valid": True,
                "payload": {"user_id": "user123", "role": "subscriber"}
            }
            
            response = client.put(
                "/api/subscriptions/sub123",
                json={
                    "subscription": {
                        "user_id": "user123",
                        "plan_id": "plan456",
                        "status": "active"
                    }
                },
                headers={"Authorization": "Bearer fake_token"}
            )
        
        assert response.status_code == 200
        assert response.json()["status"] == "active"
    
    @patch('src.api.subscription_routes.supabase_auth')
    def test_update_subscription_not_found(self, mock_supabase):
        """Test update non-existent subscription"""
        mock_response = Mock()
        mock_response.data = None
        
        mock_table = Mock()
        mock_table.update.return_value.eq.return_value.execute.return_value = mock_response
        mock_supabase.service_client.table.return_value = mock_table
        
        with patch('src.auth.rbac.JWTHandler.verify_token') as mock_verify:
            mock_verify.return_value = {
                "valid": True,
                "payload": {"user_id": "user123", "role": "admin"}
            }
            
            response = client.put(
                "/api/subscriptions/sub123",
                json={
                    "subscription": {
                        "user_id": "user123",
                        "plan_id": "plan456",
                        "status": "active"
                    }
                },
                headers={"Authorization": "Bearer fake_token"}
            )
        
        assert response.status_code == 404
        assert "Subscription not found" in response.json()["detail"]
    
    @patch('src.api.subscription_routes.supabase_auth')
    def test_update_subscription_exception(self, mock_supabase):
        """Test update subscription with exception"""
        mock_supabase.service_client.table.side_effect = Exception("Database error")
        
        with patch('src.auth.rbac.JWTHandler.verify_token') as mock_verify:
            mock_verify.return_value = {
                "valid": True,
                "payload": {"user_id": "user123", "role": "admin"}
            }
            
            response = client.put(
                "/api/subscriptions/sub123",
                json={
                    "subscription": {
                        "user_id": "user123",
                        "plan_id": "plan456",
                        "status": "active"
                    }
                },
                headers={"Authorization": "Bearer fake_token"}
            )
        
        assert response.status_code == 400
        assert "Error updating subscription" in response.json()["detail"]

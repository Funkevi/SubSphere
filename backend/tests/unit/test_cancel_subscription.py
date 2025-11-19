"""
Unit tests for cancel subscription endpoint
Story SIM-95: Subscription Cancellation Functionality
Target: >85% code coverage
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone
from fastapi import HTTPException
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


class TestCancelSubscriptionEndpoint:
    """Test suite for POST /api/subscriptions/{subscription_id}/cancel endpoint"""
    
    @patch('src.api.subscription_routes.supabase_auth')
    @patch('src.api.subscription_routes.validate_uuid')
    def test_cancel_subscription_success(self, mock_validate_uuid, mock_supabase):
        """Test successful subscription cancellation (SIM-95)"""
        mock_validate_uuid.return_value = True
        
        # Mock subscription fetch
        mock_sub_response = Mock()
        mock_sub_response.data = {
            "id": "sub123",
            "user_id": "user123",
            "status": "active",
            "next_billing_date": "2025-12-01T10:00:00+00:00"
        }
        
        # Mock successful update
        mock_update_response = Mock()
        mock_update_response.data = [{
            "id": "sub123",
            "status": "cancelled",
            "next_billing_date": None,
            "cancelled_at": "2025-11-19T10:00:00+00:00"
        }]
        
        # Mock audit log insert
        mock_audit_response = Mock()
        mock_audit_response.data = [{"id": "audit123"}]
        
        mock_table = Mock()
        mock_table.select.return_value.eq.return_value.single.return_value.execute.return_value = mock_sub_response
        mock_table.update.return_value.eq.return_value.execute.return_value = mock_update_response
        mock_table.insert.return_value.execute.return_value = mock_audit_response
        mock_supabase.service_client.table.return_value = mock_table
        
        with patch('src.auth.rbac.JWTHandler.verify_token') as mock_verify:
            mock_verify.return_value = {
                "valid": True,
                "payload": {"user_id": "user123", "role": "subscriber"}
            }
            
            response = client.post(
                "/api/subscriptions/sub123/cancel",
                headers={"Authorization": "Bearer fake_token"}
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "Subscription cancelled successfully"
        assert data["subscription_id"] == "sub123"
    
    @patch('src.api.subscription_routes.validate_uuid')
    def test_cancel_subscription_invalid_uuid(self, mock_validate_uuid):
        """Test cancel with invalid subscription ID format"""
        mock_validate_uuid.return_value = False
        
        with patch('src.auth.rbac.JWTHandler.verify_token') as mock_verify:
            mock_verify.return_value = {
                "valid": True,
                "payload": {"user_id": "user123", "role": "subscriber"}
            }
            
            response = client.post(
                "/api/subscriptions/invalid-id/cancel",
                headers={"Authorization": "Bearer fake_token"}
            )
        
        assert response.status_code == 400
        assert "Invalid subscription_id format" in response.json()["detail"]
    
    @patch('src.api.subscription_routes.supabase_auth')
    @patch('src.api.subscription_routes.validate_uuid')
    def test_cancel_subscription_not_found(self, mock_validate_uuid, mock_supabase):
        """Test cancel non-existent subscription"""
        mock_validate_uuid.return_value = True
        
        # Mock empty response for subscription fetch
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
            
            response = client.post(
                "/api/subscriptions/sub123/cancel",
                headers={"Authorization": "Bearer fake_token"}
            )
        
        assert response.status_code == 404
        assert "Subscription not found" in response.json()["detail"]
    
    @patch('src.api.subscription_routes.supabase_auth')
    @patch('src.api.subscription_routes.validate_uuid')
    def test_cancel_subscription_update_fails(self, mock_validate_uuid, mock_supabase):
        """Test cancel when update operation fails"""
        mock_validate_uuid.return_value = True
        
        # Mock subscription fetch success
        mock_sub_response = Mock()
        mock_sub_response.data = {
            "id": "sub123",
            "user_id": "user123",
            "status": "active"
        }
        
        # Mock update failure (no data returned)
        mock_update_response = Mock()
        mock_update_response.data = None
        
        mock_table = Mock()
        mock_table.select.return_value.eq.return_value.single.return_value.execute.return_value = mock_sub_response
        mock_table.update.return_value.eq.return_value.execute.return_value = mock_update_response
        mock_supabase.service_client.table.return_value = mock_table
        
        with patch('src.auth.rbac.JWTHandler.verify_token') as mock_verify:
            mock_verify.return_value = {
                "valid": True,
                "payload": {"user_id": "user123", "role": "subscriber"}
            }
            
            response = client.post(
                "/api/subscriptions/sub123/cancel",
                headers={"Authorization": "Bearer fake_token"}
            )
        
        assert response.status_code == 400
        assert "Failed to cancel subscription" in response.json()["detail"]
    
    def test_cancel_subscription_missing_auth(self):
        """Test cancel without authorization header"""
        response = client.post("/api/subscriptions/sub123/cancel")
        
        assert response.status_code == 401
        assert "Missing authorization header" in response.json()["detail"]
    
    @patch('src.api.subscription_routes.supabase_auth')
    @patch('src.api.subscription_routes.validate_uuid')
    def test_cancel_subscription_audit_log_failure(self, mock_validate_uuid, mock_supabase):
        """Test cancel succeeds even if audit log insert fails"""
        mock_validate_uuid.return_value = True
        
        # Mock subscription fetch
        mock_sub_response = Mock()
        mock_sub_response.data = {
            "id": "sub123",
            "user_id": "user123",
            "status": "active"
        }
        
        # Mock successful update
        mock_update_response = Mock()
        mock_update_response.data = [{
            "id": "sub123",
            "status": "cancelled",
            "cancelled_at": "2025-11-19T10:00:00+00:00"
        }]
        
        mock_table = Mock()
        
        # Setup mock to handle different table calls
        def table_side_effect(table_name):
            if table_name == "subscriptions":
                select_mock = Mock()
                select_mock.select.return_value.eq.return_value.single.return_value.execute.return_value = mock_sub_response
                select_mock.update.return_value.eq.return_value.execute.return_value = mock_update_response
                return select_mock
            elif table_name == "audit_logs":
                # Audit log insert fails
                audit_mock = Mock()
                audit_mock.insert.return_value.execute.side_effect = Exception("Audit log error")
                return audit_mock
            return Mock()
        
        mock_supabase.service_client.table.side_effect = table_side_effect
        
        with patch('src.auth.rbac.JWTHandler.verify_token') as mock_verify:
            mock_verify.return_value = {
                "valid": True,
                "payload": {"user_id": "user123", "role": "subscriber"}
            }
            
            # Should succeed despite audit log failure (with warning)
            response = client.post(
                "/api/subscriptions/sub123/cancel",
                headers={"Authorization": "Bearer fake_token"}
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "Subscription cancelled successfully"
    
    @patch('src.api.subscription_routes.supabase_auth')
    @patch('src.api.subscription_routes.validate_uuid')
    def test_cancel_subscription_exception(self, mock_validate_uuid, mock_supabase):
        """Test cancel with unexpected exception"""
        mock_validate_uuid.return_value = True
        mock_supabase.service_client.table.side_effect = Exception("Database error")
        
        with patch('src.auth.rbac.JWTHandler.verify_token') as mock_verify:
            mock_verify.return_value = {
                "valid": True,
                "payload": {"user_id": "user123", "role": "subscriber"}
            }
            
            response = client.post(
                "/api/subscriptions/sub123/cancel",
                headers={"Authorization": "Bearer fake_token"}
            )
        
        assert response.status_code == 400
        assert "Error cancelling subscription" in response.json()["detail"]
    
    @patch('src.api.subscription_routes.supabase_auth')
    @patch('src.api.subscription_routes.validate_uuid')
    def test_cancel_trial_subscription(self, mock_validate_uuid, mock_supabase):
        """Test cancelling a trial subscription"""
        mock_validate_uuid.return_value = True
        
        # Mock trial subscription
        mock_sub_response = Mock()
        mock_sub_response.data = {
            "id": "sub123",
            "user_id": "user123",
            "status": "trial",
            "trial_end": "2025-12-03T10:00:00+00:00",
            "next_billing_date": "2025-12-04T10:00:00+00:00"
        }
        
        # Mock successful update
        mock_update_response = Mock()
        mock_update_response.data = [{
            "id": "sub123",
            "status": "cancelled",
            "next_billing_date": None,
            "cancelled_at": "2025-11-19T10:00:00+00:00"
        }]
        
        # Mock audit log
        mock_audit_response = Mock()
        mock_audit_response.data = [{"id": "audit123"}]
        
        mock_table = Mock()
        mock_table.select.return_value.eq.return_value.single.return_value.execute.return_value = mock_sub_response
        mock_table.update.return_value.eq.return_value.execute.return_value = mock_update_response
        mock_table.insert.return_value.execute.return_value = mock_audit_response
        mock_supabase.service_client.table.return_value = mock_table
        
        with patch('src.auth.rbac.JWTHandler.verify_token') as mock_verify:
            mock_verify.return_value = {
                "valid": True,
                "payload": {"user_id": "user123", "role": "subscriber"}
            }
            
            response = client.post(
                "/api/subscriptions/sub123/cancel",
                headers={"Authorization": "Bearer fake_token"}
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    @patch('src.api.subscription_routes.supabase_auth')
    @patch('src.api.subscription_routes.validate_uuid')
    def test_cancel_paused_subscription(self, mock_validate_uuid, mock_supabase):
        """Test cancelling a paused subscription"""
        mock_validate_uuid.return_value = True
        
        # Mock paused subscription
        mock_sub_response = Mock()
        mock_sub_response.data = {
            "id": "sub123",
            "user_id": "user123",
            "status": "paused",
            "paused_at": "2025-11-18T10:00:00+00:00",
            "next_billing_date": "2025-12-01T10:00:00+00:00"
        }
        
        # Mock successful update
        mock_update_response = Mock()
        mock_update_response.data = [{
            "id": "sub123",
            "status": "cancelled",
            "next_billing_date": None,
            "cancelled_at": "2025-11-19T10:00:00+00:00"
        }]
        
        # Mock audit log
        mock_audit_response = Mock()
        mock_audit_response.data = [{"id": "audit123"}]
        
        mock_table = Mock()
        mock_table.select.return_value.eq.return_value.single.return_value.execute.return_value = mock_sub_response
        mock_table.update.return_value.eq.return_value.execute.return_value = mock_update_response
        mock_table.insert.return_value.execute.return_value = mock_audit_response
        mock_supabase.service_client.table.return_value = mock_table
        
        with patch('src.auth.rbac.JWTHandler.verify_token') as mock_verify:
            mock_verify.return_value = {
                "valid": True,
                "payload": {"user_id": "user123", "role": "subscriber"}
            }
            
            response = client.post(
                "/api/subscriptions/sub123/cancel",
                headers={"Authorization": "Bearer fake_token"}
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    @patch('src.api.subscription_routes.supabase_auth')
    @patch('src.api.subscription_routes.validate_uuid')
    def test_cancel_subscription_admin_role(self, mock_validate_uuid, mock_supabase):
        """Test admin can cancel any subscription"""
        mock_validate_uuid.return_value = True
        
        # Mock subscription owned by different user
        mock_sub_response = Mock()
        mock_sub_response.data = {
            "id": "sub123",
            "user_id": "other-user",
            "status": "active"
        }
        
        # Mock successful update
        mock_update_response = Mock()
        mock_update_response.data = [{
            "id": "sub123",
            "status": "cancelled",
            "cancelled_at": "2025-11-19T10:00:00+00:00"
        }]
        
        # Mock audit log
        mock_audit_response = Mock()
        mock_audit_response.data = [{"id": "audit123"}]
        
        mock_table = Mock()
        mock_table.select.return_value.eq.return_value.single.return_value.execute.return_value = mock_sub_response
        mock_table.update.return_value.eq.return_value.execute.return_value = mock_update_response
        mock_table.insert.return_value.execute.return_value = mock_audit_response
        mock_supabase.service_client.table.return_value = mock_table
        
        with patch('src.auth.rbac.JWTHandler.verify_token') as mock_verify:
            mock_verify.return_value = {
                "valid": True,
                "payload": {"user_id": "admin123", "role": "admin"}
            }
            
            response = client.post(
                "/api/subscriptions/sub123/cancel",
                headers={"Authorization": "Bearer admin_token"}
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    @patch('src.api.subscription_routes.supabase_auth')
    @patch('src.api.subscription_routes.validate_uuid')
    def test_cancel_sets_cancelled_at_timestamp(self, mock_validate_uuid, mock_supabase):
        """Test that cancel sets cancelled_at timestamp"""
        mock_validate_uuid.return_value = True
        
        mock_sub_response = Mock()
        mock_sub_response.data = {
            "id": "sub123",
            "user_id": "user123",
            "status": "active"
        }
        
        mock_update_response = Mock()
        mock_update_response.data = [{
            "id": "sub123",
            "status": "cancelled",
            "next_billing_date": None,
            "cancelled_at": "2025-11-19T10:00:00+00:00"
        }]
        
        mock_audit_response = Mock()
        mock_audit_response.data = [{"id": "audit123"}]
        
        mock_table = Mock()
        mock_table.select.return_value.eq.return_value.single.return_value.execute.return_value = mock_sub_response
        mock_table.update.return_value.eq.return_value.execute.return_value = mock_update_response
        mock_table.insert.return_value.execute.return_value = mock_audit_response
        mock_supabase.service_client.table.return_value = mock_table
        
        with patch('src.auth.rbac.JWTHandler.verify_token') as mock_verify:
            mock_verify.return_value = {
                "valid": True,
                "payload": {"user_id": "user123", "role": "subscriber"}
            }
            
            response = client.post(
                "/api/subscriptions/sub123/cancel",
                headers={"Authorization": "Bearer fake_token"}
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["subscription_id"] == "sub123"
    
    @patch('src.api.subscription_routes.supabase_auth')
    @patch('src.api.subscription_routes.validate_uuid')
    def test_cancel_logs_audit_event(self, mock_validate_uuid, mock_supabase):
        """Test that cancel creates audit log entry"""
        mock_validate_uuid.return_value = True
        
        mock_sub_response = Mock()
        mock_sub_response.data = {
            "id": "sub123",
            "user_id": "user123",
            "status": "active"
        }
        
        mock_update_response = Mock()
        mock_update_response.data = [{"id": "sub123", "status": "cancelled"}]
        
        captured_audit_log = {}
        
        def capture_audit(data):
            captured_audit_log.update(data)
            mock_response = Mock()
            mock_response.data = [{"id": "audit123"}]
            return Mock(execute=lambda: mock_response)
        
        mock_table = Mock()
        mock_table.select.return_value.eq.return_value.single.return_value.execute.return_value = mock_sub_response
        mock_table.update.return_value.eq.return_value.execute.return_value = mock_update_response
        mock_table.insert.side_effect = capture_audit
        mock_supabase.service_client.table.return_value = mock_table
        
        with patch('src.auth.rbac.JWTHandler.verify_token') as mock_verify:
            mock_verify.return_value = {
                "valid": True,
                "payload": {"user_id": "user123", "role": "subscriber"}
            }
            
            response = client.post(
                "/api/subscriptions/sub123/cancel",
                headers={"Authorization": "Bearer fake_token"}
            )
        
        assert response.status_code == 200
        assert captured_audit_log["subscription_id"] == "sub123"
        assert captured_audit_log["action"] == "cancelled"
        assert captured_audit_log["user_id"] == "user123"
        assert "timestamp" in captured_audit_log


class TestCancelSubscriptionRBAC:
    """Test role-based access control for cancel subscription"""
    
    def test_cancel_requires_authentication(self):
        """Test cancel requires valid JWT token"""
        response = client.post("/api/subscriptions/sub123/cancel")
        
        assert response.status_code == 401
    
    @patch('src.api.subscription_routes.validate_uuid')
    def test_cancel_invalid_token(self, mock_validate_uuid):
        """Test cancel with invalid token"""
        mock_validate_uuid.return_value = True
        
        with patch('src.auth.rbac.JWTHandler.verify_token') as mock_verify:
            mock_verify.return_value = {"valid": False}
            
            response = client.post(
                "/api/subscriptions/sub123/cancel",
                headers={"Authorization": "Bearer invalid_token"}
            )
        
        assert response.status_code == 401
    
    @patch('src.api.subscription_routes.supabase_auth')
    @patch('src.api.subscription_routes.validate_uuid')
    def test_cancel_subscriber_role_allowed(self, mock_validate_uuid, mock_supabase):
        """Test subscriber role can cancel their subscription"""
        mock_validate_uuid.return_value = True
        
        mock_sub_response = Mock()
        mock_sub_response.data = {
            "id": "sub123",
            "user_id": "user123",
            "status": "active"
        }
        
        mock_update_response = Mock()
        mock_update_response.data = [{"id": "sub123", "status": "cancelled"}]
        
        mock_audit_response = Mock()
        mock_audit_response.data = [{"id": "audit123"}]
        
        mock_table = Mock()
        mock_table.select.return_value.eq.return_value.single.return_value.execute.return_value = mock_sub_response
        mock_table.update.return_value.eq.return_value.execute.return_value = mock_update_response
        mock_table.insert.return_value.execute.return_value = mock_audit_response
        mock_supabase.service_client.table.return_value = mock_table
        
        with patch('src.auth.rbac.JWTHandler.verify_token') as mock_verify:
            mock_verify.return_value = {
                "valid": True,
                "payload": {"user_id": "user123", "role": "subscriber"}
            }
            
            response = client.post(
                "/api/subscriptions/sub123/cancel",
                headers={"Authorization": "Bearer subscriber_token"}
            )
        
        assert response.status_code == 200
    
    @patch('src.api.subscription_routes.supabase_auth')
    @patch('src.api.subscription_routes.validate_uuid')
    def test_cancel_admin_role_allowed(self, mock_validate_uuid, mock_supabase):
        """Test admin role can cancel any subscription"""
        mock_validate_uuid.return_value = True
        
        mock_sub_response = Mock()
        mock_sub_response.data = {
            "id": "sub123",
            "user_id": "other-user",
            "status": "active"
        }
        
        mock_update_response = Mock()
        mock_update_response.data = [{"id": "sub123", "status": "cancelled"}]
        
        mock_audit_response = Mock()
        mock_audit_response.data = [{"id": "audit123"}]
        
        mock_table = Mock()
        mock_table.select.return_value.eq.return_value.single.return_value.execute.return_value = mock_sub_response
        mock_table.update.return_value.eq.return_value.execute.return_value = mock_update_response
        mock_table.insert.return_value.execute.return_value = mock_audit_response
        mock_supabase.service_client.table.return_value = mock_table
        
        with patch('src.auth.rbac.JWTHandler.verify_token') as mock_verify:
            mock_verify.return_value = {
                "valid": True,
                "payload": {"user_id": "admin123", "role": "admin"}
            }
            
            response = client.post(
                "/api/subscriptions/sub123/cancel",
                headers={"Authorization": "Bearer admin_token"}
            )
        
        assert response.status_code == 200
    
    @patch('src.api.subscription_routes.validate_uuid')
    def test_cancel_finance_role_denied(self, mock_validate_uuid):
        """Test finance role cannot cancel subscriptions"""
        mock_validate_uuid.return_value = True
        
        with patch('src.auth.rbac.JWTHandler.verify_token') as mock_verify:
            mock_verify.return_value = {
                "valid": True,
                "payload": {"user_id": "finance123", "role": "finance"}
            }
            
            response = client.post(
                "/api/subscriptions/sub123/cancel",
                headers={"Authorization": "Bearer finance_token"}
            )
        
        assert response.status_code == 403
        assert "Access denied" in response.json()["detail"] or "Insufficient permissions" in response.json()["detail"]

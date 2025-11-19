"""
Unit tests for pause and resume subscription endpoints
Story SIM-101: Subscription Pause/Resume Functionality
Target: >85% code coverage
"""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


class TestPauseSubscriptionEndpoint:
    """Test suite for POST /api/subscriptions/{subscription_id}/pause endpoint"""
    
    @patch('src.api.subscription_routes.supabase_auth')
    @patch('src.api.subscription_routes.validate_uuid')
    def test_pause_subscription_success(self, mock_validate_uuid, mock_supabase):
        """Test successful subscription pause (SIM-101)"""
        mock_validate_uuid.return_value = True
        
        # Mock successful update
        mock_response = Mock()
        mock_response.data = [{
            "id": "sub123",
            "status": "paused",
            "paused_at": "2025-11-19T10:00:00+00:00"
        }]
        
        mock_table = Mock()
        mock_table.update.return_value.eq.return_value.execute.return_value = mock_response
        mock_supabase.service_client.table.return_value = mock_table
        
        with patch('src.auth.rbac.JWTHandler.verify_token') as mock_verify:
            mock_verify.return_value = {
                "valid": True,
                "payload": {"user_id": "user123", "role": "subscriber"}
            }
            
            response = client.post(
                "/api/subscriptions/sub123/pause",
                headers={"Authorization": "Bearer fake_token"}
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "Subscription paused successfully"
        assert data["subscription_id"] == "sub123"
        assert "paused_at" in data
    
    @patch('src.api.subscription_routes.validate_uuid')
    def test_pause_subscription_invalid_uuid(self, mock_validate_uuid):
        """Test pause with invalid subscription ID format"""
        mock_validate_uuid.return_value = False
        
        with patch('src.auth.rbac.JWTHandler.verify_token') as mock_verify:
            mock_verify.return_value = {
                "valid": True,
                "payload": {"user_id": "user123", "role": "subscriber"}
            }
            
            response = client.post(
                "/api/subscriptions/invalid-id/pause",
                headers={"Authorization": "Bearer fake_token"}
            )
        
        assert response.status_code == 400
        assert "Invalid subscription_id format" in response.json()["detail"]
    
    @patch('src.api.subscription_routes.supabase_auth')
    @patch('src.api.subscription_routes.validate_uuid')
    def test_pause_subscription_not_found(self, mock_validate_uuid, mock_supabase):
        """Test pause non-existent subscription"""
        mock_validate_uuid.return_value = True
        
        # Mock empty response
        mock_response = Mock()
        mock_response.data = None
        
        mock_table = Mock()
        mock_table.update.return_value.eq.return_value.execute.return_value = mock_response
        mock_supabase.service_client.table.return_value = mock_table
        
        with patch('src.auth.rbac.JWTHandler.verify_token') as mock_verify:
            mock_verify.return_value = {
                "valid": True,
                "payload": {"user_id": "user123", "role": "subscriber"}
            }
            
            response = client.post(
                "/api/subscriptions/sub123/pause",
                headers={"Authorization": "Bearer fake_token"}
            )
        
        assert response.status_code == 404
        assert "Subscription not found" in response.json()["detail"]
    
    def test_pause_subscription_missing_auth(self):
        """Test pause without authorization"""
        response = client.post("/api/subscriptions/sub123/pause")
        
        assert response.status_code == 401
        assert "Missing authorization header" in response.json()["detail"]
    
    @patch('src.api.subscription_routes.supabase_auth')
    @patch('src.api.subscription_routes.validate_uuid')
    def test_pause_subscription_exception(self, mock_validate_uuid, mock_supabase):
        """Test pause with unexpected exception"""
        mock_validate_uuid.return_value = True
        mock_supabase.service_client.table.side_effect = Exception("Database error")
        
        with patch('src.auth.rbac.JWTHandler.verify_token') as mock_verify:
            mock_verify.return_value = {
                "valid": True,
                "payload": {"user_id": "user123", "role": "subscriber"}
            }
            
            response = client.post(
                "/api/subscriptions/sub123/pause",
                headers={"Authorization": "Bearer fake_token"}
            )
        
        assert response.status_code == 400
        assert "Error pausing subscription" in response.json()["detail"]


class TestResumeSubscriptionEndpoint:
    """Test suite for POST /api/subscriptions/{subscription_id}/resume endpoint"""
    
    @patch('src.api.subscription_routes.supabase_auth')
    @patch('src.api.subscription_routes.validate_uuid')
    def test_resume_subscription_success_active(self, mock_validate_uuid, mock_supabase):
        """Test successful resume of active (non-trial) subscription"""
        mock_validate_uuid.return_value = True
        
        # Mock subscription fetch
        mock_sub_response = Mock()
        mock_sub_response.data = {
            "id": "sub123",
            "status": "paused",
            "paused_at": "2025-11-19T10:00:00+00:00",
            "trial_end": None,
            "next_billing_date": "2025-12-01T10:00:00+00:00"
        }
        
        # Mock update response
        mock_update_response = Mock()
        mock_update_response.data = [{"id": "sub123", "status": "active"}]
        
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
                "/api/subscriptions/sub123/resume",
                headers={"Authorization": "Bearer fake_token"}
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "Subscription resumed successfully"
        assert data["subscription_id"] == "sub123"
        assert "next_billing_date" in data
    
    @patch('src.api.subscription_routes.supabase_auth')
    @patch('src.api.subscription_routes.validate_uuid')
    def test_resume_subscription_success_trial(self, mock_validate_uuid, mock_supabase):
        """Test successful resume of trial subscription with trial_end extension"""
        mock_validate_uuid.return_value = True
        
        # Mock trial subscription fetch
        mock_sub_response = Mock()
        mock_sub_response.data = {
            "id": "sub123",
            "status": "paused",
            "paused_at": "2025-11-19T10:00:00+00:00",
            "trial_end": "2025-12-03T10:00:00+00:00",
            "next_billing_date": "2025-12-04T10:00:00+00:00"
        }
        
        # Mock update response
        mock_update_response = Mock()
        mock_update_response.data = [{"id": "sub123", "status": "active"}]
        
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
                "/api/subscriptions/sub123/resume",
                headers={"Authorization": "Bearer fake_token"}
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "trial_end" in data
        assert "next_billing_date" in data
    
    @patch('src.api.subscription_routes.validate_uuid')
    def test_resume_subscription_invalid_uuid(self, mock_validate_uuid):
        """Test resume with invalid subscription ID format"""
        mock_validate_uuid.return_value = False
        
        with patch('src.auth.rbac.JWTHandler.verify_token') as mock_verify:
            mock_verify.return_value = {
                "valid": True,
                "payload": {"user_id": "user123", "role": "subscriber"}
            }
            
            response = client.post(
                "/api/subscriptions/invalid-id/resume",
                headers={"Authorization": "Bearer fake_token"}
            )
        
        assert response.status_code == 400
        assert "Invalid subscription_id format" in response.json()["detail"]
    
    @patch('src.api.subscription_routes.supabase_auth')
    @patch('src.api.subscription_routes.validate_uuid')
    def test_resume_subscription_not_found(self, mock_validate_uuid, mock_supabase):
        """Test resume non-existent subscription"""
        mock_validate_uuid.return_value = True
        
        # Mock empty response
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
                "/api/subscriptions/sub123/resume",
                headers={"Authorization": "Bearer fake_token"}
            )
        
        assert response.status_code == 404
        assert "Subscription not found" in response.json()["detail"]
    
    @patch('src.api.subscription_routes.supabase_auth')
    @patch('src.api.subscription_routes.validate_uuid')
    def test_resume_subscription_not_paused(self, mock_validate_uuid, mock_supabase):
        """Test resume subscription that is not paused"""
        mock_validate_uuid.return_value = True
        
        # Mock active subscription
        mock_sub_response = Mock()
        mock_sub_response.data = {
            "id": "sub123",
            "status": "active",  # Not paused
            "paused_at": None
        }
        
        mock_table = Mock()
        mock_table.select.return_value.eq.return_value.single.return_value.execute.return_value = mock_sub_response
        mock_supabase.service_client.table.return_value = mock_table
        
        with patch('src.auth.rbac.JWTHandler.verify_token') as mock_verify:
            mock_verify.return_value = {
                "valid": True,
                "payload": {"user_id": "user123", "role": "subscriber"}
            }
            
            response = client.post(
                "/api/subscriptions/sub123/resume",
                headers={"Authorization": "Bearer fake_token"}
            )
        
        assert response.status_code == 400
        assert "Subscription is not paused" in response.json()["detail"]
    
    @patch('src.api.subscription_routes.supabase_auth')
    @patch('src.api.subscription_routes.validate_uuid')
    def test_resume_subscription_missing_paused_at(self, mock_validate_uuid, mock_supabase):
        """Test resume subscription without paused_at timestamp"""
        mock_validate_uuid.return_value = True
        
        # Mock subscription without paused_at
        mock_sub_response = Mock()
        mock_sub_response.data = {
            "id": "sub123",
            "status": "paused",
            "paused_at": None  # Missing timestamp
        }
        
        mock_table = Mock()
        mock_table.select.return_value.eq.return_value.single.return_value.execute.return_value = mock_sub_response
        mock_supabase.service_client.table.return_value = mock_table
        
        with patch('src.auth.rbac.JWTHandler.verify_token') as mock_verify:
            mock_verify.return_value = {
                "valid": True,
                "payload": {"user_id": "user123", "role": "subscriber"}
            }
            
            response = client.post(
                "/api/subscriptions/sub123/resume",
                headers={"Authorization": "Bearer fake_token"}
            )
        
        assert response.status_code == 400
        assert "Paused at timestamp not found" in response.json()["detail"]
    
    @patch('src.api.subscription_routes.supabase_auth')
    @patch('src.api.subscription_routes.validate_uuid')
    def test_resume_subscription_no_billing_date(self, mock_validate_uuid, mock_supabase):
        """Test resume subscription without next_billing_date (fallback to 30 days)"""
        mock_validate_uuid.return_value = True
        
        # Mock subscription without billing date
        mock_sub_response = Mock()
        mock_sub_response.data = {
            "id": "sub123",
            "status": "paused",
            "paused_at": "2025-11-19T10:00:00+00:00",
            "trial_end": None,
            "next_billing_date": None  # No billing date
        }
        
        # Mock update response
        mock_update_response = Mock()
        mock_update_response.data = [{"id": "sub123", "status": "active"}]
        
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
                "/api/subscriptions/sub123/resume",
                headers={"Authorization": "Bearer fake_token"}
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "next_billing_date" in data
    
    def test_resume_subscription_missing_auth(self):
        """Test resume without authorization"""
        response = client.post("/api/subscriptions/sub123/resume")
        
        assert response.status_code == 401
        assert "Missing authorization header" in response.json()["detail"]
    
    @patch('src.api.subscription_routes.supabase_auth')
    @patch('src.api.subscription_routes.validate_uuid')
    def test_resume_subscription_exception(self, mock_validate_uuid, mock_supabase):
        """Test resume with unexpected exception"""
        mock_validate_uuid.return_value = True
        mock_supabase.service_client.table.side_effect = Exception("Database error")
        
        with patch('src.auth.rbac.JWTHandler.verify_token') as mock_verify:
            mock_verify.return_value = {
                "valid": True,
                "payload": {"user_id": "user123", "role": "subscriber"}
            }
            
            response = client.post(
                "/api/subscriptions/sub123/resume",
                headers={"Authorization": "Bearer fake_token"}
            )
        
        assert response.status_code == 400
        assert "Error resuming subscription" in response.json()["detail"]


class TestPauseResumeIntegration:
    """Integration tests for pause and resume workflow"""
    
    @patch('src.api.subscription_routes.supabase_auth')
    @patch('src.api.subscription_routes.validate_uuid')
    def test_pause_then_resume_workflow(self, mock_validate_uuid, mock_supabase):
        """Test complete pause and resume workflow"""
        mock_validate_uuid.return_value = True
        
        # Mock pause response
        pause_time = datetime.now(timezone.utc)
        mock_pause_response = Mock()
        mock_pause_response.data = [{
            "id": "sub123",
            "status": "paused",
            "paused_at": pause_time.isoformat()
        }]
        
        # Mock subscription fetch for resume
        mock_sub_response = Mock()
        mock_sub_response.data = {
            "id": "sub123",
            "status": "paused",
            "paused_at": pause_time.isoformat(),
            "trial_end": None,
            "next_billing_date": "2025-12-01T10:00:00+00:00"
        }
        
        # Mock resume response
        mock_resume_response = Mock()
        mock_resume_response.data = [{"id": "sub123", "status": "active"}]
        
        mock_table = Mock()
        # First call for pause
        mock_table.update.return_value.eq.return_value.execute.return_value = mock_pause_response
        # Second call for resume fetch
        mock_table.select.return_value.eq.return_value.single.return_value.execute.return_value = mock_sub_response
        mock_supabase.service_client.table.return_value = mock_table
        
        with patch('src.auth.rbac.JWTHandler.verify_token') as mock_verify:
            mock_verify.return_value = {
                "valid": True,
                "payload": {"user_id": "user123", "role": "subscriber"}
            }
            
            # Pause subscription
            pause_response = client.post(
                "/api/subscriptions/sub123/pause",
                headers={"Authorization": "Bearer fake_token"}
            )
            
            assert pause_response.status_code == 200
            assert pause_response.json()["success"] is True
            
            # Update mock for resume update call
            mock_table.update.return_value.eq.return_value.execute.return_value = mock_resume_response
            
            # Resume subscription
            resume_response = client.post(
                "/api/subscriptions/sub123/resume",
                headers={"Authorization": "Bearer fake_token"}
            )
            
            assert resume_response.status_code == 200
            assert resume_response.json()["success"] is True
    
    @patch('src.api.subscription_routes.supabase_auth')
    @patch('src.api.subscription_routes.validate_uuid')
    def test_resume_extends_trial_correctly(self, mock_validate_uuid, mock_supabase):
        """Test that resume correctly extends trial_end by paused duration"""
        mock_validate_uuid.return_value = True
        
        # 2 day pause
        paused_at = datetime(2025, 11, 19, 10, 0, 0, tzinfo=timezone.utc)
        trial_end_original = datetime(2025, 12, 3, 10, 0, 0, tzinfo=timezone.utc)
        
        mock_sub_response = Mock()
        mock_sub_response.data = {
            "id": "sub123",
            "status": "paused",
            "paused_at": paused_at.isoformat(),
            "trial_end": trial_end_original.isoformat(),
            "next_billing_date": (trial_end_original + timedelta(days=1)).isoformat()
        }
        
        mock_update_response = Mock()
        mock_update_response.data = [{"id": "sub123", "status": "active"}]
        
        mock_table = Mock()
        mock_table.select.return_value.eq.return_value.single.return_value.execute.return_value = mock_sub_response
        mock_table.update.return_value.eq.return_value.execute.return_value = mock_update_response
        mock_supabase.service_client.table.return_value = mock_table
        
        with patch('src.auth.rbac.JWTHandler.verify_token') as mock_verify:
            mock_verify.return_value = {
                "valid": True,
                "payload": {"user_id": "user123", "role": "subscriber"}
            }
            
            with patch('src.api.subscription_routes.datetime') as mock_datetime:
                # Mock resume happens 2 days after pause
                resume_time = paused_at + timedelta(days=2)
                mock_datetime.now.return_value = resume_time
                mock_datetime.fromisoformat = datetime.fromisoformat
                
                response = client.post(
                    "/api/subscriptions/sub123/resume",
                    headers={"Authorization": "Bearer fake_token"}
                )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify trial_end and next_billing_date are returned
        assert "trial_end" in data
        assert "next_billing_date" in data

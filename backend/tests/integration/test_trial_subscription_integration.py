"""
Integration tests for trial subscription activation
Story SIM-89
"""
import pytest
from unittest.mock import patch, Mock
from fastapi.testclient import TestClient
from datetime import datetime
from src.main import app

client = TestClient(app)


@pytest.fixture
def mock_auth_token():
    """Mock authentication token"""
    with patch('src.auth.rbac.JWTHandler.verify_token') as mock_verify:
        mock_verify.return_value = {
            "valid": True,
            "payload": {
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "role": "admin"
            }
        }
        yield "fake_token_12345"


@pytest.fixture
def mock_supabase():
    """Mock Supabase client"""
    with patch('src.api.subscription_routes.supabase_auth') as mock:
        yield mock


def test_activate_trial_success(mock_auth_token, mock_supabase):
    """Test successful trial activation (SIM-94)"""
    # Mock UUID validation
    with patch('src.api.subscription_routes.validate_uuid') as mock_validate:
        mock_validate.return_value = True
        
        # Mock plan exists
        mock_plan_response = Mock()
        mock_plan_response.data = {
            "id": "plan123",
            "name": "Premium",
            "is_active": True
        }
        
        # Mock no existing subscriptions
        mock_existing_response = Mock()
        mock_existing_response.data = []
        
        # Mock successful insert
        mock_insert_response = Mock()
        mock_insert_response.data = [{
            "id": "650e8400-e29b-41d4-a716-446655440000",
            "user_id": "550e8400-e29b-41d4-a716-446655440000",
            "plan_id": "plan123",
            "status": "trial",
            "trial_start": "2025-11-19T09:00:00+00:00",
            "trial_end": "2025-12-03T09:00:00+00:00",
            "next_billing_date": "2025-12-04T09:00:00+00:00",
            "created_at": "2025-11-19T09:00:00+00:00"
        }]
        
        mock_table = Mock()
        mock_table.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.return_value = mock_plan_response
        mock_table.select.return_value.eq.return_value.eq.return_value.execute.return_value = mock_existing_response
        mock_table.insert.return_value.execute.return_value = mock_insert_response
        mock_supabase.service_client.table.return_value = mock_table
        
        response = client.post(
            "/api/subscriptions/trial",
            json={"plan_id": "plan123"},
            headers={"Authorization": f"Bearer {mock_auth_token}"}
        )
        
        assert response.status_code == 201
        data = response.json()
        
        # Verify trial fields (SIM-93)
        assert data["status"] == "trial"
        assert data["plan_id"] == "plan123"
        assert "trial_start" in data
        assert "trial_end" in data
        assert "next_billing_date" in data
        
        # Verify 14-day trial duration (SIM-92)
        trial_start = datetime.fromisoformat(data["trial_start"].replace('Z', '+00:00'))
        trial_end = datetime.fromisoformat(data["trial_end"].replace('Z', '+00:00'))
        duration = (trial_end - trial_start).days
        assert duration == 14
        
        # Verify next_billing_date is 1 day after trial_end
        next_billing = datetime.fromisoformat(data["next_billing_date"].replace('Z', '+00:00'))
        billing_duration = (next_billing - trial_end).days
        assert billing_duration == 1


def test_activate_trial_invalid_plan(mock_auth_token, mock_supabase):
    """Test trial activation with invalid plan"""
    # Mock plan not found
    mock_plan_response = Mock()
    mock_plan_response.data = None
    
    mock_table = Mock()
    mock_table.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.return_value = mock_plan_response
    mock_supabase.service_client.table.return_value = mock_table
    
    response = client.post(
        "/api/subscriptions/trial",
        json={"plan_id": "00000000-0000-0000-0000-000000000000"},
        headers={"Authorization": f"Bearer {mock_auth_token}"}
    )
    
    assert response.status_code == 404


def test_activate_trial_without_authentication():
    """Test trial activation without token"""
    response = client.post(
        "/api/subscriptions/trial",
        json={"plan_id": "550e8400-e29b-41d4-a716-446655440000"}
    )
    
    assert response.status_code == 401


def test_activate_trial_duplicate_subscription(mock_auth_token, mock_supabase):
    """Test cannot create duplicate trial for same plan"""
    with patch('src.api.subscription_routes.validate_uuid') as mock_validate:
        mock_validate.return_value = True
        
        # Mock plan exists
        mock_plan_response = Mock()
        mock_plan_response.data = {
            "id": "plan123",
            "is_active": True
        }
        
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
        
        response = client.post(
            "/api/subscriptions/trial",
            json={"plan_id": "plan123"},
            headers={"Authorization": f"Bearer {mock_auth_token}"}
        )
        
        assert response.status_code == 400
        assert "already has active/trial subscription" in response.json()["detail"]

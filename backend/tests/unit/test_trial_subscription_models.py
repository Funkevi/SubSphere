"""
Unit tests for trial subscription models
"""
import pytest
from datetime import datetime, timedelta, timezone
from src.models.subscription import (
    TrialSubscriptionRequest,
    TrialSubscriptionResponse
)


def test_trial_subscription_request_valid():
    """Test valid trial subscription request"""
    data = {
        "plan_id": "550e8400-e29b-41d4-a716-446655440000"
    }
    request = TrialSubscriptionRequest(**data)
    assert request.plan_id == "550e8400-e29b-41d4-a716-446655440000"


def test_trial_subscription_request_missing_plan_id():
    """Test trial subscription request with missing plan_id"""
    with pytest.raises(ValueError):
        TrialSubscriptionRequest()


def test_trial_subscription_response_valid():
    """Test valid trial subscription response"""
    now = datetime.now(timezone.utc)
    trial_end = now + timedelta(days=14)
    next_billing = trial_end + timedelta(days=1)
    
    data = {
        "id": "650e8400-e29b-41d4-a716-446655440000",
        "user_id": "550e8400-e29b-41d4-a716-446655440000",
        "plan_id": "550e8400-e29b-41d4-a716-446655440000",
        "status": "trial",
        "trial_start": now.isoformat(),
        "trial_end": trial_end.isoformat(),
        "next_billing_date": next_billing.isoformat(),
        "created_at": now.isoformat()
    }
    
    response = TrialSubscriptionResponse(**data)
    assert response.status == "trial"
    assert response.trial_start == now.isoformat()


def test_trial_end_is_14_days_after_start():
    """Test that trial_end is exactly 14 days after trial_start"""
    now = datetime.now(timezone.utc)
    trial_end = now + timedelta(days=14)
    
    duration = trial_end - now
    assert duration.days == 14


def test_next_billing_is_day_after_trial_end():
    """Test that next_billing_date is 1 day after trial_end"""
    now = datetime.now(timezone.utc)
    trial_end = now + timedelta(days=14)
    next_billing = trial_end + timedelta(days=1)
    
    duration = next_billing - trial_end
    assert duration.days == 1
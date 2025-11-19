"""
Subscription models for Trial Period Activation
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class TrialSubscriptionRequest(BaseModel):
    """Request model for activating trial subscription"""
    plan_id: str = Field(..., description="Subscription plan ID (UUID)")
    
    class Config:
        examples = {
            "plan_id": "550e8400-e29b-41d4-a716-446655440000"
        }


class TrialSubscriptionResponse(BaseModel):
    """Response model for trial subscription"""
    id: str
    user_id: str
    plan_id: str
    status: str  # 'trial'
    trial_start: str  # ISO format datetime
    trial_end: str    # ISO format datetime
    next_billing_date: str  # ISO format datetime
    created_at: str
    
    class Config:
        from_attributes = True
        examples = {
            "id": "650e8400-e29b-41d4-a716-446655440000",
            "user_id": "550e8400-e29b-41d4-a716-446655440000",
            "plan_id": "550e8400-e29b-41d4-a716-446655440000",
            "status": "trial",
            "trial_start": "2025-11-19T09:00:00+00:00",
            "trial_end": "2025-12-03T09:00:00+00:00",
            "next_billing_date": "2025-12-04T09:00:00+00:00",
            "created_at": "2025-11-19T09:00:00+00:00"
        }


class SubscriptionResponse(BaseModel):
    """Detailed subscription response"""
    id: str
    user_id: str
    plan_id: str
    status: str
    trial_start: Optional[str]
    trial_end: Optional[str]
    next_billing_date: Optional[str]
    paused_at: Optional[str]
    resumed_at: Optional[str]
    cancelled_at: Optional[str]
    created_at: str
    updated_at: Optional[str]
    
    class Config:
        from_attributes = True


class SubscriptionListResponse(BaseModel):
    """List of subscriptions"""
    subscriptions: List[SubscriptionResponse]
    total: int
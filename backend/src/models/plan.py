"""
Subscription Plan Models
Pydantic models for plan creation, updates, and responses
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class PlanFeature(BaseModel):
    """Individual feature of a subscription plan"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None


class CreatePlanRequest(BaseModel):
    """Request model for creating a new subscription plan"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    price: float = Field(..., gt=0, description="Price must be greater than 0")
    duration_days: int = Field(..., gt=0, description="Duration in days, must be positive")
    features: List[PlanFeature] = []


class UpdatePlanRequest(BaseModel):
    """Request model for updating an existing plan"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    duration_days: Optional[int] = Field(None, gt=0)
    features: Optional[List[PlanFeature]] = None
    is_active: Optional[bool] = None


class PlanResponse(BaseModel):
    """Response model for subscription plan"""
    id: str
    name: str
    description: Optional[str]
    price: float
    duration_days: int
    features: List[dict]  # Changed from List[PlanFeature] for DB compatibility
    is_active: bool
    created_at: str  # Changed from datetime for JSON serialization

    class Config:
        from_attributes = True  # For Pydantic v2 compatibility

"""
Payment Models
Pydantic models for payment operations
"""
from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime


class CreatePaymentRequest(BaseModel):
    """Request model for creating a payment"""
    subscription_id: str = Field(..., description="Subscription UUID")
    amount: float = Field(..., gt=0, description="Payment amount must be positive")
    should_succeed: bool = Field(True, description="Mock payment success/failure flag for testing")


class PaymentResponse(BaseModel):
    """Response model for payment"""
    id: str
    subscription_id: str
    amount: float
    status: Literal["pending", "success", "failed"]
    transaction_id: Optional[str] = None
    payment_method: str
    created_at: str

    class Config:
        from_attributes = True

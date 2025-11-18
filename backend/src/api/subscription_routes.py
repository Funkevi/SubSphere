"""
Subscription API Routes
Handles subscription CRUD operations
"""
from typing import Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Header, Body
from pydantic import BaseModel
from src.auth.supabase_auth import supabase_auth
from src.auth.rbac import require_role
from uuid import uuid4

router = APIRouter(prefix="/api/subscriptions", tags=["subscriptions"])


class CreateSubscriptionRequest(BaseModel):
    user_id: str
    plan_id: str
    status: str = "active"


@router.post("", status_code=201)
@require_role(["admin", "subscriber"])
async def create_subscription(
    subscription: CreateSubscriptionRequest = Body(..., embed=True),
    authorization: Optional[str] = Header(None),
    token: str = None,
    current_user: dict = None
):
    """
    Create a new subscription
    
    - Requires authentication
    - Creates subscription record in database
    - Sets expiry based on plan billing cycle
    """
    try:
        # Get plan details to determine duration
        plan_response = supabase_auth.service_client.table("subscription_plans").select(
            "duration_days"
        ).eq("id", subscription.plan_id).single().execute()
        
        if not plan_response.data:
            raise HTTPException(status_code=404, detail="Plan not found")
        
        # Calculate expiry date based on plan duration
        duration_days = plan_response.data.get("duration_days", 30)
        current_period_start = datetime.utcnow()
        expires_at = current_period_start + timedelta(days=duration_days)
        
        response = supabase_auth.service_client.table("subscriptions").insert({
            "user_id": subscription.user_id,
            "plan_id": subscription.plan_id,
            "status": subscription.status,
            "started_at": current_period_start.isoformat(),
            "expires_at": expires_at.isoformat()
        }).execute()

        if not response.data:
            raise HTTPException(status_code=400, detail="Failed to create subscription")

        return response.data[0]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creating subscription: {str(e)}")


@router.get("/user/{user_id}")
@require_role(["admin", "subscriber"])
async def get_user_subscriptions(
    user_id: str,
    authorization: Optional[str] = Header(None),
    token: str = None,
    current_user: dict = None
):
    """
    Get all subscriptions for a user
    
    - Requires authentication
    - Returns list of subscriptions with plan details
    """
    try:
        response = supabase_auth.service_client.table("subscriptions").select(
            "*, subscription_plans(*)"
        ).eq("user_id", user_id).order("created_at", desc=True).execute()

        return response.data

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error fetching subscriptions: {str(e)}")


@router.get("/{subscription_id}")
@require_role(["admin", "subscriber"])
async def get_subscription(
    subscription_id: str,
    authorization: Optional[str] = Header(None),
    token: str = None,
    current_user: dict = None
):
    """
    Get subscription by ID
    
    - Requires authentication
    - Returns subscription with plan details
    """
    try:
        response = supabase_auth.service_client.table("subscriptions").select(
            "*, subscription_plans(*)"
        ).eq("id", subscription_id).single().execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Subscription not found")

        return response.data

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=404, detail="Subscription not found")


@router.put("/{subscription_id}")
@require_role(["admin", "subscriber"])
async def update_subscription(
    subscription_id: str,
    subscription: CreateSubscriptionRequest = Body(..., embed=True),
    authorization: Optional[str] = Header(None),
    token: str = None,
    current_user: dict = None
):
    """
    Update subscription
    
    - Requires authentication
    - Updates subscription status or plan
    """
    try:
        response = supabase_auth.service_client.table("subscriptions").update({
            "plan_id": subscription.plan_id,
            "status": subscription.status
        }).eq("id", subscription_id).execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Subscription not found")

        return response.data[0]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error updating subscription: {str(e)}")

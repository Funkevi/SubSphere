"""
Subscription management API routes
Story SIM-89: Trial Period Activation
"""
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import APIRouter, HTTPException, Header, Body, Query
from pydantic import BaseModel
from src.models.subscription import (
    TrialSubscriptionRequest,
    TrialSubscriptionResponse,
    SubscriptionResponse,
    SubscriptionListResponse
)
from src.auth.supabase_auth import supabase_auth
from src.auth.rbac import require_role
from src.utils.validators import validate_uuid

router = APIRouter(prefix="/api/subscriptions", tags=["subscriptions"])


class CreateSubscriptionRequest(BaseModel):
    user_id: str
    plan_id: str
    status: str = "active"


@router.post("/trial", response_model=TrialSubscriptionResponse, status_code=201)
@require_role(["subscriber", "admin"])
async def activate_trial(
    plan_id: str = Body(..., embed=True),
    authorization: Optional[str] = Header(None),
    token: str = None,
    current_user: dict = None
):
    """
    SIM-89: Activate 14-day trial period for subscription
    
    Creates subscription with:
    - status='trial'
    - trial_start = today
    - trial_end = today + 14 days
    - next_billing_date = trial_end + 1 day
    
    **Request Body:**
    ```json
    {
        "plan_id": "550e8400-e29b-41d4-a716-446655440000"
    }
    ```
    
    **Response (201):**
    ```json
    {
        "id": "650e8400-e29b-41d4-a716-446655440000",
        "user_id": "550e8400-e29b-41d4-a716-446655440000",
        "plan_id": "550e8400-e29b-41d4-a716-446655440000",
        "status": "trial",
        "trial_start": "2025-11-19T09:00:00+00:00",
        "trial_end": "2025-12-03T09:00:00+00:00",
        "next_billing_date": "2025-12-04T09:00:00+00:00",
        "created_at": "2025-11-19T09:00:00+00:00"
    }
    ```
    """
    try:
        # Validate plan_id format
        if not validate_uuid(plan_id):
            raise HTTPException(status_code=400, detail="Invalid plan_id format")
        
        # Get plan details to verify it exists
        plan_response = supabase_auth.service_client.table("subscription_plans").select(
            "*"
        ).eq("id", plan_id).eq("is_active", True).single().execute()
        
        if not plan_response.data:
            raise HTTPException(status_code=404, detail="Plan not found or inactive")
        
        plan = plan_response.data
        
        # Check if user already has active trial or subscription for this plan
        existing = supabase_auth.service_client.table("subscriptions").select(
            "*"
        ).eq("user_id", current_user["user_id"]).eq("plan_id", plan_id).execute()
        
        if existing.data and len(existing.data) > 0:
            sub = existing.data[0]
            if sub["status"] in ["trial", "active"]:
                raise HTTPException(
                    status_code=400,
                    detail="User already has active/trial subscription for this plan"
                )
        
        # Calculate trial dates (SIM-92)
        trial_start = datetime.now(timezone.utc)
        trial_end = trial_start + timedelta(days=14)  # 14-day trial period
        next_billing_date = trial_end + timedelta(days=1)  # Billing starts day after trial ends
        
        # Create subscription record (SIM-93)
        subscription_data = {
            "user_id": current_user["user_id"],
            "plan_id": plan_id,
            "status": "trial",  # SIM-93: Set status to 'trial'
            "trial_start": trial_start.isoformat(),
            "trial_end": trial_end.isoformat(),  # SIM-92: Calculate expiry
            "next_billing_date": next_billing_date.isoformat(),
            "started_at": trial_start.isoformat(),
            "expires_at": trial_end.isoformat()
        }
        
        # Insert into database
        response = supabase_auth.service_client.table("subscriptions").insert(
            subscription_data
        ).execute()
        
        if not response.data or len(response.data) == 0:
            raise HTTPException(status_code=400, detail="Failed to create trial subscription")
        
        subscription = response.data[0]
        
        return TrialSubscriptionResponse(
            id=subscription["id"],
            user_id=subscription["user_id"],
            plan_id=subscription["plan_id"],
            status=subscription["status"],
            trial_start=subscription["trial_start"],
            trial_end=subscription["trial_end"],
            next_billing_date=subscription["next_billing_date"],
            created_at=subscription["created_at"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error creating trial subscription: {str(e)}"
        ) from e


@router.get("/user/{user_id}")
@require_role(["admin", "subscriber"])
async def get_user_subscriptions(  # pylint: disable=unused-argument
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
        raise HTTPException(status_code=400, detail=f"Error fetching subscriptions: {str(e)}") from e


@router.get("/{subscription_id}", response_model=SubscriptionResponse, status_code=200)
@require_role(["subscriber", "admin"])
async def get_subscription(
    subscription_id: str,
    authorization: Optional[str] = Header(None),
    token: str = None,
    current_user: dict = None
):
    """Get subscription details"""
    try:
        if not validate_uuid(subscription_id):
            raise HTTPException(status_code=400, detail="Invalid subscription_id format")
        
        response = supabase_auth.service_client.table("subscriptions").select(
            "*"
        ).eq("id", subscription_id).single().execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Subscription not found")
        
        subscription = response.data
        
        # Check authorization (user can only view own subscription)
        if subscription["user_id"] != current_user["user_id"] and current_user["role"] != "admin":
            raise HTTPException(status_code=403, detail="Access denied")
        
        return SubscriptionResponse(**subscription)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving subscription: {str(e)}") from e


@router.get("", response_model=SubscriptionListResponse, status_code=200)
@require_role(["subscriber", "admin"])
async def list_subscriptions(
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    authorization: Optional[str] = Header(None),
    token: str = None,
    current_user: dict = None
):
    """List user's subscriptions"""
    try:
        query = supabase_auth.service_client.table("subscriptions").select(
            "*"
        ).eq("user_id", current_user["user_id"])
        
        if status:
            query = query.eq("status", status)
        
        response = query.order("created_at", desc=True).range(offset, offset + limit).execute()
        
        subscriptions = [SubscriptionResponse(**sub) for sub in response.data]
        
        # Get total count
        count_response = supabase_auth.service_client.table("subscriptions").select(
            "id", count="exact"
        ).eq("user_id", current_user["user_id"])
        
        if status:
            count_response = count_response.eq("status", status)
        
        total = count_response.execute().count
        
        return SubscriptionListResponse(
            subscriptions=subscriptions,
            total=total
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing subscriptions: {str(e)}") from e


@router.put("/{subscription_id}")
@require_role(["admin", "subscriber"])
async def update_subscription(  # pylint: disable=unused-argument
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
        raise HTTPException(status_code=400, detail=f"Error updating subscription: {str(e)}") from e

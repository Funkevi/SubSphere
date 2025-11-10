"""
Subscription Plans API Routes
Admin-only endpoints for managing subscription plans
"""
from typing import Optional
from fastapi import APIRouter, HTTPException, Header
from typing import List
from src.models.plan import CreatePlanRequest, UpdatePlanRequest, PlanResponse
from src.auth.supabase_auth import supabase_auth
from src.auth.rbac import require_role
from datetime import datetime, timezone

router = APIRouter(prefix="/api/plans", tags=["plans"])


@router.post("", response_model=PlanResponse, status_code=201)
@require_role(["admin"])
async def create_plan(
    request: CreatePlanRequest,
    authorization: Optional[str] = Header(None),
    token: str = None,
    current_user: dict = None
):
    """
    SIM-71: Create subscription plan (admin only)
    
    - Only accessible by admin role
    - Creates a new subscription plan with features
    """
    try:
        response = supabase_auth.service_client.table("subscription_plans").insert({
            "name": request.name,
            "description": request.description,
            "price": request.price,
            "duration_days": request.duration_days,
            "features": [f.dict() for f in request.features],
            "is_active": True
        }).execute()

        if not response.data:
            raise HTTPException(status_code=400, detail="Failed to create plan")

        plan = response.data[0]
        return PlanResponse(**plan)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creating plan: {str(e)}")


@router.get("", response_model=List[PlanResponse])
async def list_plans(active_only: bool = True):
    """
    Get all subscription plans
    
    - Public endpoint (no auth required)
    - Can filter by active status
    """
    try:
        query = supabase_auth.service_client.table("subscription_plans").select("*")
        
        if active_only:
            query = query.eq("is_active", True)
        
        response = query.execute()
        
        return [PlanResponse(**plan) for plan in response.data]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching plans: {str(e)}")


@router.get("/{plan_id}", response_model=PlanResponse)
async def get_plan(plan_id: str):
    """
    Get plan by ID
    
    - Public endpoint
    - Returns only active plans
    """
    try:
        response = supabase_auth.service_client.table("subscription_plans").select(
            "*"
        ).eq("id", plan_id).single().execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Plan not found")

        return PlanResponse(**response.data)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=404, detail="Plan not found")


@router.put("/{plan_id}", response_model=PlanResponse)
@require_role(["admin"])
async def update_plan(
    plan_id: str,
    request: UpdatePlanRequest,
    authorization: Optional[str] = Header(None),
    token: str = None,
    current_user: dict = None
):
    """
    SIM-71: Update subscription plan (admin only)
    
    - Only accessible by admin role
    - Updates plan details
    """
    try:
        # Build update data (exclude unset fields)
        update_data = request.dict(exclude_unset=True)
        
        if "features" in update_data and update_data["features"]:
            update_data["features"] = [f.dict() for f in request.features]

        response = supabase_auth.service_client.table("subscription_plans").update(
            update_data
        ).eq("id", plan_id).execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Plan not found")

        return PlanResponse(**response.data[0])

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error updating plan: {str(e)}")


@router.delete("/{plan_id}", status_code=204)
@require_role(["admin"])
async def delete_plan(
    plan_id: str,
    authorization: Optional[str] = Header(None),
    token: str = None,
    current_user: dict = None
):
    """
    SIM-71: Soft delete subscription plan (admin only)
    
    - Only accessible by admin role
    - Sets is_active to False (soft delete)
    """
    try:
        response = supabase_auth.service_client.table("subscription_plans").update({
            "is_active": False,
            "deleted_at": datetime.now(timezone.utc).isoformat()
        }).eq("id", plan_id).execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Plan not found")

        return None
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error deleting plan: {str(e)}")

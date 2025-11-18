"""
Subscription Plans API Routes
Admin-only endpoints for managing subscription plans
"""
from datetime import datetime, timezone
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Header, Body
from src.models.plan import CreatePlanRequest, UpdatePlanRequest, PlanResponse
from src.auth.supabase_auth import supabase_auth
from src.auth.rbac import require_role

router = APIRouter(prefix="/api/plans", tags=["plans"])


@router.post("", response_model=PlanResponse, status_code=201)
@require_role(["admin"])
async def create_plan(
    plan: CreatePlanRequest = Body(..., embed=True),
    _authorization: Optional[str] = Header(None),
    _token: str = None,
    _current_user: dict = None
):
    """
    SIM-71: Create subscription plan (admin only)
    """
    try:
        response = supabase_auth.service_client.table("subscription_plans").insert({
            "name": plan.name,
            "description": plan.description,
            "price": plan.price,
            "duration_days": plan.duration_days,
            "features": [f.dict() for f in plan.features],
            "is_active": True
        }).execute()

        if not response.data:
            raise HTTPException(status_code=400, detail="Failed to create plan")

        plan_data = response.data[0]
        return PlanResponse(**plan_data)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creating plan: {str(e)}") from e


@router.get("", response_model=List[PlanResponse])
async def list_plans(active_only: bool = True):
    """Get all subscription plans"""
    try:
        query = supabase_auth.service_client.table("subscription_plans").select("*")

        if active_only:
            query = query.eq("is_active", True)

        response = query.execute()

        return [PlanResponse(**plan) for plan in response.data]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching plans: {str(e)}") from e


@router.get("/{plan_id}", response_model=PlanResponse)
async def get_plan(plan_id: str):
    """Get plan by ID"""
    try:
        response = supabase_auth.service_client.table("subscription_plans").select(
            "*"
        ).eq("id", plan_id).single().execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Plan not found")

        return PlanResponse(**response.data)

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=404, detail="Plan not found") from None


@router.put("/{plan_id}", response_model=PlanResponse)
@require_role(["admin"])
async def update_plan(
    plan_id: str,
    plan: UpdatePlanRequest = Body(..., embed=True),
    _authorization: Optional[str] = Header(None),
    _token: str = None,
    _current_user: dict = None
):
    """
    SIM-71: Update subscription plan (admin only)
    """
    try:
        # Build update data (exclude unset fields)
        update_data = plan.dict(exclude_unset=True)

        if "features" in update_data and update_data["features"]:
            update_data["features"] = [f.dict() for f in plan.features]

        response = supabase_auth.service_client.table("subscription_plans").update(
            update_data
        ).eq("id", plan_id).execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Plan not found")

        return PlanResponse(**response.data[0])

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error updating plan: {str(e)}") from e


@router.delete("/{plan_id}", status_code=204)
@require_role(["admin"])
async def delete_plan(
    plan_id: str,
    _authorization: Optional[str] = Header(None),
    _token: str = None,
    _current_user: dict = None
):
    """
    SIM-71: Soft delete subscription plan (admin only)
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
        raise HTTPException(status_code=400, detail=f"Error deleting plan: {str(e)}") from e

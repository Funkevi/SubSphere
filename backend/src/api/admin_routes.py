from fastapi import APIRouter, HTTPException, Request, Depends
from src.auth.rbac import require_role

router = APIRouter(prefix="/api/admin", tags=["admin"])

@router.get("/dashboard")
async def admin_dashboard(request: Request):
    '''Admin-only endpoint'''

    # Check if user has admin role
    user_role = getattr(request.state, "user", {}).get("role")
    if user_role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can access this endpoint")

    return {
        "success": True,
        "message": "Welcome admin!",
        "user_id": request.state.user.get("user_id")
    }

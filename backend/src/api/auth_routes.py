from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.auth.supabase_auth import supabase_auth
from src.utils.validators import Validators

router = APIRouter(prefix="/api/auth", tags=["auth"])

class RegisterRequest(BaseModel):
    email: str
    password: str

class RegisterResponse(BaseModel):
    success: bool
    message: str
    user_id: str = None

@router.post("/register", response_model=RegisterResponse, status_code=201)
async def register(request: RegisterRequest):
    '''SIM-45: User Registration endpoint'''

    # Validate email
    is_valid_email, email_error = Validators.validate_email(request.email)
    if not is_valid_email:
        raise HTTPException(status_code=400, detail=email_error)

    # Validate password
    is_valid_password, password_error = Validators.validate_password(request.password)
    if not is_valid_password:
        raise HTTPException(status_code=400, detail=password_error)

    # Register with Supabase
    result = await supabase_auth.sign_up(request.email, request.password)

    if not result["success"]:
        status_code = result.get("code", 400)
        raise HTTPException(status_code=status_code, detail=result["error"])

    return RegisterResponse(
        success=True,
        message="User registered successfully",
        user_id=str(result["user"].id)
    )

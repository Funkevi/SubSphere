from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.auth.supabase_auth import supabase_auth
from src.utils.validators import Validators
from src.auth.jwt_handler import jwt_handler  # added import

router = APIRouter(prefix="/api/auth", tags=["auth"])


# ============================================
# SIM-45: User Registration Endpoint
# ============================================
class RegisterRequest(BaseModel):
    email: str
    password: str


class RegisterResponse(BaseModel):
    success: bool
    message: str
    user_id: str = None


@router.post("/register", response_model=RegisterResponse, status_code=201)
async def register(request: RegisterRequest):
    """SIM-45: User Registration endpoint"""

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
        user_id=str(result["user"].id),
    )


# ============================================
# SIM-52: User Login Endpoint (JWT + RBAC)
# ============================================
class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    success: bool
    access_token: str = None
    user_id: str = None
    role: str = None
    message: str


@router.post("/login", response_model=LoginResponse, status_code=200)
async def login(request: LoginRequest):
    """SIM-52: User authentication with JWT and RBAC"""

    # Validate email format
    is_valid_email, email_error = Validators.validate_email(request.email)
    if not is_valid_email:
        raise HTTPException(status_code=400, detail=email_error)

    # Sign in with Supabase
    result = await supabase_auth.sign_in(request.email, request.password)

    if not result["success"]:
        raise HTTPException(status_code=401, detail=result["error"])

    # Get user profile with role
    user_id = str(result["user"].id)
    profile_result = await supabase_auth.get_user_profile(user_id)

    if not profile_result["success"]:
        raise HTTPException(status_code=500, detail="Error fetching user profile")

    # Extract role_id (fallback to subscriber)
    user_role = profile_result["profile"].get("role_id", "subscriber")

    # Generate JWT token
    access_token = jwt_handler.generate_token(user_id, user_role)

    return LoginResponse(
        success=True,
        access_token=access_token,
        user_id=user_id,
        role=user_role,
        message="Login successful",
    )

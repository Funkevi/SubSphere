"""
Authentication API routes
"""
from typing import Optional
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from src.auth.supabase_auth import supabase_auth
from src.utils.validators import Validators
from src.auth.jwt_handler import JWTHandler

router = APIRouter(prefix="/api/auth", tags=["auth"])


# ========== Models ==========

class RegisterRequest(BaseModel):
    email: str
    password: str


class RegisterResponse(BaseModel):
    success: bool
    message: str
    user_id: str = None


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    success: bool
    access_token: str = None
    user_id: str = None
    role: str = None
    message: str
    email: str = None


# ========== Role Mapping ==========

ROLE_UUID_TO_NAME = {
    "422b8113-a6d2-404f-9cf0-9ccdf48c0c03": "subscriber",
    "ea31bc06-c648-4361-b611-d5f028c2b117": "admin",
    "49d95cb2-0f50-4842-8a55-a324a6a0f404": "finance"
}


def get_role_name(role_id: str) -> str:
    """Convert role UUID to role name"""
    return ROLE_UUID_TO_NAME.get(role_id, "subscriber")


# ========== Endpoints ==========

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
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Get user profile with role
    user_id = str(result["user"].id)
    profile_result = await supabase_auth.get_user_profile(user_id)
    
    # Extract role_id (UUID)
    if profile_result["success"]:
        role_id = profile_result["profile"].get("role_id", "422b8113-a6d2-404f-9cf0-9ccdf48c0c03")
    else:
        role_id = "422b8113-a6d2-404f-9cf0-9ccdf48c0c03"
    
    # Convert UUID to role name
    role_name = get_role_name(role_id)
    
    # Generate JWT token with role NAME (not UUID)
    access_token = JWTHandler.generate_token(user_id, role_name)
    
    return LoginResponse(
        success=True,
        access_token=access_token,
        user_id=user_id,
        role=role_name,  # "admin", not UUID
        email=result["user"].email,
        message="Login successful",
    )


@router.get("/me", status_code=200)
async def get_current_user(authorization: Optional[str] = Header(None)):
    """Get current authenticated user info"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    try:
        token = authorization.split(" ")[1]
    except IndexError:
        raise HTTPException(status_code=401, detail="Invalid authorization header format")
    
    result = JWTHandler.verify_token(token)
    
    if not result["valid"]:
        raise HTTPException(status_code=401, detail=result["error"])
    
    return {
        "user_id": result["payload"]["user_id"],
        "role": result["payload"]["role"]
    }

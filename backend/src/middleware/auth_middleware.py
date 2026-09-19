from fastapi import Request, HTTPException
from src.auth.jwt_handler import jwt_handler

class AuthMiddleware:
    '''Middleware to verify JWT in requests'''

    def __init__(self, app):
        self.app = app

    async def __call__(self, request: Request, call_next):
        # Skip auth check for public endpoints
        public_endpoints = ["/api/auth/register", "/api/auth/login", "/health"]

        if request.url.path not in public_endpoints:
            auth_header = request.headers.get("Authorization")

            if not auth_header:
                raise HTTPException(status_code=401, detail="Missing authorization header")

            try:
                scheme, token = auth_header.split()
                if scheme.lower() != "bearer":
                    raise HTTPException(status_code=401, detail="Invalid authorization scheme")
            except:
                raise HTTPException(status_code=401, detail="Invalid authorization header")

            # Verify token
            token_result = jwt_handler.verify_token(token)
            if not token_result["valid"]:
                raise HTTPException(status_code=401, detail=token_result["error"])

            # Add user to request state
            request.state.user = token_result["payload"]

        response = await call_next(request)
        return response


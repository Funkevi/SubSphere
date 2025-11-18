from supabase import create_client, Client
from src.config import settings

class SupabaseAuth:
    def __init__(self):
        self.client: Client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_KEY
        )
        self.service_client: Client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SERVICE_ROLE_KEY
        )

    async def sign_up(self, email: str, password: str):
        '''Register new user with Supabase Auth'''
        try:
            response = self.client.auth.sign_up({
                "email": email,
                "password": password,
            })
            return {"success": True, "user": response.user, "session": response.session}
        except Exception as e:
            if "already registered" in str(e):
                return {"success": False, "error": "User already registered", "code": 409}
            return {"success": False, "error": str(e), "code": 400}

    async def sign_in(self, email: str, password: str):
        '''Login user with Supabase Auth'''
        try:
            response = self.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            return {"success": True, "user": response.user, "session": response.session}
        except Exception:
            return {"success": False, "error": "Invalid credentials", "code": 401}

    async def get_user_profile(self, user_id: str):
        '''Get user profile with role'''
        try:
            response = self.service_client.table("profiles").select(
                "*"
            ).eq("user_id", user_id).single().execute()
            return {"success": True, "profile": response.data}
        except Exception as e:
            return {"success": False, "error": str(e)}

supabase_auth = SupabaseAuth()

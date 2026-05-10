import os
import json
from contextvars import ContextVar
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from starlette.requests import Request
from dotenv import load_dotenv

load_dotenv()

# ContextVar to store the current user profile
current_user: ContextVar[dict] = ContextVar("current_user", default={})

def load_profiles():
    profiles_path = os.getenv("PROFILES_PATH", "profiles.json")
    if not os.path.exists(profiles_path):
        return []
    with open(profiles_path, "r") as f:
        data = json.load(f)
        return data.get("profiles", [])

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Allow preflight requests
        if request.method == "OPTIONS":
            return await call_next(request)
        
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse({"error": "Unauthorized"}, status_code=401)
        
        token = auth_header.split(" ")[1]
        
        profiles = load_profiles()
        user_profile = next((p for p in profiles if p["token"] == token), None)
        
        if not user_profile:
            return JSONResponse({"error": "Forbidden"}, status_code=403)
        
        # Store user profile in context variable and request state
        request.state.user = user_profile
        token_context = current_user.set(user_profile)
        
        try:
            response = await call_next(request)
        finally:
            current_user.reset(token_context)
            
        return response

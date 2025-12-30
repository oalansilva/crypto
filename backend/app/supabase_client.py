# file: backend/app/supabase_client.py
from supabase import create_client, Client
from app.config import get_settings
from typing import Optional

_supabase_client: Optional[Client] = None

def get_supabase() -> Client:
    """Dependency for FastAPI endpoints - lazy initialization"""
    global _supabase_client
    
    if _supabase_client is None:
        settings = get_settings()
        try:
            _supabase_client = create_client(
                settings.supabase_url,
                settings.supabase_service_role_key
            )
        except Exception as e:
            # Fallback: if supabase client fails, we can still use direct DB connection
            print(f"Warning: Supabase client initialization failed: {e}")
            print("API will work but without Supabase SDK features")
            # Return a mock client or raise
            raise RuntimeError(f"Failed to initialize Supabase client: {e}")
    
    return _supabase_client

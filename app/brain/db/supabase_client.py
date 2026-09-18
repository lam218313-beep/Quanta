"""
Supabase client connection.
"""
import os
from supabase import create_client, Client
try:
    from app.brain.config import get_settings
except ModuleNotFoundError:
    from brain.config import get_settings


def get_supabase_client() -> Client:
    """
    Create and return a Supabase client.
    Uses service role for backend operations (bypasses RLS).
    """
    settings = get_settings()
    return create_client(
        settings.supabase_url,
        settings.supabase_key
    )


# Singleton instance
_supabase_client: Client | None = None


def get_supabase() -> Client:
    """Get or create Supabase client singleton."""
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = get_supabase_client()
    return _supabase_client

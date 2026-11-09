from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.database import get_db
from database.models import User
from backend.dependencies import get_current_user
from voice.follow_up_engine import follow_up_engine
from agents.ollama_client import ollama_client

router = APIRouter(prefix="/system", tags=["System & Reminders"])

@router.get("/ollama-status")
def get_ollama_status(current_user: User = Depends(get_current_user)):
    """Checks whether Ollama daemon is running and returns installed local models."""
    is_running = ollama_client.is_service_running()
    installed = ollama_client.list_installed_models()
    return {
        "is_running": is_running,
        "base_url": ollama_client.base_url,
        "installed_models": installed,
        "recommended_model": "llama3.2:3b",
        "recommended_for_hardware": "llama3.2:3b (Optimized for 16GB RAM & 12 CPU cores)"
    }

@router.get("/follow-up-reminders")
def get_follow_up_reminders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Returns 5-day application follow-up reminders with spoken prompts."""
    return follow_up_engine.check_pending_follow_ups(db=db, follow_up_days=5)


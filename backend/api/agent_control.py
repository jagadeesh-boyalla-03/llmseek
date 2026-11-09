from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.database import get_db
from database.models import User, AgentRun, AgentActivityLog
from database.crud import log_activity
from backend.dependencies import get_current_user

router = APIRouter(prefix="/agent", tags=["Autonomous Agent Supervisor"])

# In-memory agent state
AGENT_STATE = {
    "status": "RUNNING", # RUNNING, PAUSED, STOPPED
    "last_action": "System initialized and monitoring active.",
    "active_tasks": 0,
    "dry_run_enabled": True
}

@router.get("/status")
def get_agent_status(current_user: User = Depends(get_current_user)):
    return AGENT_STATE

@router.post("/pause")
def pause_agent(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    AGENT_STATE["status"] = "PAUSED"
    AGENT_STATE["last_action"] = "Monitoring and automated applications paused by user."
    log_activity(db, "SupervisorAgent", "AGENT_PAUSED", "User requested agent pause")
    return {"message": "Agent paused", "state": AGENT_STATE}

@router.post("/resume")
def resume_agent(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    AGENT_STATE["status"] = "RUNNING"
    AGENT_STATE["last_action"] = "Autonomous monitoring and matching resumed."
    log_activity(db, "SupervisorAgent", "AGENT_RESUMED", "User resumed agent")
    return {"message": "Agent resumed", "state": AGENT_STATE}

@router.post("/emergency-stop")
def emergency_stop(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    AGENT_STATE["status"] = "STOPPED"
    AGENT_STATE["last_action"] = "Emergency stop executed. All operations halted."
    log_activity(db, "SupervisorAgent", "EMERGENCY_STOP", "Emergency stop triggered", log_level="CRITICAL")
    return {"message": "Emergency stop executed", "state": AGENT_STATE}


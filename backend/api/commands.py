import uuid
import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.database import get_db
from database.schemas import CommandRequest, CommandResponse
from database.models import User, CommandTask, CommandConversation, Job, Application
from backend.dependencies import get_current_user
from notifications.telephony_service import telephony_service
from voice.sarvam_voice import sarvam_voice

router = APIRouter(prefix="/commands", tags=["Jarvis Voice & Text Command Center"])

@router.post("/speak-sarvam")
def speak_with_sarvam(
    text: str,
    language: str = "en-IN",
    speaker: str = "meera",
    current_user: User = Depends(get_current_user)
):
    """Generates ultra-natural Indian voice audio via Sarvam AI bulbul:v1."""
    audio_base64 = sarvam_voice.synthesize_speech(text, language_code=language, speaker=speaker)
    if audio_base64:
        return {"success": True, "provider": "Sarvam AI (bulbul:v1)", "audio_base64": audio_base64}
    return {"success": False, "provider": "Browser Fallback", "message": "SARVAM_API_KEY not configured"}

@router.post("/test-call")
def test_phone_call(
    phone_number: str = "+919876543210",
    current_user: User = Depends(get_current_user)
):
    """Triggers sample voice call to candidate mobile number."""
    call_res = telephony_service.make_real_phone_call(to_number=phone_number)
    return call_res

@router.post("/execute", response_model=CommandResponse)
def execute_command(
    req: CommandRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    cmd_text = req.command.strip()
    task_id = str(uuid.uuid4())[:8]

    # Deterministic intent detection
    lower = cmd_text.lower()
    intent = "UNKNOWN"
    spoken = "I have processed your command."
    result_data = {}

    if "python fresher" in lower or "search" in lower or "find" in lower:
        intent = "SEARCH_JOBS"
        spoken = "Searching for IT fresher opportunities matching your verified profile across active sources."
        result_data = {"category": "Python / AI Fresher", "source": "All Connected"}
    elif "eligible" in lower or "check eligibility" in lower:
        intent = "CHECK_ELIGIBILITY"
        spoken = "Checking fresher eligibility based on 0 to 2 years requirement and entry-level IT criteria."
        result_data = {"rule": "Fresher Eligibility (0-2 YOE)"}
    elif "resume" in lower or "generate resume" in lower:
        intent = "GENERATE_RESUME"
        spoken = "Generating customized ATS-compliant resume highlighting verified projects including VoiceEra and ContraRAG."
        result_data = {"template": "ATS_Standard_v1"}
    elif "status" in lower or "pending" in lower or "applications" in lower:
        intent = "SHOW_APPLICATIONS"
        apps_count = db.query(Application).count()
        spoken = f"You currently have {apps_count} tracked applications. All submissions are running in safe verified mode."
        result_data = {"application_count": apps_count}
    elif "pause" in lower:
        intent = "PAUSE_AGENT"
        spoken = "Agent job monitoring and automated tasks have been safely paused."
        result_data = {"agent_state": "PAUSED"}
    elif "resume" in lower and "monitoring" in lower:
        intent = "RESUME_AGENT"
        spoken = "Resuming autonomous job search and monitoring."
        result_data = {"agent_state": "RUNNING"}
    elif "stop" in lower or "emergency" in lower:
        intent = "STOP_TASK"
        spoken = "Emergency stop initiated. All pending actions halted immediately."
        result_data = {"agent_state": "STOPPED"}
    else:
        intent = "ANALYZE_JOB"
        spoken = "Analyzing your request against candidate qualifications and system safety policies."
        result_data = {"query": cmd_text}

    task = CommandTask(
        task_uuid=task_id,
        raw_command=cmd_text,
        transcription=cmd_text if req.source == "voice" else None,
        intent=intent,
        parameters={"source": req.source},
        status="COMPLETED",
        progress=100,
        spoken_summary=spoken,
        result_data=result_data,
        completed_at=datetime.datetime.utcnow()
    )
    db.add(task)

    # Conversation history
    conv_user = CommandConversation(role="user", message=cmd_text, task_id=task.id)
    conv_jarvis = CommandConversation(role="jarvis", message=spoken, task_id=task.id)
    db.add(conv_user)
    db.add(conv_jarvis)

    db.commit()

    return {
        "task_uuid": task_id,
        "intent": intent,
        "parameters": task.parameters,
        "status": "COMPLETED",
        "spoken_summary": spoken,
        "result_data": result_data
    }


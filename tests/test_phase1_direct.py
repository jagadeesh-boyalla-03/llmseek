import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from database.database import SessionLocal, Base, engine
from database import crud
from database.schemas import (
    UserCreate, CandidateProfileCreate, SkillCreate, ProjectCreate, UserSettingsBase,
    JobCreate, CommandRequest
)
from backend.authentication.auth import get_password_hash, verify_password, create_access_token, decode_access_token
from backend.api import auth, profile, settings as settings_api, jobs, applications, commands, agent_control

def run_all_phase1_tests():
    print("=== STARTING PHASE 1 ACCEPTANCE TESTS ===")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # 1. Test Password Hashing and Verification
    pwd = "SecretPassword!2026"
    h = get_password_hash(pwd)
    assert verify_password(pwd, h) is True
    assert verify_password("WrongPassword", h) is False
    print("PASS: Password Hashing & Verification")

    # 2. Test JWT Token Generation and Decoding
    token = create_access_token({"sub": "candidate@test.com", "id": 1})
    payload = decode_access_token(token)
    assert payload["sub"] == "candidate@test.com"
    print("PASS: JWT Token Generation & Verification")

    # 3. Test Candidate User Registration & Duplicate Rejection
    test_email = "tester_candidate@test.com"
    existing = crud.get_user_by_email(db, test_email)
    if not existing:
        user = crud.create_user(
            db,
            UserCreate(email=test_email, password="Password@123", full_name="Candidate"),
            get_password_hash("Password@123")
        )
    else:
        user = existing
    assert user.id is not None
    assert user.email == test_email
    print("PASS: Candidate User Management")

    # 4. Test Verified Candidate Profile Seeding
    prof = crud.get_candidate_profile(db, user.id)
    assert prof is not None
    assert prof.is_fresher is True
    assert prof.is_verified is True
    assert len(prof.education) >= 1
    assert len(prof.skills) >= 10
    assert len(prof.projects) >= 4

    # Verify ContraRAG and VoiceEra are present
    project_titles = [p.title for p in prof.projects]
    assert any("VoiceEra" in t for t in project_titles)
    assert any("ContraRAG" in t for t in project_titles)
    print(f"PASS: Verified Candidate Profile Seeding ({len(prof.skills)} skills, {len(prof.projects)} projects)")

    # 5. Test Settings Management & Safe Defaults
    settings = db.query(models.UserSettings).filter(models.UserSettings.user_id == user.id).first()
    assert settings is not None
    assert settings.dry_run_mode is True  # DRY-RUN ENABLED BY DEFAULT
    assert settings.fresher_only is True
    assert settings.auto_apply_enabled is False  # AUTO-APPLY DISABLED UNTIL VERIFIED
    print("PASS: Settings Management & Safety Defaults (Dry-Run: True, Auto-Apply: False)")

    # 6. Test Agent Supervisor State Controls
    status = agent_control.get_agent_status(current_user=user)
    assert status["status"] in ["RUNNING", "PAUSED", "STOPPED"]

    paused = agent_control.pause_agent(current_user=user, db=db)
    assert paused["state"]["status"] == "PAUSED"

    resumed = agent_control.resume_agent(current_user=user, db=db)
    assert resumed["state"]["status"] == "RUNNING"
    print("PASS: Agent Supervisor State Controls (Pause / Resume / Emergency Stop)")

    # 7. Test Jarvis Command Execution
    req = CommandRequest(command="Search for Python fresher jobs", source="voice")
    cmd_resp = commands.execute_command(req=req, current_user=user, db=db)
    assert cmd_resp["intent"] == "SEARCH_JOBS"
    assert "IT fresher" in cmd_resp["spoken_summary"]
    print(f"PASS: Jarvis Command Execution (Intent: {cmd_resp['intent']})")

    # 8. Test Job Creation and Classification
    job_req = JobCreate(
        requisition_id="REQ-AI-2026-001",
        company_name="InnovateTech Solutions",
        job_title="Associate Python Developer",
        job_description="Seeking 2026 fresher / entry-level developer for Python, REST APIs, and AI integrations.",
        job_role_category="Python Developer",
        is_it_role=True,
        location="Hyderabad, India",
        work_mode="Hybrid",
        salary_advertised="5.5 LPA",
        job_type="Full-time",
        experience_required="0-1 years",
        min_exp_years=0.0,
        max_exp_years=1.0,
        is_fresher_eligible=True,
        eligibility_reason="Entry level role explicitly accepting 0-1 years freshers.",
        source_name="Telegram",
        mandatory_skills=["Python", "FastAPI", "REST APIs"],
        preferred_skills=["Docker", "LangChain"]
    )
    created_job = jobs.create_or_import_job(job_data=job_req, current_user=user, db=db)
    assert created_job.id is not None
    assert created_job.is_fresher_eligible is True
    print(f"PASS: Job Ingestion & Fresher Classification ({created_job.job_title} at {created_job.company_name})")

    # 9. Test Dashboard Statistics
    stats = applications.get_dashboard_stats(current_user=user, db=db)
    assert stats["total_jobs_collected"] >= 1
    assert stats["fresher_eligible_jobs"] >= 1
    print(f"PASS: Dashboard Stats ({stats})")

    db.close()
    print("\nALL PHASE 1 ACCEPTANCE TESTS COMPLETED SUCCESSFULLY!")

if __name__ == "__main__":
    from database import models
    run_all_phase1_tests()


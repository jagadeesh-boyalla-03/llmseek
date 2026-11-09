import json
import os
from sqlalchemy.orm import Session
from database.models import (
    User, CandidateProfile, CandidateEducation, CandidateSkill,
    CandidateProject, CandidateCertification, UserSettings, Job,
    JobRequirement, JobMatch, Application, Resume, CommandTask, AgentActivityLog
)
from database.schemas import UserCreate, CandidateProfileCreate, UserSettingsBase

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user: UserCreate, hashed_password: str):
    db_user = User(
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # Initialize default settings
    settings = UserSettings(user_id=db_user.id)
    db.add(settings)
    db.commit()
    return db_user

def seed_candidate_profile_from_json(db: Session, user_id: int):
    # Check if profile already exists
    existing = db.query(CandidateProfile).filter(CandidateProfile.user_id == user_id).first()
    if existing:
        return existing

    profile_json_path = os.path.join(
        os.path.dirname(__file__), "..", "storage", "master_resume", "candidate_profile.json"
    )
    if not os.path.exists(profile_json_path):
        return None

    with open(profile_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    p_info = data.get("personal_info", {})
    profile = CandidateProfile(
        user_id=user_id,
        headline=p_info.get("headline"),
        phone=p_info.get("phone"),
        email=p_info.get("email"),
        linkedin_url=p_info.get("linkedin"),
        github_url=p_info.get("github"),
        location=p_info.get("location"),
        summary=data.get("summary"),
        is_fresher=True,
        is_verified=True
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)

    # Add Education
    for edu in data.get("education", []):
        db_edu = CandidateEducation(
            profile_id=profile.id,
            degree=edu.get("degree"),
            institution=edu.get("institution"),
            location=edu.get("location"),
            cgpa_or_percentage=edu.get("cgpa"),
            graduation_year=edu.get("graduation_year"),
            verified=True
        )
        db.add(db_edu)

    # Add Skills
    tech_skills = data.get("technical_skills", {})
    for category, skills in tech_skills.items():
        for s in skills:
            db_skill = CandidateSkill(
                profile_id=profile.id,
                category=category,
                name=s,
                proficiency="Advanced" if category in ["languages", "ai_ml", "backend"] else "Intermediate",
                verified=True
            )
            db.add(db_skill)

    # Add Projects
    for proj in data.get("projects", []):
        db_proj = CandidateProject(
            profile_id=profile.id,
            title=proj.get("title"),
            tech_stack=proj.get("tech_stack", []),
            about=proj.get("about"),
            features=proj.get("features", []),
            github_url=proj.get("links", {}).get("github"),
            live_url=proj.get("links", {}).get("live"),
            verified=True
        )
        db.add(db_proj)

    # Add Certifications
    for cert in data.get("certifications", []):
        db_cert = CandidateCertification(
            profile_id=profile.id,
            title=cert.get("title"),
            issuer=cert.get("issuer"),
            issue_date=cert.get("date"),
            verified=True
        )
        db.add(db_cert)

    db.commit()
    db.refresh(profile)
    return profile

def get_candidate_profile(db: Session, user_id: int):
    profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == user_id).first()
    if not profile:
        profile = seed_candidate_profile_from_json(db, user_id)
    return profile

def log_activity(db: Session, agent_name: str, action: str, details: str, log_level: str = "INFO", run_id: int = None):
    log = AgentActivityLog(
        run_id=run_id,
        agent_name=agent_name,
        log_level=log_level,
        action=action,
        details=details
    )
    db.add(log)
    db.commit()
    return log


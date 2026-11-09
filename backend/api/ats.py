from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.database import get_db
from database.models import User, GeneratedResume, Job, ResumeAtsScore
from database import crud
from resume_engine.ats_scorer import ats_scorer
from resume_engine.optimizer import resume_optimizer
from backend.dependencies import get_current_user

router = APIRouter(prefix="/ats", tags=["ATS Resume Scoring & Optimization"])

@router.get("/resume/{resume_id}")
def get_resume_ats_details(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    resume = db.query(GeneratedResume).filter(GeneratedResume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    ats = resume.ats_score
    history = [
        {
            "attempt": h.attempt_number,
            "pre_score": h.pre_score,
            "post_score": h.post_score,
            "improvements": h.improvements_applied,
            "outcome": h.outcome
        }
        for h in resume.optimization_history
    ]

    return {
        "resume_id": resume.id,
        "targeted_role": resume.targeted_role,
        "version_tag": resume.version_tag,
        "overall_score": ats.overall_score if ats else 0.0,
        "is_90_plus": ats.is_90_plus if ats else False,
        "breakdown": ats.score_breakdown if ats else {},
        "missing_mandatory": ats.missing_mandatory_requirements if ats else [],
        "optimization_attempts": resume.optimization_attempts,
        "history": history,
        "pdf_path": resume.pdf_path,
        "docx_path": resume.docx_path
    }


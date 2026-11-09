import os
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from database.database import get_db
from database.models import User, CandidateProfile, MasterResumeVersion, CandidateProfileVersion
from database import crud
from resume_engine.document_parser import document_parser
from backend.dependencies import get_current_user
from backend.config import settings

router = APIRouter(prefix="/master-resume", tags=["Master Resume & Verification"])

@router.post("/upload")
async def upload_master_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    1. Detects uploaded file (PDF, DOCX, TXT).
    2. Extracts name, contact, education, skills, projects, certifications, achievements.
    3. Computes differences against current profile.
    4. Does NOT automatically overwrite verified profile. Returns diff for user confirmation.
    """
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in [".pdf", ".docx", ".txt"]:
        raise HTTPException(status_code=400, detail="Supported formats: PDF, DOCX, TXT")

    save_dir = os.path.join(settings.STORAGE_DIR, "master_resume")
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, file.filename)

    content = await file.read()
    with open(save_path, "wb") as f:
        f.write(content)

    raw_text = document_parser.extract_text_from_file(save_path)
    extracted = document_parser.parse_resume_to_candidate_profile(raw_text)

    profile = crud.get_candidate_profile(db, current_user.id)
    current_dict = {
        "personal_info": {"name": profile.headline, "email": profile.email},
        "skills": [{"name": s.name} for s in profile.skills],
        "projects": [{"title": p.title} for p in profile.projects]
    }
    diff = document_parser.compute_profile_differences(current_dict, extracted)

    # Save Master Resume Version
    master_version = MasterResumeVersion(
        profile_id=profile.id,
        file_name=file.filename,
        file_path=save_path,
        file_type=ext.replace(".", "").upper(),
        raw_text=raw_text[:5000],
        extracted_data=extracted,
        is_active_master=False # Awaiting verification
    )
    db.add(master_version)
    db.commit()
    db.refresh(master_version)

    return {
        "message": "Resume uploaded and extracted successfully.",
        "master_version_id": master_version.id,
        "extracted_profile": extracted,
        "differences": diff,
        "status": "Awaiting User Verification & Approval"
    }

@router.post("/approve-update/{master_version_id}")
def approve_profile_update(
    master_version_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    mv = db.query(MasterResumeVersion).filter(MasterResumeVersion.id == master_version_id).first()
    if not mv:
        raise HTTPException(status_code=404, detail="Master resume version not found")

    profile = crud.get_candidate_profile(db, current_user.id)
    mv.is_active_master = True

    # Snapshot current profile before update
    snapshot = CandidateProfileVersion(
        profile_id=profile.id,
        snapshot_json=mv.extracted_data,
        change_summary="User approved master resume updates.",
        verified_by_user=True
    )
    db.add(snapshot)
    db.commit()

    return {"message": "Candidate profile successfully updated and verified.", "profile_id": profile.id}


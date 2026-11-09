import os
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from database.database import get_db
from database.models import User, ResumeTemplate, ApprovedResumeTemplate, CandidateProfile
from resume_engine.template_manager import template_manager
from backend.dependencies import get_current_user

router = APIRouter(prefix="/templates", tags=["Resume Template Manager"])

@router.get("")
def get_templates(db: Session = Depends(get_db)):
    # Initialize default templates if table is empty
    existing = db.query(ResumeTemplate).count()
    if existing == 0:
        default_structure = {
            "template_name": "Standard Tech ATS Single Column",
            "file_type": "DOCX",
            "layout": "single_column_ats_friendly",
            "section_order": ["HEADER", "SUMMARY", "EDUCATION", "SKILLS", "PROJECTS", "CERTIFICATIONS", "ACHIEVEMENTS"],
            "typography": {"font_family": "Helvetica, Arial", "heading_size": 13, "body_size": 10},
            "margins": "0.75 in",
            "ats_readability_rating": 99.0
        }
        template_manager.register_approved_template(db, "Standard Tech ATS Single Column", default_structure, is_default=True)

        genai_structure = {
            "template_name": "Generative AI / Agentic Focus",
            "file_type": "PDF",
            "layout": "single_column_ats_friendly",
            "section_order": ["HEADER", "SUMMARY", "SKILLS", "PROJECTS", "EDUCATION", "CERTIFICATIONS"],
            "typography": {"font_family": "Calibri", "heading_size": 14, "body_size": 10.5},
            "margins": "0.75 in",
            "ats_readability_rating": 98.0
        }
        template_manager.register_approved_template(db, "Generative AI / Agentic Focus", genai_structure, is_default=False)

    return template_manager.list_templates(db)

@router.post("/upload")
async def upload_template(
    file: UploadFile = File(...),
    template_name: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    name = template_name or os.path.splitext(file.filename)[0]
    save_path = os.path.join(template_manager.ref_dir, file.filename)
    
    with open(save_path, "wb") as f:
        content = await file.read()
        f.write(content)

    structure = template_manager.analyze_uploaded_template(save_path, name)
    registered = template_manager.register_approved_template(db, name, structure)
    return {"message": "Template uploaded and analyzed successfully", "template": registered.name, "structure": structure}

@router.post("/{template_id}/set-default")
def set_default(
    template_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    tmpl = template_manager.set_default_template(db, template_id)
    if not tmpl:
        raise HTTPException(status_code=404, detail="Template not found")
    return {"message": f"Template '{tmpl.name}' set as active default"}


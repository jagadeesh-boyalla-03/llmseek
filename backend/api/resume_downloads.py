import os
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from database.database import get_db
from database.models import GeneratedResume, User
from backend.dependencies import get_current_user

router = APIRouter(prefix="/resumes", tags=["Resume Downloads"])

@router.get("/{resume_id}/download/pdf")
def download_resume_pdf(
    resume_id: int,
    db: Session = Depends(get_db)
):
    gen_res = db.query(GeneratedResume).filter(GeneratedResume.id == resume_id).first()
    if not gen_res or not gen_res.pdf_path or not os.path.exists(gen_res.pdf_path):
        raise HTTPException(status_code=404, detail="PDF resume file not found")
    
    filename = os.path.basename(gen_res.pdf_path)
    return FileResponse(
        path=gen_res.pdf_path,
        filename=filename,
        media_type="application/pdf"
    )

@router.get("/{resume_id}/download/docx")
def download_resume_docx(
    resume_id: int,
    db: Session = Depends(get_db)
):
    gen_res = db.query(GeneratedResume).filter(GeneratedResume.id == resume_id).first()
    if not gen_res or not gen_res.docx_path or not os.path.exists(gen_res.docx_path):
        raise HTTPException(status_code=404, detail="DOCX resume file not found")
    
    filename = os.path.basename(gen_res.docx_path)
    return FileResponse(
        path=gen_res.docx_path,
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )


from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from database.database import get_db
from database.schemas import JobResponse, JobCreate
from database.models import User, Job, JobRequirement, JobMatch
from backend.dependencies import get_current_user

router = APIRouter(prefix="/jobs", tags=["Job Discovery & Matching"])

@router.get("", response_model=List[JobResponse])
def get_jobs(
    fresher_only: bool = Query(True, description="Filter for fresher eligible jobs"),
    min_score: Optional[float] = Query(None, description="Minimum match score"),
    search: Optional[str] = Query(None, description="Search keyword in title, company, or skills"),
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Job)
    if fresher_only:
        query = query.filter(Job.is_fresher_eligible == True)
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (Job.job_title.ilike(search_pattern)) | 
            (Job.company_name.ilike(search_pattern)) |
            (Job.job_description.ilike(search_pattern))
        )
    jobs = query.order_by(Job.created_at.desc()).offset(offset).limit(limit).all()
    if min_score is not None:
        jobs = [j for j in jobs if j.match and j.match.overall_score >= min_score]
    return jobs

@router.get("/{job_id}", response_model=JobResponse)
def get_job_detail(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@router.post("", response_model=JobResponse)
def create_or_import_job(
    job_data: JobCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check for direct requisition ID duplicate
    if job_data.requisition_id:
        existing = db.query(Job).filter(Job.requisition_id == job_data.requisition_id).first()
        if existing:
            return existing

    new_job = Job(
        requisition_id=job_data.requisition_id,
        company_name=job_data.company_name,
        job_title=job_data.job_title,
        job_description=job_data.job_description,
        job_role_category=job_data.job_role_category,
        is_it_role=job_data.is_it_role,
        location=job_data.location,
        work_mode=job_data.work_mode,
        salary_advertised=job_data.salary_advertised,
        bonus_and_benefits=job_data.bonus_and_benefits,
        job_type=job_data.job_type,
        experience_required=job_data.experience_required,
        min_exp_years=job_data.min_exp_years,
        max_exp_years=job_data.max_exp_years,
        is_fresher_eligible=job_data.is_fresher_eligible,
        eligibility_reason=job_data.eligibility_reason,
        job_url=job_data.job_url,
        company_url=job_data.company_url,
        recruiter_name=job_data.recruiter_name,
        recruiter_url=job_data.recruiter_url,
        source_name=job_data.source_name,
        status="Discovered"
    )
    db.add(new_job)
    db.commit()
    db.refresh(new_job)

    # Add requirements
    req = JobRequirement(
        job_id=new_job.id,
        mandatory_skills=job_data.mandatory_skills,
        preferred_skills=job_data.preferred_skills
    )
    db.add(req)
    db.commit()
    db.refresh(new_job)
    return new_job


from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.database import get_db
from database.schemas import (
    CandidateProfileResponse, CandidateProfileCreate,
    SkillCreate, SkillResponse, ProjectCreate, ProjectResponse,
    CertificationCreate, CertificationResponse, EducationCreate, EducationResponse
)
from database import crud
from database.models import (
    User, CandidateProfile, CandidateSkill, CandidateProject,
    CandidateCertification, CandidateEducation
)
from backend.dependencies import get_current_user

router = APIRouter(prefix="/profile", tags=["Candidate Profile"])

@router.get("", response_model=CandidateProfileResponse)
def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = crud.get_candidate_profile(db=db, user_id=current_user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate profile not found"
        )
    return profile

@router.put("", response_model=CandidateProfileResponse)
def update_profile(
    profile_data: CandidateProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = crud.get_candidate_profile(db=db, user_id=current_user.id)
    if not profile:
        profile = CandidateProfile(user_id=current_user.id)
        db.add(profile)

    for field, value in profile_data.model_dump(exclude_unset=True).items():
        setattr(profile, field, value)

    db.commit()
    db.refresh(profile)
    return profile

@router.post("/skills", response_model=SkillResponse)
def add_skill(
    skill: SkillCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = crud.get_candidate_profile(db=db, user_id=current_user.id)
    new_skill = CandidateSkill(
        profile_id=profile.id,
        category=skill.category,
        name=skill.name,
        proficiency=skill.proficiency,
        verified=skill.verified
    )
    db.add(new_skill)
    db.commit()
    db.refresh(new_skill)
    return new_skill

@router.delete("/skills/{skill_id}")
def delete_skill(
    skill_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = crud.get_candidate_profile(db=db, user_id=current_user.id)
    skill = db.query(CandidateSkill).filter(
        CandidateSkill.id == skill_id,
        CandidateSkill.profile_id == profile.id
    ).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    db.delete(skill)
    db.commit()
    return {"message": "Skill removed successfully"}

@router.post("/projects", response_model=ProjectResponse)
def add_project(
    project: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = crud.get_candidate_profile(db=db, user_id=current_user.id)
    new_proj = CandidateProject(
        profile_id=profile.id,
        title=project.title,
        tech_stack=project.tech_stack,
        about=project.about,
        features=project.features,
        github_url=project.github_url,
        live_url=project.live_url,
        verified=project.verified
    )
    db.add(new_proj)
    db.commit()
    db.refresh(new_proj)
    return new_proj


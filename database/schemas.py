from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

# Auth Schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class TokenData(BaseModel):
    email: Optional[str] = None

# Candidate Education Schemas
class EducationBase(BaseModel):
    degree: str
    institution: str
    location: Optional[str] = None
    cgpa_or_percentage: Optional[str] = None
    graduation_year: Optional[int] = None
    verified: bool = True

class EducationCreate(EducationBase):
    pass

class EducationResponse(EducationBase):
    id: int
    profile_id: int
    class Config:
        from_attributes = True

# Candidate Skill Schemas
class SkillBase(BaseModel):
    category: str
    name: str
    proficiency: str = "Intermediate"
    verified: bool = True

class SkillCreate(SkillBase):
    pass

class SkillResponse(SkillBase):
    id: int
    profile_id: int
    class Config:
        from_attributes = True

# Candidate Project Schemas
class ProjectBase(BaseModel):
    title: str
    tech_stack: List[str] = []
    about: Optional[str] = None
    features: List[str] = []
    github_url: Optional[str] = None
    live_url: Optional[str] = None
    verified: bool = True

class ProjectCreate(ProjectBase):
    pass

class ProjectResponse(ProjectBase):
    id: int
    profile_id: int
    class Config:
        from_attributes = True

# Candidate Certification Schemas
class CertificationBase(BaseModel):
    title: str
    issuer: str
    issue_date: Optional[str] = None
    credential_url: Optional[str] = None
    verified: bool = True

class CertificationCreate(CertificationBase):
    pass

class CertificationResponse(CertificationBase):
    id: int
    profile_id: int
    class Config:
        from_attributes = True

# Candidate Profile Schemas
class CandidateProfileBase(BaseModel):
    headline: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    location: Optional[str] = None
    summary: Optional[str] = None
    is_fresher: bool = True
    is_verified: bool = True

class CandidateProfileCreate(CandidateProfileBase):
    pass

class CandidateProfileResponse(CandidateProfileBase):
    id: int
    user_id: int
    education: List[EducationResponse] = []
    skills: List[SkillResponse] = []
    projects: List[ProjectResponse] = []
    certifications: List[CertificationResponse] = []
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True

# User Settings Schemas
class UserSettingsBase(BaseModel):
    min_match_score: float = 70.0
    dry_run_mode: bool = True
    auto_apply_enabled: bool = False
    hybrid_approval_threshold: float = 80.0
    max_experience_years: float = 2.0
    fresher_only: bool = True
    primary_ollama_model: str = "llama3.2:3b"
    email_alerts: bool = True
    whatsapp_alerts: bool = False
    telegram_alerts: bool = False
    voice_enabled: bool = True
    jarvis_voice_rate: int = 175
    parebo_portal_url: Optional[str] = ""

class UserSettingsResponse(UserSettingsBase):
    id: int
    user_id: int
    class Config:
        from_attributes = True

# Job Schemas
class JobBase(BaseModel):
    requisition_id: Optional[str] = None
    company_name: str
    job_title: str
    job_description: str
    job_role_category: Optional[str] = "Software Developer"
    is_it_role: bool = True
    location: Optional[str] = "Remote / India"
    work_mode: str = "On-site"
    salary_advertised: Optional[str] = None
    bonus_and_benefits: Optional[str] = None
    job_type: str = "Full-time"
    experience_required: Optional[str] = "0-1 years"
    min_exp_years: float = 0.0
    max_exp_years: float = 2.0
    is_fresher_eligible: bool = True
    eligibility_reason: Optional[str] = None
    job_url: Optional[str] = None
    company_url: Optional[str] = None
    recruiter_name: Optional[str] = None
    recruiter_url: Optional[str] = None
    source_name: str = "Manual"
    status: str = "Discovered"

class JobCreate(JobBase):
    mandatory_skills: List[str] = []
    preferred_skills: List[str] = []

class JobMatchResponse(BaseModel):
    overall_score: float
    category_fit: str
    technical_skills_score: float
    fresher_eligibility_score: float
    project_relevance_score: float
    education_score: float
    experience_score: float
    location_score: float
    certifications_score: float
    matched_skills: List[str] = []
    missing_skills: List[str] = []
    relevant_projects: List[str] = []
    strengths: List[str] = []
    weaknesses: List[str] = []
    recommendation: Optional[str] = None
    class Config:
        from_attributes = True

class JobResponse(JobBase):
    id: int
    is_duplicate: bool
    created_at: datetime
    match: Optional[JobMatchResponse] = None
    class Config:
        from_attributes = True

# Application Schemas
class ApplicationBase(BaseModel):
    job_id: int
    resume_id: Optional[int] = None
    application_mode: str = "Dry-Run"
    status: str = "Discovered"
    application_url: Optional[str] = None
    application_reference: Optional[str] = None
    confirmation_evidence: Optional[str] = None
    submission_answers: Dict[str, Any] = {}
    validation_status: str = "Valid"
    requires_approval: bool = True
    approval_reason: Optional[str] = None
    notes: Optional[str] = None

class ApplicationResponse(ApplicationBase):
    id: int
    created_at: datetime
    updated_at: datetime
    job: JobResponse
    class Config:
        from_attributes = True

# Command Schemas
class CommandRequest(BaseModel):
    command: str
    source: str = "text" # text or voice

class CommandResponse(BaseModel):
    task_uuid: str
    intent: str
    parameters: Dict[str, Any] = {}
    status: str
    spoken_summary: str
    result_data: Dict[str, Any] = {}


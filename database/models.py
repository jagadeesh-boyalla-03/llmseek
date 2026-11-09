import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey, JSON
)
from sqlalchemy.orm import relationship
from database.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    profile = relationship("CandidateProfile", back_populates="user", uselist=False)
    settings = relationship("UserSettings", back_populates="user", uselist=False)


class CandidateProfile(Base):
    __tablename__ = "candidate_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    headline = Column(String(255))
    phone = Column(String(50))
    email = Column(String(255))
    linkedin_url = Column(String(500))
    github_url = Column(String(500))
    portfolio_url = Column(String(500))
    location = Column(String(255))
    summary = Column(Text)
    is_fresher = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    user = relationship("User", back_populates="profile")
    education = relationship("CandidateEducation", back_populates="profile", cascade="all, delete-orphan")
    skills = relationship("CandidateSkill", back_populates="profile", cascade="all, delete-orphan")
    projects = relationship("CandidateProject", back_populates="profile", cascade="all, delete-orphan")
    certifications = relationship("CandidateCertification", back_populates="profile", cascade="all, delete-orphan")
    resumes = relationship("Resume", back_populates="profile")
    versions = relationship("CandidateProfileVersion", back_populates="profile")


class CandidateEducation(Base):
    __tablename__ = "candidate_education"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("candidate_profiles.id"), nullable=False)
    degree = Column(String(255), nullable=False)
    institution = Column(String(255), nullable=False)
    location = Column(String(255))
    cgpa_or_percentage = Column(String(50))
    graduation_year = Column(Integer)
    verified = Column(Boolean, default=True)

    profile = relationship("CandidateProfile", back_populates="education")


class CandidateSkill(Base):
    __tablename__ = "candidate_skills"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("candidate_profiles.id"), nullable=False)
    category = Column(String(100), nullable=False)
    name = Column(String(100), nullable=False, index=True)
    proficiency = Column(String(50), default="Intermediate")
    verified = Column(Boolean, default=True)

    profile = relationship("CandidateProfile", back_populates="skills")


class CandidateProject(Base):
    __tablename__ = "candidate_projects"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("candidate_profiles.id"), nullable=False)
    title = Column(String(255), nullable=False)
    tech_stack = Column(JSON, default=list)
    about = Column(Text)
    features = Column(JSON, default=list)
    github_url = Column(String(500))
    live_url = Column(String(500))
    verified = Column(Boolean, default=True)

    profile = relationship("CandidateProfile", back_populates="projects")


class CandidateCertification(Base):
    __tablename__ = "candidate_certifications"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("candidate_profiles.id"), nullable=False)
    title = Column(String(255), nullable=False)
    issuer = Column(String(255), nullable=False)
    issue_date = Column(String(50))
    credential_url = Column(String(500))
    verified = Column(Boolean, default=True)

    profile = relationship("CandidateProfile", back_populates="certifications")


# ============================================================
# NEW MODELS: MASTER RESUME & RESUME TEMPLATE ARCHITECTURE
# ============================================================

class MasterResumeVersion(Base):
    __tablename__ = "master_resume_versions"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("candidate_profiles.id"), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(50), nullable=False) # PDF, DOCX, TXT
    raw_text = Column(Text, nullable=False)
    extracted_data = Column(JSON, default=dict)
    is_active_master = Column(Boolean, default=False)
    uploaded_at = Column(DateTime, default=datetime.datetime.utcnow)


class CandidateProfileVersion(Base):
    __tablename__ = "candidate_profile_versions"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("candidate_profiles.id"), nullable=False)
    version_number = Column(Integer, default=1)
    snapshot_json = Column(JSON, nullable=False)
    change_summary = Column(Text)
    verified_by_user = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    profile = relationship("CandidateProfile", back_populates="versions")


class ResumeTemplate(Base):
    __tablename__ = "resume_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False) # e.g. Modern ATS Single Column, Tech Minimalist
    category = Column(String(50), default="Technical") # Technical, Executive, Research
    source_file_path = Column(String(500))
    file_type = Column(String(50)) # PDF, DOCX
    structure_json = Column(JSON, default=dict) # Section order, margins, fonts, spacing
    is_default = Column(Boolean, default=False)
    is_approved = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    approved_record = relationship("ApprovedResumeTemplate", back_populates="template", uselist=False)
    generated_resumes = relationship("GeneratedResume", back_populates="template")


class ApprovedResumeTemplate(Base):
    __tablename__ = "approved_resume_templates"

    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("resume_templates.id"), unique=True, nullable=False)
    approved_by = Column(String(100), default="User")
    layout_guidelines = Column(Text)
    section_order = Column(JSON, default=list) # ["HEADER", "SUMMARY", "EDUCATION", "SKILLS", "PROJECTS", "CERTIFICATIONS"]
    approved_at = Column(DateTime, default=datetime.datetime.utcnow)

    template = relationship("ResumeTemplate", back_populates="approved_record")


class GeneratedResume(Base):
    __tablename__ = "generated_resumes"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("candidate_profiles.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    template_id = Column(Integer, ForeignKey("resume_templates.id"), nullable=True)
    version_tag = Column(String(100), nullable=False) # e.g. Python_Dev_v1
    targeted_role = Column(String(255), nullable=False)
    tailored_summary = Column(Text)
    pdf_path = Column(String(500))
    docx_path = Column(String(500))
    content_json = Column(JSON, default=dict)
    optimization_attempts = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    template = relationship("ResumeTemplate", back_populates="generated_resumes")
    ats_score = relationship("ResumeAtsScore", back_populates="resume", uselist=False, cascade="all, delete-orphan")
    keyword_analysis = relationship("ResumeKeywordAnalysis", back_populates="resume", uselist=False, cascade="all, delete-orphan")
    optimization_history = relationship("ResumeOptimizationHistory", back_populates="resume", cascade="all, delete-orphan")
    approval_record = relationship("ResumeApprovalRecord", back_populates="resume", uselist=False)


class ResumeAtsScore(Base):
    __tablename__ = "resume_ats_scores"

    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("generated_resumes.id"), unique=True, nullable=False)
    overall_score = Column(Float, nullable=False) # 0 - 100
    is_90_plus = Column(Boolean, default=False)
    required_skill_coverage = Column(Float, default=0.0)    # 25%
    jd_keyword_relevance = Column(Float, default=0.0)       # 20%
    technical_skill_alignment = Column(Float, default=0.0)  # 15%
    relevant_project_alignment = Column(Float, default=0.0) # 15%
    education_alignment = Column(Float, default=0.0)        # 10%
    experience_compatibility = Column(Float, default=0.0)   # 5%
    ats_structure_readability = Column(Float, default=0.0)  # 10%
    score_breakdown = Column(JSON, default=dict)
    missing_mandatory_requirements = Column(JSON, default=list)
    calculated_at = Column(DateTime, default=datetime.datetime.utcnow)

    resume = relationship("GeneratedResume", back_populates="ats_score")


class ResumeKeywordAnalysis(Base):
    __tablename__ = "resume_keyword_analysis"

    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("generated_resumes.id"), unique=True, nullable=False)
    extracted_job_keywords = Column(JSON, default=list)
    matched_keywords = Column(JSON, default=list)
    missing_keywords = Column(JSON, default=list)
    density_analysis = Column(JSON, default=dict)

    resume = relationship("GeneratedResume", back_populates="keyword_analysis")


class ResumeOptimizationHistory(Base):
    __tablename__ = "resume_optimization_history"

    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("generated_resumes.id"), nullable=False)
    attempt_number = Column(Integer, nullable=False) # 1, 2, 3
    pre_score = Column(Float, nullable=False)
    post_score = Column(Float, nullable=False)
    improvements_applied = Column(JSON, default=list)
    verified_facts_expanded = Column(JSON, default=list)
    outcome = Column(String(50)) # "PASSED_90", "IMPROVED", "NEEDS_MANUAL_REVIEW"
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    resume = relationship("GeneratedResume", back_populates="optimization_history")


class ResumeApprovalRecord(Base):
    __tablename__ = "resume_approval_records"

    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("generated_resumes.id"), unique=True, nullable=False)
    status = Column(String(50), default="Pending") # "Auto-Approved (90+)", "Manual Review Required", "Approved by User", "Rejected"
    reason = Column(Text)
    reviewed_at = Column(DateTime)
    notes = Column(Text)

    resume = relationship("GeneratedResume", back_populates="approval_record")


# ============================================================
# SOURCES, JOBS & APPLICATIONS (PRESERVED)
# ============================================================

class JobSource(Base):
    __tablename__ = "job_sources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    source_type = Column(String(50), nullable=False)
    base_url = Column(String(500))
    is_enabled = Column(Boolean, default=True)
    status = Column(String(50), default="configured")
    last_scan_at = Column(DateTime)
    jobs_collected = Column(Integer, default=0)
    error_count = Column(Integer, default=0)
    last_error_message = Column(Text)
    config = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    postings = relationship("SourcePosting", back_populates="source")
    health_logs = relationship("ConnectorHealth", back_populates="source")


class SourcePosting(Base):
    __tablename__ = "source_postings"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("job_sources.id"), nullable=False)
    raw_content = Column(Text, nullable=False)
    sender = Column(String(255))
    message_type = Column(String(50), default="text")
    raw_metadata = Column(JSON, default=dict)
    processed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    source = relationship("JobSource", back_populates="postings")
    job = relationship("Job", back_populates="posting", uselist=False)


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    posting_id = Column(Integer, ForeignKey("source_postings.id"), nullable=True)
    canonical_job_id = Column(Integer, ForeignKey("jobs.id"), nullable=True)
    requisition_id = Column(String(100), index=True)
    company_name = Column(String(255), index=True, nullable=False)
    job_title = Column(String(255), index=True, nullable=False)
    job_description = Column(Text, nullable=False)
    clean_description = Column(Text)
    job_role_category = Column(String(100), index=True)
    is_it_role = Column(Boolean, default=True)
    location = Column(String(255))
    work_mode = Column(String(50), default="On-site")
    salary_advertised = Column(String(100))
    bonus_and_benefits = Column(Text)
    job_type = Column(String(50), default="Full-time")
    experience_required = Column(String(100))
    min_exp_years = Column(Float, default=0.0)
    max_exp_years = Column(Float, default=2.0)
    is_fresher_eligible = Column(Boolean, default=True)
    eligibility_reason = Column(Text)
    job_url = Column(String(500))
    company_url = Column(String(500))
    recruiter_name = Column(String(255))
    recruiter_url = Column(String(500))
    source_name = Column(String(100), default="Manual")
    is_duplicate = Column(Boolean, default=False)
    status = Column(String(50), default="Discovered")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    posting = relationship("SourcePosting", back_populates="job")
    requirements = relationship("JobRequirement", back_populates="job", uselist=False, cascade="all, delete-orphan")
    match = relationship("JobMatch", back_populates="job", uselist=False, cascade="all, delete-orphan")
    resumes = relationship("Resume", back_populates="job")
    applications = relationship("Application", back_populates="job")


class JobRequirement(Base):
    __tablename__ = "job_requirements"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False, unique=True)
    mandatory_skills = Column(JSON, default=list)
    preferred_skills = Column(JSON, default=list)
    responsibilities = Column(JSON, default=list)
    mandatory_degrees = Column(JSON, default=list)
    preferred_degrees = Column(JSON, default=list)
    certifications_required = Column(JSON, default=list)

    job = relationship("Job", back_populates="requirements")


class JobMatch(Base):
    __tablename__ = "job_matches"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False, unique=True)
    overall_score = Column(Float, nullable=False)
    category_fit = Column(String(50))
    technical_skills_score = Column(Float, default=0.0)
    fresher_eligibility_score = Column(Float, default=0.0)
    project_relevance_score = Column(Float, default=0.0)
    education_score = Column(Float, default=0.0)
    experience_score = Column(Float, default=0.0)
    location_score = Column(Float, default=0.0)
    certifications_score = Column(Float, default=0.0)
    matched_skills = Column(JSON, default=list)
    missing_skills = Column(JSON, default=list)
    relevant_projects = Column(JSON, default=list)
    strengths = Column(JSON, default=list)
    weaknesses = Column(JSON, default=list)
    recommendation = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    job = relationship("Job", back_populates="match")


class DuplicateCandidate(Base):
    __tablename__ = "duplicate_candidates"

    id = Column(Integer, primary_key=True, index=True)
    primary_job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    duplicate_job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    similarity_score = Column(Float, nullable=False)
    matched_attributes = Column(JSON, default=list)
    resolution = Column(String(50), default="Merged")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("candidate_profiles.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=True)
    version_tag = Column(String(100), nullable=False)
    targeted_role = Column(String(255))
    tailored_summary = Column(Text)
    selected_skills = Column(JSON, default=dict)
    selected_projects = Column(JSON, default=list)
    keywords_aligned = Column(JSON, default=list)
    pdf_path = Column(String(500))
    docx_path = Column(String(500))
    content_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    profile = relationship("CandidateProfile", back_populates="resumes")
    job = relationship("Job", back_populates="resumes")
    applications = relationship("Application", back_populates="resume")


class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=True)
    generated_resume_id = Column(Integer, ForeignKey("generated_resumes.id"), nullable=True)
    application_mode = Column(String(50), default="Dry-Run")
    status = Column(String(50), default="Discovered")
    applied_at = Column(DateTime)
    application_url = Column(String(500))
    application_reference = Column(String(100))
    confirmation_evidence = Column(Text)
    submission_answers = Column(JSON, default=dict)
    validation_status = Column(String(50), default="Valid")
    requires_approval = Column(Boolean, default=True)
    approval_reason = Column(Text)
    ats_score = Column(Float, default=0.0)
    ats_pass_90 = Column(Boolean, default=False)
    last_status_check = Column(DateTime)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    job = relationship("Job", back_populates="applications")
    resume = relationship("Resume", back_populates="applications")
    events = relationship("ApplicationEvent", back_populates="application", cascade="all, delete-orphan")
    approval_request = relationship("ApprovalRequest", back_populates="application", uselist=False)
    reminders = relationship("FollowUpReminder", back_populates="application")


class ApplicationEvent(Base):
    __tablename__ = "application_events"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id"), nullable=False)
    event_type = Column(String(100), nullable=False)
    old_status = Column(String(50))
    new_status = Column(String(50))
    details = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    application = relationship("Application", back_populates="events")


class ApprovalRequest(Base):
    __tablename__ = "approval_requests"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id"), unique=True, nullable=False)
    job_summary = Column(Text)
    answers_preview = Column(JSON, default=dict)
    reason = Column(Text)
    status = Column(String(50), default="Pending")
    reviewed_at = Column(DateTime)
    user_feedback = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    application = relationship("Application", back_populates="approval_request")


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    channel = Column(String(50), nullable=False)
    recipient = Column(String(255), nullable=False)
    subject = Column(String(255))
    message = Column(Text, nullable=False)
    notification_type = Column(String(100))
    status = Column(String(50), default="Queued")
    error_message = Column(Text)
    sent_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class AgentRun(Base):
    __tablename__ = "agent_runs"

    id = Column(Integer, primary_key=True, index=True)
    agent_name = Column(String(100), nullable=False)
    status = Column(String(50), default="Running")
    started_at = Column(DateTime, default=datetime.datetime.utcnow)
    finished_at = Column(DateTime)
    items_processed = Column(Integer, default=0)
    summary = Column(Text)


class AgentActivityLog(Base):
    __tablename__ = "agent_activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(Integer, ForeignKey("agent_runs.id"), nullable=True)
    agent_name = Column(String(100), nullable=False)
    log_level = Column(String(20), default="INFO")
    action = Column(String(100), nullable=False)
    details = Column(Text)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)


class ConnectorHealth(Base):
    __tablename__ = "connector_health"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("job_sources.id"), nullable=False)
    status = Column(String(50), nullable=False)
    ping_ms = Column(Float)
    details = Column(Text)
    checked_at = Column(DateTime, default=datetime.datetime.utcnow)

    source = relationship("JobSource", back_populates="health_logs")


class UserSettings(Base):
    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    min_match_score = Column(Float, default=70.0)
    min_ats_score = Column(Float, default=85.0) # TARGET 85-95 THRESHOLD
    dry_run_mode = Column(Boolean, default=True)
    auto_apply_enabled = Column(Boolean, default=False)
    hybrid_approval_threshold = Column(Float, default=80.0)
    max_experience_years = Column(Float, default=2.0)
    fresher_only = Column(Boolean, default=True)
    primary_ollama_model = Column(String(100), default="llama3.2:3b")
    email_alerts = Column(Boolean, default=True)
    whatsapp_alerts = Column(Boolean, default=False)
    telegram_alerts = Column(Boolean, default=False)
    voice_enabled = Column(Boolean, default=True)
    jarvis_voice_rate = Column(Integer, default=175)
    parebo_portal_url = Column(String(500), default="")
    preferred_template_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    user = relationship("User", back_populates="settings")


class CommandTask(Base):
    __tablename__ = "command_tasks"

    id = Column(Integer, primary_key=True, index=True)
    task_uuid = Column(String(100), unique=True, index=True, nullable=False)
    raw_command = Column(Text, nullable=False)
    transcription = Column(Text)
    intent = Column(String(100), nullable=False)
    parameters = Column(JSON, default=dict)
    status = Column(String(50), default="QUEUED")
    progress = Column(Integer, default=0)
    spoken_summary = Column(Text)
    result_data = Column(JSON, default=dict)
    error_message = Column(Text)
    started_at = Column(DateTime, default=datetime.datetime.utcnow)
    completed_at = Column(DateTime)


class CommandConversation(Base):
    __tablename__ = "command_conversations"

    id = Column(Integer, primary_key=True, index=True)
    role = Column(String(20), nullable=False)
    message = Column(Text, nullable=False)
    audio_url = Column(String(500))
    task_id = Column(Integer, ForeignKey("command_tasks.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class FollowUpReminder(Base):
    __tablename__ = "follow_up_reminders"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id"), nullable=False)
    due_date = Column(DateTime, nullable=False)
    status = Column(String(50), default="Pending")
    reminder_note = Column(Text)
    spoken_prompt = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    application = relationship("Application", back_populates="reminders")

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from database.database import engine, Base, SessionLocal
from database import crud, models
from database.schemas import UserCreate
from backend.authentication.auth import get_password_hash
from backend.api import auth, profile, settings as settings_api, jobs, applications, commands, agent_control, master_resume, templates, ats, resume_downloads, system, websockets

# Create all database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI JOB HUNTER – Autonomous Agent API",
    description="Autonomous IT Job Search, ATS Resume Generation, Hybrid Auto-Apply, and Jarvis Command Center",
    version="1.0.0"
)

# Enable CORS for local Vite dev server and PWA
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(profile.router, prefix="/api/v1")
app.include_router(settings_api.router, prefix="/api/v1")
app.include_router(jobs.router, prefix="/api/v1")
app.include_router(applications.router, prefix="/api/v1")
app.include_router(commands.router, prefix="/api/v1")
app.include_router(agent_control.router, prefix="/api/v1")
app.include_router(master_resume.router, prefix="/api/v1")
app.include_router(templates.router, prefix="/api/v1")
app.include_router(ats.router, prefix="/api/v1")
app.include_router(resume_downloads.router, prefix="/api/v1")
app.include_router(system.router, prefix="/api/v1")
app.include_router(websockets.router, prefix="/api/v1")

# Mount Static Assets & PWA
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

SAMPLE_FRESHER_JOBS = [
    {
        "requisition_id": "REQ-PY-2026-01",
        "company_name": "Cognizant Technology Solutions",
        "job_title": "Programmer Analyst Trainee (Python / AI)",
        "job_description": "Looking for 2026 B.Tech freshers with strong Python fundamentals, REST APIs, OOP principles, and exposure to AI/ML or LLM applications. Freshers explicitly eligible.",
        "job_role_category": "Python Developer",
        "location": "Hyderabad, Telangana",
        "work_mode": "Hybrid",
        "salary_advertised": "4.5 LPA",
        "bonus_and_benefits": "Health insurance, performance bonus, continuous learning stipend",
        "job_type": "Full-time",
        "experience_required": "0-1 years (Freshers Accepted)",
        "min_exp_years": 0.0,
        "max_exp_years": 1.0,
        "is_fresher_eligible": True,
        "eligibility_reason": "Entry-level engineering trainee role targeting 2026 graduates.",
        "source_name": "Naukri",
        "job_url": "https://naukri.com/job-listings-python-trainee-cognizant",
        "mandatory_skills": ["Python", "OOP", "SQL", "REST APIs"],
        "preferred_skills": ["FastAPI", "Docker", "Git"]
    },
    {
        "requisition_id": "REQ-AI-2026-02",
        "company_name": "InnovateAI Labs (Codegnan Partner)",
        "job_title": "Associate Agentic AI Engineer",
        "job_description": "Join our AI research and agent team. Developing multi-agent systems, RAG retrieval pipelines, voice bots, and tool-calling agents with LangChain and FastAPI.",
        "job_role_category": "AI Engineer",
        "location": "Hyderabad, Telangana",
        "work_mode": "Hybrid",
        "salary_advertised": "6.0 - 7.5 LPA",
        "bonus_and_benefits": "Flexible work hours, GPU compute allowance, hackathon sponsorships",
        "job_type": "Full-time",
        "experience_required": "0-2 years (Freshers with hands-on projects encouraged)",
        "min_exp_years": 0.0,
        "max_exp_years": 2.0,
        "is_fresher_eligible": True,
        "eligibility_reason": "Project-based entry-level role accepting fresh graduates with demonstrated Agentic AI skills.",
        "source_name": "Telegram",
        "job_url": "https://t.me/techjobsindia/4892",
        "mandatory_skills": ["Python", "Agentic AI", "LangChain", "RAG", "FastAPI"],
        "preferred_skills": ["ChromaDB", "Prompt Engineering", "Speech AI"]
    },
    {
        "requisition_id": "REQ-VOICE-2026-03",
        "company_name": "VoiceVani Systems",
        "job_title": "Junior Speech & NLP Engineer",
        "job_description": "Building multilingual Indian speech agents, speech-in speech-out pipelines, and intent recognition models across Indian regional languages.",
        "job_role_category": "NLP Engineer",
        "location": "Bengaluru / Hyderabad (Remote Allowed)",
        "work_mode": "Remote",
        "salary_advertised": "5.5 LPA",
        "bonus_and_benefits": "Remote workstation setup allowance, health cover",
        "job_type": "Full-time",
        "experience_required": "0-1 years",
        "min_exp_years": 0.0,
        "max_exp_years": 1.0,
        "is_fresher_eligible": True,
        "eligibility_reason": "Freshers with speech AI / NLP projects like VoiceEra are direct fits.",
        "source_name": "LinkedIn",
        "job_url": "https://linkedin.com/jobs/view/4100998877",
        "mandatory_skills": ["Python", "Speech AI", "NLP", "REST APIs"],
        "preferred_skills": ["Flask", "FastAPI", "Multilingual NLP"]
    },
    {
        "requisition_id": "REQ-BE-2026-04",
        "company_name": "FinTech Matrix",
        "job_title": "Junior Backend Developer (Python / FastAPI)",
        "job_description": "Seeking fresher backend engineer to design REST APIs, PostgreSQL queries, budget tracking logic, and caching layers for financial applications.",
        "job_role_category": "Backend Developer",
        "location": "Hyderabad, Telangana",
        "work_mode": "On-site",
        "salary_advertised": "5.0 LPA",
        "bonus_and_benefits": "Annual performance bonus, medical coverage",
        "job_type": "Full-time",
        "experience_required": "0-1 years",
        "min_exp_years": 0.0,
        "max_exp_years": 1.0,
        "is_fresher_eligible": True,
        "eligibility_reason": "Entry-level backend position.",
        "source_name": "Indeed",
        "job_url": "https://indeed.com/viewjob?jk=fintechbackend2026",
        "mandatory_skills": ["Python", "FastAPI", "SQL", "PostgreSQL"],
        "preferred_skills": ["Docker", "Git", "Pytest"]
    },
    {
        "requisition_id": "REQ-INT-2026-05",
        "company_name": "TCS (Tata Consultancy Services)",
        "job_title": "Assistant System Engineer Trainee",
        "job_description": "TCS National Qualifier Test (NQT) entry-level software engineer trainee role. Training in enterprise software development, testing, and modern Python systems.",
        "job_role_category": "Software Engineer",
        "location": "Hyderabad / Pan India",
        "work_mode": "Hybrid",
        "salary_advertised": "4.0 - 7.0 LPA (Ninja / Digital / Prime)",
        "bonus_and_benefits": "Relocation assistance, health insurance, provident fund",
        "job_type": "Full-time",
        "experience_required": "0 years (2026 Batch Graduates Only)",
        "min_exp_years": 0.0,
        "max_exp_years": 0.0,
        "is_fresher_eligible": True,
        "eligibility_reason": "Campus / Off-campus fresher batch 2026 eligibility.",
        "source_name": "Company Careers",
        "job_url": "https://careers.tcs.com/jobs/nqt-2026",
        "mandatory_skills": ["Python", "Java", "SQL", "OOP"],
        "preferred_skills": ["Data Structures", "Algorithms"]
    }
]

@app.on_event("startup")
def startup_event():
    # Initialize default candidate account
    db = SessionLocal()
    try:
        user = crud.get_user_by_email(db, "candidate@example.com")
        if not user:
            new_user = crud.create_user(
                db=db,
                user=UserCreate(
                    email="candidate@example.com",
                    password="Password@123",
                    full_name="Candidate"
                ),
                hashed_password=get_password_hash("Password@123")
            )
            crud.seed_candidate_profile_from_json(db, new_user.id)
            user = new_user
            print("Initialized default candidate account.")

        profile = crud.get_candidate_profile(db, user.id)

        # Seed sample fresher jobs if DB has few jobs
        existing_jobs_count = db.query(models.Job).count()
        if existing_jobs_count < 3:
            for sj in SAMPLE_FRESHER_JOBS:
                exists = db.query(models.Job).filter(models.Job.requisition_id == sj["requisition_id"]).first()
                if not exists:
                    job = models.Job(
                        requisition_id=sj["requisition_id"],
                        company_name=sj["company_name"],
                        job_title=sj["job_title"],
                        job_description=sj["job_description"],
                        job_role_category=sj["job_role_category"],
                        is_it_role=True,
                        location=sj["location"],
                        work_mode=sj["work_mode"],
                        salary_advertised=sj["salary_advertised"],
                        bonus_and_benefits=sj["bonus_and_benefits"],
                        job_type=sj["job_type"],
                        experience_required=sj["experience_required"],
                        min_exp_years=sj["min_exp_years"],
                        max_exp_years=sj["max_exp_years"],
                        is_fresher_eligible=sj["is_fresher_eligible"],
                        eligibility_reason=sj["eligibility_reason"],
                        job_url=sj["job_url"],
                        source_name=sj["source_name"],
                        status="Discovered"
                    )
                    db.add(job)
                    db.commit()
                    db.refresh(job)

                    # Add requirements
                    req = models.JobRequirement(
                        job_id=job.id,
                        mandatory_skills=sj["mandatory_skills"],
                        preferred_skills=sj["preferred_skills"]
                    )
                    db.add(req)

                    # Calculate and attach match
                    match_data = matching_engine.compute_match(sj, profile)
                    job_match = models.JobMatch(
                        job_id=job.id,
                        overall_score=match_data["overall_score"],
                        category_fit=match_data["category_fit"],
                        technical_skills_score=match_data["technical_skills_score"],
                        fresher_eligibility_score=match_data["fresher_eligibility_score"],
                        project_relevance_score=match_data["project_relevance_score"],
                        education_score=match_data["education_score"],
                        experience_score=match_data["experience_score"],
                        location_score=match_data["location_score"],
                        certifications_score=match_data["certifications_score"],
                        matched_skills=match_data["matched_skills"],
                        missing_skills=match_data["missing_skills"],
                        relevant_projects=match_data["relevant_projects"],
                        strengths=match_data["strengths"],
                        weaknesses=match_data["weaknesses"],
                        recommendation=match_data["recommendation"]
                    )
                    db.add(job_match)
                    db.commit()
            print("Seeded top fresher opportunities with explainable match scores.")
    finally:
        db.close()

@app.get("/")
def serve_dashboard():
    index_file = os.path.join(os.path.dirname(__file__), "static", "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {
        "status": "online",
        "service": "AI JOB HUNTER – Autonomous IT Job Search Agent",
        "version": "1.0.0",
        "api_docs": "/docs"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "AI JOB HUNTER"}

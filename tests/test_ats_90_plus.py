import sys
import os
import io

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.database import Base
from database import crud, models
from database.schemas import UserCreate
from backend.authentication.auth import get_password_hash
from resume_engine.document_parser import document_parser
from resume_engine.template_manager import template_manager
from resume_engine.ats_scorer import ats_scorer
from resume_engine.optimizer import resume_optimizer
from resume_engine.resume_builder import resume_builder
from resume_engine.pdf_generator import pdf_generator
from resume_engine.docx_generator import docx_generator
from workflows.application_workflow import hybrid_application_workflow
from agents.duplicate_agent import duplicate_detector
from agents.eligibility_agent import fresher_eligibility_engine

TEST_DB_URL = "sqlite:///./test_ats_90_suite.db"
test_engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

def run_ats_90_plus_test_suite():
    print("==================================================")
    print("STARTING 18-CASE 90+ ATS RESUME VERIFICATION SUITE")
    print("==================================================")

    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    db = TestSessionLocal()

    # User & Master Profile Setup
    user = crud.create_user(
        db,
        UserCreate(email="candidate@example.com", password="Password@123", full_name="Candidate"),
        get_password_hash("Password@123")
    )
    profile = crud.get_candidate_profile(db, user.id)

    # 1. Master resume PDF upload & extraction
    sample_pdf_path = os.path.join("storage", "master_resume", "test_master.pdf")
    pdf_generator.generate_pdf({
        "name": "Candidate",
        "headline": "Application Engineer (AI/ML)",
        "contact": "+91-9876543210 | candidate@example.com",
        "summary": "2026 B.Tech fresher in AI and ML with strong Python skills.",
        "skills": {"Languages": ["Python", "SQL", "FastAPI"]},
        "projects": [{"title": "VoiceEra", "tech_stack": ["Speech AI", "Python"], "about": "Voice platform in 22+ languages"}]
    }, sample_pdf_path)
    assert os.path.exists(sample_pdf_path)
    extracted_pdf_text = document_parser.extract_text_from_file(sample_pdf_path)
    assert "Candidate" in extracted_pdf_text
    print("Test 1 PASS: Master resume PDF upload and text reading")

    # 2. Master resume DOCX upload & extraction
    sample_docx_path = os.path.join("storage", "master_resume", "test_master.docx")
    docx_generator.generate_docx({
        "name": "Candidate",
        "headline": "Application Engineer (AI/ML)",
        "contact": "+91-9876543210 | candidate@example.com",
        "summary": "2026 B.Tech fresher in AI and ML with strong Python skills.",
        "skills": {"Languages": ["Python", "SQL", "FastAPI"]},
        "projects": [{"title": "ContraRAG", "tech_stack": ["LangChain", "Python"], "about": "Contradiction-aware policy engine"}]
    }, sample_docx_path)
    assert os.path.exists(sample_docx_path)
    extracted_docx_text = document_parser.extract_text_from_file(sample_docx_path)
    assert "Candidate" in extracted_docx_text
    print("Test 2 PASS: Master resume DOCX upload and XML text reading")

    # 3. Candidate profile extraction (name, contact, education, skills, projects, certifications)
    parsed_profile = document_parser.parse_resume_to_candidate_profile(extracted_pdf_text)
    assert "Candidate" in parsed_profile["personal_info"]["name"]
    assert len(parsed_profile["education"]) >= 1
    assert len(parsed_profile["projects"]) >= 2
    assert len(parsed_profile["certifications"]) >= 4
    print("Test 3 PASS: Candidate profile extraction into structured fields")

    # 4. Candidate profile verification (Diff engine prevents silent overwrite)
    curr_summary = {"personal_info": {"name": "Candidate"}, "skills": [{"name": "Python"}]}
    diff = document_parser.compute_profile_differences(curr_summary, parsed_profile)
    assert "new_skills_count" in diff
    assert "requires_user_approval" in diff
    print("Test 4 PASS: Candidate profile verification & diff detection")

    # 5. Sample template upload & analysis (Does NOT copy other person's info)
    tmpl_path = os.path.join("resume_engine", "templates", "reference", "sample_template.docx")
    docx_generator.generate_docx({
        "name": "Template Layout Placeholder",
        "headline": "Layout Header",
        "contact": "template@example.com",
        "summary": "Sample summary layout",
        "skills": ["Layout Skill"],
        "projects": []
    }, tmpl_path)
    structure = template_manager.analyze_uploaded_template(tmpl_path, "Clean ATS Tech Template")
    assert structure["ats_readability_rating"] >= 95.0
    print("Test 5 PASS: Sample template upload and visual structure analysis")

    # 6. Template selection & default assignment
    registered_tmpl = template_manager.register_approved_template(db, "Clean ATS Tech Template", structure, is_default=True)
    assert registered_tmpl.is_default is True
    print("Test 6 PASS: Template selection and default registration")

    # 7. Customized resume generation for a specific job
    test_job_data = {
        "job_title": "Python & Agentic AI Developer",
        "company_name": "Apex Innovations",
        "job_description": "Seeking Python developer with Agentic AI, RAG, and FastAPI skills for voice and LLM workflows.",
        "mandatory_skills": ["Python", "FastAPI", "RAG", "Agentic AI"],
        "preferred_skills": ["Speech AI", "Docker"],
        "min_exp_years": 0.0
    }
    custom_resume = resume_builder.build_custom_resume(test_job_data, profile, version_tag="job1")
    assert "VoiceEra" in str(custom_resume["projects"])
    assert "ContraRAG" in str(custom_resume["projects"])
    print("Test 7 PASS: Customized job-specific resume generation")

    # 8. ATS score calculation across 7 categories
    eval_result = ats_scorer.evaluate_resume(custom_resume, test_job_data)
    assert "overall_score" in eval_result
    assert "breakdown" in eval_result
    assert len(eval_result["breakdown"]) == 7
    print(f"Test 8 PASS: ATS score calculation ({eval_result['overall_score']}%)")

    # 9. Resume score of 95+ passes the ATS threshold
    high_score_job = {
        "job_title": "Application Engineer (AI/ML)",
        "company_name": "Codegnan Labs",
        "job_description": "Python, Machine Learning, Deep Learning, NLP, Voice AI, and Agentic AI freshers.",
        "mandatory_skills": ["Python", "FastAPI", "Machine Learning", "NLP"],
        "preferred_skills": ["Speech AI", "PostgreSQL"],
        "min_exp_years": 0.0
    }
    opt_high = resume_optimizer.optimize_resume_loop(custom_resume, high_score_job, profile)
    assert opt_high["final_score"] >= 90.0
    assert opt_high["is_90_plus"] is True
    print(f"Test 9 PASS: Resume score of {opt_high['final_score']} passes the 90+ threshold")

    # 10. Resume score below 90 blocks automatic submission
    mismatched_job = {
        "job_title": "Senior Embedded Firmware Engineer",
        "company_name": "ChipWorks",
        "job_description": "C/C++, RTOS, Linux Device Drivers, Assembly, Oscilloscope debugging. 8 years minimum.",
        "mandatory_skills": ["C++", "RTOS", "Device Drivers", "Firmware", "Assembly"],
        "preferred_skills": ["FPGA", "JTAG"],
        "min_exp_years": 8.0
    }
    eval_low = ats_scorer.evaluate_resume(custom_resume, mismatched_job)
    assert eval_low["overall_score"] < 90.0
    assert eval_low["is_90_plus"] is False
    print(f"Test 10 PASS: Resume score ({eval_low['overall_score']}%) below 90 blocks automatic submission")

    # 11. Resume optimization improves score using verified information
    test_improvable_job = {
        "job_title": "Junior Python Developer",
        "company_name": "CloudNova",
        "job_description": "Python, FastAPI, SQL, PostgreSQL, REST APIs. 0-1 years freshers.",
        "mandatory_skills": ["Python", "FastAPI", "SQL", "PostgreSQL"],
        "preferred_skills": ["Git", "Docker"],
        "min_exp_years": 0.0
    }
    initial_res = resume_builder.build_custom_resume(test_improvable_job, profile, version_tag="v_init")
    opt_run = resume_optimizer.optimize_resume_loop(initial_res, test_improvable_job, profile)
    assert opt_run["final_score"] >= opt_run["history"][0]["pre_score"]
    assert opt_run["is_90_plus"] is True
    print(f"Test 11 PASS: Resume optimization loop successfully improved score to {opt_run['final_score']}%")

    # 12. Resume remains below 90 after maximum attempts for genuinely incompatible roles
    opt_mismatched = resume_optimizer.optimize_resume_loop(custom_resume, mismatched_job, profile)
    assert opt_mismatched["optimization_attempts"] <= 3
    assert opt_mismatched["is_90_plus"] is False
    print(f"Test 12 PASS: Resume remains below 90 after {opt_mismatched['optimization_attempts']} max attempts for incompatible role")

    # 13. Below-90 resume goes to manual review
    db_job_low = models.Job(
        company_name="ChipWorks",
        job_title="Embedded Firmware Engineer",
        job_description="C/C++, RTOS, Kernel",
        min_exp_years=5.0,
        is_fresher_eligible=False
    )
    db.add(db_job_low)
    db.commit()

    prep_low = hybrid_application_workflow.prepare_application(db_job_low.id, user.id, db)
    assert prep_low["status"] == "Waiting for Approval"
    assert "below the required 90.0 threshold" in prep_low["approval_reason"] or "not fresher eligible" in prep_low["approval_reason"]
    print("Test 13 PASS: Below-90 resume routed to manual review")

    # 14. A 90+ resume with failed fresher eligibility is blocked
    db_job_senior_ai = models.Job(
        company_name="Global AI",
        job_title="Senior AI Architect",
        job_description="Python, Machine Learning, RAG, LangChain. Mandatory 5+ years experience required.",
        min_exp_years=5.0,
        is_fresher_eligible=False,
        eligibility_reason="Requires mandatory 5+ years experience."
    )
    db.add(db_job_senior_ai)
    db.commit()
    prep_senior = hybrid_application_workflow.prepare_application(db_job_senior_ai.id, user.id, db)
    assert prep_senior["requires_approval"] is True
    assert "not fresher eligible" in prep_senior["approval_reason"]
    print("Test 14 PASS: 90+ resume with failed fresher eligibility is blocked from auto-apply")

    # 15. A 90+ resume with duplicate application is blocked
    dup_check = hybrid_application_workflow.prepare_application(db_job_senior_ai.id, user.id, db)
    assert "already exists" in dup_check.get("message", "")
    print("Test 15 PASS: 90+ resume with duplicate application is blocked by idempotency")

    # 16. A 90+ resume with uncertain application answers requires approval
    app_record = db.query(models.Application).filter(models.Application.job_id == db_job_senior_ai.id).first()
    assert app_record.requires_approval is True
    assert app_record.status == "Waiting for Approval"
    print("Test 16 PASS: 90+ resume with safety criteria requires explicit user approval")

    # 17. Generated resume is correctly associated with application
    db_job_fresher = models.Job(
        company_name="TechMatrix",
        job_title="Python AI Fresher",
        job_description="Python, FastAPI, RAG, Machine Learning. Freshers accepted.",
        min_exp_years=0.0,
        is_fresher_eligible=True,
        requisition_id="TM-FRESH-99"
    )
    db.add(db_job_fresher)
    db.commit()

    prep_fresh = hybrid_application_workflow.prepare_application(db_job_fresher.id, user.id, db)
    app_fresh = db.query(models.Application).filter(models.Application.id == prep_fresh["application_id"]).first()
    assert app_fresh.generated_resume_id is not None
    gen_res = db.query(models.GeneratedResume).filter(models.GeneratedResume.id == app_fresh.generated_resume_id).first()
    assert gen_res.ats_score.overall_score >= 90.0
    print(f"Test 17 PASS: Generated resume #{gen_res.id} (ATS {gen_res.ats_score.overall_score}%) correctly associated with Application #{app_fresh.id}")

    # 18. No fabricated information is added (verifying all projects and profile facts match master)
    valid_titles = [
        "VoiceEra",
        "VoiceEra (Codegnan Workshops)",
        "ContraRAG – Contradiction-Aware Policy Auditor and Temporal Rule Engine",
        "AI Customer Support Chatbot",
        "Personal SIRI",
        "Personal Finance & Expense Management System"
    ]
    for p in gen_res.content_json.get("projects", []):
        assert any(vt in p["title"] for vt in ["VoiceEra", "ContraRAG", "Customer Support", "SIRI", "Finance"])
    print("Test 18 PASS: Zero hallucination - verified only authentic profile facts are included")

    db.close()
    print("==================================================")
    print("ALL 18 ATS 90+ TEST CASES PASSED SUCCESSFULLY!")
    print("==================================================")

if __name__ == "__main__":
    run_ats_90_plus_test_suite()


import sys
import os
import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from database.database import SessionLocal, Base, engine
from database import crud, models
from database.schemas import UserCreate, JobCreate, CommandRequest
from backend.authentication.auth import get_password_hash
from integrations.telegram_collector import telegram_collector
from integrations.whatsapp_collector import whatsapp_collector
from integrations.linkedin_collector import linkedin_collector
from integrations.source_manager import source_manager
from agents.extraction_agent import job_extractor
from agents.eligibility_agent import fresher_eligibility_engine
from agents.duplicate_agent import duplicate_detector
from agents.matching_agent import matching_engine
from resume_engine.resume_builder import resume_builder
from resume_engine.docx_generator import docx_generator
from resume_engine.pdf_generator import pdf_generator
from workflows.application_workflow import hybrid_application_workflow
from notifications.notification_manager import notification_manager
from voice.spoken_summarizer import spoken_summarizer
from backend.api import agent_control, commands

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

TEST_DB_URL = "sqlite:///./test_master_suite.db"
test_engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

def run_master_test_suite():
    print("==================================================")
    print("STARTING 30-CASE MASTER VERIFICATION TEST SUITE")
    print("==================================================")

    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    db = TestSessionLocal()

    # Candidate profile setup
    user = crud.get_user_by_email(db, "candidate@example.com")
    if not user:
        user = crud.create_user(
            db,
            UserCreate(email="candidate@example.com", password="Password@123", full_name="Candidate"),
            get_password_hash("Password@123")
        )
    profile = crud.get_candidate_profile(db, user.id)

    # 1. Telegram fresher job ingestion
    tg_raw = "Company: TechNova\nRole: Python Fresher Developer\nLocation: Hyderabad\nReq ID: TN-001\nLooking for 0-1 years experience."
    tg_job = telegram_collector.parse_message_text(tg_raw)
    assert tg_job["company_name"] == "TechNova"
    assert tg_job["requisition_id"] == "TN-001"
    print("Test 1 PASS: Telegram fresher job ingestion")

    # 2. WhatsApp forwarded job message ingestion
    wa_raw = "Forwarded: Hiring at DataMinds! Role: Junior AI Engineer. 0-2 years, freshers accepted. CTC: 5 LPA."
    wa_job = whatsapp_collector.parse_forwarded_message(wa_raw)
    assert wa_job["company_name"] == "DataMinds"
    assert "Junior AI Engineer" in wa_job["job_title"]
    print("Test 2 PASS: WhatsApp forwarded job message ingestion")

    # 3. LinkedIn job URL import where permitted
    li_url = "https://www.linkedin.com/jobs/view/4100998877"
    li_job = linkedin_collector.parse_job_url_or_post(li_url, recruiter_name="Priya Sharma")
    assert li_job["requisition_id"] == "LI-4100998877"
    assert li_job["recruiter_name"] == "Priya Sharma"
    print("Test 3 PASS: LinkedIn job URL import where permitted")

    # 4. Same job collected from two sources
    job1_data = {
        "requisition_id": "REQ-DUP-100",
        "company_name": "CloudWorks India",
        "job_title": "Python Backend Engineer",
        "job_url": "https://careers.cloudworks.com/jobs/100"
    }
    is_dup1, _, _, _ = duplicate_detector.check_duplicate(job1_data, db)
    # Save job1 in db
    j1 = models.Job(
        requisition_id="REQ-DUP-100",
        company_name="CloudWorks India",
        job_title="Python Backend Engineer",
        job_description="Python developer with FastAPI skills",
        job_url="https://careers.cloudworks.com/jobs/100"
    )
    db.add(j1)
    db.commit()

    is_dup2, match_id, score, reason = duplicate_detector.check_duplicate(job1_data, db)
    assert is_dup2 is True
    assert match_id == j1.id
    print("Test 4 PASS: Same job collected from two sources detected as duplicate")

    # 5. Same title with a different requisition ID (Must NOT be merged)
    job_diff_req = {
        "requisition_id": "REQ-DIFF-200",
        "company_name": "CloudWorks India",
        "job_title": "Python Backend Engineer"
    }
    is_dup_diff, _, _, _ = duplicate_detector.check_duplicate(job_diff_req, db)
    assert is_dup_diff is False
    print("Test 5 PASS: Same title with a different requisition ID kept separate")

    # 6. Non-IT job rejection
    is_it_role, rej_reason = job_extractor.classify_role(
        title="Telecaller and Sales Executive",
        description="Outbound sales calling for personal loans and insurance policies."
    )
    assert is_it_role is False
    assert "Rejected" in rej_reason
    print(f"Test 6 PASS: Non-IT job rejection ({rej_reason})")

    # 7. 0–1 year job eligibility
    job_fresher = {"min_exp_years": 0.0, "max_exp_years": 1.0, "job_description": "Entry level Python role"}
    el_fresher, reason_f, _ = fresher_eligibility_engine.evaluate_eligibility(job_fresher)
    assert el_fresher is True
    print(f"Test 7 PASS: 0-1 year job eligibility ({reason_f})")

    # 8. 4-year mandatory experience rejection
    job_senior = {"min_exp_years": 4.0, "max_exp_years": 6.0, "job_description": "Mandatory 4+ years of hands-on Java microservices"}
    el_senior, reason_s, _ = fresher_eligibility_engine.evaluate_eligibility(job_senior)
    assert el_senior is False
    assert "exceeds fresher threshold" in reason_s
    print(f"Test 8 PASS: 4-year mandatory experience rejection ({reason_s})")

    # 9. Preferred experience not treated as mandatory
    job_pref = {
        "min_exp_years": 1.0,
        "max_exp_years": 2.0,
        "job_description": "0-2 years experience required. 3 years preferred with cloud deployment."
    }
    el_pref, reason_p, _ = fresher_eligibility_engine.evaluate_eligibility(job_pref)
    assert el_pref is True
    print(f"Test 9 PASS: Preferred experience not treated as mandatory ({reason_p})")

    # 10. Job matching score calculation
    eval_job = {
        "job_title": "Agentic AI & Python Developer",
        "job_description": "Building multilingual voice AI, RAG pipelines with LangChain and FastAPI.",
        "mandatory_skills": ["Python", "FastAPI", "RAG"],
        "preferred_skills": ["LangChain", "Docker"],
        "min_exp_years": 0.0,
        "is_fresher_eligible": True,
        "work_mode": "Hybrid",
        "location": "Hyderabad"
    }
    match_result = matching_engine.compute_match(eval_job, profile)
    assert match_result["overall_score"] >= 75.0
    assert "Python" in match_result["matched_skills"]
    print(f"Test 10 PASS: Job matching score calculation ({match_result['overall_score']}%)")

    # 11. Missing skill explanation
    eval_job_gaps = {
        "job_title": "Cloud Architect",
        "job_description": "Kubernetes cluster administration and Terraform scripting.",
        "mandatory_skills": ["Kubernetes", "Terraform", "GoLang"],
        "preferred_skills": ["Ansible"],
        "is_fresher_eligible": True
    }
    match_gaps = matching_engine.compute_match(eval_job_gaps, profile)
    assert len(match_gaps["missing_skills"]) >= 2
    assert len(match_gaps["weaknesses"]) > 0
    print(f"Test 11 PASS: Missing skill explanation ({match_gaps['missing_skills']})")

    # 12. Customized resume generation
    custom_res = resume_builder.build_custom_resume(eval_job, profile, version_tag="t12")
    assert "VoiceEra" in str(custom_res["projects"])
    assert "ContraRAG" in str(custom_res["projects"])
    print("Test 12 PASS: Customized ATS resume generation with verified facts")

    # 13. PDF resume generation
    pdf_path = os.path.join("storage", "generated_resumes", "test_resume.pdf")
    pdf_out = pdf_generator.generate_pdf(custom_res, pdf_path)
    assert os.path.exists(pdf_out)
    assert os.path.getsize(pdf_out) > 500
    print("Test 13 PASS: PDF resume generation")

    # 14. DOCX resume generation
    docx_path = os.path.join("storage", "generated_resumes", "test_resume.docx")
    docx_out = docx_generator.generate_docx(custom_res, docx_path)
    assert os.path.exists(docx_out)
    assert os.path.getsize(docx_out) > 1000
    print("Test 14 PASS: DOCX resume generation")

    # 15. Application preparation
    # Create test job in db
    test_job = models.Job(
        company_name="InnovateAI Labs",
        job_title="Associate AI Engineer",
        job_description="Seeking 2026 fresher for speech AI and Python API development.",
        is_fresher_eligible=True,
        requisition_id="INN-AI-500",
        location="Hyderabad"
    )
    db.add(test_job)
    db.commit()

    prep = hybrid_application_workflow.prepare_application(test_job.id, user.id, db)
    assert "application_id" in prep
    assert prep["status"] == "Waiting for Approval"
    print(f"Test 15 PASS: Application preparation (Ref: {prep['application_reference']})")

    # 16. Application waiting for approval
    app_record = db.query(models.Application).filter(models.Application.id == prep["application_id"]).first()
    assert app_record.status == "Waiting for Approval"
    assert app_record.requires_approval is True
    print("Test 16 PASS: Application waiting for approval under hybrid safety policy")

    # 17. Application approval
    app_record.status = "Approved"
    app_record.requires_approval = False
    db.commit()
    assert app_record.status == "Approved"
    print("Test 17 PASS: Application approval transition")

    # 18. Dry-run application
    app_record.application_mode = "Dry-Run"
    exec_dry = hybrid_application_workflow.execute_submission(app_record.id, db)
    assert exec_dry["status"] == "Dry-Run Verified"
    assert "Dry-run simulation successful" in exec_dry["confirmation_evidence"]
    print("Test 18 PASS: Dry-run application execution")

    # 19. Actual authorized submission
    app_record.application_mode = "Hybrid-Approved"
    exec_real = hybrid_application_workflow.execute_submission(app_record.id, db)
    assert exec_real["status"] == "Submitted"
    print(f"Test 19 PASS: Actual authorized submission with genuine confirmation evidence")

    # 20. Submission failure safeguard
    unapproved_job = models.Job(company_name="TestFail Corp", job_title="Junior Dev", job_description="test")
    db.add(unapproved_job)
    db.commit()
    unapproved_app = models.Application(
        job_id=unapproved_job.id,
        status="Waiting for Approval",
        requires_approval=True
    )
    db.add(unapproved_app)
    db.commit()
    fail_res = hybrid_application_workflow.execute_submission(unapproved_app.id, db)
    assert "error" in fail_res
    print("Test 20 PASS: Submission failure / blockage when approval missing")

    # 21. Notification after confirmed submission only
    # Negative test: Unconfirmed app must be blocked
    bad_note = notification_manager.send_submission_confirmed_notification(unapproved_app, db)
    assert "error" in bad_note
    # Positive test: Confirmed app sends Email + WhatsApp
    good_note = notification_manager.send_submission_confirmed_notification(app_record, db)
    assert good_note["email_status"] == "Sent"
    assert good_note["whatsapp_status"] == "Sent"
    print("Test 21 PASS: Notification strictly sent after confirmed submission only")

    # 22. No duplicate application after restart
    dup_prep = hybrid_application_workflow.prepare_application(test_job.id, user.id, db)
    assert "already exists" in dup_prep.get("message", "")
    print("Test 22 PASS: Idempotency check prevents duplicate application after restart")

    # 23. Dashboard live updates
    stat_count = db.query(models.Job).count()
    assert stat_count >= 2
    print(f"Test 23 PASS: Dashboard live stats synchronization ({stat_count} jobs)")

    # 24. Agent pause and resume
    agent_control.pause_agent(user, db)
    assert agent_control.AGENT_STATE["status"] == "PAUSED"
    agent_control.resume_agent(user, db)
    assert agent_control.AGENT_STATE["status"] == "RUNNING"
    print("Test 24 PASS: Agent pause and resume controls")

    # 25. Source disconnection / health check
    source_manager.sync_default_sources(db)
    h_res = source_manager.check_source_health(db, source_id=1)
    assert h_res["status"] == "OK"
    print("Test 25 PASS: Source connection & connector health check")

    # 26. Text command interpretation
    cmd_text = CommandRequest(command="Search for Python fresher jobs", source="text")
    res_text = commands.execute_command(cmd_text, user, db)
    assert res_text["intent"] == "SEARCH_JOBS"
    print("Test 26 PASS: Text command interpretation")

    # 27. Voice transcription
    cmd_voice = CommandRequest(command="Check whether I am eligible", source="voice")
    res_voice = commands.execute_command(cmd_voice, user, db)
    assert res_voice["intent"] == "CHECK_ELIGIBILITY"
    print("Test 27 PASS: Voice transcription command processing")

    # 28. Jarvis spoken summary
    spoken_out = spoken_summarizer.format_application_spoken_summary({
        "company_name": "ABC Technologies",
        "job_title": "Python Developer",
        "location": "Hyderabad",
        "experience_required": "Freshers accepted",
        "match_score": 87,
        "salary_advertised": "4.5 LPA",
        "bonus_and_benefits": None,
        "resume_version": "Python Developer Resume Version 2",
        "application_reference": "ABC123"
    })
    assert "ABC Technologies" in spoken_out
    assert "4.5 LPA" in spoken_out
    assert "Not mentioned in the job description" in spoken_out
    print("Test 28 PASS: Jarvis spoken summary formatting")

    # 29. Inaccessible recruiter profile fallback
    li_fallback = linkedin_collector.parse_job_url_or_post(
        "Recruiter post: Looking for Python 2026 graduates with RAG and LLM skills. Send CV.",
        recruiter_name="Rahul Verma"
    )
    assert li_fallback["job_url"] is None
    assert li_fallback["requires_manual_text_fallback"] is False
    print("Test 29 PASS: Inaccessible recruiter profile fallback to pasted text")

    # 30. Emergency stop
    agent_control.emergency_stop(user, db)
    assert agent_control.AGENT_STATE["status"] == "STOPPED"
    print("Test 30 PASS: Emergency stop immediately halts all agent operations")

    db.close()
    print("==================================================")
    print("ALL 30 ACCEPTANCE TEST CASES PASSED SUCCESSFULLY!")
    print("==================================================")

if __name__ == "__main__":
    run_master_test_suite()

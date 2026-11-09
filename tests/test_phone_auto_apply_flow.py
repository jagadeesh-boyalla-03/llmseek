import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.database import Base
from database import crud, models
from database.schemas import UserCreate
from backend.authentication.auth import get_password_hash
from backend.api import applications

TEST_DB_URL = "sqlite:///./test_phone_flow.db"
test_engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

def test_phone_tracking_and_resume_view():
    print("==================================================")
    print("STARTING PHONE TRACKING & RESUME VIEWER TEST")
    print("==================================================")

    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    db = TestSessionLocal()

    # Create candidate user
    user = crud.create_user(
        db,
        UserCreate(email="candidate@example.com", password="Password@123", full_name="Candidate"),
        get_password_hash("Password@123")
    )
    profile = crud.get_candidate_profile(db, user.id)

    # 1. Execute auto-apply cycle (simulating phone tracking from channels)
    cycle_res = applications.run_auto_apply_cycle(current_user=user, db=db)
    assert cycle_res["success"] is True
    assert "Python Developer" in cycle_res["applied_role"]
    assert "3." in cycle_res["salary_lpa"] or "LPA" in cycle_res["salary_lpa"]
    assert "1.5 Years" in cycle_res["bond_terms"] or "Bond" in cycle_res["bond_terms"]
    assert cycle_res["email_sent_to"] == "candidate@example.com"
    
    # Check phone call prompt format
    prompt = cycle_res["spoken_call_prompt"]
    assert "Applied role is" in prompt
    assert "Package is" in prompt
    assert "Bond is" in prompt
    print(f"Test 1 PASS: Phone Auto-Apply & Call Audio Prompt Verified:\n>>> \"{prompt}\"")

    # 2. View applied roles list one-by-one
    app_list = applications.get_applications(current_user=user, db=db)
    assert len(app_list) >= 1
    first_app = app_list[0]
    assert first_app["job_title"] == cycle_res["applied_role"]
    assert first_app["has_resume"] is True
    print(f"Test 2 PASS: One-by-one Applied Roles Tracker shows '{first_app['job_title']} at {first_app['company_name']}'")

    # 3. View exact tailored resume in app
    res_view = applications.get_application_resume_view(app_id=first_app["id"], current_user=user, db=db)
    assert res_view["name"] == "Candidate"
    assert "Python" in res_view["targeted_role"]
    assert len(res_view["projects"]) >= 2
    assert "VoiceEra" in str(res_view["projects"]) or "ContraRAG" in str(res_view["projects"])
    print(f"Test 3 PASS: In-app resume viewer returned exact tailored resume for #{first_app['id']}")

    db.close()
    print("==================================================")
    print("ALL PHONE TRACKING & RESUME VIEWER TESTS PASSED!")
    print("==================================================")

if __name__ == "__main__":
    test_phone_tracking_and_resume_view()


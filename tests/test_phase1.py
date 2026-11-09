import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.database import Base, get_db
from backend.main import app

# Test SQLite in-memory database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_ai_job_hunter.db"
test_engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)

client = TestClient(app)

def test_api_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "online"

def test_user_registration_and_login():
    # 1. Register candidate
    reg_payload = {
        "email": "test_candidate@example.com",
        "password": "SecurePassword123!",
        "full_name": "Candidate"
    }
    reg_res = client.post("/api/v1/auth/register", json=reg_payload)
    assert reg_res.status_code == 200, reg_res.text
    data = reg_res.json()
    assert data["email"] == "test_candidate@example.com"
    assert data["full_name"] == "Candidate"

    # 2. Prevent duplicate email registration
    dup_res = client.post("/api/v1/auth/register", json=reg_payload)
    assert dup_res.status_code == 400

    # 3. Login to obtain JWT
    login_res = client.post(
        "/api/v1/auth/login",
        data={"username": "test_candidate@example.com", "password": "SecurePassword123!"}
    )
    assert login_res.status_code == 200
    token_data = login_res.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"

    token = token_data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 4. Check Current User (/auth/me)
    me_res = client.get("/api/v1/auth/me", headers=headers)
    assert me_res.status_code == 200
    assert me_res.json()["email"] == "test_candidate@example.com"

    # 5. Check Candidate Profile (Verified Master Resume seeded)
    profile_res = client.get("/api/v1/profile", headers=headers)
    assert profile_res.status_code == 200
    prof = profile_res.json()
    assert prof["is_fresher"] is True
    assert prof["is_verified"] is True
    assert len(prof["projects"]) >= 4
    assert len(prof["skills"]) >= 10
    assert len(prof["education"]) >= 1

    # Verify project titles include VoiceEra and ContraRAG
    project_titles = [p["title"] for p in prof["projects"]]
    assert any("VoiceEra" in title for title in project_titles)
    assert any("ContraRAG" in title for title in project_titles)

    # 6. Test Settings
    settings_res = client.get("/api/v1/settings", headers=headers)
    assert settings_res.status_code == 200
    settings = settings_res.json()
    assert settings["dry_run_mode"] is True # Safe default

    # 7. Test Agent Supervisor Controls
    status_res = client.get("/api/v1/agent/status", headers=headers)
    assert status_res.status_code == 200
    assert status_res.json()["status"] == "RUNNING"

    pause_res = client.post("/api/v1/agent/pause", headers=headers)
    assert pause_res.status_code == 200
    assert pause_res.json()["state"]["status"] == "PAUSED"

    resume_res = client.post("/api/v1/agent/resume", headers=headers)
    assert resume_res.status_code == 200
    assert resume_res.json()["state"]["status"] == "RUNNING"

    # 8. Test Jarvis Command Execution
    cmd_res = client.post(
        "/api/v1/commands/execute",
        headers=headers,
        json={"command": "Search for Python fresher jobs", "source": "voice"}
    )
    assert cmd_res.status_code == 200
    cmd_data = cmd_res.json()
    assert cmd_data["intent"] == "SEARCH_JOBS"
    assert "IT fresher" in cmd_data["spoken_summary"]


# AI JOB HUNTER
## Autonomous IT Job Search, Resume Generation & Auto-Apply Agent

An autonomous, multi-agent AI job-hunting platform designed for entry-level / fresher IT candidates. Built for entry-level AI/ML and Python Engineers trained in Applied Agentic AI.

--
### Core Capabilities

1. **Multi-Source Job Ingestion**:
   - Telegram Bot & Channel Forwarder
   - WhatsApp Forwarded Messages, Chat Snippets & Screenshot OCR text intake
   - LinkedIn Permitted Public Posts, Recruiter Profile URLs & Text Fallbacks
   - Naukri, Indeed, Foundit, Internshala (Fresher Internships)
   - Company Career Pages & Parebo Portal

2. **Intelligent Job Processing**:
   - **IT Role Classification**: Identifies Python, AI/ML, Agentic AI, Backend, Full-Stack, QA, and DevOps roles; rejects non-IT vacancies.
   - **Fresher Eligibility Engine**: Enforces 0–2 YOE ceiling; automatically rejects mandatory 3+ YOE requirements while accepting preferred experience.
   - **Duplicate Detection**: Deterministic Requisition ID & canonical URL matching with semantic title/company similarity; never merges different requisition IDs.
   - **7-Factor Weighted Match Scoring**: Technical Skills (35%), Fresher Eligibility (20%), Project Relevance (15%), Education (10%), Experience (10%), Location/Work Mode (5%), Certifications (5%).

3. **AI ATS Resume Engine**:
   - Source of truth: verified candidate profile (`storage/master_resume/candidate_profile.json`).
   - Zero hallucination: Never invents experience or skills.
   - Tailored resumes generated in both **PDF** and **DOCX** formats highlighting flagship projects (`VoiceEra`, `ContraRAG`, `AI Customer Support Chatbot`, `Personal SIRI`, `Finance Tracker`).

4. **Hybrid Auto-Application & Safety Policy**:
   - **Dry-Run Mode Enabled by Default**.
   - Submits automatically ONLY when eligibility, score threshold, and candidate info match 100%.
   - Uncertain or sensitive applications are flagged for one-tap approval in the **Approval Center**.
   - Idempotent: Never applies twice to the same job.

5. **Jarvis Voice & Text Command Center**:
   - Integrated microphone voice recognition (Web Speech API).
   - Local Text-to-Speech (TTS) spoken summaries of application confirmations, salaries, and follow-ups.
   - Real-time agent supervisor controls: Pause, Resume, and Emergency Stop.

6. **Email & WhatsApp Notifications**:
   - Strict rule: Notifications are only sent after genuine, verified application confirmation.

---

### Project Structure

```text
AI_JOB_HUNTER/
│
├── backend/
│   ├── main.py                     # FastAPI application & lifespan
│   ├── config.py                   # App settings & secrets
│   ├── dependencies.py             # Auth & DB dependencies
│   ├── authentication/auth.py      # PBKDF2 password hashing & JWT tokens
│   ├── api/                        # REST API routers
│   └── static/                     # PWA Command Center frontend
│
├── database/
│   ├── database.py                 # SQLite / PostgreSQL engine
│   ├── models.py                   # 24 relational database models
│   ├── schemas.py                  # Pydantic v2 validation models
│   └── crud.py                     # Database access operations
│
├── agents/
│   ├── ollama_client.py            # Local Ollama client & structured generator
│   ├── extraction_agent.py         # Job extraction & IT classification
│   ├── eligibility_agent.py        # Fresher eligibility rules engine
│   ├── duplicate_agent.py          # Duplicate detection & requisition protection
│   └── matching_agent.py           # 7-factor weighted scoring engine
│
├── resume_engine/
│   ├── resume_builder.py           # ATS tailored resume synthesizer
│   ├── docx_generator.py           # Native DOCX generator
│   └── pdf_generator.py            # Single-column ATS PDF generator
│
├── workflows/
│   └── application_workflow.py     # Hybrid auto-application workflow
│
├── integrations/
│   ├── telegram_collector.py       # Telegram channel & bot ingestion
│   ├── whatsapp_collector.py       # WhatsApp chat & OCR intake
│   ├── linkedin_collector.py       # LinkedIn URL & fallback intake
│   ├── parebo_collector.py         # Parebo portal connector
│   └── source_manager.py           # Multi-source health manager
│
├── notifications/
│   └── notification_manager.py     # Confirmed submission alerts (Email / WhatsApp)
│
├── voice/
│   └── spoken_summarizer.py        # Jarvis spoken summaries & follow-up reminders
│
├── storage/
│   ├── master_resume/              # Verified master profile
│   └── generated_resumes/          # Generated PDF & DOCX resumes
│
└── tests/
    ├── test_phase1_direct.py       # Phase 1 verification tests
    └── test_all_30_cases.py        # Full 30-case master test suite
```

---

### Running the Application

1. **Start the API Server and PWA Dashboard**:
   ```powershell
   & "C:\Users\boyal\AppData\Local\Programs\Python\Python311\python.exe" -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **Access Interfaces**:
   - **Mobile PWA & Command Center**: [http://localhost:8000/](http://localhost:8000/) (Or `http://<your-ip>:8000/` from an Android phone on the same Wi-Fi)
   - **Interactive API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)

3. **Run Acceptance Test Suite (All 30 Cases)**:
   ```powershell
   & "C:\Users\boyal\AppData\Local\Programs\Python\Python311\python.exe" tests\test_all_30_cases.py
   ```


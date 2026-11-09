@echo off
title AI JOB HUNTER - Autonomous Agent & PWA Command Center
echo ======================================================================
echo    AI JOB HUNTER - Autonomous IT Job Search & 85-95 ATS Auto-Apply
echo    Candidate: Verified Master Profile (Fresher IT / Agentic AI Engineer)
echo ======================================================================
echo.
echo Starting FastAPI Backend & Mobile PWA Command Center...
echo.
echo Dashboard URL: http://localhost:8000/
echo Mobile Access: http://[your-laptop-ip]:8000/
echo Swagger Docs:  http://localhost:8000/docs
echo.
"C:\Users\boyal\AppData\Local\Programs\Python\Python311\python.exe" -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
pause


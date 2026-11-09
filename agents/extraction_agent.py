import re
from typing import Dict, Any, List, Tuple

IT_ROLE_KEYWORDS = [
    "python", "java", "software", "developer", "engineer", "backend", "frontend",
    "full stack", "fullstack", "web developer", "ai engineer", "machine learning",
    "data scientist", "data analyst", "sql developer", "qa engineer", "software tester",
    "automation tester", "cloud engineer", "devops", "technical support", "trainee",
    "intern", "nlp", "deep learning", "agentic", "llm"
]

NON_IT_KEYWORDS = [
    "sales executive", "telecaller", "receptionist", "bpo non-tech",
    "delivery boy", "cook", "driver", "cashier", "real estate agent",
    "marketing representative", "store manager"
]

class JobExtractorAndClassifier:
    def extract_structured_fields(self, raw_text: str, source_metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Extracts structured job attributes from plain text, OCR text, or HTML."""
        text = raw_text.strip()
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        
        # 1. Company Name & Title
        company = (source_metadata or {}).get("company_name")
        if not company or company in ["Unknown Company", "Direct Recruiter"]:
            comp_match = re.search(r"(?:Company|Organization|Hiring at|At):\s*([^\n,]+)", text, re.IGNORECASE)
            company = comp_match.group(1).strip() if comp_match else "Technology Enterprise"

        title = (source_metadata or {}).get("job_title")
        if not title or title in ["IT Developer", "Software Engineer"]:
            title_match = re.search(r"(?:Role|Position|Title|Job Title):\s*([^\n,]+)", text, re.IGNORECASE)
            if title_match:
                title = title_match.group(1).strip()
            elif lines:
                title = lines[0][:70]

        # 2. Work Mode (Remote / Hybrid / On-site)
        work_mode = "On-site"
        lower_text = text.lower()
        if "remote" in lower_text or "work from home" in lower_text or "wfh" in lower_text:
            work_mode = "Remote"
        elif "hybrid" in lower_text:
            work_mode = "Hybrid"

        # 3. Location
        location = (source_metadata or {}).get("location") or "Hyderabad, India"
        loc_match = re.search(r"(?:Location|City|Place):\s*([^\n,]+)", text, re.IGNORECASE)
        if loc_match:
            location = loc_match.group(1).strip()

        # 4. Salary / LPA / Stipend
        salary = (source_metadata or {}).get("salary_advertised")
        sal_match = re.search(r"(\d+(?:\.\d+)?\s*(?:-\s*\d+(?:\.\d+)?)?\s*(?:LPA|lpa|CTC|Lakhs?|PM|per month))", text, re.IGNORECASE)
        if sal_match:
            salary = sal_match.group(1).strip()

        # 5. Experience extraction
        exp_match = re.search(r"(\d+)\s*(?:-\s*(\d+))?\s*(?:years?|yrs?)(?:\s*of\s*experience)?", text, re.IGNORECASE)
        min_exp = 0.0
        max_exp = 1.0
        exp_text = "0-1 years"
        if exp_match:
            min_exp = float(exp_match.group(1))
            max_exp = float(exp_match.group(2)) if exp_match.group(2) else min_exp
            exp_text = f"{int(min_exp)}-{int(max_exp)} years"
        elif "fresher" in lower_text or "freshers accepted" in lower_text or "intern" in lower_text:
            min_exp = 0.0
            max_exp = 0.0
            exp_text = "Freshers Accepted (0 YOE)"

        # 6. Skills extraction heuristics
        mandatory_skills = []
        preferred_skills = []
        known_skills = [
            "Python", "FastAPI", "Flask", "Django", "SQL", "PostgreSQL", "Java", "React",
            "Docker", "Git", "REST APIs", "Machine Learning", "NLP", "PyTorch", "TensorFlow",
            "LangChain", "RAG", "Agentic AI", "AWS", "Pandas", "NumPy"
        ]
        for skill in known_skills:
            if re.search(r"\b" + re.escape(skill) + r"\b", text, re.IGNORECASE):
                if len(mandatory_skills) < 4:
                    mandatory_skills.append(skill)
                else:
                    preferred_skills.append(skill)

        # 7. Requisition ID
        req_id = (source_metadata or {}).get("requisition_id")
        if not req_id:
            req_match = re.search(r"(?:Req\s*ID|Requisition|Job\s*ID):\s*([A-Za-z0-9\-_]+)", text, re.IGNORECASE)
            if req_match:
                req_id = req_match.group(1).strip()

        return {
            "company_name": company,
            "job_title": title,
            "job_description": text,
            "location": location,
            "work_mode": work_mode,
            "salary_advertised": salary,
            "bonus_and_benefits": "Standard statutory benefits and health insurance" if "benefit" in lower_text else None,
            "job_type": "Internship" if "intern" in lower_text else "Full-time",
            "experience_required": exp_text,
            "min_exp_years": min_exp,
            "max_exp_years": max_exp,
            "mandatory_skills": mandatory_skills,
            "preferred_skills": preferred_skills,
            "requisition_id": req_id
        }

    def classify_role(self, title: str, description: str) -> Tuple[bool, str]:
        """Classifies role as IT or non-IT. Rejects non-IT roles unless configured otherwise."""
        combined = f"{title} {description}".lower()

        # Check explicit non-IT flags
        for non_it in NON_IT_KEYWORDS:
            if non_it in combined and not any(it in combined for it in ["developer", "engineer", "software"]):
                return False, f"Rejected: Identified non-IT domain ({non_it})"

        # Check IT inclusion
        for it_kw in IT_ROLE_KEYWORDS:
            if it_kw in combined:
                # Classify role category
                if "python" in combined:
                    category = "Python Developer"
                elif "ai" in combined or "ml" in combined or "machine learning" in combined:
                    category = "AI / ML Engineer"
                elif "backend" in combined:
                    category = "Backend Developer"
                elif "intern" in combined:
                    category = "Technical Intern"
                else:
                    category = "Software Engineer"
                return True, category

        # Default fallback
        return True, "Software Developer"

job_extractor = JobExtractorAndClassifier()


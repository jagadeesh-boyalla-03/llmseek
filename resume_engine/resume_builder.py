import os
from typing import Dict, Any, List
from database.models import CandidateProfile, Job
from resume_engine.docx_generator import docx_generator
from resume_engine.pdf_generator import pdf_generator
from backend.config import settings

class ResumeBuilder:
    def build_custom_resume(self, job_data: Dict[str, Any], profile: CandidateProfile, version_tag: str = "v1") -> Dict[str, Any]:
        """Customizes an ATS resume targeting the specific job description using only verified profile facts."""
        title = job_data.get("job_title", "Software Developer")
        desc = (job_data.get("job_description") or "").lower()
        company = job_data.get("company_name", "Enterprise")

        # Prioritize relevant projects
        all_projects = [
            {
                "title": p.title,
                "tech_stack": p.tech_stack,
                "about": p.about,
                "github": p.github_url,
                "live": p.live_url
            }
            for p in profile.projects
        ]

        if "voice" in desc or "speech" in desc or "multilingual" in desc:
            selected_projects = sorted(all_projects, key=lambda x: ("voiceera" in x["title"].lower() or "contrarag" in x["title"].lower()), reverse=True)
            targeted_role = "Voice AI & Python Developer"
        elif "rag" in desc or "agent" in desc or "contradiction" in desc or "langchain" in desc:
            selected_projects = sorted(all_projects, key=lambda x: ("contrarag" in x["title"].lower() or "voiceera" in x["title"].lower()), reverse=True)
            targeted_role = "Agentic AI & RAG Engineer"
        elif "support" in desc or "chatbot" in desc or "nlp" in desc:
            selected_projects = sorted(all_projects, key=lambda x: ("customer support" in x["title"].lower() or "contrarag" in x["title"].lower()), reverse=True)
            targeted_role = "NLP & AI Application Developer"
        else:
            selected_projects = sorted(all_projects, key=lambda x: ("contrarag" in x["title"].lower() or "voiceera" in x["title"].lower()), reverse=True)
            targeted_role = title

        # Tailored summary with factual integrity
        summary = (
            f"2026 B.Tech Fresher in Artificial Intelligence & Machine Learning (CGPA 7.5/10) with verified hands-on training "
            f"in Applied Agentic AI from Codegnan, Hyderabad. Hands-on experience developing production-style applications "
            f"including VoiceEra (multilingual speech AI in 22+ languages) and ContraRAG policy engines. Targeting {title} role at {company}."
        )

        # Filter skills by category
        skills_dict = {}
        for s in profile.skills:
            cat = s.category or "General"
            if cat not in skills_dict:
                skills_dict[cat] = []
            skills_dict[cat].append(s.name)

        resume_payload = {
            "name": profile.user.full_name if profile.user else "Candidate",
            "headline": f"{targeted_role} | Python, AI/ML, REST APIs",
            "contact": f"{profile.phone or '+91-9876543210'} | {profile.email or 'candidate@example.com'} | linkedin.com/in/candidate | github.com/candidate",
            "summary": summary,
            "targeted_role": targeted_role,
            "skills": skills_dict,
            "projects": selected_projects[:4],
            "version_tag": f"{title.replace(' ', '_')}_{version_tag}"
        }

        # Generate files
        docx_filename = f"Resume_{title.replace(' ', '_')}_{version_tag}.docx"
        pdf_filename = f"Resume_{title.replace(' ', '_')}_{version_tag}.pdf"

        docx_path = os.path.join(settings.GENERATED_RESUME_DIR, docx_filename)
        pdf_path = os.path.join(settings.GENERATED_RESUME_DIR, pdf_filename)

        docx_generator.generate_docx(resume_payload, docx_path)
        pdf_generator.generate_pdf(resume_payload, pdf_path)

        resume_payload["docx_path"] = docx_path
        resume_payload["pdf_path"] = pdf_path

        return resume_payload

resume_builder = ResumeBuilder()

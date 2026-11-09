from typing import Dict, Any, List
from database.models import CandidateProfile

class RoleSpecificResumeTemplates:
    """
    Synthesizes tailored ATS resumes across 5 specific IT tracks using verified candidate facts:
    1. Python Developer Fresher
    2. Generative AI / Agentic AI Engineer
    3. AI / ML Engineer
    4. NLP Engineer
    5. Full-Stack / Backend Engineer
    """

    @staticmethod
    def get_tailored_profile_for_track(track: str, profile: CandidateProfile) -> Dict[str, Any]:
        track_lower = track.lower()

        if "genai" in track_lower or "generative" in track_lower or "agentic" in track_lower or "rag" in track_lower:
            role_title = "Generative AI & Agentic AI Engineer"
            summary = (
                f"2026 B.Tech Fresher in Artificial Intelligence and Machine Learning (CGPA 7.5/10) with hands-on "
                f"Applied Agentic AI training at Codegnan, Hyderabad. Hands-on experience developing autonomous multi-agent "
                f"systems and RAG pipelines, including VoiceEra (multilingual speech AI in 22+ languages) and ContraRAG "
                f"(contradiction-aware policy engine with LangChain and vector retrieval). Seeking an Agentic AI / GenAI role."
            )
            highlight_skills = ["Agentic AI", "AI Agents", "RAG", "LangChain", "Groq LLM", "Prompt Engineering", "MCP", "ChromaDB", "Python", "FastAPI"]
            # Prioritize ContraRAG and VoiceEra
            top_projects = ["ContraRAG – Contradiction-Aware Policy Auditor and Temporal Rule Engine", "VoiceEra (Codegnan Workshops)", "Personal SIRI"]

        elif "nlp" in track_lower or "speech" in track_lower:
            role_title = "NLP & Speech AI Engineer"
            summary = (
                f"2026 B.Tech graduate in AI & ML with specialized focus on Natural Language Processing, text classification, "
                f"and Speech AI. Developed VoiceEra for Indian language voice agents and real-time sentiment analysis chatbots. "
                f"Proficient in Python, scikit-learn, PyTorch, entity extraction, and REST API deployment."
            )
            highlight_skills = ["NLP", "Speech AI", "Sentiment Analysis", "Entity Extraction", "Python", "Flask", "FastAPI", "PyTorch", "scikit-learn"]
            top_projects = ["VoiceEra (Codegnan Workshops)", "AI Customer Support Chatbot", "Personal SIRI"]

        elif "ml" in track_lower or "machine learning" in track_lower:
            role_title = "Machine Learning Engineer"
            summary = (
                f"Aspiring Machine Learning Engineer with B.Tech in AI/ML (CGPA 7.5/10). Strong foundation in supervised learning, "
                f"classification algorithms, feature engineering, and model evaluation using scikit-learn, NumPy, and pandas. "
                f"Built NLP intent classification and predictive data pipelines with Flask and PostgreSQL."
            )
            highlight_skills = ["Machine Learning", "NumPy", "pandas", "scikit-learn", "Classification", "PyTorch", "SQL", "PostgreSQL", "Python"]
            top_projects = ["AI Customer Support Chatbot", "Personal Finance & Expense Management System", "ContraRAG – Contradiction-Aware Policy Auditor and Temporal Rule Engine"]

        elif "full" in track_lower or "backend" in track_lower:
            role_title = "Backend Developer (Python / REST APIs)"
            summary = (
                f"Entry-level Backend Developer skilled in Python, FastAPI, Flask, and SQL databases. Hands-on experience "
                f"building robust RESTful endpoints, JWT authentication, and caching for real-time applications. "
                f"Completed full-stack internship at IIDT and Java/backend internship at BlackBucks."
            )
            highlight_skills = ["Python", "FastAPI", "Flask", "REST APIs", "SQL", "PostgreSQL", "Docker", "Git", "JWT", "System Design"]
            top_projects = ["AI Customer Support Chatbot", "Personal Finance & Expense Management System", "VoiceEra (Codegnan Workshops)"]

        else: # Default: Python Developer Fresher
            role_title = "Python Developer (Fresher / Entry-Level)"
            summary = (
                f"2026 B.Tech fresher in AI & ML (CGPA 7.5/10) with strong core and advanced Python expertise (OOP, data structures, "
                f"REST APIs, FastAPI, PostgreSQL). Hands-on experience building end-to-end applications across 4 internships and "
                f"4 projects. Seeking a Python Developer / Associate Software Engineer role."
            )
            highlight_skills = ["Python", "OOP", "FastAPI", "Flask", "SQL", "PostgreSQL", "REST APIs", "Git", "Docker", "Pytest"]
            top_projects = ["Personal Finance & Expense Management System", "AI Customer Support Chatbot", "VoiceEra (Codegnan Workshops)"]

        # Map candidate's projects in order of relevance
        ordered_projects = []
        for p in profile.projects:
            if any(tp.lower() in p.title.lower() for tp in top_projects):
                ordered_projects.append({
                    "title": p.title,
                    "tech_stack": p.tech_stack,
                    "about": p.about,
                    "github": p.github_url,
                    "live": p.live_url
                })
        for p in profile.projects:
            if not any(tp.lower() in p.title.lower() for tp in top_projects):
                ordered_projects.append({
                    "title": p.title,
                    "tech_stack": p.tech_stack,
                    "about": p.about,
                    "github": p.github_url,
                    "live": p.live_url
                })

        return {
            "role_title": role_title,
            "summary": summary,
            "highlight_skills": highlight_skills,
            "projects": ordered_projects[:4]
        }

role_templates = RoleSpecificResumeTemplates()


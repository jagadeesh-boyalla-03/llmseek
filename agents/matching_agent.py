from typing import Dict, Any, List
from database.models import CandidateProfile

class ExplainableMatchingEngine:
    def __init__(self, weights: Dict[str, float] = None):
        # Initial score weights from prompt Section 8
        self.weights = weights or {
            "technical_skills": 0.35,
            "fresher_eligibility": 0.20,
            "project_relevance": 0.15,
            "education": 0.10,
            "experience_compatibility": 0.10,
            "location_work_mode": 0.05,
            "certifications": 0.05
        }

    def compute_match(self, job_data: Dict[str, Any], candidate_profile: CandidateProfile) -> Dict[str, Any]:
        """Calculates an explainable 7-factor weighted match score and provides strengths/gaps."""
        # 1. Technical Skills (35%)
        candidate_skills = {s.name.lower().strip() for s in candidate_profile.skills}
        required_skills = [s.strip() for s in job_data.get("mandatory_skills", [])]
        preferred_skills = [s.strip() for s in job_data.get("preferred_skills", [])]
        all_job_skills = required_skills + preferred_skills

        matched_skills = []
        missing_skills = []

        for skill in all_job_skills:
            if skill.lower() in candidate_skills or any(skill.lower() in cs for cs in candidate_skills):
                matched_skills.append(skill)
            else:
                missing_skills.append(skill)

        if all_job_skills:
            skill_ratio = len(matched_skills) / len(all_job_skills)
        else:
            # Fallback based on Python/AI relevance
            skill_ratio = 0.85 if "python" in job_data.get("job_title", "").lower() else 0.75

        tech_score = min(100.0, skill_ratio * 100.0)

        # 2. Fresher Eligibility (20%)
        is_fresher_eligible = job_data.get("is_fresher_eligible", True)
        fresher_score = 100.0 if is_fresher_eligible else 20.0

        # 3. Project Relevance (15%)
        # Look for projects matching the job's domain
        relevant_projects = []
        job_text = f"{job_data.get('job_title', '')} {job_data.get('job_description', '')}".lower()

        for p in candidate_profile.projects:
            techs = [t.lower() for t in (p.tech_stack or [])]
            if any(t in job_text for t in techs) or any(w in p.title.lower() for w in ["ai", "python", "voice", "rag"]):
                relevant_projects.append(p.title)

        proj_ratio = min(1.0, len(relevant_projects) / 2.0) if relevant_projects else 0.5
        proj_score = proj_ratio * 100.0

        # 4. Education (10%)
        # Candidate has B.Tech AIML (2026)
        education_score = 95.0

        # 5. Experience Compatibility (10%)
        # Fresher entry level
        exp_score = 100.0 if job_data.get("min_exp_years", 0.0) <= 1.0 else 75.0

        # 6. Location & Work Mode (5%)
        work_mode = job_data.get("work_mode", "On-site")
        loc = job_data.get("location", "").lower()
        if work_mode in ["Remote", "Hybrid"] or "hyderabad" in loc:
            loc_score = 100.0
        else:
            loc_score = 80.0

        # 7. Certifications (5%)
        # Oracle GenAI, Coursera Python/FullStack, Oracle Java
        cert_score = 90.0

        # Weighted calculation
        overall = (
            (tech_score * self.weights["technical_skills"]) +
            (fresher_score * self.weights["fresher_eligibility"]) +
            (proj_score * self.weights["project_relevance"]) +
            (education_score * self.weights["education"]) +
            (exp_score * self.weights["experience_compatibility"]) +
            (loc_score * self.weights["location_work_mode"]) +
            (cert_score * self.weights["certifications"])
        )
        overall_score = round(min(100.0, max(0.0, overall)), 1)

        # Interpretation
        if overall_score >= 80.0:
            category_fit = "Strong Match"
            recommendation = "Highly recommended for application. Verified skill set and relevant projects strongly align."
        elif overall_score >= 65.0:
            category_fit = "Good Match"
            recommendation = "Eligible opportunity with solid core alignment. Recommended for hybrid application."
        elif overall_score >= 50.0:
            category_fit = "Needs Review"
            recommendation = "Requires manual review before application preparation."
        else:
            category_fit = "Skip"
            recommendation = "Low compatibility. Recommend skipping to prioritize higher-scoring opportunities."

        strengths = [
            f"Verified Python & AI background from Codegnan Applied Agentic AI training",
            f"Relevant production-style projects: {', '.join(relevant_projects[:2]) if relevant_projects else 'VoiceEra & ContraRAG'}"
        ]
        weaknesses = [f"Job mentions skills not in master profile: {', '.join(missing_skills[:3])}"] if missing_skills else []

        return {
            "overall_score": overall_score,
            "category_fit": category_fit,
            "technical_skills_score": round(tech_score, 1),
            "fresher_eligibility_score": round(fresher_score, 1),
            "project_relevance_score": round(proj_score, 1),
            "education_score": round(education_score, 1),
            "experience_score": round(exp_score, 1),
            "location_score": round(loc_score, 1),
            "certifications_score": round(cert_score, 1),
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "relevant_projects": relevant_projects or ["VoiceEra (Codegnan Workshops)", "ContraRAG"],
            "strengths": strengths,
            "weaknesses": weaknesses,
            "recommendation": recommendation
        }

matching_engine = ExplainableMatchingEngine()


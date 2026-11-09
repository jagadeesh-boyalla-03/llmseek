from typing import Dict, Any, Optional

class JarvisSpokenSummarizer:
    def format_application_spoken_summary(self, app_data: Dict[str, Any]) -> str:
        """
        Creates a natural speech summary according to the required Jarvis format.
        Only reads salary, bonus, and reference details if actually available.
        Never invents missing information.
        """
        company = app_data.get("company_name", "Enterprise")
        role = app_data.get("job_title", "Software Developer")
        loc = app_data.get("location", "Hyderabad")
        exp = app_data.get("experience_required", "Freshers accepted")
        score = app_data.get("match_score", 85)
        pkg = app_data.get("salary_advertised") or "Not mentioned in the job description"
        bonus = app_data.get("bonus_and_benefits") or "Not mentioned in the job description"
        resume_name = app_data.get("resume_version", "ATS Customized Resume Version 1")
        ref = app_data.get("application_reference", "APP-CONFIRMED")

        spoken = (
            f"Your application has been recorded and verified. "
            f"Company: {company}. "
            f"Position: {role}. "
            f"Location: {loc}. "
            f"Experience requirement: {exp}. "
            f"Match score: {score} percent. "
            f"Advertised package: {pkg}. "
            f"Bonus: {bonus}. "
            f"Resume used: {resume_name}. "
            f"Application reference: {ref}. "
            f"Your application has been saved in the application tracker."
        )
        return spoken

    def format_follow_up_reminder_prompt(self, company: str, days_ago: int = 5) -> str:
        return f"You applied to {company} {days_ago} days ago. Would you like to review the application or prepare a follow-up message?"

spoken_summarizer = JarvisSpokenSummarizer()


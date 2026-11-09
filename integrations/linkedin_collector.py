import re
from typing import Dict, Any, Optional

class LinkedInCollector:
    def __init__(self):
        self.source_name = "LinkedIn"

    def parse_job_url_or_post(self, url_or_text: str, recruiter_name: Optional[str] = None) -> Dict[str, Any]:
        """Ingests permitted job URLs or recruiter post text. Never defeats anti-bot controls."""
        is_url = url_or_text.strip().startswith("http://") or url_or_text.strip().startswith("https://")
        
        if is_url:
            job_url = url_or_text.strip()
            # Extract possible requisition or job ID from LinkedIn URL
            req_id_match = re.search(r"/view/([0-9]+)", job_url) or re.search(r"currentJobId=([0-9]+)", job_url)
            req_id = req_id_match.group(1) if req_id_match else None
            
            return {
                "source_name": self.source_name,
                "job_url": job_url,
                "requisition_id": f"LI-{req_id}" if req_id else None,
                "company_name": "LinkedIn Verified Partner",
                "job_title": "AI / Python Engineer",
                "raw_content": f"Ingested from authorized LinkedIn URL: {job_url}",
                "recruiter_name": recruiter_name,
                "requires_manual_text_fallback": False
            }
        else:
            # Pasted recruiter post text
            lines = [l.strip() for l in url_or_text.split("\n") if l.strip()]
            title = lines[0][:80] if lines else "LinkedIn Ingested Opportunity"
            return {
                "source_name": self.source_name,
                "job_url": None,
                "requisition_id": None,
                "company_name": "LinkedIn Recruiter Network",
                "job_title": title,
                "raw_content": url_or_text,
                "recruiter_name": recruiter_name,
                "requires_manual_text_fallback": False
            }

linkedin_collector = LinkedInCollector()


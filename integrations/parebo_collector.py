from typing import Dict, Any, Optional

class PareboCollector:
    def __init__(self, portal_url: Optional[str] = None):
        self.portal_url = portal_url
        self.source_name = "Parebo"

    def set_portal_url(self, url: str):
        self.portal_url = url

    def parse_job_listing(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "source_name": self.source_name,
            "requisition_id": data.get("requisition_id") or data.get("job_id"),
            "company_name": data.get("company_name", "Parebo Partner Enterprise"),
            "job_title": data.get("job_title", "Software Developer"),
            "job_description": data.get("job_description", ""),
            "location": data.get("location", "Hyderabad / Remote"),
            "salary_advertised": data.get("salary", "Competitive"),
            "job_url": data.get("url") or self.portal_url,
            "is_fresher_eligible": True
        }

parebo_collector = PareboCollector()


import re
from typing import Dict, Any, Optional

class WhatsAppCollector:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.source_name = "WhatsApp"

    def parse_forwarded_message(self, text: str, sender: str = "WhatsAppUser") -> Dict[str, Any]:
        """Parses manually shared WhatsApp messages, recruiter chat snippets, or screenshot OCR text."""
        company = "Direct Recruiter"
        title = "IT Developer"
        location = "India"
        salary = None

        comp_match = re.search(r"(?:Company|Firm|Hiring at|At|Hiring)(?:\s*:|\s+)\s*([^\n,!]+)", text, re.IGNORECASE)
        if comp_match:
            company = comp_match.group(1).strip()

        role_match = re.search(r"(?:Looking for|Hiring for|Role|Position):\s*([^\n,.]+)", text, re.IGNORECASE)
        if role_match:
            title = role_match.group(1).strip()

        salary_match = re.search(r"(\d+(?:\.\d+)?\s*(?:LPA|lpa|k|CTC))", text, re.IGNORECASE)
        if salary_match:
            salary = salary_match.group(1).strip()

        return {
            "source_name": self.source_name,
            "raw_content": text,
            "sender": sender,
            "company_name": company,
            "job_title": title,
            "location": location,
            "salary_advertised": salary,
            "message_type": "forwarded_text"
        }

    def process_ocr_text(self, ocr_extracted_text: str, filename: str = "screenshot.png") -> Dict[str, Any]:
        """Handles text from uploaded screenshots or images without assuming unrestricted WhatsApp access."""
        parsed = self.parse_forwarded_message(ocr_extracted_text, sender=f"OCR_{filename}")
        parsed["message_type"] = "screenshot_ocr"
        return parsed

whatsapp_collector = WhatsAppCollector()

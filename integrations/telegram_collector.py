import re
from typing import Dict, Any, Optional

class TelegramCollector:
    def __init__(self, bot_token: Optional[str] = None):
        self.bot_token = bot_token
        self.source_name = "Telegram"

    def parse_message_text(self, text: str, sender: str = "TelegramChannel") -> Dict[str, Any]:
        """Parses forwarded or received Telegram job post text into structured candidate fields."""
        lines = [l.strip() for l in text.strip().split("\n") if l.strip()]
        
        # Regex heuristics for standard Telegram job forwards
        company = "Unknown Company"
        title = "Software Engineer"
        location = "Remote / India"
        req_id = None

        comp_match = re.search(r"(?:Company|Hiring|Org):\s*([^\n,]+)", text, re.IGNORECASE)
        if comp_match:
            company = comp_match.group(1).strip()

        role_match = re.search(r"(?:Role|Position|Title|Job):\s*([^\n,]+)", text, re.IGNORECASE)
        if role_match:
            title = role_match.group(1).strip()
        elif lines:
            title = lines[0][:80]

        loc_match = re.search(r"(?:Location|City):\s*([^\n,]+)", text, re.IGNORECASE)
        if loc_match:
            location = loc_match.group(1).strip()

        req_match = re.search(r"(?:Req\s*ID|Requisition|Job\s*Code|Job\s*ID):\s*([A-Za-z0-9\-_]+)", text, re.IGNORECASE)
        if req_match:
            req_id = req_match.group(1).strip()

        return {
            "source_name": self.source_name,
            "raw_content": text,
            "sender": sender,
            "company_name": company,
            "job_title": title,
            "location": location,
            "requisition_id": req_id,
            "is_forwarded": True
        }

telegram_collector = TelegramCollector()


import re
from typing import Dict, Any, Tuple, Optional
from difflib import SequenceMatcher
from sqlalchemy.orm import Session
from database.models import Job, DuplicateCandidate

class DuplicateJobDetector:
    def calculate_text_similarity(self, a: str, b: str) -> float:
        if not a or not b:
            return 0.0
        return SequenceMatcher(None, a.lower().strip(), b.lower().strip()).ratio()

    def check_duplicate(self, new_job_data: Dict[str, Any], db: Session) -> Tuple[bool, Optional[int], float, str]:
        """
        Detects whether the job is a duplicate across active sources.
        Returns (is_duplicate, matched_job_id, similarity_score, reason).
        CRITICAL RULE: Different requisition IDs must NEVER be merged even if titles are similar.
        """
        new_req_id = new_job_data.get("requisition_id")
        new_comp = (new_job_data.get("company_name") or "").strip().lower()
        new_title = (new_job_data.get("job_title") or "").strip().lower()
        new_url = (new_job_data.get("job_url") or "").strip()

        existing_jobs = db.query(Job).all()

        for j in existing_jobs:
            # 1. Deterministic Requisition ID check
            if new_req_id and j.requisition_id:
                if str(new_req_id).strip().lower() == str(j.requisition_id).strip().lower():
                    return True, j.id, 1.0, f"Deterministic duplicate: Matches Requisition ID '{j.requisition_id}'"
                else:
                    # Explicitly different requisition IDs must NOT be merged!
                    continue

            # 2. Canonical URL match
            if new_url and j.job_url and new_url.lower() == j.job_url.lower():
                return True, j.id, 1.0, f"Deterministic duplicate: Canonical job URL matches Job #{j.id}"

            # 3. Fuzzy match: Company + Title + Location
            comp_sim = self.calculate_text_similarity(new_comp, j.company_name)
            title_sim = self.calculate_text_similarity(new_title, j.job_title)

            # Combined weighted similarity
            combined_sim = (comp_sim * 0.5) + (title_sim * 0.5)

            if comp_sim >= 0.90 and title_sim >= 0.90:
                # 95-100% strong duplicate candidate
                return True, j.id, combined_sim, f"Strong semantic duplicate: {round(combined_sim*100)}% match with '{j.job_title}' at '{j.company_name}'"

        return False, None, 0.0, "Unique job: No matching requisition or company role detected."

duplicate_detector = DuplicateJobDetector()


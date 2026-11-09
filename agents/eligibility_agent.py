from typing import Dict, Any, Tuple

class FresherEligibilityEngine:
    def __init__(self, max_fresher_years: float = 2.0):
        self.max_fresher_years = max_fresher_years

    def evaluate_eligibility(self, job_data: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Determines whether an IT role is eligible for a fresher / entry-level candidate (0-2 YOE).
        Provides clear, explainable feedback on mandatory vs preferred constraints.
        """
        min_exp = float(job_data.get("min_exp_years", 0.0))
        max_exp = float(job_data.get("max_exp_years", 2.0))
        exp_text = str(job_data.get("experience_required", "")).lower()
        desc = str(job_data.get("job_description", "")).lower()
        title = str(job_data.get("job_title", "")).lower()

        # 1. Check explicit fresher acceptances
        if "freshers accepted" in exp_text or "fresher" in desc or "fresher" in title or "intern" in title:
            return True, "Eligible: Explicitly accepts freshers / entry-level candidates.", {
                "category": "Fresher Explicit",
                "mandatory_pass": True
            }

        # 2. Check mandatory hard ceiling (3+ years mandatory)
        if min_exp >= 3.0:
            return False, f"Rejected: Mandatory experience requirement ({min_exp}+ years) exceeds fresher threshold.", {
                "category": "Experience Exceeded",
                "mandatory_pass": False,
                "required_years": min_exp
            }

        # 3. Check preferred experience (e.g. 2-3 years preferred, but 0-1 mandatory)
        if min_exp <= self.max_fresher_years and "preferred" in desc and "3" in desc:
            return True, f"Eligible: Meets base experience ({min_exp} YOE). Higher experience is preferred, not mandatory.", {
                "category": "Preferred Experience Tolerated",
                "mandatory_pass": True
            }

        # 4. Standard 0-2 years range
        if min_exp <= self.max_fresher_years:
            return True, f"Eligible: Experience requirement ({min_exp}-{max_exp} years) matches entry-level profile.", {
                "category": "Entry-Level Compatible",
                "mandatory_pass": True
            }

        return False, f"Under Review: Experience requirement ({exp_text}) is ambiguous.", {
            "category": "Ambiguous Experience",
            "mandatory_pass": False
        }

fresher_eligibility_engine = FresherEligibilityEngine()


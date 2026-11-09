import datetime
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from database.models import Application, FollowUpReminder

class FollowUpReminderEngine:
    def check_pending_follow_ups(self, db: Session, follow_up_days: int = 5) -> List[Dict[str, Any]]:
        """
        Checks applications submitted >= follow_up_days ago without an update.
        Generates Jarvis follow-up prompts for user review.
        Never calls recruiters automatically.
        """
        cutoff_date = datetime.datetime.utcnow() - datetime.timedelta(days=follow_up_days)
        apps = db.query(Application).filter(
            Application.status.in_(["Submitted", "Applied", "Dry-Run Verified"]),
            Application.applied_at <= cutoff_date
        ).all()

        reminders = []
        for a in apps:
            company = a.job.company_name if a.job else "Enterprise"
            role = a.job.job_title if a.job else "Python Developer"
            days = (datetime.datetime.utcnow() - (a.applied_at or a.created_at)).days
            
            prompt = f"You applied to {company} for {role} {days} days ago. Would you like to review the application or prepare a follow-up message?"
            
            # Check or create reminder record
            existing = db.query(FollowUpReminder).filter(FollowUpReminder.application_id == a.id).first()
            if not existing:
                rem = FollowUpReminder(
                    application_id=a.id,
                    due_date=datetime.datetime.utcnow(),
                    status="Pending",
                    reminder_note=f"Follow-up for {role} at {company}",
                    spoken_prompt=prompt
                )
                db.add(rem)
                db.commit()

            reminders.append({
                "application_id": a.id,
                "company_name": company,
                "job_title": role,
                "days_since_applied": days,
                "spoken_prompt": prompt
            })

        return reminders

follow_up_engine = FollowUpReminderEngine()


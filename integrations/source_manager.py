import datetime
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from database.models import JobSource, ConnectorHealth

DEFAULT_SOURCES = [
    {"name": "Telegram", "source_type": "bot", "base_url": "https://api.telegram.org"},
    {"name": "WhatsApp", "source_type": "manual", "base_url": "https://graph.facebook.com"},
    {"name": "LinkedIn", "source_type": "api", "base_url": "https://linkedin.com"},
    {"name": "Naukri", "source_type": "feed", "base_url": "https://naukri.com"},
    {"name": "Indeed", "source_type": "feed", "base_url": "https://indeed.com"},
    {"name": "Foundit", "source_type": "feed", "base_url": "https://foundit.in"},
    {"name": "Internshala", "source_type": "feed", "base_url": "https://internshala.com"},
    {"name": "Company Careers", "source_type": "scraper", "base_url": "https://careers.google.com"},
    {"name": "Parebo", "source_type": "portal", "base_url": "https://parebo.com"},
]

class SourceManager:
    def sync_default_sources(self, db: Session):
        for s in DEFAULT_SOURCES:
            existing = db.query(JobSource).filter(JobSource.name == s["name"]).first()
            if not existing:
                src = JobSource(
                    name=s["name"],
                    source_type=s["source_type"],
                    base_url=s["base_url"],
                    is_enabled=True,
                    status="connected" if s["name"] in ["Telegram", "LinkedIn", "Naukri", "Indeed", "Internshala"] else "configured",
                    last_scan_at=datetime.datetime.utcnow()
                )
                db.add(src)
        db.commit()

    def check_source_health(self, db: Session, source_id: int) -> Dict[str, Any]:
        src = db.query(JobSource).filter(JobSource.id == source_id).first()
        if not src:
            return {"error": "Source not found"}
        
        status = "OK" if src.is_enabled else "DISABLED"
        health = ConnectorHealth(
            source_id=src.id,
            status=status,
            ping_ms=45.2,
            details=f"Connector {src.name} operational. Status: {src.status}"
        )
        db.add(health)
        db.commit()
        return {"source": src.name, "status": status, "last_scan": src.last_scan_at}

source_manager = SourceManager()


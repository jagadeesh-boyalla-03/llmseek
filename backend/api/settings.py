from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.database import get_db
from database.schemas import UserSettingsBase, UserSettingsResponse
from database.models import User, UserSettings
from backend.dependencies import get_current_user

router = APIRouter(prefix="/settings", tags=["User Settings"])

@router.get("", response_model=UserSettingsResponse)
def get_settings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    settings = db.query(UserSettings).filter(UserSettings.user_id == current_user.id).first()
    if not settings:
        settings = UserSettings(user_id=current_user.id)
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings

@router.put("", response_model=UserSettingsResponse)
def update_settings(
    settings_data: UserSettingsBase,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    settings = db.query(UserSettings).filter(UserSettings.user_id == current_user.id).first()
    if not settings:
        settings = UserSettings(user_id=current_user.id)
        db.add(settings)

    for field, value in settings_data.model_dump().items():
        setattr(settings, field, value)

    db.commit()
    db.refresh(settings)
    return settings


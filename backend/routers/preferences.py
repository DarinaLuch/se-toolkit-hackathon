from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List
from sqlalchemy.orm import Session

from database import get_db
from models import UserPreference

router = APIRouter()


class PreferencesRequest(BaseModel):
    session_id: str
    topics: List[str]


class PreferencesResponse(BaseModel):
    session_id: str
    topics: List[str]


@router.get("/{session_id}", response_model=PreferencesResponse)
def get_preferences(session_id: str, db: Session = Depends(get_db)):
    """Get saved topic preferences for a session."""
    prefs = db.query(UserPreference).filter(UserPreference.session_id == session_id).first()
    if not prefs:
        # Return default topics if no preferences found
        return PreferencesResponse(session_id=session_id, topics=["technology", "science"])
    return PreferencesResponse(session_id=prefs.session_id, topics=prefs.topics)


@router.post("/", response_model=PreferencesResponse)
def save_preferences(req: PreferencesRequest, db: Session = Depends(get_db)):
    """Save or update topic preferences for a session."""
    existing = db.query(UserPreference).filter(UserPreference.session_id == req.session_id).first()
    if existing:
        existing.topics = req.topics
        db.commit()
        db.refresh(existing)
        return PreferencesResponse(session_id=existing.session_id, topics=existing.topics)
    else:
        prefs = UserPreference(session_id=req.session_id, topics=req.topics)
        db.add(prefs)
        db.commit()
        db.refresh(prefs)
        return PreferencesResponse(session_id=prefs.session_id, topics=prefs.topics)

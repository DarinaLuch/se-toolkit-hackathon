from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from database import get_db
from models import Digest

router = APIRouter()


class DigestCreate(BaseModel):
    session_id: str
    topics: List[str]
    summary: str
    article_ids: Optional[List[int]] = None


class DigestOut(BaseModel):
    id: int
    session_id: str
    topics: List[str]
    summary: str
    article_ids: Optional[List[int]] = None
    created_at: datetime

    model_config = {"from_attributes": True}


@router.get("/{session_id}", response_model=List[DigestOut])
def get_digest_history(session_id: str, db: Session = Depends(get_db)):
    """Get all past digests for a session, newest first."""
    digests = (
        db.query(Digest)
        .filter(Digest.session_id == session_id)
        .order_by(Digest.created_at.desc())
        .all()
    )
    return digests


@router.post("/", response_model=DigestOut)
def save_digest(digest: DigestCreate, db: Session = Depends(get_db)):
    """Save a generated digest to history."""
    db_digest = Digest(
        session_id=digest.session_id,
        topics=digest.topics,
        summary=digest.summary,
        article_ids=digest.article_ids or [],
    )
    db.add(db_digest)
    db.commit()
    db.refresh(db_digest)
    return db_digest

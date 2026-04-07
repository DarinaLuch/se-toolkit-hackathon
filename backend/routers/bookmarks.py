from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from database import get_db
from models import Bookmark, Article

router = APIRouter()


class BookmarkCreate(BaseModel):
    session_id: str
    article_id: int


class ArticleOut(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    url: Optional[str] = None
    url_to_image: Optional[str] = None
    source_name: Optional[str] = None
    topic: Optional[str] = None

    model_config = {"from_attributes": True}


class BookmarkOut(BaseModel):
    id: int
    session_id: str
    article_id: int
    created_at: datetime
    article: Optional[ArticleOut] = None

    model_config = {"from_attributes": True}


@router.get("/{session_id}", response_model=List[BookmarkOut])
def get_bookmarks(session_id: str, db: Session = Depends(get_db)):
    """Get all bookmarked articles for a session."""
    bookmarks = (
        db.query(Bookmark)
        .filter(Bookmark.session_id == session_id)
        .order_by(Bookmark.created_at.desc())
        .all()
    )
    # Enrich with article data
    result = []
    for bm in bookmarks:
        article = db.query(Article).filter(Article.id == bm.article_id).first()
        result.append(BookmarkOut(
            id=bm.id,
            session_id=bm.session_id,
            article_id=bm.article_id,
            created_at=bm.created_at,
            article=article,
        ))
    return result


@router.post("/", response_model=BookmarkOut)
def add_bookmark(bookmark: BookmarkCreate, db: Session = Depends(get_db)):
    """Bookmark an article."""
    # Check if article exists
    article = db.query(Article).filter(Article.id == bookmark.article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    # Check if already bookmarked
    existing = (
        db.query(Bookmark)
        .filter(
            Bookmark.session_id == bookmark.session_id,
            Bookmark.article_id == bookmark.article_id,
        )
        .first()
    )
    if existing:
        return BookmarkOut(
            id=existing.id,
            session_id=existing.session_id,
            article_id=existing.article_id,
            created_at=existing.created_at,
            article=article,
        )

    bm = Bookmark(session_id=bookmark.session_id, article_id=bookmark.article_id)
    db.add(bm)
    db.commit()
    db.refresh(bm)
    return BookmarkOut(
        id=bm.id,
        session_id=bm.session_id,
        article_id=bm.article_id,
        created_at=bm.created_at,
        article=article,
    )


@router.delete("/{session_id}/{article_id}")
def remove_bookmark(session_id: str, article_id: int, db: Session = Depends(get_db)):
    """Remove a bookmark."""
    bm = (
        db.query(Bookmark)
        .filter(
            Bookmark.session_id == session_id,
            Bookmark.article_id == article_id,
        )
        .first()
    )
    if not bm:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    db.delete(bm)
    db.commit()
    return {"status": "ok"}

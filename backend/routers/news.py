from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional, Any
from sqlalchemy.orm import Session

from database import get_db
from models import UserPreference, Article, Digest
from services.news_service import fetch_articles
from services.llm_service import summarize_articles

router = APIRouter()


class ArticleResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    url: Optional[str] = None
    url_to_image: Optional[str] = None
    source_name: Optional[str] = None
    published_at: Optional[str] = None
    topic: Optional[str] = None

    model_config = {"from_attributes": True}


class DigestResponse(BaseModel):
    summary: str
    article_count: int
    topics: List[str]


@router.get("/articles", response_model=List[ArticleResponse])
async def get_articles(session_id: str = Query(...), db: Session = Depends(get_db)):
    """Fetch articles for a user's saved topics. Creates article records in DB."""
    # Get user preferences
    prefs = db.query(UserPreference).filter(UserPreference.session_id == session_id).first()
    if not prefs:
        # Default topics if no preferences saved yet
        topics = ["technology", "science"]
    else:
        topics = prefs.topics

    # Fetch articles (real or mock)
    raw_articles = await fetch_articles(topics)

    # Save articles to DB and build response
    article_responses = []
    for raw in raw_articles:
        source = raw.get("source", {})
        source_name = source.get("name", "") if isinstance(source, dict) else raw.get("source_name", "")

        article = Article(
            title=raw.get("title", ""),
            description=raw.get("description"),
            url=raw.get("url"),
            url_to_image=raw.get("urlToImage") or raw.get("url_to_image"),
            source_name=source_name,
            published_at=raw.get("publishedAt") or raw.get("published_at"),
            content=raw.get("content"),
            topic=raw.get("topic"),
        )
        db.add(article)
        db.flush()  # Get the ID without committing

        article_responses.append(ArticleResponse(
            id=article.id,
            title=article.title,
            description=article.description,
            url=article.url,
            url_to_image=article.url_to_image,
            source_name=article.source_name,
            published_at=article.published_at,
            topic=article.topic,
        ))

    db.commit()
    return article_responses


@router.get("/digest", response_model=DigestResponse)
async def generate_digest(session_id: str = Query(...), db: Session = Depends(get_db)):
    """Generate AI-powered digest summary for user's topics."""
    # Get user preferences
    prefs = db.query(UserPreference).filter(UserPreference.session_id == session_id).first()
    if not prefs:
        topics = ["technology", "science"]
    else:
        topics = prefs.topics

    # Fetch articles
    raw_articles = await fetch_articles(topics)

    if not raw_articles:
        raise HTTPException(status_code=404, detail="No articles found for selected topics")

    # Generate summary via LLM
    summary = await summarize_articles(raw_articles, topics)

    return DigestResponse(
        summary=summary,
        article_count=len(raw_articles),
        topics=topics,
    )

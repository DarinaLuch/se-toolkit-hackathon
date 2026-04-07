from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class UserPreference(Base):
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True, nullable=False)
    topics = Column(JSON, nullable=False, default=list)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint("session_id", name="uq_session_id"),
    )


class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    url = Column(String, nullable=True)
    url_to_image = Column(String, nullable=True)
    source_name = Column(String, nullable=True)
    published_at = Column(String, nullable=True)
    content = Column(Text, nullable=True)
    topic = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    bookmarks = relationship("Bookmark", back_populates="article", cascade="all, delete-orphan")


class Digest(Base):
    __tablename__ = "digests"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True, nullable=False)
    topics = Column(JSON, nullable=False, default=list)
    summary = Column(Text, nullable=False)
    article_ids = Column(JSON, nullable=True, default=list)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Bookmark(Base):
    __tablename__ = "bookmarks"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True, nullable=False)
    article_id = Column(Integer, ForeignKey("articles.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    article = relationship("Article", back_populates="bookmarks")

    __table_args__ = (
        UniqueConstraint("session_id", "article_id", name="uq_session_article"),
    )

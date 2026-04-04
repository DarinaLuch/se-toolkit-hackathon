from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from database import engine, Base
from routers import news, preferences, digests, bookmarks


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="AI News Digest API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(news.router, prefix="/api/news", tags=["news"])
app.include_router(preferences.router, prefix="/api/preferences", tags=["preferences"])
app.include_router(digests.router, prefix="/api/digests", tags=["digests"])
app.include_router(bookmarks.router, prefix="/api/bookmarks", tags=["bookmarks"])


@app.get("/health")
def health():
    return {"status": "ok"}

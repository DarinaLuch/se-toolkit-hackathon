import httpx
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any

NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")
NEWS_API_BASE = "https://newsapi.org/v2"

MOCK_ARTICLES = {
    "technology": [
        {
            "title": "OpenAI releases new reasoning model surpassing human performance",
            "description": "The latest AI model demonstrates unprecedented capabilities in complex reasoning tasks across mathematics, science, and coding.",
            "url": "https://example.com/openai-model",
            "urlToImage": "https://picsum.photos/seed/tech1/800/400",
            "source": {"name": "Tech Crunch"},
            "publishedAt": datetime.utcnow().isoformat(),
            "content": "OpenAI has released a new model that surpasses human performance on many benchmarks..."
        },
        {
            "title": "Apple Vision Pro 2 announced with 40% lighter design",
            "description": "Apple's next generation spatial computer promises a dramatically improved experience with new display technology.",
            "url": "https://example.com/vision-pro-2",
            "urlToImage": "https://picsum.photos/seed/tech2/800/400",
            "source": {"name": "The Verge"},
            "publishedAt": datetime.utcnow().isoformat(),
            "content": "Apple has unveiled the Vision Pro 2 with a much lighter design..."
        },
    ],
    "science": [
        {
            "title": "Scientists discover new species of deep-sea creature near hydrothermal vents",
            "description": "A research team has found a previously unknown organism that thrives in extreme conditions at the ocean floor.",
            "url": "https://example.com/deep-sea-creature",
            "urlToImage": "https://picsum.photos/seed/sci1/800/400",
            "source": {"name": "Nature"},
            "publishedAt": datetime.utcnow().isoformat(),
            "content": "Scientists have discovered a new species near hydrothermal vents..."
        },
    ],
    "business": [
        {
            "title": "Global markets rally as inflation data shows continued cooling",
            "description": "Stock markets surged worldwide after new economic data suggested inflation is returning to target levels.",
            "url": "https://example.com/markets-rally",
            "urlToImage": "https://picsum.photos/seed/biz1/800/400",
            "source": {"name": "Financial Times"},
            "publishedAt": datetime.utcnow().isoformat(),
            "content": "Global markets rallied strongly on the latest inflation data..."
        },
    ],
    "health": [
        {
            "title": "New study links Mediterranean diet to 25% lower dementia risk",
            "description": "A large-scale study following 60,000 participants over 10 years finds strong correlation between diet and brain health.",
            "url": "https://example.com/mediterranean-diet",
            "urlToImage": "https://picsum.photos/seed/health1/800/400",
            "source": {"name": "The Lancet"},
            "publishedAt": datetime.utcnow().isoformat(),
            "content": "Researchers have found that following a Mediterranean diet reduces dementia risk..."
        },
    ],
    "sports": [
        {
            "title": "Champions League final set: Real Madrid vs Manchester City",
            "description": "Both clubs secured their spots in the final with dominant semi-final performances.",
            "url": "https://example.com/champions-league",
            "urlToImage": "https://picsum.photos/seed/sport1/800/400",
            "source": {"name": "ESPN"},
            "publishedAt": datetime.utcnow().isoformat(),
            "content": "Real Madrid and Manchester City will meet in the Champions League final..."
        },
    ],
    "entertainment": [
        {
            "title": "Dune: Part Three officially greenlit by Warner Bros",
            "description": "Following the massive box office success of Part Two, the trilogy's conclusion is confirmed.",
            "url": "https://example.com/dune-three",
            "urlToImage": "https://picsum.photos/seed/ent1/800/400",
            "source": {"name": "Variety"},
            "publishedAt": datetime.utcnow().isoformat(),
            "content": "Warner Bros has officially greenlit Dune Part Three..."
        },
    ],
}


async def fetch_articles(topics: List[str]) -> List[Dict[str, Any]]:
    if not NEWS_API_KEY:
        # Return mock articles for selected topics
        articles = []
        for topic in topics:
            topic_lower = topic.lower()
            if topic_lower in MOCK_ARTICLES:
                for article in MOCK_ARTICLES[topic_lower]:
                    articles.append({**article, "topic": topic})
        return articles

    articles = []
    async with httpx.AsyncClient() as client:
        for topic in topics:
            try:
                response = await client.get(
                    f"{NEWS_API_BASE}/top-headlines",
                    params={
                        "category": topic.lower(),
                        "language": "en",
                        "pageSize": 5,
                        "apiKey": NEWS_API_KEY,
                    },
                    timeout=10,
                )
                if response.status_code == 200:
                    data = response.json()
                    for article in data.get("articles", []):
                        articles.append({**article, "topic": topic})
            except Exception as e:
                print(f"Error fetching {topic}: {e}")

    return articles

import httpx
import os
import json
from typing import List, Dict, Any

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "anthropic")  # anthropic | openai | qwen
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "")  # for qwen proxy
LLM_MODEL = os.getenv("LLM_MODEL", "claude-sonnet-4-20250514")


def _build_prompt(articles: List[Dict[str, Any]], topics: List[str]) -> str:
    topic_str = ", ".join(topics)
    articles_text = ""
    for i, a in enumerate(articles[:15], 1):
        articles_text += f"\n[{i}] {a.get('title', 'No title')}\n"
        if a.get("description"):
            articles_text += f"    {a['description']}\n"
        articles_text += f"    Source: {a.get('source', {}).get('name', 'Unknown') if isinstance(a.get('source'), dict) else a.get('source_name', 'Unknown')}\n"

    return f"""You are a news digest assistant. The user is interested in: {topic_str}.

Here are today's top articles:
{articles_text}

Write a clear, engaging daily news digest. For each topic that has articles:
1. Write a short section header (e.g. "🔬 Science")
2. Write 2-3 sentences summarizing the key story
3. Mention the source

Keep it conversational, informative, and under 400 words total. End with one sentence: "That's your digest for today!"

Do NOT add any preamble like "Here is your digest". Just start with the first section."""


async def summarize_articles(articles: List[Dict[str, Any]], topics: List[str]) -> str:
    prompt = _build_prompt(articles, topics)

    if not LLM_API_KEY and not LLM_BASE_URL:
        # Fallback: simple template-based digest
        return _template_digest(articles, topics)

    if LLM_PROVIDER == "anthropic":
        return await _call_anthropic(prompt)
    else:
        # OpenAI-compatible (openai or qwen proxy)
        return await _call_openai_compatible(prompt)


async def _call_anthropic(prompt: str) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": LLM_API_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": LLM_MODEL,
                "max_tokens": 1024,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=30,
        )
        data = response.json()
        return data["content"][0]["text"]


async def _call_openai_compatible(prompt: str) -> str:
    base_url = LLM_BASE_URL or "https://api.openai.com/v1"
    model = LLM_MODEL if LLM_PROVIDER != "openai" else "gpt-4o-mini"

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {LLM_API_KEY}",
                "content-type": "application/json",
            },
            json={
                "model": model,
                "max_tokens": 1024,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=30,
        )
        data = response.json()
        return data["choices"][0]["message"]["content"]


def _template_digest(articles: List[Dict[str, Any]], topics: List[str]) -> str:
    """Fallback digest when no LLM key is configured."""
    lines = ["📰 **Your News Digest**\n"]
    by_topic: Dict[str, list] = {}
    for a in articles:
        t = a.get("topic", "General")
        by_topic.setdefault(t, []).append(a)

    icons = {"technology": "💻", "science": "🔬", "business": "💼",
             "health": "🏥", "sports": "⚽", "entertainment": "🎬"}

    for topic, arts in by_topic.items():
        icon = icons.get(topic.lower(), "📌")
        lines.append(f"\n{icon} **{topic.title()}**")
        for a in arts[:2]:
            title = a.get("title", "")
            source = a.get("source", {})
            source_name = source.get("name", "") if isinstance(source, dict) else a.get("source_name", "")
            lines.append(f"• {title} *(via {source_name})*")

    lines.append("\nThat's your digest for today!")
    return "\n".join(lines)

import httpx
import os
import json
from typing import List, Dict, Any

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "anthropic")
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "")
LLM_MODEL = os.getenv("LLM_MODEL", "claude-sonnet-4-20250514")


def _build_prompt(articles: List[Dict[str, Any]], topics: List[str]) -> str:
    topic_str = ", ".join(topics)
    articles_text = ""
    for i, a in enumerate(articles[:15], 1):
        title = a.get('title', 'No title')
        desc = a.get('description', '')
        content = a.get('content', '') or a.get('content_full', '')
        if content and len(content) > 500:
            content = content[:500] + '...'
        articles_text += f"\n[{i}] {title}"
        if desc:
            articles_text += f"\n    Summary: {desc}"
        if content:
            articles_text += f"\n    Details: {content}"
        source = a.get('source', {})
        source_name = source.get('name', '') if isinstance(source, dict) else a.get('source_name', 'Unknown')
        articles_text += f"\n    Source: {source_name}\n"

    return f"""You are a professional news editor writing a daily digest. The user is interested in: {topic_str}.

Here are today's articles with their summaries and details:
{articles_text}

Write a clear, engaging daily news digest that reads like a newsletter, NOT a list of headlines. For each topic:
1. Start with a section header (e.g. "🔬 Science")
2. Write 2-3 SENTENCES that synthesize the KEY POINTS — explain what happened, why it matters, and any important details
3. Do NOT just repeat headlines — write actual summary paragraphs a person would enjoy reading
4. Mention the source in parentheses at the end

Keep it conversational, informative, and under 400 words total. End with: "That's your digest for today!"

Do NOT add any preamble like "Here is your digest". Just start with the first section."""


async def summarize_articles(articles: List[Dict[str, Any]], topics: List[str]) -> str:
    prompt = _build_prompt(articles, topics)

    if not LLM_API_KEY and not LLM_BASE_URL:
        return _template_digest(articles, topics)

    try:
        if LLM_PROVIDER == "anthropic":
            return await _call_anthropic(prompt)
        else:
            return await _call_openai_compatible(prompt)
    except Exception as e:
        print(f"LLM call failed, using template fallback: {e}")
        return _template_digest(articles, topics)


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
            timeout=10,
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
            timeout=10,
        )
        data = response.json()
        return data["choices"][0]["message"]["content"]


def _template_digest(articles: List[Dict[str, Any]], topics: List[str]) -> str:
    """Template-based digest — shows all articles with full descriptions/content."""
    lines: List[str] = []
    by_topic: Dict[str, list] = {}
    for a in articles:
        t = a.get("topic", "General")
        by_topic.setdefault(t, []).append(a)

    icons = {"technology": "💻", "science": "🔬", "business": "💼",
             "health": "🏥", "sports": "⚽", "entertainment": "🎬"}

    for topic, arts in by_topic.items():
        icon = icons.get(topic.lower(), "📌")
        lines.append(f"\n{icon} **{topic.title()}**")
        lines.append("")
        for a in arts[:3]:
            title = a.get("title", "")
            desc = a.get("description", "")
            content = a.get("content", "") or a.get("content_full", "")
            source = a.get("source", {})
            source_name = source.get("name", "") if isinstance(source, dict) else a.get("source_name", "")

            lines.append(f"**{title}**")
            if desc:
                lines.append(desc)
            elif content:
                clean = content.replace("[+...]", "").replace("[...]", "").strip()
                if clean:
                    lines.append(clean[:400] + "..." if len(clean) > 400 else clean)
            lines.append("")

    if not lines:
        return "📰 No articles found for your selected topics. Try different topics or check back later!"

    lines.append("—\nThat's your digest for today!")
    return "\n".join(lines)

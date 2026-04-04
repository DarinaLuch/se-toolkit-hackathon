# Briefed — AI News Digest

> Get a daily personalized news summary on topics you care about, explained simply by AI.

## Demo

![Digest view](https://picsum.photos/seed/briefed1/800/400)
![Articles view](https://picsum.photos/seed/briefed2/800/400)

## Product Context

**End users:** Anyone who wants to stay informed without spending hours reading news.

**Problem:** There's too much news. It's hard to know what matters, and reading across multiple sources is exhausting.

**Solution:** Pick your topics, click one button — the app fetches real articles and an AI writes you a clean, readable digest in plain language. You can also browse individual articles and bookmark the ones you want to read later.

## Features

### Implemented ✅
- Select topics you care about (technology, science, business, health, sports, entertainment)
- AI-generated digest summarizing today's top articles in plain language
- Browse individual articles grouped by topic
- Bookmark articles to read later
- Digest history — browse past digests
- Works with mock data (no NewsAPI key needed to try it)
- LLM-powered via Qwen proxy (OpenAI-compatible) or Anthropic/OpenAI keys

### Not yet implemented 🔜
- "Explain this like I'm 5" mode per article
- Email/scheduled delivery
- Bias detector
- User accounts (currently uses browser session ID)

## Usage

1. Open the app at `http://your-vm-ip:3000`
2. In the sidebar, select the topics you care about and click **Save & Refresh**
3. Click **Generate Today's Digest** — the AI will summarize today's top articles
4. Browse articles below, click 🔖 to save any you want to read later
5. Click **History** to revisit past digests

## Deployment

### Requirements
- Ubuntu 24.04
- Docker and Docker Compose installed
- A NewsAPI key (free at https://newsapi.org)
- Qwen proxy running on port 42005 (from Lab 7/8 setup), OR an Anthropic/OpenAI API key

### Step-by-step

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/se-toolkit-hackathon
cd se-toolkit-hackathon

# 2. Create your env file
cp .env.example .env.secret

# 3. Fill in your keys
nano .env.secret
# Set NEWS_API_KEY, LLM_PROVIDER, LLM_API_KEY, etc.

# 4. Build and start
docker compose --env-file .env.secret up --build -d

# 5. Open in browser
# http://your-vm-ip:3000
```

### Environment variables

| Variable | Description | Default |
|---|---|---|
| `NEWS_API_KEY` | From newsapi.org (free) | *(uses mock data if empty)* |
| `LLM_PROVIDER` | `anthropic`, `openai`, or `qwen` | `anthropic` |
| `LLM_API_KEY` | Your API key | *(uses template digest if empty)* |
| `LLM_BASE_URL` | For Qwen proxy: `http://host.docker.internal:42005/v1` | |
| `LLM_MODEL` | Model name | `claude-sonnet-4-20250514` |

### Qwen proxy setup (from labs)

```bash
# In .env.secret:
LLM_PROVIDER=qwen
LLM_API_KEY=my-secret-qwen-key
LLM_BASE_URL=http://host.docker.internal:42005/v1
LLM_MODEL=coder-model
```

### Verify it's running

```bash
docker compose --env-file .env.secret ps
curl http://localhost:8000/health
# → {"status":"ok"}
```

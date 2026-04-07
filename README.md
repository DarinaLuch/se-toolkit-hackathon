# Briefed — AI News Digest

> Get a daily personalized news summary on topics you care about, explained simply by AI.

## Demo
<img width="1917" height="1042" alt="1" src="https://github.com/user-attachments/assets/a714ace5-3a4a-474c-9038-dec53afa4f5b" />
<img width="1916" height="1038" alt="2" src="https://github.com/user-attachments/assets/19176abc-2875-488a-b876-c52f3abe3b12" />

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
- Works with NewsAPI
- LLM-powered via Qwen proxy
  
## Usage

1. Open the app at `http://your-vm-ip:3000`
2. In the sidebar, select the topics you care about and click **Find News**
3. You can read the latest news on selected topics, click 🔖 to save any you want to read later
5. Click **Generate Today's Digest** — the AI will summarize today's top articles
6. Click **History** to revisit past digests
7. Click **Saved** to read saved news


## Deployment Instructions

### Prerequisites
- OS: Ubuntu 22.04 / 24.04
- Tools: Docker Engine & Docker Compose plugin, `git`, `curl`
- Network: Public IP address for the VM
- Firewall: Inbound traffic allowed on port `3000` (Frontend) and `8000` (Backend API)

### 1. Clone the Repository
```bash
git clone https://github.com/DarinaLuch/se-toolkit-hackathon.git
cd se-toolkit-hackathon
```

### 2. Configure Environment Variables

Create a local secret file. Never commit this to git.
```bash
cp .env.example .env.secret
nano .env.secret
```

| Variable | Description | Fallback Behavior |
|---|---|---|
| `NEWS_API_KEY` | Key from NewsAPI.org | If empty, app serves built-in mock articles |
| `LLM_PROVIDER` | `qwen`, `anthropic`, or `openai` | Defaults to `qwen` |
| `LLM_API_KEY` | Your LLM proxy/API key | If empty, app uses a readable template summary |
| `LLM_BASE_URL` | Proxy URL (e.g. `http://host.docker.internal:42005/v1`) | Falls back to `https://api.openai.com/v1` if `qwen`/`openai` selected |
| `LLM_MODEL` | Model name (e.g. `coder-model`) | Defaults to `gpt-4o-mini` for OpenAI |

### 3. Configure Docker DNS (VM Network Fix)

University/corporate networks often block external DNS resolution inside containers. Fix this by adding public DNS resolvers:
```bash
echo '{"dns": ["8.8.8.8", "8.8.4.4", "1.1.1.1"]}' | sudo tee /etc/docker/daemon.json
sudo systemctl restart docker
```

### 4. Build & Start Services
```bash
docker compose --env-file .env.secret up --build -d
```

This command:
1. Builds backend & frontend images
2. Starts PostgreSQL with a health check
3. Waits for the database to be `healthy`
4. Launches backend (FastAPI) and frontend (Nginx)

### 5. Verify Deployment

Check container status (all should show `healthy` or `up`):
```bash
docker compose ps
```

Test backend health endpoint:
```bash
curl http://localhost:8000/health
# → {"status":"ok"}
```

Test frontend proxy & API routing:
```bash
curl -s http://localhost:3000/api/news/articles?session_id=test | head -c 200
# → JSON array of articles (real or mock)
```

### 6. Access the Application

Open your browser and navigate to: http://10.93.25.191:3000/
- Select topics in the sidebar and click **Find News**
- Click **Generate Today's Digest** to fetch an AI-written summary
- Browse individual articles and click 🔖 to bookmark them

### 🔒 Security & Maintenance

- **Secrets:** `.env.secret` is in `.gitignore` and never pushed to GitHub
- **Updates:** `git pull && docker compose --env-file .env.secret up -d --build`
- **Stop:** `docker compose down`
- **Wipe Data:** `docker compose down -v` (removes the PostgreSQL volume)

### 🛠 Troubleshooting

| Issue | Fix |
|---|---|
| `getaddrinfo EAI_AGAIN` / DNS errors | Apply Step 3 (Docker DNS config) and restart Docker |
| "No articles found" on UI | Check `docker compose logs backend`. If NewsAPI is blocked, leave `NEWS_API_KEY` empty to test mock mode |
| Digest shows template instead of AI summary | Verify `LLM_BASE_URL` is reachable. Leave `LLM_API_KEY` empty to intentionally use template fallback |
| Port 3000/8000 unreachable | Run `sudo ufw allow 3000,8000/tcp` and check cloud provider security groups |
| Backend container unhealthy | Run `docker compose logs backend` to check for migration or connection errors |

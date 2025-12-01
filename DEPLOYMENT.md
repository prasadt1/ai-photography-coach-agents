# Deployment Guide: AI Photography Coach

This guide covers multiple deployment options for the AI Photography Coach multi-agent system.

---

## Table of Contents

1. [Local Development](#local-development)
2. [Docker Deployment](#docker-deployment)
3. [Google Cloud Run Deployment](#google-cloud-run-deployment)
4. [Agent Development Kit (ADK) Deployment](#agent-development-kit-adk-deployment)
5. [Production Considerations](#production-considerations)

---

## Local Development

### Prerequisites

- Python 3.11+
- Google API Key (Gemini API access)

### Setup

```bash
# Clone repository
git clone https://github.com/prasadt1/ai-photography-coach-agents.git
cd ai-photography-coach-agents

# Install dependencies
pip install -r requirements.txt

# Configure API key
export GOOGLE_API_KEY="your_gemini_api_key_here"

# Run Streamlit app
python3 -m streamlit run agents_capstone/app_streamlit.py
```

### Verify Installation

```bash
# Test agent functionality
python3 demo_eval.py

# Run evaluation suite
python3 run_evaluation.py
```

**Access:** http://localhost:8501

---

## Docker Deployment

### Build Container

```bash
# Build Docker image
docker build -t ai-photography-coach:latest .

# Run container
docker run -p 8501:8501 \
  -e GOOGLE_API_KEY="your_api_key" \
  -v $(pwd)/agents_memory.db:/app/agents_memory.db \
  ai-photography-coach:latest
```

### Docker Compose (Recommended for Production)

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8501:8501"
    environment:
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
    volumes:
      - ./agents_memory.db:/app/agents_memory.db
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8501/_stcore/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

Run with:

```bash
docker-compose up -d
```

**Access:** http://localhost:8501

---

## Google Cloud Run Deployment

### Prerequisites

- Google Cloud SDK installed
- Google Cloud project with billing enabled
- Container Registry or Artifact Registry enabled

### Step 1: Build and Push Container

```bash
# Authenticate with Google Cloud
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# Build and push to Google Container Registry
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/ai-photography-coach:latest

# Alternative: Use Artifact Registry
gcloud builds submit --tag us-central1-docker.pkg.dev/YOUR_PROJECT_ID/ai-coach/app:latest
```

### Step 2: Deploy to Cloud Run

```bash
# Deploy with Cloud Run
gcloud run deploy ai-photography-coach \
  --image gcr.io/YOUR_PROJECT_ID/ai-photography-coach:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_API_KEY="your_api_key" \
  --memory 2Gi \
  --cpu 2 \
  --max-instances 10 \
  --timeout 300
```

### Step 3: Configure Persistent Storage (Optional)

For production, replace SQLite with Cloud SQL:

```bash
# Create Cloud SQL instance
gcloud sql instances create photo-coach-db \
  --database-version=POSTGRES_14 \
  --tier=db-f1-micro \
  --region=us-central1

# Create database
gcloud sql databases create agents_memory \
  --instance=photo-coach-db

# Connect Cloud Run to Cloud SQL
gcloud run services update ai-photography-coach \
  --add-cloudsql-instances YOUR_PROJECT_ID:us-central1:photo-coach-db
```

Update `agents_capstone/tools/memory.py` to use Cloud SQL connection.

**Access:** Your app will be available at the provided Cloud Run URL

---

## Agent Development Kit (ADK) Deployment

### Prerequisites

- Google Cloud project
- ADK SDK installed: `pip install google-adk`

### Step 1: ADK-Compatible Architecture

The system is already designed with ADK compatibility:

- **Memory Adapter** (`tools/adk_adapter.py`): Matches ADK Memory API
- **Orchestrator**: Stateless coordination (ADK-ready)
- **Agents**: Independent modules (can be deployed as separate Cloud Functions)

### Step 2: Deploy Agents with ADK

```python
# adk_deployment.py
from google.adk import Agent, Memory, Tool
from agents_capstone.agents import VisionAgent, KnowledgeAgent, Orchestrator

# Define agent with ADK
photography_agent = Agent(
    name="photography-coach",
    description="AI-powered photography coaching system",
    memory=Memory(backend="cloud"),  # Uses Cloud Memory Store
)

# Register tools
@photography_agent.tool
def analyze_photo(image_url: str) -> dict:
    """Analyze photo composition and technical settings."""
    vision = VisionAgent()
    return vision.analyze(image_url, skill_level="beginner")

@photography_agent.tool
def get_coaching(query: str, session_id: str) -> dict:
    """Get personalized photography coaching."""
    knowledge = KnowledgeAgent()
    # ... coaching logic
    
# Deploy to Agent Engine
photography_agent.deploy(
    project_id="YOUR_PROJECT_ID",
    region="us-central1",
)
```

### Step 3: Deploy

```bash
# Deploy agent to Google Cloud
python adk_deployment.py

# Test deployed agent
curl -X POST https://YOUR_AGENT_URL/invoke \
  -H "Content-Type: application/json" \
  -d '{"query": "How can I improve composition?"}'
```

---

## Production Considerations

### 1. **Authentication & Authorization**

```python
# Add to Streamlit app
import streamlit_authenticator as stauth

authenticator = stauth.Authenticate(
    credentials,
    "photo_coach_cookie",
    "signature_key",
    cookie_expiry_days=30
)

name, authentication_status, username = authenticator.login("Login", "main")

if authentication_status:
    # Show app
    pass
elif authentication_status == False:
    st.error("Username/password is incorrect")
```

### 2. **Rate Limiting**

```python
# Add to agents/knowledge_agent.py
from functools import lru_cache
import time

class RateLimiter:
    def __init__(self, max_calls=10, period=60):
        self.calls = []
        self.max_calls = max_calls
        self.period = period
    
    def allow_call(self):
        now = time.time()
        self.calls = [c for c in self.calls if now - c < self.period]
        if len(self.calls) < self.max_calls:
            self.calls.append(now)
            return True
        return False
```

### 3. **Monitoring & Observability**

Enable structured logging:

```python
# Already implemented in logging_config.py
import logging.config
logging.config.fileConfig('logging_config.py')

# Add Cloud Logging integration
from google.cloud import logging as cloud_logging

client = cloud_logging.Client()
client.setup_logging()
```

### 4. **Caching**

Add Redis for response caching:

```python
import redis

cache = redis.Redis(host='localhost', port=6379, decode_responses=True)

def get_coaching_cached(query, vision_data):
    cache_key = f"coach:{query}:{hash(str(vision_data))}"
    cached = cache.get(cache_key)
    if cached:
        return json.loads(cached)
    
    result = knowledge_agent.coach(query, vision_data, session)
    cache.setex(cache_key, 3600, json.dumps(result))  # 1 hour TTL
    return result
```

### 5. **Horizontal Scaling**

For high traffic, use Cloud Run with autoscaling:

```bash
gcloud run services update ai-photography-coach \
  --min-instances 2 \
  --max-instances 100 \
  --concurrency 80
```

### 6. **Cost Optimization**

- **Use Gemini Flash** (not Pro) for cost-effective responses
- **Implement caching** to reduce API calls
- **Set max instances** to control Cloud Run costs
- **Monitor usage** with Cloud Monitoring

### 7. **Security**

```bash
# Store API keys in Secret Manager
gcloud secrets create GOOGLE_API_KEY --data-file=-

# Grant Cloud Run access
gcloud secrets add-iam-policy-binding GOOGLE_API_KEY \
  --member serviceAccount:YOUR_SERVICE_ACCOUNT \
  --role roles/secretmanager.secretAccessor

# Update Cloud Run to use secrets
gcloud run services update ai-photography-coach \
  --update-secrets GOOGLE_API_KEY=GOOGLE_API_KEY:latest
```

---

## Environment Variables

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `GOOGLE_API_KEY` | Yes | Gemini API key | None |
| `DB_PATH` | No | SQLite database path | `agents_memory.db` |
| `LOG_LEVEL` | No | Logging level | `INFO` |
| `MAX_HISTORY_TURNS` | No | Max conversation turns | `50` |
| `CONTEXT_COMPACT_THRESHOLD` | No | When to compact context | `6` |

---

## Troubleshooting

### Issue: "API Key Not Found"

**Solution:**
```bash
# Verify API key is set
echo $GOOGLE_API_KEY

# Set in current shell
export GOOGLE_API_KEY="your_key"

# Set permanently (add to ~/.zshrc or ~/.bashrc)
echo 'export GOOGLE_API_KEY="your_key"' >> ~/.zshrc
source ~/.zshrc
```

### Issue: "Database Locked"

**Solution:**
```bash
# Check for stale locks
rm agents_memory.db-lock

# Or use WAL mode (better for concurrent access)
# Add to memory.py:
# conn.execute("PRAGMA journal_mode=WAL")
```

### Issue: "Streamlit Port Already in Use"

**Solution:**
```bash
# Use different port
streamlit run agents_capstone/app_streamlit.py --server.port 8502

# Or kill existing process
lsof -ti:8501 | xargs kill -9
```

### Issue: Cloud Run Timeout

**Solution:**
```bash
# Increase timeout
gcloud run services update ai-photography-coach \
  --timeout 600  # 10 minutes
```

---

## Performance Benchmarks

### Local Development
- Response latency: 1-3 seconds
- Memory usage: ~200MB
- Concurrent users: 1-5

### Docker Deployment
- Response latency: 1-3 seconds
- Memory usage: ~300MB
- Concurrent users: 10-20

### Cloud Run (2 vCPU, 2GB RAM)
- Response latency: 2-4 seconds
- Memory usage: ~500MB
- Concurrent users: 100+
- Cost: ~$0.10/1000 requests

---

## Support

For deployment issues:
1. Check logs: `docker logs <container_id>` or Cloud Run logs
2. Review [GitHub Issues](https://github.com/prasadt1/ai-photography-coach-agents/issues)
3. Consult [Google Cloud Documentation](https://cloud.google.com/run/docs)

---

## License

MIT License - See LICENSE file for details

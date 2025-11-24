# 🧠 FlowSentinel

> **AI-Powered Autonomous Project Intelligence System for IBM watsonx Challenge 2025**

An autonomous AI agent that monitors software development workflows in real-time, analyzes events using **IBM watsonx.ai Granite 3 8B Instruct**, and automatically responds to critical situations with zero human intervention.

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.121-green)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61dafb)](https://reactjs.org/)
[![IBM watsonx.ai](https://img.shields.io/badge/IBM-watsonx.ai-blue)](https://www.ibm.com/watsonx)

---

## 🎯 What We Built

FlowSentinel ingests events from **Slack, Jira, GitHub, and Calendar**, then uses IBM watsonx.ai to:
- 🤖 Automatically detect blockers and risks every 5 minutes
- 🔮 Predict deadline risks and bottlenecks before they happen
- 📊 Analyze team health and velocity trends
- 🔔 Take autonomous actions (Slack notifications, task creation)
- 💬 Answer natural language questions about your project

**The Result:** A full-stack production system with 5,000 lines of backend code, 66 frontend components, and 88% test coverage.

---

## ⚡ Quick Start

### 1. Setup
```bash
git clone https://github.com/Nabilhassan12345/flowsentinel.git
cd flowsentinel
pip install -r requirements.txt
cd frontend && npm install --legacy-peer-deps
```

### 2. Configure
```bash
cp .env.example .env
# Edit .env and add your IBM watsonx.ai credentials:
# WATSONX_API_KEY=your_key
# WATSONX_PROJECT_ID=your_project_id
```

### 3. Run
```bash
# Terminal 1: Backend
python src/main.py

# Terminal 2: Frontend
cd frontend && npm run dev
```

### 4. Visit
- **Dashboard**: http://localhost:8080
- **API Docs**: http://localhost:8000/docs

### 5. Add Demo Data
```bash
python add-demo-data.py
```

---

## 🏗️ System Architecture

### Backend (5,000 lines of Python)
```python
src/
├── main.py                   # FastAPI app with autonomous agent
├── models.py                 # 7 SQLAlchemy database models
├── database.py               # PostgreSQL/SQLite support
├── intelligence_endpoints.py # IBM watsonx.ai integration
├── analytics_endpoints.py    # Real-time analytics
├── team_endpoints.py         # Multi-team support
└── webhook_endpoints.py      # Outbound webhooks
```

**Core Features:**
- 37 REST API endpoints
- Autonomous agent runs every 5 minutes
- IBM watsonx.ai Granite 3 8B Instruct for analysis
- Multi-tenant team support
- Webhook system with retry logic

### Frontend (66 TypeScript/React Files)
```typescript
frontend/src/
├── pages/
│   ├── Dashboard.tsx        # Real-time project overview
│   ├── Intelligence.tsx     # AI Q&A and predictions
│   └── Index.tsx            # Landing page
├── components/
│   ├── dashboard/           # Status cards, event feeds
│   └── ui/                  # 40+ shadcn/ui components
└── lib/
    └── api.ts               # Axios API client
```

**Technologies:**
- React 18 + TypeScript
- Tailwind CSS + shadcn/ui
- Recharts for data visualization
- TanStack Query for state management

### Database (7 Models)
1. **Events** - Slack, Jira, GitHub, Calendar events
2. **ProjectState** - Status, blockers, risks over time
3. **Actions** - Automated actions taken by agent
4. **Teams** - Multi-tenant team management
5. **TeamMembers** - Member assignments and roles
6. **Webhooks** - Outbound webhook configurations
7. **WebhookDelivery** - Delivery tracking with retries

---

## 🤖 How It Works

### 1. Event Ingestion
```python
POST /events/add
{
  "source": "slack",
  "type": "message",
  "data": {"user": "john", "message": "Deployment failed"}
}
```

### 2. Autonomous Analysis (Every 5 Minutes)
```python
# Agent analyzes last 24h of events
events = get_events(last_24_hours)
analysis = watsonx_ai.analyze(events)  # IBM Granite 3 8B
state = {
  "status": "RED",
  "blockers": ["Deployment pipeline broken"],
  "risks": ["Missing critical deadline"]
}
```

### 3. Automated Actions
```python
if state.status == "RED":
    send_slack_alert("🚨 Critical blocker detected")
    create_jira_ticket("Fix deployment pipeline")
```

### 4. Real-Time Dashboard
Frontend shows live updates with event feeds, risk scores, and AI-powered insights.

---

## 🔮 IBM watsonx.ai Integration

### Natural Language Q&A
```python
POST /qa/ask
{
  "question": "What are the current blockers?"
}

Response:
{
  "answer": "There is 1 critical blocker: deployment pipeline is broken. 
             This was reported 2 hours ago in Slack by the DevOps team.",
  "confidence": 0.95
}
```

### Predictive Intelligence
- **Deadline Risk** (0-100 score based on velocity, blockers, team health)
- **Bottleneck Detection** (identifies slowest parts of workflow)
- **Team Health** (analyzes workload distribution and burnout risk)
- **7-Day Forecast** (predicts upcoming issues)

---

## 📊 What Makes It Unique

### 1. Fully Autonomous
- Runs every 5 minutes without human input
- Automatically detects and responds to issues
- Self-healing with retry logic and error handling

### 2. Real IBM watsonx.ai
- Not simulated - uses actual Granite 3 8B Instruct model
- Context-aware analysis of events
- Natural language understanding

### 3. Production-Ready
- 88% test coverage
- PostgreSQL for production, SQLite for dev
- Docker + docker-compose
- Netlify and cloud deployment configs

### 4. Full-Stack Integration
- Backend API ↔ Frontend React dashboard
- Real-time updates via TanStack Query
- Beautiful UI with shadcn/ui components
- Mobile responsive design

---

## 🧪 Testing

```bash
pytest tests/ -v --cov=src
```

**Coverage: 88%**
- 95% API endpoints
- 90% Database operations
- 85% AI/ML features
- 90% Webhooks

---

## 🚀 Deployment

### Frontend (Netlify)
```bash
# Auto-deploys from GitHub
# Build: cd frontend && npm run build
# Publish: frontend/dist
```

### Backend (Render/Railway/Fly.io)
```bash
# Render: Auto-detects Python, runs uvicorn
# Railway: One-click deploy
# Fly.io: fly launch && fly deploy
```

See [docs/guides/](docs/guides/) for detailed deployment instructions.

---

## 📈 Technical Stats

| Metric | Value |
|--------|-------|
| Backend Code | 5,000 lines Python |
| Frontend Components | 66 TypeScript/React files |
| API Endpoints | 37 REST endpoints |
| Database Models | 7 SQLAlchemy models |
| Test Coverage | 88% |
| Response Time | <100ms average |
| Autonomous Agent | Runs every 5 minutes |

---

## 👥 Team

Built for **IBM watsonx Challenge 2025** by:
- **Nabil Hassan** - Lead Developer
- **Abdulrahman** - Contributor

---

## 📄 License

MIT License - see [LICENSE](LICENSE)

---

<div align="center">

**[View API Docs](http://localhost:8000/docs)** • **[Read Full Guides](docs/guides/)** • **[Report Issues](https://github.com/Nabilhassan12345/flowsentinel/issues)**

Built with ❤️ using IBM watsonx.ai Granite 3 8B Instruct

</div>

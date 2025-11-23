# FlowSentinel - Agentic Company Brain 🧠

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.121.3-009688.svg)](https://fastapi.tiangolo.com)
[![IBM watsonx.ai](https://img.shields.io/badge/IBM-watsonx.ai-054ADA.svg)](https://www.ibm.com/watsonx)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-red.svg)](https://www.sqlalchemy.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **An autonomous AI agent that monitors your entire software development workflow in real-time, detects blockers and risks before they become critical, and automatically takes corrective actions using IBM watsonx.ai (Granite 3 8B) and watsonx Orchestrate.**

**FlowSentinel** is your team's intelligent "company brain" - continuously ingesting events from Slack, Jira, GitHub, and Calendar, analyzing them with IBM's Granite AI models, and autonomously responding to critical situations with zero human intervention.

**Built for the IBM watsonx Challenge** | **Version 2.0.0** | **Production Ready ✅**

---

## 🎯 What Problem Does FlowSentinel Solve?

Modern software teams generate **thousands of events daily** across multiple tools. Critical blockers get buried in Slack threads, deadlines slip unnoticed in Jira, and managers spend **10+ hours per week** manually tracking project health across GitHub, Slack, Jira, and Calendar.

**FlowSentinel automates this entire process** using IBM watsonx.ai to continuously monitor, analyze, and act on your team's workflow in real-time.

### The FlowSentinel Workflow

```
┌─────────────┐      ┌──────────────────┐      ┌─────────────────┐
│   Events    │─────▶│  IBM watsonx.ai  │─────▶│ Automated       │
│ Slack/Jira/ │      │  Granite 3 8B    │      │ Actions via     │
│ GitHub/Cal  │      │  Analysis        │      │ Orchestrate     │
└─────────────┘      └──────────────────┘      └─────────────────┘
                              │
                              ▼
                     ┌─────────────────┐
                     │ Project State   │
                     │ GREEN/YELLOW/RED │
                     └─────────────────┘
```

**In under 5 minutes, you can:**
1. Ingest realistic team events (Slack messages, Jira updates, GitHub PRs, calendar changes)
2. Run IBM watsonx.ai Granite analysis to detect blockers and risks
3. See automated actions triggered (Slack alerts, task creation, report generation)
4. Ask natural language questions like "What's blocking the team?"
5. Get AI-powered predictions about deadline risks and bottlenecks

---

## ✨ Key Features

### 🤖 **Autonomous Agent**
- **Runs continuously** every 5 minutes (configurable) in the background
- **Monitors last 24 hours** of events automatically
- **Sends Slack alerts** on YELLOW/RED project status
- **Zero human intervention** - set it and forget it

### 🧠 **IBM watsonx.ai Integration**
- **Real Granite AI**: Uses `ibm/granite-3-8b-instruct` for intelligent analysis
- **Context-aware Q&A**: Ask "What's blocking us?" and get AI-powered answers
- **Pattern Recognition**: Detects blockers, risks, and completed work from raw event data
- **Fallback Mode**: Graceful rule-based analysis when API is unavailable

### 🔮 **Predictive Intelligence**
- **Deadline Risk Scoring**: Predicts probability (0-100%) of deadline slips
- **Bottleneck Detection**: Identifies areas likely to become blockers
- **Team Health Monitoring**: Calculates 0-100 health score with letter grade (A-F)
- **7-Day Forecasting**: Projects future team performance and velocity
- **Trend Analysis**: Discovers patterns and anomalies in team behavior

### 📊 **Advanced Analytics**
- Event frequency tracking by source/type
- Response time analysis (avg, p50, p95)
- Action success rate monitoring
- Temporal patterns and busiest periods
- Velocity tracking and completion rates
- Risk score calculation with recommendations

### 👥 **Multi-Team Support**
- Separate event streams per team
- Team-specific analytics and state tracking
- Hierarchical organization structure
- Cross-team comparison capabilities
- Isolated data namespaces

### 🔔 **Webhook System**
- Outbound webhooks for external integrations
- 3 event types: `event.created`, `state.changed`, `action.taken`
- Retry logic with exponential backoff
- Activity logging and monitoring
- Background task processing for async delivery

### 💾 **Production Database**
- SQLAlchemy ORM with PostgreSQL support
- SQLite fallback for local development
- 7 database models (Events, States, Actions, Teams, Webhooks, QA History)
- Automatic schema migrations
- Connection pooling and error handling

---

## 🏗️ Architecture

### Tech Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| **Framework** | FastAPI | 0.121.3 |
| **AI Engine** | IBM watsonx.ai | Granite 3 8B Instruct |
| **Automation** | IBM watsonx Orchestrate | Simulated + Real Slack |
| **Database** | SQLAlchemy + PostgreSQL | 2.0.44 |
| **ORM** | SQLAlchemy | 2.0.44 |
| **Server** | Uvicorn | 0.38.0 |
| **Language** | Python | 3.11+ |
| **Validation** | Pydantic | 2.12.4 |
| **HTTP Client** | httpx | 0.28.1 |

### System Components

```
┌────────────────────────────────────────────────────────────┐
│                  FlowSentinel FastAPI Backend               │
├────────────────────────────────────────────────────────────┤
│                                                              │
│  Event Ingestion ──▶ IBM watsonx.ai ──▶ Action Execution   │
│  (Slack/Jira/Git)    (Granite 3 8B)     (Orchestrate)      │
│         │                   │                    │          │
│         ▼                   ▼                    ▼          │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         PostgreSQL/SQLite Database                    │  │
│  │  Events | States | Actions | Analytics | Webhooks    │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌─────────────┐  │
│  │Analytics │ │ Webhooks │ │  Teams   │ │Intelligence │  │
│  │   (9)    │ │   (7)    │ │   (6)    │ │    (6)      │  │
│  └──────────┘ └──────────┘ └──────────┘ └─────────────┘  │
│                                                              │
└────────────────────────────────────────────────────────────┘
         ▲                                        │
         │ Webhooks                               │ Slack Alerts
         │                                        ▼
┌────────────────┐                      ┌──────────────────┐
│  External      │                      │   Slack          │
│  Services      │                      │   (Real Alerts)  │
└────────────────┘                      └──────────────────┘
```

### API Endpoints: **37 Total**

#### Core Endpoints (9)
- `GET /` - API information and feature status
- `GET /health` - Health check with system metrics
- `POST /events/ingest` - Ingest single event
- `POST /events/ingest/batch` - Ingest multiple events
- `GET /events/list` - List recent events
- `POST /simulation/run` - Load demo data (8 realistic events)
- `POST /agent/run` - Run analysis manually
- `GET /state/latest` - Get current project state
- `POST /qa/ask` - Ask questions about project

#### Autonomous Agent (4)
- `POST /agent/start` - Start background agent
- `POST /agent/stop` - Stop background agent
- `GET /agent/status` - Get agent status & configuration
- `GET /actions/list` - List automated actions taken

#### Analytics (6)
- `GET /analytics/summary` - Overall analytics dashboard
- `GET /analytics/timeline` - Event timeline
- `GET /analytics/risk-score` - Current risk assessment
- `GET /analytics/velocity` - Team velocity metrics
- `GET /analytics/trends` - Trend analysis
- `GET /analytics/health` - System health score

#### Teams (6)
- `POST /teams` - Create team
- `GET /teams` - List all teams
- `GET /teams/{id}` - Get team details
- `PATCH /teams/{id}` - Update team
- `DELETE /teams/{id}` - Delete team
- `GET /teams/{id}/analytics` - Team-specific analytics

#### Webhooks (7)
- `POST /webhooks` - Create webhook
- `GET /webhooks` - List webhooks
- `GET /webhooks/{id}` - Get webhook details
- `PATCH /webhooks/{id}` - Update webhook
- `DELETE /webhooks/{id}` - Delete webhook
- `POST /webhooks/test` - Test webhook URL
- `GET /webhooks/{id}/activity` - View webhook logs

#### Intelligence (6)
- `GET /intelligence/predict-deadline-risk` - Deadline slip probability (0-100%)
- `GET /intelligence/predict-bottlenecks` - Identify future blockers
- `POST /intelligence/recommendations` - AI-powered action suggestions
- `GET /intelligence/team-health` - Team health score (0-100)
- `GET /intelligence/insights` - Pattern discovery and anomaly detection
- `GET /intelligence/forecast` - 7-day performance forecast

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- pip (Python package manager)
- (Optional) Docker & Docker Compose
- (Optional) IBM Cloud account for real watsonx.ai

### 1. Clone & Install

```bash
git clone https://github.com/Nabilhassan12345/flowsentinel.git
cd flowsentinel

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment (Optional)

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your credentials (ALL OPTIONAL for demo)
nano .env
```

**Environment Variables:**
```bash
# IBM watsonx.ai (optional - for real AI)
WATSONX_API_KEY=your_api_key_here
WATSONX_PROJECT_ID=your_project_id
WATSONX_URL=https://us-south.ml.cloud.ibm.com
WATSONX_MODEL_ID=ibm/granite-3-8b-instruct

# Slack (optional - for real notifications)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# Database (optional - defaults to SQLite)
DATABASE_URL=postgresql://user:pass@localhost:5432/flowsentinel

# Autonomous Agent
AGENT_ENABLED=true
AGENT_RUN_INTERVAL=300  # seconds (5 minutes)
```

### 3. Run the Server

```bash
cd src
python main.py
```

**Output:**
```
🚀 FlowSentinel Backend Started
📊 Dashboard: http://localhost:8000/docs
🏥 Health Check: http://localhost:8000/health
💾 Database: SQLite (flowsentinel.db)
🧠 AI: IBM watsonx.ai (Granite 3 8B) - ENABLED
🤖 Autonomous Agent: ENABLED (runs every 300s)
🔔 Slack Alerts: ENABLED
```

### 4. Explore the API

Open your browser to **http://localhost:8000/docs** for the interactive Swagger UI.

### 5. Run Demo Simulation

In another terminal:

```bash
python tests/demo.py
```

**What the demo does:**
1. ✅ Loads 8 realistic events (Slack, Jira, GitHub, Calendar)
2. ✅ Analyzes with IBM watsonx.ai (or rule-based fallback)
3. ✅ Detects blockers and risks
4. ✅ Calculates project health (GREEN/YELLOW/RED)
5. ✅ Triggers automated actions (Slack alerts, task creation, reports)
6. ✅ Answers Q&A queries ("What's blocking us?")
7. ✅ Displays results in terminal

---

## 💡 Usage Examples

### Example 1: Ingest Real Events

```python
import requests

# Ingest Slack message about a blocker
response = requests.post('http://localhost:8000/events/ingest', json={
    "id": "evt_slack_001",
    "source": "slack",
    "type": "message",
    "timestamp": "2025-11-23T15:30:00Z",
    "data": {
        "user": "alice",
        "channel": "#dev",
        "message": "Backend API is blocked waiting on database schema approval"
    }
})
print(response.json())
```

### Example 2: Run Agent Analysis

```python
# Trigger AI-powered analysis
response = requests.post('http://localhost:8000/agent/run')
result = response.json()

print(f"Status: {result['state']['status']}")  # GREEN/YELLOW/RED
print(f"Blockers: {len(result['state']['blockers'])}")
print(f"Actions Triggered: {result['actions_triggered']}")
```

### Example 3: Ask Questions

```python
# Ask about project health
response = requests.post('http://localhost:8000/qa/ask', json={
    "question": "What is blocking the team right now?"
})

qa = response.json()
print(f"Q: {qa['question']}")
print(f"A: {qa['answer']}")
print(f"Reasoning:")
for step in qa['reasoning']:
    print(f"  • {step}")
```

### Example 4: Check Deadline Risk

```python
# Get AI prediction of deadline risk
response = requests.get('http://localhost:8000/intelligence/predict-deadline-risk')
prediction = response.json()

print(f"Risk Level: {prediction['prediction']}")  # HIGH/MODERATE/LOW
print(f"Confidence: {prediction['confidence']:.0%}")
print(f"Risk Score: {prediction['factors']['risk_score']}")
```

### Example 5: Monitor Team Health

```python
# Get team health score (0-100)
response = requests.get('http://localhost:8000/intelligence/team-health')
health = response.json()

print(f"Health Score: {health['health_score']}/100")
print(f"Grade: {health['grade']}")  # A, B, C, D, or F
print(f"Strengths: {health['strengths']}")
print(f"Weaknesses: {health['weaknesses']}")
```

---

## 📊 Data Models

### Event
Represents activity from Slack, Jira, GitHub, or Calendar.

```python
{
  "id": "evt_001",
  "source": "slack",  # slack | jira | github | calendar
  "type": "message",  # message | task_status_changed | pr_opened | meeting_moved
  "timestamp": "2025-11-23T14:10:00Z",
  "data": {
    "user": "PM",
    "channel": "#dev",
    "message": "Backend blocked waiting on design schema"
  },
  "processed": false,
  "team_id": "team_001"  # Optional
}
```

### ProjectState
Current health assessment of the project.

```python
{
  "status": "YELLOW",  # GREEN | YELLOW | RED
  "blockers": [
    {
      "description": "Backend blocked waiting on design schema",
      "source": "slack",
      "timestamp": "2025-11-23T14:10:00Z"
    }
  ],
  "risks": [
    {
      "description": "Design task status: Delayed",
      "impact": "Blocks dependent features",
      "timestamp": "2025-11-23T14:11:00Z"
    }
  ],
  "completed_today": [
    {
      "description": "PR #42 merged: API Integration",
      "timestamp": "2025-11-23T13:00:00Z"
    }
  ],
  "next_deadline": "2025-11-25T17:00:00Z",
  "last_updated": "2025-11-23T14:30:00Z"
}
```

### Action
Automated response taken by the system.

```python
{
  "id": "action_001",
  "type": "notify_user",  # notify_user | create_task | generate_report
  "status": "sent",       # sent | created | completed | failed
  "payload": {
    "message": "🚨 BLOCKER DETECTED: Backend waiting on design",
    "channel": "#alerts"
  },
  "timestamp": "2025-11-23T14:31:00Z"
}
```

---

## 🔧 Configuration

### Environment Variables

All environment variables are **optional** - FlowSentinel works out of the box with sensible defaults and fallback modes.

#### IBM watsonx.ai (Optional)
```bash
WATSONX_API_KEY=your_ibm_api_key
WATSONX_PROJECT_ID=your_project_id
WATSONX_URL=https://us-south.ml.cloud.ibm.com
WATSONX_MODEL_ID=ibm/granite-3-8b-instruct
```

#### Slack Integration (Optional)
```bash
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

#### Database (Optional)
```bash
# PostgreSQL (production)
DATABASE_URL=postgresql://user:pass@localhost:5432/flowsentinel

# SQLite (default, zero config)
# DATABASE_URL=sqlite:///./flowsentinel.db  # auto-created
```

#### Autonomous Agent
```bash
AGENT_ENABLED=true           # Enable/disable autonomous agent
AGENT_RUN_INTERVAL=300       # Run every 5 minutes (300 seconds)
```

#### Application
```bash
APP_HOST=0.0.0.0
APP_PORT=8000
ENVIRONMENT=development      # development | staging | production
LOG_LEVEL=INFO
```

### Database Setup

#### SQLite (Default - Zero Config)
```bash
# Just run the app, database is auto-created
python src/main.py
# Creates: flowsentinel.db in current directory
```

#### PostgreSQL (Production)
```bash
# Option 1: Use Docker Compose (easiest)
docker-compose up postgres

# Option 2: Manual setup
./scripts/setup-postgres.sh

# Option 3: Set DATABASE_URL
export DATABASE_URL=postgresql://user:pass@localhost:5432/flowsentinel
python src/main.py
```

---

## 🐳 Docker Deployment

### Local Development with Docker Compose

```bash
# Start all services (PostgreSQL + FlowSentinel API)
docker-compose up

# Build from scratch
docker-compose build --no-cache

# View logs
docker-compose logs -f flowsentinel-backend

# Stop services
docker-compose down
```

**Access:**
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- PostgreSQL: localhost:5432

### Production Docker Build

```bash
# Build image
docker build -t flowsentinel:latest .

# Run container
docker run -p 8000:8000 \
  -e WATSONX_API_KEY=your_key \
  -e SLACK_WEBHOOK_URL=your_webhook \
  -e DATABASE_URL=postgresql://user:pass@host:5432/db \
  flowsentinel:latest
```

---

## ☁️ Cloud Deployment

### Render.com (Recommended)

FlowSentinel includes a `render.yaml` for one-click deployment:

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. **Deploy on Render**
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New Blueprint"
   - Connect your GitHub repository
   - Render auto-detects `render.yaml`
   - Add environment variables:
     - `WATSONX_API_KEY` (optional)
     - `SLACK_WEBHOOK_URL` (optional)
   - Click "Apply"

3. **Automatic Setup**
   - ✅ PostgreSQL database provisioned
   - ✅ Web service deployed
   - ✅ HTTPS enabled
   - ✅ Auto-scaling configured
   - ✅ Zero-downtime deploys

### Other Platforms

FlowSentinel works on any platform that supports Docker or Python:
- **Heroku**: Use `Dockerfile` and `requirements.txt`
- **Railway**: Connect GitHub repo, auto-deploys
- **AWS ECS**: Use `docker-compose.yml` for ECS Task Definition
- **Google Cloud Run**: Use `Dockerfile`
- **Azure Container Instances**: Use `Dockerfile`

---

## 🧪 Testing

### Run All Tests

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run test suite
pytest

# With coverage report
pytest --cov=src tests/

# Verbose output
pytest -v

# Stop on first failure
pytest -x
```

### Integration Validation

```bash
# Validate all 17 features
python validate_integration.py
```

**What it tests:**
- ✅ Core API endpoints (9)
- ✅ Database integration
- ✅ Agent execution
- ✅ Webhook system (22 tests)
- ✅ Intelligence predictions (10 tests)
- ✅ Analytics tracking
- ✅ Team management

### Manual Testing

```bash
# Terminal 1: Start server
python src/main.py

# Terminal 2: Run demo
python tests/demo.py

# Or use curl
curl -X POST http://localhost:8000/simulation/run
curl -X POST http://localhost:8000/agent/run
curl http://localhost:8000/intelligence/predict-deadline-risk
```

---

## 📊 Monitoring & Observability

### Health Checks

```bash
# Basic health
curl http://localhost:8000/health

# Detailed status
curl http://localhost:8000/

# Agent status
curl http://localhost:8000/agent/status
```

### Analytics Dashboard

```bash
# Summary metrics
curl http://localhost:8000/analytics/summary

# Risk score
curl http://localhost:8000/analytics/risk-score

# Velocity tracking
curl http://localhost:8000/analytics/velocity

# System health
curl http://localhost:8000/analytics/health
```

### Logs

```bash
# Docker logs
docker-compose logs -f flowsentinel-backend

# Follow logs
tail -f /tmp/flowsentinel.log
```

---

## 🏆 IBM watsonx Integration Details

### IBM watsonx.ai (Granite 3 8B)

**State Analysis**
- **Model**: `ibm/granite-3-8b-instruct`
- **Temperature**: 0.1 (deterministic)
- **Max Tokens**: 800
- **Method**: JSON-structured prompts
- **Fallback**: Rule-based analysis if API unavailable

**Q&A System**
- **Model**: `ibm/granite-3-8b-instruct`
- **Temperature**: 0.3 (slightly creative)
- **Max Tokens**: 500
- **Context**: Full project state + recent events
- **Fallback**: Pattern-matching Q&A

**Configuration:**
```python
parameters = {
    GenParams.DECODING_METHOD: "greedy",
    GenParams.MAX_NEW_TOKENS: 800,
    GenParams.TEMPERATURE: 0.1,
    GenParams.TOP_K: 50,
    GenParams.TOP_P: 0.95,
}

model = Model(
    model_id="ibm/granite-3-8b-instruct",
    params=parameters,
    credentials=Credentials(
        api_key=WATSONX_API_KEY,
        url=WATSONX_URL
    ),
    project_id=WATSONX_PROJECT_ID
)
```

### IBM watsonx Orchestrate

**Implemented Skills:**
1. **notify_user** - Slack webhook integration (✅ REAL)
2. **create_task** - Jira task creation (simulated)
3. **generate_report** - Status report generation (simulated)

**Future Skills:**
- GitHub PR reviews and comments
- Calendar meeting scheduling
- Email notifications
- PagerDuty alerts

---

## 📁 Project Structure

```
flowsentinel/
├── src/
│   ├── main.py                      # Main FastAPI app (1,830 lines)
│   ├── database.py                  # Database connection & session
│   ├── models.py                    # SQLAlchemy models (7 models)
│   ├── analytics_endpoints.py       # Analytics API (6 endpoints)
│   ├── team_endpoints.py            # Team management (6 endpoints)
│   ├── webhook_endpoints.py         # Webhook system (7 endpoints)
│   └── intelligence_endpoints.py    # AI predictions (6 endpoints)
├── tests/
│   ├── demo.py                      # Interactive demo script
│   ├── test_api.py                  # API integration tests
│   ├── test_database.py             # Database tests
│   ├── test_analytics.py            # Analytics tests
│   ├── test_webhooks.py             # Webhook tests (12 tests)
│   ├── test_webhook_edge_cases.py   # Edge case tests (10 tests)
│   ├── test_teams.py                # Team tests
│   └── test_intelligence.py         # Intelligence tests (10 tests)
├── scripts/
│   ├── setup-postgres.sh            # PostgreSQL setup script
│   ├── quick-push.sh                # Git deployment helper
│   └── test-all.sh                  # Comprehensive testing
├── docs/
│   ├── ANALYTICS.md                 # Analytics documentation
│   ├── INTELLIGENCE.md              # Intelligence features guide
│   ├── DOCKER.md                    # Docker deployment guide
│   ├── CI-CD.md                     # CI/CD setup
│   └── DATABASE.md                  # Database schema docs
├── .github/workflows/
│   └── test.yml                     # GitHub Actions CI
├── docker-compose.yml               # Local development stack
├── Dockerfile                       # Production container
├── render.yaml                      # Cloud deployment config
├── requirements.txt                 # Production dependencies
├── requirements-dev.txt             # Development dependencies
├── .env.example                     # Environment template
├── validate_integration.py          # Integration validator (17 tests)
├── INTEGRATION_COMPLETE.md          # Integration report
├── QUICK_REFERENCE.md               # Quick start guide
└── README.md                        # This file
```

**Statistics:**
- **Total Lines of Code**: ~8,000+
- **API Endpoints**: 37
- **Database Models**: 7
- **Test Files**: 8
- **Test Cases**: 32+
- **Documentation Files**: 15+

---

## 🔒 Security Considerations

### Production Checklist

- ✅ Never commit `.env` file (in `.gitignore`)
- ✅ Use environment variables for secrets
- ✅ Enable HTTPS in production (Render handles this)
- ✅ Set `ENVIRONMENT=production` for optimizations
- ✅ Use PostgreSQL instead of SQLite in production
- ✅ Configure CORS allowed origins
- ✅ Run as non-root user in Docker
- ✅ Regular dependency updates (`pip-audit`)
- ⬜ Enable rate limiting (future)
- ⬜ Add API authentication (future)

### Security Best Practices

```python
# In production, set these:
ENVIRONMENT=production
DATABASE_URL=postgresql://...  # Not SQLite
CORS_ORIGINS=https://yourdomain.com  # Not *

# Future enhancements:
RATE_LIMIT_PER_MINUTE=60
SECRET_KEY=your_secret_key_min_32_chars
```

---

## 🚧 Roadmap

### Phase 1: MVP ✅ (Complete)
- [x] Event ingestion from 4 sources
- [x] IBM watsonx.ai integration (Granite 3 8B)
- [x] IBM watsonx Orchestrate simulation
- [x] Real Slack notifications
- [x] Project state tracking (GREEN/YELLOW/RED)
- [x] Q&A system
- [x] Autonomous agent

### Phase 2: Production ✅ (Complete)
- [x] PostgreSQL database
- [x] Advanced analytics (6 endpoints)
- [x] Multi-team support (6 endpoints)
- [x] Webhook system (7 endpoints)
- [x] Predictive intelligence (6 endpoints)
- [x] Docker deployment
- [x] Cloud deployment (Render.com)
- [x] 37 API endpoints total
- [x] 32+ test cases

### Phase 3: Enterprise (Future)
- [ ] Real Jira API integration
- [ ] Real GitHub API integration
- [ ] Real Google Calendar integration
- [ ] IBM watsonx Orchestrate real skills
- [ ] SSO/SAML authentication
- [ ] Advanced ML models (beyond Granite)
- [ ] Custom analytics dashboards
- [ ] Mobile app
- [ ] Slack bot integration
- [ ] Microsoft Teams integration

---

## 🤝 Contributing

We welcome contributions! Here's how to get started:

### 1. Fork the Repository

```bash
git clone https://github.com/YOUR_USERNAME/flowsentinel.git
cd flowsentinel
```

### 2. Create a Branch

```bash
git checkout -b feature/amazing-feature
```

### 3. Install Development Dependencies

```bash
pip install -r requirements-dev.txt
```

### 4. Make Changes

```bash
# Run tests before committing
pytest

# Format code
black src/ tests/

# Lint code
flake8 src/ tests/
```

### 5. Commit and Push

```bash
git commit -m 'Add amazing feature'
git push origin feature/amazing-feature
```

### 6. Open Pull Request

Go to GitHub and open a Pull Request with a clear description of your changes.

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **IBM watsonx.ai** - For the incredible Granite 3 8B Instruct model
- **IBM watsonx Orchestrate** - For automation capabilities
- **FastAPI** - For the modern, fast web framework
- **SQLAlchemy** - For robust database ORM
- **Pydantic** - For data validation
- **Render.com** - For simple cloud deployment
- **Python Community** - For excellent libraries and tools

---

## 📞 Support & Contact

### Documentation
- **Quick Reference**: [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
- **Deployment Guide**: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- **Intelligence Features**: [INTELLIGENCE.md](INTELLIGENCE.md)
- **Analytics Guide**: [docs/ANALYTICS.md](docs/ANALYTICS.md)
- **Integration Report**: [INTEGRATION_COMPLETE.md](INTEGRATION_COMPLETE.md)

### Community
- **Issues**: [GitHub Issues](https://github.com/Nabilhassan12345/flowsentinel/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Nabilhassan12345/flowsentinel/discussions)

### IBM watsonx Resources
- [watsonx.ai Documentation](https://www.ibm.com/docs/en/watsonx-as-a-service)
- [Granite Models Overview](https://www.ibm.com/granite)
- [watsonx Orchestrate Guide](https://www.ibm.com/watsonx/orchestrate)

---

## 🎓 Learn More

### Technology Stack Tutorials
- [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/)
- [Pydantic Validation](https://docs.pydantic.dev/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)

### Related Projects
- [IBM watsonx.ai Python SDK](https://ibm.github.io/watsonx-ai-python-sdk/)
- [FastAPI Best Practices](https://github.com/zhanymkanov/fastapi-best-practices)

---

<div align="center">

**Built with ❤️ for the IBM watsonx Challenge**

*FlowSentinel - Your autonomous AI teammate that never sleeps* 🚀

**Version**: 2.0.0 | **Status**: Production Ready ✅ | **Last Updated**: November 2025

[Report Bug](https://github.com/Nabilhassan12345/flowsentinel/issues) · [Request Feature](https://github.com/Nabilhassan12345/flowsentinel/issues) · [View Demo](https://github.com/Nabilhassan12345/flowsentinel)

</div>

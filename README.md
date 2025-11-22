# 🧠 FlowSentinel - Agentic Company Brain

> An intelligent workflow monitoring system that acts as your team's digital brain, ingesting events from Slack, Jira, GitHub, and Calendar to detect risks, identify blockers, and automate responses using IBM watsonx.ai and watsonx Orchestrate.

[![Tests](https://github.com/YOUR_USERNAME/flowsentinel/workflows/Tests/badge.svg)](https://github.com/YOUR_USERNAME/flowsentinel/actions)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 📖 Overview

FlowSentinel is an agentic AI system that continuously monitors your team's workflow across multiple platforms. It doesn't just collect data—it **understands context**, **detects problems**, and **takes action automatically**.

### What Makes It Special?

- 🤖 **Agentic AI**: Autonomous decision-making based on project state
- 🔍 **Cross-Platform Intelligence**: Connects dots across Slack, Jira, GitHub, Calendar
- 🚨 **Proactive Alerts**: Detects blockers before they become critical
- 💬 **Natural Language Q&A**: Ask about your project in plain English
- ⚡ **Automated Actions**: Auto-notifies, creates tasks, generates reports

---

## ✨ Features

### Core Capabilities
- ✅ **Multi-Source Event Ingestion** - Real-time data from Slack, Jira, GitHub, Calendar
- ✅ **AI-Powered Analysis** - IBM watsonx.ai for intelligent state understanding
- ✅ **Smart Blocker Detection** - Scans messages for keywords like "blocked", "stuck", "waiting"
- ✅ **Risk Assessment** - Identifies deadline changes and delayed tasks
- ✅ **Automated Actions** - IBM watsonx Orchestrate skills (notify, create tasks, reports)
- ✅ **Natural Language Q&A** - Ask questions, get intelligent answers with reasoning
- ✅ **Health Status Monitoring** - 🟢 GREEN / 🟡 YELLOW / 🔴 RED indicators
- ✅ **Real Slack Integration** - Actual webhook notifications (optional)
- ✅ **RESTful API** - Clean, documented endpoints with FastAPI
- ✅ **Interactive Docs** - Auto-generated Swagger UI

---

## �️ Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Framework** | FastAPI 0.104.1 | High-performance async web framework |
| **Server** | Uvicorn | ASGI server with hot reload |
| **Validation** | Pydantic v2 | Type-safe data models |
| **AI Engine** | IBM watsonx.ai | Event analysis & state generation (simulated) |
| **Automation** | IBM watsonx Orchestrate | Action execution (simulated) |
| **HTTP Client** | httpx + requests | Async/sync HTTP requests |
| **Storage** | In-Memory (MVP) | Lists/dicts (ready for PostgreSQL) |
| **Config** | python-dotenv | Environment variable management |
| **Date Handling** | python-dateutil | Advanced datetime operations |

---

## �🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Terminal/Command line access

### Installation

**Option 1: Using setup script (Recommended)**
```bash
# Navigate to project directory
cd flowsentinel

# Run automated setup
chmod +x setup.sh
./setup.sh

# Activate virtual environment
source venv/bin/activate
```

**Option 2: Manual setup**
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env
```

### Running the Server

```bash
# Start the FastAPI server
python main.py
```

You should see:
```
🚀 FlowSentinel Backend Started
📊 Dashboard: http://localhost:8000/docs
🧠 Watsonx.ai Integration: Ready
🤖 Orchestrate Bridge: Ready
```

**Access Points:**
- 🌐 API Server: http://localhost:8000
- 📚 Interactive Docs: http://localhost:8000/docs
- 📖 ReDoc: http://localhost:8000/redoc

### Testing Endpoints

**Option 1: Using the demo script (Recommended)**
```bash
# In a new terminal (keep server running)
python demo.py
```

**Option 2: Using the comprehensive test suite**
```bash
python test_api.py
```

**Option 3: Manual curl commands**
```bash
# Load simulation data
curl -X POST http://localhost:8000/simulation/run

# Run agent analysis
curl -X POST http://localhost:8000/agent/run

# Check project status
curl http://localhost:8000/state/latest

# Ask a question
curl -X POST http://localhost:8000/qa/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Is the project at risk?"}'
```

---

## 📡 API Endpoints

### Health & Info
```
GET  /           # API information
GET  /health     # Health check with metrics
```

### Event Management
```
POST /events/ingest        # Ingest single event
POST /events/ingest/batch  # Ingest multiple events
GET  /events/list          # List recent events (supports ?limit=N)
POST /simulation/run       # Load 8 demo events
```

### Agent Operations
```
POST /agent/run      # Run AI analysis + trigger actions
GET  /state/latest   # Get current project state
GET  /actions/list   # List executed actions (supports ?limit=N)
```

### Q&A
```
POST /qa/ask         # Ask natural language questions
```

**Full API Documentation:** Visit http://localhost:8000/docs when server is running

---

## 🔐 Environment Variables

Copy `.env.example` to `.env` and configure:

### Required for Production
```bash
# IBM watsonx.ai (for real AI analysis)
WATSONX_API_KEY=your_api_key_here
WATSONX_PROJECT_ID=your_project_id
WATSONX_URL=https://us-south.ml.cloud.ibm.com

# IBM watsonx Orchestrate (for real automation)
ORCHESTRATE_API_KEY=your_api_key_here
ORCHESTRATE_INSTANCE_ID=your_instance_id
ORCHESTRATE_URL=https://your-instance.watsonx-orchestrate.ibm.com
```

### Optional (Enhances Features)
```bash
# Slack Integration (enables real notifications)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# GitHub Integration (for future features)
GITHUB_TOKEN=ghp_your_token_here
GITHUB_REPO_OWNER=your-username
GITHUB_REPO_NAME=your-repo

# Application Settings
APP_PORT=8000
LOG_LEVEL=INFO
```

**Note:** For MVP/demo, NO environment variables are required! System works with simulation mode.

---

## 📁 Project Structure

```
flowsentinel/
├── main.py              # Main FastAPI application (650+ lines)
│   ├── Database         # In-memory storage class
│   ├── WatsonxAgent     # AI analysis engine
│   ├── OrchestrateBridge # Action execution
│   └── API Endpoints    # 11 REST endpoints
├── demo.py              # Interactive demo script
├── test_api.py          # Comprehensive test suite
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variable template
├── .gitignore           # Git ignore rules
├── setup.sh             # Automated setup script
└── README.md            # This file
```

### Key Components

**`Database` Class**
- In-memory storage for events, state, actions
- Easy to swap for PostgreSQL later

**`WatsonxAgent` Class**
- Analyzes events to detect blockers/risks
- Calculates project health status
- Answers natural language questions

**`OrchestrateBridge` Class**
- Executes automated skills
- Real Slack webhook integration
- Simulated task creation & reports

---

## 🎮 Demo Instructions

### Full Demo Sequence

1. **Start the server:**
   ```bash
   python main.py
   ```

2. **Run the demo script** (in a new terminal):
   ```bash
   python demo.py
   ```

3. **What you'll see:**
   - ✅ Health check
   - 📥 8 events loaded (Slack messages, Jira updates, GitHub PRs)
   - 🤖 Agent analysis detecting 1 blocker + 2 risks
   - 🚦 Status: YELLOW (warning level)
   - 📬 Slack notification sent (if webhook configured)
   - 📋 Escalation task created
   - 💬 Q&A with 3 sample questions
   - 📊 Summary of all actions taken

### Understanding the Simulation

The demo creates a realistic scenario:
- **Blocker:** "Backend is blocked waiting on design schema"
- **Risk 1:** Landing Page Schema delayed
- **Risk 2:** API Integration deadline changed
- **Result:** Project status = YELLOW (1 blocker + 2 risks)

---

## � Development Tips

### Running in Development Mode

```bash
# Auto-reload on file changes (default in main.py)
python main.py

# Manual reload with uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Testing Individual Endpoints

```bash
# Test health
curl http://localhost:8000/health

# Test with pretty output
curl http://localhost:8000/state/latest | python -m json.tool
```

### Adding New Event Sources

1. Add event type to `Event.source` enum in `main.py`
2. Update `WatsonxAgent.analyze_state()` to process new events
3. Add sample events to `/simulation/run` endpoint

### Customizing Analysis Logic

Edit `WatsonxAgent.analyze_state()` in `main.py`:
- Modify blocker keywords (line ~250)
- Adjust risk detection logic (line ~260)
- Change status calculation thresholds (line ~295)

---

## 🔧 Troubleshooting

### Server Won't Start

**Problem:** `Address already in use`
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>
```

**Problem:** `ModuleNotFoundError`
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Agent Returns 400 Error

**Problem:** `No events to analyze`
```bash
# Solution: Load simulation data first
curl -X POST http://localhost:8000/simulation/run
curl -X POST http://localhost:8000/agent/run
```

### Slack Notifications Not Working

**Problem:** No webhook configured
```bash
# Check console for message like:
# "ℹ️ Slack webhook not configured"

# Solution: Add webhook to .env
echo "SLACK_WEBHOOK_URL=https://hooks.slack.com/..." >> .env

# Restart server
```

### Tests Failing

**Problem:** Server not running
```bash
# Start server first
python main.py

# Then run tests in new terminal
python test_api.py
```

---

## 🎓 How It Works

### Analysis Algorithm

1. **Event Collection:** Gather last 20 events from database
2. **Blocker Detection:** Scan Slack messages for keywords:
   - "blocked", "waiting", "stuck", "can't proceed", "need", "missing"
3. **Risk Identification:** Find Jira deadline changes and delays
4. **Completion Tracking:** Identify merged PRs and completed tasks
5. **Status Calculation:**
   - 🔴 **RED:** 2+ blockers OR 2+ risks
   - 🟡 **YELLOW:** 1+ blockers OR 1+ risks
   - 🟢 **GREEN:** No blockers or risks
6. **Action Triggers:**
   - If blockers exist → Send Slack notification
   - If status is RED → Create escalation task
   - Always → Generate status report

### Q&A System

The natural language Q&A uses pattern matching to understand questions:
- Keywords: "risk", "blocker", "status"
- Context: Recent events + current state
- Output: Multi-sentence answer + reasoning steps

---

## 🔮 Future Enhancements

### Near Term
- [ ] PostgreSQL database integration
- [ ] WebSocket support for real-time updates
- [ ] User authentication & authorization
- [ ] Multi-project/tenant support

### Medium Term
- [ ] Real IBM watsonx.ai API integration
- [ ] Real IBM watsonx Orchestrate integration
- [ ] Advanced analytics dashboard
- [ ] Custom action workflow builder

### Long Term
- [ ] Machine learning for predictive risk analysis
- [ ] Sentiment analysis on team communications
- [ ] Auto-generated status reports (PDF/email)
- [ ] Mobile app for notifications
- [ ] Integration with MS Teams, Discord, etc.

---

## � Data Models

### Event Schema
```python
{
  "id": "evt_001",
  "source": "slack" | "jira" | "github" | "calendar",
  "type": "message" | "task_status_changed" | "pr_opened" | ...,
  "timestamp": "2024-03-20T14:10:00Z",
  "data": { /* flexible payload */ },
  "processed": false
}
```

### ProjectState Schema
```python
{
  "status": "GREEN" | "YELLOW" | "RED",
  "blockers": [{"description": "...", "source": "...", "timestamp": "..."}],
  "risks": [{"description": "...", "impact": "...", "timestamp": "..."}],
  "completed_today": [{"description": "...", "timestamp": "..."}],
  "next_deadline": "2024-03-25T17:00:00Z",
  "last_updated": "2024-03-20T15:00:00Z"
}
```

---

## 📄 License

MIT License

Copyright (c) 2024 FlowSentinel

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

---

## 🤝 Contributing

This project was built for a hackathon but welcomes contributions!

**To contribute:**
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## � Acknowledgments

- **IBM watsonx.ai** - For inspiration on agentic AI systems
- **IBM watsonx Orchestrate** - For digital labor automation concepts
- **FastAPI** - For making Python APIs a joy to build
- **The Open Source Community** - For amazing tools and libraries

---

## 📞 Support

- 📧 Report issues on GitHub Issues
- 💬 Questions? Check out the `/docs` endpoint when running
- 🌟 Star this repo if you find it helpful!

---

**Built with ❤️ using FastAPI, IBM watsonx.ai, and IBM watsonx Orchestrate**

*Last updated: November 2024*

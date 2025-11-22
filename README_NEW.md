# 🧠 FlowSentinel

> **Agentic AI Company Brain for Workflow Monitoring**  
> Automatically detects blockers, identifies risks, and takes action across Slack, Jira, GitHub, and Calendar.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/Nabilhassan12345/flowsentinel/workflows/Tests/badge.svg)](https://github.com/Nabilhassan12345/flowsentinel/actions)

---

## ⚡ Quick Start (60 Seconds)

```bash
# 1. Clone
git clone https://github.com/Nabilhassan12345/flowsentinel.git
cd flowsentinel

# 2. Setup
./scripts/setup.sh

# 3. Run
./scripts/start.sh
```

**🎉 Done!** Open http://localhost:8000/docs

📖 **Detailed Guide:** [GETTING_STARTED.md](GETTING_STARTED.md)

---

## 🎯 What Is This?

FlowSentinel is an **intelligent AI agent** that monitors your team's workflow and automatically takes action.

### The Problem
- Teams use Slack + Jira + GitHub + Calendar
- Important information gets lost
- Blockers go unnoticed
- Deadlines slip

### The Solution
Flow Sentinel:
1. **📥 Ingests** events from all platforms
2. **🤖 Analyzes** using IBM watsonx.ai
3. **🚨 Detects** blockers and risks automatically
4. **⚡ Acts** via IBM watsonx Orchestrate (Slack alerts, creates tasks)
5. **💬 Answers** questions in natural language

---

## ✨ Features

### Core Capabilities
- ✅ **Multi-Source Event Ingestion** - Slack, Jira, GitHub, Calendar
- ✅ **AI-Powered Analysis** - IBM watsonx.ai for intelligent understanding
- ✅ **Smart Blocker Detection** - Scans for "blocked", "stuck", "waiting"
- ✅ **Risk Assessment** - Identifies deadline changes and delays
- ✅ **Automated Actions** - Slack notifications, task creation, reports
- ✅ **Natural Language Q&A** - Ask questions, get intelligent answers
- ✅ **Health Monitoring** - 🟢 GREEN / 🟡 YELLOW / 🔴 RED status
- ✅ **RESTful API** - 11 documented endpoints
- ✅ **Interactive Docs** - Auto-generated Swagger UI

### Technical Highlights
- 🐍 **Python 3.11** with FastAPI
- 🔄 **Async/Await** for performance
- ✅ **Type Safety** with Pydantic v2
- 🐳 **Docker Ready** with compose
- ⚙️ **CI/CD Pipeline** via GitHub Actions
- 📊 **Comprehensive Tests** with colored output
- 📚 **Complete Documentation** (1000+ lines)

---

## 📁 Project Structure

```
flowsentinel/
├── src/                      # 📦 Source Code
│   └── main.py              # Main application (933 lines)
│
├── tests/                    # 🧪 Testing
│   ├── test_api.py          # Test suite
│   └── demo.py              # Interactive demo
│
├── scripts/                  # 🔧 Automation
│   ├── setup.sh             # Project setup
│   ├── start.sh             # Server start
│   └── quick-push.sh        # GitHub push
│
├── docs/                     # 📚 Documentation
│   ├── CI-CD.md             # CI/CD guide
│   └── DOCKER.md            # Docker guide
│
├── .github/workflows/        # ⚙️ CI/CD
│   └── test.yml             # GitHub Actions
│
├── 📄 README.md              # This file
├── 📄 GETTING_STARTED.md     # Beginner guide
├── 📄 STRUCTURE.md           # Structure explained
├── 📄 DOCS.md                # Documentation index
│
├── 🐳 Dockerfile             # Container image
├── 🐳 docker-compose.yml     # Orchestration
│
├── 📦 requirements.txt       # Dependencies
└── 🔐 .env.example           # Config template
```

**Detailed breakdown:** [STRUCTURE.md](STRUCTURE.md)

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| **[GETTING_STARTED.md](GETTING_STARTED.md)** | Complete setup guide (start here!) |
| **[STRUCTURE.md](STRUCTURE.md)** | Project organization explained |
| **[DOCS.md](DOCS.md)** | Documentation index |
| **[docs/DOCKER.md](docs/DOCKER.md)** | Docker deployment guide |
| **[docs/CI-CD.md](docs/CI-CD.md)** | Continuous integration setup |

---

## 🔌 API Endpoints

### Health & Info
- `GET /` - API information
- `GET /health` - Health check with metrics

### Event Management
- `POST /events/ingest` - Ingest single event
- `POST /events/ingest/batch` - Ingest multiple events
- `GET /events/list` - List recent events
- `POST /simulation/run` - Load demo data

### Agent Operations
- `POST /agent/run` - Run AI analysis + trigger actions
- `GET /state/latest` - Get current project state
- `GET /actions/list` - List executed actions

### Q&A
- `POST /qa/ask` - Ask natural language questions

**Interactive documentation:** http://localhost:8000/docs

---

## 🧪 Testing

```bash
# Comprehensive test suite
python tests/test_api.py

# Interactive demonstration
python tests/demo.py

# Manual health check
curl http://localhost:8000/health
```

---

## 🐳 Docker Deployment

```bash
# Build and run
docker-compose up --build

# Run in background
docker-compose up -d

# Stop
docker-compose down
```

**Full guide:** [docs/DOCKER.md](docs/DOCKER.md)

---

## 🔐 Configuration

Edit `.env` file for real integrations:

```bash
# Slack notifications (optional but recommended)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK

# IBM watsonx.ai (optional - uses simulation by default)
WATSONX_API_KEY=your_api_key
WATSONX_PROJECT_ID=your_project_id

# See .env.example for all options
```

**Get Slack webhook:** https://api.slack.com/messaging/webhooks

---

## 🎯 Use Cases

- **Software Teams** - Monitor sprints, detect blockers
- **Project Management** - Track deadlines, identify risks  
- **DevOps** - Monitor deployments, catch failures
- **Customer Support** - Track tickets, identify bottlenecks
- **Any Multi-Tool Team** - Centralize workflow data

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| **Framework** | FastAPI 0.104.1 |
| **Server** | Uvicorn (ASGI) |
| **Validation** | Pydantic v2 |
| **AI Engine** | IBM watsonx.ai |
| **Automation** | IBM watsonx Orchestrate |
| **HTTP** | httpx + requests |
| **Storage** | In-memory (PostgreSQL-ready) |
| **Container** | Docker + Compose |
| **CI/CD** | GitHub Actions |

---

## 📊 Project Stats

- **Total Lines**: ~3,650
- **Main App**: 933 lines
- **Tests**: 800 lines
- **Docs**: 1,000+ lines
- **Files**: 20+ organized files
- **API Endpoints**: 11 REST endpoints
- **Test Coverage**: 10+ test functions

---

## 🚀 What's Next?

### For Users
1. ✅ Setup and run (see [GETTING_STARTED.md](GETTING_STARTED.md))
2. 🔑 Add Slack webhook for real notifications
3. 🧪 Experiment with demo.py
4. 📖 Explore /docs endpoint

### For Developers
1. 📝 Read [STRUCTURE.md](STRUCTURE.md)
2. 🔍 Explore `src/main.py`
3. 🧪 Run tests with `tests/test_api.py`
4. 🛠️ Customize analysis logic
5. 🎨 Build frontend dashboard

### For Production
1. 🔐 Get IBM watsonx.ai API keys
2. 🐳 Deploy with Docker (see [docs/DOCKER.md](docs/DOCKER.md))
3. ⚙️ Setup CI/CD (see [docs/CI-CD.md](docs/CI-CD.md))
4. 📊 Add PostgreSQL database
5. 🔒 Implement authentication

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

## 📄 License

MIT License - See [LICENSE](LICENSE) file

---

## 🙏 Acknowledgments

- **IBM watsonx.ai** - AI/ML platform
- **IBM watsonx Orchestrate** - Workflow automation
- **FastAPI** - Modern Python web framework
- **Open Source Community** - Amazing tools and libraries

---

## 📞 Support

- 📧 **Issues**: [GitHub Issues](https://github.com/Nabilhassan12345/flowsentinel/issues)
- 📚 **Documentation**: [DOCS.md](DOCS.md)
- 💬 **Questions**: Check `/docs` endpoint
- 🌟 **Star** this repo if helpful!

---

<div align="center">

**Built with ❤️ using FastAPI, IBM watsonx.ai, and IBM watsonx Orchestrate**

**[Get Started](GETTING_STARTED.md)** • **[Documentation](DOCS.md)** • **[Structure](STRUCTURE.md)**

</div>

---

*Last updated: November 22, 2025*

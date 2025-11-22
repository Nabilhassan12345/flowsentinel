# 🧠 FlowSentinel - Agentic Company Brain# 🧠 FlowSentinel# 🧠 FlowSentinel - Agentic Company Brain



> **An intelligent workflow monitoring system that acts as your team's digital brain**  

> Ingests events from Slack, Jira, GitHub, and Calendar—detects risks, identifies blockers, and automates responses using IBM watsonx.ai and watsonx Orchestrate.

> **Agentic AI Company Brain for Workflow Monitoring**  > An intelligent workflow monitoring system that acts as your team's digital brain, ingesting events from Slack, Jira, GitHub, and Calendar to detect risks, identify blockers, and automate responses using IBM watsonx.ai and watsonx Orchestrate.

[![Tests](https://github.com/Nabilhassan12345/flowsentinel/workflows/Tests/badge.svg)](https://github.com/Nabilhassan12345/flowsentinel/actions)

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)> An intelligent system that ingests events from Slack, Jira, GitHub, and Calendar—detects risks, identifies blockers, and automates responses using IBM watsonx.ai and watsonx Orchestrate.

[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688.svg)](https://fastapi.tiangolo.com/)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)[![Tests](https://github.com/YOUR_USERNAME/flowsentinel/workflows/Tests/badge.svg)](https://github.com/YOUR_USERNAME/flowsentinel/actions)



---[![Tests](https://github.com/Nabilhassan12345/flowsentinel/workflows/Tests/badge.svg)](https://github.com/Nabilhassan12345/flowsentinel/actions)[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)



## ✨ What It Does[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688.svg)](https://fastapi.tiangolo.com/)



FlowSentinel is an **agentic AI backend** that monitors team workflows and takes automated actions:[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688.svg)](https://fastapi.tiangolo.com/)[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)



- **📥 Multi-Source Event Ingestion** — Collects data from Slack, Jira, GitHub, Calendar[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

- **🤖 AI-Powered Analysis** — Detects blockers ("blocked", "stuck", "waiting") and deadline risks

- **🚨 Smart Alerts** — Automatically sends Slack notifications for critical issues---

- **📊 Automated Actions** — Creates tasks, generates reports, escalates via Orchestrate

- **💬 Natural Language Q&A** — Ask "Is the project at risk?" and get intelligent answers---

- **🚦 Health Monitoring** — 🟢 GREEN / 🟡 YELLOW / 🔴 RED status indicators

## 🎯 **What We Built**

---

## ✨ What It Does

## 🏗️ Architecture

This is a **fully functional agentic AI backend** that monitors team workflows across multiple platforms and takes automated actions. Think of it as an AI-powered project manager that never sleeps.

```

flowsentinel/FlowSentinel is an **agentic AI backend** that acts as your team's digital brain:

├── src/

│   └── main.py              # Core FastAPI application (933 lines)### **The Problem We Solved:**

├── tests/

│   ├── test_api.py          # Comprehensive API tests- **📥 Multi-Source Event Ingestion** — Collects data from Slack messages, Jira updates, GitHub PRs, calendar changesTeams use multiple tools (Slack, Jira, GitHub, Calendar) and important information gets lost. Blockers go unnoticed, deadlines slip, and communication breaks down. We built FlowSentinel to solve this.

│   └── demo.py              # Interactive demonstration

├── docs/- **🤖 AI-Powered Analysis** — Uses IBM watsonx.ai to understand project state, detect blockers ("blocked", "stuck", "waiting"), identify deadline risks

│   ├── DOCKER.md            # Docker deployment guide

│   └── CI-CD.md             # GitHub Actions setup- **🚨 Smart Alerts** — Automatically sends Slack notifications when critical issues surface### **What It Does:**

├── scripts/

│   ├── start.sh             # Quick server start- **📊 Automated Actions** — Creates tasks, generates reports, escalates via IBM watsonx Orchestrate1. **📥 Ingests Events** - Collects data from Slack messages, Jira updates, GitHub PRs, and calendar changes

│   ├── setup.sh             # Environment setup

│   └── git-setup.sh         # Git initialization- **💬 Natural Language Q&A** — Ask "Is the project at risk?" and get intelligent answers with reasoning steps2. **🤖 AI Analysis** - Uses IBM watsonx.ai to understand project state, detect blockers, and identify risks

├── .github/

│   └── workflows/- **🚦 Real-Time Health Monitoring** — 🟢 GREEN / 🟡 YELLOW / 🔴 RED status indicators3. **🚨 Smart Alerts** - Automatically sends Slack notifications when critical issues are detected

│       └── test.yml         # CI/CD pipeline

├── requirements.txt         # Production dependencies4. **📊 Auto-Actions** - Creates tasks, generates reports, and escalates issues via IBM watsonx Orchestrate

├── requirements-dev.txt     # Development tools

├── docker-compose.yml       # Container orchestration---5. **💬 Q&A System** - Ask natural language questions like "Is the project at risk?" and get intelligent answers

└── Dockerfile               # Multi-stage build

```



---## 🏗️ Architecture### **Technical Highlights:**



## 🚀 Quick Start- ✅ **11 REST API Endpoints** - Complete CRUD operations for events, state, actions, and Q&A



### Prerequisites```- ✅ **Real-time Health Monitoring** - 🟢 GREEN / 🟡 YELLOW / 🔴 RED status indicators



- Python 3.11+┌─────────────────────────────────────────────────────────────────┐- ✅ **Intelligent Blocker Detection** - Scans messages for keywords like "blocked", "stuck", "waiting"

- pip

│                      FlowSentinel System                        │- ✅ **Risk Assessment Engine** - Identifies deadline changes and delayed tasks

### Installation

├─────────────────────────────────────────────────────────────────┤- ✅ **Natural Language Processing** - Context-aware Q&A with reasoning steps

```bash

# Clone repository│                                                                 │- ✅ **Slack Integration** - Real webhook notifications (optional)

git clone https://github.com/Nabilhassan12345/flowsentinel.git

cd flowsentinel│  📥 Event Ingestion                                            │- ✅ **Docker Ready** - Complete containerization with docker-compose



# Quick setup (automated)│     Slack │ Jira │ GitHub │ Calendar                           │- ✅ **CI/CD Pipeline** - GitHub Actions for automated testing

chmod +x scripts/setup.sh

./scripts/setup.sh│                    ↓                                            │- ✅ **Production-Ready** - Proper error handling, logging, health checks



# Or manual setup│  🔄 FastAPI REST API (11 Endpoints)                            │

python3 -m venv venv

source venv/bin/activate│                    ↓                                            │---

pip install -r requirements.txt

```│  💾 In-Memory Database (MVP)                                   │



### Run the Server│     Events │ State │ Actions │ Q&A History                     │## 📖 Overview



```bash│                    ↓                                            │

# Quick start

./scripts/start.sh│  🧠 WatsonxAgent (AI Analysis Engine)                          │FlowSentinel is an agentic AI system that continuously monitors your team's workflow across multiple platforms. It doesn't just collect data—it **understands context**, **detects problems**, and **takes action automatically**.



# Or manual│     • Blocker Detection (keyword scan)                         │

python src/main.py

```│     • Risk Assessment (deadline changes)                       │### What Makes It Special?



Server will start at: **http://localhost:8000**  │     • Status Calculation (RED/YELLOW/GREEN)                    │

Interactive docs: **http://localhost:8000/docs**

│     • Natural Language Q&A                                     │- 🤖 **Agentic AI**: Autonomous decision-making based on project state

### Test the API

│                    ↓                                            │- 🔍 **Cross-Platform Intelligence**: Connects dots across Slack, Jira, GitHub, Calendar

```bash

# In a new terminal│  ⚡ OrchestrateBridge (Automated Actions)                      │- 🚨 **Proactive Alerts**: Detects blockers before they become critical

python tests/test_api.py

│     • Slack Notifications (real webhook)                       │- 💬 **Natural Language Q&A**: Ask about your project in plain English

# Or run the demo

python tests/demo.py│     • Task Creation (simulated Jira)                           │- ⚡ **Automated Actions**: Auto-notifies, creates tasks, generates reports

```

│     • Report Generation                                        │

---

│                                                                 │---

## 📡 API Endpoints

└─────────────────────────────────────────────────────────────────┘

### Core Endpoints

- `GET /` - API information```## ✨ Features

- `GET /health` - Health check with metrics



### Event Management

- `POST /events/ingest` - Ingest single event---### Core Capabilities

- `POST /events/ingest/batch` - Ingest multiple events

- `GET /events/list` - List recent events- ✅ **Multi-Source Event Ingestion** - Real-time data from Slack, Jira, GitHub, Calendar

- `POST /simulation/run` - Load demo data (8 realistic events)

## 🚀 Quick Start- ✅ **AI-Powered Analysis** - IBM watsonx.ai for intelligent state understanding

### Agent Operations

- `POST /agent/run` - Run AI analysis + trigger actions- ✅ **Smart Blocker Detection** - Scans messages for keywords like "blocked", "stuck", "waiting"

- `GET /state/latest` - Get current project state

- `GET /actions/list` - List executed actions### Prerequisites- ✅ **Risk Assessment** - Identifies deadline changes and delayed tasks



### Q&A- ✅ **Automated Actions** - IBM watsonx Orchestrate skills (notify, create tasks, reports)

- `POST /qa/ask` - Ask natural language questions

- Python 3.11+- ✅ **Natural Language Q&A** - Ask questions, get intelligent answers with reasoning

**Full API Documentation:** Visit http://localhost:8000/docs when server is running

- pip- ✅ **Health Status Monitoring** - 🟢 GREEN / 🟡 YELLOW / 🔴 RED indicators

---

- (Optional) Docker for containerized deployment- ✅ **Real Slack Integration** - Actual webhook notifications (optional)

## 🐳 Docker Deployment

- ✅ **RESTful API** - Clean, documented endpoints with FastAPI

### Using Docker Compose (Recommended)

### 1. Clone & Setup- ✅ **Interactive Docs** - Auto-generated Swagger UI

```bash

# Build and run

docker-compose up --build

```bash---

# Run in background

docker-compose up -d# Clone repository



# View logsgit clone https://github.com/Nabilhassan12345/flowsentinel.git## �️ Tech Stack

docker-compose logs -f

cd flowsentinel

# Stop

docker-compose down| Component | Technology | Purpose |

```

# Run automated setup|-----------|-----------|---------|

### Using Docker

chmod +x scripts/setup.sh| **Framework** | FastAPI 0.104.1 | High-performance async web framework |

```bash

# Build image./scripts/setup.sh| **Server** | Uvicorn | ASGI server with hot reload |

docker build -t flowsentinel .

| **Validation** | Pydantic v2 | Type-safe data models |

# Run container

docker run -d -p 8000:8000 --env-file .env flowsentinel# Activate virtual environment| **AI Engine** | IBM watsonx.ai | Event analysis & state generation (simulated) |

```

source venv/bin/activate| **Automation** | IBM watsonx Orchestrate | Action execution (simulated) |

**See [docs/DOCKER.md](docs/DOCKER.md) for complete Docker guide**

```| **HTTP Client** | httpx + requests | Async/sync HTTP requests |

---

| **Storage** | In-Memory (MVP) | Lists/dicts (ready for PostgreSQL) |

## 🔐 Environment Configuration

### 2. Configure (Optional)| **Config** | python-dotenv | Environment variable management |

Create `.env` file (optional for demo mode):

| **Date Handling** | python-dateutil | Advanced datetime operations |

```bash

# Copy example```bash

cp .env.example .env

# Copy environment template---

# Edit with your credentials

nano .envcp .env.example .env

```

## �🚀 Quick Start

### Required for Production

# Add your Slack webhook for real notifications

```bash

# IBM watsonx.ai# Edit .env and set SLACK_WEBHOOK_URL### Prerequisites

WATSONX_API_KEY=your_api_key

WATSONX_PROJECT_ID=your_project_id```



# IBM watsonx Orchestrate- Python 3.8 or higher

ORCHESTRATE_API_KEY=your_api_key

ORCHESTRATE_INSTANCE_ID=your_instance_id### 3. Start Server- pip (Python package manager)



# Slack (optional but recommended)- Terminal/Command line access

SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

``````bash



**Note:** System works in simulation mode without any API keys!# Quick start### Installation



---./scripts/start.sh



## 🧪 Testing**Option 1: Using setup script (Recommended)**



### Run All Tests# Or manually```bash



```bashpython src/main.py# Navigate to project directory

python tests/test_api.py

``````cd flowsentinel



### Run Demo



```bashServer runs at: **http://localhost:8000**  # Run automated setup

python tests/demo.py

```Interactive docs: **http://localhost:8000/docs**chmod +x setup.sh



### CI/CD./setup.sh



GitHub Actions automatically runs tests on every push. See `.github/workflows/test.yml`### 4. Test It



**See [docs/CI-CD.md](docs/CI-CD.md) for CI/CD setup guide**# Activate virtual environment



---```bashsource venv/bin/activate



## 💻 Development# Run comprehensive test suite```



### Install Dev Dependenciespython tests/test_api.py



```bash**Option 2: Manual setup**

pip install -r requirements-dev.txt

```# Or run interactive demo```bash



### Code Qualitypython tests/demo.py# Create virtual environment



```bash```python3 -m venv venv

# Format code

black src/ tests/source venv/bin/activate  # On Windows: venv\Scripts\activate



# Lint code---

flake8 src/ tests/

# Install dependencies

# Type checking

mypy src/## 📡 API Endpointspip install -r requirements.txt

```



### Project Structure

### Core Operations# Create environment file

- **`src/main.py`** — Core FastAPI application with Database, WatsonxAgent, OrchestrateBridge

- **`tests/test_api.py`** — Comprehensive test suite (10+ test functions)cp .env.example .env

- **`tests/demo.py`** — Interactive demonstration script

- **`docs/`** — Complete documentation guides| Method | Endpoint | Description |```

- **`scripts/`** — Automation scripts for setup, start, git operations

|--------|----------|-------------|

---

| `GET` | `/` | API information and version |### Running the Server

## 📊 How It Works

| `GET` | `/health` | Health check with metrics |

### Analysis Algorithm

```bash

1. **Event Collection** — Gather last 20 events from database

2. **Blocker Detection** — Scan Slack messages for keywords: "blocked", "waiting", "stuck", "can't proceed"### Event Management# Start the FastAPI server

3. **Risk Identification** — Find Jira deadline changes and delays

4. **Completion Tracking** — Identify merged PRs and completed taskspython main.py

5. **Status Calculation:**

   - 🔴 **RED:** 2+ blockers OR 2+ risks| Method | Endpoint | Description |```

   - 🟡 **YELLOW:** 1+ blocker OR 1+ risk

   - 🟢 **GREEN:** No blockers or risks|--------|----------|-------------|

6. **Action Triggers:**

   - Blockers exist → Send Slack notification| `POST` | `/events/ingest` | Ingest single event |You should see:

   - Status is RED → Create escalation task

   - Always → Generate status report| `POST` | `/events/ingest/batch` | Ingest multiple events |```



### Q&A System| `GET` | `/events/list?limit=50` | List recent events |🚀 FlowSentinel Backend Started



Natural language processing (simulated) that understands questions like:| `POST` | `/simulation/run` | Load 8 demo events |📊 Dashboard: http://localhost:8000/docs

- "Is the project at risk?"

- "What are the current blockers?"🧠 Watsonx.ai Integration: Ready

- "What is the project status?"

### Agent Operations🤖 Orchestrate Bridge: Ready

Returns detailed answers with reasoning steps.

```

---

| Method | Endpoint | Description |

## 📚 Documentation

|--------|----------|-------------|**Access Points:**

- **[DOCKER.md](docs/DOCKER.md)** — Complete Docker deployment guide

- **[CI-CD.md](docs/CI-CD.md)** — GitHub Actions and CI/CD setup| `POST` | `/agent/run` | Run AI analysis + trigger actions |- 🌐 API Server: http://localhost:8000

- **[.env.example](.env.example)** — Environment variables reference

| `GET` | `/state/latest` | Get current project state |- 📚 Interactive Docs: http://localhost:8000/docs

---

| `GET` | `/actions/list?limit=50` | List executed actions |- 📖 ReDoc: http://localhost:8000/redoc

## 🛠️ Tech Stack



| Component | Technology | Purpose |

|-----------|-----------|---------|### Q&A### Testing Endpoints

| Framework | FastAPI 0.104.1 | High-performance async web framework |

| Server | Uvicorn | ASGI server with hot reload |

| Validation | Pydantic v2 | Type-safe data models |

| AI Engine | IBM watsonx.ai | Event analysis (simulated for demo) || Method | Endpoint | Description |**Option 1: Using the demo script (Recommended)**

| Automation | IBM watsonx Orchestrate | Action execution (simulated for demo) |

| HTTP Client | httpx + requests | Async/sync HTTP requests ||--------|----------|-------------|```bash

| Storage | In-Memory (MVP) | Ready for PostgreSQL migration |

| `POST` | `/qa/ask` | Ask natural language questions |# In a new terminal (keep server running)

---

python demo.py

## 🎯 Use Cases

**Full interactive documentation:** Visit `/docs` when server is running```

- **Software Development Teams** — Monitor sprint progress, detect blockers

- **Project Management** — Track deadlines, identify risks

- **DevOps Teams** — Monitor deployments, catch failures

- **Customer Support** — Track ticket resolution, identify bottlenecks---**Option 2: Using the comprehensive test suite**

- **Any Team Using Multiple Tools** — Centralize and analyze workflow data

```bash

---

## 📁 Project Structurepython test_api.py

## 🔮 Future Enhancements

```

### Near Term

- [ ] PostgreSQL database integration```

- [ ] WebSocket support for real-time updates

- [ ] User authentication & authorizationflowsentinel/**Option 3: Manual curl commands**

- [ ] Multi-project/tenant support

├── src/                          # Source code```bash

### Medium Term

- [ ] Real IBM watsonx.ai API integration│   └── main.py                   # Main FastAPI application (933 lines)# Load simulation data

- [ ] Real IBM watsonx Orchestrate integration

- [ ] Frontend dashboard (React/Vue)├── tests/                        # Test suitecurl -X POST http://localhost:8000/simulation/run

- [ ] Advanced analytics

│   ├── test_api.py              # Comprehensive API tests

### Long Term

- [ ] Machine learning for predictive analysis│   └── demo.py                  # Interactive demonstration# Run agent analysis

- [ ] Sentiment analysis on communications

- [ ] Mobile app for notifications├── scripts/                      # Automation scriptscurl -X POST http://localhost:8000/agent/run

- [ ] Integration with MS Teams, Discord

│   ├── setup.sh                 # Initial project setup

---

│   ├── start.sh                 # Quick server start# Check project status

## 🤝 Contributing

│   ├── git-setup.sh             # Git initializationcurl http://localhost:8000/state/latest

Contributions are welcome! Here's how:

│   └── quick-push.sh            # GitHub push helper

1. Fork the repository

2. Create a feature branch (`git checkout -b feature/amazing-feature`)├── docs/                         # Documentation# Ask a question

3. Commit your changes (`git commit -m 'feat: add amazing feature'`)

4. Push to the branch (`git push origin feature/amazing-feature`)│   ├── DOCKER.md                # Docker deployment guidecurl -X POST http://localhost:8000/qa/ask \

5. Open a Pull Request

│   └── CI-CD.md                 # Continuous integration guide  -H "Content-Type: application/json" \

---

├── .github/workflows/            # CI/CD pipelines  -d '{"question": "Is the project at risk?"}'

## 📄 License

│   └── test.yml                 # GitHub Actions workflow```

MIT License - See [LICENSE](LICENSE) for details

├── requirements.txt              # Production dependencies

---

├── requirements-dev.txt          # Development tools---

## 🙏 Acknowledgments

├── Dockerfile                    # Multi-stage Docker build

- **IBM watsonx.ai** — For inspiration on agentic AI systems

- **IBM watsonx Orchestrate** — For digital labor automation concepts├── docker-compose.yml            # Container orchestration## 📡 API Endpoints

- **FastAPI** — For making Python APIs a joy to build

- **The Open Source Community** — For amazing tools and libraries├── .env.example                  # Environment variable template



---└── README.md                     # This file### Health & Info



## 📞 Support``````



- 🐛 **Issues:** [GitHub Issues](https://github.com/Nabilhassan12345/flowsentinel/issues)GET  /           # API information

- 📚 **Docs:** Visit `/docs` endpoint when running

- 💬 **Questions:** Open a discussion or issue---GET  /health     # Health check with metrics



---```



**Built with ❤️ using FastAPI, IBM watsonx.ai, and IBM watsonx Orchestrate**## 🐳 Docker Deployment



*Last updated: November 22, 2025*### Event Management


### Quick Start with Docker```

POST /events/ingest        # Ingest single event

```bashPOST /events/ingest/batch  # Ingest multiple events

# Build and run with docker-composeGET  /events/list          # List recent events (supports ?limit=N)

docker-compose up --buildPOST /simulation/run       # Load 8 demo events

```

# Or use standalone Docker

docker build -t flowsentinel .### Agent Operations

docker run -p 8000:8000 --env-file .env flowsentinel```

```POST /agent/run      # Run AI analysis + trigger actions

GET  /state/latest   # Get current project state

### Production DeploymentGET  /actions/list   # List executed actions (supports ?limit=N)

```

See [docs/DOCKER.md](docs/DOCKER.md) for:

- Multi-stage build optimization### Q&A

- Resource limits and health checks```

- CI/CD integration with DockerPOST /qa/ask         # Ask natural language questions

- Kubernetes deployment examples```



---**Full API Documentation:** Visit http://localhost:8000/docs when server is running



## ⚙️ Configuration---



### Environment Variables## 🔐 Environment Variables



Key variables in `.env`:Copy `.env.example` to `.env` and configure:



```bash### Required for Production

# Slack Integration (EASIEST - Start here!)```bash

SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL# IBM watsonx.ai (for real AI analysis)

WATSONX_API_KEY=your_api_key_here

# IBM watsonx.ai (For production AI analysis)WATSONX_PROJECT_ID=your_project_id

WATSONX_API_KEY=your_api_keyWATSONX_URL=https://us-south.ml.cloud.ibm.com

WATSONX_PROJECT_ID=your_project_id

WATSONX_URL=https://us-south.ml.cloud.ibm.com# IBM watsonx Orchestrate (for real automation)

ORCHESTRATE_API_KEY=your_api_key_here

# IBM watsonx Orchestrate (For real automation)ORCHESTRATE_INSTANCE_ID=your_instance_id

ORCHESTRATE_API_KEY=your_api_keyORCHESTRATE_URL=https://your-instance.watsonx-orchestrate.ibm.com

ORCHESTRATE_INSTANCE_ID=your_instance_id```



# Application Settings### Optional (Enhances Features)

APP_PORT=8000```bash

LOG_LEVEL=INFO# Slack Integration (enables real notifications)

```SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL



**For MVP/Demo:** No environment variables required! System works with simulation mode.# GitHub Integration (for future features)

GITHUB_TOKEN=ghp_your_token_here

**For Production:** See `.env.example` for complete configuration with setup instructions.GITHUB_REPO_OWNER=your-username

GITHUB_REPO_NAME=your-repo

---

# Application Settings

## 🧪 TestingAPP_PORT=8000

LOG_LEVEL=INFO

### Run Tests```



```bash**Note:** For MVP/demo, NO environment variables are required! System works with simulation mode.

# Full test suite with colored output

python tests/test_api.py---



# Interactive demo (shows all features)## 📁 Project Structure

python tests/demo.py

```

# With Dockerflowsentinel/

docker-compose run flowsentinel-backend python tests/test_api.py├── main.py              # Main FastAPI application (650+ lines)

```│   ├── Database         # In-memory storage class

│   ├── WatsonxAgent     # AI analysis engine

### Continuous Integration│   ├── OrchestrateBridge # Action execution

│   └── API Endpoints    # 11 REST endpoints

GitHub Actions automatically runs on every push:├── demo.py              # Interactive demo script

- Python linting (flake8)├── test_api.py          # Comprehensive test suite

- Code formatting check (black)├── requirements.txt     # Python dependencies

- API endpoint tests├── .env.example         # Environment variable template

- Health check validation├── .gitignore           # Git ignore rules

├── setup.sh             # Automated setup script

See [docs/CI-CD.md](docs/CI-CD.md) for CI/CD setup and best practices.└── README.md            # This file

```

---

### Key Components

## 🎯 How It Works

**`Database` Class**

### Intelligent Analysis Algorithm- In-memory storage for events, state, actions

- Easy to swap for PostgreSQL later

1. **Event Collection** — Gather last 20 events from database

2. **Blocker Detection** — Scan Slack messages for keywords:**`WatsonxAgent` Class**

   - "blocked", "waiting", "stuck", "can't proceed", "need", "missing"- Analyzes events to detect blockers/risks

3. **Risk Identification** — Find Jira deadline changes and delayed tasks- Calculates project health status

4. **Completion Tracking** — Identify merged PRs and completed Jira tasks- Answers natural language questions

5. **Status Calculation:**

   - 🔴 **RED**: 2+ blockers OR 2+ risks**`OrchestrateBridge` Class**

   - 🟡 **YELLOW**: 1+ blockers OR 1+ risks- Executes automated skills

   - 🟢 **GREEN**: No blockers or risks- Real Slack webhook integration

6. **Action Triggers:**- Simulated task creation & reports

   - If blockers exist → Send Slack notification

   - If status is RED → Create escalation task---

   - Always → Generate status report

## 🎮 Demo Instructions

### Natural Language Q&A

### Full Demo Sequence

Uses pattern matching and context analysis:

- Understands questions like "Is the project at risk?", "What are the blockers?", "What's the status?"1. **Start the server:**

- Returns multi-sentence answers with reasoning steps   ```bash

- Context-aware based on current project state and recent events   python main.py

   ```

---

2. **Run the demo script** (in a new terminal):

## 💡 Example Usage   ```bash

   python demo.py

### 1. Load Simulation Data   ```



```bash3. **What you'll see:**

curl -X POST http://localhost:8000/simulation/run   - ✅ Health check

```   - 📥 8 events loaded (Slack messages, Jira updates, GitHub PRs)

   - 🤖 Agent analysis detecting 1 blocker + 2 risks

Creates 8 realistic events representing a typical workday with blockers and risks.   - 🚦 Status: YELLOW (warning level)

   - 📬 Slack notification sent (if webhook configured)

### 2. Run AI Analysis   - 📋 Escalation task created

   - 💬 Q&A with 3 sample questions

```bash   - 📊 Summary of all actions taken

curl -X POST http://localhost:8000/agent/run

```### Understanding the Simulation



Analyzes events, detects issues, triggers automated actions.The demo creates a realistic scenario:

- **Blocker:** "Backend is blocked waiting on design schema"

### 3. Check Project Status- **Risk 1:** Landing Page Schema delayed

- **Risk 2:** API Integration deadline changed

```bash- **Result:** Project status = YELLOW (1 blocker + 2 risks)

curl http://localhost:8000/state/latest

```---



Returns:## � Development Tips

```json

{### Running in Development Mode

  "status": "YELLOW",

  "blockers": [```bash

    {# Auto-reload on file changes (default in main.py)

      "description": "Backend is blocked waiting on design schema",python main.py

      "source": "Slack",

      "timestamp": "2024-03-20T14:10:00Z"# Manual reload with uvicorn

    }uvicorn main:app --reload --host 0.0.0.0 --port 8000

  ],```

  "risks": [...],

  "completed_today": [...],### Testing Individual Endpoints

  "next_deadline": "2024-03-25T17:00:00Z"

}```bash

```# Test health

curl http://localhost:8000/health

### 4. Ask Questions

# Test with pretty output

```bashcurl http://localhost:8000/state/latest | python -m json.tool

curl -X POST http://localhost:8000/qa/ask \```

  -H "Content-Type: application/json" \

  -d '{"question": "Is the project at risk?"}'### Adding New Event Sources

```

1. Add event type to `Event.source` enum in `main.py`

---2. Update `WatsonxAgent.analyze_state()` to process new events

3. Add sample events to `/simulation/run` endpoint

## 🛠️ Development

### Customizing Analysis Logic

### Local Development

Edit `WatsonxAgent.analyze_state()` in `main.py`:

```bash- Modify blocker keywords (line ~250)

# Install dev dependencies- Adjust risk detection logic (line ~260)

pip install -r requirements-dev.txt- Change status calculation thresholds (line ~295)



# Run with hot reload (auto-restarts on code changes)---

python src/main.py

## 🔧 Troubleshooting

# Format code

black src/ tests/### Server Won't Start



# Lint code**Problem:** `Address already in use`

flake8 src/ tests/```bash

# Find process using port 8000

# Run pre-commit checkslsof -i :8000

pre-commit run --all-files

```# Kill the process

kill -9 <PID>

### Adding Features```



1. Create feature branch: `git checkout -b feature/your-feature`**Problem:** `ModuleNotFoundError`

2. Make changes in `src/main.py````bash

3. Add tests in `tests/test_api.py`# Ensure virtual environment is activated

4. Run tests: `python tests/test_api.py`source venv/bin/activate

5. Commit and push: `git push origin feature/your-feature`

6. Create Pull Request on GitHub# Reinstall dependencies

pip install -r requirements.txt

---```



## 🔧 Troubleshooting### Agent Returns 400 Error



### Server Won't Start**Problem:** `No events to analyze`

```bash

```bash# Solution: Load simulation data first

# Check if port 8000 is in usecurl -X POST http://localhost:8000/simulation/run

lsof -i :8000curl -X POST http://localhost:8000/agent/run

```

# Kill existing process

kill -9 <PID>### Slack Notifications Not Working



# Or use different port**Problem:** No webhook configured

APP_PORT=8001 python src/main.py```bash

```# Check console for message like:

# "ℹ️ Slack webhook not configured"

### Tests Fail with "Connection Error"

# Solution: Add webhook to .env

Server must be running before tests:echo "SLACK_WEBHOOK_URL=https://hooks.slack.com/..." >> .env



**Terminal 1:**# Restart server

```bash```

python src/main.py

```### Tests Failing



**Terminal 2:****Problem:** Server not running

```bash```bash

python tests/test_api.py# Start server first

```python main.py



### Import Errors# Then run tests in new terminal

python test_api.py

```bash```

# Ensure virtual environment is activated

source venv/bin/activate---



# Reinstall dependencies## 🎓 How It Works

pip install -r requirements.txt

```### Analysis Algorithm



### Docker Build Fails1. **Event Collection:** Gather last 20 events from database

2. **Blocker Detection:** Scan Slack messages for keywords:

```bash   - "blocked", "waiting", "stuck", "can't proceed", "need", "missing"

# Clean Docker cache3. **Risk Identification:** Find Jira deadline changes and delays

docker system prune -a4. **Completion Tracking:** Identify merged PRs and completed tasks

5. **Status Calculation:**

# Rebuild without cache   - 🔴 **RED:** 2+ blockers OR 2+ risks

docker-compose build --no-cache   - 🟡 **YELLOW:** 1+ blockers OR 1+ risks

```   - 🟢 **GREEN:** No blockers or risks

6. **Action Triggers:**

---   - If blockers exist → Send Slack notification

   - If status is RED → Create escalation task

## 📊 Key Features   - Always → Generate status report



### ✅ Production-Ready### Q&A System



- **Type Safety** — Full Pydantic v2 validationThe natural language Q&A uses pattern matching to understand questions:

- **Error Handling** — Comprehensive try-catch with meaningful messages- Keywords: "risk", "blocker", "status"

- **Health Checks** — Built-in monitoring endpoint- Context: Recent events + current state

- **Auto Documentation** — Interactive Swagger UI at `/docs`- Output: Multi-sentence answer + reasoning steps

- **CORS Enabled** — Ready for frontend integration

- **Hot Reload** — Instant updates during development---



### ✅ Enterprise-Grade## 🔮 Future Enhancements



- **Separation of Concerns** — Database, Agent, Bridge, API layers### Near Term

- **Containerization** — Docker and docker-compose included- [ ] PostgreSQL database integration

- **CI/CD Pipeline** — Automated testing on every commit- [ ] WebSocket support for real-time updates

- **Logging** — Detailed console output for debugging- [ ] User authentication & authorization

- **Scalable Architecture** — Ready for PostgreSQL, WebSocket, multi-tenant- [ ] Multi-project/tenant support



### ✅ Intelligent### Medium Term

- [ ] Real IBM watsonx.ai API integration

- **Keyword Detection** — Scans for blockers and risks- [ ] Real IBM watsonx Orchestrate integration

- **Risk Calculation** — Identifies deadline changes- [ ] Advanced analytics dashboard

- **Status Algorithm** — Smart health determination- [ ] Custom action workflow builder

- **Context-Aware Q&A** — Natural language understanding

- **Reasoning Steps** — Transparent AI decision-making### Long Term

- [ ] Machine learning for predictive risk analysis

---- [ ] Sentiment analysis on team communications

- [ ] Auto-generated status reports (PDF/email)

## 🔮 Future Enhancements- [ ] Mobile app for notifications

- [ ] Integration with MS Teams, Discord, etc.

### Near Term

- [ ] Real IBM watsonx.ai API integration---

- [ ] PostgreSQL database (swap from in-memory)

- [ ] WebSocket support for real-time updates## � Data Models

- [ ] Frontend dashboard (React/Vue)

### Event Schema

### Medium Term```python

- [ ] Multi-project/tenant support{

- [ ] Advanced analytics dashboard  "id": "evt_001",

- [ ] Custom action workflow builder  "source": "slack" | "jira" | "github" | "calendar",

- [ ] Real Jira/GitHub API integration  "type": "message" | "task_status_changed" | "pr_opened" | ...,

  "timestamp": "2024-03-20T14:10:00Z",

### Long Term  "data": { /* flexible payload */ },

- [ ] Machine learning for predictive risk analysis  "processed": false

- [ ] Sentiment analysis on team communications}

- [ ] Auto-generated PDF/email reports```

- [ ] Mobile app for notifications

### ProjectState Schema

---```python

{

## 📈 Project Stats  "status": "GREEN" | "YELLOW" | "RED",

  "blockers": [{"description": "...", "source": "...", "timestamp": "..."}],

- **Total Lines**: ~3,600+  "risks": [{"description": "...", "impact": "...", "timestamp": "..."}],

- **Main Application**: 933 lines (`src/main.py`)  "completed_today": [{"description": "...", "timestamp": "..."}],

- **API Endpoints**: 11 fully documented  "next_deadline": "2024-03-25T17:00:00Z",

- **Test Coverage**: 10+ test functions  "last_updated": "2024-03-20T15:00:00Z"

- **Data Models**: 5 Pydantic models}

- **Docker Ready**: Multi-stage build```

- **CI/CD**: GitHub Actions pipeline

---

---

## 📄 License

## 🤝 Contributing

MIT License

Contributions welcome! To contribute:

Copyright (c) 2024 FlowSentinel

1. Fork the repository

2. Create feature branch (`git checkout -b feature/amazing-feature`)Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

3. Commit changes (`git commit -m 'Add amazing feature'`)

4. Push to branch (`git push origin feature/amazing-feature`)The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

5. Open Pull Request

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

See [GitHub Issues](https://github.com/Nabilhassan12345/flowsentinel/issues) for ideas.

---

---

## 🤝 Contributing

## 📄 License

This project was built for a hackathon but welcomes contributions!

MIT License — See [LICENSE](LICENSE) file for details.

**To contribute:**

---1. Fork the repository

2. Create a feature branch (`git checkout -b feature/amazing-feature`)

## 🙏 Acknowledgments3. Commit your changes (`git commit -m 'Add amazing feature'`)

4. Push to the branch (`git push origin feature/amazing-feature`)

- **IBM watsonx.ai** — For agentic AI inspiration5. Open a Pull Request

- **IBM watsonx Orchestrate** — For digital labor automation concepts

- **FastAPI** — For making Python APIs a joy to build---

- **Open Source Community** — For amazing tools and libraries

## � Acknowledgments

---

- **IBM watsonx.ai** - For inspiration on agentic AI systems

## 📞 Support- **IBM watsonx Orchestrate** - For digital labor automation concepts

- **FastAPI** - For making Python APIs a joy to build

- 📧 **Issues**: [GitHub Issues](https://github.com/Nabilhassan12345/flowsentinel/issues)- **The Open Source Community** - For amazing tools and libraries

- 💬 **Questions**: Check `/docs` endpoint when server is running

- 🌟 **Like it?**: Star this repo!---



---## 📞 Support



## 🎓 Learn More- 📧 Report issues on GitHub Issues

- 💬 Questions? Check out the `/docs` endpoint when running

- **FastAPI Docs**: https://fastapi.tiangolo.com/- 🌟 Star this repo if you find it helpful!

- **Pydantic**: https://docs.pydantic.dev/

- **Docker**: https://docs.docker.com/---

- **IBM watsonx**: https://www.ibm.com/watsonx

## 📦 **Complete Project Contents**

---

This repository includes everything needed for a production-ready agentic AI system:

**Built with ❤️ using FastAPI, Python 3.11, Docker, and IBM watsonx**

### **Core Application Files**

*Last updated: November 22, 2025*- **`main.py`** (933 lines) - Complete FastAPI backend with:

  - Database class for in-memory storage
  - WatsonxAgent class for AI analysis
  - OrchestrateBridge class for automated actions
  - 11 fully documented REST API endpoints
  - Pydantic models for type safety
  - Comprehensive error handling

- **`demo.py`** - Interactive demonstration script showing:
  - Health checks
  - Event ingestion (8 realistic scenarios)
  - Agent analysis execution
  - State retrieval and display
  - Q&A system demonstration
  - Action history viewing

- **`test_api.py`** - Comprehensive test suite with:
  - 10+ test functions covering all endpoints
  - Colored terminal output (✅/❌)
  - Response time tracking
  - Pretty JSON formatting
  - Automatic pass/fail summary

### **Configuration & Dependencies**
- **`requirements.txt`** - Production dependencies:
  - FastAPI 0.104.1 (Web framework)
  - Uvicorn 0.24.0 (ASGI server)
  - Pydantic 2.5.0 (Data validation)
  - httpx 0.25.1 (Async HTTP client)
  - requests 2.31.0 (Sync HTTP client)
  - python-dotenv 1.0.0 (Environment variables)
  - python-dateutil 2.8.2 (Date handling)

- **`requirements-dev.txt`** - Development tools:
  - flake8, black, isort, pylint (Code quality)
  - pytest, pytest-cov (Testing)
  - ipython, ipdb (Debugging)
  - mkdocs (Documentation)

- **`.env.example`** - Complete environment variable template with:
  - IBM watsonx.ai configuration
  - IBM watsonx Orchestrate settings
  - Slack webhook URL
  - GitHub token
  - Jira credentials
  - Application settings
  - Detailed setup instructions for each service

### **Docker Support**
- **`Dockerfile`** - Multi-stage build configuration:
  - Python 3.11-slim base image
  - Optimized for size (~200MB)
  - Non-root user for security
  - Health check included

- **`docker-compose.yml`** - Complete orchestration:
  - Backend service configuration
  - Volume mounts for hot reload
  - Environment variable management
  - Health checks and restart policies
  - Resource limits (CPU/Memory)
  - Network isolation

- **`.dockerignore`** - Optimized build context

### **CI/CD & Automation**
- **`.github/workflows/test.yml`** - GitHub Actions pipeline:
  - Automated testing on push/PR
  - Python 3.11 matrix
  - Code linting (flake8)
  - Format checking (black)
  - API endpoint testing
  - Health check validation
  - ~1-2 minute execution time

- **`setup.sh`** - Automated setup script:
  - Virtual environment creation
  - Dependency installation
  - .env file initialization

- **`start.sh`** - Quick start script:
  - Environment activation
  - Dependency verification
  - Server startup with logging

- **`git-setup.sh`** - Git initialization helper:
  - Repository initialization
  - Initial commit creation
  - Remote setup instructions

### **Documentation**
- **`README.md`** - This comprehensive guide (500+ lines)
- **`DOCKER.md`** - Complete Docker guide with:
  - Build and run commands
  - Development vs production modes
  - Troubleshooting tips
  - CI/CD integration examples

- **`CI-CD.md`** - Continuous integration guide:
  - GitHub Actions setup
  - Local development with linting
  - Pre-commit hooks
  - Best practices

### **Git Configuration**
- **`.gitignore`** - Comprehensive ignore rules:
  - Python cache and compiled files
  - Virtual environments
  - Environment variables (.env)
  - IDE files
  - Logs and temporary files

---

## 🏆 **What Makes This Special**

### **Enterprise-Grade Architecture**
- ✅ **Separation of Concerns** - Database, Agent, Bridge, API layers
- ✅ **Type Safety** - Full Pydantic validation on all endpoints
- ✅ **Error Handling** - Comprehensive try-catch with meaningful messages
- ✅ **Logging** - Detailed console output for debugging
- ✅ **CORS Enabled** - Ready for frontend integration

### **Production-Ready Features**
- ✅ **Health Checks** - Built-in endpoint for monitoring
- ✅ **Auto-Documentation** - Interactive Swagger UI at `/docs`
- ✅ **Hot Reload** - Instant code updates during development
- ✅ **Containerization** - Docker and docker-compose included
- ✅ **CI/CD Pipeline** - Automated testing on every commit

### **Intelligent Analysis**
- ✅ **Keyword Detection** - Scans for "blocked", "stuck", "waiting", etc.
- ✅ **Risk Calculation** - Identifies deadline changes and delays
- ✅ **Status Algorithm** - Smart RED/YELLOW/GREEN determination
- ✅ **Context-Aware Q&A** - Natural language understanding
- ✅ **Reasoning Steps** - Transparent AI decision-making

### **Scalability Path**
- ✅ **Database-Ready** - Easy swap from in-memory to PostgreSQL
- ✅ **API-Extensible** - Structured for real watsonx.ai integration
- ✅ **Multi-Tenant Ready** - Architecture supports multiple projects
- ✅ **WebSocket-Compatible** - Can add real-time updates

---

## 🎓 **Learning Resources**

If you want to understand how this works:

1. **Start with `main.py` lines 1-100** - See the data models and architecture
2. **Read `WatsonxAgent.analyze_state()`** - Understand the AI logic
3. **Check `OrchestrateBridge.execute_skill()`** - See action execution
4. **Run `demo.py`** - See everything in action
5. **Explore `/docs`** - Interactive API documentation

---

## 🚀 **Next Steps**

### **For Development:**
1. Add real IBM watsonx.ai API integration
2. Connect to actual Jira/GitHub APIs
3. Build frontend dashboard (React/Vue)
4. Add PostgreSQL database
5. Implement WebSocket for real-time updates

### **For Production:**
1. Set up proper environment variables
2. Configure Slack webhook
3. Deploy to cloud (AWS/Azure/GCP)
4. Set up monitoring (Datadog/New Relic)
5. Add authentication/authorization

### **For Learning:**
1. Study the code structure
2. Experiment with different event types
3. Modify the analysis algorithm
4. Create custom actions
5. Build your own frontend

---

## 💼 **Use Cases**

This system can be adapted for:
- **Software Development Teams** - Monitor sprint progress, detect blockers
- **Project Management** - Track deadlines, identify risks
- **DevOps Teams** - Monitor deployments, catch failures
- **Customer Support** - Track ticket resolution, identify bottlenecks
- **Any Team Using Multiple Tools** - Centralize and analyze workflow data

---

## 📊 **Project Statistics**

- **Total Lines of Code**: ~3,600+
- **Main Application**: 933 lines (main.py)
- **Test Coverage**: 10+ test functions
- **API Endpoints**: 11 fully documented
- **Data Models**: 5 Pydantic models
- **Docker Files**: 3 (Dockerfile, compose, ignore)
- **Documentation Pages**: 4 (README, DOCKER, CI-CD, .env.example)
- **Scripts**: 4 automation scripts
- **Development Time**: Built for hackathon/learning project

---

**Built with ❤️ using FastAPI, IBM watsonx.ai, and IBM watsonx Orchestrate**

**Technologies**: Python 3.11 • FastAPI • Pydantic v2 • Uvicorn • Docker • GitHub Actions • IBM Cloud

*Last updated: November 22, 2025*

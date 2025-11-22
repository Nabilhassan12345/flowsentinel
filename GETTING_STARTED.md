# 🚀 Getting Started with FlowSentinel

Complete beginner-friendly guide to get FlowSentinel running in 5 minutes.

---

## ⚡ Quick Start (3 Commands)

```bash
# 1. Setup project (creates venv, installs dependencies)
./scripts/setup.sh

# 2. Start server
./scripts/start.sh

# 3. In new terminal: Run tests
python tests/test_api.py
```

**That's it!** Your FlowSentinel backend is running at http://localhost:8000

---

## 📋 Detailed Setup Guide

### Prerequisites

✅ Python 3.8 or higher  
✅ pip (Python package manager)  
✅ Terminal/Command line  

**Check your Python version:**
```bash
python3 --version
# Should show: Python 3.8.x or higher
```

### Step-by-Step Installation

#### 1️⃣ Clone the Repository

```bash
git clone https://github.com/Nabilhassan12345/flowsentinel.git
cd flowsentinel
```

#### 2️⃣ Run Setup Script

```bash
chmod +x scripts/*.sh  # Make scripts executable
./scripts/setup.sh      # Run automated setup
```

**What this does:**
- Creates Python virtual environment
- Installs all dependencies
- Creates `.env` file from template

#### 3️⃣ Start the Server

```bash
./scripts/start.sh
```

**You should see:**
```
🚀 FlowSentinel Backend Started
📊 Dashboard: http://localhost:8000/docs
🧠 Watsonx.ai Integration: Ready
🤖 Orchestrate Bridge: Ready
INFO:     Uvicorn running on http://0.0.0.0:8000
```

✅ **Server is running!** Leave this terminal open.

#### 4️⃣ Test the API (New Terminal)

Open a **new terminal** and run:

```bash
cd flowsentinel
source venv/bin/activate  # Activate virtual environment
python tests/test_api.py  # Run comprehensive tests
```

**You should see:**
```
✅ Test 1: Health Check - PASSED
✅ Test 2: Root Endpoint - PASSED
✅ Test 3: Load Simulation - PASSED
...
🎉 ALL TESTS PASSED! 🎉
```

#### 5️⃣ Try the Interactive Demo

```bash
python tests/demo.py
```

This demonstrates:
- Event ingestion
- AI analysis
- Blocker detection
- Q&A system
- Automated actions

---

## 🌐 Access Points

Once the server is running:

| Service | URL | Description |
|---------|-----|-------------|
| **API Server** | http://localhost:8000 | Main API endpoint |
| **Interactive Docs** | http://localhost:8000/docs | Swagger UI |
| **Alternative Docs** | http://localhost:8000/redoc | ReDoc UI |
| **Health Check** | http://localhost:8000/health | Server status |

---

## 📝 Common Commands

### Server Management

```bash
# Start server
./scripts/start.sh

# Start server manually
source venv/bin/activate
python src/main.py

# Stop server
# Press Ctrl+C in the server terminal
```

### Testing

```bash
# Run all tests
python tests/test_api.py

# Run demo
python tests/demo.py

# Manual API test
curl http://localhost:8000/health
```

### Development

```bash
# Activate virtual environment
source venv/bin/activate

# Install new package
pip install package-name

# Update requirements
pip freeze > requirements.txt

# Code formatting
pip install black
black src/main.py

# Linting
pip install flake8
flake8 src/main.py
```

---

## 🔧 Configuration

### Environment Variables (Optional)

Edit `.env` file to add real API keys:

```bash
# Slack notifications (optional but recommended)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# IBM watsonx.ai (optional - uses simulation by default)
WATSONX_API_KEY=your_api_key
WATSONX_PROJECT_ID=your_project_id

# See .env.example for all options
```

**To get Slack webhook:**
1. Go to https://api.slack.com/apps
2. Create new app → "Incoming Webhooks"
3. Copy webhook URL to `.env`

---

## 🐳 Docker Alternative

If you prefer Docker:

```bash
# Build and run
docker-compose up --build

# Run in background
docker-compose up -d

# Stop
docker-compose down
```

**Access same URLs:**
- http://localhost:8000
- http://localhost:8000/docs

---

## 🧪 Testing Different Features

### 1. Load Simulation Data

```bash
curl -X POST http://localhost:8000/simulation/run
```

### 2. Run AI Analysis

```bash
curl -X POST http://localhost:8000/agent/run
```

### 3. Get Project Status

```bash
curl http://localhost:8000/state/latest
```

### 4. Ask a Question

```bash
curl -X POST http://localhost:8000/qa/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Is the project at risk?"}'
```

---

## ❓ Troubleshooting

### Server Won't Start

**Problem:** Port 8000 already in use

```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>
```

**Problem:** ModuleNotFoundError

```bash
# Activate virtual environment
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Tests Fail

**Problem:** "Server is not running"

```bash
# Start server in separate terminal first
./scripts/start.sh

# Then run tests in new terminal
python tests/test_api.py
```

### Import Errors

**Problem:** "Cannot import main"

```bash
# Make sure you're in project root
cd /path/to/flowsentinel

# Run from project root
python tests/test_api.py
```

---

## 📚 Next Steps

### Learn the API
1. Open http://localhost:8000/docs
2. Click "Try it out" on any endpoint
3. See request/response examples

### Explore the Code
1. Start with `src/main.py` (lines 1-100)
2. Read `WatsonxAgent` class (AI logic)
3. Check `OrchestrateBridge` class (actions)

### Customize
1. Modify `WatsonxAgent.analyze_state()` for different analysis
2. Add new event types in `Event` model
3. Create new API endpoints

### Deploy
1. See `docs/DOCKER.md` for Docker deployment
2. See `docs/CI-CD.md` for GitHub Actions
3. Add real API keys for production

---

## 🎯 Project Structure

```
flowsentinel/
├── src/main.py          # Main application
├── tests/               # Tests and demos
├── scripts/             # Helper scripts
├── docs/                # Documentation
└── README.md            # Main guide
```

See `STRUCTURE.md` for detailed breakdown.

---

## 💡 Tips

✅ **Keep server running** - Don't close the terminal  
✅ **Use virtual environment** - `source venv/bin/activate`  
✅ **Check logs** - Server terminal shows all activity  
✅ **Read errors** - They're usually self-explanatory  
✅ **Start simple** - Use demo.py to understand flow  

---

## 🆘 Need Help?

1. Check `README.md` for comprehensive guide
2. Check `docs/` folder for specific topics
3. Open an issue on GitHub
4. Review interactive docs at `/docs` endpoint

---

**You're ready to start! Run `./scripts/start.sh` and explore!** 🚀

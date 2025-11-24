# ⚡ FLOWSENTINEL - QUICK COMMAND REFERENCE

## 🚀 START SERVER
```bash
cd /Users/nabilhassan/Desktop/flowsentinel
source .venv/bin/activate
python src/main.py
```

## 🎬 RUN DEMO
```bash
# Option 1: Full demo script
python demo.py

# Option 2: Quick shell script
./run-demo.sh

# Option 3: Manual commands
curl -X POST http://localhost:8000/simulation/run
curl -X POST http://localhost:8000/agent/run
```

## 🔍 CHECK STATUS
```bash
# Health check
curl http://localhost:8000/health

# Agent status
curl http://localhost:8000/agent/status | python -m json.tool

# View latest state
curl http://localhost:8000/state/latest | python -m json.tool
```

## 📊 ANALYTICS
```bash
# Risk score
curl http://localhost:8000/analytics/risk-score | python -m json.tool

# Team velocity
curl http://localhost:8000/analytics/velocity | python -m json.tool

# Workload distribution
curl http://localhost:8000/analytics/workload | python -m json.tool
```

## 🔮 INTELLIGENCE
```bash
# Predictions
curl http://localhost:8000/intelligence/predictions | python -m json.tool

# Team health
curl http://localhost:8000/intelligence/team-health | python -m json.tool

# Anomalies
curl http://localhost:8000/intelligence/anomalies | python -m json.tool
```

## 🤖 AGENT CONTROL
```bash
# Start agent
curl -X POST http://localhost:8000/agent/start

# Stop agent
curl -X POST http://localhost:8000/agent/stop

# Check status
curl http://localhost:8000/agent/status

# Manual trigger
curl -X POST http://localhost:8000/agent/run
```

## 📢 SLACK
```bash
# Test Slack webhook
curl -X POST http://localhost:8000/debug/slack-test
```

## 🌐 BROWSER URLS
```bash
# API Documentation (Interactive)
open http://localhost:8000/docs

# Alternative docs
open http://localhost:8000/redoc

# Root endpoint
open http://localhost:8000/
```

## 🛠️ TROUBLESHOOTING
```bash
# Kill server on port 8000
lsof -ti:8000 | xargs kill -9

# Check if server is running
lsof -i:8000

# View logs (if using background)
tail -f /tmp/flowsentinel.log

# Check Python environment
which python
python --version
```

## 📦 QUICK SETUP (If Needed)
```bash
# Install dependencies
pip install -r requirements.txt

# Initialize database
python -c "from src.database import init_db; init_db()"

# Run tests
pytest tests/ -v
```

## 🎯 DEMO SEQUENCE
```bash
# 1. Start server
python src/main.py

# 2. New terminal - run demo
python demo.py

# 3. Check Slack for alert!

# 4. Show API docs
open http://localhost:8000/docs
```

## 💻 ONE-LINERS FOR JUDGES

```bash
# Show autonomous agent status
curl -s http://localhost:8000/agent/status | python -m json.tool

# Trigger immediate analysis
curl -X POST http://localhost:8000/agent/run

# Show all endpoints
curl -s http://localhost:8000/ | python -m json.tool

# Test Slack integration
curl -X POST http://localhost:8000/debug/slack-test
```

## 🎨 TERMINAL COLORS (Optional Enhancement)
```bash
# Add to demo for better visual output
export FORCE_COLOR=1
export CLICOLOR=1
```

## 📋 PRE-DEMO CHECKLIST COMMANDS
```bash
# 1. Check server
curl http://localhost:8000/health && echo "✅ Server OK" || echo "❌ Server DOWN"

# 2. Check IBM integration
curl -s http://localhost:8000/ | grep -q "WATSONX" && echo "✅ IBM OK" || echo "❌ IBM Missing"

# 3. Check Slack
curl -s http://localhost:8000/ | grep -q "SLACK" && echo "✅ Slack OK" || echo "⚠️  Slack not configured"

# 4. Check agent
curl -s http://localhost:8000/agent/status | grep -q "running" && echo "✅ Agent OK" || echo "⚠️  Agent not running"
```

## 🔥 IMPRESSIVE DEMO COMMANDS

### Show Real-Time Event Stream
```bash
# Create events and watch agent analyze
curl -X POST http://localhost:8000/simulation/run && \
sleep 2 && \
curl -X POST http://localhost:8000/agent/run | python -m json.tool
```

### Show Multi-Endpoint Power
```bash
# Hit multiple endpoints in sequence
echo "Health:" && curl -s http://localhost:8000/health && \
echo -e "\n\nRisk Score:" && curl -s http://localhost:8000/analytics/risk-score && \
echo -e "\n\nAgent Status:" && curl -s http://localhost:8000/agent/status
```

### Show Database Persistence
```bash
# Show events are saved
curl -s http://localhost:8000/events/list?limit=5 | python -m json.tool
```

## 🎤 LIVE DEMO COMMENTARY

```bash
# While demo.py runs, say:
"Watch as we create a realistic crisis scenario..."
  → Events appear in terminal

"IBM Granite AI analyzes all 12 events in real-time..."
  → Analysis output shows

"Status: RED - 3 critical blockers detected..."
  → Results displayed

"Automatic Slack alert sent to the team..."
  → Show Slack on phone

"35+ API endpoints, all documented and production-ready..."
  → Open /docs in browser
```

## ⚡ EMERGENCY FIXES

### Server Won't Start
```bash
pkill -f "python src/main.py"
lsof -ti:8000 | xargs kill -9
sleep 2
python src/main.py
```

### Demo Script Fails
```bash
# Check server first
curl http://localhost:8000/health

# If OK, try direct API calls
curl -X POST http://localhost:8000/simulation/run
curl -X POST http://localhost:8000/agent/run
```

### No Slack Alerts
```bash
# Verify webhook
echo $SLACK_WEBHOOK_URL

# Test it
curl -X POST http://localhost:8000/debug/slack-test
```

## 📱 MOBILE DEMO (If Using Phone for Slack)
```bash
# QR code for mobile browser (if needed)
# Use this to quickly share localhost URL via tunnel

# Or just show Slack app notifications!
```

## 🏆 FINAL COMMAND BEFORE SUBMISSION
```bash
# Verify everything works
python demo.py && \
curl http://localhost:8000/agent/status && \
echo "🎉 DEMO READY!"
```

---

## 💡 PRO TIPS

1. **Keep terminal visible** - Shows real-time processing
2. **Have Slack open** - Immediate alert demonstration
3. **Browser on /docs** - Interactive API exploration
4. **Confident body language** - You built something amazing!

---

## 🎯 THE 30-SECOND DEMO

If time is limited:
```bash
python demo.py
# [While running, say:]
# "IBM Granite AI analyzing 12 crisis events..."
# "RED status detected, automatic Slack alert sent..."
# "Completely autonomous, production-ready, solving real problems."
# [Show Slack alert]
# [Open /docs]
# [Done!]
```

---

**Remember**: You have a working, production-ready AI system. Be proud! 🚀

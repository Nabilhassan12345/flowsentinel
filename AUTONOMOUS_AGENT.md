# 🤖 Autonomous Agent - Full Documentation

## Overview
FlowSentinel now runs **fully autonomously** with a background AI agent that continuously monitors your project without human intervention.

## 🎯 What It Does

### Autonomous Operation
The agent runs in the background and automatically:
1. **Analyzes Events** - Fetches and analyzes events from the last 24 hours every 5 minutes
2. **AI Assessment** - Uses IBM watsonx.ai Granite model to understand project state
3. **Smart Alerts** - Sends Slack notifications when status is YELLOW or RED
4. **Action Triggers** - Automatically triggers critical actions (escalation, reports, etc.)
5. **State Persistence** - Saves all analysis results to database for history tracking

### Real-Time Intelligence
- **Status Detection**: GREEN, YELLOW, or RED based on AI analysis
- **Blocker Identification**: Automatically detects what's blocking progress
- **Risk Assessment**: Identifies potential risks before they become blockers
- **Completion Tracking**: Recognizes completed work and milestones

## 🚀 Getting Started

### 1. Server Startup
The agent starts automatically when the server launches:

```bash
python src/main.py
```

You'll see:
```
🤖 Starting Autonomous Agent...
   Interval: 300 seconds (5.0 minutes)
   Control: POST /agent/start, /agent/stop, GET /agent/status
✅ Autonomous Agent: Launched
```

### 2. Configuration
Set these environment variables in `.env`:

```bash
# Agent Configuration
AGENT_ENABLED=true                # Enable/disable autonomous agent
AGENT_RUN_INTERVAL=300            # Analysis interval in seconds (default: 300 = 5 minutes)

# Required for AI analysis
WATSONX_API_KEY=your-api-key
WATSONX_PROJECT_ID=your-project-id
WATSONX_URL=https://us-south.ml.cloud.ibm.com
WATSONX_MODEL_ID=ibm/granite-3-8b-instruct

# Required for Slack alerts
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

## 📡 API Endpoints

### Check Agent Status
```bash
GET /agent/status
```

Response:
```json
{
  "enabled": true,
  "running": true,
  "run_count": 5,
  "last_run": "2025-11-23T18:45:24.599837",
  "next_run": {
    "timestamp": "2025-11-23T18:50:24.599837",
    "seconds_remaining": 139
  },
  "config": {
    "interval_seconds": 300,
    "interval_minutes": 5.0
  }
}
```

### Start Agent (Manual)
```bash
POST /agent/start
```

Use this if you stopped the agent and want to restart it.

### Stop Agent
```bash
POST /agent/stop
```

Use this to temporarily pause autonomous monitoring.

### Manual Trigger
```bash
POST /agent/run
```

Trigger an immediate analysis without waiting for the next interval.

## 🔔 Slack Alerts

### When Alerts Are Sent
Alerts are automatically sent when status is **YELLOW** or **RED**.

### Alert Format
```
⚠️ *FlowSentinel Autonomous Alert*

*Status:* YELLOW
*Time:* 2025-11-23 18:45:24
*Run:* #3

*🚫 Blockers (1):*
  • Backend is blocked waiting on design schema

*⚠️ Risks (2):*
  • PR #42 needs review urgently
  • API Integration task has new deadline

*💡 Suggested Actions:*
  • Escalate blocker to tech lead
  • Send reminder for PR review
```

### Testing Slack
```bash
POST /debug/slack-test
```

Sends a test message to verify your webhook is configured correctly.

## 📊 What Happens Each Run

### Agent Execution Flow
1. **Wake Up** - Agent wakes up every AGENT_RUN_INTERVAL seconds (default: 300 = 5 min)
2. **Fetch Events** - Retrieves all events from the last 24 hours
3. **Skip or Analyze**:
   - If no events: Skip analysis and go back to sleep
   - If events exist: Continue to analysis
4. **AI Analysis** - IBM Granite analyzes events and determines:
   - Status (GREEN/YELLOW/RED)
   - Blockers
   - Risks
   - Completed items
   - Suggested actions
5. **Alert Decision**:
   - GREEN status: No alert sent (all good)
   - YELLOW status: Warning alert sent to Slack
   - RED status: Critical alert sent to Slack
6. **Action Execution** - High/critical priority actions are triggered
7. **Save State** - Analysis results saved to database
8. **Sleep** - Agent sleeps until next interval

### Console Output
```
======================================================================
🤖 Autonomous Agent Run #3 - 2025-11-23 18:45:24
======================================================================
📊 Found 8 events in last 24h
🧠 Analyzing with IBM watsonx.ai Granite...
   Status: RED
   Blockers: 1
   Risks: 2
   Completed: 1
✅ Slack alert sent (RED)

🎯 Triggering 2 critical actions...
   → Escalate blocker to tech lead (Priority: high)
   → Send reminder for PR review (Priority: high)

💾 State saved to database

✅ Agent run #3 complete
⏰ Next run in 300s...
```

## 🎭 Demo Mode

### Quick Demo
1. Start server: `python src/main.py`
2. Load demo events: `curl -X POST http://localhost:8000/simulation/run`
3. Trigger analysis: `curl -X POST http://localhost:8000/agent/run`
4. Check Slack for alert! 🎉

### What You'll See
- Server logs showing real-time analysis
- Slack message with status and recommendations
- Database entry with full state history

## 🏆 Production Features

### Reliability
- ✅ **Error Handling** - Agent continues running even if one analysis fails
- ✅ **Graceful Recovery** - Automatic retry on errors
- ✅ **Clean Shutdown** - Properly stops on server shutdown

### Performance
- ✅ **Async Execution** - Non-blocking background operation
- ✅ **Configurable Interval** - Adjust frequency via env var
- ✅ **Efficient Analysis** - Only analyzes recent events (24h window)

### Monitoring
- ✅ **Run Counter** - Track how many times agent has executed
- ✅ **Last Run Timestamp** - See when last analysis occurred
- ✅ **Next Run Countdown** - Know exactly when next run happens
- ✅ **Detailed Logging** - Complete console output for debugging

## 🔧 Troubleshooting

### Agent Not Starting?
Check logs for:
```
✅ Autonomous Agent: Launched
```

If you see:
```
⚠️  Autonomous Agent: Disabled (set AGENT_ENABLED=true)
```

Add to `.env`:
```
AGENT_ENABLED=true
```

### No Slack Alerts?
1. Verify webhook URL: `curl -X POST http://localhost:8000/debug/slack-test`
2. Check `.env` has: `SLACK_WEBHOOK_URL=https://hooks.slack.com/...`
3. Make sure status is YELLOW or RED (GREEN doesn't send alerts)

### IBM AI Not Working?
Verify credentials in `.env`:
```bash
WATSONX_API_KEY=your-key-here
WATSONX_PROJECT_ID=9bf9f847-e68a-4e23-b0f7-2494e143bb71
WATSONX_URL=https://us-south.ml.cloud.ibm.com
WATSONX_MODEL_ID=ibm/granite-3-8b-instruct
```

Test manually: `curl -X POST http://localhost:8000/agent/run`

## 📈 Monitoring & Analytics

### Check System Health
```bash
curl http://localhost:8000/health
```

### View Recent States
```bash
curl http://localhost:8000/state/latest
```

### View Agent History
```bash
curl http://localhost:8000/agent/status
```

## 🎯 Best Practices

### For Development
- Set `AGENT_RUN_INTERVAL=60` for faster testing (1 minute)
- Use `/agent/run` to trigger immediate analysis
- Monitor server logs for real-time feedback

### For Production
- Keep `AGENT_RUN_INTERVAL=300` (5 minutes) to avoid API rate limits
- Set up proper log aggregation (Datadog, CloudWatch, etc.)
- Monitor Slack channel for critical alerts
- Review database states weekly for trends

### For Demos
1. Load simulation: `POST /simulation/run`
2. Trigger immediate analysis: `POST /agent/run`
3. Show Slack alert in real-time
4. Display API dashboard: `http://localhost:8000/docs`
5. Show agent status: `GET /agent/status`

## 🚀 What Makes This "Agentic"

### True Autonomy
- ❌ **Before**: Manual API calls required (`POST /agent/run`)
- ✅ **Now**: Runs continuously 24/7 without human intervention

### Intelligence
- Uses real IBM watsonx.ai Granite model
- Natural language understanding of events
- Context-aware decision making

### Action
- Automatically sends alerts
- Triggers actions based on priority
- Adapts behavior to project state

### Memory
- Tracks run history
- Saves all analysis states
- Learns from past events

## 🎉 Success Metrics

After implementing autonomous agent:
- **Zero Manual Intervention** - System runs 24/7 autonomously
- **Real-Time Alerts** - Team notified within 5 minutes of issues
- **100% Event Coverage** - Every event analyzed by AI
- **Complete History** - All states saved to database
- **Production Ready** - Error handling, graceful shutdown, monitoring

---

## 🎊 You're All Set!

Your FlowSentinel is now a **true AI agent** that:
- 🧠 Thinks (IBM Granite AI analysis)
- 👀 Observes (Continuous event monitoring)
- 📢 Communicates (Slack alerts)
- 🎯 Acts (Automated actions)
- 📝 Remembers (Database state history)

**This is agentic AI in action!** 🚀

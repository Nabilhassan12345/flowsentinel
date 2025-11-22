# 📊 FlowSentinel Analytics API

Advanced analytics endpoints showing system value, risk scoring, and team velocity.

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Endpoints](#endpoints)
3. [Metrics Explained](#metrics-explained)
4. [Use Cases](#use-cases)

---

## 🎯 Overview

The Analytics API provides **6 powerful endpoints** that demonstrate FlowSentinel's value:

- **Summary** - Show time saved and automation value
- **Timeline** - Unified view of events and actions
- **Risk Score** - Real-time project health assessment (0-100)
- **Velocity** - Team productivity trends
- **Trends** - Historical patterns and forecasting
- **Health** - Overall system health score

---

## 🔌 Endpoints

### 1. **GET `/analytics/summary`**

**High-level analytics showing system value.**

**Response:**
```json
{
  "total_events_processed": 150,
  "processed_events": 145,
  "processing_rate_percent": 96.7,
  "events_by_source": {
    "slack": 85,
    "jira": 40,
    "github": 20,
    "calendar": 5
  },
  "actions_taken_automatically": 45,
  "successful_actions": 43,
  "action_success_rate_percent": 95.6,
  "estimated_time_saved_minutes": 675,
  "estimated_time_saved_hours": 11.25,
  "estimated_time_saved_days": 1.41,
  "blockers_detected": 3,
  "risks_detected": 5,
  "average_detection_time_seconds": 45,
  "improvement_factor": 6.7,
  "value_proposition": "FlowSentinel detected issues 6.7x faster than manual monitoring, saving 11.25 hours of work"
}
```

**Value Metrics:**
- 💰 **Time Saved** - Each automated action saves ~15 minutes
- ⚡ **Speed** - 6.7x faster issue detection than manual monitoring
- 🤖 **Automation** - Actions taken without human intervention

**Example Use:**
```bash
curl http://localhost:8000/analytics/summary
```

---

### 2. **GET `/analytics/timeline`**

**Unified timeline of events and actions.**

**Response:**
```json
{
  "timeline": [
    {
      "type": "action",
      "id": "act_123",
      "timestamp": "2025-11-22T15:30:00",
      "action_type": "notify_user",
      "status": "sent",
      "team_id": "team_456",
      "payload_preview": "{\"message\": \"Backend blocked on design schema\"}"
    },
    {
      "type": "event",
      "id": "evt_789",
      "timestamp": "2025-11-22T15:25:00",
      "source": "slack",
      "event_type": "message",
      "processed": true,
      "team_id": "team_456",
      "data_preview": "{\"channel\": \"#engineering\", \"user\": \"alice\"}"
    }
  ],
  "total_items": 50,
  "time_range": {
    "oldest": "2025-11-22T10:00:00",
    "newest": "2025-11-22T15:30:00"
  }
}
```

**Features:**
- 📅 Chronological order (newest first)
- 🔀 Merged events and actions
- 📊 Limited to 50 most recent items

---

### 3. **GET `/analytics/risk-score`**

**Real-time project risk assessment (0-100).**

**Risk Algorithm:**
- Base score: 0
- +15 points per active blocker
- +10 points per identified risk
- +30 points if status is RED
- +15 points if status is YELLOW
- Cap at 100

**Response:**
```json
{
  "risk_score": 55,
  "level": "HIGH",
  "message": "⚠️  High risk level (55/100) - Address issues promptly",
  "factors": {
    "blockers": 2,
    "blocker_penalty": 30,
    "risks": 1,
    "risk_penalty": 10,
    "status": "YELLOW",
    "status_penalty": 15
  },
  "recommendations": [
    "🚨 Address 2 active blockers immediately",
    "⚠️  Mitigate 1 identified risks before they become blockers",
    "🟡 Project status is YELLOW - increase monitoring"
  ],
  "last_updated": "2025-11-22T15:30:00"
}
```

**Risk Levels:**
- 🔴 **CRITICAL** (75-100) - Immediate action required
- 🟠 **HIGH** (50-74) - Address issues promptly
- 🟡 **MODERATE** (25-49) - Monitor closely
- 🟢 **LOW** (0-24) - Project is healthy

---

### 4. **GET `/analytics/velocity`**

**Team productivity and velocity metrics.**

**Response:**
```json
{
  "completed_last_24h": 5,
  "completed_last_7d": 28,
  "completed_previous_7d": 22,
  "average_completion_time_hours": 24,
  "blockers_current": 2,
  "blockers_per_week": 2.0,
  "velocity_trend": "increasing",
  "velocity_trend_emoji": "📈",
  "velocity_score": 75.0,
  "insights": {
    "message": "📈 Team velocity is increasing",
    "weekly_throughput": "28 items completed this week",
    "daily_average": 4.0,
    "blocker_impact": "2 active blockers affecting velocity"
  }
}
```

**Velocity Trends:**
- 📈 **Increasing** - Completing >10% more than last week
- ➡️  **Stable** - Within 10% of last week
- 📉 **Decreasing** - Completing <10% less than last week

---

### 5. **GET `/analytics/trends`**

**Historical trends and patterns.**

**Response:**
```json
{
  "events_per_day": {
    "2025-11-22": 45,
    "2025-11-21": 38,
    "2025-11-20": 52,
    "2025-11-19": 41,
    "2025-11-18": 35,
    "2025-11-17": 29,
    "2025-11-16": 33
  },
  "status_history": [
    {
      "timestamp": "2025-11-22T15:00:00",
      "status": "YELLOW",
      "blockers_count": 2,
      "risks_count": 3
    },
    {
      "timestamp": "2025-11-21T15:00:00",
      "status": "GREEN",
      "blockers_count": 0,
      "risks_count": 1
    }
  ],
  "trends": {
    "event_activity": "increasing",
    "project_health": "deteriorating"
  },
  "insights": [
    "Event activity is increasing over the last week",
    "Project health is deteriorating"
  ]
}
```

**Trend Indicators:**
- **Event Activity** - increasing/stable/decreasing
- **Project Health** - improving/stable/deteriorating

---

### 6. **GET `/analytics/health`**

**Overall system health score (0-100).**

**Health Components:**
- **Recent Activity** (0-30 points) - Events in last hour
- **Processing Rate** (0-25 points) - % of events processed
- **Action Rate** (0-25 points) - Actions taken in last day
- **Project Status** (0-20 points) - Current project health

**Response:**
```json
{
  "health_score": 82,
  "status": "HEALTHY",
  "status_emoji": "🟢",
  "message": "🟢 System is healthy (82/100)",
  "factors": {
    "recent_activity_score": 27.0,
    "recent_events_count": 9,
    "processing_score": 24.2,
    "processing_rate_percent": 96.7,
    "action_rate_score": 22.0,
    "recent_actions_count": 11,
    "status_score": 20.0,
    "project_status": "GREEN"
  },
  "recommendations": [
    "✅ Excellent system health - keep up the great work!"
  ],
  "timestamp": "2025-11-22T15:30:00"
}
```

**Health Status:**
- 🟢 **HEALTHY** (80-100) - System performing optimally
- 🟡 **DEGRADED** (50-79) - Some issues detected
- 🔴 **CRITICAL** (0-49) - Immediate attention needed

---

## 📊 Metrics Explained

### **Time Saved Calculation**

```
Time Saved = Actions Taken × 15 minutes per action

Example:
- 45 automated actions
- 45 × 15 = 675 minutes saved
- 675 ÷ 60 = 11.25 hours saved
- 11.25 ÷ 8 = 1.41 workdays saved
```

### **Improvement Factor**

```
Improvement Factor = Manual Detection Time / AI Detection Time

Manual: ~5 minutes (30-minute check intervals)
AI: ~45 seconds
Factor: 300 / 45 = 6.7x faster
```

### **Risk Score Formula**

```python
risk_score = min(
    (blockers × 15) + (risks × 10) + status_penalty,
    100  # Cap at 100
)

status_penalty = {
    "RED": 30,
    "YELLOW": 15,
    "GREEN": 0
}
```

### **Health Score Formula**

```python
health_score = min(
    recent_activity_score +    # 0-30
    processing_score +         # 0-25
    action_rate_score +        # 0-25
    status_score,              # 0-20
    100  # Total
)
```

---

## 🎯 Use Cases

### **1. Executive Dashboard**
```bash
# Show value metrics
curl http://localhost:8000/analytics/summary

# Display:
# - Time saved: 11.25 hours
# - Improvement: 6.7x faster
# - Cost savings: $450 (at $40/hour)
```

### **2. Project Manager View**
```bash
# Check risk and velocity
curl http://localhost:8000/analytics/risk-score
curl http://localhost:8000/analytics/velocity

# Make decisions based on:
# - Current risk level
# - Team velocity trend
# - Blocker count
```

### **3. Operations Monitoring**
```bash
# Monitor system health
curl http://localhost:8000/analytics/health

# Alert if health_score < 50
# Check recommendations
```

### **4. Trend Analysis**
```bash
# View historical patterns
curl http://localhost:8000/analytics/trends

# Identify:
# - Activity patterns
# - Health trends
# - Predictive signals
```

### **5. Real-time Timeline**
```bash
# See recent activity
curl http://localhost:8000/analytics/timeline

# Track:
# - Event ingestion
# - Action execution
# - System flow
```

---

## 🚀 Quick Start

### **Start Server:**
```bash
python src/main.py
```

### **Test All Endpoints:**
```bash
python tests/test_analytics.py
```

### **API Documentation:**
```
http://localhost:8000/docs
```

Navigate to "Analytics" section for interactive testing.

---

## 📈 Example Dashboard Data

```json
{
  "kpis": {
    "time_saved_today": "2.5 hours",
    "current_risk_score": "25/100 (LOW)",
    "team_velocity": "📈 Increasing",
    "system_health": "🟢 HEALTHY (85/100)"
  },
  "alerts": [
    "2 blockers detected - Review immediately",
    "Velocity increased 15% this week"
  ],
  "recommendations": [
    "Continue current monitoring practices",
    "Review blocker #1: Backend waiting on design"
  ]
}
```

---

## 🔗 Integration Examples

### **Python Client:**
```python
import requests

# Get summary
response = requests.get("http://localhost:8000/analytics/summary")
data = response.json()

print(f"Time saved: {data['estimated_time_saved_hours']} hours")
print(f"Improvement: {data['improvement_factor']}x")
```

### **JavaScript/React:**
```javascript
fetch('http://localhost:8000/analytics/health')
  .then(res => res.json())
  .then(data => {
    console.log(`Health: ${data.health_score}/100`);
    console.log(`Status: ${data.status}`);
  });
```

### **cURL:**
```bash
# Get all analytics
curl http://localhost:8000/analytics/summary | jq
curl http://localhost:8000/analytics/risk-score | jq
curl http://localhost:8000/analytics/velocity | jq
curl http://localhost:8000/analytics/trends | jq
curl http://localhost:8000/analytics/health | jq
```

---

## 📝 Notes

- All timestamps are in ISO 8601 format (UTC)
- Scores are integers (0-100)
- Percentages are floats (0.0-100.0)
- All endpoints return JSON
- No authentication required (add in production)

---

**Need help?** Check the [main README](../README.md) or visit `/docs` for interactive API!

# Intelligence Endpoints Documentation

AI-powered predictions, recommendations, and insights for FlowSentinel.

## Overview

The Intelligence system uses statistical analysis and historical event data to provide:
- **Deadline Risk Predictions** - Forecast likelihood of deadline slips
- **Bottleneck Detection** - Identify areas likely to become blockers
- **AI Recommendations** - Priority-based action items
- **Team Health Scoring** - 0-100 health score with letter grade
- **Pattern Insights** - Discover trends, anomalies, and correlations
- **7-Day Forecasting** - Project future team performance

## Endpoints

### 1. Predict Deadline Risk

```bash
GET /intelligence/predict-deadline-risk
```

Analyzes velocity, blocker rate, and historical data to predict deadline slip probability.

**Response:**
```json
{
  "prediction": "LOW",
  "confidence": 0.90,
  "message": "Low risk - project on track",
  "factors": {
    "velocity": 3.2,
    "blocker_rate": 0.15,
    "risk_score": 15.0,
    "total_events": 45
  },
  "recommendations": [
    "Maintain current pace",
    "Continue regular check-ins",
    "Watch for emerging risks"
  ],
  "timestamp": "2025-01-15T10:00:00"
}
```

**Risk Levels:**
- **HIGH** (risk_score > 50): Critical risk of deadline slip
- **MODERATE** (risk_score 25-50): Monitor closely
- **LOW** (risk_score < 25): Project on track

**Risk Score Calculation:**
```
risk_score = (blocker_rate × 100) - (velocity × 10)
```

---

### 2. Predict Bottlenecks

```bash
GET /intelligence/predict-bottlenecks
```

Identifies areas likely to become bottlenecks based on historical patterns.

**Response:**
```json
[
  {
    "area": "code_review",
    "probability": 0.75,
    "average_resolution_time": 24.5,
    "recent_occurrences": 12,
    "recommendation": "Add more reviewers or automate checks"
  },
  {
    "area": "testing",
    "probability": 0.60,
    "average_resolution_time": 18.0,
    "recent_occurrences": 8,
    "recommendation": "Increase testing resources"
  }
]
```

**Detection Logic:**
- Analyzes event patterns over last 7 days
- Identifies areas with frequent blocker events
- Calculates probability based on occurrence frequency
- Estimates average resolution time

---

### 3. Generate Recommendations

```bash
POST /intelligence/recommendations
```

Generates priority-based action recommendations based on current project state.

**Response:**
```json
[
  {
    "priority": 1,
    "action": "Extend deadline or reduce scope",
    "reason": "High blocker rate (45%)",
    "estimated_impact": "Reduce team stress, improve quality",
    "affected_areas": ["project_management", "scope"]
  },
  {
    "priority": 2,
    "action": "Schedule design review meeting",
    "reason": "Design is blocking 3 features",
    "estimated_impact": "Unblock 3 features, reduce risk by 40%",
    "affected_areas": ["design", "frontend", "backend"]
  }
]
```

**Priority Levels:**
- **1**: Critical - Immediate action required
- **2**: High - Action needed within 24 hours
- **3**: Medium - Action needed this week
- **4**: Low - Monitor and plan
- **5**: Info - Good to know

---

### 4. Team Health Score

```bash
GET /intelligence/team-health
```

Calculates comprehensive team health score (0-100) with letter grade.

**Response:**
```json
{
  "health_score": 82,
  "grade": "B",
  "strengths": [
    "High velocity - team is productive",
    "Low blocker rate - smooth execution",
    "Strong communication"
  ],
  "weaknesses": [
    "Low completion rate"
  ],
  "recommendations": [
    "Focus on finishing in-progress work"
  ],
  "component_scores": {
    "velocity": 35.0,
    "blockers": 28.0,
    "communication": 18.0,
    "completion": 7.0
  }
}
```

**Score Components:**
- **Velocity** (0-40 pts): Completions per day × 10
- **Blockers** (0-30 pts): 30 - (blocker_rate × 100)
- **Communication** (0-20 pts): Communication events ÷ 2
- **Completion** (0-10 pts): Completion rate × 10

**Grades:**
- **A**: 90-100 (Excellent)
- **B**: 80-89 (Good)
- **C**: 70-79 (Average)
- **D**: 60-69 (Below Average)
- **F**: 0-59 (Poor)

---

### 5. Discover Insights

```bash
GET /intelligence/insights
```

Discovers patterns, anomalies, trends, and correlations in event data.

**Response:**
```json
{
  "patterns_detected": [
    "Code review bottleneck pattern: High activity Mon-Wed, drops Thu-Fri",
    "Testing blockers increase 2 days before deadline",
    "Communication spike precedes successful releases"
  ],
  "anomalies": [
    "Unusual blocker spike on 2025-01-10 (400% above average)",
    "Zero communication events on 2025-01-12 (holiday?)"
  ],
  "trends": {
    "event_volume": {
      "direction": "increasing",
      "slope": 0.15,
      "description": "Event volume trending upward"
    },
    "blocker_frequency": {
      "direction": "stable",
      "slope": 0.02,
      "description": "Blocker frequency stable"
    }
  },
  "correlations": [
    {
      "factor1": "high_communication",
      "factor2": "low_blockers",
      "strength": "strong",
      "description": "More communication correlates with fewer blockers"
    }
  ]
}
```

---

### 6. Forecast Next 7 Days

```bash
GET /intelligence/forecast
```

Projects team performance over the next 7 days using trend analysis.

**Response:**
```json
{
  "forecast_days": [
    {
      "date": "2025-01-16",
      "expected_completions": 3,
      "likely_blockers": 1,
      "risk_level": "LOW",
      "confidence": 0.75
    },
    {
      "date": "2025-01-17",
      "expected_completions": 3,
      "likely_blockers": 1,
      "risk_level": "LOW",
      "confidence": 0.72
    }
  ],
  "overall_trend": "stable",
  "key_insights": [
    "Velocity expected to remain steady at ~3 completions/day",
    "Blocker rate predicted to stay below 20%",
    "Weekend may see reduced activity",
    "Team on track to meet deadlines"
  ]
}
```

**Forecasting Algorithm:**
1. Calculate historical baseline (mean)
2. Calculate linear trend (slope)
3. Project: `forecast = baseline + (trend × days_ahead)`
4. Adjust confidence based on data variability

---

## Statistical Methods

### Linear Trend Calculation

```python
def calculate_simple_linear_trend(values: List[float]) -> float:
    """
    Calculate linear trend using simple regression.
    Returns slope of best-fit line.
    """
    n = len(values)
    x_values = list(range(n))
    x_mean = sum(x_values) / n
    y_mean = sum(values) / n
    
    numerator = sum((x - x_mean) * (y - y_mean) 
                    for x, y in zip(x_values, values))
    denominator = sum((x - x_mean) ** 2 for x in x_values)
    
    return numerator / denominator if denominator != 0 else 0.0
```

### Velocity Calculation

```python
velocity = completed_events / days
```

### Blocker Rate Calculation

```python
blocker_rate = blocker_events / total_events
```

---

## Usage Examples

### Check Project Risk

```python
import requests

response = requests.get('http://localhost:8000/intelligence/predict-deadline-risk')
prediction = response.json()

if prediction['prediction'] == 'HIGH':
    print(f"⚠️ High risk detected! Confidence: {prediction['confidence']}")
    for rec in prediction['recommendations']:
        print(f"  - {rec}")
```

### Monitor Team Health

```python
response = requests.get('http://localhost:8000/intelligence/team-health')
health = response.json()

print(f"Team Health: {health['health_score']}/100 ({health['grade']})")

if health['grade'] in ['D', 'F']:
    print("Action required:")
    for rec in health['recommendations']:
        print(f"  - {rec}")
```

### Get AI Recommendations

```python
response = requests.post('http://localhost:8000/intelligence/recommendations')
recommendations = response.json()

for rec in sorted(recommendations, key=lambda x: x['priority']):
    print(f"Priority {rec['priority']}: {rec['action']}")
    print(f"  Reason: {rec['reason']}")
    print(f"  Impact: {rec['estimated_impact']}")
```

---

## Configuration

The Intelligence system uses the last 7 days of data by default. This can be adjusted in the code:

```python
events = get_events_last_n_days(db, days=7)  # Change days here
```

---

## Testing

Run the comprehensive test suite:

```bash
python tests/test_intelligence.py
```

**Test Coverage:**
- ✅ Deadline risk prediction
- ✅ Bottleneck detection
- ✅ Recommendation generation
- ✅ Team health scoring
- ✅ Insight discovery
- ✅ 7-day forecasting
- ✅ Insufficient data handling
- ✅ Confidence score validation
- ✅ Priority ordering
- ✅ Statistical accuracy

---

## Integration

The Intelligence endpoints are automatically integrated into the main FastAPI app:

```python
from src.intelligence_endpoints import router as intelligence_router
app.include_router(intelligence_router, prefix="/intelligence", tags=["intelligence"])
```

---

## Best Practices

1. **Data Quality**: Ensure consistent event ingestion for accurate predictions
2. **Minimum Data**: System works with minimal data but improves with more history
3. **Regular Monitoring**: Check team health and deadline risk daily
4. **Act on Recommendations**: AI recommendations are priority-ordered for action
5. **Trend Analysis**: Use insights to identify long-term patterns
6. **Confidence Scores**: Higher confidence indicates more reliable predictions

---

## Limitations

- **Historical Data Required**: Predictions improve with more data (minimum 7 days recommended)
- **Simple Statistics**: Uses linear trends, not ML models (by design for simplicity)
- **7-Day Window**: Currently analyzes last 7 days (adjustable)
- **No External Data**: Only uses FlowSentinel event data

---

## Future Enhancements

- [ ] Configurable time windows (14 days, 30 days)
- [ ] ML model integration for advanced predictions
- [ ] Real-time anomaly detection
- [ ] Custom recommendation rules
- [ ] Historical accuracy tracking
- [ ] A/B testing for recommendation effectiveness

---

## See Also

- [Analytics Documentation](./ANALYTICS.md)
- [Webhook Documentation](./WEBHOOKS.md)
- [API Documentation](./API_DOCS.md)

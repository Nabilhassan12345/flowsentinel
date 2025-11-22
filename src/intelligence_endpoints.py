"""
Intelligence Endpoints for FlowSentinel
AI-powered predictions, recommendations, and insights.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import statistics
import json

try:
    from .database import get_db
    from .models import EventDB, ProjectStateDB, ActionDB, QAHistoryDB
except ImportError:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))
    from database import get_db
    from models import EventDB, ProjectStateDB, ActionDB, QAHistoryDB


# ============================================================
# Pydantic Models
# ============================================================

class PredictionResponse(BaseModel):
    """Response model for predictions."""
    prediction: str = Field(..., description="Prediction level: HIGH, MODERATE, or LOW")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score (0-1)")
    message: str = Field(..., description="Human-readable prediction message")
    factors: Dict[str, Any] = Field(..., description="Factors contributing to prediction")
    recommendations: List[str] = Field(..., description="Actionable recommendations")
    timestamp: str = Field(..., description="When prediction was made")

    class Config:
        json_schema_extra = {
            "example": {
                "prediction": "HIGH",
                "confidence": 0.85,
                "message": "High risk of deadline slip detected",
                "factors": {
                    "velocity": 2.5,
                    "blocker_rate": 0.45,
                    "risk_score": 70
                },
                "recommendations": [
                    "Schedule daily standups",
                    "Identify and remove blockers immediately"
                ],
                "timestamp": "2025-11-22T10:00:00"
            }
        }


class BottleneckPrediction(BaseModel):
    """Predicted bottleneck."""
    area: str = Field(..., description="Area where bottleneck will occur")
    probability: float = Field(..., ge=0.0, le=1.0, description="Probability (0-1)")
    average_resolution_time: float = Field(..., description="Average time to resolve (hours)")
    recent_occurrences: int = Field(..., description="Recent occurrence count")
    recommendation: str = Field(..., description="How to prevent/mitigate")


class RecommendationResponse(BaseModel):
    """AI-powered recommendation."""
    priority: int = Field(..., ge=1, le=5, description="Priority level (1=highest)")
    action: str = Field(..., description="Recommended action")
    reason: str = Field(..., description="Why this is recommended")
    estimated_impact: str = Field(..., description="Expected impact")
    affected_areas: List[str] = Field(..., description="Areas that will be affected")

    class Config:
        json_schema_extra = {
            "example": {
                "priority": 1,
                "action": "Schedule design review meeting",
                "reason": "Design is blocking 3 features",
                "estimated_impact": "Unblock 3 features, reduce risk by 40%",
                "affected_areas": ["design", "frontend", "backend"]
            }
        }


class TeamHealthResponse(BaseModel):
    """Team health assessment."""
    health_score: int = Field(..., ge=0, le=100, description="Overall health score")
    grade: str = Field(..., description="Letter grade (A/B/C/D/F)")
    strengths: List[str] = Field(..., description="Team strengths")
    weaknesses: List[str] = Field(..., description="Areas needing improvement")
    recommendations: List[str] = Field(..., description="Improvement recommendations")
    component_scores: Dict[str, float] = Field(..., description="Individual component scores")


class InsightResponse(BaseModel):
    """Discovered insights and patterns."""
    patterns_detected: List[str] = Field(..., description="Detected patterns")
    anomalies: List[str] = Field(..., description="Unusual events or behaviors")
    trends: Dict[str, str] = Field(..., description="Increasing/decreasing metrics")
    correlations: List[str] = Field(..., description="Discovered correlations")


class DailyForecast(BaseModel):
    """Forecast for a single day."""
    date: str
    expected_completions: int
    likely_blockers: int
    risk_level: str
    confidence: float


class ForecastResponse(BaseModel):
    """7-day forecast."""
    forecast_days: List[DailyForecast]
    overall_trend: str
    key_insights: List[str]


# ============================================================
# Router Setup
# ============================================================

router = APIRouter(prefix="/intelligence", tags=["AI Intelligence"])


# ============================================================
# Helper Functions
# ============================================================

def calculate_simple_linear_trend(values: List[float]) -> float:
    """
    Calculate simple linear trend (slope).
    Positive = increasing, Negative = decreasing.
    """
    if len(values) < 2:
        return 0.0
    
    n = len(values)
    x_values = list(range(n))
    
    # Calculate means
    x_mean = statistics.mean(x_values)
    y_mean = statistics.mean(values)
    
    # Calculate slope
    numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, values))
    denominator = sum((x - x_mean) ** 2 for x in x_values)
    
    if denominator == 0:
        return 0.0
    
    return numerator / denominator


def get_events_last_n_days(db: Session, days: int = 7) -> List[EventDB]:
    """Get events from the last N days."""
    cutoff_date = datetime.now() - timedelta(days=days)
    return db.query(EventDB).filter(
        EventDB.created_at >= cutoff_date
    ).order_by(EventDB.created_at.desc()).all()


def calculate_velocity(events: List[EventDB], days: int = 7) -> float:
    """Calculate team velocity (completions per day)."""
    completed = sum(1 for e in events if 'complet' in json.dumps(e.data).lower() or 'done' in json.dumps(e.data).lower())
    return completed / max(days, 1)


def calculate_blocker_rate(events: List[EventDB]) -> float:
    """Calculate rate of blocking events."""
    if not events:
        return 0.0
    blockers = sum(1 for e in events if 'block' in json.dumps(e.data).lower() or e.type == 'blocker_detected')
    return blockers / len(events)


# ============================================================
# Endpoints
# ============================================================

@router.get("/predict-deadline-risk", response_model=PredictionResponse)
def predict_deadline_risk(db: Session = Depends(get_db)):
    """
    Predict likelihood of deadline slips.
    
    Uses velocity, blocker rate, and historical data to predict
    whether upcoming deadlines are at risk.
    """
    # Get recent events
    events = get_events_last_n_days(db, days=7)
    
    if not events:
        return PredictionResponse(
            prediction="LOW",
            confidence=0.50,
            message="Insufficient data for prediction",
            factors={
                "velocity": 0.0,
                "blocker_rate": 0.0,
                "risk_score": 0.0,
                "total_events": 0,
                "data_points": 0
            },
            recommendations=["Ingest more events to enable predictions"],
            timestamp=datetime.now().isoformat()
        )
    
    # Calculate metrics
    velocity = calculate_velocity(events, days=7)
    blocker_rate = calculate_blocker_rate(events)
    
    # Calculate risk score
    risk_score = (blocker_rate * 100) - (velocity * 10)
    
    # Determine prediction
    if risk_score > 50:
        prediction = "HIGH"
        confidence = 0.85
        message = "High risk of deadline slip detected"
        recommendations = [
            "Schedule daily standups to track progress",
            "Identify and remove blockers immediately",
            "Consider extending deadline or reducing scope",
            "Add more resources to critical path items"
        ]
    elif risk_score > 25:
        prediction = "MODERATE"
        confidence = 0.70
        message = "Moderate risk - monitor closely"
        recommendations = [
            "Increase communication frequency",
            "Address blockers proactively",
            "Review scope and priorities"
        ]
    else:
        prediction = "LOW"
        confidence = 0.90
        message = "Low risk - project on track"
        recommendations = [
            "Maintain current pace",
            "Continue regular check-ins",
            "Watch for emerging risks"
        ]
    
    return PredictionResponse(
        prediction=prediction,
        confidence=confidence,
        message=message,
        factors={
            "velocity": round(velocity, 2),
            "blocker_rate": round(blocker_rate, 2),
            "risk_score": round(risk_score, 2),
            "total_events": len(events),
            "analysis_period_days": 7
        },
        recommendations=recommendations,
        timestamp=datetime.now().isoformat()
    )


@router.get("/predict-bottlenecks", response_model=List[BottleneckPrediction])
def predict_bottlenecks(db: Session = Depends(get_db)):
    """
    Predict where bottlenecks will occur.
    
    Analyzes historical patterns to identify areas most likely
    to become bottlenecks.
    """
    events = get_events_last_n_days(db, days=14)
    
    if not events:
        return []
    
    # Analyze blocker sources
    bottleneck_areas = {}
    
    for event in events:
        data_str = json.dumps(event.data).lower()
        
        # Detect area
        area = None
        if 'design' in data_str:
            area = "design"
        elif 'backend' in data_str or 'api' in data_str:
            area = "backend"
        elif 'frontend' in data_str or 'ui' in data_str:
            area = "frontend"
        elif 'review' in data_str or 'pr' in data_str:
            area = "code_review"
        elif 'test' in data_str or 'qa' in data_str:
            area = "testing"
        elif 'deploy' in data_str:
            area = "deployment"
        
        if area and ('block' in data_str or 'delay' in data_str or 'waiting' in data_str):
            if area not in bottleneck_areas:
                bottleneck_areas[area] = {
                    'count': 0,
                    'times': []
                }
            bottleneck_areas[area]['count'] += 1
            # Simulate resolution time (in real system, calculate from event pairs)
            bottleneck_areas[area]['times'].append(4.5)  # hours
    
    # Build predictions
    predictions = []
    total_blockers = sum(data['count'] for data in bottleneck_areas.values())
    
    for area, data in sorted(bottleneck_areas.items(), key=lambda x: x[1]['count'], reverse=True):
        probability = min(data['count'] / max(total_blockers, 1), 1.0)
        avg_time = statistics.mean(data['times']) if data['times'] else 0
        
        # Generate recommendations
        recommendations = {
            "design": "Allocate dedicated design time, create design system",
            "backend": "Review API architecture, add backend resources",
            "frontend": "Conduct code review, improve component reusability",
            "code_review": "Assign additional reviewers, set review SLAs",
            "testing": "Automate tests, add QA resources",
            "deployment": "Improve CI/CD pipeline, automate deployment"
        }
        
        predictions.append(BottleneckPrediction(
            area=area,
            probability=round(probability, 2),
            average_resolution_time=round(avg_time, 1),
            recent_occurrences=data['count'],
            recommendation=recommendations.get(area, "Monitor and address proactively")
        ))
    
    return predictions[:5]  # Top 5


@router.post("/recommendations", response_model=List[RecommendationResponse])
def generate_recommendations(db: Session = Depends(get_db)):
    """
    Generate AI-powered recommendations.
    
    Analyzes current state and generates prioritized,
    actionable recommendations.
    """
    # Get current state
    latest_state = db.query(ProjectStateDB).order_by(ProjectStateDB.created_at.desc()).first()
    events = get_events_last_n_days(db, days=7)
    
    recommendations = []
    
    # Check for blockers
    if latest_state and latest_state.blockers:
        blockers = json.loads(latest_state.blockers) if isinstance(latest_state.blockers, str) else latest_state.blockers
        
        for blocker in blockers[:3]:  # Top 3 blockers
            blocker_desc = blocker.get('description', '') if isinstance(blocker, dict) else str(blocker)
            
            if 'design' in blocker_desc.lower():
                recommendations.append(RecommendationResponse(
                    priority=1,
                    action="Schedule design review meeting",
                    reason=f"Design blocker: {blocker_desc}",
                    estimated_impact="Unblock features, reduce risk by 30-40%",
                    affected_areas=["design", "frontend", "backend"]
                ))
            elif 'review' in blocker_desc.lower() or 'pr' in blocker_desc.lower():
                recommendations.append(RecommendationResponse(
                    priority=2,
                    action="Assign additional code reviewer",
                    reason=f"Review bottleneck: {blocker_desc}",
                    estimated_impact="Speed up PR merges by 50%",
                    affected_areas=["code_review", "development"]
                ))
    
    # Check velocity
    velocity = calculate_velocity(events, days=7)
    if velocity < 2.0:
        recommendations.append(RecommendationResponse(
            priority=3,
            action="Identify and remove process blockers",
            reason=f"Low velocity detected ({velocity:.1f} completions/day)",
            estimated_impact="Increase throughput by 30-50%",
            affected_areas=["process", "team_efficiency"]
        ))
    
    # Check deadline risk
    blocker_rate = calculate_blocker_rate(events)
    if blocker_rate > 0.3:
        recommendations.append(RecommendationResponse(
            priority=1,
            action="Extend deadline or reduce scope",
            reason=f"High blocker rate ({blocker_rate*100:.0f}%)",
            estimated_impact="Reduce team stress, improve quality",
            affected_areas=["project_management", "scope"]
        ))
    
    # Check communication
    slack_events = [e for e in events if e.source == 'slack']
    if len(slack_events) < 10:
        recommendations.append(RecommendationResponse(
            priority=4,
            action="Increase team communication",
            reason="Low communication activity detected",
            estimated_impact="Improve collaboration and alignment",
            affected_areas=["communication", "team_coordination"]
        ))
    
    # Sort by priority
    recommendations.sort(key=lambda x: x.priority)
    
    return recommendations if recommendations else [
        RecommendationResponse(
            priority=5,
            action="Continue current practices",
            reason="No critical issues detected",
            estimated_impact="Maintain project health",
            affected_areas=["all"]
        )
    ]


@router.get("/team-health", response_model=TeamHealthResponse)
def calculate_team_health(db: Session = Depends(get_db)):
    """
    Calculate comprehensive team health score.
    
    Evaluates velocity, blockers, communication, and completion rate
    to produce an overall health score.
    """
    events = get_events_last_n_days(db, days=7)
    
    if not events:
        return TeamHealthResponse(
            health_score=50,
            grade="C",
            strengths=[],
            weaknesses=["Insufficient data"],
            recommendations=["Start tracking events"],
            component_scores={
                "velocity": 0.0,
                "blockers": 0.0,
                "communication": 0.0,
                "completion": 0.0
            }
        )
    
    # Calculate component scores
    
    # 1. Velocity score (0-40 points)
    velocity = calculate_velocity(events, days=7)
    velocity_score = min(velocity * 10, 40)
    
    # 2. Blocker score (0-30 points, negative impact)
    blocker_rate = calculate_blocker_rate(events)
    blocker_score = max(30 - (blocker_rate * 100), 0)
    
    # 3. Communication score (0-20 points)
    comm_events = [e for e in events if e.source == 'slack']
    comm_score = min(len(comm_events) / 2, 20)
    
    # 4. Completion rate (0-10 points)
    completed = sum(1 for e in events if 'complet' in json.dumps(e.data).lower())
    completion_rate = completed / max(len(events), 1)
    completion_score = completion_rate * 10
    
    # Calculate total
    health_score = int(velocity_score + blocker_score + comm_score + completion_score)
    
    # Determine grade
    if health_score >= 90:
        grade = "A"
    elif health_score >= 80:
        grade = "B"
    elif health_score >= 70:
        grade = "C"
    elif health_score >= 60:
        grade = "D"
    else:
        grade = "F"
    
    # Identify strengths and weaknesses
    strengths = []
    weaknesses = []
    recommendations = []
    
    if velocity_score > 30:
        strengths.append("High velocity - team is productive")
    elif velocity_score < 15:
        weaknesses.append("Low velocity")
        recommendations.append("Review process bottlenecks")
    
    if blocker_score > 20:
        strengths.append("Low blocker rate - smooth execution")
    else:
        weaknesses.append("High blocker rate")
        recommendations.append("Prioritize removing blockers")
    
    if comm_score > 15:
        strengths.append("Strong communication")
    else:
        weaknesses.append("Low communication activity")
        recommendations.append("Increase team sync meetings")
    
    if completion_score > 7:
        strengths.append("Good completion rate")
    else:
        weaknesses.append("Low completion rate")
        recommendations.append("Focus on finishing in-progress work")
    
    return TeamHealthResponse(
        health_score=health_score,
        grade=grade,
        strengths=strengths,
        weaknesses=weaknesses,
        recommendations=recommendations if recommendations else ["Maintain current practices"],
        component_scores={
            "velocity": round(velocity_score, 1),
            "blockers": round(blocker_score, 1),
            "communication": round(comm_score, 1),
            "completion": round(completion_score, 1)
        }
    )


@router.get("/insights", response_model=InsightResponse)
def discover_insights(db: Session = Depends(get_db)):
    """
    Discover patterns, anomalies, and insights.
    
    Uses statistical analysis to find interesting patterns
    in the data.
    """
    events = get_events_last_n_days(db, days=14)
    
    patterns = []
    anomalies = []
    trends = {}
    correlations = []
    
    if not events:
        return InsightResponse(
            patterns_detected=["Insufficient data for pattern detection"],
            anomalies=[],
            trends={},
            correlations=[]
        )
    
    # Detect patterns
    
    # Pattern: Peak activity times
    hours = {}
    for event in events:
        hour = event.created_at.hour
        hours[hour] = hours.get(hour, 0) + 1
    
    if hours:
        peak_hour = max(hours.items(), key=lambda x: x[1])[0]
        patterns.append(f"Peak activity occurs around {peak_hour}:00")
    
    # Pattern: Event clustering
    sources = {}
    for event in events:
        sources[event.source] = sources.get(event.source, 0) + 1
    
    dominant_source = max(sources.items(), key=lambda x: x[1])[0] if sources else None
    if dominant_source:
        patterns.append(f"Most events come from {dominant_source} ({sources[dominant_source]} events)")
    
    # Detect anomalies
    daily_counts = {}
    for event in events:
        day = event.created_at.date()
        daily_counts[day] = daily_counts.get(day, 0) + 1
    
    if len(daily_counts) >= 3:
        counts = list(daily_counts.values())
        avg = statistics.mean(counts)
        stdev = statistics.stdev(counts) if len(counts) > 1 else 0
        
        for day, count in daily_counts.items():
            if stdev > 0 and abs(count - avg) > 2 * stdev:
                anomalies.append(f"Unusual activity on {day}: {count} events (avg: {avg:.1f})")
    
    # Calculate trends
    if len(daily_counts) >= 3:
        sorted_days = sorted(daily_counts.items())
        counts = [count for _, count in sorted_days]
        
        trend_slope = calculate_simple_linear_trend(counts)
        
        if trend_slope > 0.5:
            trends["activity"] = "increasing"
        elif trend_slope < -0.5:
            trends["activity"] = "decreasing"
        else:
            trends["activity"] = "stable"
    
    # Detect correlations
    blocker_events = [e for e in events if 'block' in json.dumps(e.data).lower()]
    pr_events = [e for e in events if 'pr' in json.dumps(e.data).lower() or e.source == 'github']
    
    if len(blocker_events) > 2 and len(pr_events) > 2:
        correlations.append("Code review bottlenecks often lead to blockers")
    
    if len([e for e in events if e.source == 'slack']) > len(events) * 0.5:
        correlations.append("High communication activity correlates with active development")
    
    return InsightResponse(
        patterns_detected=patterns if patterns else ["No clear patterns detected yet"],
        anomalies=anomalies,
        trends=trends,
        correlations=correlations if correlations else ["Need more data for correlation analysis"]
    )


@router.get("/forecast", response_model=ForecastResponse)
def forecast_next_week(db: Session = Depends(get_db)):
    """
    Forecast next 7 days.
    
    Projects future activity based on historical trends.
    """
    events = get_events_last_n_days(db, days=14)
    
    if len(events) < 7:
        return ForecastResponse(
            forecast_days=[],
            overall_trend="insufficient_data",
            key_insights=["Need at least 7 days of data for forecasting"]
        )
    
    # Calculate historical averages
    velocity = calculate_velocity(events, days=14)
    blocker_rate = calculate_blocker_rate(events)
    
    # Calculate trend
    daily_counts = {}
    for event in events:
        day = event.created_at.date()
        daily_counts[day] = daily_counts.get(day, 0) + 1
    
    sorted_days = sorted(daily_counts.items())
    counts = [count for _, count in sorted_days]
    trend_slope = calculate_simple_linear_trend(counts)
    
    # Generate 7-day forecast
    forecast_days = []
    base_date = datetime.now().date()
    
    for i in range(7):
        forecast_date = base_date + timedelta(days=i+1)
        
        # Project completions (with trend adjustment)
        expected_completions = int(velocity + (trend_slope * i))
        expected_completions = max(0, expected_completions)
        
        # Project blockers
        likely_blockers = int(blocker_rate * 10)  # Assuming ~10 events per day
        
        # Determine risk level
        daily_risk_score = (blocker_rate * 100) - (velocity * 10)
        if daily_risk_score > 50:
            risk_level = "HIGH"
            confidence = 0.70
        elif daily_risk_score > 25:
            risk_level = "MODERATE"
            confidence = 0.75
        else:
            risk_level = "LOW"
            confidence = 0.80
        
        forecast_days.append(DailyForecast(
            date=forecast_date.isoformat(),
            expected_completions=expected_completions,
            likely_blockers=likely_blockers,
            risk_level=risk_level,
            confidence=round(confidence, 2)
        ))
    
    # Determine overall trend
    if trend_slope > 0.5:
        overall_trend = "improving"
    elif trend_slope < -0.5:
        overall_trend = "declining"
    else:
        overall_trend = "stable"
    
    # Generate insights
    key_insights = []
    key_insights.append(f"Current velocity: {velocity:.1f} completions/day")
    key_insights.append(f"Blocker rate: {blocker_rate*100:.0f}%")
    key_insights.append(f"Trend: {overall_trend}")
    
    if trend_slope > 0:
        key_insights.append("Activity is trending upward - good momentum")
    elif trend_slope < 0:
        key_insights.append("Activity declining - may need intervention")
    
    return ForecastResponse(
        forecast_days=forecast_days,
        overall_trend=overall_trend,
        key_insights=key_insights
    )


# ============================================================
# Export
# ============================================================

__all__ = ["router"]

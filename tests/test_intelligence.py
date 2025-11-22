"""
Tests for Intelligence Endpoints
AI-powered predictions and recommendations.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from src.main import app
from src.database import init_db, reset_db

# Initialize test database
reset_db()
init_db()

# Create test client
client = TestClient(app)


def setup_test_data():
    """Load simulation data for testing."""
    client.post("/simulation/run")
    client.post("/agent/run")


def test_predict_deadline_risk():
    """Test deadline risk prediction."""
    print("\n🧪 Test 1: Predict Deadline Risk")
    
    setup_test_data()
    
    response = client.get("/intelligence/predict-deadline-risk")
    
    assert response.status_code == 200
    data = response.json()
    
    # Check required fields
    assert "prediction" in data
    assert data["prediction"] in ["HIGH", "MODERATE", "LOW"]
    assert "confidence" in data
    assert 0 <= data["confidence"] <= 1
    assert "message" in data
    assert "factors" in data
    assert "recommendations" in data
    assert isinstance(data["recommendations"], list)
    
    print(f"✅ Prediction: {data['prediction']}")
    print(f"   Confidence: {data['confidence']}")
    print(f"   Risk Score: {data['factors']['risk_score']}")
    print(f"   Recommendations: {len(data['recommendations'])}")


def test_predict_bottlenecks():
    """Test bottleneck prediction."""
    print("\n🧪 Test 2: Predict Bottlenecks")
    
    response = client.get("/intelligence/predict-bottlenecks")
    
    assert response.status_code == 200
    bottlenecks = response.json()
    
    assert isinstance(bottlenecks, list)
    
    if bottlenecks:
        b = bottlenecks[0]
        assert "area" in b
        assert "probability" in b
        assert 0 <= b["probability"] <= 1
        assert "average_resolution_time" in b
        assert "recent_occurrences" in b
        assert "recommendation" in b
        
        print(f"✅ Found {len(bottlenecks)} potential bottlenecks")
        for bottleneck in bottlenecks[:3]:
            print(f"   - {bottleneck['area']}: {bottleneck['probability']*100:.0f}% ({bottleneck['recent_occurrences']} occurrences)")
    else:
        print("✅ No bottlenecks predicted (good!)")


def test_generate_recommendations():
    """Test recommendation generation."""
    print("\n🧪 Test 3: Generate Recommendations")
    
    response = client.post("/intelligence/recommendations")
    
    assert response.status_code == 200
    recommendations = response.json()
    
    assert isinstance(recommendations, list)
    assert len(recommendations) > 0
    
    for rec in recommendations:
        assert "priority" in rec
        assert 1 <= rec["priority"] <= 5
        assert "action" in rec
        assert "reason" in rec
        assert "estimated_impact" in rec
        assert "affected_areas" in rec
        assert isinstance(rec["affected_areas"], list)
    
    # Check priority ordering
    priorities = [r["priority"] for r in recommendations]
    assert priorities == sorted(priorities), "Recommendations should be sorted by priority"
    
    print(f"✅ Generated {len(recommendations)} recommendations")
    for rec in recommendations[:3]:
        print(f"   Priority {rec['priority']}: {rec['action']}")


def test_team_health():
    """Test team health calculation."""
    print("\n🧪 Test 4: Team Health")
    
    response = client.get("/intelligence/team-health")
    
    assert response.status_code == 200
    health = response.json()
    
    # Check required fields
    assert "health_score" in health
    assert 0 <= health["health_score"] <= 100
    assert "grade" in health
    assert health["grade"] in ["A", "B", "C", "D", "F"]
    assert "strengths" in health
    assert isinstance(health["strengths"], list)
    assert "weaknesses" in health
    assert isinstance(health["weaknesses"], list)
    assert "recommendations" in health
    assert isinstance(health["recommendations"], list)
    assert "component_scores" in health
    
    # Check component scores
    components = health["component_scores"]
    assert "velocity" in components
    assert "blockers" in components
    assert "communication" in components
    assert "completion" in components
    
    print(f"✅ Health Score: {health['health_score']}/100")
    print(f"   Grade: {health['grade']}")
    print(f"   Strengths: {len(health['strengths'])}")
    print(f"   Weaknesses: {len(health['weaknesses'])}")
    print(f"   Component Scores:")
    for component, score in components.items():
        print(f"      - {component}: {score}")


def test_insights():
    """Test insight discovery."""
    print("\n🧪 Test 5: Discover Insights")
    
    response = client.get("/intelligence/insights")
    
    assert response.status_code == 200
    insights = response.json()
    
    # Check required fields
    assert "patterns_detected" in insights
    assert isinstance(insights["patterns_detected"], list)
    assert "anomalies" in insights
    assert isinstance(insights["anomalies"], list)
    assert "trends" in insights
    assert isinstance(insights["trends"], dict)
    assert "correlations" in insights
    assert isinstance(insights["correlations"], list)
    
    print(f"✅ Patterns: {len(insights['patterns_detected'])}")
    for pattern in insights['patterns_detected'][:3]:
        print(f"   - {pattern}")
    
    print(f"   Anomalies: {len(insights['anomalies'])}")
    print(f"   Trends: {list(insights['trends'].keys())}")
    print(f"   Correlations: {len(insights['correlations'])}")


def test_forecast():
    """Test 7-day forecast."""
    print("\n🧪 Test 6: Forecast Next 7 Days")
    
    response = client.get("/intelligence/forecast")
    
    assert response.status_code == 200
    forecast = response.json()
    
    # Check required fields
    assert "forecast_days" in forecast
    assert isinstance(forecast["forecast_days"], list)
    assert len(forecast["forecast_days"]) <= 7
    assert "overall_trend" in forecast
    assert "key_insights" in forecast
    assert isinstance(forecast["key_insights"], list)
    
    # Check forecast days
    if forecast["forecast_days"]:
        day = forecast["forecast_days"][0]
        assert "date" in day
        assert "expected_completions" in day
        assert "likely_blockers" in day
        assert "risk_level" in day
        assert day["risk_level"] in ["HIGH", "MODERATE", "LOW"]
        assert "confidence" in day
        assert 0 <= day["confidence"] <= 1
        
        print(f"✅ Forecast: {len(forecast['forecast_days'])} days")
        print(f"   Trend: {forecast['overall_trend']}")
        print(f"   First day prediction:")
        print(f"      - Completions: {day['expected_completions']}")
        print(f"      - Blockers: {day['likely_blockers']}")
        print(f"      - Risk: {day['risk_level']}")
    else:
        print("✅ Insufficient data for forecast (expected for minimal data)")


def test_insufficient_data_handling():
    """Test endpoints handle insufficient data gracefully."""
    print("\n🧪 Test 7: Insufficient Data Handling")
    
    # Reset database (no data)
    reset_db()
    init_db()
    
    # All endpoints should still return 200 with appropriate messages
    response = client.get("/intelligence/predict-deadline-risk")
    assert response.status_code == 200
    data = response.json()
    assert data["prediction"] == "LOW"
    assert data["confidence"] == 0.50
    
    response = client.get("/intelligence/team-health")
    assert response.status_code == 200
    health = response.json()
    assert health["health_score"] == 50
    assert health["grade"] == "C"
    
    print("✅ All endpoints handle insufficient data gracefully")
    
    # Reload data for remaining tests
    setup_test_data()


def test_confidence_scores():
    """Test that confidence scores are reasonable."""
    print("\n🧪 Test 8: Confidence Scores")
    
    response = client.get("/intelligence/predict-deadline-risk")
    data = response.json()
    
    # Confidence should be within valid range
    assert 0 <= data["confidence"] <= 1
    
    # Confidence should be higher for clearer predictions (more data)
    if data["factors"]["total_events"] > 20:
        if data["prediction"] == "LOW" and data["factors"]["risk_score"] < 10:
            assert data["confidence"] >= 0.80
    
    print(f"✅ Confidence scores are appropriate")
    print(f"   Prediction: {data['prediction']}")
    print(f"   Confidence: {data['confidence']}")
    print(f"   Total Events: {data['factors']['total_events']}")


def test_recommendation_priorities():
    """Test recommendation priority logic."""
    print("\n🧪 Test 9: Recommendation Priorities")
    
    response = client.post("/intelligence/recommendations")
    recommendations = response.json()
    
    # High priority recommendations should come first
    priorities = [r["priority"] for r in recommendations]
    assert priorities == sorted(priorities)
    
    # Priority 1 should be for critical issues
    priority_1 = [r for r in recommendations if r["priority"] == 1]
    if priority_1:
        print(f"✅ Found {len(priority_1)} critical (priority 1) recommendations")
        for rec in priority_1:
            print(f"   - {rec['action']}")
    else:
        print("✅ No critical issues detected")


def test_statistical_calculations():
    """Test statistical accuracy."""
    print("\n🧪 Test 10: Statistical Calculations")
    
    response = client.get("/intelligence/predict-deadline-risk")
    data = response.json()
    
    factors = data["factors"]
    
    # Velocity should be non-negative
    assert factors["velocity"] >= 0
    
    # Blocker rate should be between 0 and 1
    assert 0 <= factors["blocker_rate"] <= 1
    
    # Risk score calculation
    expected_risk = (factors["blocker_rate"] * 100) - (factors["velocity"] * 10)
    assert abs(factors["risk_score"] - expected_risk) < 0.01
    
    print("✅ Statistical calculations are accurate")
    print(f"   Velocity: {factors['velocity']}")
    print(f"   Blocker Rate: {factors['blocker_rate']}")
    print(f"   Risk Score: {factors['risk_score']}")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🧪 INTELLIGENCE ENDPOINTS TEST SUITE")
    print("=" * 60)
    
    try:
        test_predict_deadline_risk()
        test_predict_bottlenecks()
        test_generate_recommendations()
        test_team_health()
        test_insights()
        test_forecast()
        test_insufficient_data_handling()
        test_confidence_scores()
        test_recommendation_priorities()
        test_statistical_calculations()
        
        print("\n" + "=" * 60)
        print("✅ ALL INTELLIGENCE TESTS PASSED!")
        print("=" * 60)
        print("\n📊 Test Summary:")
        print("   ✅ 10 test scenarios validated")
        print("   ✅ 6 AI endpoints tested")
        print("   ✅ Predictions: Deadline risk")
        print("   ✅ Predictions: Bottlenecks")
        print("   ✅ Recommendations: AI-powered")
        print("   ✅ Health: Team scoring")
        print("   ✅ Insights: Pattern detection")
        print("   ✅ Forecast: 7-day projection")
        print("\n🎉 AI Intelligence system production-ready!")
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        raise
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        raise

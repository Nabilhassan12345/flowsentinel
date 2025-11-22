"""
Test Analytics Endpoints

Validates all analytics endpoints and their calculations.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from src.main import app

# Create test client
client = TestClient(app)


def test_analytics_summary():
    """Test /analytics/summary endpoint."""
    print("=" * 60)
    print("TEST: Analytics Summary")
    print("=" * 60)
    
    response = client.get("/analytics/summary")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    data = response.json()
    
    # Check required fields
    required_fields = [
        "total_events_processed",
        "events_by_source",
        "actions_taken_automatically",
        "estimated_time_saved_minutes",
        "estimated_time_saved_hours",
        "blockers_detected",
        "average_detection_time_seconds",
        "improvement_factor",
    ]
    
    for field in required_fields:
        assert field in data, f"Missing field: {field}"
    
    print(f"✅ Total events: {data['total_events_processed']}")
    print(f"✅ Actions taken: {data['actions_taken_automatically']}")
    print(f"✅ Time saved: {data['estimated_time_saved_hours']} hours")
    print(f"✅ Blockers detected: {data['blockers_detected']}")
    print(f"✅ Improvement factor: {data['improvement_factor']}x")
    print()


def test_analytics_timeline():
    """Test /analytics/timeline endpoint."""
    print("=" * 60)
    print("TEST: Analytics Timeline")
    print("=" * 60)
    
    response = client.get("/analytics/timeline")
    assert response.status_code == 200
    
    data = response.json()
    assert "timeline" in data
    assert "total_items" in data
    assert "time_range" in data
    
    print(f"✅ Timeline items: {data['total_items']}")
    print(f"✅ Time range: {data['time_range']}")
    print()


def test_analytics_risk_score():
    """Test /analytics/risk-score endpoint."""
    print("=" * 60)
    print("TEST: Risk Score")
    print("=" * 60)
    
    response = client.get("/analytics/risk-score")
    assert response.status_code == 200
    
    data = response.json()
    assert "risk_score" in data
    assert "level" in data
    assert "message" in data
    assert "factors" in data
    assert "recommendations" in data
    
    print(f"✅ Risk score: {data['risk_score']}/100")
    print(f"✅ Level: {data['level']}")
    print(f"✅ Message: {data['message']}")
    print(f"✅ Recommendations: {len(data['recommendations'])}")
    print()


def test_analytics_velocity():
    """Test /analytics/velocity endpoint."""
    print("=" * 60)
    print("TEST: Velocity Metrics")
    print("=" * 60)
    
    response = client.get("/analytics/velocity")
    assert response.status_code == 200
    
    data = response.json()
    assert "completed_last_24h" in data
    assert "completed_last_7d" in data
    assert "velocity_trend" in data
    assert "velocity_score" in data
    
    print(f"✅ Completed (24h): {data['completed_last_24h']}")
    print(f"✅ Completed (7d): {data['completed_last_7d']}")
    print(f"✅ Trend: {data['velocity_trend']}")
    print(f"✅ Score: {data['velocity_score']}/100")
    print()


def test_analytics_trends():
    """Test /analytics/trends endpoint."""
    print("=" * 60)
    print("TEST: Trends")
    print("=" * 60)
    
    response = client.get("/analytics/trends")
    assert response.status_code == 200
    
    data = response.json()
    assert "events_per_day" in data
    assert "status_history" in data
    assert "trends" in data
    
    print(f"✅ Days tracked: {len(data['events_per_day'])}")
    print(f"✅ Status history: {len(data['status_history'])} records")
    print(f"✅ Event trend: {data['trends']['event_activity']}")
    print(f"✅ Health trend: {data['trends']['project_health']}")
    print()


def test_analytics_health():
    """Test /analytics/health endpoint."""
    print("=" * 60)
    print("TEST: System Health")
    print("=" * 60)
    
    response = client.get("/analytics/health")
    assert response.status_code == 200
    
    data = response.json()
    assert "health_score" in data
    assert "status" in data
    assert "factors" in data
    assert "recommendations" in data
    
    print(f"✅ Health score: {data['health_score']}/100")
    print(f"✅ Status: {data['status']}")
    print(f"✅ Message: {data['message']}")
    print(f"✅ Recommendations: {len(data['recommendations'])}")
    print()


def run_all_tests():
    """Run all analytics endpoint tests."""
    print("\n" + "=" * 60)
    print("🧪 ANALYTICS ENDPOINTS TESTS")
    print("=" * 60 + "\n")
    
    try:
        test_analytics_summary()
        test_analytics_timeline()
        test_analytics_risk_score()
        test_analytics_velocity()
        test_analytics_trends()
        test_analytics_health()
        
        print("=" * 60)
        print("✅ ALL ANALYTICS TESTS PASSED!")
        print("=" * 60)
        print("\n📊 Endpoints Validated:")
        print("   ✅ GET /analytics/summary")
        print("   ✅ GET /analytics/timeline")
        print("   ✅ GET /analytics/risk-score")
        print("   ✅ GET /analytics/velocity")
        print("   ✅ GET /analytics/trends")
        print("   ✅ GET /analytics/health")
        print("\n🎉 Analytics layer is ready!\n")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    run_all_tests()

"""
FlowSentinel v2.0 Integration Validation Script

This script validates that all features are properly integrated and working.
Run this after starting the server to ensure everything is operational.
"""

import sys
sys.path.insert(0, 'src')

from fastapi.testclient import TestClient
from src.main import app
from src.database import reset_db, init_db

def print_banner():
    print("\n" + "=" * 70)
    print("   FlowSentinel v2.0 - Integration Validation")
    print("=" * 70 + "\n")

def print_section(title):
    print(f"\n{'─' * 70}")
    print(f"  {title}")
    print('─' * 70)

def validate_feature(name, test_func):
    """Run a validation test and report results."""
    try:
        result = test_func()
        if result:
            print(f"✅ {name:30s} PASS")
            return True
        else:
            print(f"❌ {name:30s} FAIL")
            return False
    except Exception as e:
        print(f"❌ {name:30s} ERROR: {str(e)[:40]}")
        return False

def main():
    print_banner()
    
    # Initialize database
    print("Initializing database...")
    reset_db()
    init_db()
    
    # Create test client
    client = TestClient(app)
    
    results = []
    
    # ================================================================
    # Core API Tests
    # ================================================================
    print_section("Core API")
    
    results.append(validate_feature(
        "Root Endpoint",
        lambda: client.get("/").status_code == 200
    ))
    
    results.append(validate_feature(
        "Health Check",
        lambda: client.get("/health").json()["status"] == "healthy"
    ))
    
    results.append(validate_feature(
        "API Version 2.0.0",
        lambda: client.get("/").json()["version"] == "2.0.0"
    ))
    
    # ================================================================
    # Database Tests
    # ================================================================
    print_section("Database Integration")
    
    results.append(validate_feature(
        "Database Enabled",
        lambda: client.get("/").json()["status"]["database"] == "enabled"
    ))
    
    results.append(validate_feature(
        "Simulation Storage",
        lambda: "database" in client.post("/simulation/run").json()["storage"]
    ))
    
    # ================================================================
    # Agent Tests
    # ================================================================
    print_section("Agent & Analysis")
    
    def test_agent():
        r = client.post("/agent/run")
        data = r.json()
        return r.status_code == 200 and "state" in data and "actions_triggered" in data
    
    results.append(validate_feature("Agent Execution", test_agent))
    
    def test_state():
        r = client.get("/state/latest")
        return r.status_code == 200 and r.json()["status"] in ["GREEN", "YELLOW", "RED"]
    
    results.append(validate_feature("State Tracking", test_state))
    
    # ================================================================
    # Webhook Tests
    # ================================================================
    print_section("Webhook System")
    
    results.append(validate_feature(
        "Webhook Endpoint",
        lambda: client.get("/webhooks").status_code == 200
    ))
    
    def test_webhook_create():
        payload = {
            "url": "https://webhook.site/test",
            "events": ["event.created"],
            "active": True
        }
        r = client.post("/webhooks", json=payload)
        return r.status_code == 201  # POST should return 201 Created
    
    results.append(validate_feature("Webhook Creation", test_webhook_create))
    
    # ================================================================
    # Intelligence Tests
    # ================================================================
    print_section("Intelligence System")
    
    def test_deadline_risk():
        r = client.get("/intelligence/predict-deadline-risk")
        data = r.json()
        return (r.status_code == 200 and 
                "prediction" in data and 
                data["prediction"] in ["HIGH", "MODERATE", "LOW"])
    
    results.append(validate_feature("Deadline Risk Prediction", test_deadline_risk))
    
    def test_team_health():
        r = client.get("/intelligence/team-health")
        data = r.json()
        return (r.status_code == 200 and 
                "health_score" in data and 
                0 <= data["health_score"] <= 100)
    
    results.append(validate_feature("Team Health Scoring", test_team_health))
    
    def test_recommendations():
        r = client.post("/intelligence/recommendations")
        return r.status_code == 200 and isinstance(r.json(), list)
    
    results.append(validate_feature("AI Recommendations", test_recommendations))
    
    def test_forecast():
        r = client.get("/intelligence/forecast")
        return r.status_code == 200 and "forecast_days" in r.json()
    
    results.append(validate_feature("7-Day Forecast", test_forecast))
    
    # ================================================================
    # Analytics Tests
    # ================================================================
    print_section("Analytics System")
    
    def test_analytics_summary():
        r = client.get("/analytics/summary")
        data = r.json()
        return (r.status_code == 200 and 
                "total_events_processed" in data)
    
    results.append(validate_feature("Analytics Summary", test_analytics_summary))
    
    def test_analytics_velocity():
        r = client.get("/analytics/velocity")
        return r.status_code == 200
    
    results.append(validate_feature("Velocity Tracking", test_analytics_velocity))
    
    # ================================================================
    # Team Management Tests
    # ================================================================
    print_section("Team Management")
    
    results.append(validate_feature(
        "Team List Endpoint",
        lambda: client.get("/teams").status_code == 200
    ))
    
    def test_team_create():
        payload = {
            "name": "Test Team",
            "description": "Integration test team"
        }
        r = client.post("/teams", json=payload)
        return r.status_code == 201  # POST should return 201 Created
    
    results.append(validate_feature("Team Creation", test_team_create))
    
    # ================================================================
    # Summary
    # ================================================================
    print_section("Validation Summary")
    
    total_tests = len(results)
    passed_tests = sum(results)
    failed_tests = total_tests - passed_tests
    
    print(f"\nTotal Tests: {total_tests}")
    print(f"✅ Passed: {passed_tests}")
    print(f"❌ Failed: {failed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    print("\n" + "=" * 70)
    
    if passed_tests == total_tests:
        print("   🎉 ALL VALIDATIONS PASSED - SYSTEM FULLY OPERATIONAL!")
    else:
        print(f"   ⚠️  {failed_tests} VALIDATION(S) FAILED - REVIEW REQUIRED")
    
    print("=" * 70 + "\n")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

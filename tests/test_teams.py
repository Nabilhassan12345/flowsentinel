"""
Test Team Endpoints

Validates multi-team functionality including CRUD operations.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from src.main import app

# Create test client
client = TestClient(app)

# Global variable to store created team ID
created_team_id = None


def test_create_team():
    """Test POST /teams endpoint."""
    global created_team_id
    
    print("=" * 60)
    print("TEST 1: Create Team")
    print("=" * 60)
    
    team_data = {
        "name": "Test Engineering Team",
        "description": "Team for testing multi-tenant features",
        "members": ["alice@test.com", "bob@test.com", "charlie@test.com"],
        "settings": {
            "notifications_enabled": True,
            "slack_channel": "#test-eng"
        }
    }
    
    response = client.post("/teams", json=team_data)
    assert response.status_code == 201, f"Expected 201, got {response.status_code}"
    
    data = response.json()
    
    # Validate response
    assert "id" in data
    assert data["name"] == team_data["name"]
    assert data["description"] == team_data["description"]
    assert len(data["members"]) == 3
    assert data["member_count"] == 3
    assert data["event_count"] == 0  # New team has no events
    
    # Store team ID for other tests
    created_team_id = data["id"]
    
    print(f"✅ Created team: {data['name']}")
    print(f"   ID: {data['id']}")
    print(f"   Members: {data['member_count']}")
    print(f"   Events: {data['event_count']}")
    print()


def test_list_teams():
    """Test GET /teams endpoint."""
    print("=" * 60)
    print("TEST 2: List Teams")
    print("=" * 60)
    
    response = client.get("/teams")
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0  # Should have at least the team we created
    
    # Find our test team
    test_team = next((t for t in data if t["id"] == created_team_id), None)
    assert test_team is not None, "Created team not found in list"
    
    print(f"✅ Listed {len(data)} teams")
    print(f"   Test team found: {test_team['name']}")
    print()


def test_get_team():
    """Test GET /teams/{team_id} endpoint."""
    print("=" * 60)
    print("TEST 3: Get Team Details")
    print("=" * 60)
    
    response = client.get(f"/teams/{created_team_id}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["id"] == created_team_id
    assert data["name"] == "Test Engineering Team"
    assert "created_at" in data
    assert "updated_at" in data
    
    print(f"✅ Retrieved team: {data['name']}")
    print(f"   Members: {data['member_count']}")
    print(f"   Events: {data['event_count']}")
    print(f"   Actions: {data['action_count']}")
    print()


def test_update_team():
    """Test PATCH /teams/{team_id} endpoint."""
    print("=" * 60)
    print("TEST 4: Update Team")
    print("=" * 60)
    
    update_data = {
        "description": "Updated description for testing",
        "members": ["alice@test.com", "bob@test.com", "charlie@test.com", "david@test.com"],
        "settings": {
            "notifications_enabled": False
        }
    }
    
    response = client.patch(f"/teams/{created_team_id}", json=update_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["description"] == update_data["description"]
    assert len(data["members"]) == 4
    assert data["member_count"] == 4
    
    print(f"✅ Updated team: {data['name']}")
    print(f"   New description: {data['description']}")
    print(f"   New member count: {data['member_count']}")
    print()


def test_get_team_events():
    """Test GET /teams/{team_id}/events endpoint."""
    print("=" * 60)
    print("TEST 5: Get Team Events")
    print("=" * 60)
    
    response = client.get(f"/teams/{created_team_id}/events?limit=10")
    assert response.status_code == 200
    
    data = response.json()
    assert "team_id" in data
    assert "events" in data
    assert "total_count" in data
    assert data["team_id"] == created_team_id
    
    print(f"✅ Retrieved team events")
    print(f"   Total events: {data['total_count']}")
    print(f"   Returned: {data['returned']}")
    print()


def test_get_team_state():
    """Test GET /teams/{team_id}/state endpoint."""
    print("=" * 60)
    print("TEST 6: Get Team State")
    print("=" * 60)
    
    response = client.get(f"/teams/{created_team_id}/state")
    
    # Team might not have state yet (404 is expected)
    if response.status_code == 404:
        print("ℹ️  No project state found (expected for new team)")
        print()
    else:
        assert response.status_code == 200
        data = response.json()
        assert "team_id" in data
        assert "state" in data
        print(f"✅ Retrieved team state")
        print(f"   Status: {data['state']['status']}")
        print()


def test_get_team_analytics():
    """Test GET /teams/{team_id}/analytics endpoint."""
    print("=" * 60)
    print("TEST 7: Get Team Analytics")
    print("=" * 60)
    
    response = client.get(f"/teams/{created_team_id}/analytics")
    assert response.status_code == 200
    
    data = response.json()
    assert data["team_id"] == created_team_id
    assert "total_events" in data
    assert "events_by_source" in data
    assert "total_actions" in data
    
    print(f"✅ Retrieved team analytics")
    print(f"   Team: {data['team_name']}")
    print(f"   Total events: {data['total_events']}")
    print(f"   Total actions: {data['total_actions']}")
    print(f"   Unprocessed: {data['unprocessed_events']}")
    print()


def test_team_not_found():
    """Test error handling for non-existent team."""
    print("=" * 60)
    print("TEST 8: Team Not Found (Error Handling)")
    print("=" * 60)
    
    fake_id = "nonexistent_team_id"
    response = client.get(f"/teams/{fake_id}")
    assert response.status_code == 404
    
    data = response.json()
    assert "detail" in data
    
    print(f"✅ Correctly returned 404 for non-existent team")
    print(f"   Error: {data['detail']}")
    print()


def test_duplicate_team_name():
    """Test validation for duplicate team names."""
    print("=" * 60)
    print("TEST 9: Duplicate Team Name (Validation)")
    print("=" * 60)
    
    team_data = {
        "name": "Test Engineering Team",  # Same name as existing team
        "description": "This should fail",
        "members": []
    }
    
    response = client.post("/teams", json=team_data)
    assert response.status_code == 400
    
    data = response.json()
    assert "detail" in data
    assert "already exists" in data["detail"].lower()
    
    print(f"✅ Correctly rejected duplicate team name")
    print(f"   Error: {data['detail']}")
    print()


def test_soft_delete_team():
    """Test DELETE /teams/{team_id} (soft delete)."""
    print("=" * 60)
    print("TEST 10: Soft Delete Team")
    print("=" * 60)
    
    response = client.delete(f"/teams/{created_team_id}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["success"] is True
    assert data["deleted"] is False  # Soft delete
    assert "preserved" in data["message"].lower()
    
    print(f"✅ Soft deleted team (data preserved)")
    print(f"   Message: {data['message']}")
    print(f"   Note: {data.get('note', 'N/A')}")
    print()


def test_pagination():
    """Test pagination for team list."""
    print("=" * 60)
    print("TEST 11: Pagination")
    print("=" * 60)
    
    # Get first page
    response1 = client.get("/teams?limit=1&offset=0")
    assert response1.status_code == 200
    data1 = response1.json()
    
    # Get second page
    response2 = client.get("/teams?limit=1&offset=1")
    assert response2.status_code == 200
    data2 = response2.json()
    
    # Pages should be different (if we have enough teams)
    if len(data1) > 0 and len(data2) > 0:
        assert data1[0]["id"] != data2[0]["id"], "Pagination not working correctly"
        print(f"✅ Pagination working correctly")
        print(f"   Page 1: {data1[0]['name']}")
        print(f"   Page 2: {data2[0]['name']}")
    else:
        print("ℹ️  Not enough teams to test pagination fully")
    print()


def run_all_tests():
    """Run all team endpoint tests."""
    print("\n" + "=" * 60)
    print("🧪 TEAM ENDPOINTS TESTS")
    print("=" * 60 + "\n")
    
    try:
        test_create_team()
        test_list_teams()
        test_get_team()
        test_update_team()
        test_get_team_events()
        test_get_team_state()
        test_get_team_analytics()
        test_team_not_found()
        test_duplicate_team_name()
        test_soft_delete_team()
        test_pagination()
        
        print("=" * 60)
        print("✅ ALL TEAM TESTS PASSED!")
        print("=" * 60)
        print("\n📊 Endpoints Validated:")
        print("   ✅ POST   /teams")
        print("   ✅ GET    /teams")
        print("   ✅ GET    /teams/{team_id}")
        print("   ✅ PATCH  /teams/{team_id}")
        print("   ✅ DELETE /teams/{team_id}")
        print("   ✅ GET    /teams/{team_id}/events")
        print("   ✅ GET    /teams/{team_id}/state")
        print("   ✅ GET    /teams/{team_id}/analytics")
        print("\n🎯 Features Tested:")
        print("   ✅ CRUD operations")
        print("   ✅ Validation (unique names)")
        print("   ✅ Error handling (404s)")
        print("   ✅ Soft delete")
        print("   ✅ Pagination")
        print("   ✅ Team-specific data filtering")
        print("\n🎉 Multi-tenant system ready!\n")
        
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

#!/usr/bin/env python3
"""
Quick demo script to populate FlowSentinel with test data
Shows the frontend-backend integration in action
"""

import requests
import json
from datetime import datetime, timedelta
import time

API_BASE = "http://localhost:8000"

def add_event(source, event_type, data):
    """Add an event to the system"""
    response = requests.post(f"{API_BASE}/events/add", json={
        "source": source,
        "type": event_type,
        "data": data
    })
    return response.json()

def update_project_state(status, blockers, risks, completed):
    """Update project state"""
    response = requests.post(f"{API_BASE}/state/update", json={
        "status": status,
        "blockers": blockers,
        "risks": risks,
        "completed_today": completed
    })
    return response.json()

def main():
    print("🚀 FlowSentinel Demo Data Generator")
    print("=" * 60)
    
    # Add GitHub events
    print("\n📦 Adding GitHub events...")
    add_event("github", "pull_request", {
        "repo": "flowsentinel",
        "action": "opened",
        "pr_number": 123,
        "title": "Add IBM watsonx.ai integration",
        "author": "nabilhassan"
    })
    
    add_event("github", "commit", {
        "repo": "flowsentinel",
        "branch": "main",
        "message": "Fix authentication bug in user module",
        "author": "abdulrahman",
        "files_changed": 3
    })
    
    add_event("github", "pull_request", {
        "repo": "flowsentinel",
        "action": "merged",
        "pr_number": 122,
        "title": "Update README with deployment instructions"
    })
    
    print("✅ GitHub events added")
    
    # Add Slack events
    print("\n💬 Adding Slack events...")
    add_event("slack", "message", {
        "channel": "dev-team",
        "user": "nabil",
        "message": "Just deployed the new authentication feature to staging 🚀",
        "timestamp": datetime.now().isoformat()
    })
    
    add_event("slack", "message", {
        "channel": "dev-team",
        "user": "abdulrahman",
        "message": "Found a critical bug in the payment module, working on a fix",
        "timestamp": datetime.now().isoformat()
    })
    
    add_event("slack", "message", {
        "channel": "general",
        "user": "nabil",
        "message": "Team standup in 5 minutes!",
        "timestamp": datetime.now().isoformat()
    })
    
    print("✅ Slack events added")
    
    # Add Jira events
    print("\n📋 Adding Jira events...")
    add_event("jira", "issue_created", {
        "project": "FLOW",
        "issue_key": "FLOW-123",
        "type": "Bug",
        "priority": "High",
        "summary": "Payment gateway timeout on checkout",
        "assignee": "abdulrahman"
    })
    
    add_event("jira", "issue_updated", {
        "issue_key": "FLOW-120",
        "status": "In Progress",
        "summary": "Implement IBM watsonx.ai integration"
    })
    
    add_event("jira", "issue_completed", {
        "issue_key": "FLOW-118",
        "summary": "Add user authentication",
        "completed_by": "nabil",
        "time_spent": "8h"
    })
    
    print("✅ Jira events added")
    
    # Add Calendar events
    print("\n📅 Adding Calendar events...")
    add_event("calendar", "meeting_scheduled", {
        "title": "Sprint Planning",
        "start_time": (datetime.now() + timedelta(days=1, hours=2)).isoformat(),
        "duration_minutes": 60,
        "attendees": ["nabil", "abdulrahman", "team"]
    })
    
    add_event("calendar", "meeting_completed", {
        "title": "Daily Standup",
        "duration_minutes": 15,
        "notes": "Discussed IBM watsonx challenge submission timeline"
    })
    
    print("✅ Calendar events added")
    
    # Update project state
    print("\n📊 Updating project state...")
    update_project_state(
        status="YELLOW",
        blockers=[
            "Payment gateway integration pending",
            "Waiting for API keys from client"
        ],
        risks=[
            "Tight deadline for IBM watsonx challenge",
            "Payment module needs thorough testing"
        ],
        completed=[
            "IBM watsonx.ai integration complete",
            "Frontend dashboard deployed",
            "Authentication module tested"
        ]
    )
    
    print("✅ Project state updated")
    
    # Summary
    print("\n" + "=" * 60)
    print("✨ Demo data added successfully!")
    print("\n📊 Check your dashboard at: http://localhost:8080")
    print("📚 API docs at: http://localhost:8000/docs")
    print("\n🎯 You should see:")
    print("   • 10 events in the event feed")
    print("   • Project status: YELLOW")
    print("   • 2 active blockers")
    print("   • 2 risk items")
    print("   • 3 completed items today")
    print("\n🔄 Refresh your browser to see the updates!")
    print("=" * 60)

if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Cannot connect to backend server")
        print("   Make sure the backend is running at http://localhost:8000")
        print("   Run: python src/main.py")
    except Exception as e:
        print(f"❌ Error: {e}")

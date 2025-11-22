#!/usr/bin/env python3
"""
FlowSentinel Demo Script

This script demonstrates the complete FlowSentinel workflow:
1. Check server health
2. Load simulation data
3. Run agent analysis
4. Query project state
5. Ask questions via Q&A
6. View triggered actions

Run this after starting the server with: python main.py
"""

import requests
import json
import time
from typing import Dict, Any

BASE_URL = "http://localhost:8000"


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_json(data: Dict[Any, Any]):
    """Pretty print JSON data."""
    print(json.dumps(data, indent=2))


def make_request(method: str, endpoint: str, data: Dict = None) -> Dict:
    """Make HTTP request and return JSON response."""
    url = f"{BASE_URL}{endpoint}"

    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        else:
            raise ValueError(f"Unsupported method: {method}")

        response.raise_for_status()
        return response.json()

    except requests.exceptions.ConnectionError:
        print(f"❌ Error: Could not connect to {BASE_URL}")
        print("   Make sure the server is running: python main.py")
        exit(1)

    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP Error: {e}")
        print(f"   Response: {response.text}")
        return None


def main():
    """Run the complete demo workflow."""

    print("\n🧠 FlowSentinel Demo Script")
    print("=" * 60)

    # 1. Health Check
    print_section("1. Health Check")
    health = make_request("GET", "/health")
    print_json(health)
    time.sleep(1)

    # 2. Load Simulation Data
    print_section("2. Loading Simulation Data")
    sim_result = make_request("POST", "/simulation/run")
    print_json(sim_result)
    time.sleep(1)

    # 3. View Events
    print_section("3. Recent Events (First 3)")
    events = make_request("GET", "/events/list?limit=3")
    if events:
        print(f"Total events: {events['count']}")
        for event in events["events"][:3]:
            print(f"\n  [{event['source'].upper()}] {event['type']}")
            print(f"  Timestamp: {event['timestamp']}")
            print(f"  Data: {event['data']}")
    time.sleep(1)

    # 4. Run Agent Analysis
    print_section("4. Running Agent Analysis")
    agent_result = make_request("POST", "/agent/run")
    if agent_result:
        print(f"Status: {agent_result['status']}")
        print(f"Actions triggered: {agent_result['actions_triggered']}")
        print(f"\nProject State:")
        print(f"  Health: {agent_result['state']['status']}")
        print(f"  Blockers: {len(agent_result['state']['blockers'])}")
        print(f"  Risks: {len(agent_result['state']['risks'])}")
        print(f"  Completed: {len(agent_result['state']['completed_today'])}")
    time.sleep(1)

    # 5. Get Project State
    print_section("5. Current Project State")
    state = make_request("GET", "/state/latest")
    if state:
        print(f"Overall Status: {state['status']} 🚦")

        if state["blockers"]:
            print("\n🚨 Blockers:")
            for blocker in state["blockers"]:
                print(f"  - {blocker['description']}")
                print(f"    Source: {blocker['source']}, Time: {blocker['timestamp']}")

        if state["risks"]:
            print("\n⚠️  Risks:")
            for risk in state["risks"]:
                print(f"  - {risk['description']}")
                print(f"    Impact: {risk['impact']}")

        if state["completed_today"]:
            print("\n✅ Completed:")
            for item in state["completed_today"]:
                print(f"  - {item['description']}")

        print(f"\n📅 Next Deadline: {state['next_deadline']}")
    time.sleep(1)

    # 6. Ask Questions
    print_section("6. Q&A - Asking Questions")

    questions = [
        "Is the project at risk?",
        "What are the current blockers?",
        "What is the project status?",
    ]

    for question in questions:
        print(f"\n❓ Question: {question}")
        qa_response = make_request("POST", "/qa/ask", {"question": question})

        if qa_response:
            print(f"\n💡 Answer: {qa_response['answer']}")
            print(f"\n🧠 Reasoning:")
            for step in qa_response["reasoning"]:
                print(f"  • {step}")

        time.sleep(1)

    # 7. View Actions
    print_section("7. Automated Actions Taken")
    actions = make_request("GET", "/actions/list?limit=5")
    if actions:
        print(f"Total actions: {actions['count']}\n")
        for action in actions["actions"]:
            icon = {"notify_user": "📬", "create_task": "📋", "generate_report": "📊"}.get(
                action["type"], "🤖"
            )
            print(f"{icon} {action['type'].upper()}")
            print(f"  Status: {action['status']}")
            print(f"  Time: {action['timestamp']}")
            if action["payload"]:
                print(f"  Details: {json.dumps(action['payload'], indent=4)}")
            print()

    # 8. Final Summary
    print_section("✅ Demo Complete!")
    print(
        """
The FlowSentinel agent has:
  ✓ Ingested 8 events from Slack, Jira, GitHub, and Calendar
  ✓ Analyzed project state using watsonx.ai
  ✓ Detected blockers and risks
  ✓ Triggered automated actions via Orchestrate
  ✓ Answered questions about project health

🌐 View interactive API docs: http://localhost:8000/docs
📊 Try more queries or add your own events!
    """
    )


if __name__ == "__main__":
    main()

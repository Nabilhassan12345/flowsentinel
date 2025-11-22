#!/usr/bin/env python3
"""
FlowSentinel API Test Script

Comprehensive test suite for all FlowSentinel endpoints.
Tests include health checks, event ingestion, agent execution,
state retrieval, actions, and Q&A functionality.

Usage:
    python test_api.py

Requirements:
    - Server must be running: python main.py
    - requests library: pip install requests
"""

import requests
import json
import sys
import time
from typing import Dict, Any, Tuple
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
TIMEOUT = 10  # seconds


# ANSI color codes for terminal output
class Colors:
    """Terminal color codes for pretty output."""

    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    MAGENTA = "\033[95m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    END = "\033[0m"


# Test results tracker
test_results = {"passed": 0, "failed": 0, "tests": []}


def print_header(title: str, char: str = "="):
    """Print a formatted section header."""
    width = 70
    print(f"\n{Colors.BOLD}{Colors.CYAN}{char * width}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{title.center(width)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{char * width}{Colors.END}\n")


def print_subheader(title: str):
    """Print a formatted subsection header."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'─' * 70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{title}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'─' * 70}{Colors.END}")


def print_success(message: str):
    """Print success message."""
    print(f"{Colors.GREEN}✅ {message}{Colors.END}")


def print_error(message: str):
    """Print error message."""
    print(f"{Colors.RED}❌ {message}{Colors.END}")


def print_warning(message: str):
    """Print warning message."""
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.END}")


def print_info(message: str):
    """Print info message."""
    print(f"{Colors.BLUE}ℹ️  {message}{Colors.END}")


def print_json(data: Dict[Any, Any], indent: int = 2):
    """Pretty print JSON data with syntax highlighting."""
    json_str = json.dumps(data, indent=indent)
    print(f"{Colors.CYAN}{json_str}{Colors.END}")


def record_test(test_name: str, passed: bool, response_time: float = None):
    """Record test result."""
    test_results["tests"].append(
        {"name": test_name, "passed": passed, "response_time": response_time}
    )
    if passed:
        test_results["passed"] += 1
    else:
        test_results["failed"] += 1


def make_request(
    method: str, endpoint: str, data: Dict = None, test_name: str = None
) -> Tuple[bool, Any]:
    """
    Make HTTP request and handle response.

    Args:
        method: HTTP method (GET, POST)
        endpoint: API endpoint path
        data: Request payload for POST requests
        test_name: Name of the test for tracking

    Returns:
        Tuple of (success: bool, response_data: Any)
    """
    url = f"{BASE_URL}{endpoint}"
    start_time = time.time()

    try:
        if method == "GET":
            response = requests.get(url, timeout=TIMEOUT)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=TIMEOUT)
        else:
            raise ValueError(f"Unsupported method: {method}")

        response_time = time.time() - start_time

        # Check status code
        response.raise_for_status()

        # Parse JSON response
        response_data = response.json()

        if test_name:
            record_test(test_name, True, response_time)
            print_success(
                f"{test_name} - {response.status_code} ({response_time:.3f}s)"
            )

        return True, response_data

    except requests.exceptions.ConnectionError:
        if test_name:
            record_test(test_name, False)
        print_error(f"Connection failed: Cannot connect to {BASE_URL}")
        print_warning("Make sure the server is running: python main.py")
        return False, None

    except requests.exceptions.Timeout:
        if test_name:
            record_test(test_name, False)
        print_error(f"Request timeout: Server took longer than {TIMEOUT}s")
        return False, None

    except requests.exceptions.HTTPError as e:
        response_time = time.time() - start_time
        if test_name:
            record_test(test_name, False, response_time)
        print_error(
            f"{test_name or 'Request'} - {e.response.status_code} ({response_time:.3f}s)"
        )
        try:
            error_detail = e.response.json()
            print_json(error_detail)
        except:
            print(f"Response: {e.response.text}")
        return False, None

    except Exception as e:
        if test_name:
            record_test(test_name, False)
        print_error(f"Unexpected error: {str(e)}")
        return False, None


def test_server_health() -> bool:
    """Test if server is running and healthy."""
    print_subheader("1. Server Health Check")

    success, data = make_request("GET", "/health", test_name="Health Check")

    if success and data:
        print_info("Server Status:")
        print_json(data)
        return True

    return False


def test_root_endpoint():
    """Test root endpoint."""
    print_subheader("2. Root Endpoint")

    success, data = make_request("GET", "/", test_name="Root Endpoint")

    if success and data:
        print_info("API Information:")
        print_json(data)


def test_simulation_load():
    """Test loading simulation data."""
    print_subheader("3. Load Simulation Data")

    success, data = make_request("POST", "/simulation/run", test_name="Load Simulation")

    if success and data:
        print_info("Simulation Result:")
        print_json(data)

        if data.get("events_created") == 8:
            print_success(f"Created {data['events_created']} simulation events")
        else:
            print_warning(f"Expected 8 events, got {data.get('events_created', 0)}")


def test_list_events():
    """Test listing events."""
    print_subheader("4. List Recent Events")

    success, data = make_request("GET", "/events/list?limit=5", test_name="List Events")

    if success and data:
        print_info(f"Total events: {data.get('count', 0)}")

        if data.get("events"):
            print_info("Sample events (first 3):")
            for i, event in enumerate(data["events"][:3], 1):
                print(f"\n  {Colors.MAGENTA}Event {i}:{Colors.END}")
                print(f"    Source: {event['source']}")
                print(f"    Type: {event['type']}")
                print(f"    Timestamp: {event['timestamp']}")
                print(f"    Data: {json.dumps(event['data'], indent=6)}")


def test_ingest_single_event():
    """Test ingesting a single event."""
    print_subheader("5. Ingest Single Event")

    # Create a test event
    test_event = {
        "id": f"test_evt_{int(time.time())}",
        "source": "slack",
        "type": "message",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "data": {
            "user": "test_user",
            "message": "This is a test event from test_api.py",
        },
        "processed": False,
    }

    success, data = make_request(
        "POST", "/events/ingest", data=test_event, test_name="Ingest Single Event"
    )

    if success and data:
        print_info("Ingest Result:")
        print_json(data)


def test_ingest_batch_events():
    """Test ingesting multiple events."""
    print_subheader("6. Ingest Batch Events")

    # Create batch of test events
    batch_events = [
        {
            "id": f"batch_evt_{int(time.time())}_{i}",
            "source": "github",
            "type": "pr_opened",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "data": {
                "pr_number": 100 + i,
                "title": f"Test PR {i}",
                "author": "test_bot",
            },
            "processed": False,
        }
        for i in range(3)
    ]

    success, data = make_request(
        "POST",
        "/events/ingest/batch",
        data=batch_events,
        test_name="Ingest Batch Events",
    )

    if success and data:
        print_info("Batch Ingest Result:")
        print_json(data)
        print_success(f"Ingested {data.get('count', 0)} events")


def test_run_agent():
    """Test running the agent analysis."""
    print_subheader("7. Run Agent Analysis")

    success, data = make_request("POST", "/agent/run", test_name="Run Agent")

    if success and data:
        print_info("Agent Analysis Result:")

        state = data.get("state", {})
        print(
            f"\n  {Colors.BOLD}Project Status:{Colors.END} {state.get('status', 'N/A')} 🚦"
        )
        print(
            f"  {Colors.BOLD}Actions Triggered:{Colors.END} {data.get('actions_triggered', 0)}"
        )

        print(
            f"\n  {Colors.BOLD}Blockers:{Colors.END} {len(state.get('blockers', []))}"
        )
        for blocker in state.get("blockers", [])[:3]:
            print(f"    • {blocker.get('description', 'N/A')}")

        print(f"\n  {Colors.BOLD}Risks:{Colors.END} {len(state.get('risks', []))}")
        for risk in state.get("risks", [])[:3]:
            print(f"    • {risk.get('description', 'N/A')}")

        print(
            f"\n  {Colors.BOLD}Completed:{Colors.END} {len(state.get('completed_today', []))}"
        )
        for item in state.get("completed_today", [])[:3]:
            print(f"    • {item.get('description', 'N/A')}")


def test_get_state():
    """Test getting latest project state."""
    print_subheader("8. Get Latest State")

    success, data = make_request("GET", "/state/latest", test_name="Get State")

    if success and data:
        print_info("Current Project State:")
        print_json(data)


def test_list_actions():
    """Test listing executed actions."""
    print_subheader("9. List Actions")

    success, data = make_request(
        "GET", "/actions/list?limit=5", test_name="List Actions"
    )

    if success and data:
        print_info(f"Total actions: {data.get('count', 0)}")

        if data.get("actions"):
            print_info("Recent actions:")
            for action in data["actions"][:5]:
                icon = {
                    "notify_user": "📬",
                    "create_task": "📋",
                    "generate_report": "📊",
                }.get(action["type"], "🤖")

                print(f"\n  {icon} {Colors.BOLD}{action['type']}{Colors.END}")
                print(f"    Status: {action['status']}")
                print(f"    Time: {action['timestamp']}")
                if action.get("payload"):
                    print(f"    Payload: {json.dumps(action['payload'], indent=6)}")


def test_qa_ask():
    """Test Q&A endpoint."""
    print_subheader("10. Ask Question (Q&A)")

    questions = [
        "Is the project at risk?",
        "What are the current blockers?",
        "What is the project status?",
    ]

    for i, question in enumerate(questions, 1):
        print(f"\n{Colors.BOLD}Question {i}:{Colors.END} {question}")

        success, data = make_request(
            "POST",
            "/qa/ask",
            data={"question": question},
            test_name=f"Q&A: {question[:30]}...",
        )

        if success and data:
            print(f"\n{Colors.GREEN}Answer:{Colors.END}")
            print(f"  {data.get('answer', 'N/A')}")

            print(f"\n{Colors.BLUE}Reasoning:{Colors.END}")
            for step in data.get("reasoning", []):
                print(f"  • {step}")

            print()  # Extra line for readability

        time.sleep(0.5)  # Brief pause between questions


def run_full_demo_sequence():
    """Run a complete demo sequence of all features."""
    print_header("FLOWSENTINEL API FULL DEMO SEQUENCE", "═")

    # Step 1: Check server health
    if not test_server_health():
        print_error("Server is not running. Please start it with: python main.py")
        return False

    # Step 2: Test root endpoint
    test_root_endpoint()

    # Step 3: Load simulation data
    test_simulation_load()

    # Step 4: List events
    test_list_events()

    # Step 5: Ingest single event
    test_ingest_single_event()

    # Step 6: Ingest batch events
    test_ingest_batch_events()

    # Step 7: Run agent analysis
    test_run_agent()

    # Step 8: Get current state
    test_get_state()

    # Step 9: List actions
    test_list_actions()

    # Step 10: Ask questions
    test_qa_ask()

    return True


def print_test_summary():
    """Print final test summary."""
    print_header("TEST SUMMARY", "═")

    total_tests = test_results["passed"] + test_results["failed"]
    pass_rate = (test_results["passed"] / total_tests * 100) if total_tests > 0 else 0

    print(f"\n{Colors.BOLD}Total Tests:{Colors.END} {total_tests}")
    print(f"{Colors.GREEN}{Colors.BOLD}✅ Passed:{Colors.END} {test_results['passed']}")
    print(f"{Colors.RED}{Colors.BOLD}❌ Failed:{Colors.END} {test_results['failed']}")
    print(f"{Colors.BOLD}Pass Rate:{Colors.END} {pass_rate:.1f}%\n")

    # Show detailed results
    if test_results["tests"]:
        print(f"{Colors.BOLD}Detailed Results:{Colors.END}\n")
        for test in test_results["tests"]:
            status = (
                f"{Colors.GREEN}✅ PASS{Colors.END}"
                if test["passed"]
                else f"{Colors.RED}❌ FAIL{Colors.END}"
            )
            time_str = (
                f"({test['response_time']:.3f}s)" if test.get("response_time") else ""
            )
            print(f"  {status} - {test['name']} {time_str}")

    print()

    # Overall result
    if test_results["failed"] == 0:
        print(f"{Colors.GREEN}{Colors.BOLD}{'═' * 70}{Colors.END}")
        print(
            f"{Colors.GREEN}{Colors.BOLD}🎉 ALL TESTS PASSED! 🎉{Colors.END}".center(80)
        )
        print(f"{Colors.GREEN}{Colors.BOLD}{'═' * 70}{Colors.END}\n")
        return True
    else:
        print(f"{Colors.RED}{Colors.BOLD}{'═' * 70}{Colors.END}")
        print(
            f"{Colors.RED}{Colors.BOLD}⚠️  SOME TESTS FAILED ⚠️{Colors.END}".center(80)
        )
        print(f"{Colors.RED}{Colors.BOLD}{'═' * 70}{Colors.END}\n")
        return False


def check_server_running() -> bool:
    """Quick check if server is accessible."""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=3)
        return response.status_code == 200
    except:
        return False


def main():
    """Main test execution."""
    print(f"\n{Colors.BOLD}{Colors.MAGENTA}{'=' * 70}{Colors.END}")
    print(
        f"{Colors.BOLD}{Colors.MAGENTA}🧠 FLOWSENTINEL API TEST SUITE{Colors.END}".center(
            80
        )
    )
    print(f"{Colors.BOLD}{Colors.MAGENTA}{'=' * 70}{Colors.END}\n")

    print_info(f"Base URL: {BASE_URL}")
    print_info(f"Timeout: {TIMEOUT}s")
    print_info(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Check if server is running
    print("Checking server status...", end=" ")
    if check_server_running():
        print_success("Server is running!")
    else:
        print_error("Server is not running!")
        print_warning("Please start the server first:")
        print(f"  {Colors.CYAN}python main.py{Colors.END}\n")
        sys.exit(1)

    # Run all tests
    try:
        success = run_full_demo_sequence()

        # Print summary
        print_test_summary()

        # Exit with appropriate code
        sys.exit(0 if success and test_results["failed"] == 0 else 1)

    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Test interrupted by user{Colors.END}\n")
        print_test_summary()
        sys.exit(130)

    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

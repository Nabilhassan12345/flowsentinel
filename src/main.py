"""
FlowSentinel - Agentic Company Brain for Team Workflow Monitoring

A hackathon project that ingests events from Slack, Jira, GitHub, and Calendar,
analyzes them using IBM watsonx.ai to understand project state, detects risks/blockers,
and takes automated actions via IBM watsonx Orchestrate.

Technical Stack:
- Framework: FastAPI with Python 3.8+
- Data Validation: Pydantic v2
- Server: Uvicorn with hot reload
- Storage: In-memory (lists/dicts) for MVP
- AI: IBM watsonx.ai (simulated for demo)
- Actions: IBM watsonx Orchestrate (simulated, real Slack webhook)
"""

import os
import json
import re
import requests
import asyncio
from datetime import datetime, timedelta
from typing import Any, Dict, List, Literal, Optional
from textwrap import shorten
from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
import httpx

# IBM watsonx.ai imports
try:
    from ibm_watsonx_ai.foundation_models import Model
    from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
    from ibm_watsonx_ai.foundation_models.utils.enums import ModelTypes
    from ibm_watsonx_ai import Credentials
    IBM_SDK_AVAILABLE = True
except ImportError:
    print("⚠️  IBM watsonx.ai SDK not installed")
    IBM_SDK_AVAILABLE = False

# Load environment variables
load_dotenv()

# Import database and routers with fallback
try:
    from database import init_db, get_db, test_connection
    from models import EventDB, ProjectStateDB, ActionDB
    DATABASE_ENABLED = True
except ImportError:
    print("⚠️  Database not available - using in-memory storage")
    DATABASE_ENABLED = False
    
    # Create a dummy dependency for type checking
    def get_db():
        """Dummy database dependency when database is not enabled."""
        yield None

try:
    from analytics_endpoints import router as analytics_router
    ANALYTICS_ENABLED = True
except ImportError:
    print("⚠️  Analytics endpoints not available")
    ANALYTICS_ENABLED = False

try:
    from team_endpoints import router as team_router
    TEAMS_ENABLED = True
except ImportError:
    print("⚠️  Team endpoints not available")
    TEAMS_ENABLED = False

try:
    from webhook_endpoints import router as webhook_router, trigger_webhooks
    WEBHOOKS_ENABLED = True
except ImportError:
    print("⚠️  Webhook endpoints not available")
    WEBHOOKS_ENABLED = False
    trigger_webhooks = None

try:
    from intelligence_endpoints import router as intelligence_router
    INTELLIGENCE_ENABLED = True
except ImportError:
    print("⚠️  Intelligence endpoints not available")
    INTELLIGENCE_ENABLED = False

try:
    from rag_endpoints import router as rag_router
    RAG_ENABLED = True
except ImportError:
    print("⚠️  RAG endpoints not available")
    RAG_ENABLED = False

try:
    from agent_endpoints import router as agent_router
    AGENT_ENABLED = True
except ImportError:
    print("⚠️  Agent endpoints not available")
    AGENT_ENABLED = False

try:
    from feedback_endpoints import router as feedback_router
    FEEDBACK_ENABLED = True
except ImportError:
    print("⚠️  Feedback endpoints not available")
    FEEDBACK_ENABLED = False

try:
    from pattern_endpoints import router as pattern_router
    PATTERNS_ENABLED = True
except ImportError:
    print("⚠️  Pattern endpoints not available")
    PATTERNS_ENABLED = False

try:
    from streaming_endpoints import router as streaming_router
    STREAMING_ENABLED = True
except ImportError:
    print("⚠️  Streaming endpoints not available")
    STREAMING_ENABLED = False


# ============================================================================
# AUTONOMOUS AGENT CONFIGURATION
# ============================================================================

# Agent control flags
AGENT_ENABLED = os.getenv("AGENT_ENABLED", "true").lower() == "true"
AGENT_RUN_INTERVAL = int(os.getenv("AGENT_RUN_INTERVAL", "300"))  # Default: 5 minutes (300 seconds)
agent_running = False
agent_task = None
agent_last_run = None
agent_run_count = 0


# ============================================================================
# PYDANTIC MODELS
# ============================================================================


class Event(BaseModel):
    """
    Represents an event from various sources (Slack, Jira, GitHub, Calendar).

    Attributes:
        id: Unique identifier for the event (e.g., "evt_001")
        source: The platform that generated the event
        type: The specific event type
        timestamp: When the event occurred (ISO 8601 format)
        data: Flexible payload containing event-specific data
        processed: Whether this event has been analyzed by the agent
    """

    id: str
    source: Literal["slack", "jira", "github", "calendar"]
    type: Literal[
        "message",
        "task_status_changed",
        "pr_opened",
        "pr_merged",
        "pr_review_requested",
        "meeting_moved",
        "deadline_changed",
    ]
    timestamp: str
    data: Dict[str, Any]
    processed: bool = False


class ProjectState(BaseModel):
    """
    Represents the current state of the project based on analyzed events.

    Attributes:
        status: Overall project health (GREEN=healthy, YELLOW=warning, RED=critical)
        blockers: List of current blockers preventing progress
        risks: List of identified risks that could impact the project
        completed_today: List of completed tasks/PRs today
        next_deadline: Upcoming deadline timestamp
        last_updated: When this state was last calculated
    """

    status: Literal["GREEN", "YELLOW", "RED"]
    blockers: List[Dict[str, str]]
    risks: List[Dict[str, str]]
    completed_today: List[Dict[str, str]]
    next_deadline: Optional[str]
    last_updated: str


class Action(BaseModel):
    """
    Represents an action taken by the Orchestrate bridge.

    Attributes:
        id: Unique action identifier
        type: The type of action performed
        status: Current status of the action
        payload: Action-specific data
        timestamp: When the action was executed
    """

    id: str
    type: Literal["notify_user", "create_task", "generate_report"]
    status: str
    payload: Dict[str, Any]
    timestamp: str


class QARequest(BaseModel):
    """Request model for Q&A endpoint."""

    question: str


class QAResponse(BaseModel):
    """
    Response model for Q&A queries about project state.

    Attributes:
        question: The original question asked
        answer: Detailed multi-sentence answer
        reasoning: List of reasoning steps taken to generate the answer
        timestamp: When the answer was generated
    """

    question: str
    answer: str
    reasoning: List[str]
    timestamp: str


# ============================================================================
# SLACK INTEGRATION
# ============================================================================


def send_slack_alert(text: str) -> None:
    """
    Send a simple alert message to Slack using the incoming webhook URL.

    If no SLACK_WEBHOOK_URL is configured, this function does nothing and logs a warning.
    It must NEVER crash the app.

    Args:
        text: The message text to send to Slack
    """
    webhook = os.getenv("SLACK_WEBHOOK_URL")
    if not webhook:
        print("⚠️  No SLACK_WEBHOOK_URL set, skipping Slack alert.")
        return

    try:
        response = requests.post(webhook, json={"text": text}, timeout=5)
        if response.status_code >= 300:
            print(f"⚠️  Slack returned {response.status_code}: {response.text[:200]}")
        else:
            print("✅ Slack alert sent to Slack channel.")
    except Exception as e:
        print(f"❌ Failed to send Slack alert: {e}")


# ============================================================================
# DATABASE CLASS
# ============================================================================


class Database:
    """
    In-memory storage for MVP. Easy to swap for PostgreSQL later.

    Stores events, project state, actions, and Q&A history in memory.
    All data is lost on restart, which is acceptable for demo purposes.
    """

    def __init__(self):
        """Initialize empty data stores."""
        self.events: List[Event] = []
        self.state: Optional[ProjectState] = None
        self.actions: List[Action] = []
        self.qa_history: List[QAResponse] = []

    def add_event(self, event: Event) -> None:
        """
        Add a new event to the database.

        Args:
            event: The event to store
        """
        self.events.append(event)

    def get_events(self, limit: int = 100) -> List[Event]:
        """
        Retrieve recent events, sorted by timestamp descending.

        Args:
            limit: Maximum number of events to return

        Returns:
            List of events, most recent first
        """
        # Sort by timestamp in descending order (most recent first)
        sorted_events = sorted(self.events, key=lambda e: e.timestamp, reverse=True)
        return sorted_events[:limit]

    def update_state(self, state: ProjectState) -> None:
        """
        Update the current project state.

        Args:
            state: The new project state
        """
        self.state = state

    def get_state(self) -> Optional[ProjectState]:
        """
        Get the current project state.

        Returns:
            Current project state or None if not yet calculated
        """
        return self.state

    def add_action(self, action: Action) -> None:
        """
        Add a new action to the history.

        Args:
            action: The action that was executed
        """
        self.actions.append(action)

    def get_actions(self, limit: int = 50) -> List[Action]:
        """
        Retrieve recent actions, sorted by timestamp descending.

        Args:
            limit: Maximum number of actions to return

        Returns:
            List of actions, most recent first
        """
        # Sort by timestamp in descending order (most recent first)
        sorted_actions = sorted(self.actions, key=lambda a: a.timestamp, reverse=True)
        return sorted_actions[:limit]

    def add_qa(self, qa: QAResponse) -> None:
        """
        Add a Q&A response to the history.

        Args:
            qa: The Q&A response to store
        """
        self.qa_history.append(qa)


# Global database instance
db = Database()


# ============================================================================
# WATSONX AGENT CLASS
# ============================================================================


class WatsonxAgent:
    """
    Simulates IBM watsonx.ai analysis. Structured for easy real API integration.

    In production, this would make API calls to IBM watsonx.ai.
    For the hackathon demo, it implements intelligent analysis logic locally.
    """

    @staticmethod
    async def analyze_state(events: List[Event]) -> ProjectState:
        """
        Analyze events and generate project state using IBM watsonx.ai.

        This method processes recent events to identify:
        - Blockers: Issues preventing progress
        - Risks: Potential problems that could impact timeline
        - Completed work: Recent accomplishments
        - Overall status: Health indicator for the project

        Args:
            events: List of events to analyze

        Returns:
            ProjectState object with analysis results
        """
        # Get API credentials
        api_key = os.getenv("WATSONX_API_KEY", "")
        project_id = os.getenv("WATSONX_PROJECT_ID", "")
        watsonx_url = os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com")
        
        # Process last 25 events
        recent_events = events[:25] if len(events) > 25 else events

        blockers = []
        risks = []
        completed = []
        status = "GREEN"

        # Check if we have real API credentials
        if IBM_SDK_AVAILABLE and api_key and project_id and len(api_key) > 20:
            # === REAL IBM WATSONX.AI MODE ===
            print("🔵 USING REAL IBM WATSONX.AI API (Granite)")
            try:
                # Initialize credentials
                credentials = Credentials(
                    url=watsonx_url,
                    api_key=api_key
                )
                
                # Set up model parameters
                parameters = {
                    GenParams.DECODING_METHOD: "greedy",
                    GenParams.MAX_NEW_TOKENS: 800,
                    GenParams.TEMPERATURE: 0.1,
                    GenParams.TOP_K: 50,
                    GenParams.TOP_P: 0.95,
                }
                
                # Initialize model (use env var if set)
                model_id = os.getenv("WATSONX_MODEL_ID", "ibm/granite-3-8b-instruct")
                model = Model(
                    model_id=model_id,
                    params=parameters,
                    credentials=credentials,
                    project_id=project_id,
                )
                
                # Build events summary
                events_data = [
                    {"source": e.source, "type": e.type, "timestamp": e.timestamp, "data": e.data}
                    for e in recent_events
                ]
                
                events_json = json.dumps(events_data, indent=2)
                
                prompt = f"""You are an expert project management AI. Analyze these software development events and provide a comprehensive analysis.

Events (JSON format):
{events_json}

Analyze the events and return ONLY a valid JSON object (no markdown, no code fences) with this exact structure:
{{
  "status": "GREEN or YELLOW or RED",
  "blockers": [
    {{"description": "detailed blocker description", "source": "slack|jira|github", "timestamp": "ISO8601"}}
  ],
  "risks": [
    {{"description": "detailed risk description", "impact": "impact assessment", "timestamp": "ISO8601"}}
  ],
  "completed": [
    {{"description": "completed item description", "timestamp": "ISO8601"}}
  ]
}}

Rules:
- status: GREEN = no blockers/risks, YELLOW = 1 blocker or 1-2 risks, RED = 2+ blockers or 3+ risks
- blockers: things explicitly blocking progress (keywords: blocked, waiting, stuck, need, missing)
- risks: potential timeline issues (deadline changes, delays, review backlogs)
- completed: merged PRs, completed tasks, done items
- Return ONLY valid JSON, no other text"""

                print("📡 Calling IBM watsonx.ai API...")
                response = model.generate_text(prompt=prompt)
                print("✅ Response received from IBM watsonx.ai")
                
                # Clean the response - remove markdown fences and extra text
                cleaned_response = response.strip()
                
                # Remove ```json and ``` fences if present
                if cleaned_response.startswith("```"):
                    cleaned_response = re.sub(r'^```(?:json)?\s*', '', cleaned_response)
                    cleaned_response = re.sub(r'\s*```\s*$', '', cleaned_response)
                
                # Try to extract JSON if there's extra text
                json_match = re.search(r'\{.*\}', cleaned_response, re.DOTALL)
                if json_match:
                    cleaned_response = json_match.group(0)
                
                # Parse JSON
                try:
                    ai_result = json.loads(cleaned_response)
                    print("✅ Parsed IBM watsonx.ai response")
                    
                    # Extract data from AI response
                    status = ai_result.get("status", "YELLOW")
                    blockers = ai_result.get("blockers", [])
                    risks = ai_result.get("risks", [])
                    completed = ai_result.get("completed", [])
                    
                    print(f"🧠 IBM watsonx.ai analysis: Status={status}, Blockers={len(blockers)}, Risks={len(risks)}, Completed={len(completed)}")
                    
                except json.JSONDecodeError as je:
                    print(f"⚠️  JSON parse error: {je}")
                    print(f"   Response snippet: {cleaned_response[:200]}")
                    print("   Falling back to rule-based analysis...")
                
            except Exception as e:
                print(f"⚠️  IBM watsonx.ai API error: {type(e).__name__}: {str(e)}")
                print("   Falling back to rule-based analysis...")
        
        # === FALLBACK: RULE-BASED ANALYSIS ===
        # This runs if no API key OR if API call failed
        if not blockers and not risks and not completed:
            # Keywords for blocker detection
            blocker_keywords = [
                "blocked",
                "waiting",
                "waiting on",
                "stuck",
                "can't proceed",
                "need",
                "missing",
            ]

            for event in recent_events:
                # BLOCKERS: Scan Slack messages for blocking keywords
                if event.source == "slack" and event.type == "message":
                    message = event.data.get("message", "").lower()
                    if any(keyword in message for keyword in blocker_keywords):
                        blockers.append(
                            {
                                "description": event.data.get("message", ""),
                                "source": "Slack",
                                "timestamp": event.timestamp,
                            }
                        )

                # RISKS: Scan Jira events for deadline changes or delays
                if event.source == "jira":
                    if event.type == "deadline_changed":
                        task = event.data.get("task", "Unknown task")
                        risks.append(
                            {
                                "description": f"Deadline changed for: {task}",
                                "impact": "May slip release by 1-2 days",
                                "timestamp": event.timestamp,
                            }
                        )
                    elif event.data.get("new_status") == "Delayed":
                        task = event.data.get("task", "Unknown task")
                        risks.append(
                            {
                                "description": f"Task delayed: {task}",
                                "impact": "May slip release by 1-2 days",
                                "timestamp": event.timestamp,
                            }
                        )

                # COMPLETED: Scan GitHub PR merges and Jira completions
                if event.source == "github" and event.type == "pr_merged":
                    pr_title = event.data.get("title", "Unknown PR")
                    completed.append(
                        {
                            "description": f"PR merged: {pr_title}",
                            "timestamp": event.timestamp,
                        }
                    )

                if event.source == "jira" and event.data.get("new_status") == "Done":
                    task = event.data.get("task", "Unknown task")
                    completed.append(
                        {
                            "description": f"Task completed: {task}",
                            "timestamp": event.timestamp,
                        }
                    )

        # Limit each list to max 5 items
        blockers = blockers[:5]
        risks = risks[:5]
        completed = completed[:5]

        # Calculate status based on blocker and risk counts
        blocker_count = len(blockers)
        risk_count = len(risks)

        if blocker_count >= 2 or risk_count >= 2:
            status = "RED"
        elif blocker_count >= 1 or risk_count >= 1:
            status = "YELLOW"
        else:
            status = "GREEN"

        # Generate current timestamp
        current_time = datetime.utcnow().isoformat() + "Z"

        return ProjectState(
            status=status,
            blockers=blockers,
            risks=risks,
            completed_today=completed,
            next_deadline="2024-03-25T17:00:00Z",
            last_updated=current_time,
        )

    @staticmethod
    async def answer_question(
        question: str, state: ProjectState, events: List[Event]
    ) -> QAResponse:
        """
        Generate intelligent answers to questions about project state using IBM watsonx.ai.

        Uses IBM watsonx.ai to understand the question and provide detailed,
        contextual answers based on current project state.

        Args:
            question: The question to answer
            state: Current project state
            events: Recent events for additional context

        Returns:
            QAResponse with answer and reasoning
        """
        # Get API credentials
        api_key = os.getenv("WATSONX_API_KEY", "")
        project_id = os.getenv("WATSONX_PROJECT_ID", "")
        watsonx_url = os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com")
        
        # Generate current timestamp
        current_time = datetime.utcnow().isoformat() + "Z"
        
        # Check if we have real API credentials
        if IBM_SDK_AVAILABLE and api_key and project_id and len(api_key) > 20:
            # === REAL IBM WATSONX.AI MODE ===
            print(f"🔵 IBM watsonx.ai Q&A (Granite) - Question: {question[:60]}")
            try:
                # Initialize credentials
                credentials = Credentials(url=watsonx_url, api_key=api_key)
                
                # Set up model parameters
                parameters = {
                    GenParams.DECODING_METHOD: "greedy",
                    GenParams.MAX_NEW_TOKENS: 500,
                    GenParams.TEMPERATURE: 0.3,
                    GenParams.TOP_K: 50,
                    GenParams.TOP_P: 0.95,
                }
                
                # Initialize model (use env var if set)
                model_id = os.getenv("WATSONX_MODEL_ID", "ibm/granite-3-8b-instruct")
                model = Model(
                    model_id=model_id,
                    params=parameters,
                    credentials=credentials,
                    project_id=project_id,
                )
                
                # Build context JSON
                recent_events_list = [
                    {"source": e.source, "type": e.type, "data": e.data}
                    for e in events[:10]
                ]
                
                context = {
                    "status": state.status,
                    "blockers": state.blockers,
                    "risks": state.risks,
                    "completed_today": state.completed_today,
                    "next_deadline": state.next_deadline,
                    "recent_events": recent_events_list
                }
                
                context_json = json.dumps(context, indent=2)
                
                prompt = f"""You are an expert project management AI assistant. Answer the user's question based on the provided context.

CONTEXT (JSON):
{context_json}

USER QUESTION: {question}

Return ONLY a valid JSON object (no markdown, no code fences) with this structure:
{{
  "answer": "2-4 sentence answer with specific details from context",
  "reasoning": [
    "reasoning step 1",
    "reasoning step 2",
    "reasoning step 3"
  ]
}}

Be specific and reference actual data from the context. Return ONLY valid JSON."""

                print("📡 Calling IBM watsonx.ai API for Q&A...")
                response = model.generate_text(prompt=prompt)
                print("✅ Response received from IBM watsonx.ai")
                
                # Clean response
                cleaned_response = response.strip()
                
                # Remove markdown fences
                if cleaned_response.startswith("```"):
                    cleaned_response = re.sub(r'^```(?:json)?\s*', '', cleaned_response)
                    cleaned_response = re.sub(r'\s*```\s*$', '', cleaned_response)
                
                # Extract JSON
                json_match = re.search(r'\{.*\}', cleaned_response, re.DOTALL)
                if json_match:
                    cleaned_response = json_match.group(0)
                
                try:
                    qa_result = json.loads(cleaned_response)
                    answer = qa_result.get("answer", "Unable to generate answer")
                    reasoning = qa_result.get("reasoning", ["IBM watsonx.ai analysis"])
                    
                    print(f"✅ IBM watsonx.ai Q&A completed")
                    
                    return QAResponse(
                        question=question,
                        answer=answer,
                        reasoning=reasoning,
                        timestamp=current_time,
                    )
                    
                except json.JSONDecodeError as je:
                    print(f"⚠️  JSON parse error in Q&A: {je}")
                    print(f"   Response snippet: {cleaned_response[:200]}")
                    # Use the raw response as answer
                    model_name_for_log = os.getenv("WATSONX_MODEL_ID", "ibm/granite-3-8b-instruct")
                    return QAResponse(
                        question=question,
                        answer=response.strip(),
                        reasoning=[f"IBM watsonx.ai {model_name_for_log} (raw response)"],
                        timestamp=current_time,
                    )
                
            except Exception as e:
                print(f"⚠️  IBM watsonx.ai Q&A error: {type(e).__name__}: {str(e)}")
                print("   Falling back to rule-based Q&A...")
                # Fall through to rule-based Q&A below

        # === FALLBACK: RULE-BASED Q&A ===
        question_lower = question.lower()

        # Answer based on question content
        if "risk" in question_lower or "at risk" in question_lower:
            reasoning = [
                "Analyzed blockers and deadline changes",
                "Identified dependency chain",
                "Calculated timeline impact",
            ]

            if state.blockers:
                first_blocker = state.blockers[0]
                answer = (
                    f"Yes, the project has identified risks. "
                    f"The primary blocker is: '{first_blocker['description']}'. "
                    f"This is blocking critical work and could cause a 1-2 day slip in the timeline. "
                    f"Current project status is {state.status}. "
                    f"We have {len(state.blockers)} active blocker(s) and {len(state.risks)} identified risk(s)."
                )
            else:
                answer = (
                    f"The project status is currently {state.status}. "
                    f"We have {len(state.risks)} identified risk(s). "
                    f"No active blockers at this time."
                )

        elif "blocker" in question_lower or "blocked" in question_lower:
            reasoning = [
                "Scanned recent Slack and Jira events",
                "Identified blocked dependencies",
            ]

            if state.blockers:
                blocker_list = "\n".join(
                    [
                        f"- {b['description']} (from {b['source']})"
                        for b in state.blockers
                    ]
                )
                answer = (
                    f"The following blockers have been identified:\n{blocker_list}\n\n"
                    f"Total active blockers: {len(state.blockers)}"
                )
            else:
                answer = "No active blockers have been identified. The team is progressing smoothly."

        elif "status" in question_lower or "how" in question_lower:
            reasoning = ["Analyzed project state", "Calculated metrics"]

            answer = (
                f"Project status is {state.status}. "
                f"Completed items today: {len(state.completed_today)}. "
                f"Active blockers: {len(state.blockers)}. "
                f"Identified risks: {len(state.risks)}. "
                f"Next deadline: {state.next_deadline}."
            )

        else:
            # Default generic answer
            reasoning = ["Analyzed project state"]
            answer = (
                f"Based on the current analysis, the project status is {state.status}. "
                f"There are {len(state.blockers)} active blocker(s), "
                f"{len(state.risks)} identified risk(s), and "
                f"{len(state.completed_today)} item(s) completed today."
            )

        return QAResponse(
            question=question,
            answer=answer,
            reasoning=reasoning,
            timestamp=current_time,
        )


# ============================================================================
# ORCHESTRATE BRIDGE CLASS
# ============================================================================


class OrchestrateBridge:
    """
    Execute IBM watsonx Orchestrate digital labor skills.

    In production, this would call IBM watsonx Orchestrate APIs to execute
    automated skills. For the demo, it simulates most skills but implements
    real Slack webhook notifications.
    """

    @staticmethod
    async def execute_skill(skill_name: str, payload: Dict[str, Any]) -> Action:
        """
        Execute Orchestrate skills.

        Implements three core skills:
        1. notify_user: Send Slack notifications (real webhook)
        2. create_task: Create Jira tasks (simulated)
        3. generate_report: Generate status reports (simulated)

        Args:
            skill_name: Name of the skill to execute
            payload: Skill-specific parameters

        Returns:
            Action object representing the executed skill

        Raises:
            HTTPException: If skill name is unknown
        """
        # Generate timestamp for action ID
        timestamp_id = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
        current_time = datetime.utcnow().isoformat() + "Z"

        if skill_name == "notify_user":
            # Real Slack webhook integration
            slack_webhook_url = os.getenv("SLACK_WEBHOOK_URL")

            if slack_webhook_url:
                try:
                    async with httpx.AsyncClient() as client:
                        await client.post(
                            slack_webhook_url,
                            json={
                                "text": payload.get(
                                    "message", "Notification from FlowSentinel"
                                )
                            },
                            timeout=5.0,
                        )
                    print(
                        f"✅ Slack notification sent: {payload.get('message', '')[:50]}..."
                    )
                except Exception as e:
                    # Don't crash if webhook fails, just log it
                    print(f"⚠️ Slack webhook failed: {str(e)}")
            else:
                print(
                    f"ℹ️ Slack webhook not configured. Would send: {payload.get('message', '')}"
                )

            return Action(
                id=f"action_{timestamp_id}",
                type="notify_user",
                status="sent",
                payload=payload,
                timestamp=current_time,
            )

        elif skill_name == "create_task":
            # Simulated Jira task creation
            print(f"📋 Task would be created in Jira: {payload}")

            return Action(
                id=f"action_{timestamp_id}",
                type="create_task",
                status="created",
                payload=payload,
                timestamp=current_time,
            )

        elif skill_name == "generate_report":
            # Simulated report generation
            print(f"📊 Report generated: {payload}")

            return Action(
                id=f"action_{timestamp_id}",
                type="generate_report",
                status="completed",
                payload=payload,
                timestamp=current_time,
            )

        else:
            raise HTTPException(status_code=400, detail=f"Unknown skill: {skill_name}")


# ============================================================================
# FASTAPI APPLICATION
# ============================================================================

app = FastAPI(
    title="FlowSentinel API",
    version="2.0.0",
    description="Agentic Company Brain powered by IBM watsonx - Real-time monitoring, AI predictions, and automated actions",
)

# Add CORS middleware to allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers for all features (routers already have their own prefixes)
if ANALYTICS_ENABLED:
    app.include_router(analytics_router, tags=["analytics"])
    
if TEAMS_ENABLED:
    app.include_router(team_router, tags=["teams"])
    
if WEBHOOKS_ENABLED:
    app.include_router(webhook_router, tags=["webhooks"])
    
if INTELLIGENCE_ENABLED:
    app.include_router(intelligence_router, tags=["intelligence"])

if RAG_ENABLED:
    app.include_router(rag_router, tags=["rag"])

if AGENT_ENABLED:
    app.include_router(agent_router, tags=["agent"])

if FEEDBACK_ENABLED:
    app.include_router(feedback_router, tags=["feedback"])

if PATTERNS_ENABLED:
    app.include_router(pattern_router, tags=["patterns"])

if STREAMING_ENABLED:
    app.include_router(streaming_router, tags=["streaming"])


# ============================================================================
# API ENDPOINTS
# ============================================================================


@app.get("/")
async def root():
    """Root endpoint - Complete API information."""
    return {
        "service": "FlowSentinel API",
        "version": "2.0.0",
        "description": "Agentic Company Brain powered by IBM watsonx",
        "features": [
            "Real-time event monitoring",
            "IBM watsonx.ai analysis",
            "Automated actions via Orchestrate",
            "Advanced analytics" if ANALYTICS_ENABLED else None,
            "Team management" if TEAMS_ENABLED else None,
            "Webhook notifications" if WEBHOOKS_ENABLED else None,
            "Predictive intelligence" if INTELLIGENCE_ENABLED else None,
            "Risk scoring",
        ],
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "events": "/events/ingest",
            "simulation": "/simulation/run",
            "agent": "/agent/run",
            "state": "/state/latest",
            "qa": "/qa/ask",
            "analytics": "/analytics/summary" if ANALYTICS_ENABLED else None,
            "teams": "/teams" if TEAMS_ENABLED else None,
            "webhooks": "/webhooks" if WEBHOOKS_ENABLED else None,
            "intelligence": "/intelligence/predict-deadline-risk" if INTELLIGENCE_ENABLED else None,
        },
        "status": {
            "database": "enabled" if DATABASE_ENABLED else "in-memory",
            "analytics": "enabled" if ANALYTICS_ENABLED else "disabled",
            "teams": "enabled" if TEAMS_ENABLED else "disabled",
            "webhooks": "enabled" if WEBHOOKS_ENABLED else "disabled",
            "intelligence": "enabled" if INTELLIGENCE_ENABLED else "disabled",
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint with system metrics."""
    return {
        "status": "healthy",
        "events_count": len(db.events),
        "actions_count": len(db.actions),
        "has_state": db.state is not None,
    }


@app.post("/events/ingest")
async def ingest_event(
    event: Event,
    background_tasks: BackgroundTasks,
    team_id: Optional[str] = None,
    db_session: Session = Depends(get_db)
):
    """
    Ingest a single event from any source.

    Args:
        event: Event object to ingest
        background_tasks: FastAPI background tasks for webhook triggering
        team_id: Optional team ID to associate with event
        db_session: Database session for persistence

    Returns:
        Success status and event ID
    """
    # Add to in-memory database
    db.add_event(event)
    
    # Add to SQL database if enabled
    if DATABASE_ENABLED and db_session:
        try:
            db_event = EventDB(
                id=event.id,
                source=event.source,
                type=event.type,
                timestamp=datetime.fromisoformat(event.timestamp.replace('Z', '+00:00')),
                data=event.data,
                processed=event.processed,
                team_id=team_id
            )
            db_session.add(db_event)
            db_session.commit()
        except Exception as e:
            print(f"⚠️  Failed to save event to database: {e}")
            db_session.rollback()
    
    # Trigger webhooks in background
    if WEBHOOKS_ENABLED and trigger_webhooks and db_session:
        payload = {
            "event_type": "event.created",
            "event_id": event.id,
            "source": event.source,
            "type": event.type,
            "timestamp": event.timestamp,
            "data": event.data,
            "team_id": team_id
        }
        
        background_tasks.add_task(trigger_webhooks, "event.created", payload, db_session)
    
    return {
        "status": "success",
        "event_id": event.id,
        "team_id": team_id,
        "storage": "database" if DATABASE_ENABLED else "in-memory"
    }


@app.post("/events/ingest/batch")
async def ingest_events_batch(
    events: List[Event],
    background_tasks: BackgroundTasks,
    team_id: Optional[str] = None,
    db_session: Session = Depends(get_db)
):
    """
    Ingest multiple events at once.

    Args:
        events: List of event objects to ingest
        background_tasks: FastAPI background tasks for webhook triggering
        team_id: Optional team ID to associate with events
        db_session: Database session for persistence

    Returns:
        Success status and count of ingested events
    """
    for event in events:
        # Add to in-memory database
        db.add_event(event)
        
        # Add to SQL database if enabled
        if DATABASE_ENABLED and db_session:
            try:
                db_event = EventDB(
                    id=event.id,
                    source=event.source,
                    type=event.type,
                    timestamp=datetime.fromisoformat(event.timestamp.replace('Z', '+00:00')),
                    data=event.data,
                    processed=event.processed,
                    team_id=team_id
                )
                db_session.add(db_event)
            except Exception as e:
                print(f"⚠️  Failed to save event {event.id} to database: {e}")
        
        # Trigger webhooks for each event in background
        if WEBHOOKS_ENABLED and trigger_webhooks and db_session:
            payload = {
                "event_type": "event.created",
                "event_id": event.id,
                "source": event.source,
                "type": event.type,
                "timestamp": event.timestamp,
                "data": event.data,
                "team_id": team_id
            }
            
            background_tasks.add_task(trigger_webhooks, "event.created", payload, db_session)
    
    # Commit all events at once if database enabled
    if DATABASE_ENABLED and db_session:
        try:
            db_session.commit()
        except Exception as e:
            print(f"⚠️  Failed to commit batch events: {e}")
            db_session.rollback()

    return {
        "status": "success",
        "count": len(events),
        "team_id": team_id,
        "storage": "database" if DATABASE_ENABLED else "in-memory"
    }


@app.get("/events/list")
async def list_events(limit: int = 50):
    """
    List recent events.

    Args:
        limit: Maximum number of events to return (default: 50)

    Returns:
        List of events and total count
    """
    events = db.get_events(limit)
    return {"events": events, "count": len(events)}


@app.post("/simulation/run")
async def run_simulation(db_session: Session = Depends(get_db)):
    """
    Load hardcoded simulation data for demo purposes.

    Creates 8 realistic events representing a typical day:
    - Slack messages about blockers
    - Jira task updates and delays
    - GitHub PR activities
    - Calendar changes

    Returns:
        Success status and event count
    """
    # Create hardcoded events for simulation
    simulation_events = [
        Event(
            id="evt_001",
            source="slack",
            type="message",
            timestamp="2024-03-20T14:10:00Z",
            data={
                "user": "PM",
                "message": "Backend is blocked waiting on design schema",
            },
        ),
        Event(
            id="evt_002",
            source="jira",
            type="task_status_changed",
            timestamp="2024-03-20T14:11:00Z",
            data={
                "task": "Landing Page Schema",
                "old_status": "In Progress",
                "new_status": "Delayed",
            },
        ),
        Event(
            id="evt_003",
            source="github",
            type="pr_opened",
            timestamp="2024-03-20T14:12:00Z",
            data={"pr_number": 42, "title": "API Integration", "author": "dev_alice"},
        ),
        Event(
            id="evt_004",
            source="slack",
            type="message",
            timestamp="2024-03-20T14:15:00Z",
            data={"user": "Designer", "message": "Schema will be ready in 2 hours"},
        ),
        Event(
            id="evt_005",
            source="calendar",
            type="meeting_moved",
            timestamp="2024-03-20T14:20:00Z",
            data={"meeting": "Sprint Review", "old_time": "16:00", "new_time": "17:00"},
        ),
        Event(
            id="evt_006",
            source="jira",
            type="deadline_changed",
            timestamp="2024-03-20T14:25:00Z",
            data={"task": "API Integration", "new_deadline": "2024-03-25T17:00:00Z"},
        ),
        Event(
            id="evt_007",
            source="github",
            type="pr_review_requested",
            timestamp="2024-03-20T14:30:00Z",
            data={"pr_number": 42, "reviewer": "tech_lead", "status": "pending"},
        ),
        Event(
            id="evt_008",
            source="slack",
            type="message",
            timestamp="2024-03-20T14:35:00Z",
            data={"user": "QA", "message": "PR #42 needs review urgently"},
        ),
    ]

    # Add events to in-memory database
    for event in simulation_events:
        db.add_event(event)

    # Also add to SQL database if enabled
    if DATABASE_ENABLED and db_session:
        try:
            for event in simulation_events:
                db_event = EventDB(
                    id=event.id,
                    source=event.source,
                    type=event.type,
                    timestamp=datetime.fromisoformat(event.timestamp.replace('Z', '+00:00')),
                    data=event.data,
                    processed=event.processed
                )
                db_session.add(db_event)
            db_session.commit()
        except Exception as e:
            print(f"⚠️  Failed to save to database: {e}")
            db_session.rollback()

    return {
        "status": "success",
        "events_created": 8,
        "message": "Simulation loaded successfully",
        "storage": "database" if DATABASE_ENABLED else "in-memory"
    }


@app.post("/agent/run")
async def run_agent(
    background_tasks: BackgroundTasks,
    db_session: Session = Depends(get_db)
):
    """
    Run the watsonx.ai agent to analyze events and trigger actions.

    This is the core orchestration endpoint that:
    1. Retrieves recent events
    2. Analyzes them using watsonx.ai
    3. Updates project state
    4. Triggers appropriate actions via Orchestrate

    Args:
        background_tasks: FastAPI background tasks for webhook triggering
        db_session: Database session for webhook triggering

    Returns:
        Analysis results, updated state, and triggered actions

    Raises:
        HTTPException: If no events available to analyze
    """
    # Get recent events
    events = db.get_events(100)

    if not events:
        raise HTTPException(
            status_code=400,
            detail="No events to analyze. Please ingest events first or run simulation.",
        )

    # Analyze events with watsonx.ai
    state = await WatsonxAgent.analyze_state(events)

    # Send Slack alert if status is YELLOW or RED
    if state.status in ("YELLOW", "RED"):
        try:
            lines = [f"🚨 *FlowSentinel Alert*", f"Project status: *{state.status}*", ""]
            
            if state.blockers:
                lines.append(f"*Blockers ({len(state.blockers)}):*")
                for b in state.blockers[:3]:
                    desc = b.get("description", "")
                    lines.append(f"• {shorten(desc, width=90, placeholder='...')}")
                lines.append("")
            
            if state.risks:
                lines.append(f"*Risks ({len(state.risks)}):*")
                for r in state.risks[:2]:
                    desc = r.get("description", "")
                    lines.append(f"• {shorten(desc, width=90, placeholder='...')}")
                lines.append("")
            
            send_slack_alert("\n".join(lines))
        except Exception as e:
            print(f"⚠️  Failed to build/send Slack alert: {e}")

    # Save updated state to in-memory
    db.update_state(state)
    
    # Save to database if enabled
    if DATABASE_ENABLED and db_session:
        try:
            db_state = ProjectStateDB(
                status=state.status,
                blockers=state.blockers,
                risks=state.risks,
                completed_today=state.completed_today,
                next_deadline=state.next_deadline,
                last_updated=datetime.fromisoformat(state.last_updated.replace('Z', '+00:00'))
            )
            db_session.add(db_state)
            db_session.commit()
        except Exception as e:
            print(f"⚠️  Failed to save state to database: {e}")
            db_session.rollback()
    
    # Trigger state.changed webhook
    if WEBHOOKS_ENABLED and trigger_webhooks and db_session:
        state_payload = {
            "event_type": "state.changed",
            "status": state.status,
            "blockers_count": len(state.blockers),
            "risks_count": len(state.risks),
            "completed_today": len(state.completed_today),
            "next_deadline": state.next_deadline,
            "timestamp": datetime.now().isoformat()
        }
        
        background_tasks.add_task(trigger_webhooks, "state.changed", state_payload, db_session)

    # Trigger actions based on state
    actions_triggered = []

    # If there are blockers, notify team
    if state.blockers:
        first_blocker = state.blockers[0]
        action = await OrchestrateBridge.execute_skill(
            "notify_user",
            {
                "message": f"🚨 BLOCKER DETECTED: {first_blocker['description']}",
                "channel": "#project-alerts",
                "priority": "high",
            },
        )
        db.add_action(action)
        actions_triggered.append(action)
        
        # Save action to database if enabled
        if DATABASE_ENABLED and db_session:
            try:
                db_action = ActionDB(
                    id=action.id,
                    type=action.type,
                    status=action.status,
                    payload=action.payload,
                    timestamp=datetime.fromisoformat(action.timestamp.replace('Z', '+00:00'))
                )
                db_session.add(db_action)
                db_session.commit()
            except Exception as e:
                print(f"⚠️  Failed to save action to database: {e}")
                db_session.rollback()
        
        # Trigger action.taken webhook for blocker notification
        if WEBHOOKS_ENABLED and trigger_webhooks and db_session:
            action_payload = {
                "event_type": "action.taken",
                "action_type": action.type,
                "action_id": action.id,
                "status": action.status,
                "payload": action.payload,
                "timestamp": datetime.now().isoformat()
            }
            
            background_tasks.add_task(trigger_webhooks, "action.taken", action_payload, db_session)

    # If status is RED, escalate by creating a task
    if state.status == "RED":
        action = await OrchestrateBridge.execute_skill(
            "create_task",
            {
                "title": "URGENT: Multiple blockers detected",
                "description": f"Project status is RED. Blockers: {len(state.blockers)}, Risks: {len(state.risks)}",
                "priority": "critical",
                "assignee": "tech_lead",
            },
        )
        db.add_action(action)
        actions_triggered.append(action)

    # Always generate a status report
    action = await OrchestrateBridge.execute_skill(
        "generate_report",
        {
            "type": "status_summary",
            "status": state.status,
            "blockers_count": len(state.blockers),
            "risks_count": len(state.risks),
            "completed_count": len(state.completed_today),
            "next_deadline": state.next_deadline,
        },
    )
    db.add_action(action)
    actions_triggered.append(action)

    return {
        "status": "success",
        "state": state,
        "actions_triggered": len(actions_triggered),
    }


@app.get("/state/latest")
async def get_latest_state():
    """
    Get the most recent project state.

    Returns:
        Current ProjectState object

    Raises:
        HTTPException: If no state has been calculated yet
    """
    state = db.get_state()

    if not state:
        raise HTTPException(
            status_code=404,
            detail="No state available. Run agent first using POST /agent/run",
        )

    return state


@app.post("/debug/slack-test")
async def debug_slack_test():
    """
    Simple endpoint to verify Slack integration works.
    
    Returns:
        Success message indicating test alert was sent
    """
    send_slack_alert("✅ FlowSentinel Slack test: integration is working.")
    return {"ok": True, "message": "Slack test alert sent (if webhook is configured)."}


# ============================================================================
# AUTONOMOUS AGENT CONTROL ENDPOINTS
# ============================================================================

@app.post("/agent/start")
async def start_autonomous_agent():
    """
    Start the autonomous background agent.
    
    The agent will continuously monitor project state and send alerts
    every AGENT_RUN_INTERVAL seconds (default: 5 minutes).
    
    Returns:
        Status message and agent configuration
    """
    global agent_running, agent_task
    
    if agent_running:
        return {
            "ok": False,
            "message": "Agent is already running",
            "status": "running",
            "run_count": agent_run_count,
            "last_run": agent_last_run.isoformat() if agent_last_run else None,
            "interval_seconds": AGENT_RUN_INTERVAL
        }
    
    # Start the agent
    agent_task = asyncio.create_task(autonomous_agent_loop())
    
    return {
        "ok": True,
        "message": "Autonomous agent started successfully",
        "status": "started",
        "interval_seconds": AGENT_RUN_INTERVAL,
        "next_run": "in progress"
    }


@app.post("/agent/stop")
async def stop_autonomous_agent():
    """
    Stop the autonomous background agent.
    
    Returns:
        Status message with agent statistics
    """
    global agent_running, agent_task
    
    if not agent_running:
        return {
            "ok": False,
            "message": "Agent is not running",
            "status": "stopped"
        }
    
    # Stop the agent
    agent_running = False
    
    # Wait for the task to complete (with timeout)
    if agent_task:
        try:
            await asyncio.wait_for(agent_task, timeout=5.0)
        except asyncio.TimeoutError:
            print("⚠️  Agent task did not stop gracefully - forcing cancellation")
            agent_task.cancel()
    
    return {
        "ok": True,
        "message": "Autonomous agent stopped successfully",
        "status": "stopped",
        "total_runs": agent_run_count,
        "last_run": agent_last_run.isoformat() if agent_last_run else None
    }


@app.get("/agent/status")
async def get_agent_status():
    """
    Get the current status of the autonomous agent.
    
    Returns:
        Agent status, configuration, and runtime statistics
    """
    global agent_running, agent_last_run, agent_run_count
    
    next_run = None
    if agent_running and agent_last_run:
        next_run_time = agent_last_run + timedelta(seconds=AGENT_RUN_INTERVAL)
        seconds_until_next = (next_run_time - datetime.now()).total_seconds()
        next_run = {
            "timestamp": next_run_time.isoformat(),
            "seconds_remaining": max(0, int(seconds_until_next))
        }
    
    return {
        "enabled": AGENT_ENABLED,
        "running": agent_running,
        "run_count": agent_run_count,
        "last_run": agent_last_run.isoformat() if agent_last_run else None,
        "next_run": next_run,
        "config": {
            "interval_seconds": AGENT_RUN_INTERVAL,
            "interval_minutes": AGENT_RUN_INTERVAL / 60
        }
    }


@app.get("/actions/list")
async def list_actions(limit: int = 50):
    """
    List recent actions taken by the system.

    Args:
        limit: Maximum number of actions to return (default: 50)

    Returns:
        List of actions and total count
    """
    actions = db.get_actions(limit)
    return {"actions": actions, "count": len(actions)}


@app.post("/qa/ask")
async def ask_question(request: QARequest):
    """
    Ask questions about the project state using natural language.

    Uses watsonx.ai to generate intelligent answers based on:
    - Current project state
    - Recent events
    - Historical patterns

    Args:
        request: QARequest containing the question

    Returns:
        QAResponse with answer and reasoning

    Raises:
        HTTPException: If no state is available to answer questions
    """
    # Get current state
    state = db.get_state()

    if not state:
        raise HTTPException(
            status_code=400,
            detail="No state available. Run agent first using POST /agent/run",
        )

    # Get recent events for context
    events = db.get_events(100)

    # Generate answer using watsonx.ai
    qa = await WatsonxAgent.answer_question(request.question, state, events)

    # Save to history
    db.add_qa(qa)

    return qa


# ============================================================================
# AUTONOMOUS AGENT LOOP
# ============================================================================

async def autonomous_agent_loop():
    """
    Autonomous background agent that continuously monitors project state.
    
    Runs every AGENT_RUN_INTERVAL seconds and:
    1. Fetches recent events
    2. Analyzes project state with IBM Granite AI
    3. Sends Slack alerts on YELLOW/RED status
    4. Triggers automated actions for critical issues
    5. Logs all operations for monitoring
    """
    global agent_running, agent_last_run, agent_run_count
    
    agent_running = True
    print(f"\n🤖 Autonomous Agent: Started (interval: {AGENT_RUN_INTERVAL}s)")
    
    while agent_running:
        try:
            agent_run_count += 1
            agent_last_run = datetime.now()
            
            print(f"\n{'='*70}")
            print(f"🤖 Autonomous Agent Run #{agent_run_count} - {agent_last_run.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"{'='*70}")
            
            # 1. Fetch recent events (last 24 hours)
            cutoff_time = datetime.now() - timedelta(hours=24)
            recent_events = [e for e in db.events if datetime.fromisoformat(e["timestamp"]) > cutoff_time]
            
            print(f"📊 Found {len(recent_events)} events in last 24h")
            
            if len(recent_events) == 0:
                print("⏭️  No recent events - skipping analysis")
            else:
                # 2. Analyze with IBM Granite AI
                print("🧠 Analyzing with IBM watsonx.ai Granite...")
                state = await WatsonxAgent.analyze_state(recent_events)
                
                print(f"   Status: {state.status}")
                print(f"   Blockers: {len(state.blockers)}")
                print(f"   Risks: {len(state.risks)}")
                print(f"   Completed: {len(state.completed)}")
                
                # 3. Send Slack alerts on YELLOW/RED status
                if state.status in ["YELLOW", "RED"]:
                    status_emoji = "⚠️" if state.status == "YELLOW" else "🚨"
                    alert_text = f"{status_emoji} *FlowSentinel Autonomous Alert*\n\n"
                    alert_text += f"*Status:* {state.status}\n"
                    alert_text += f"*Time:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                    alert_text += f"*Run:* #{agent_run_count}\n\n"
                    
                    if state.blockers:
                        alert_text += f"*🚫 Blockers ({len(state.blockers)}):*\n"
                        for blocker in state.blockers[:3]:  # Top 3
                            alert_text += f"  • {blocker}\n"
                    
                    if state.risks:
                        alert_text += f"\n*⚠️ Risks ({len(state.risks)}):*\n"
                        for risk in state.risks[:3]:  # Top 3
                            alert_text += f"  • {risk}\n"
                    
                    if state.actions:
                        alert_text += f"\n*💡 Suggested Actions:*\n"
                        for action in state.actions[:2]:  # Top 2
                            alert_text += f"  • {action.action}\n"
                    
                    # Send alert
                    send_slack_alert(alert_text)
                    print(f"✅ Slack alert sent ({state.status})")
                
                # 4. Trigger critical actions
                critical_actions = [a for a in state.actions if a.priority in ["high", "critical"]]
                if critical_actions:
                    print(f"\n🎯 Triggering {len(critical_actions)} critical actions...")
                    for action in critical_actions[:3]:  # Max 3 per run
                        print(f"   → {action.action} (Priority: {action.priority})")
                        # Note: orchestrate.execute_action is simulated
                        # In production, integrate with real IBM Orchestrate or other automation
                
                # 5. Save state to database
                if DATABASE_ENABLED:
                    try:
                        from models import ProjectStateDB
                        with next(get_db()) as db_session:
                            db_state = ProjectStateDB(
                                status=state.status,
                                blockers=state.blockers,
                                risks=state.risks,
                                completed=state.completed,
                                next_steps=[a.action for a in state.actions[:5]],
                                metadata={
                                    "agent_run": agent_run_count,
                                    "events_analyzed": len(recent_events),
                                    "auto_triggered": True
                                }
                            )
                            db_session.add(db_state)
                            db_session.commit()
                            print("💾 State saved to database")
                    except Exception as e:
                        print(f"⚠️  Database save failed: {e}")
            
            print(f"\n✅ Agent run #{agent_run_count} complete")
            print(f"⏰ Next run in {AGENT_RUN_INTERVAL}s...")
            
            # 6. Sleep until next interval
            await asyncio.sleep(AGENT_RUN_INTERVAL)
            
        except Exception as e:
            print(f"\n❌ Agent error: {e}")
            import traceback
            traceback.print_exc()
            print(f"⏰ Retrying in {AGENT_RUN_INTERVAL}s...")
            await asyncio.sleep(AGENT_RUN_INTERVAL)
    
    print("\n🛑 Autonomous Agent: Stopped")


# ============================================================================
# STARTUP EVENT
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize database and print startup information."""
    # Initialize database if enabled
    if DATABASE_ENABLED:
        try:
            init_db()
            print("🗄️  Database initialized")
            
            # Test database connection
            test_connection()
        except Exception as e:
            print(f"⚠️  Database initialization failed: {e}")
    
    # Print feature list
    print("\n" + "=" * 70)
    print("🚀 FlowSentinel Backend v2.0 Started")
    print("=" * 70)
    print("📊 Dashboard: http://localhost:8000/docs")
    print("🔗 API Root: http://localhost:8000/")
    print()
    
    # IBM watsonx.ai status
    api_key = os.getenv("WATSONX_API_KEY", "")
    project_id = os.getenv("WATSONX_PROJECT_ID", "")
    
    print("\n" + "=" * 60)
    if IBM_SDK_AVAILABLE and api_key and project_id and len(api_key) > 20:
        print("🧠 IBM WATSONX.AI: ✅ REAL API ENABLED")
        print(f"   Project ID: {project_id[:20]}...")
        print(f"   Region: {os.getenv('WATSONX_URL', 'not set')}")
        print(f"   Model: {os.getenv('WATSONX_MODEL_ID', 'ibm/granite-3-8b-instruct')}")
    else:
        print("⚠️  IBM WATSONX.AI: Simulation Mode")
        print("   Add credentials to .env to enable real AI:")
        print("   1. WATSONX_API_KEY=your-key")
        print("   2. WATSONX_PROJECT_ID=your-project-id")
    print("=" * 60 + "\n")
    
    print("🤖 Orchestrate: Ready")
    print(f"💾 Database: {'SQLite' if DATABASE_ENABLED else 'In-Memory (MVP)'}")
    print()
    print("📈 Analytics: " + ("Enabled ✅" if ANALYTICS_ENABLED else "Disabled ⚠️"))
    print("👥 Teams: " + ("Enabled ✅" if TEAMS_ENABLED else "Disabled ⚠️"))
    print("🔔 Webhooks: " + ("Enabled ✅" if WEBHOOKS_ENABLED else "Disabled ⚠️"))
    print("🔮 Predictions: " + ("Enabled ✅" if INTELLIGENCE_ENABLED else "Disabled ⚠️"))
    print()
    
    if os.getenv("SLACK_WEBHOOK_URL"):
        print("✅ Slack Webhook: Configured")
    else:
        print("⚠️  Slack Webhook: Not configured (set SLACK_WEBHOOK_URL)")
    
    print("=" * 70 + "\n")
    
    # Start autonomous agent if enabled
    global agent_task
    if AGENT_ENABLED:
        print("🤖 Starting Autonomous Agent...")
        print(f"   Interval: {AGENT_RUN_INTERVAL} seconds ({AGENT_RUN_INTERVAL / 60:.1f} minutes)")
        print(f"   Control: POST /agent/start, /agent/stop, GET /agent/status")
        agent_task = asyncio.create_task(autonomous_agent_loop())
        print("✅ Autonomous Agent: Launched")
    else:
        print("⚠️  Autonomous Agent: Disabled (set AGENT_ENABLED=true)")
    
    print("=" * 70 + "\n")


def print_startup_info():
    """
    Print startup information (deprecated - replaced by startup_event).

    Displays helpful information when the server starts, including
    API documentation URL and system status.
    """
    # This function is kept for backward compatibility
    # but the actual startup logic is now in startup_event()
    pass


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    # Get port from environment variable (for cloud deployment)
    # Render, Heroku, Railway all use PORT env variable
    PORT = int(os.getenv("PORT", 8000))
    
    # Get environment mode
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    
    # Run the server with hot reload for development
    # Startup info is printed by startup_event()
    uvicorn.run(
        "main:app",  # Import string required for reload
        host="0.0.0.0",
        port=PORT,
        reload=(ENVIRONMENT == "development"),  # Only reload in dev
        log_level="info"
    )

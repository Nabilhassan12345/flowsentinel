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
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional
from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
import httpx

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
        Analyze events and generate project state.

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
        # Process last 20 events
        recent_events = events[:20] if len(events) > 20 else events

        blockers = []
        risks = []
        completed = []

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
        Generate intelligent answers to questions about project state.

        Uses natural language processing (simulated) to understand the question
        and provide detailed, contextual answers based on current project state.

        Args:
            question: The question to answer
            state: Current project state
            events: Recent events for additional context

        Returns:
            QAResponse with answer and reasoning
        """
        question_lower = question.lower()

        # Generate current timestamp
        current_time = datetime.utcnow().isoformat() + "Z"

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
    print("🧠 Watsonx.ai: Ready")
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

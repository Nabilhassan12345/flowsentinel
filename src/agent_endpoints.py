"""
FlowSentinel Agent API Endpoints

FastAPI router for interacting with the AI agent.

Endpoints:
- POST /agent/run - Run the agent with a user input
- POST /agent/process-event - Process an event with the agent
- GET /agent/status - Get agent status
- GET /agent/history - Get agent execution history
- POST /agent/confirm/{action_id} - Confirm a pending action
- PUT /agent/mode - Change agent mode
- GET /agent/tools - List available tools
- POST /agent/execute-tool - Execute a tool directly
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from agent import (
    FlowSentinelAgent,
    AgentMode,
    AgentResponse,
    get_agent,
    process_event_with_agent,
)
from agent_executor import get_agent_executor, safe_execute
from tools import get_tool_registry, execute_tool

router = APIRouter(prefix="/agent", tags=["agent"])


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================


class AgentRunRequest(BaseModel):
    """Request to run the agent"""
    input: str = Field(..., description="User input or query for the agent")
    context: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional context (events, project state, etc.)"
    )


class AgentRunResponse(BaseModel):
    """Response from agent run"""
    success: bool
    message: str
    final_answer: Optional[str]
    steps_taken: int
    actions_taken: List[Dict[str, Any]]
    total_time_ms: float


class ProcessEventRequest(BaseModel):
    """Request to process an event"""
    source: str = Field(..., description="Event source: slack, jira, github, calendar")
    type: str = Field(..., description="Event type")
    data: Dict[str, Any] = Field(..., description="Event data payload")
    timestamp: Optional[str] = Field(default=None, description="Event timestamp")


class AgentModeRequest(BaseModel):
    """Request to change agent mode"""
    mode: str = Field(
        ...,
        description="Agent mode: autonomous, supervised, advisory, disabled"
    )


class ToolExecuteRequest(BaseModel):
    """Request to execute a tool directly"""
    tool_name: str = Field(..., description="Name of the tool to execute")
    arguments: Dict[str, Any] = Field(
        default_factory=dict,
        description="Arguments to pass to the tool"
    )


class ConfirmActionRequest(BaseModel):
    """Request to confirm a pending action"""
    confirmed_by: str = Field(
        default="user",
        description="Who confirmed the action"
    )


class ToolInfo(BaseModel):
    """Information about a tool"""
    name: str
    description: str
    category: str
    requires_confirmation: bool
    parameters: Dict[str, Any]


class AgentStatusResponse(BaseModel):
    """Agent status response"""
    mode: str
    model_available: bool
    tools_available: int
    max_steps: int
    actions_taken: int
    pending_confirmations: int
    rate_limit_stats: Dict[str, Any]


# ============================================================================
# ENDPOINTS
# ============================================================================


@router.post(
    "/run",
    response_model=AgentRunResponse,
    summary="Run the agent",
    description="Execute the agent with a user input. The agent will observe, think, and potentially take actions."
)
async def run_agent(request: AgentRunRequest):
    """
    Run the FlowSentinel agent.
    
    The agent will:
    1. Analyze the input and context
    2. Reason about what actions to take
    3. Execute tools if in autonomous mode
    4. Return a response with actions taken
    """
    try:
        agent = get_agent()
        response = await agent.run(
            user_input=request.input,
            context=request.context
        )
        
        return AgentRunResponse(
            success=response.success,
            message=response.message,
            final_answer=response.final_answer,
            steps_taken=len(response.steps),
            actions_taken=response.actions_taken,
            total_time_ms=response.total_time_ms
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/process-event",
    response_model=AgentRunResponse,
    summary="Process an event",
    description="Have the agent process a project event and determine if any action is needed."
)
async def process_event(request: ProcessEventRequest):
    """
    Process a project event with the agent.
    
    Events can come from Slack, Jira, GitHub, or Calendar.
    The agent will analyze the event and take appropriate actions.
    """
    try:
        event = {
            "source": request.source,
            "type": request.type,
            "data": request.data,
            "timestamp": request.timestamp or datetime.utcnow().isoformat()
        }
        
        result = process_event_with_agent(event)
        
        return AgentRunResponse(
            success=result["success"],
            message=result["message"],
            final_answer=result.get("final_answer"),
            steps_taken=len(result.get("steps", [])),
            actions_taken=result.get("actions_taken", []),
            total_time_ms=result.get("total_time_ms", 0)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/status",
    response_model=AgentStatusResponse,
    summary="Get agent status",
    description="Get the current status of the agent including mode, available tools, and statistics."
)
async def get_agent_status():
    """Get current agent status and statistics."""
    try:
        agent = get_agent()
        executor = get_agent_executor()
        
        status = agent.get_status()
        executor_stats = executor.get_stats()
        
        return AgentStatusResponse(
            mode=status["mode"],
            model_available=status["model_available"],
            tools_available=status["tools_available"],
            max_steps=status["max_steps"],
            actions_taken=status["actions_taken"],
            pending_confirmations=executor_stats["pending_confirmations"],
            rate_limit_stats=executor_stats["rate_limits"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put(
    "/mode",
    summary="Change agent mode",
    description="Change the agent's operating mode (autonomous, supervised, advisory, disabled)."
)
async def set_agent_mode(request: AgentModeRequest):
    """
    Change the agent's operating mode.
    
    Modes:
    - autonomous: Agent acts without confirmation
    - supervised: Agent suggests actions, requires confirmation
    - advisory: Agent only provides advice, no actions
    - disabled: Agent is turned off
    """
    try:
        mode_map = {
            "autonomous": AgentMode.AUTONOMOUS,
            "supervised": AgentMode.SUPERVISED,
            "advisory": AgentMode.ADVISORY,
            "disabled": AgentMode.DISABLED
        }
        
        if request.mode not in mode_map:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid mode. Must be one of: {list(mode_map.keys())}"
            )
        
        agent = get_agent()
        agent.mode = mode_map[request.mode]
        
        return {
            "success": True,
            "message": f"Agent mode changed to {request.mode}",
            "mode": request.mode
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/tools",
    response_model=List[ToolInfo],
    summary="List available tools",
    description="Get a list of all tools available to the agent."
)
async def list_tools(
    category: Optional[str] = Query(
        default=None,
        description="Filter by category"
    )
):
    """List all available tools."""
    try:
        registry = get_tool_registry()
        tools = registry.list_tools(category=category)
        
        return [
            ToolInfo(
                name=tool.name,
                description=tool.description,
                category=tool.category,
                requires_confirmation=tool.requires_confirmation,
                parameters=tool.parameters
            )
            for tool in tools
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/execute-tool",
    summary="Execute a tool directly",
    description="Execute a specific tool without going through the agent reasoning loop."
)
async def execute_tool_endpoint(request: ToolExecuteRequest):
    """
    Execute a tool directly.
    
    This bypasses the agent reasoning and executes the tool immediately.
    Use with caution - this is typically for testing or manual intervention.
    """
    try:
        result = safe_execute(request.tool_name, request.arguments)
        
        return {
            "success": result.status.value == "success",
            "status": result.status.value,
            "message": result.message,
            "data": result.data,
            "execution_time_ms": result.execution_time_ms
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/history",
    summary="Get execution history",
    description="Get the history of agent actions and tool executions."
)
async def get_execution_history(
    limit: int = Query(default=50, le=200, description="Maximum records to return"),
    tool_name: Optional[str] = Query(default=None, description="Filter by tool name")
):
    """Get agent execution history."""
    try:
        executor = get_agent_executor()
        history = executor.get_execution_history(limit=limit, tool_name=tool_name)
        
        return {
            "total": len(history),
            "history": history
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/pending",
    summary="Get pending confirmations",
    description="Get all actions waiting for user confirmation."
)
async def get_pending_confirmations():
    """Get pending action confirmations."""
    try:
        executor = get_agent_executor()
        pending = executor.get_pending_confirmations()
        
        return {
            "count": len(pending),
            "pending": pending
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/confirm/{action_id}",
    summary="Confirm a pending action",
    description="Confirm a pending action to allow it to execute."
)
async def confirm_action(
    action_id: str,
    request: ConfirmActionRequest
):
    """Confirm and execute a pending action."""
    try:
        executor = get_agent_executor()
        result = executor.execute_confirmed(action_id, request.confirmed_by)
        
        if result is None:
            raise HTTPException(
                status_code=404,
                detail=f"Pending action not found: {action_id}"
            )
        
        tool_result, record = result
        
        return {
            "success": tool_result.status.value == "success",
            "status": tool_result.status.value,
            "message": tool_result.message,
            "data": tool_result.data,
            "confirmed_by": request.confirmed_by,
            "execution_time_ms": record.execution_duration_ms
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/reject/{action_id}",
    summary="Reject a pending action",
    description="Reject a pending action to prevent it from executing."
)
async def reject_action(
    action_id: str,
    reason: str = Query(default="User rejected", description="Rejection reason")
):
    """Reject a pending action."""
    try:
        executor = get_agent_executor()
        success = executor.confirmation_manager.reject(action_id, reason)
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"Pending action not found: {action_id}"
            )
        
        return {
            "success": True,
            "message": f"Action {action_id} rejected",
            "reason": reason
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/schemas",
    summary="Get tool schemas",
    description="Get OpenAI/watsonx compatible tool schemas for function calling."
)
async def get_tool_schemas(
    format: str = Query(
        default="openai",
        description="Schema format: openai or watsonx"
    )
):
    """Get tool schemas for function calling integration."""
    try:
        registry = get_tool_registry()
        schemas = registry.get_all_schemas(format=format)
        
        return {
            "format": format,
            "tools": schemas
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

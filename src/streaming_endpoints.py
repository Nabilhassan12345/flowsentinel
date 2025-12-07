"""
FlowSentinel Streaming API Endpoints

FastAPI router for Server-Sent Events (SSE) streaming.

Endpoints:
- GET /stream/chat - Stream chat response
- GET /stream/agent - Stream agent execution
- GET /stream/rag - Stream RAG-powered answer
- GET /stream/events - Subscribe to real-time events
"""

import asyncio
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from streaming import (
    StreamEventType,
    StreamEvent,
    get_streaming_llm,
    get_agent_streaming_runner,
    get_event_broadcaster,
)

router = APIRouter(prefix="/stream", tags=["streaming"])


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


async def event_generator(events_gen):
    """Convert async generator to SSE format"""
    async for event in events_gen:
        yield event.to_sse()


# ============================================================================
# ENDPOINTS
# ============================================================================


@router.get(
    "/chat",
    summary="Stream chat response",
    description="Stream an AI response token by token using Server-Sent Events."
)
async def stream_chat(
    query: str = Query(..., description="User query"),
    context: Optional[str] = Query(default=None, description="Additional context")
):
    """
    Stream a chat response.
    
    Returns Server-Sent Events with tokens as they're generated.
    
    Event format:
    ```
    data: {"type": "token", "data": "Hello", "timestamp": "..."}
    
    data: {"type": "complete", "data": {"total_tokens": 50}}
    ```
    """
    llm = get_streaming_llm()
    
    prompt = query
    if context:
        prompt = f"Context: {context}\n\nQuery: {query}"
    
    async def generate():
        async for event in llm.stream_generate(prompt):
            yield event.to_sse()
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable nginx buffering
        }
    )


@router.get(
    "/agent",
    summary="Stream agent execution",
    description="Stream the agent's thinking process and actions in real-time."
)
async def stream_agent(
    query: str = Query(..., description="User query for the agent"),
    include_thinking: bool = Query(default=True, description="Include thinking steps")
):
    """
    Stream agent execution.
    
    Events include:
    - thinking: Agent's reasoning process
    - tool_call: When agent calls a tool
    - tool_result: Result of tool execution
    - token: Response generation
    - complete: Execution finished
    """
    runner = get_agent_streaming_runner()
    
    async def generate():
        async for event in runner.run_streaming(query):
            # Optionally filter thinking events
            if not include_thinking and event.type == StreamEventType.THINKING:
                continue
            yield event.to_sse()
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive"
        }
    )


@router.get(
    "/rag",
    summary="Stream RAG answer",
    description="Stream a RAG-powered answer showing retrieval and generation."
)
async def stream_rag_answer(
    question: str = Query(..., description="Question to answer"),
    show_progress: bool = Query(default=True, description="Show progress updates")
):
    """
    Stream a RAG-powered answer.
    
    Events include:
    - progress: Retrieval and processing progress
    - token: Answer generation
    - complete: Generation finished
    """
    runner = get_agent_streaming_runner()
    
    # Mock some context events (in production, this would query the RAG pipeline)
    context_events = [
        {"source": "slack", "data": {"message": "Backend API is ready for testing"}},
        {"source": "jira", "data": {"message": "TASK-123: Authentication module complete"}}
    ]
    
    async def generate():
        async for event in runner.stream_rag_answer(question, context_events):
            if not show_progress and event.type == StreamEventType.PROGRESS:
                continue
            yield event.to_sse()
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive"
        }
    )


@router.get(
    "/events",
    summary="Subscribe to real-time events",
    description="Subscribe to real-time project events and agent actions."
)
async def subscribe_to_events():
    """
    Subscribe to real-time events.
    
    Long-running SSE connection that receives:
    - New project events
    - Agent actions
    - Status changes
    - Notifications
    
    Keep the connection open to receive updates.
    """
    broadcaster = get_event_broadcaster()
    
    async def generate():
        # Send initial connection event
        yield StreamEvent(
            type=StreamEventType.PROGRESS,
            data={"message": "Connected to event stream"},
            metadata={"subscribers": broadcaster.subscriber_count + 1}
        ).to_sse()
        
        # Subscribe and stream events
        async for event in broadcaster.subscribe():
            yield event.to_sse()
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive"
        }
    )


@router.post(
    "/broadcast",
    summary="Broadcast an event",
    description="Broadcast an event to all connected clients (for testing/admin)."
)
async def broadcast_event(
    event_type: str = Query(..., description="Event type"),
    message: str = Query(..., description="Event message")
):
    """
    Broadcast an event to all subscribers.
    
    Useful for testing SSE connections and sending notifications.
    """
    broadcaster = get_event_broadcaster()
    
    # Map string to event type
    type_map = {
        "token": StreamEventType.TOKEN,
        "thinking": StreamEventType.THINKING,
        "tool_call": StreamEventType.TOOL_CALL,
        "tool_result": StreamEventType.TOOL_RESULT,
        "progress": StreamEventType.PROGRESS,
        "complete": StreamEventType.COMPLETE,
        "error": StreamEventType.ERROR
    }
    
    ev_type = type_map.get(event_type, StreamEventType.PROGRESS)
    
    await broadcaster.broadcast_event(
        event_type=ev_type,
        data={"message": message}
    )
    
    return {
        "success": True,
        "message": f"Event broadcast to {broadcaster.subscriber_count} subscribers",
        "subscribers": broadcaster.subscriber_count
    }


@router.get(
    "/status",
    summary="Get streaming status",
    description="Get information about active streaming connections."
)
async def get_streaming_status():
    """Get streaming service status."""
    broadcaster = get_event_broadcaster()
    llm = get_streaming_llm()
    
    return {
        "active_subscribers": broadcaster.subscriber_count,
        "llm_available": llm.model is not None,
        "streaming_enabled": True
    }


@router.get(
    "/demo",
    summary="Demo streaming response",
    description="A demo endpoint showing streaming in action."
)
async def demo_streaming():
    """
    Demo streaming response.
    
    Streams a predefined demo message to show how streaming works.
    """
    demo_text = """
    Welcome to FlowSentinel streaming demo!
    
    This demonstrates real-time AI response streaming.
    Each word is sent as a separate event, allowing the
    frontend to display the response progressively.
    
    Key benefits:
    • Better user experience
    • Faster perceived response time
    • Ability to show thinking process
    • Real-time updates
    
    Thank you for trying FlowSentinel!
    """
    
    words = demo_text.split()
    
    async def generate():
        # Start event
        yield StreamEvent(
            type=StreamEventType.PROGRESS,
            data={"message": "Starting demo..."}
        ).to_sse()
        
        await asyncio.sleep(0.3)
        
        # Stream words
        for i, word in enumerate(words):
            token = word + " "
            yield StreamEvent(
                type=StreamEventType.TOKEN,
                data=token,
                metadata={"index": i, "total": len(words)}
            ).to_sse()
            
            await asyncio.sleep(0.05)
        
        # Complete event
        yield StreamEvent(
            type=StreamEventType.COMPLETE,
            data={"total_tokens": len(words), "message": "Demo complete!"}
        ).to_sse()
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive"
        }
    )

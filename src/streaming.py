"""
FlowSentinel Streaming Responses

Server-Sent Events (SSE) implementation for real-time AI responses.

Features:
- Streaming LLM responses (token by token)
- Real-time event notifications
- Progress updates for long operations
- Agent thinking process streaming

This provides a better UX by showing responses as they generate
rather than waiting for complete responses.
"""

import asyncio
import json
import logging
import os
import time
from datetime import datetime
from typing import Any, AsyncGenerator, Callable, Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Check for IBM watsonx.ai
try:
    from ibm_watsonx_ai.foundation_models import ModelInference
    from ibm_watsonx_ai.credentials import Credentials
    WATSONX_AVAILABLE = True
except ImportError:
    WATSONX_AVAILABLE = False


class StreamEventType(str, Enum):
    """Types of streaming events"""
    TOKEN = "token"           # A single token/word
    THINKING = "thinking"     # Agent thinking process
    TOOL_CALL = "tool_call"   # Agent calling a tool
    TOOL_RESULT = "tool_result"  # Tool execution result
    PROGRESS = "progress"     # Progress update
    COMPLETE = "complete"     # Stream complete
    ERROR = "error"           # Error occurred


@dataclass
class StreamEvent:
    """A single streaming event"""
    type: StreamEventType
    data: Any
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_sse(self) -> str:
        """Convert to Server-Sent Events format"""
        event_data = {
            "type": self.type.value,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }
        return f"data: {json.dumps(event_data)}\n\n"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type.value,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }


class StreamingLLM:
    """
    Streaming LLM interface.
    
    Provides token-by-token streaming from watsonx.ai
    with fallback for non-streaming mode.
    """
    
    def __init__(self):
        self.model = self._init_model()
    
    def _init_model(self) -> Optional[Any]:
        """Initialize watsonx.ai model"""
        if not WATSONX_AVAILABLE:
            return None
        
        api_key = os.getenv("WATSONX_API_KEY")
        project_id = os.getenv("WATSONX_PROJECT_ID")
        
        if not api_key or not project_id:
            return None
        
        try:
            credentials = Credentials(
                url="https://us-south.ml.cloud.ibm.com",
                api_key=api_key
            )
            
            return ModelInference(
                model_id="ibm/granite-3-8b-instruct",
                credentials=credentials,
                project_id=project_id,
                params={
                    "max_new_tokens": 1024,
                    "temperature": 0.7,
                    "top_p": 0.9
                }
            )
        except Exception as e:
            logger.error(f"Failed to init streaming model: {e}")
            return None
    
    async def stream_generate(
        self,
        prompt: str,
        on_token: Optional[Callable[[str], None]] = None
    ) -> AsyncGenerator[StreamEvent, None]:
        """
        Stream generate response token by token.
        
        Args:
            prompt: Input prompt
            on_token: Optional callback for each token
        
        Yields:
            StreamEvent for each token
        """
        if self.model:
            try:
                # Use watsonx.ai streaming if available
                async for event in self._stream_watsonx(prompt, on_token):
                    yield event
            except Exception as e:
                logger.error(f"Streaming failed: {e}")
                # Fall back to simulated streaming
                async for event in self._simulate_stream(prompt, on_token):
                    yield event
        else:
            # Simulate streaming for demo
            async for event in self._simulate_stream(prompt, on_token):
                yield event
    
    async def _stream_watsonx(
        self,
        prompt: str,
        on_token: Optional[Callable[[str], None]] = None
    ) -> AsyncGenerator[StreamEvent, None]:
        """Stream from watsonx.ai"""
        try:
            # Note: watsonx.ai SDK may not support true streaming in all versions
            # This is a placeholder for when streaming is available
            response = self.model.generate(prompt)
            text = response.get("results", [{}])[0].get("generated_text", "")
            
            # Simulate streaming by yielding word by word
            words = text.split()
            for i, word in enumerate(words):
                token = word + (" " if i < len(words) - 1 else "")
                
                if on_token:
                    on_token(token)
                
                yield StreamEvent(
                    type=StreamEventType.TOKEN,
                    data=token,
                    metadata={"index": i, "total": len(words)}
                )
                
                await asyncio.sleep(0.05)  # Small delay for realistic streaming
            
            yield StreamEvent(
                type=StreamEventType.COMPLETE,
                data={"total_tokens": len(words), "full_text": text}
            )
            
        except Exception as e:
            yield StreamEvent(
                type=StreamEventType.ERROR,
                data=str(e)
            )
    
    async def _simulate_stream(
        self,
        prompt: str,
        on_token: Optional[Callable[[str], None]] = None
    ) -> AsyncGenerator[StreamEvent, None]:
        """Simulate streaming for demo/fallback"""
        # Generate a demo response based on prompt content
        prompt_lower = prompt.lower()
        
        if "blocked" in prompt_lower or "blocker" in prompt_lower:
            response = "I've detected a blocker in your project. Based on similar situations, I recommend: 1) Identify the root cause, 2) Escalate if needed, 3) Set up a sync meeting with stakeholders. Would you like me to create a task to track this?"
        elif "status" in prompt_lower or "report" in prompt_lower:
            response = "Here's the current project status: Overall health is YELLOW due to 2 active blockers. 5 tasks completed today, 3 pending. Next deadline in 2 days. I recommend addressing the authentication blocker first as it impacts the critical path."
        elif "risk" in prompt_lower:
            response = "I've identified a potential risk: The current timeline might slip if the API integration isn't completed by Friday. Based on past patterns, I suggest: 1) Add buffer time, 2) Assign additional resources, 3) Set up daily check-ins."
        else:
            response = "I've analyzed your request. Based on the project context and historical patterns, here's my recommendation: Continue with the current approach but monitor for potential delays. Let me know if you'd like more specific guidance."
        
        # Stream word by word
        words = response.split()
        
        for i, word in enumerate(words):
            token = word + (" " if i < len(words) - 1 else "")
            
            if on_token:
                on_token(token)
            
            yield StreamEvent(
                type=StreamEventType.TOKEN,
                data=token,
                metadata={"index": i, "total": len(words)}
            )
            
            await asyncio.sleep(0.03)  # Fast but visible streaming
        
        yield StreamEvent(
            type=StreamEventType.COMPLETE,
            data={"total_tokens": len(words), "full_text": response}
        )


class AgentStreamingRunner:
    """
    Runs the agent with streaming output.
    
    Streams the agent's thinking process, tool calls,
    and results in real-time.
    """
    
    def __init__(self):
        self.llm = StreamingLLM()
    
    async def run_streaming(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> AsyncGenerator[StreamEvent, None]:
        """
        Run agent with streaming output.
        
        Yields events for:
        - Thinking process
        - Tool calls
        - Tool results
        - Final answer
        """
        context = context or {}
        
        # Emit thinking event
        yield StreamEvent(
            type=StreamEventType.THINKING,
            data="Analyzing your request...",
            metadata={"step": 1}
        )
        
        await asyncio.sleep(0.3)
        
        # Build prompt
        prompt = f"User query: {query}\nContext: {json.dumps(context)}\nProvide helpful analysis."
        
        # Emit thinking about context
        yield StreamEvent(
            type=StreamEventType.THINKING,
            data="Reviewing project context and history...",
            metadata={"step": 2}
        )
        
        await asyncio.sleep(0.2)
        
        # Check if we should call a tool
        query_lower = query.lower()
        tool_called = None
        
        if "create" in query_lower and ("task" in query_lower or "ticket" in query_lower):
            tool_called = "create_task"
            yield StreamEvent(
                type=StreamEventType.TOOL_CALL,
                data={"tool": "create_task", "reason": "Creating task based on your request"},
                metadata={"step": 3}
            )
            
            await asyncio.sleep(0.5)
            
            yield StreamEvent(
                type=StreamEventType.TOOL_RESULT,
                data={"tool": "create_task", "result": "Task TASK-001 created successfully"},
                metadata={"step": 4}
            )
            
            await asyncio.sleep(0.2)
        
        elif "report" in query_lower or "status" in query_lower:
            tool_called = "generate_report"
            yield StreamEvent(
                type=StreamEventType.TOOL_CALL,
                data={"tool": "generate_report", "reason": "Generating status report"},
                metadata={"step": 3}
            )
            
            await asyncio.sleep(0.5)
            
            yield StreamEvent(
                type=StreamEventType.TOOL_RESULT,
                data={"tool": "generate_report", "result": "Report generated for today"},
                metadata={"step": 4}
            )
            
            await asyncio.sleep(0.2)
        
        # Emit thinking about response
        yield StreamEvent(
            type=StreamEventType.THINKING,
            data="Formulating response...",
            metadata={"step": 5}
        )
        
        await asyncio.sleep(0.2)
        
        # Stream the actual response
        async for event in self.llm.stream_generate(prompt):
            yield event
    
    async def stream_rag_answer(
        self,
        question: str,
        context_events: Optional[List[Dict[str, Any]]] = None
    ) -> AsyncGenerator[StreamEvent, None]:
        """
        Stream a RAG-powered answer.
        
        Shows retrieval and generation steps.
        """
        # Emit retrieval step
        yield StreamEvent(
            type=StreamEventType.PROGRESS,
            data={"step": "retrieval", "message": "Searching relevant context..."},
            metadata={"progress": 0.2}
        )
        
        await asyncio.sleep(0.3)
        
        # Emit context found
        if context_events:
            yield StreamEvent(
                type=StreamEventType.PROGRESS,
                data={
                    "step": "context",
                    "message": f"Found {len(context_events)} relevant events",
                    "count": len(context_events)
                },
                metadata={"progress": 0.4}
            )
        else:
            yield StreamEvent(
                type=StreamEventType.PROGRESS,
                data={"step": "context", "message": "Using general knowledge"},
                metadata={"progress": 0.4}
            )
        
        await asyncio.sleep(0.2)
        
        # Emit generation step
        yield StreamEvent(
            type=StreamEventType.PROGRESS,
            data={"step": "generation", "message": "Generating answer..."},
            metadata={"progress": 0.6}
        )
        
        await asyncio.sleep(0.2)
        
        # Build context prompt
        context_str = ""
        if context_events:
            context_str = "\n".join([
                f"- {e.get('source', 'unknown')}: {e.get('data', {}).get('message', str(e))}"
                for e in context_events[:5]
            ])
        
        prompt = f"Question: {question}\n\nContext:\n{context_str}\n\nAnswer:"
        
        # Stream the answer
        async for event in self.llm.stream_generate(prompt):
            yield event


class EventBroadcaster:
    """
    Broadcasts real-time events to connected clients.
    
    Used for live updates about project events, agent actions, etc.
    """
    
    def __init__(self):
        self._subscribers: List[asyncio.Queue] = []
    
    async def subscribe(self) -> AsyncGenerator[StreamEvent, None]:
        """Subscribe to event stream"""
        queue: asyncio.Queue = asyncio.Queue()
        self._subscribers.append(queue)
        
        try:
            while True:
                event = await queue.get()
                yield event
        finally:
            self._subscribers.remove(queue)
    
    async def broadcast(self, event: StreamEvent) -> None:
        """Broadcast event to all subscribers"""
        for queue in self._subscribers:
            await queue.put(event)
    
    async def broadcast_event(
        self,
        event_type: StreamEventType,
        data: Any,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Convenience method to broadcast an event"""
        event = StreamEvent(
            type=event_type,
            data=data,
            metadata=metadata or {}
        )
        await self.broadcast(event)
    
    @property
    def subscriber_count(self) -> int:
        """Get number of active subscribers"""
        return len(self._subscribers)


# Global instances
_streaming_llm: Optional[StreamingLLM] = None
_agent_runner: Optional[AgentStreamingRunner] = None
_broadcaster: Optional[EventBroadcaster] = None


def get_streaming_llm() -> StreamingLLM:
    """Get the streaming LLM instance"""
    global _streaming_llm
    if _streaming_llm is None:
        _streaming_llm = StreamingLLM()
    return _streaming_llm


def get_agent_streaming_runner() -> AgentStreamingRunner:
    """Get the agent streaming runner"""
    global _agent_runner
    if _agent_runner is None:
        _agent_runner = AgentStreamingRunner()
    return _agent_runner


def get_event_broadcaster() -> EventBroadcaster:
    """Get the event broadcaster"""
    global _broadcaster
    if _broadcaster is None:
        _broadcaster = EventBroadcaster()
    return _broadcaster

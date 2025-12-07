"""
FlowSentinel AI Agent

Autonomous agent that observes project events, thinks about what actions
to take, and executes tools to help the team.

Architecture:
    Observe → Think → Act → Learn

The agent uses IBM watsonx.ai Granite models for reasoning and
tool selection. It follows a ReAct-style approach.

Key Features:
- Event-driven activation
- Tool-augmented reasoning
- Memory of past interactions
- Configurable autonomy levels
"""

import json
import logging
import os
import time
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

from tools import ToolRegistry, get_tool_registry, ToolResult, ToolResultStatus
from agent_executor import AgentExecutor, get_agent_executor, safe_execute

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
    logger.warning("IBM watsonx.ai not available - agent will use fallback mode")


class AgentMode(str, Enum):
    """Agent operating modes"""
    AUTONOMOUS = "autonomous"   # Agent acts without confirmation
    SUPERVISED = "supervised"   # Agent suggests, human confirms
    ADVISORY = "advisory"       # Agent only provides advice
    DISABLED = "disabled"       # Agent is turned off


class ThoughtType(str, Enum):
    """Types of agent thoughts"""
    OBSERVATION = "observation"
    REASONING = "reasoning"
    PLAN = "plan"
    ACTION = "action"
    REFLECTION = "reflection"


@dataclass
class Thought:
    """Represents a single thought in the agent's reasoning chain"""
    type: ThoughtType
    content: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type.value,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }


@dataclass
class AgentStep:
    """A single step in the agent's execution"""
    step_number: int
    thoughts: List[Thought]
    tool_called: Optional[str] = None
    tool_arguments: Optional[Dict[str, Any]] = None
    tool_result: Optional[ToolResult] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "step": self.step_number,
            "thoughts": [t.to_dict() for t in self.thoughts],
            "tool_called": self.tool_called,
            "tool_arguments": self.tool_arguments,
            "tool_result": self.tool_result.to_dict() if self.tool_result else None
        }


@dataclass
class AgentResponse:
    """Complete response from an agent run"""
    success: bool
    message: str
    steps: List[AgentStep]
    total_tokens: int = 0
    total_time_ms: float = 0.0
    final_answer: Optional[str] = None
    actions_taken: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "message": self.message,
            "steps": [s.to_dict() for s in self.steps],
            "total_tokens": self.total_tokens,
            "total_time_ms": self.total_time_ms,
            "final_answer": self.final_answer,
            "actions_taken": self.actions_taken
        }


class FlowSentinelAgent:
    """
    The main AI agent for FlowSentinel.
    
    Implements a ReAct-style agent loop:
    1. Observe: Gather context from events and project state
    2. Think: Reason about what to do using the LLM
    3. Act: Execute tools to take action
    4. Learn: Update memory with outcomes
    """
    
    # System prompt for the agent
    SYSTEM_PROMPT = """You are FlowSentinel, an AI project intelligence agent. Your job is to help software development teams by:
1. Monitoring project events (Slack messages, Jira tickets, GitHub activity, calendar)
2. Identifying blockers, risks, and opportunities
3. Taking proactive actions to help the team succeed

You have access to the following tools:
{tools}

When analyzing a situation:
1. First, observe and understand the context
2. Then, reason about what actions might help
3. Finally, decide whether to take action or provide advice

Be proactive but careful. Consider the impact of your actions.

Always respond with valid JSON in this format:
{{
    "thought": "Your reasoning about the situation",
    "action": "tool_name" or null if no action needed,
    "action_input": {{}} or null if no action,
    "final_answer": "Your response to the user" or null if continuing
}}"""

    def __init__(
        self,
        mode: AgentMode = AgentMode.SUPERVISED,
        max_steps: int = 5,
        tool_registry: Optional[ToolRegistry] = None,
        executor: Optional[AgentExecutor] = None
    ):
        self.mode = mode
        self.max_steps = max_steps
        self.registry = tool_registry or get_tool_registry()
        self.executor = executor or get_agent_executor()
        
        # Initialize watsonx.ai if available
        self.model = self._init_model()
        
        # Agent memory
        self._conversation_history: List[Dict[str, str]] = []
        self._action_history: List[Dict[str, Any]] = []
    
    def _init_model(self) -> Optional[Any]:
        """Initialize the IBM watsonx.ai model"""
        if not WATSONX_AVAILABLE:
            return None
        
        api_key = os.getenv("WATSONX_API_KEY")
        project_id = os.getenv("WATSONX_PROJECT_ID")
        
        if not api_key or not project_id:
            logger.warning("watsonx.ai credentials not configured")
            return None
        
        try:
            credentials = Credentials(
                url="https://us-south.ml.cloud.ibm.com",
                api_key=api_key
            )
            
            model = ModelInference(
                model_id="ibm/granite-3-8b-instruct",
                credentials=credentials,
                project_id=project_id,
                params={
                    "max_new_tokens": 1024,
                    "temperature": 0.1,
                    "top_p": 0.9,
                    "stop_sequences": ["```", "\n\n\n"]
                }
            )
            
            logger.info("IBM watsonx.ai model initialized successfully")
            return model
        except Exception as e:
            logger.error(f"Failed to initialize watsonx.ai: {e}")
            return None
    
    def _get_tool_descriptions(self) -> str:
        """Get formatted tool descriptions for the prompt"""
        tools = self.registry.list_tools()
        descriptions = []
        
        for tool in tools:
            params_str = json.dumps(tool.parameters, indent=2)
            descriptions.append(f"""
Tool: {tool.name}
Description: {tool.description}
Parameters: {params_str}
""")
        
        return "\n".join(descriptions)
    
    def _build_prompt(self, user_input: str, context: Dict[str, Any]) -> str:
        """Build the full prompt for the agent"""
        system = self.SYSTEM_PROMPT.format(tools=self._get_tool_descriptions())
        
        # Add context
        context_str = ""
        if context.get("events"):
            context_str += f"\nRecent Events:\n{json.dumps(context['events'], indent=2)}"
        if context.get("project_state"):
            context_str += f"\nProject State:\n{json.dumps(context['project_state'], indent=2)}"
        
        # Build conversation
        conversation = f"{system}\n\nContext:{context_str}\n\nUser: {user_input}\n\nAssistant:"
        
        return conversation
    
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse the LLM response into structured format"""
        # Try to extract JSON from the response
        try:
            # Handle markdown code blocks
            if "```json" in response:
                start = response.find("```json") + 7
                end = response.find("```", start)
                response = response[start:end].strip()
            elif "```" in response:
                start = response.find("```") + 3
                end = response.find("```", start)
                response = response[start:end].strip()
            
            return json.loads(response)
        except json.JSONDecodeError:
            # If parsing fails, treat as final answer
            return {
                "thought": "Unable to parse response as JSON",
                "action": None,
                "action_input": None,
                "final_answer": response
            }
    
    def _call_llm(self, prompt: str) -> str:
        """Call the LLM (watsonx.ai or fallback)"""
        if self.model:
            try:
                response = self.model.generate(prompt)
                return response.get("results", [{}])[0].get("generated_text", "")
            except Exception as e:
                logger.error(f"LLM call failed: {e}")
        
        # Fallback: Simple rule-based response
        return self._fallback_reasoning(prompt)
    
    def _fallback_reasoning(self, prompt: str) -> str:
        """Fallback reasoning when LLM is not available"""
        # Extract key patterns from the prompt
        prompt_lower = prompt.lower()
        
        if "blocked" in prompt_lower or "blocker" in prompt_lower:
            return json.dumps({
                "thought": "I detected a blocker mentioned. This could impact project progress.",
                "action": "create_task",
                "action_input": {
                    "title": "Address blocker",
                    "description": "A blocker was detected that needs attention",
                    "priority": "high"
                },
                "final_answer": None
            })
        elif "risk" in prompt_lower or "concern" in prompt_lower:
            return json.dumps({
                "thought": "I detected a potential risk that should be tracked.",
                "action": "send_notification",
                "action_input": {
                    "recipients": ["all"],
                    "message": "A potential risk has been identified",
                    "urgency": "normal"
                },
                "final_answer": None
            })
        elif "report" in prompt_lower or "status" in prompt_lower:
            return json.dumps({
                "thought": "The user is asking about project status.",
                "action": "generate_report",
                "action_input": {
                    "report_type": "daily_standup",
                    "time_range": "today"
                },
                "final_answer": None
            })
        else:
            return json.dumps({
                "thought": "I've analyzed the situation but no immediate action is needed.",
                "action": None,
                "action_input": None,
                "final_answer": "I've reviewed the situation. Everything appears to be on track. Let me know if you'd like me to take any specific action."
            })
    
    async def run(
        self,
        user_input: str,
        context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        """
        Run the agent loop.
        
        Args:
            user_input: The user's request or event to process
            context: Additional context (events, project state, etc.)
        
        Returns:
            AgentResponse with results
        """
        start_time = time.time()
        context = context or {}
        steps: List[AgentStep] = []
        actions_taken: List[Dict[str, Any]] = []
        total_tokens = 0
        
        if self.mode == AgentMode.DISABLED:
            return AgentResponse(
                success=False,
                message="Agent is disabled",
                steps=[],
                total_time_ms=(time.time() - start_time) * 1000
            )
        
        logger.info(f"Agent running in {self.mode.value} mode")
        
        for step_num in range(1, self.max_steps + 1):
            thoughts: List[Thought] = []
            
            # Observe
            thoughts.append(Thought(
                type=ThoughtType.OBSERVATION,
                content=f"Processing input: {user_input[:200]}..."
            ))
            
            # Build and send prompt
            prompt = self._build_prompt(user_input, context)
            
            # Think (call LLM)
            llm_response = self._call_llm(prompt)
            parsed = self._parse_response(llm_response)
            
            thoughts.append(Thought(
                type=ThoughtType.REASONING,
                content=parsed.get("thought", "Analyzing situation...")
            ))
            
            step = AgentStep(
                step_number=step_num,
                thoughts=thoughts
            )
            
            # Check for final answer
            if parsed.get("final_answer"):
                step.thoughts.append(Thought(
                    type=ThoughtType.REFLECTION,
                    content=parsed["final_answer"]
                ))
                steps.append(step)
                
                return AgentResponse(
                    success=True,
                    message="Agent completed successfully",
                    steps=steps,
                    total_tokens=total_tokens,
                    total_time_ms=(time.time() - start_time) * 1000,
                    final_answer=parsed["final_answer"],
                    actions_taken=actions_taken
                )
            
            # Act (if action specified)
            if parsed.get("action"):
                action_name = parsed["action"]
                action_input = parsed.get("action_input", {})
                
                step.tool_called = action_name
                step.tool_arguments = action_input
                
                thoughts.append(Thought(
                    type=ThoughtType.ACTION,
                    content=f"Executing tool: {action_name}"
                ))
                
                # Execute based on mode
                if self.mode == AgentMode.AUTONOMOUS:
                    result = safe_execute(action_name, action_input)
                    step.tool_result = result
                    
                    actions_taken.append({
                        "tool": action_name,
                        "input": action_input,
                        "result": result.to_dict()
                    })
                    
                    # Add result to context for next iteration
                    context["last_action_result"] = result.to_dict()
                    
                elif self.mode == AgentMode.SUPERVISED:
                    # Return pending action for confirmation
                    step.tool_result = ToolResult(
                        status=ToolResultStatus.PENDING,
                        data={"action": action_name, "input": action_input},
                        message="Action requires user confirmation"
                    )
                    steps.append(step)
                    
                    return AgentResponse(
                        success=True,
                        message="Action pending confirmation",
                        steps=steps,
                        total_tokens=total_tokens,
                        total_time_ms=(time.time() - start_time) * 1000,
                        final_answer=f"I recommend taking action: {action_name}. Do you want me to proceed?",
                        actions_taken=[{"tool": action_name, "input": action_input, "status": "pending"}]
                    )
                
                else:  # ADVISORY mode
                    step.tool_result = ToolResult(
                        status=ToolResultStatus.SUCCESS,
                        data={"suggested_action": action_name, "suggested_input": action_input},
                        message="Action suggested (advisory mode)"
                    )
            
            steps.append(step)
            
            # Update user_input for next iteration with result
            if step.tool_result and step.tool_result.status == ToolResultStatus.SUCCESS:
                user_input = f"Previous action result: {step.tool_result.message}. What should I do next?"
        
        # Max steps reached
        return AgentResponse(
            success=True,
            message="Max steps reached",
            steps=steps,
            total_tokens=total_tokens,
            total_time_ms=(time.time() - start_time) * 1000,
            final_answer="I've analyzed the situation but couldn't reach a conclusion within the step limit.",
            actions_taken=actions_taken
        )
    
    def run_sync(
        self,
        user_input: str,
        context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        """Synchronous version of run()"""
        import asyncio
        
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(self.run(user_input, context))
    
    def process_event(self, event: Dict[str, Any]) -> AgentResponse:
        """
        Process a single event and determine actions.
        
        Args:
            event: Event data from Slack, Jira, GitHub, etc.
        
        Returns:
            AgentResponse with any actions taken
        """
        # Build context from event
        context = {
            "events": [event],
            "event_type": event.get("type"),
            "event_source": event.get("source")
        }
        
        # Create prompt from event
        event_summary = self._summarize_event(event)
        
        return self.run_sync(
            user_input=f"Process this event and determine if any action is needed: {event_summary}",
            context=context
        )
    
    def _summarize_event(self, event: Dict[str, Any]) -> str:
        """Create a text summary of an event"""
        source = event.get("source", "unknown")
        event_type = event.get("type", "unknown")
        data = event.get("data", {})
        
        if source == "slack":
            return f"Slack message in {data.get('channel', 'unknown')}: {data.get('message', '')}"
        elif source == "jira":
            return f"Jira {event_type}: {data.get('key', '')} - {data.get('summary', '')}"
        elif source == "github":
            return f"GitHub {event_type}: {data.get('title', data.get('message', ''))}"
        elif source == "calendar":
            return f"Calendar {event_type}: {data.get('title', '')}"
        else:
            return json.dumps(event)
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            "mode": self.mode.value,
            "max_steps": self.max_steps,
            "model_available": self.model is not None,
            "tools_available": len(self.registry.list_tools()),
            "actions_taken": len(self._action_history)
        }


# Global agent instance
_agent: Optional[FlowSentinelAgent] = None


def get_agent(mode: AgentMode = AgentMode.SUPERVISED) -> FlowSentinelAgent:
    """Get or create the global agent instance"""
    global _agent
    if _agent is None:
        _agent = FlowSentinelAgent(mode=mode)
    return _agent


def process_event_with_agent(event: Dict[str, Any]) -> Dict[str, Any]:
    """Convenience function to process an event with the agent"""
    agent = get_agent()
    response = agent.process_event(event)
    return response.to_dict()

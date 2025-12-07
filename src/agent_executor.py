"""
FlowSentinel Agent Executor

Safe execution environment for running agent tools.
Handles:
- Execution isolation
- Rate limiting
- Logging and auditing
- Error recovery
- Confirmation workflows

This is a critical security layer between the AI agent and actual actions.
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict

from tools import (
    ToolRegistry,
    ToolDefinition,
    ToolResult,
    ToolResultStatus,
    get_tool_registry,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ExecutionPolicy(str, Enum):
    """Policies for tool execution"""
    ALLOW = "allow"           # Execute immediately
    CONFIRM = "confirm"       # Require user confirmation
    DENY = "deny"             # Block execution
    RATE_LIMIT = "rate_limit" # Temporarily blocked due to rate limit


@dataclass
class ExecutionRequest:
    """Request to execute a tool"""
    id: str
    tool_name: str
    arguments: Dict[str, Any]
    requested_at: datetime = field(default_factory=datetime.utcnow)
    requested_by: str = "agent"
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionRecord:
    """Record of a tool execution"""
    request: ExecutionRequest
    result: ToolResult
    policy_applied: ExecutionPolicy
    executed_at: datetime
    execution_duration_ms: float
    confirmation_required: bool = False
    confirmed_by: Optional[str] = None
    confirmed_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "request_id": self.request.id,
            "tool_name": self.request.tool_name,
            "arguments": self.request.arguments,
            "result": self.result.to_dict(),
            "policy": self.policy_applied.value,
            "executed_at": self.executed_at.isoformat(),
            "duration_ms": self.execution_duration_ms,
            "confirmation_required": self.confirmation_required,
            "confirmed_by": self.confirmed_by
        }


class RateLimiter:
    """
    Rate limiter for tool execution.
    
    Prevents runaway agents from executing too many actions.
    """
    
    def __init__(
        self,
        max_calls_per_minute: int = 30,
        max_calls_per_hour: int = 200,
        max_calls_per_tool_per_minute: int = 10
    ):
        self.max_calls_per_minute = max_calls_per_minute
        self.max_calls_per_hour = max_calls_per_hour
        self.max_calls_per_tool_per_minute = max_calls_per_tool_per_minute
        
        self._calls: List[datetime] = []
        self._calls_by_tool: Dict[str, List[datetime]] = defaultdict(list)
    
    def _cleanup_old_calls(self, tool_name: Optional[str] = None) -> None:
        """Remove calls older than 1 hour"""
        cutoff = datetime.utcnow() - timedelta(hours=1)
        self._calls = [c for c in self._calls if c > cutoff]
        
        if tool_name:
            self._calls_by_tool[tool_name] = [
                c for c in self._calls_by_tool[tool_name] if c > cutoff
            ]
    
    def check_limit(self, tool_name: str) -> Tuple[bool, str]:
        """
        Check if execution is allowed under rate limits.
        
        Returns:
            Tuple of (allowed: bool, reason: str)
        """
        now = datetime.utcnow()
        self._cleanup_old_calls(tool_name)
        
        # Check per-minute global limit
        minute_ago = now - timedelta(minutes=1)
        calls_last_minute = len([c for c in self._calls if c > minute_ago])
        if calls_last_minute >= self.max_calls_per_minute:
            return False, f"Global rate limit: {calls_last_minute}/{self.max_calls_per_minute} calls/minute"
        
        # Check per-hour global limit
        hour_ago = now - timedelta(hours=1)
        calls_last_hour = len([c for c in self._calls if c > hour_ago])
        if calls_last_hour >= self.max_calls_per_hour:
            return False, f"Global rate limit: {calls_last_hour}/{self.max_calls_per_hour} calls/hour"
        
        # Check per-tool limit
        tool_calls = [c for c in self._calls_by_tool[tool_name] if c > minute_ago]
        if len(tool_calls) >= self.max_calls_per_tool_per_minute:
            return False, f"Tool rate limit: {len(tool_calls)}/{self.max_calls_per_tool_per_minute} calls/minute for {tool_name}"
        
        return True, "OK"
    
    def record_call(self, tool_name: str) -> None:
        """Record a tool call"""
        now = datetime.utcnow()
        self._calls.append(now)
        self._calls_by_tool[tool_name].append(now)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get rate limit statistics"""
        now = datetime.utcnow()
        minute_ago = now - timedelta(minutes=1)
        hour_ago = now - timedelta(hours=1)
        
        return {
            "calls_last_minute": len([c for c in self._calls if c > minute_ago]),
            "calls_last_hour": len([c for c in self._calls if c > hour_ago]),
            "limits": {
                "per_minute": self.max_calls_per_minute,
                "per_hour": self.max_calls_per_hour,
                "per_tool_per_minute": self.max_calls_per_tool_per_minute
            }
        }


class ConfirmationManager:
    """
    Manages confirmation workflows for sensitive actions.
    
    Stores pending confirmations and handles approval/rejection.
    """
    
    def __init__(self, confirmation_timeout_minutes: int = 30):
        self.timeout_minutes = confirmation_timeout_minutes
        self._pending: Dict[str, ExecutionRequest] = {}
        self._rejected: Dict[str, str] = {}  # request_id -> reason
    
    def request_confirmation(self, request: ExecutionRequest) -> str:
        """Store a request pending confirmation"""
        self._pending[request.id] = request
        return request.id
    
    def confirm(self, request_id: str, confirmed_by: str) -> Optional[ExecutionRequest]:
        """Confirm a pending request"""
        request = self._pending.pop(request_id, None)
        if request:
            # Check timeout
            if datetime.utcnow() - request.requested_at > timedelta(minutes=self.timeout_minutes):
                self._rejected[request_id] = "Confirmation timeout"
                return None
        return request
    
    def reject(self, request_id: str, reason: str) -> bool:
        """Reject a pending request"""
        request = self._pending.pop(request_id, None)
        if request:
            self._rejected[request_id] = reason
            return True
        return False
    
    def get_pending(self) -> List[Dict[str, Any]]:
        """Get all pending confirmations"""
        now = datetime.utcnow()
        pending = []
        
        for request_id, request in list(self._pending.items()):
            age = now - request.requested_at
            if age > timedelta(minutes=self.timeout_minutes):
                # Expired
                self._pending.pop(request_id)
                self._rejected[request_id] = "Timeout"
            else:
                pending.append({
                    "id": request_id,
                    "tool": request.tool_name,
                    "arguments": request.arguments,
                    "requested_at": request.requested_at.isoformat(),
                    "expires_in_minutes": self.timeout_minutes - (age.total_seconds() / 60)
                })
        
        return pending


class AgentExecutor:
    """
    Safe execution environment for agent tools.
    
    Features:
    - Policy-based execution control
    - Rate limiting
    - Confirmation workflows
    - Execution logging/auditing
    - Error handling and recovery
    """
    
    def __init__(
        self,
        tool_registry: Optional[ToolRegistry] = None,
        rate_limiter: Optional[RateLimiter] = None,
        confirmation_manager: Optional[ConfirmationManager] = None,
        audit_log_enabled: bool = True
    ):
        self.registry = tool_registry or get_tool_registry()
        self.rate_limiter = rate_limiter or RateLimiter()
        self.confirmation_manager = confirmation_manager or ConfirmationManager()
        self.audit_log_enabled = audit_log_enabled
        
        self._execution_history: List[ExecutionRecord] = []
        self._blocked_tools: set = set()
        self._tool_policies: Dict[str, ExecutionPolicy] = {}
    
    def block_tool(self, tool_name: str) -> None:
        """Block a tool from execution"""
        self._blocked_tools.add(tool_name)
        logger.warning(f"Tool blocked: {tool_name}")
    
    def unblock_tool(self, tool_name: str) -> None:
        """Unblock a tool"""
        self._blocked_tools.discard(tool_name)
        logger.info(f"Tool unblocked: {tool_name}")
    
    def set_tool_policy(self, tool_name: str, policy: ExecutionPolicy) -> None:
        """Set execution policy for a specific tool"""
        self._tool_policies[tool_name] = policy
        logger.info(f"Policy set for {tool_name}: {policy.value}")
    
    def _get_policy(self, tool: ToolDefinition) -> ExecutionPolicy:
        """Determine execution policy for a tool"""
        # Check if blocked
        if tool.name in self._blocked_tools:
            return ExecutionPolicy.DENY
        
        # Check custom policy
        if tool.name in self._tool_policies:
            return self._tool_policies[tool.name]
        
        # Check rate limits
        allowed, reason = self.rate_limiter.check_limit(tool.name)
        if not allowed:
            logger.warning(f"Rate limit hit: {reason}")
            return ExecutionPolicy.RATE_LIMIT
        
        # Check if tool requires confirmation
        if tool.requires_confirmation:
            return ExecutionPolicy.CONFIRM
        
        return ExecutionPolicy.ALLOW
    
    def execute(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        request_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Tuple[ToolResult, ExecutionRecord]:
        """
        Execute a tool with full safety checks.
        
        Args:
            tool_name: Name of the tool to execute
            arguments: Arguments to pass to the tool
            request_id: Optional unique request ID
            context: Optional execution context
        
        Returns:
            Tuple of (ToolResult, ExecutionRecord)
        """
        import uuid
        start_time = time.time()
        
        # Create execution request
        request = ExecutionRequest(
            id=request_id or str(uuid.uuid4()),
            tool_name=tool_name,
            arguments=arguments,
            context=context or {}
        )
        
        # Get tool definition
        tool = self.registry.get(tool_name)
        if not tool:
            result = ToolResult(
                status=ToolResultStatus.ERROR,
                data=None,
                message=f"Tool not found: {tool_name}"
            )
            record = ExecutionRecord(
                request=request,
                result=result,
                policy_applied=ExecutionPolicy.DENY,
                executed_at=datetime.utcnow(),
                execution_duration_ms=(time.time() - start_time) * 1000
            )
            return result, record
        
        # Check policy
        policy = self._get_policy(tool)
        
        if policy == ExecutionPolicy.DENY:
            result = ToolResult(
                status=ToolResultStatus.ERROR,
                data=None,
                message=f"Tool execution denied: {tool_name} is blocked"
            )
        elif policy == ExecutionPolicy.RATE_LIMIT:
            result = ToolResult(
                status=ToolResultStatus.ERROR,
                data=None,
                message=f"Rate limit exceeded for {tool_name}"
            )
        elif policy == ExecutionPolicy.CONFIRM:
            # Request confirmation
            self.confirmation_manager.request_confirmation(request)
            result = ToolResult(
                status=ToolResultStatus.PENDING,
                data={"confirmation_id": request.id},
                message=f"Confirmation required for {tool_name}"
            )
        else:
            # Execute the tool
            try:
                logger.info(f"Executing tool: {tool_name} with args: {arguments}")
                result = tool.function(**arguments)
                self.rate_limiter.record_call(tool_name)
                logger.info(f"Tool executed: {tool_name} -> {result.status.value}")
            except Exception as e:
                logger.error(f"Tool execution failed: {tool_name} -> {str(e)}")
                result = ToolResult(
                    status=ToolResultStatus.ERROR,
                    data=None,
                    message=f"Execution error: {str(e)}"
                )
        
        # Create execution record
        record = ExecutionRecord(
            request=request,
            result=result,
            policy_applied=policy,
            executed_at=datetime.utcnow(),
            execution_duration_ms=(time.time() - start_time) * 1000,
            confirmation_required=(policy == ExecutionPolicy.CONFIRM)
        )
        
        # Store in history
        if self.audit_log_enabled:
            self._execution_history.append(record)
        
        return result, record
    
    def execute_confirmed(
        self,
        confirmation_id: str,
        confirmed_by: str
    ) -> Optional[Tuple[ToolResult, ExecutionRecord]]:
        """
        Execute a previously confirmed request.
        
        Args:
            confirmation_id: ID of the pending confirmation
            confirmed_by: Who confirmed the action
        
        Returns:
            Tuple of (ToolResult, ExecutionRecord) or None if not found
        """
        request = self.confirmation_manager.confirm(confirmation_id, confirmed_by)
        if not request:
            return None
        
        # Execute with confirmation bypass
        tool = self.registry.get(request.tool_name)
        if not tool:
            return None
        
        start_time = time.time()
        
        try:
            result = tool.function(**request.arguments)
            self.rate_limiter.record_call(request.tool_name)
        except Exception as e:
            result = ToolResult(
                status=ToolResultStatus.ERROR,
                data=None,
                message=f"Execution error: {str(e)}"
            )
        
        record = ExecutionRecord(
            request=request,
            result=result,
            policy_applied=ExecutionPolicy.ALLOW,
            executed_at=datetime.utcnow(),
            execution_duration_ms=(time.time() - start_time) * 1000,
            confirmation_required=True,
            confirmed_by=confirmed_by,
            confirmed_at=datetime.utcnow()
        )
        
        if self.audit_log_enabled:
            self._execution_history.append(record)
        
        return result, record
    
    def get_execution_history(
        self,
        limit: int = 100,
        tool_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get execution history"""
        history = self._execution_history[-limit:]
        
        if tool_name:
            history = [r for r in history if r.request.tool_name == tool_name]
        
        return [r.to_dict() for r in history]
    
    def get_pending_confirmations(self) -> List[Dict[str, Any]]:
        """Get all pending confirmations"""
        return self.confirmation_manager.get_pending()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get executor statistics"""
        return {
            "total_executions": len(self._execution_history),
            "blocked_tools": list(self._blocked_tools),
            "custom_policies": {k: v.value for k, v in self._tool_policies.items()},
            "rate_limits": self.rate_limiter.get_stats(),
            "pending_confirmations": len(self.confirmation_manager.get_pending())
        }


# Global executor instance
_executor: Optional[AgentExecutor] = None


def get_agent_executor() -> AgentExecutor:
    """Get or create the global agent executor"""
    global _executor
    if _executor is None:
        _executor = AgentExecutor()
    return _executor


def safe_execute(
    tool_name: str,
    arguments: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None
) -> ToolResult:
    """
    Convenience function for safe tool execution.
    
    Args:
        tool_name: Name of the tool to execute
        arguments: Tool arguments
        context: Optional context
    
    Returns:
        ToolResult
    """
    executor = get_agent_executor()
    result, _ = executor.execute(tool_name, arguments, context=context)
    return result

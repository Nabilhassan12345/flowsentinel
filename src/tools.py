"""
FlowSentinel Tool Definitions

Defines the tools available to the AI agent for autonomous actions.
Each tool has a schema (for the LLM) and an implementation.

Tools:
- create_task: Create a task in the system
- send_notification: Send a notification to users
- generate_report: Generate a project status report
- update_project_status: Update project health status
- get_events: Retrieve recent events
- search_events: Search events semantically

This follows the OpenAI function calling pattern for maximum compatibility.
"""

import json
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum


class ToolResultStatus(str, Enum):
    """Status of tool execution"""
    SUCCESS = "success"
    ERROR = "error"
    PENDING = "pending"


@dataclass
class ToolResult:
    """Result of executing a tool"""
    status: ToolResultStatus
    data: Any
    message: str
    execution_time_ms: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status.value,
            "data": self.data,
            "message": self.message,
            "execution_time_ms": self.execution_time_ms
        }


@dataclass
class ToolDefinition:
    """
    Definition of a tool that the agent can use.
    
    Attributes:
        name: Unique identifier for the tool
        description: What the tool does (for LLM context)
        parameters: JSON Schema for the tool's parameters
        function: The actual function to execute
        requires_confirmation: Whether to ask user before executing
        is_destructive: Whether the action can cause data loss
    """
    name: str
    description: str
    parameters: Dict[str, Any]
    function: Callable
    requires_confirmation: bool = False
    is_destructive: bool = False
    category: str = "general"
    
    def to_openai_schema(self) -> Dict[str, Any]:
        """Convert to OpenAI function calling format"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters
            }
        }
    
    def to_watsonx_schema(self) -> Dict[str, Any]:
        """Convert to IBM watsonx.ai tool format"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters
            }
        }


class ToolRegistry:
    """
    Registry of all available tools.
    
    Manages tool registration, lookup, and schema generation.
    """
    
    def __init__(self):
        self._tools: Dict[str, ToolDefinition] = {}
        self._initialize_default_tools()
    
    def register(self, tool: ToolDefinition) -> None:
        """Register a new tool"""
        self._tools[tool.name] = tool
    
    def get(self, name: str) -> Optional[ToolDefinition]:
        """Get a tool by name"""
        return self._tools.get(name)
    
    def list_tools(self, category: Optional[str] = None) -> List[ToolDefinition]:
        """List all tools, optionally filtered by category"""
        tools = list(self._tools.values())
        if category:
            tools = [t for t in tools if t.category == category]
        return tools
    
    def get_all_schemas(self, format: str = "openai") -> List[Dict[str, Any]]:
        """Get schemas for all tools in specified format"""
        if format == "openai":
            return [t.to_openai_schema() for t in self._tools.values()]
        elif format == "watsonx":
            return [t.to_watsonx_schema() for t in self._tools.values()]
        else:
            raise ValueError(f"Unknown format: {format}")
    
    def _initialize_default_tools(self) -> None:
        """Register the default FlowSentinel tools"""
        
        # Tool: Create Task
        self.register(ToolDefinition(
            name="create_task",
            description="Create a new task or action item. Use this when you identify work that needs to be done, such as fixing bugs, addressing blockers, or following up on issues.",
            parameters={
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Short title for the task"
                    },
                    "description": {
                        "type": "string",
                        "description": "Detailed description of what needs to be done"
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high", "critical"],
                        "description": "Priority level of the task"
                    },
                    "assignee": {
                        "type": "string",
                        "description": "Email or username of person to assign to"
                    },
                    "due_date": {
                        "type": "string",
                        "description": "Due date in ISO format (YYYY-MM-DD)"
                    }
                },
                "required": ["title", "description", "priority"]
            },
            function=self._create_task,
            category="task_management"
        ))
        
        # Tool: Send Notification
        self.register(ToolDefinition(
            name="send_notification",
            description="Send a notification to team members. Use this to alert users about important updates, risks, or actions needed.",
            parameters={
                "type": "object",
                "properties": {
                    "recipients": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of usernames or 'all' for everyone"
                    },
                    "message": {
                        "type": "string",
                        "description": "The notification message"
                    },
                    "urgency": {
                        "type": "string",
                        "enum": ["low", "normal", "high", "urgent"],
                        "description": "Urgency level affects how notification is delivered"
                    },
                    "channel": {
                        "type": "string",
                        "enum": ["email", "slack", "in_app", "all"],
                        "description": "Which channel to send the notification through"
                    }
                },
                "required": ["recipients", "message"]
            },
            function=self._send_notification,
            category="communication"
        ))
        
        # Tool: Generate Report
        self.register(ToolDefinition(
            name="generate_report",
            description="Generate a project status report. Use this to create summaries of project health, recent activity, or specific metrics.",
            parameters={
                "type": "object",
                "properties": {
                    "report_type": {
                        "type": "string",
                        "enum": ["daily_standup", "weekly_summary", "risk_assessment", "blocker_report", "custom"],
                        "description": "Type of report to generate"
                    },
                    "time_range": {
                        "type": "string",
                        "enum": ["today", "yesterday", "this_week", "last_week", "this_month"],
                        "description": "Time range to cover in the report"
                    },
                    "include_sections": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Sections to include: blockers, risks, completed, upcoming, metrics"
                    }
                },
                "required": ["report_type"]
            },
            function=self._generate_report,
            category="reporting"
        ))
        
        # Tool: Update Project Status
        self.register(ToolDefinition(
            name="update_project_status",
            description="Update the overall project health status. Use this when you've analyzed events and determined the project status should change.",
            parameters={
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "enum": ["GREEN", "YELLOW", "RED"],
                        "description": "New project status"
                    },
                    "reason": {
                        "type": "string",
                        "description": "Explanation for the status change"
                    },
                    "blockers": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "title": {"type": "string"},
                                "severity": {"type": "string"}
                            }
                        },
                        "description": "Current blockers affecting the project"
                    },
                    "risks": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "title": {"type": "string"},
                                "likelihood": {"type": "string"}
                            }
                        },
                        "description": "Identified risks"
                    }
                },
                "required": ["status", "reason"]
            },
            function=self._update_project_status,
            requires_confirmation=True,
            category="project_management"
        ))
        
        # Tool: Get Events
        self.register(ToolDefinition(
            name="get_events",
            description="Retrieve recent events from the system. Use this to gather context about what's happening in the project.",
            parameters={
                "type": "object",
                "properties": {
                    "source": {
                        "type": "string",
                        "enum": ["all", "slack", "jira", "github", "calendar"],
                        "description": "Filter by event source"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of events to retrieve",
                        "default": 10
                    },
                    "hours_ago": {
                        "type": "integer",
                        "description": "Only get events from the last N hours",
                        "default": 24
                    }
                }
            },
            function=self._get_events,
            category="data_retrieval"
        ))
        
        # Tool: Search Events (uses RAG)
        self.register(ToolDefinition(
            name="search_events",
            description="Search for events semantically. Use this when you need to find specific information or context from past events.",
            parameters={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Natural language search query"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results",
                        "default": 5
                    }
                },
                "required": ["query"]
            },
            function=self._search_events,
            category="data_retrieval"
        ))
        
        # Tool: Analyze Sentiment
        self.register(ToolDefinition(
            name="analyze_sentiment",
            description="Analyze the sentiment of messages or discussions. Use this to gauge team morale or identify concerning communication patterns.",
            parameters={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Text to analyze"
                    },
                    "context": {
                        "type": "string",
                        "description": "Additional context about the text"
                    }
                },
                "required": ["text"]
            },
            function=self._analyze_sentiment,
            category="analysis"
        ))
        
        # Tool: Schedule Meeting
        self.register(ToolDefinition(
            name="schedule_meeting",
            description="Schedule a meeting to address issues. Use this when a synchronous discussion is needed to resolve blockers or align the team.",
            parameters={
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Meeting title"
                    },
                    "attendees": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of attendees"
                    },
                    "duration_minutes": {
                        "type": "integer",
                        "description": "Meeting duration in minutes"
                    },
                    "urgency": {
                        "type": "string",
                        "enum": ["normal", "urgent", "asap"],
                        "description": "How urgently the meeting is needed"
                    },
                    "agenda": {
                        "type": "string",
                        "description": "Meeting agenda"
                    }
                },
                "required": ["title", "attendees", "agenda"]
            },
            function=self._schedule_meeting,
            requires_confirmation=True,
            category="communication"
        ))
    
    # ============================================================================
    # TOOL IMPLEMENTATIONS
    # ============================================================================
    
    def _create_task(self, **kwargs) -> ToolResult:
        """Create a task in the system"""
        import time
        start = time.time()
        
        try:
            # In production, this would integrate with Jira, GitHub Issues, etc.
            task = {
                "id": f"TASK-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "title": kwargs.get("title"),
                "description": kwargs.get("description"),
                "priority": kwargs.get("priority", "medium"),
                "assignee": kwargs.get("assignee"),
                "due_date": kwargs.get("due_date"),
                "status": "created",
                "created_at": datetime.now().isoformat()
            }
            
            return ToolResult(
                status=ToolResultStatus.SUCCESS,
                data=task,
                message=f"Created task: {task['id']} - {task['title']}",
                execution_time_ms=(time.time() - start) * 1000
            )
        except Exception as e:
            return ToolResult(
                status=ToolResultStatus.ERROR,
                data=None,
                message=f"Failed to create task: {str(e)}",
                execution_time_ms=(time.time() - start) * 1000
            )
    
    def _send_notification(self, **kwargs) -> ToolResult:
        """Send a notification"""
        import time
        start = time.time()
        
        try:
            notification = {
                "id": f"NOTIF-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "recipients": kwargs.get("recipients", []),
                "message": kwargs.get("message"),
                "urgency": kwargs.get("urgency", "normal"),
                "channel": kwargs.get("channel", "in_app"),
                "sent_at": datetime.now().isoformat()
            }
            
            # In production, this would actually send notifications
            return ToolResult(
                status=ToolResultStatus.SUCCESS,
                data=notification,
                message=f"Notification sent to {len(notification['recipients'])} recipients",
                execution_time_ms=(time.time() - start) * 1000
            )
        except Exception as e:
            return ToolResult(
                status=ToolResultStatus.ERROR,
                data=None,
                message=f"Failed to send notification: {str(e)}",
                execution_time_ms=(time.time() - start) * 1000
            )
    
    def _generate_report(self, **kwargs) -> ToolResult:
        """Generate a project report"""
        import time
        start = time.time()
        
        try:
            report_type = kwargs.get("report_type", "daily_standup")
            time_range = kwargs.get("time_range", "today")
            
            # In production, this would aggregate real data
            report = {
                "id": f"REPORT-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "type": report_type,
                "time_range": time_range,
                "generated_at": datetime.now().isoformat(),
                "summary": f"Project status report ({report_type}) for {time_range}",
                "sections": {
                    "blockers": [],
                    "risks": [],
                    "completed": [],
                    "upcoming": []
                }
            }
            
            return ToolResult(
                status=ToolResultStatus.SUCCESS,
                data=report,
                message=f"Generated {report_type} report for {time_range}",
                execution_time_ms=(time.time() - start) * 1000
            )
        except Exception as e:
            return ToolResult(
                status=ToolResultStatus.ERROR,
                data=None,
                message=f"Failed to generate report: {str(e)}",
                execution_time_ms=(time.time() - start) * 1000
            )
    
    def _update_project_status(self, **kwargs) -> ToolResult:
        """Update project status"""
        import time
        start = time.time()
        
        try:
            status_update = {
                "status": kwargs.get("status"),
                "reason": kwargs.get("reason"),
                "blockers": kwargs.get("blockers", []),
                "risks": kwargs.get("risks", []),
                "updated_at": datetime.now().isoformat()
            }
            
            return ToolResult(
                status=ToolResultStatus.SUCCESS,
                data=status_update,
                message=f"Project status updated to {status_update['status']}",
                execution_time_ms=(time.time() - start) * 1000
            )
        except Exception as e:
            return ToolResult(
                status=ToolResultStatus.ERROR,
                data=None,
                message=f"Failed to update status: {str(e)}",
                execution_time_ms=(time.time() - start) * 1000
            )
    
    def _get_events(self, **kwargs) -> ToolResult:
        """Retrieve events from the database"""
        import time
        start = time.time()
        
        try:
            # This would query the actual database
            events = []  # Placeholder
            
            return ToolResult(
                status=ToolResultStatus.SUCCESS,
                data=events,
                message=f"Retrieved {len(events)} events",
                execution_time_ms=(time.time() - start) * 1000
            )
        except Exception as e:
            return ToolResult(
                status=ToolResultStatus.ERROR,
                data=None,
                message=f"Failed to get events: {str(e)}",
                execution_time_ms=(time.time() - start) * 1000
            )
    
    def _search_events(self, **kwargs) -> ToolResult:
        """Search events using RAG"""
        import time
        start = time.time()
        
        try:
            query = kwargs.get("query", "")
            # This would use the RAG pipeline
            results = []  # Placeholder
            
            return ToolResult(
                status=ToolResultStatus.SUCCESS,
                data=results,
                message=f"Found {len(results)} matching events for query: {query}",
                execution_time_ms=(time.time() - start) * 1000
            )
        except Exception as e:
            return ToolResult(
                status=ToolResultStatus.ERROR,
                data=None,
                message=f"Search failed: {str(e)}",
                execution_time_ms=(time.time() - start) * 1000
            )
    
    def _analyze_sentiment(self, **kwargs) -> ToolResult:
        """Analyze text sentiment"""
        import time
        start = time.time()
        
        try:
            text = kwargs.get("text", "")
            
            # Simple sentiment analysis (in production, use watsonx.ai)
            negative_words = ["blocked", "issue", "problem", "failed", "error", "frustrated", "delay"]
            positive_words = ["completed", "done", "success", "great", "awesome", "merged", "shipped"]
            
            text_lower = text.lower()
            neg_count = sum(1 for w in negative_words if w in text_lower)
            pos_count = sum(1 for w in positive_words if w in text_lower)
            
            if pos_count > neg_count:
                sentiment = "positive"
                score = 0.5 + (pos_count * 0.1)
            elif neg_count > pos_count:
                sentiment = "negative"
                score = 0.5 - (neg_count * 0.1)
            else:
                sentiment = "neutral"
                score = 0.5
            
            result = {
                "sentiment": sentiment,
                "score": min(1.0, max(0.0, score)),
                "positive_indicators": pos_count,
                "negative_indicators": neg_count
            }
            
            return ToolResult(
                status=ToolResultStatus.SUCCESS,
                data=result,
                message=f"Sentiment: {sentiment} (score: {score:.2f})",
                execution_time_ms=(time.time() - start) * 1000
            )
        except Exception as e:
            return ToolResult(
                status=ToolResultStatus.ERROR,
                data=None,
                message=f"Sentiment analysis failed: {str(e)}",
                execution_time_ms=(time.time() - start) * 1000
            )
    
    def _schedule_meeting(self, **kwargs) -> ToolResult:
        """Schedule a meeting"""
        import time
        start = time.time()
        
        try:
            meeting = {
                "id": f"MTG-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "title": kwargs.get("title"),
                "attendees": kwargs.get("attendees", []),
                "duration_minutes": kwargs.get("duration_minutes", 30),
                "urgency": kwargs.get("urgency", "normal"),
                "agenda": kwargs.get("agenda"),
                "status": "scheduled",
                "scheduled_at": datetime.now().isoformat()
            }
            
            return ToolResult(
                status=ToolResultStatus.SUCCESS,
                data=meeting,
                message=f"Meeting scheduled: {meeting['title']} with {len(meeting['attendees'])} attendees",
                execution_time_ms=(time.time() - start) * 1000
            )
        except Exception as e:
            return ToolResult(
                status=ToolResultStatus.ERROR,
                data=None,
                message=f"Failed to schedule meeting: {str(e)}",
                execution_time_ms=(time.time() - start) * 1000
            )


# Global tool registry instance
tool_registry = ToolRegistry()


def get_tool_registry() -> ToolRegistry:
    """Get the global tool registry"""
    return tool_registry


def execute_tool(tool_name: str, arguments: Dict[str, Any]) -> ToolResult:
    """
    Execute a tool by name with given arguments.
    
    Args:
        tool_name: Name of the tool to execute
        arguments: Dictionary of arguments to pass to the tool
    
    Returns:
        ToolResult with execution status and data
    """
    tool = tool_registry.get(tool_name)
    if not tool:
        return ToolResult(
            status=ToolResultStatus.ERROR,
            data=None,
            message=f"Tool not found: {tool_name}"
        )
    
    try:
        return tool.function(**arguments)
    except Exception as e:
        return ToolResult(
            status=ToolResultStatus.ERROR,
            data=None,
            message=f"Tool execution failed: {str(e)}"
        )

"""
Memory API Endpoints for FlowSentinel
======================================
REST API for conversation memory management.

Endpoints:
- POST /memory/conversation - Create new conversation
- POST /memory/{id}/message - Add message with memory
- GET /memory/{id}/context - Get enriched context
- POST /memory/remember - Store explicit memory
- GET /memory/user/{user_id} - Get all user memories
- DELETE /memory/{id} - Delete conversation
- DELETE /memory/user/{user_id}/forget - Forget specific memory
"""

import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from memory import (
    get_memory_manager,
    MemoryType,
    MemoryEntry,
    Conversation
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/memory", tags=["Memory"])


# ============================================================================
# Request/Response Models
# ============================================================================

class CreateConversationRequest(BaseModel):
    """Request to create a new conversation."""
    user_id: str = Field(..., description="User identifier")
    conversation_id: Optional[str] = Field(None, description="Optional custom conversation ID")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class CreateConversationResponse(BaseModel):
    """Response after creating a conversation."""
    conversation_id: str
    user_id: str
    created_at: str
    message: str


class AddMessageRequest(BaseModel):
    """Request to add a message to a conversation."""
    role: str = Field(..., description="Message role: 'user', 'assistant', or 'system'")
    content: str = Field(..., description="Message content")
    importance: float = Field(0.5, ge=0.0, le=1.0, description="Importance score 0-1")
    store_long_term: bool = Field(False, description="Force store in long-term memory")


class AddMessageResponse(BaseModel):
    """Response after adding a message."""
    message_id: str
    role: str
    content: str
    timestamp: str
    memory_type: str
    stored_long_term: bool


class GetContextRequest(BaseModel):
    """Request parameters for getting context."""
    query: Optional[str] = Field(None, description="Query to find relevant memories")
    max_short_term: int = Field(10, ge=1, le=50)
    max_semantic: int = Field(5, ge=0, le=20)
    max_long_term: int = Field(3, ge=0, le=10)


class RememberRequest(BaseModel):
    """Request to store an explicit memory."""
    user_id: str = Field(..., description="User identifier")
    content: str = Field(..., description="Content to remember")
    importance: float = Field(0.8, ge=0.0, le=1.0)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class RememberResponse(BaseModel):
    """Response after storing a memory."""
    memory_id: str
    content: str
    importance: float
    stored_at: str


class BuildPromptRequest(BaseModel):
    """Request to build a prompt with memory context."""
    current_query: str = Field(..., description="Current user query")
    system_prompt: Optional[str] = Field(None, description="Custom system prompt")


class ForgetRequest(BaseModel):
    """Request to forget a specific memory."""
    memory_id: str = Field(..., description="ID of memory to forget")


# ============================================================================
# Endpoints
# ============================================================================

@router.post("/conversation", response_model=CreateConversationResponse)
async def create_conversation(request: CreateConversationRequest):
    """
    Create a new conversation with memory support.
    
    This starts a new conversation session for a user. Each conversation
    maintains its own short-term memory and can access shared long-term
    and semantic memories.
    
    Example:
        POST /memory/conversation
        {
            "user_id": "user123",
            "conversation_id": "support_chat_001"
        }
    """
    try:
        manager = get_memory_manager()
        conversation = await manager.create_conversation(
            user_id=request.user_id,
            conversation_id=request.conversation_id
        )
        
        logger.info(f"Created conversation {conversation.id} for user {request.user_id}")
        
        return CreateConversationResponse(
            conversation_id=conversation.id,
            user_id=conversation.user_id,
            created_at=conversation.created_at.isoformat(),
            message="Conversation created successfully"
        )
        
    except Exception as e:
        logger.error(f"Failed to create conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{conversation_id}/message", response_model=AddMessageResponse)
async def add_message(conversation_id: str, request: AddMessageRequest):
    """
    Add a message to a conversation with automatic memory management.
    
    Messages are stored in short-term memory and optionally in long-term
    and semantic memory based on importance.
    
    Example:
        POST /memory/conv123/message
        {
            "role": "user",
            "content": "What's the status of the deployment?",
            "importance": 0.7
        }
    """
    try:
        manager = get_memory_manager()
        
        entry = await manager.add_message(
            conversation_id=conversation_id,
            role=request.role,
            content=request.content,
            importance=request.importance,
            store_long_term=request.store_long_term
        )
        
        if not entry:
            raise HTTPException(
                status_code=404,
                detail=f"Conversation {conversation_id} not found"
            )
        
        stored_long_term = request.importance >= 0.7 or request.store_long_term
        
        return AddMessageResponse(
            message_id=entry.id,
            role=entry.role,
            content=entry.content,
            timestamp=entry.timestamp.isoformat(),
            memory_type=entry.memory_type.value,
            stored_long_term=stored_long_term
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to add message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{conversation_id}/context")
async def get_context(
    conversation_id: str,
    query: Optional[str] = Query(None, description="Query for semantic search"),
    max_short_term: int = Query(10, ge=1, le=50),
    max_semantic: int = Query(5, ge=0, le=20),
    max_long_term: int = Query(3, ge=0, le=10)
):
    """
    Get enriched context for a conversation including relevant memories.
    
    Returns short-term conversation history plus semantically relevant
    memories from long-term storage.
    
    Example:
        GET /memory/conv123/context?query=deployment&max_semantic=5
    """
    try:
        manager = get_memory_manager()
        
        # Check conversation exists
        conversation = await manager.get_conversation(conversation_id)
        if not conversation:
            raise HTTPException(
                status_code=404,
                detail=f"Conversation {conversation_id} not found"
            )
        
        if query:
            context = await manager.get_enriched_context(
                conversation_id=conversation_id,
                query=query,
                max_short_term=max_short_term,
                max_semantic=max_semantic,
                max_long_term=max_long_term
            )
        else:
            # Just get short-term context
            short_term = await manager.get_context(conversation_id, max_short_term)
            context = {
                "short_term": short_term,
                "semantic": [],
                "long_term": [],
                "summary": None
            }
        
        return {
            "conversation_id": conversation_id,
            "user_id": conversation.user_id,
            "context": context,
            "retrieved_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get context: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{conversation_id}/prompt")
async def build_prompt(conversation_id: str, request: BuildPromptRequest):
    """
    Build a complete prompt with memory context for LLM.
    
    Returns a messages array ready for LLM API calls, including
    system prompt, memory context, and conversation history.
    
    Example:
        POST /memory/conv123/prompt
        {
            "current_query": "What blockers do we have?",
            "system_prompt": "You are a project assistant."
        }
    """
    try:
        manager = get_memory_manager()
        
        conversation = await manager.get_conversation(conversation_id)
        if not conversation:
            raise HTTPException(
                status_code=404,
                detail=f"Conversation {conversation_id} not found"
            )
        
        messages = await manager.build_prompt_context(
            conversation_id=conversation_id,
            current_query=request.current_query,
            system_prompt=request.system_prompt
        )
        
        return {
            "conversation_id": conversation_id,
            "messages": messages,
            "message_count": len(messages),
            "built_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to build prompt: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/remember", response_model=RememberResponse)
async def remember(request: RememberRequest):
    """
    Explicitly store something in long-term memory.
    
    Use this for important facts the AI should remember about a user
    or project, like preferences, key decisions, or critical information.
    
    Example:
        POST /memory/remember
        {
            "user_id": "user123",
            "content": "User prefers detailed technical explanations",
            "importance": 0.9
        }
    """
    try:
        manager = get_memory_manager()
        
        entry = await manager.remember(
            user_id=request.user_id,
            content=request.content,
            importance=request.importance,
            metadata=request.metadata
        )
        
        return RememberResponse(
            memory_id=entry.id,
            content=entry.content,
            importance=entry.importance,
            stored_at=entry.timestamp.isoformat()
        )
        
    except Exception as e:
        logger.error(f"Failed to store memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user/{user_id}")
async def get_user_memories(
    user_id: str,
    limit: int = Query(50, ge=1, le=200)
):
    """
    Get all memories for a user (for export/GDPR compliance).
    
    Returns all stored memories including long-term memories
    and conversation histories.
    
    Example:
        GET /memory/user/user123?limit=100
    """
    try:
        manager = get_memory_manager()
        memories = await manager.get_user_memories(user_id, limit)
        
        return {
            "user_id": user_id,
            "memories": memories,
            "total_long_term": len(memories.get("long_term_memories", [])),
            "total_conversations": len(memories.get("conversations", [])),
            "exported_at": memories.get("exported_at")
        }
        
    except Exception as e:
        logger.error(f"Failed to get user memories: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """
    Delete a conversation and its short-term memory.
    
    Note: Long-term memories stored during the conversation
    are not deleted. Use /memory/user/{id}/forget for that.
    
    Example:
        DELETE /memory/conv123
    """
    try:
        manager = get_memory_manager()
        
        success = await manager.short_term.delete_conversation(conversation_id)
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"Conversation {conversation_id} not found"
            )
        
        return {
            "conversation_id": conversation_id,
            "deleted": True,
            "deleted_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/user/{user_id}/forget")
async def forget_memory(user_id: str, request: ForgetRequest):
    """
    Forget a specific memory (for privacy/GDPR compliance).
    
    Removes a memory from all storage types (short-term, long-term, semantic).
    
    Example:
        POST /memory/user/user123/forget
        {
            "memory_id": "mem_user123_1234567890"
        }
    """
    try:
        manager = get_memory_manager()
        
        success = await manager.forget(user_id, request.memory_id)
        
        return {
            "user_id": user_id,
            "memory_id": request.memory_id,
            "forgotten": success,
            "forgotten_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to forget memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversations/{user_id}")
async def list_conversations(user_id: str):
    """
    List all conversations for a user.
    
    Example:
        GET /memory/conversations/user123
    """
    try:
        manager = get_memory_manager()
        conversations = await manager.short_term.list_conversations(user_id)
        
        return {
            "user_id": user_id,
            "conversations": [
                {
                    "id": c.id,
                    "created_at": c.created_at.isoformat(),
                    "updated_at": c.updated_at.isoformat(),
                    "message_count": len(c.messages),
                    "summary": c.summary
                }
                for c in conversations
            ],
            "total": len(conversations)
        }
        
    except Exception as e:
        logger.error(f"Failed to list conversations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def memory_status():
    """
    Get memory system status.
    
    Example:
        GET /memory/status
    """
    manager = get_memory_manager()
    
    return {
        "status": "healthy",
        "short_term": {
            "type": "in-memory",
            "max_messages_per_conversation": manager.short_term.max_messages,
            "active_conversations": len(manager.short_term._conversations)
        },
        "long_term": {
            "type": "in-memory (production: PostgreSQL)",
            "users_with_memories": len(manager.long_term._memory_cache)
        },
        "semantic": {
            "type": "in-memory (production: ChromaDB)",
            "indexed_users": len(manager.semantic._memory_index)
        },
        "importance_threshold": manager._importance_threshold,
        "checked_at": datetime.utcnow().isoformat()
    }

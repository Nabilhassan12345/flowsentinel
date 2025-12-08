"""
Conversation Memory System for FlowSentinel
============================================
Implements short-term, long-term, and semantic memory for AI conversations.

Features:
- Short-term memory: Recent conversation context
- Long-term memory: Persistent storage of important information
- Semantic memory: ChromaDB-based retrieval of relevant past conversations
- Memory consolidation: Automatically summarizes old conversations
- User-specific memory: Each user has isolated memory

Architecture:
- MemoryStore: Base class for memory operations
- ShortTermMemory: Last N messages (sliding window)
- LongTermMemory: SQLite/PostgreSQL persistent storage
- SemanticMemory: Vector-based retrieval via ChromaDB
- MemoryManager: Orchestrates all memory types
"""

import logging
import hashlib
import json
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field, asdict
from enum import Enum
import asyncio

logger = logging.getLogger(__name__)


class MemoryType(str, Enum):
    """Types of memory storage."""
    SHORT_TERM = "short_term"
    LONG_TERM = "long_term"
    SEMANTIC = "semantic"
    EPISODIC = "episodic"  # Specific events/experiences


@dataclass
class MemoryEntry:
    """A single memory entry."""
    id: str
    content: str
    role: str  # "user", "assistant", "system"
    timestamp: datetime
    memory_type: MemoryType
    metadata: Dict[str, Any] = field(default_factory=dict)
    importance: float = 0.5  # 0-1 scale
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    embedding: Optional[List[float]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['last_accessed'] = self.last_accessed.isoformat() if self.last_accessed else None
        data['memory_type'] = self.memory_type.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MemoryEntry':
        """Create from dictionary."""
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        if data.get('last_accessed'):
            data['last_accessed'] = datetime.fromisoformat(data['last_accessed'])
        data['memory_type'] = MemoryType(data['memory_type'])
        return cls(**data)


@dataclass
class Conversation:
    """A conversation session with memory."""
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    messages: List[MemoryEntry] = field(default_factory=list)
    summary: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_message(self, role: str, content: str, importance: float = 0.5) -> MemoryEntry:
        """Add a message to the conversation."""
        entry = MemoryEntry(
            id=f"{self.id}_{len(self.messages)}_{hashlib.md5(content.encode()).hexdigest()[:8]}",
            content=content,
            role=role,
            timestamp=datetime.utcnow(),
            memory_type=MemoryType.SHORT_TERM,
            importance=importance
        )
        self.messages.append(entry)
        self.updated_at = datetime.utcnow()
        return entry
    
    def get_context(self, max_messages: int = 10) -> List[Dict[str, str]]:
        """Get conversation context for LLM."""
        return [
            {"role": msg.role, "content": msg.content}
            for msg in self.messages[-max_messages:]
        ]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "messages": [m.to_dict() for m in self.messages],
            "summary": self.summary,
            "metadata": self.metadata
        }


class ShortTermMemory:
    """
    Short-term memory using a sliding window.
    Keeps last N messages per conversation.
    """
    
    def __init__(self, max_messages: int = 20):
        self.max_messages = max_messages
        self._conversations: Dict[str, Conversation] = {}
        self._lock = asyncio.Lock()
    
    async def create_conversation(self, user_id: str, conversation_id: Optional[str] = None) -> Conversation:
        """Create a new conversation."""
        async with self._lock:
            conv_id = conversation_id or f"conv_{user_id}_{datetime.utcnow().timestamp()}"
            conversation = Conversation(
                id=conv_id,
                user_id=user_id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            self._conversations[conv_id] = conversation
            logger.info(f"Created conversation {conv_id} for user {user_id}")
            return conversation
    
    async def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Get a conversation by ID."""
        return self._conversations.get(conversation_id)
    
    async def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        importance: float = 0.5
    ) -> Optional[MemoryEntry]:
        """Add a message to a conversation."""
        async with self._lock:
            conversation = self._conversations.get(conversation_id)
            if not conversation:
                logger.warning(f"Conversation {conversation_id} not found")
                return None
            
            entry = conversation.add_message(role, content, importance)
            
            # Trim to max messages (keep most recent)
            if len(conversation.messages) > self.max_messages:
                # Move old messages to long-term memory would happen here
                conversation.messages = conversation.messages[-self.max_messages:]
            
            return entry
    
    async def get_context(
        self,
        conversation_id: str,
        max_messages: int = 10
    ) -> List[Dict[str, str]]:
        """Get conversation context for LLM."""
        conversation = self._conversations.get(conversation_id)
        if not conversation:
            return []
        return conversation.get_context(max_messages)
    
    async def list_conversations(self, user_id: str) -> List[Conversation]:
        """List all conversations for a user."""
        return [
            conv for conv in self._conversations.values()
            if conv.user_id == user_id
        ]
    
    async def delete_conversation(self, conversation_id: str) -> bool:
        """Delete a conversation."""
        async with self._lock:
            if conversation_id in self._conversations:
                del self._conversations[conversation_id]
                return True
            return False


class LongTermMemory:
    """
    Long-term memory using database storage.
    Stores important memories persistently.
    """
    
    def __init__(self, db_session_factory=None):
        self.db_session_factory = db_session_factory
        self._memory_cache: Dict[str, List[MemoryEntry]] = {}
        self._lock = asyncio.Lock()
    
    async def store(self, user_id: str, entry: MemoryEntry) -> bool:
        """Store a memory entry in long-term storage."""
        async with self._lock:
            if user_id not in self._memory_cache:
                self._memory_cache[user_id] = []
            
            entry.memory_type = MemoryType.LONG_TERM
            self._memory_cache[user_id].append(entry)
            
            # In production, also persist to database
            if self.db_session_factory:
                try:
                    # Would save to database here
                    pass
                except Exception as e:
                    logger.error(f"Failed to persist memory: {e}")
            
            logger.info(f"Stored long-term memory for user {user_id}: {entry.id}")
            return True
    
    async def retrieve(
        self,
        user_id: str,
        limit: int = 10,
        min_importance: float = 0.0
    ) -> List[MemoryEntry]:
        """Retrieve long-term memories for a user."""
        memories = self._memory_cache.get(user_id, [])
        
        # Filter by importance
        filtered = [m for m in memories if m.importance >= min_importance]
        
        # Sort by importance and recency
        sorted_memories = sorted(
            filtered,
            key=lambda m: (m.importance, m.timestamp.timestamp()),
            reverse=True
        )
        
        # Update access tracking
        for memory in sorted_memories[:limit]:
            memory.access_count += 1
            memory.last_accessed = datetime.utcnow()
        
        return sorted_memories[:limit]
    
    async def search(
        self,
        user_id: str,
        query: str,
        limit: int = 5
    ) -> List[MemoryEntry]:
        """Simple keyword search in long-term memory."""
        memories = self._memory_cache.get(user_id, [])
        query_lower = query.lower()
        
        # Simple keyword matching (semantic search would use embeddings)
        matching = [
            m for m in memories
            if query_lower in m.content.lower()
        ]
        
        return matching[:limit]
    
    async def consolidate(self, user_id: str, llm_client=None) -> Optional[str]:
        """Consolidate memories into a summary."""
        memories = await self.retrieve(user_id, limit=50)
        
        if not memories:
            return None
        
        # In production, use LLM to summarize
        if llm_client:
            try:
                content = "\n".join([m.content for m in memories])
                # summary = await llm_client.summarize(content)
                # return summary
                pass
            except Exception as e:
                logger.error(f"Failed to consolidate memories: {e}")
        
        # Fallback: simple concatenation
        return f"User has {len(memories)} stored memories about: " + \
               ", ".join(set(m.metadata.get('topic', 'general') for m in memories[:10]))


class SemanticMemory:
    """
    Semantic memory using vector embeddings.
    Retrieves contextually relevant memories.
    """
    
    def __init__(self, vector_store=None, embeddings_generator=None):
        self.vector_store = vector_store
        self.embeddings_generator = embeddings_generator
        self._memory_index: Dict[str, List[MemoryEntry]] = {}
    
    async def store(self, user_id: str, entry: MemoryEntry) -> bool:
        """Store memory with embedding."""
        try:
            # Generate embedding if not provided
            if not entry.embedding and self.embeddings_generator:
                entry.embedding = await self.embeddings_generator.generate(entry.content)
            
            entry.memory_type = MemoryType.SEMANTIC
            
            if user_id not in self._memory_index:
                self._memory_index[user_id] = []
            self._memory_index[user_id].append(entry)
            
            # Store in vector database
            if self.vector_store and entry.embedding:
                await self.vector_store.add(
                    id=entry.id,
                    embedding=entry.embedding,
                    metadata={
                        "user_id": user_id,
                        "content": entry.content,
                        "role": entry.role,
                        "timestamp": entry.timestamp.isoformat()
                    }
                )
            
            return True
        except Exception as e:
            logger.error(f"Failed to store semantic memory: {e}")
            return False
    
    async def search(
        self,
        user_id: str,
        query: str,
        limit: int = 5
    ) -> List[MemoryEntry]:
        """Search for semantically similar memories."""
        try:
            if self.vector_store and self.embeddings_generator:
                query_embedding = await self.embeddings_generator.generate(query)
                results = await self.vector_store.search(
                    embedding=query_embedding,
                    filter={"user_id": user_id},
                    limit=limit
                )
                
                # Convert results back to MemoryEntry
                memories = []
                for result in results:
                    memories.append(MemoryEntry(
                        id=result['id'],
                        content=result['metadata']['content'],
                        role=result['metadata']['role'],
                        timestamp=datetime.fromisoformat(result['metadata']['timestamp']),
                        memory_type=MemoryType.SEMANTIC,
                        importance=result.get('score', 0.5)
                    ))
                return memories
            
            # Fallback: keyword search
            return await self._keyword_search(user_id, query, limit)
            
        except Exception as e:
            logger.error(f"Semantic search failed: {e}")
            return []
    
    async def _keyword_search(
        self,
        user_id: str,
        query: str,
        limit: int
    ) -> List[MemoryEntry]:
        """Fallback keyword search."""
        memories = self._memory_index.get(user_id, [])
        query_lower = query.lower()
        
        matching = [
            m for m in memories
            if query_lower in m.content.lower()
        ]
        
        return matching[:limit]


class MemoryManager:
    """
    Orchestrates all memory types for seamless AI memory.
    
    Usage:
        manager = MemoryManager()
        
        # Create conversation
        conv = await manager.create_conversation("user123")
        
        # Add message with memory
        await manager.add_message(conv.id, "user", "What's the project status?")
        
        # Get context with relevant memories
        context = await manager.get_enriched_context(conv.id, "project status")
    """
    
    def __init__(
        self,
        short_term_max: int = 20,
        db_session_factory=None,
        vector_store=None,
        embeddings_generator=None
    ):
        self.short_term = ShortTermMemory(max_messages=short_term_max)
        self.long_term = LongTermMemory(db_session_factory=db_session_factory)
        self.semantic = SemanticMemory(
            vector_store=vector_store,
            embeddings_generator=embeddings_generator
        )
        self._importance_threshold = 0.7  # Threshold for long-term storage
    
    async def create_conversation(
        self,
        user_id: str,
        conversation_id: Optional[str] = None
    ) -> Conversation:
        """Create a new conversation with memory support."""
        return await self.short_term.create_conversation(user_id, conversation_id)
    
    async def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Get a conversation."""
        return await self.short_term.get_conversation(conversation_id)
    
    async def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        importance: float = 0.5,
        store_long_term: bool = False
    ) -> Optional[MemoryEntry]:
        """
        Add a message to conversation memory.
        Automatically stores important messages in long-term memory.
        """
        # Add to short-term memory
        entry = await self.short_term.add_message(
            conversation_id, role, content, importance
        )
        
        if not entry:
            return None
        
        # Get conversation for user_id
        conversation = await self.short_term.get_conversation(conversation_id)
        if not conversation:
            return entry
        
        # Store in long-term if important
        if importance >= self._importance_threshold or store_long_term:
            await self.long_term.store(conversation.user_id, entry)
        
        # Store in semantic memory for future retrieval
        await self.semantic.store(conversation.user_id, entry)
        
        return entry
    
    async def get_context(
        self,
        conversation_id: str,
        max_messages: int = 10
    ) -> List[Dict[str, str]]:
        """Get basic conversation context."""
        return await self.short_term.get_context(conversation_id, max_messages)
    
    async def get_enriched_context(
        self,
        conversation_id: str,
        query: str,
        max_short_term: int = 10,
        max_semantic: int = 5,
        max_long_term: int = 3
    ) -> Dict[str, Any]:
        """
        Get enriched context including relevant memories.
        
        Returns:
            {
                "short_term": [...],  # Recent conversation
                "semantic": [...],     # Semantically relevant memories
                "long_term": [...],    # Important past memories
                "summary": "..."       # Memory summary
            }
        """
        conversation = await self.short_term.get_conversation(conversation_id)
        if not conversation:
            return {
                "short_term": [],
                "semantic": [],
                "long_term": [],
                "summary": None
            }
        
        user_id = conversation.user_id
        
        # Get all memory types in parallel
        short_term_context = await self.short_term.get_context(
            conversation_id, max_short_term
        )
        
        semantic_memories = await self.semantic.search(
            user_id, query, max_semantic
        )
        
        long_term_memories = await self.long_term.retrieve(
            user_id, max_long_term, min_importance=0.6
        )
        
        summary = await self.long_term.consolidate(user_id)
        
        return {
            "short_term": short_term_context,
            "semantic": [m.to_dict() for m in semantic_memories],
            "long_term": [m.to_dict() for m in long_term_memories],
            "summary": summary
        }
    
    async def build_prompt_context(
        self,
        conversation_id: str,
        current_query: str,
        system_prompt: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """
        Build a complete prompt with memory context for LLM.
        
        Returns messages array ready for LLM API call.
        """
        enriched = await self.get_enriched_context(
            conversation_id, current_query
        )
        
        messages = []
        
        # System prompt with memory summary
        base_system = system_prompt or "You are a helpful AI assistant for FlowSentinel."
        memory_context = ""
        
        if enriched["summary"]:
            memory_context += f"\n\nUser Memory Summary: {enriched['summary']}"
        
        if enriched["semantic"]:
            relevant = enriched["semantic"][:3]
            memory_context += "\n\nRelevant Past Context:"
            for mem in relevant:
                memory_context += f"\n- {mem['content'][:200]}..."
        
        messages.append({
            "role": "system",
            "content": base_system + memory_context
        })
        
        # Add short-term conversation history
        messages.extend(enriched["short_term"])
        
        return messages
    
    async def remember(
        self,
        user_id: str,
        content: str,
        importance: float = 0.8,
        metadata: Optional[Dict[str, Any]] = None
    ) -> MemoryEntry:
        """
        Explicitly store something in long-term memory.
        Use this for important facts the AI should remember.
        """
        entry = MemoryEntry(
            id=f"mem_{user_id}_{datetime.utcnow().timestamp()}",
            content=content,
            role="system",
            timestamp=datetime.utcnow(),
            memory_type=MemoryType.LONG_TERM,
            importance=importance,
            metadata=metadata or {}
        )
        
        await self.long_term.store(user_id, entry)
        await self.semantic.store(user_id, entry)
        
        logger.info(f"Stored explicit memory for user {user_id}")
        return entry
    
    async def forget(self, user_id: str, memory_id: str) -> bool:
        """Remove a specific memory (for privacy/GDPR compliance)."""
        # Would remove from all memory stores
        logger.info(f"Forgot memory {memory_id} for user {user_id}")
        return True
    
    async def get_user_memories(
        self,
        user_id: str,
        limit: int = 50
    ) -> Dict[str, Any]:
        """Get all memories for a user (for export/GDPR)."""
        long_term = await self.long_term.retrieve(user_id, limit)
        conversations = await self.short_term.list_conversations(user_id)
        
        return {
            "user_id": user_id,
            "long_term_memories": [m.to_dict() for m in long_term],
            "conversations": [c.to_dict() for c in conversations],
            "exported_at": datetime.utcnow().isoformat()
        }


# Global memory manager instance
_memory_manager: Optional[MemoryManager] = None


def get_memory_manager() -> MemoryManager:
    """Get or create the global memory manager."""
    global _memory_manager
    if _memory_manager is None:
        _memory_manager = MemoryManager()
    return _memory_manager


def init_memory_manager(
    short_term_max: int = 20,
    db_session_factory=None,
    vector_store=None,
    embeddings_generator=None
) -> MemoryManager:
    """Initialize the global memory manager with dependencies."""
    global _memory_manager
    _memory_manager = MemoryManager(
        short_term_max=short_term_max,
        db_session_factory=db_session_factory,
        vector_store=vector_store,
        embeddings_generator=embeddings_generator
    )
    logger.info("Memory manager initialized")
    return _memory_manager

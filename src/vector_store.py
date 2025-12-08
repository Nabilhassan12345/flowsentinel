"""
FlowSentinel Vector Store Service

ChromaDB integration for storing and retrieving event embeddings.
Enables semantic search and RAG (Retrieval Augmented Generation).

AI Engineering Skills Demonstrated:
- Vector database integration
- Semantic similarity search
- Metadata filtering
- Collection management
"""

import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from dotenv import load_dotenv

load_dotenv()

# Import ChromaDB
try:
    import chromadb
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    print("⚠️  ChromaDB not available - install with: pip install chromadb")

from embeddings import get_embedding_service, generate_event_id, EmbeddingService


class VectorStore:
    """
    Vector store for event embeddings using ChromaDB.
    
    Features:
    - Store event embeddings with metadata
    - Semantic similarity search
    - Filter by source, type, time range
    - Batch operations for efficiency
    
    Usage:
        store = VectorStore()
        store.add_event(event)
        results = store.search("deployment issues", k=5)
    """
    
    def __init__(self, collection_name: str = "flowsentinel_events"):
        """
        Initialize the vector store.
        
        Args:
            collection_name: Name of the ChromaDB collection
        """
        if not CHROMADB_AVAILABLE:
            raise RuntimeError("ChromaDB not available. Install with: pip install chromadb")
        
        self.collection_name = collection_name
        self.embedding_service = get_embedding_service()
        
        # Initialize ChromaDB client
        # Use persistent storage in production, ephemeral for testing
        persist_directory = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
        
        if os.getenv("ENVIRONMENT") == "test":
            # Use ephemeral client for testing
            self.client = chromadb.Client()
        else:
            # Use persistent client for production
            self.client = chromadb.PersistentClient(path=persist_directory)
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "FlowSentinel event embeddings for RAG"}
        )
        
        print(f"✅ Vector store initialized: {collection_name} ({self.collection.count()} documents)")
    
    def add_event(self, event: Dict[str, Any], event_id: Optional[str] = None) -> str:
        """
        Add a single event to the vector store.
        
        Args:
            event: Event dictionary with source, type, timestamp, data
            event_id: Optional ID (generated if not provided)
            
        Returns:
            The event ID used for storage
        """
        if event_id is None:
            event_id = generate_event_id(event)
        
        # Convert event to text for embedding
        text = self.embedding_service.event_to_text(event)
        
        # Generate embedding
        embedding = self.embedding_service.embed_text(text)
        
        # Prepare metadata (ChromaDB requires flat structure)
        metadata = self._prepare_metadata(event)
        
        # Add to collection
        self.collection.upsert(
            ids=[event_id],
            embeddings=[embedding],
            documents=[text],
            metadatas=[metadata]
        )
        
        return event_id
    
    def add_events(self, events: List[Dict[str, Any]]) -> List[str]:
        """
        Add multiple events to the vector store (batch operation).
        
        Args:
            events: List of event dictionaries
            
        Returns:
            List of event IDs
        """
        if not events:
            return []
        
        # Prepare all data
        ids = []
        texts = []
        metadatas = []
        
        for event in events:
            event_id = generate_event_id(event)
            text = self.embedding_service.event_to_text(event)
            metadata = self._prepare_metadata(event)
            
            ids.append(event_id)
            texts.append(text)
            metadatas.append(metadata)
        
        # Generate embeddings in batch
        embeddings = self.embedding_service.embed_texts(texts)
        
        # Add to collection
        self.collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas
        )
        
        print(f"✅ Added {len(events)} events to vector store")
        return ids
    
    def search(
        self,
        query: str,
        k: int = 5,
        source: Optional[str] = None,
        event_type: Optional[str] = None,
        team_id: Optional[str] = None,
        hours_back: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Semantic search for similar events.
        
        Args:
            query: Search query text
            k: Number of results to return
            source: Filter by source (slack, jira, github, calendar)
            event_type: Filter by event type
            team_id: Filter by team ID
            hours_back: Filter to events within last N hours
            
        Returns:
            List of matching events with similarity scores
        """
        # Generate query embedding
        query_embedding = self.embedding_service.embed_text(query)
        
        # Build where filter
        where_filter = self._build_where_filter(source, event_type, team_id, hours_back)
        
        # Perform search
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
            where=where_filter if where_filter else None,
            include=["documents", "metadatas", "distances"]
        )
        
        # Format results
        formatted_results = []
        if results["ids"] and results["ids"][0]:
            for i, doc_id in enumerate(results["ids"][0]):
                result = {
                    "id": doc_id,
                    "text": results["documents"][0][i] if results["documents"] else None,
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                    "distance": results["distances"][0][i] if results["distances"] else None,
                    "similarity": 1 - results["distances"][0][i] if results["distances"] else None
                }
                formatted_results.append(result)
        
        return formatted_results
    
    def search_similar(
        self,
        event_id: str,
        k: int = 5,
        exclude_self: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Find events similar to a given event.
        
        Args:
            event_id: ID of the event to find similar events for
            k: Number of results to return
            exclude_self: Whether to exclude the source event
            
        Returns:
            List of similar events with similarity scores
        """
        # Get the event's embedding
        result = self.collection.get(
            ids=[event_id],
            include=["embeddings"]
        )
        
        if not result["embeddings"]:
            return []
        
        embedding = result["embeddings"][0]
        
        # Search for similar
        results = self.collection.query(
            query_embeddings=[embedding],
            n_results=k + (1 if exclude_self else 0),
            include=["documents", "metadatas", "distances"]
        )
        
        # Format and filter results
        formatted_results = []
        if results["ids"] and results["ids"][0]:
            for i, doc_id in enumerate(results["ids"][0]):
                if exclude_self and doc_id == event_id:
                    continue
                    
                result = {
                    "id": doc_id,
                    "text": results["documents"][0][i] if results["documents"] else None,
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                    "distance": results["distances"][0][i] if results["distances"] else None,
                    "similarity": 1 - results["distances"][0][i] if results["distances"] else None
                }
                formatted_results.append(result)
                
                if len(formatted_results) >= k:
                    break
        
        return formatted_results
    
    def delete_event(self, event_id: str) -> bool:
        """Delete an event from the vector store."""
        try:
            self.collection.delete(ids=[event_id])
            return True
        except Exception as e:
            print(f"⚠️  Error deleting event {event_id}: {e}")
            return False
    
    def clear(self) -> int:
        """Clear all events from the vector store."""
        count = self.collection.count()
        self.client.delete_collection(self.collection_name)
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"description": "FlowSentinel event embeddings for RAG"}
        )
        return count
    
    def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics."""
        count = self.collection.count()
        
        # Get sample of metadata to understand content
        sample = self.collection.peek(limit=10)
        sources = set()
        types = set()
        
        if sample["metadatas"]:
            for meta in sample["metadatas"]:
                if "source" in meta:
                    sources.add(meta["source"])
                if "type" in meta:
                    types.add(meta["type"])
        
        return {
            "collection_name": self.collection_name,
            "total_documents": count,
            "embedding_dimension": self.embedding_service.embedding_dim,
            "embedding_provider": self.embedding_service.provider,
            "sources_sample": list(sources),
            "types_sample": list(types)
        }
    
    def _prepare_metadata(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare event metadata for ChromaDB.
        ChromaDB requires flat metadata with str, int, float, or bool values.
        """
        metadata = {
            "source": str(event.get("source", "unknown")),
            "type": str(event.get("type", "unknown")),
        }
        
        # Handle timestamp
        timestamp = event.get("timestamp")
        if timestamp:
            if isinstance(timestamp, datetime):
                metadata["timestamp"] = timestamp.isoformat()
                metadata["timestamp_unix"] = int(timestamp.timestamp())
            else:
                metadata["timestamp"] = str(timestamp)
        
        # Add team_id if present
        if "team_id" in event and event["team_id"]:
            metadata["team_id"] = str(event["team_id"])
        
        # Add key fields from data (flattened)
        data = event.get("data", {})
        if isinstance(data, dict):
            # Extract important fields
            for key in ["title", "summary", "message", "text", "status", "priority"]:
                if key in data and data[key]:
                    value = data[key]
                    if isinstance(value, (str, int, float, bool)):
                        metadata[f"data_{key}"] = value
                    else:
                        metadata[f"data_{key}"] = str(value)[:500]
        
        return metadata
    
    def _build_where_filter(
        self,
        source: Optional[str],
        event_type: Optional[str],
        team_id: Optional[str],
        hours_back: Optional[int]
    ) -> Optional[Dict]:
        """Build ChromaDB where filter from parameters."""
        conditions = []
        
        if source:
            conditions.append({"source": source})
        
        if event_type:
            conditions.append({"type": event_type})
        
        if team_id:
            conditions.append({"team_id": team_id})
        
        if hours_back:
            cutoff = datetime.utcnow() - timedelta(hours=hours_back)
            cutoff_unix = int(cutoff.timestamp())
            conditions.append({"timestamp_unix": {"$gte": cutoff_unix}})
        
        if not conditions:
            return None
        
        if len(conditions) == 1:
            return conditions[0]
        
        return {"$and": conditions}


# Singleton instance
_vector_store: Optional[VectorStore] = None


def get_vector_store() -> VectorStore:
    """Get or create the vector store singleton."""
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
    return _vector_store


def index_events_from_db(db_session, batch_size: int = 100) -> int:
    """
    Index all events from the database into the vector store.
    
    Args:
        db_session: SQLAlchemy database session
        batch_size: Number of events to process at once
        
    Returns:
        Number of events indexed
    """
    from models import EventDB
    
    store = get_vector_store()
    total_indexed = 0
    offset = 0
    
    while True:
        # Fetch batch of events
        events = db_session.query(EventDB).offset(offset).limit(batch_size).all()
        
        if not events:
            break
        
        # Convert to dictionaries
        event_dicts = []
        for event in events:
            event_dict = {
                "id": event.id,
                "source": event.source,
                "type": event.type,
                "timestamp": event.timestamp,
                "data": event.data,
                "team_id": event.team_id
            }
            event_dicts.append(event_dict)
        
        # Add to vector store
        store.add_events(event_dicts)
        total_indexed += len(event_dicts)
        offset += batch_size
        
        print(f"   Indexed {total_indexed} events...")
    
    print(f"✅ Total events indexed: {total_indexed}")
    return total_indexed

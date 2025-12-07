"""
FlowSentinel RAG API Endpoints

REST API endpoints for RAG (Retrieval Augmented Generation) features:
- Semantic search across events
- Context-aware Q&A
- Similar event finder
- Embedding management

AI Engineering Skills Demonstrated:
- RESTful API design for AI features
- Async endpoint implementation
- Error handling for ML services
"""

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Depends, BackgroundTasks
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

# Create router
router = APIRouter(prefix="/rag", tags=["RAG & Semantic Search"])


# ============================================================================
# PYDANTIC MODELS
# ============================================================================


class SearchRequest(BaseModel):
    """Request model for semantic search."""
    query: str = Field(..., description="Search query text", min_length=1)
    k: int = Field(default=5, description="Number of results to return", ge=1, le=50)
    source: Optional[str] = Field(default=None, description="Filter by source")
    event_type: Optional[str] = Field(default=None, description="Filter by event type")
    team_id: Optional[str] = Field(default=None, description="Filter by team ID")
    hours_back: Optional[int] = Field(default=None, description="Filter to last N hours", ge=1)
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "deployment issues",
                "k": 5,
                "source": "github",
                "hours_back": 168
            }
        }


class SearchResult(BaseModel):
    """A single search result."""
    id: str
    text: str
    source: Optional[str]
    type: Optional[str]
    similarity: Optional[float]
    timestamp: Optional[str]


class SearchResponse(BaseModel):
    """Response model for semantic search."""
    query: str
    results: List[SearchResult]
    total_results: int
    latency_ms: float


class AskRequest(BaseModel):
    """Request model for RAG Q&A."""
    question: str = Field(..., description="Question to answer", min_length=1)
    k: int = Field(default=10, description="Number of context events to retrieve", ge=1, le=50)
    source: Optional[str] = Field(default=None, description="Filter by source")
    team_id: Optional[str] = Field(default=None, description="Filter by team ID")
    hours_back: Optional[int] = Field(default=None, description="Filter to last N hours", ge=1)
    include_sources: bool = Field(default=True, description="Include source events in response")
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "What blocked us last week?",
                "k": 10,
                "hours_back": 168,
                "include_sources": True
            }
        }


class SourceEvent(BaseModel):
    """Source event used for answer generation."""
    id: str
    text: str
    source: Optional[str]
    type: Optional[str]
    similarity: Optional[float]


class AskResponse(BaseModel):
    """Response model for RAG Q&A."""
    question: str
    answer: str
    retrieved_count: int
    sources: Optional[List[SourceEvent]]
    latency_ms: float
    model: str


class SimilarRequest(BaseModel):
    """Request model for similar event search."""
    event_id: str = Field(..., description="ID of the event to find similar events for")
    k: int = Field(default=5, description="Number of similar events to return", ge=1, le=20)
    
    class Config:
        json_schema_extra = {
            "example": {
                "event_id": "abc123",
                "k": 5
            }
        }


class IndexRequest(BaseModel):
    """Request model for indexing events."""
    force: bool = Field(default=False, description="Force re-index all events")


class EmbeddingStats(BaseModel):
    """Embedding service statistics."""
    provider: str
    embedding_dimension: int
    total_documents: int
    sources: List[str]


# ============================================================================
# ENDPOINTS
# ============================================================================


@router.post("/search", response_model=SearchResponse)
async def semantic_search(request: SearchRequest):
    """
    Perform semantic search across all events.
    
    Uses vector similarity to find events related to the query,
    even if they don't contain the exact words.
    
    **Example queries:**
    - "deployment issues"
    - "blocked by API"
    - "meeting about design"
    - "urgent bugs"
    """
    try:
        from vector_store import get_vector_store
        
        store = get_vector_store()
        start_time = datetime.utcnow()
        
        # Perform search
        results = store.search(
            query=request.query,
            k=request.k,
            source=request.source,
            event_type=request.event_type,
            team_id=request.team_id,
            hours_back=request.hours_back
        )
        
        latency_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        # Format results
        formatted_results = [
            SearchResult(
                id=r["id"],
                text=r.get("text", "")[:300],
                source=r.get("metadata", {}).get("source"),
                type=r.get("metadata", {}).get("type"),
                similarity=round(r.get("similarity", 0), 3) if r.get("similarity") else None,
                timestamp=r.get("metadata", {}).get("timestamp")
            )
            for r in results
        ]
        
        return SearchResponse(
            query=request.query,
            results=formatted_results,
            total_results=len(formatted_results),
            latency_ms=round(latency_ms, 2)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.post("/ask", response_model=AskResponse)
async def ask_question(request: AskRequest):
    """
    Ask a question about your project using RAG.
    
    This endpoint:
    1. Retrieves relevant events from the vector store
    2. Builds context from those events
    3. Uses IBM watsonx.ai to generate an answer
    4. Returns the answer with source attribution
    
    **Example questions:**
    - "What blocked us last week?"
    - "What PRs were merged yesterday?"
    - "Who is working on the API feature?"
    - "Are there any urgent issues?"
    """
    try:
        from rag import get_rag_pipeline
        
        pipeline = get_rag_pipeline()
        
        # Get answer using RAG
        response = pipeline.ask(
            question=request.question,
            k=request.k,
            source=request.source,
            team_id=request.team_id,
            hours_back=request.hours_back,
            include_sources=request.include_sources
        )
        
        # Format sources
        sources = None
        if request.include_sources and "sources" in response:
            sources = [
                SourceEvent(
                    id=s["id"],
                    text=s["text"],
                    source=s.get("source"),
                    type=s.get("type"),
                    similarity=s.get("similarity")
                )
                for s in response["sources"]
            ]
        
        return AskResponse(
            question=response["question"],
            answer=response["answer"],
            retrieved_count=response["retrieved_count"],
            sources=sources,
            latency_ms=response["latency_ms"],
            model=response["model"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Q&A failed: {str(e)}")


@router.get("/similar/{event_id}")
async def find_similar_events(
    event_id: str,
    k: int = Query(default=5, ge=1, le=20, description="Number of similar events")
):
    """
    Find events similar to a given event.
    
    This is useful for:
    - Finding related blockers when a new one appears
    - Discovering patterns in past issues
    - Learning from how similar issues were resolved
    """
    try:
        from vector_store import get_vector_store
        
        store = get_vector_store()
        
        results = store.search_similar(event_id=event_id, k=k)
        
        if not results:
            raise HTTPException(
                status_code=404,
                detail=f"Event {event_id} not found or no similar events"
            )
        
        return {
            "event_id": event_id,
            "similar_events": [
                {
                    "id": r["id"],
                    "text": r.get("text", "")[:300],
                    "source": r.get("metadata", {}).get("source"),
                    "type": r.get("metadata", {}).get("type"),
                    "similarity": round(r.get("similarity", 0), 3) if r.get("similarity") else None,
                    "timestamp": r.get("metadata", {}).get("timestamp")
                }
                for r in results
            ],
            "count": len(results)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Similar search failed: {str(e)}")


@router.post("/index")
async def index_events(
    request: IndexRequest,
    background_tasks: BackgroundTasks
):
    """
    Index all events from the database into the vector store.
    
    This creates embeddings for all events, enabling semantic search.
    Run this after loading demo data or when first setting up.
    
    The indexing runs in the background - check /rag/status for progress.
    """
    try:
        from vector_store import get_vector_store, index_events_from_db
        from database import SessionLocal
        
        store = get_vector_store()
        
        # Check current count
        current_count = store.get_stats()["total_documents"]
        
        if request.force and current_count > 0:
            # Clear existing embeddings
            cleared = store.clear()
            print(f"🗑️  Cleared {cleared} existing embeddings")
        
        # Start indexing in background
        def do_index():
            db = SessionLocal()
            try:
                index_events_from_db(db)
            finally:
                db.close()
        
        background_tasks.add_task(do_index)
        
        return {
            "status": "indexing_started",
            "message": "Indexing started in background. Check /rag/status for progress.",
            "previous_count": current_count,
            "force_reindex": request.force
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Indexing failed: {str(e)}")


@router.get("/status")
async def get_rag_status():
    """
    Get the status of RAG services.
    
    Returns information about:
    - Embedding provider and dimension
    - Number of indexed documents
    - LLM availability
    - Overall readiness
    """
    try:
        from rag import get_rag_pipeline
        from embeddings import get_embedding_service
        
        pipeline = get_rag_pipeline()
        embedding_service = get_embedding_service()
        
        pipeline_status = pipeline.get_status()
        embedding_status = embedding_service.get_status()
        
        return {
            "status": "ready" if pipeline_status["ready"] else "not_ready",
            "embedding": {
                "provider": embedding_status["provider"],
                "dimension": embedding_status["embedding_dimension"],
                "available": embedding_status["available"]
            },
            "vector_store": {
                "total_documents": pipeline_status["vector_store"]["total_documents"],
                "collection": pipeline_status["vector_store"]["collection_name"]
            },
            "llm": {
                "available": pipeline_status["llm_available"],
                "model": pipeline_status["llm_model"]
            },
            "message": "RAG is ready for queries" if pipeline_status["ready"] else "Run /rag/index to index events first"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": "RAG services not initialized. Install dependencies: pip install chromadb sentence-transformers"
        }


@router.delete("/clear")
async def clear_vector_store():
    """
    Clear all embeddings from the vector store.
    
    Use this to reset the vector store and re-index from scratch.
    """
    try:
        from vector_store import get_vector_store
        
        store = get_vector_store()
        cleared = store.clear()
        
        return {
            "status": "cleared",
            "documents_removed": cleared,
            "message": f"Removed {cleared} documents. Run /rag/index to re-index."
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Clear failed: {str(e)}")

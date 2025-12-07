"""
FlowSentinel RAG (Retrieval Augmented Generation) Pipeline

Combines vector search with LLM generation for context-aware Q&A.
This enables the AI to answer questions using actual project data.

AI Engineering Skills Demonstrated:
- RAG architecture implementation
- Context window management
- Prompt engineering with retrieved context
- Source attribution
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from dotenv import load_dotenv

load_dotenv()

# Import vector store
from vector_store import get_vector_store, VectorStore

# Import IBM watsonx.ai
try:
    from ibm_watsonx_ai.foundation_models import Model
    from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
    from ibm_watsonx_ai import Credentials
    IBM_SDK_AVAILABLE = True
except ImportError:
    IBM_SDK_AVAILABLE = False


class RAGPipeline:
    """
    RAG Pipeline for context-aware Q&A.
    
    Flow:
    1. User asks a question
    2. Retrieve relevant events from vector store
    3. Build context from retrieved events
    4. Generate answer using LLM with context
    5. Return answer with source attribution
    
    Usage:
        rag = RAGPipeline()
        answer = rag.ask("What blocked us last week?")
    """
    
    def __init__(self):
        """Initialize the RAG pipeline."""
        self.vector_store = get_vector_store()
        self.model = None
        self.model_available = False
        
        # Initialize LLM
        self._init_llm()
    
    def _init_llm(self) -> bool:
        """Initialize IBM watsonx.ai LLM."""
        if not IBM_SDK_AVAILABLE:
            print("⚠️  IBM watsonx.ai SDK not available")
            return False
        
        try:
            api_key = os.getenv("WATSONX_API_KEY")
            project_id = os.getenv("WATSONX_PROJECT_ID")
            url = os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com")
            
            if not api_key or not project_id:
                print("⚠️  WATSONX_API_KEY or WATSONX_PROJECT_ID not set")
                return False
            
            credentials = Credentials(
                url=url,
                api_key=api_key
            )
            
            # Parameters for generation
            parameters = {
                GenParams.DECODING_METHOD: "greedy",
                GenParams.MAX_NEW_TOKENS: 1000,
                GenParams.TEMPERATURE: 0.2,
                GenParams.TOP_K: 50,
                GenParams.TOP_P: 0.95,
            }
            
            model_id = os.getenv("WATSONX_MODEL_ID", "ibm/granite-3-8b-instruct")
            
            self.model = Model(
                model_id=model_id,
                params=parameters,
                credentials=credentials,
                project_id=project_id
            )
            
            self.model_available = True
            print(f"✅ RAG LLM initialized: {model_id}")
            return True
            
        except Exception as e:
            print(f"⚠️  Failed to initialize LLM: {e}")
            return False
    
    def ask(
        self,
        question: str,
        k: int = 10,
        source: Optional[str] = None,
        team_id: Optional[str] = None,
        hours_back: Optional[int] = None,
        include_sources: bool = True
    ) -> Dict[str, Any]:
        """
        Answer a question using RAG.
        
        Args:
            question: The user's question
            k: Number of relevant events to retrieve
            source: Filter by source (slack, jira, github, calendar)
            team_id: Filter by team ID
            hours_back: Filter to events within last N hours
            include_sources: Whether to include source events in response
            
        Returns:
            Dictionary with answer, sources, and metadata
        """
        start_time = datetime.utcnow()
        
        # Step 1: Retrieve relevant events
        retrieved_events = self.vector_store.search(
            query=question,
            k=k,
            source=source,
            team_id=team_id,
            hours_back=hours_back
        )
        
        # Step 2: Build context from retrieved events
        context = self._build_context(retrieved_events)
        
        # Step 3: Generate answer
        if self.model_available:
            answer = self._generate_answer(question, context, retrieved_events)
        else:
            answer = self._generate_fallback_answer(question, retrieved_events)
        
        # Calculate latency
        latency_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        # Build response
        response = {
            "question": question,
            "answer": answer,
            "retrieved_count": len(retrieved_events),
            "latency_ms": round(latency_ms, 2),
            "model": os.getenv("WATSONX_MODEL_ID", "ibm/granite-3-8b-instruct") if self.model_available else "fallback",
            "filters": {
                "source": source,
                "team_id": team_id,
                "hours_back": hours_back
            }
        }
        
        # Include sources if requested
        if include_sources:
            response["sources"] = [
                {
                    "id": e["id"],
                    "text": e["text"][:200] + "..." if len(e.get("text", "")) > 200 else e.get("text", ""),
                    "source": e["metadata"].get("source"),
                    "type": e["metadata"].get("type"),
                    "similarity": round(e.get("similarity", 0), 3) if e.get("similarity") else None
                }
                for e in retrieved_events[:5]  # Limit to top 5 sources
            ]
        
        return response
    
    def _build_context(self, events: List[Dict[str, Any]]) -> str:
        """
        Build context string from retrieved events.
        
        Formats events in a way that's easy for the LLM to understand.
        """
        if not events:
            return "No relevant events found in the project history."
        
        context_parts = []
        for i, event in enumerate(events, 1):
            metadata = event.get("metadata", {})
            text = event.get("text", "")
            similarity = event.get("similarity", 0)
            
            # Format each event
            event_str = f"""Event {i} (Relevance: {similarity:.1%}):
- Source: {metadata.get('source', 'unknown')}
- Type: {metadata.get('type', 'unknown')}
- Time: {metadata.get('timestamp', 'unknown')}
- Content: {text}"""
            
            context_parts.append(event_str)
        
        return "\n\n".join(context_parts)
    
    def _generate_answer(
        self,
        question: str,
        context: str,
        events: List[Dict[str, Any]]
    ) -> str:
        """Generate answer using IBM watsonx.ai with RAG context."""
        
        # Build prompt with context
        prompt = f"""You are FlowSentinel, an AI assistant that helps teams understand their software development projects.

You have access to the following project events and data:

{context}

Based on this context, please answer the following question. Be specific and reference the actual events when possible. If the context doesn't contain enough information to answer the question, say so honestly.

Question: {question}

Answer:"""
        
        try:
            response = self.model.generate_text(prompt=prompt)
            return response.strip()
        except Exception as e:
            print(f"⚠️  LLM generation error: {e}")
            return self._generate_fallback_answer(question, events)
    
    def _generate_fallback_answer(
        self,
        question: str,
        events: List[Dict[str, Any]]
    ) -> str:
        """Generate a basic answer when LLM is not available."""
        if not events:
            return "I couldn't find any relevant events in the project history to answer your question."
        
        # Build a basic response from the events
        answer_parts = [f"Based on {len(events)} relevant events I found:"]
        
        for i, event in enumerate(events[:3], 1):
            metadata = event.get("metadata", {})
            text = event.get("text", "")[:150]
            answer_parts.append(f"\n{i}. [{metadata.get('source', 'unknown')}] {text}...")
        
        answer_parts.append("\n\nNote: Full AI analysis requires IBM watsonx.ai configuration.")
        
        return "\n".join(answer_parts)
    
    def get_relevant_context(
        self,
        query: str,
        k: int = 5,
        **filters
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Get relevant context for external use (e.g., other AI features).
        
        Args:
            query: Search query
            k: Number of events to retrieve
            **filters: Additional filters (source, team_id, hours_back)
            
        Returns:
            Tuple of (context_string, list_of_events)
        """
        events = self.vector_store.search(query=query, k=k, **filters)
        context = self._build_context(events)
        return context, events
    
    def get_status(self) -> Dict[str, Any]:
        """Get RAG pipeline status."""
        vector_stats = self.vector_store.get_stats()
        
        return {
            "llm_available": self.model_available,
            "llm_model": os.getenv("WATSONX_MODEL_ID", "ibm/granite-3-8b-instruct") if self.model_available else None,
            "vector_store": vector_stats,
            "ready": self.model_available and vector_stats["total_documents"] > 0
        }


# Singleton instance
_rag_pipeline: Optional[RAGPipeline] = None


def get_rag_pipeline() -> RAGPipeline:
    """Get or create the RAG pipeline singleton."""
    global _rag_pipeline
    if _rag_pipeline is None:
        _rag_pipeline = RAGPipeline()
    return _rag_pipeline

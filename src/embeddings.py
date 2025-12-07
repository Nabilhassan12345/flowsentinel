"""
FlowSentinel Embeddings Service

Generates embeddings for events using IBM watsonx.ai or sentence-transformers fallback.
This is the foundation for RAG (Retrieval Augmented Generation) and semantic search.

AI Engineering Skills Demonstrated:
- Embedding generation with multiple providers
- Graceful fallback handling
- Batch processing for efficiency
- Text preprocessing for better embeddings
"""

import os
import json
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from dotenv import load_dotenv

load_dotenv()

# Try IBM watsonx.ai first
try:
    from ibm_watsonx_ai.foundation_models import Embeddings
    from ibm_watsonx_ai import Credentials
    IBM_EMBEDDINGS_AVAILABLE = True
except ImportError:
    IBM_EMBEDDINGS_AVAILABLE = False
    print("⚠️  IBM watsonx.ai embeddings not available")

# Fallback to sentence-transformers
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    print("⚠️  sentence-transformers not available")


class EmbeddingService:
    """
    Service for generating text embeddings.
    
    Supports:
    - IBM watsonx.ai embeddings (primary)
    - sentence-transformers (fallback)
    
    Usage:
        service = EmbeddingService()
        embeddings = service.embed_texts(["text1", "text2"])
    """
    
    def __init__(self):
        """Initialize the embedding service with available provider."""
        self.provider = None
        self.model = None
        self.embedding_dim = 384  # Default dimension
        
        # Try IBM watsonx.ai first
        if IBM_EMBEDDINGS_AVAILABLE and self._init_watsonx():
            self.provider = "watsonx"
            print("✅ Using IBM watsonx.ai for embeddings")
        # Fallback to sentence-transformers
        elif SENTENCE_TRANSFORMERS_AVAILABLE:
            self._init_sentence_transformers()
            self.provider = "sentence-transformers"
            print("✅ Using sentence-transformers for embeddings")
        else:
            print("❌ No embedding provider available!")
            raise RuntimeError("No embedding provider available. Install sentence-transformers or configure IBM watsonx.ai")
    
    def _init_watsonx(self) -> bool:
        """Initialize IBM watsonx.ai embeddings."""
        try:
            api_key = os.getenv("WATSONX_API_KEY")
            project_id = os.getenv("WATSONX_PROJECT_ID")
            url = os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com")
            
            if not api_key or not project_id:
                return False
            
            credentials = Credentials(
                url=url,
                api_key=api_key
            )
            
            # Use IBM's embedding model
            embedding_model_id = os.getenv("WATSONX_EMBEDDING_MODEL", "ibm/slate-125m-english-rtrvr")
            
            self.model = Embeddings(
                model_id=embedding_model_id,
                credentials=credentials,
                project_id=project_id
            )
            
            self.embedding_dim = 768  # IBM embedding dimension
            return True
            
        except Exception as e:
            print(f"⚠️  Failed to initialize watsonx embeddings: {e}")
            return False
    
    def _init_sentence_transformers(self):
        """Initialize sentence-transformers as fallback."""
        # Use a lightweight, efficient model
        model_name = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
        self.model = SentenceTransformer(model_name)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors (list of floats)
        """
        if not texts:
            return []
        
        # Preprocess texts
        processed_texts = [self._preprocess_text(t) for t in texts]
        
        if self.provider == "watsonx":
            return self._embed_watsonx(processed_texts)
        else:
            return self._embed_sentence_transformers(processed_texts)
    
    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text string to embed
            
        Returns:
            Embedding vector (list of floats)
        """
        embeddings = self.embed_texts([text])
        return embeddings[0] if embeddings else []
    
    def _embed_watsonx(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using IBM watsonx.ai."""
        try:
            result = self.model.embed_documents(texts)
            return result
        except Exception as e:
            print(f"⚠️  watsonx embedding error: {e}")
            # Fallback to sentence-transformers if available
            if SENTENCE_TRANSFORMERS_AVAILABLE:
                print("   Falling back to sentence-transformers...")
                self._init_sentence_transformers()
                self.provider = "sentence-transformers"
                return self._embed_sentence_transformers(texts)
            raise
    
    def _embed_sentence_transformers(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using sentence-transformers."""
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()
    
    def _preprocess_text(self, text: str) -> str:
        """
        Preprocess text for better embeddings.
        
        - Truncate to reasonable length
        - Clean up whitespace
        - Handle None/empty values
        """
        if not text:
            return ""
        
        # Convert to string if needed
        text = str(text)
        
        # Clean whitespace
        text = " ".join(text.split())
        
        # Truncate to ~500 words (embeddings have limits)
        words = text.split()
        if len(words) > 500:
            text = " ".join(words[:500])
        
        return text
    
    def event_to_text(self, event: Dict[str, Any]) -> str:
        """
        Convert an event to text for embedding.
        
        Creates a rich text representation that captures:
        - Source and type
        - Timestamp context
        - Key data fields
        
        Args:
            event: Event dictionary with source, type, timestamp, data
            
        Returns:
            Text representation of the event
        """
        source = event.get("source", "unknown")
        event_type = event.get("type", "unknown")
        timestamp = event.get("timestamp", "")
        data = event.get("data", {})
        
        # Build text representation
        parts = [
            f"Source: {source}",
            f"Type: {event_type}",
        ]
        
        # Add timestamp if available
        if timestamp:
            if isinstance(timestamp, datetime):
                parts.append(f"Time: {timestamp.strftime('%Y-%m-%d %H:%M')}")
            else:
                parts.append(f"Time: {timestamp}")
        
        # Extract key fields from data
        if isinstance(data, dict):
            # Priority fields for different sources
            priority_fields = {
                "slack": ["text", "message", "channel", "user"],
                "jira": ["summary", "description", "status", "priority", "assignee"],
                "github": ["title", "body", "state", "author", "action"],
                "calendar": ["title", "description", "attendees", "location"],
            }
            
            fields_to_extract = priority_fields.get(source, list(data.keys())[:5])
            
            for field in fields_to_extract:
                if field in data and data[field]:
                    value = data[field]
                    if isinstance(value, (list, dict)):
                        value = json.dumps(value)[:200]
                    parts.append(f"{field.title()}: {value}")
        elif data:
            parts.append(f"Data: {str(data)[:500]}")
        
        return " | ".join(parts)
    
    def get_status(self) -> Dict[str, Any]:
        """Get embedding service status."""
        return {
            "provider": self.provider,
            "embedding_dimension": self.embedding_dim,
            "model": str(self.model) if self.model else None,
            "available": self.model is not None
        }


# Singleton instance
_embedding_service: Optional[EmbeddingService] = None


def get_embedding_service() -> EmbeddingService:
    """Get or create the embedding service singleton."""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service


def generate_event_id(event: Dict[str, Any]) -> str:
    """Generate a stable ID for an event based on its content."""
    content = json.dumps(event, sort_keys=True, default=str)
    return hashlib.md5(content.encode()).hexdigest()

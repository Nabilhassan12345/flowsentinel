"""
Security Middleware for FlowSentinel
=====================================
FastAPI middleware for authentication, rate limiting, and security headers.

Features:
- JWT authentication middleware
- Rate limiting middleware
- Security headers (CORS, CSP, etc.)
- Request/Response logging
- Input sanitization
"""

import logging
import time
from typing import Optional, Callable
from datetime import datetime
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from fastapi import FastAPI

from security import get_security_manager, SecurityConfig

logger = logging.getLogger(__name__)


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """
    Middleware for JWT authentication.
    Validates tokens and attaches user info to request state.
    """
    
    # Paths that don't require authentication
    PUBLIC_PATHS = {
        "/",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/health",
        "/health/live",
        "/health/ready",
        "/auth/login",
        "/auth/register",
        "/auth/refresh",
        "/events/add",  # Webhook receiver
    }
    
    # Path prefixes that don't require auth
    PUBLIC_PREFIXES = [
        "/static/",
        "/assets/",
    ]
    
    async def dispatch(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        """Process the request through authentication."""
        path = request.url.path
        
        # Check if path is public
        if self._is_public_path(path):
            return await call_next(request)
        
        # Get authentication credentials
        auth_header = request.headers.get("Authorization", "")
        api_key = request.headers.get("X-API-Key", "")
        
        token = None
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
        
        # Validate credentials
        security = get_security_manager()
        ip_address = self._get_client_ip(request)
        
        valid, error, context = await security.validate_request(
            token=token,
            api_key=api_key,
            ip_address=ip_address
        )
        
        if not valid:
            return JSONResponse(
                status_code=401,
                content={
                    "error": "Unauthorized",
                    "message": error,
                    "timestamp": datetime.utcnow().isoformat()
                },
                headers=self._get_rate_limit_headers(context)
            )
        
        # Attach user info to request state
        request.state.user = context.get("user")
        request.state.api_key = context.get("api_key")
        request.state.rate_limit = context.get("rate_limit")
        
        # Continue processing
        response = await call_next(request)
        
        # Add rate limit headers
        rate_info = context.get("rate_limit", {})
        response.headers["X-RateLimit-Limit"] = str(rate_info.get("limit", 100))
        response.headers["X-RateLimit-Remaining"] = str(rate_info.get("remaining", 100))
        response.headers["X-RateLimit-Reset"] = str(rate_info.get("reset", 0))
        
        return response
    
    def _is_public_path(self, path: str) -> bool:
        """Check if a path is public (no auth required)."""
        if path in self.PUBLIC_PATHS:
            return True
        
        for prefix in self.PUBLIC_PREFIXES:
            if path.startswith(prefix):
                return True
        
        return False
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address."""
        # Check X-Forwarded-For header (for proxies)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        
        # Check X-Real-IP header
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fall back to client host
        if request.client:
            return request.client.host
        
        return "unknown"
    
    def _get_rate_limit_headers(
        self,
        context: Optional[dict]
    ) -> dict:
        """Get rate limit response headers."""
        if not context or "rate_limit" not in context:
            return {}
        
        rate_info = context["rate_limit"]
        return {
            "X-RateLimit-Limit": str(rate_info.get("limit", 100)),
            "X-RateLimit-Remaining": str(rate_info.get("remaining", 0)),
            "X-RateLimit-Reset": str(rate_info.get("reset", 0)),
            "Retry-After": str(rate_info.get("retry_after", 60))
        }


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware for rate limiting requests.
    Uses token bucket algorithm for fair rate limiting.
    """
    
    async def dispatch(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        """Check rate limits before processing."""
        security = get_security_manager()
        
        # Get identifier (user ID, API key, or IP)
        identifier = self._get_identifier(request)
        
        # Check rate limit
        allowed, rate_info = await security.rate_limiter.is_allowed(identifier)
        
        if not allowed:
            logger.warning(f"Rate limit exceeded for {identifier}")
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Too Many Requests",
                    "message": "Rate limit exceeded. Please slow down.",
                    "retry_after": rate_info.get("retry_after", 60),
                    "timestamp": datetime.utcnow().isoformat()
                },
                headers={
                    "X-RateLimit-Limit": str(rate_info.get("limit", 100)),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(rate_info.get("reset", 0)),
                    "Retry-After": str(rate_info.get("retry_after", 60))
                }
            )
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(rate_info.get("limit", 100))
        response.headers["X-RateLimit-Remaining"] = str(rate_info.get("remaining", 100))
        response.headers["X-RateLimit-Reset"] = str(rate_info.get("reset", 0))
        
        return response
    
    def _get_identifier(self, request: Request) -> str:
        """Get rate limit identifier from request."""
        # Prefer user ID if authenticated
        if hasattr(request.state, 'user') and request.state.user:
            return f"user:{request.state.user.get('id', 'unknown')}"
        
        # Prefer API key if provided
        if hasattr(request.state, 'api_key') and request.state.api_key:
            return f"key:{request.state.api_key.get('id', 'unknown')}"
        
        # Fall back to IP address
        if request.client:
            return f"ip:{request.client.host}"
        
        return "unknown"


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add security headers to all responses.
    """
    
    SECURITY_HEADERS = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Permissions-Policy": "geolocation=(), microphone=(), camera=()"
    }
    
    async def dispatch(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        """Add security headers to response."""
        response = await call_next(request)
        
        for header, value in self.SECURITY_HEADERS.items():
            response.headers[header] = value
        
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for request/response logging.
    Useful for debugging and audit trails.
    """
    
    async def dispatch(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        """Log request and response details."""
        start_time = time.time()
        
        # Log request
        logger.info(
            f"Request: {request.method} {request.url.path} "
            f"from {request.client.host if request.client else 'unknown'}"
        )
        
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Log response
        logger.info(
            f"Response: {request.method} {request.url.path} "
            f"status={response.status_code} duration={duration:.3f}s"
        )
        
        # Add timing header
        response.headers["X-Response-Time"] = f"{duration:.3f}s"
        
        return response


class InputSanitizationMiddleware(BaseHTTPMiddleware):
    """
    Middleware to sanitize potentially dangerous input.
    """
    
    DANGEROUS_PATTERNS = [
        "<script",
        "javascript:",
        "onerror=",
        "onclick=",
        "../",
        "..\\",
    ]
    
    async def dispatch(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        """Check for dangerous input patterns."""
        # Check query parameters
        query_string = str(request.url.query)
        for pattern in self.DANGEROUS_PATTERNS:
            if pattern.lower() in query_string.lower():
                logger.warning(
                    f"Blocked potentially dangerous request: "
                    f"{request.method} {request.url.path} - pattern: {pattern}"
                )
                return JSONResponse(
                    status_code=400,
                    content={
                        "error": "Bad Request",
                        "message": "Request contains potentially dangerous content",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                )
        
        return await call_next(request)


def setup_security_middleware(app: FastAPI) -> None:
    """
    Set up all security middleware for a FastAPI application.
    
    Usage:
        app = FastAPI()
        setup_security_middleware(app)
    """
    # Order matters! Add in reverse order of execution
    
    # 1. Request logging (first to execute, last to respond)
    app.add_middleware(RequestLoggingMiddleware)
    
    # 2. Security headers
    app.add_middleware(SecurityHeadersMiddleware)
    
    # 3. Input sanitization
    app.add_middleware(InputSanitizationMiddleware)
    
    # 4. Rate limiting
    # Note: Uncomment in production after testing
    # app.add_middleware(RateLimitMiddleware)
    
    # 5. Authentication
    # Note: Uncomment in production after testing
    # app.add_middleware(AuthenticationMiddleware)
    
    logger.info("Security middleware configured")


def setup_cors(app: FastAPI, origins: list = None) -> None:
    """
    Set up CORS middleware.
    
    Usage:
        setup_cors(app, origins=["https://flowsentinel.netlify.app"])
    """
    from starlette.middleware.cors import CORSMiddleware
    
    allowed_origins = origins or ["*"]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=[
            "X-RateLimit-Limit",
            "X-RateLimit-Remaining",
            "X-RateLimit-Reset",
            "X-Response-Time"
        ]
    )
    
    logger.info(f"CORS configured for origins: {allowed_origins}")

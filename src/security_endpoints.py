"""
Security API Endpoints for FlowSentinel
========================================
REST API for authentication and user management.

Endpoints:
- POST /auth/register - Register new user
- POST /auth/login - Login and get tokens
- POST /auth/refresh - Refresh access token
- POST /auth/logout - Logout and revoke tokens
- GET /auth/me - Get current user info
- POST /auth/api-key - Generate API key
- DELETE /auth/api-key/{key_id} - Revoke API key
- GET /auth/audit - Get audit log
"""

import logging
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel, Field, EmailStr

from security import (
    get_security_manager,
    UserRole,
    User
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["Authentication"])


# ============================================================================
# Request/Response Models
# ============================================================================

class RegisterRequest(BaseModel):
    """Request to register a new user."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="Password (min 8 chars)")
    name: Optional[str] = Field(None, description="User's display name")


class RegisterResponse(BaseModel):
    """Response after registration."""
    user_id: str
    email: str
    message: str
    created_at: str


class LoginRequest(BaseModel):
    """Request to login."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class LoginResponse(BaseModel):
    """Response with authentication tokens."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 1800  # 30 minutes


class RefreshRequest(BaseModel):
    """Request to refresh access token."""
    refresh_token: str = Field(..., description="Valid refresh token")


class RefreshResponse(BaseModel):
    """Response with new access token."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 1800


class GenerateAPIKeyRequest(BaseModel):
    """Request to generate an API key."""
    name: str = Field(..., description="Name for this API key")
    scopes: List[str] = Field(default=["read"], description="API key scopes")
    expires_in_days: Optional[int] = Field(None, description="Expiration in days")


class GenerateAPIKeyResponse(BaseModel):
    """Response with generated API key."""
    key_id: str
    api_key: str  # Only shown once!
    name: str
    scopes: List[str]
    expires_at: Optional[str]
    message: str


class UserResponse(BaseModel):
    """User information response."""
    id: str
    email: str
    role: str
    created_at: str
    last_login: Optional[str]
    is_active: bool


# ============================================================================
# Helper Functions
# ============================================================================

async def get_current_user(
    authorization: Optional[str] = Header(None)
) -> Optional[dict]:
    """Dependency to get current user from token."""
    if not authorization or not authorization.startswith("Bearer "):
        return None
    
    token = authorization[7:]
    security = get_security_manager()
    payload = security.jwt.verify_token(token)
    
    if not payload:
        return None
    
    return {
        "user_id": payload.user_id,
        "email": payload.email,
        "role": payload.role
    }


# ============================================================================
# Endpoints
# ============================================================================

@router.post("/register", response_model=RegisterResponse)
async def register(request: RegisterRequest):
    """
    Register a new user account.
    
    Password requirements:
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    
    Example:
        POST /auth/register
        {
            "email": "user@example.com",
            "password": "SecurePass123!"
        }
    """
    try:
        security = get_security_manager()
        
        success, error, user = await security.register_user(
            email=request.email,
            password=request.password,
            role=UserRole.USER
        )
        
        if not success:
            raise HTTPException(status_code=400, detail=error)
        
        return RegisterResponse(
            user_id=user.id,
            email=user.email,
            message="Registration successful. Please login.",
            created_at=user.created_at.isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    Login and receive authentication tokens.
    
    Returns:
    - access_token: Short-lived token for API access (30 min)
    - refresh_token: Long-lived token to get new access tokens (7 days)
    
    Example:
        POST /auth/login
        {
            "email": "user@example.com",
            "password": "SecurePass123!"
        }
    """
    try:
        security = get_security_manager()
        
        success, error, tokens = await security.authenticate(
            email=request.email,
            password=request.password
        )
        
        if not success:
            raise HTTPException(status_code=401, detail=error)
        
        return LoginResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type="bearer",
            expires_in=1800
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/refresh", response_model=RefreshResponse)
async def refresh_token(request: RefreshRequest):
    """
    Refresh access token using refresh token.
    
    Use this when your access token expires to get a new one
    without requiring the user to login again.
    
    Example:
        POST /auth/refresh
        {
            "refresh_token": "your_refresh_token_here"
        }
    """
    try:
        security = get_security_manager()
        
        # Verify refresh token
        payload = security.jwt.verify_token(request.refresh_token)
        
        if not payload:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        
        if payload.token_type != "refresh":
            raise HTTPException(status_code=401, detail="Not a refresh token")
        
        # Get user
        user = None
        for u in security._users.values():
            if u.id == payload.user_id:
                user = u
                break
        
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        # Generate new access token
        access_token = security.jwt.create_access_token(user)
        
        return RefreshResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=1800
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/logout")
async def logout(authorization: Optional[str] = Header(None)):
    """
    Logout and revoke the current token.
    
    After logout, the access token will no longer be valid.
    
    Example:
        POST /auth/logout
        Authorization: Bearer your_access_token
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="No token provided")
    
    token = authorization[7:]
    security = get_security_manager()
    
    success = security.jwt.revoke_token(token)
    
    return {
        "message": "Logged out successfully",
        "token_revoked": success,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    """
    Get current authenticated user's information.
    
    Requires valid access token in Authorization header.
    
    Example:
        GET /auth/me
        Authorization: Bearer your_access_token
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    security = get_security_manager()
    
    # Find user
    user = None
    for u in security._users.values():
        if u.id == current_user["user_id"]:
            user = u
            break
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserResponse(
        id=user.id,
        email=user.email,
        role=user.role.value,
        created_at=user.created_at.isoformat(),
        last_login=user.last_login.isoformat() if user.last_login else None,
        is_active=user.is_active
    )


@router.post("/api-key", response_model=GenerateAPIKeyResponse)
async def generate_api_key(
    request: GenerateAPIKeyRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Generate a new API key for programmatic access.
    
    **Important:** The API key is only shown once! Store it securely.
    
    Example:
        POST /auth/api-key
        Authorization: Bearer your_access_token
        {
            "name": "My Integration",
            "scopes": ["read", "write"],
            "expires_in_days": 90
        }
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    security = get_security_manager()
    
    raw_key, api_key = security.api_keys.generate_api_key(
        user_id=current_user["user_id"],
        name=request.name,
        scopes=request.scopes,
        expires_in_days=request.expires_in_days
    )
    
    return GenerateAPIKeyResponse(
        key_id=api_key.key_id,
        api_key=raw_key,  # Only shown once!
        name=api_key.name,
        scopes=api_key.scopes,
        expires_at=api_key.expires_at.isoformat() if api_key.expires_at else None,
        message="Store this API key securely - it won't be shown again!"
    )


@router.delete("/api-key/{key_id}")
async def revoke_api_key(
    key_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Revoke an API key.
    
    Example:
        DELETE /auth/api-key/abc123
        Authorization: Bearer your_access_token
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    security = get_security_manager()
    success = security.api_keys.revoke_api_key(key_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="API key not found")
    
    return {
        "key_id": key_id,
        "revoked": True,
        "revoked_at": datetime.utcnow().isoformat()
    }


@router.get("/audit")
async def get_audit_log(
    current_user: dict = Depends(get_current_user),
    limit: int = 100
):
    """
    Get security audit log.
    
    Admin users can see all logs, regular users only see their own.
    
    Example:
        GET /auth/audit?limit=50
        Authorization: Bearer your_access_token
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    security = get_security_manager()
    
    # Filter by user if not admin
    user_id = None
    if current_user["role"] != "admin":
        user_id = current_user["user_id"]
    
    logs = security.get_audit_log(user_id=user_id, limit=limit)
    
    return {
        "audit_logs": logs,
        "total": len(logs),
        "retrieved_at": datetime.utcnow().isoformat()
    }


@router.get("/status")
async def auth_status():
    """
    Get authentication system status.
    
    Example:
        GET /auth/status
    """
    security = get_security_manager()
    
    return {
        "status": "healthy",
        "jwt": {
            "algorithm": security.config.JWT_ALGORITHM,
            "access_token_expiry_minutes": security.config.ACCESS_TOKEN_EXPIRE_MINUTES,
            "refresh_token_expiry_days": security.config.REFRESH_TOKEN_EXPIRE_DAYS
        },
        "rate_limiting": {
            "requests_per_window": security.config.RATE_LIMIT_REQUESTS,
            "window_seconds": security.config.RATE_LIMIT_WINDOW_SECONDS,
            "burst_allowance": security.config.RATE_LIMIT_BURST
        },
        "password_policy": {
            "min_length": security.config.PASSWORD_MIN_LENGTH,
            "require_uppercase": security.config.PASSWORD_REQUIRE_UPPERCASE,
            "require_lowercase": security.config.PASSWORD_REQUIRE_LOWERCASE,
            "require_digit": security.config.PASSWORD_REQUIRE_DIGIT,
            "require_special": security.config.PASSWORD_REQUIRE_SPECIAL
        },
        "registered_users": len(security._users),
        "active_api_keys": len(security.api_keys._keys),
        "checked_at": datetime.utcnow().isoformat()
    }

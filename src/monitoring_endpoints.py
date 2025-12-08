"""
Monitoring API Endpoints for FlowSentinel
==========================================
REST API for health checks, metrics, and system monitoring.

Endpoints:
- GET /health - Basic health check
- GET /health/live - Kubernetes liveness probe
- GET /health/ready - Kubernetes readiness probe
- GET /health/detailed - Detailed health with all checks
- GET /metrics - Prometheus metrics
- GET /metrics/json - JSON metrics
- GET /metrics/dashboard - Dashboard-friendly metrics
- GET /circuit-breakers - Circuit breaker status
"""

import logging
import os
import sys
import platform
from datetime import datetime
from typing import Optional, Dict, Any
from fastapi import APIRouter, Response
from fastapi.responses import PlainTextResponse

from reliability import (
    get_health_checker,
    get_metrics_collector,
    get_all_circuit_breaker_stats,
    HealthStatus
)

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Monitoring"])


# ============================================================================
# Health Check Endpoints
# ============================================================================

@router.get("/health")
async def health_check():
    """
    Basic health check endpoint.
    
    Returns 200 if the service is running.
    Used for simple health monitoring.
    
    Example:
        GET /health
        
    Response:
        {"status": "healthy", "timestamp": "..."}
    """
    return {
        "status": "healthy",
        "service": "flowsentinel",
        "version": os.getenv("VERSION", "2.0.0"),
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/health/live")
async def liveness_probe():
    """
    Kubernetes liveness probe.
    
    Returns 200 if the application process is alive.
    If this fails, Kubernetes will restart the container.
    
    Example:
        GET /health/live
    """
    checker = get_health_checker()
    result = await checker.liveness()
    
    return result


@router.get("/health/ready")
async def readiness_probe():
    """
    Kubernetes readiness probe.
    
    Returns 200 if the application is ready to serve traffic.
    If this fails, Kubernetes will stop sending traffic.
    
    Example:
        GET /health/ready
    """
    checker = get_health_checker()
    result = await checker.readiness()
    
    status_code = 200 if result["status"] == "ready" else 503
    
    return Response(
        content=str(result),
        status_code=status_code,
        media_type="application/json"
    )


@router.get("/health/detailed")
async def detailed_health():
    """
    Detailed health check with all registered checks.
    
    Runs all health checks and returns detailed status for each.
    
    Example:
        GET /health/detailed
        
    Response:
        {
            "status": "healthy",
            "checks": {
                "database": {"status": "healthy", ...},
                "redis": {"status": "healthy", ...}
            }
        }
    """
    checker = get_health_checker()
    result = await checker.check_all()
    
    # Add system info
    result["system"] = {
        "python_version": sys.version,
        "platform": platform.platform(),
        "pid": os.getpid()
    }
    
    # Determine status code
    if result["status"] == HealthStatus.UNHEALTHY.value:
        status_code = 503
    elif result["status"] == HealthStatus.DEGRADED.value:
        status_code = 200  # Still operational
    else:
        status_code = 200
    
    return result


# ============================================================================
# Metrics Endpoints
# ============================================================================

@router.get("/metrics", response_class=PlainTextResponse)
async def prometheus_metrics():
    """
    Prometheus-compatible metrics endpoint.
    
    Returns metrics in Prometheus text format for scraping.
    
    Example:
        GET /metrics
        
    Response:
        # HELP http_requests_total Total HTTP requests
        http_requests_total{method="GET"} 1234
        ...
    """
    collector = get_metrics_collector()
    metrics = await collector.get_metrics()
    
    return PlainTextResponse(
        content=metrics,
        media_type="text/plain; version=0.0.4"
    )


@router.get("/metrics/json")
async def json_metrics():
    """
    Metrics in JSON format.
    
    Alternative to Prometheus format for custom dashboards.
    
    Example:
        GET /metrics/json
    """
    collector = get_metrics_collector()
    metrics = await collector.get_json()
    
    return {
        "metrics": metrics,
        "collected_at": datetime.utcnow().isoformat()
    }


@router.get("/metrics/dashboard")
async def dashboard_metrics():
    """
    Dashboard-friendly metrics summary.
    
    Provides key metrics formatted for dashboard display.
    
    Example:
        GET /metrics/dashboard
    """
    collector = get_metrics_collector()
    metrics = await collector.get_json()
    
    # Calculate summary stats
    uptime_hours = metrics.get("uptime_seconds", 0) / 3600
    
    # Get request stats from counters
    total_requests = sum(
        v for k, v in metrics.get("counters", {}).items()
        if "request" in k.lower()
    )
    
    # Get error rate
    errors = sum(
        v for k, v in metrics.get("counters", {}).items()
        if "error" in k.lower()
    )
    error_rate = (errors / total_requests * 100) if total_requests > 0 else 0
    
    return {
        "summary": {
            "uptime_hours": round(uptime_hours, 2),
            "total_requests": total_requests,
            "error_rate_percent": round(error_rate, 2),
            "status": "operational"
        },
        "counters": metrics.get("counters", {}),
        "gauges": metrics.get("gauges", {}),
        "histograms": {
            k: {
                "avg_ms": round(v.get("avg", 0) * 1000, 2),
                "count": v.get("count", 0)
            }
            for k, v in metrics.get("histograms", {}).items()
        },
        "generated_at": datetime.utcnow().isoformat()
    }


# ============================================================================
# Circuit Breaker Endpoints
# ============================================================================

@router.get("/circuit-breakers")
async def get_circuit_breakers():
    """
    Get status of all circuit breakers.
    
    Circuit breakers protect against cascade failures from
    external service outages.
    
    Example:
        GET /circuit-breakers
    """
    stats = await get_all_circuit_breaker_stats()
    
    return {
        "circuit_breakers": stats,
        "total": len(stats),
        "open_count": sum(
            1 for s in stats.values()
            if s.get("state") == "open"
        ),
        "checked_at": datetime.utcnow().isoformat()
    }


@router.post("/circuit-breakers/{name}/reset")
async def reset_circuit_breaker(name: str):
    """
    Manually reset a circuit breaker.
    
    Use this to force a circuit breaker back to closed state
    after fixing an external service issue.
    
    Example:
        POST /circuit-breakers/external_api/reset
    """
    from reliability import get_circuit_breaker
    
    try:
        breaker = get_circuit_breaker(name)
        await breaker.reset()
        
        return {
            "name": name,
            "reset": True,
            "new_state": breaker.state.value,
            "reset_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "name": name,
            "reset": False,
            "error": str(e)
        }


# ============================================================================
# System Info Endpoints
# ============================================================================

@router.get("/system/info")
async def system_info():
    """
    Get system information.
    
    Returns details about the running environment.
    
    Example:
        GET /system/info
    """
    import psutil
    
    try:
        memory = psutil.virtual_memory()
        cpu_percent = psutil.cpu_percent(interval=0.1)
        disk = psutil.disk_usage('/')
        
        return {
            "system": {
                "platform": platform.platform(),
                "python_version": sys.version,
                "processor": platform.processor()
            },
            "process": {
                "pid": os.getpid(),
                "memory_mb": round(psutil.Process().memory_info().rss / 1024 / 1024, 2),
                "threads": psutil.Process().num_threads()
            },
            "resources": {
                "cpu_percent": cpu_percent,
                "memory_total_gb": round(memory.total / 1024 / 1024 / 1024, 2),
                "memory_used_percent": memory.percent,
                "disk_total_gb": round(disk.total / 1024 / 1024 / 1024, 2),
                "disk_used_percent": round(disk.used / disk.total * 100, 2)
            },
            "environment": os.getenv("ENVIRONMENT", "development"),
            "retrieved_at": datetime.utcnow().isoformat()
        }
    except ImportError:
        # psutil not installed
        return {
            "system": {
                "platform": platform.platform(),
                "python_version": sys.version
            },
            "process": {
                "pid": os.getpid()
            },
            "note": "Install psutil for detailed system metrics",
            "retrieved_at": datetime.utcnow().isoformat()
        }


@router.get("/system/config")
async def system_config():
    """
    Get system configuration (non-sensitive).
    
    Returns current configuration settings.
    
    Example:
        GET /system/config
    """
    return {
        "features": {
            "database": os.getenv("DATABASE_URL") is not None,
            "redis": os.getenv("REDIS_URL") is not None,
            "watsonx": os.getenv("WATSONX_API_KEY") is not None,
            "agent_enabled": os.getenv("AGENT_ENABLED", "true").lower() == "true"
        },
        "limits": {
            "rate_limit_requests": int(os.getenv("RATE_LIMIT_REQUESTS", "100")),
            "max_workers": int(os.getenv("MAX_WORKERS", "4")),
            "cache_ttl_seconds": int(os.getenv("CACHE_TTL", "3600"))
        },
        "version": os.getenv("VERSION", "2.0.0"),
        "environment": os.getenv("ENVIRONMENT", "development"),
        "retrieved_at": datetime.utcnow().isoformat()
    }

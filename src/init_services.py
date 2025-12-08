"""
FlowSentinel Service Initialization
====================================
Central initialization for all services on application startup.

This module handles:
- Database connection and table creation
- Memory system initialization
- Security system initialization
- Cache system initialization
- Worker pool initialization
- Health check registration
- Metrics collection setup

Usage:
    from init_services import initialize_all_services, shutdown_all_services
    
    @app.on_event("startup")
    async def startup():
        await initialize_all_services()
    
    @app.on_event("shutdown")
    async def shutdown():
        await shutdown_all_services()
"""

import logging
import os
import asyncio
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

# Global state tracking
_services_initialized = False
_initialization_errors: Dict[str, str] = {}


async def initialize_all_services() -> Dict[str, Any]:
    """
    Initialize all services for production deployment.
    
    Returns:
        Dict with status of each service initialization
    """
    global _services_initialized, _initialization_errors
    
    results = {
        "database": False,
        "memory": False,
        "security": False,
        "cache": False,
        "workers": False,
        "health_checks": False,
        "metrics": False,
        "started_at": datetime.utcnow().isoformat()
    }
    
    # 1. Initialize Database
    try:
        from database import init_db, test_connection
        init_db()
        if test_connection():
            results["database"] = True
            logger.info("✅ Database initialized")
        else:
            logger.warning("⚠️ Database connection test failed")
    except ImportError:
        logger.info("📝 Database module not available, using in-memory storage")
        results["database"] = "in-memory"
    except Exception as e:
        _initialization_errors["database"] = str(e)
        logger.error(f"❌ Database initialization failed: {e}")
    
    # 2. Initialize Memory System
    try:
        from memory import init_memory_manager
        init_memory_manager(short_term_max=50)
        results["memory"] = True
        logger.info("✅ Memory system initialized")
    except Exception as e:
        _initialization_errors["memory"] = str(e)
        logger.error(f"❌ Memory initialization failed: {e}")
    
    # 3. Initialize Security System
    try:
        from security import init_security_manager, SecurityConfig
        
        config = SecurityConfig()
        config.JWT_SECRET_KEY = os.getenv("SECRET_KEY", config.JWT_SECRET_KEY)
        config.RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
        
        init_security_manager(config)
        results["security"] = True
        logger.info("✅ Security system initialized")
    except Exception as e:
        _initialization_errors["security"] = str(e)
        logger.error(f"❌ Security initialization failed: {e}")
    
    # 4. Initialize Cache System
    try:
        from cache import init_cache_manager, CacheConfig
        
        config = CacheConfig()
        redis_url = os.getenv("REDIS_URL")
        if redis_url:
            config.REDIS_URL = redis_url
        
        use_redis = redis_url is not None
        await init_cache_manager(config, use_redis=use_redis)
        results["cache"] = "redis" if use_redis else "memory"
        logger.info(f"✅ Cache system initialized ({'Redis' if use_redis else 'In-memory'})")
    except Exception as e:
        _initialization_errors["cache"] = str(e)
        logger.error(f"❌ Cache initialization failed: {e}")
    
    # 5. Initialize Worker Pool
    try:
        from workers import init_workers
        
        num_workers = int(os.getenv("NUM_WORKERS", "4"))
        await init_workers(num_workers)
        results["workers"] = True
        logger.info(f"✅ Worker pool initialized ({num_workers} workers)")
    except Exception as e:
        _initialization_errors["workers"] = str(e)
        logger.error(f"❌ Worker initialization failed: {e}")
    
    # 6. Register Health Checks
    try:
        from reliability import get_health_checker, init_reliability
        
        await init_reliability()
        checker = get_health_checker()
        
        # Register database health check
        async def check_database():
            try:
                from database import test_connection
                return test_connection()
            except:
                return True  # Pass if no database
        
        checker.register("database", check_database, critical=True)
        
        # Register cache health check
        async def check_cache():
            try:
                from cache import get_cache_manager
                cache = get_cache_manager()
                await cache.set("health_check", "ok", ttl=10)
                result = await cache.get("health_check")
                return result == "ok"
            except:
                return False
        
        checker.register("cache", check_cache, critical=False)
        
        # Register memory health check
        async def check_memory():
            try:
                from memory import get_memory_manager
                manager = get_memory_manager()
                return manager is not None
            except:
                return False
        
        checker.register("memory", check_memory, critical=False)
        
        results["health_checks"] = True
        logger.info("✅ Health checks registered")
    except Exception as e:
        _initialization_errors["health_checks"] = str(e)
        logger.error(f"❌ Health check registration failed: {e}")
    
    # 7. Initialize Metrics Collection
    try:
        from reliability import get_metrics_collector
        
        metrics = get_metrics_collector()
        await metrics.increment("app_starts")
        await metrics.set_gauge("app_version", 2.0)
        
        results["metrics"] = True
        logger.info("✅ Metrics collection initialized")
    except Exception as e:
        _initialization_errors["metrics"] = str(e)
        logger.error(f"❌ Metrics initialization failed: {e}")
    
    _services_initialized = True
    results["all_initialized"] = all(
        v not in [False] for k, v in results.items() 
        if k not in ["started_at", "all_initialized"]
    )
    results["errors"] = _initialization_errors
    
    logger.info(f"🚀 Service initialization complete: {results['all_initialized']}")
    return results


async def shutdown_all_services() -> None:
    """
    Gracefully shutdown all services.
    """
    global _services_initialized
    
    logger.info("🛑 Shutting down services...")
    
    # 1. Stop workers
    try:
        from workers import shutdown_workers
        await shutdown_workers()
        logger.info("✅ Workers stopped")
    except Exception as e:
        logger.error(f"❌ Worker shutdown error: {e}")
    
    # 2. Flush cache
    try:
        from cache import get_cache_manager
        cache = get_cache_manager()
        stats = await cache.get_stats()
        logger.info(f"📊 Cache stats at shutdown: {stats}")
    except Exception as e:
        logger.error(f"❌ Cache shutdown error: {e}")
    
    # 3. Log final metrics
    try:
        from reliability import get_metrics_collector
        metrics = get_metrics_collector()
        await metrics.increment("app_shutdowns")
        final_metrics = await metrics.get_json()
        logger.info(f"📊 Final metrics: {final_metrics.get('uptime_seconds', 0):.0f}s uptime")
    except Exception as e:
        logger.error(f"❌ Metrics shutdown error: {e}")
    
    _services_initialized = False
    logger.info("✅ All services stopped")


def get_initialization_status() -> Dict[str, Any]:
    """Get the current initialization status."""
    return {
        "initialized": _services_initialized,
        "errors": _initialization_errors,
        "checked_at": datetime.utcnow().isoformat()
    }


async def health_check_all() -> Dict[str, Any]:
    """
    Comprehensive health check for all services.
    
    Returns:
        Dict with health status of each service
    """
    results = {
        "status": "healthy",
        "services": {},
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Check each service
    services_to_check = [
        ("database", _check_database),
        ("memory", _check_memory),
        ("security", _check_security),
        ("cache", _check_cache),
        ("workers", _check_workers),
    ]
    
    unhealthy_count = 0
    
    for name, check_func in services_to_check:
        try:
            status = await check_func()
            results["services"][name] = status
            if status.get("status") == "unhealthy":
                unhealthy_count += 1
        except Exception as e:
            results["services"][name] = {"status": "error", "error": str(e)}
            unhealthy_count += 1
    
    if unhealthy_count > 0:
        results["status"] = "degraded" if unhealthy_count < 3 else "unhealthy"
    
    return results


async def _check_database() -> Dict[str, Any]:
    """Check database health."""
    try:
        from database import test_connection
        ok = test_connection()
        return {"status": "healthy" if ok else "unhealthy", "type": "postgresql"}
    except ImportError:
        return {"status": "healthy", "type": "in-memory"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


async def _check_memory() -> Dict[str, Any]:
    """Check memory system health."""
    try:
        from memory import get_memory_manager
        manager = get_memory_manager()
        return {
            "status": "healthy",
            "conversations": len(manager.short_term._conversations),
            "long_term_users": len(manager.long_term._memory_cache)
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


async def _check_security() -> Dict[str, Any]:
    """Check security system health."""
    try:
        from security import get_security_manager
        manager = get_security_manager()
        return {
            "status": "healthy",
            "registered_users": len(manager._users),
            "active_api_keys": len(manager.api_keys._keys)
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


async def _check_cache() -> Dict[str, Any]:
    """Check cache health."""
    try:
        from cache import get_cache_manager
        cache = get_cache_manager()
        stats = await cache.get_stats()
        return {
            "status": "healthy",
            "type": stats.get("type", "unknown"),
            "hit_rate": stats.get("hit_rate", 0)
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


async def _check_workers() -> Dict[str, Any]:
    """Check worker pool health."""
    try:
        from workers import get_worker_pool
        pool = get_worker_pool()
        stats = pool.get_stats()
        return {
            "status": "healthy" if stats.get("running") else "stopped",
            "workers": stats.get("num_workers", 0),
            "queue_size": stats.get("queue_size", 0)
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

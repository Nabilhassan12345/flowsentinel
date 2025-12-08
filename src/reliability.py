"""
Reliability Module for FlowSentinel
====================================
Production-grade reliability with circuit breakers, health checks, and monitoring.

Features:
- Circuit breaker pattern for external services
- Health checks (liveness, readiness)
- Retry with exponential backoff
- Bulkhead pattern for isolation
- Timeout management
- Graceful degradation
- Metrics collection (Prometheus-compatible)

Architecture:
- CircuitBreaker: Prevents cascade failures
- HealthChecker: Service health monitoring
- RetryHandler: Smart retry logic
- Bulkhead: Resource isolation
- MetricsCollector: Prometheus metrics
"""

import logging
import asyncio
import time
from typing import Optional, Any, Dict, List, Callable, Awaitable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from functools import wraps
import traceback

logger = logging.getLogger(__name__)


# ============================================================================
# Circuit Breaker
# ============================================================================

class CircuitState(str, Enum):
    """Circuit breaker states."""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if service recovered


@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration."""
    failure_threshold: int = 5      # Failures before opening
    success_threshold: int = 3      # Successes to close from half-open
    timeout_seconds: float = 30.0   # Time before trying again (open -> half-open)
    half_open_max_calls: int = 3    # Max calls in half-open state


class CircuitBreaker:
    """
    Implements the circuit breaker pattern to prevent cascade failures.
    
    Usage:
        breaker = CircuitBreaker("external_api")
        
        @breaker
        async def call_external_api():
            return await http_client.get("...")
        
        # Or manual
        async with breaker:
            result = await call_api()
    """
    
    def __init__(
        self,
        name: str,
        config: CircuitBreakerConfig = None
    ):
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self.state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time: Optional[float] = None
        self._half_open_calls = 0
        self._lock = asyncio.Lock()
        self._stats = {
            "total_calls": 0,
            "successful_calls": 0,
            "failed_calls": 0,
            "rejected_calls": 0,
            "state_changes": []
        }
    
    async def __aenter__(self):
        """Context manager entry."""
        await self._before_call()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if exc_type is None:
            await self._on_success()
        else:
            await self._on_failure(exc_val)
        return False
    
    def __call__(self, func: Callable) -> Callable:
        """Decorator usage."""
        @wraps(func)
        async def wrapper(*args, **kwargs):
            async with self:
                return await func(*args, **kwargs)
        return wrapper
    
    async def _before_call(self) -> None:
        """Check if call is allowed."""
        async with self._lock:
            self._stats["total_calls"] += 1
            
            if self.state == CircuitState.OPEN:
                # Check if timeout has passed
                if self._last_failure_time:
                    elapsed = time.time() - self._last_failure_time
                    if elapsed >= self.config.timeout_seconds:
                        self._transition_to(CircuitState.HALF_OPEN)
                    else:
                        self._stats["rejected_calls"] += 1
                        raise CircuitBreakerOpen(
                            f"Circuit breaker '{self.name}' is OPEN. "
                            f"Retry in {self.config.timeout_seconds - elapsed:.1f}s"
                        )
                else:
                    self._stats["rejected_calls"] += 1
                    raise CircuitBreakerOpen(f"Circuit breaker '{self.name}' is OPEN")
            
            if self.state == CircuitState.HALF_OPEN:
                if self._half_open_calls >= self.config.half_open_max_calls:
                    self._stats["rejected_calls"] += 1
                    raise CircuitBreakerOpen(
                        f"Circuit breaker '{self.name}' is HALF_OPEN and at max test calls"
                    )
                self._half_open_calls += 1
    
    async def _on_success(self) -> None:
        """Handle successful call."""
        async with self._lock:
            self._stats["successful_calls"] += 1
            
            if self.state == CircuitState.HALF_OPEN:
                self._success_count += 1
                if self._success_count >= self.config.success_threshold:
                    self._transition_to(CircuitState.CLOSED)
            else:
                self._failure_count = 0
    
    async def _on_failure(self, error: Exception) -> None:
        """Handle failed call."""
        async with self._lock:
            self._stats["failed_calls"] += 1
            self._failure_count += 1
            self._last_failure_time = time.time()
            
            logger.warning(f"Circuit breaker '{self.name}' recorded failure: {error}")
            
            if self.state == CircuitState.HALF_OPEN:
                self._transition_to(CircuitState.OPEN)
            elif self._failure_count >= self.config.failure_threshold:
                self._transition_to(CircuitState.OPEN)
    
    def _transition_to(self, new_state: CircuitState) -> None:
        """Transition to a new state."""
        old_state = self.state
        self.state = new_state
        
        if new_state == CircuitState.CLOSED:
            self._failure_count = 0
            self._success_count = 0
            self._half_open_calls = 0
        elif new_state == CircuitState.HALF_OPEN:
            self._success_count = 0
            self._half_open_calls = 0
        
        self._stats["state_changes"].append({
            "from": old_state.value,
            "to": new_state.value,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        logger.info(f"Circuit breaker '{self.name}': {old_state.value} -> {new_state.value}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get circuit breaker statistics."""
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self._failure_count,
            "success_count": self._success_count,
            "config": {
                "failure_threshold": self.config.failure_threshold,
                "success_threshold": self.config.success_threshold,
                "timeout_seconds": self.config.timeout_seconds
            },
            **self._stats
        }
    
    async def reset(self) -> None:
        """Manually reset the circuit breaker."""
        async with self._lock:
            self._transition_to(CircuitState.CLOSED)
            logger.info(f"Circuit breaker '{self.name}' manually reset")


class CircuitBreakerOpen(Exception):
    """Exception raised when circuit breaker is open."""
    pass


# ============================================================================
# Health Checker
# ============================================================================

class HealthStatus(str, Enum):
    """Health check status."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@dataclass
class HealthCheck:
    """A health check definition."""
    name: str
    check_func: Callable[[], Awaitable[bool]]
    critical: bool = True  # If false, won't affect overall health
    timeout_seconds: float = 5.0
    last_check: Optional[datetime] = None
    last_status: HealthStatus = HealthStatus.HEALTHY
    last_error: Optional[str] = None
    consecutive_failures: int = 0


class HealthChecker:
    """
    Manages health checks for all services and dependencies.
    
    Usage:
        checker = HealthChecker()
        
        checker.register("database", check_database, critical=True)
        checker.register("redis", check_redis, critical=False)
        
        health = await checker.check_all()
    """
    
    def __init__(self):
        self._checks: Dict[str, HealthCheck] = {}
        self._lock = asyncio.Lock()
    
    def register(
        self,
        name: str,
        check_func: Callable[[], Awaitable[bool]],
        critical: bool = True,
        timeout_seconds: float = 5.0
    ) -> None:
        """Register a health check."""
        self._checks[name] = HealthCheck(
            name=name,
            check_func=check_func,
            critical=critical,
            timeout_seconds=timeout_seconds
        )
        logger.info(f"Registered health check: {name} (critical={critical})")
    
    def unregister(self, name: str) -> bool:
        """Unregister a health check."""
        if name in self._checks:
            del self._checks[name]
            return True
        return False
    
    async def check(self, name: str) -> Dict[str, Any]:
        """Run a single health check."""
        check = self._checks.get(name)
        if not check:
            return {"name": name, "status": "unknown", "error": "Check not found"}
        
        return await self._run_check(check)
    
    async def check_all(self) -> Dict[str, Any]:
        """Run all health checks."""
        results = {}
        overall_status = HealthStatus.HEALTHY
        
        # Run checks in parallel
        tasks = [
            self._run_check(check)
            for check in self._checks.values()
        ]
        
        check_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for check, result in zip(self._checks.values(), check_results):
            if isinstance(result, Exception):
                results[check.name] = {
                    "status": HealthStatus.UNHEALTHY.value,
                    "error": str(result)
                }
                if check.critical:
                    overall_status = HealthStatus.UNHEALTHY
            else:
                results[check.name] = result
                if result["status"] == HealthStatus.UNHEALTHY.value and check.critical:
                    overall_status = HealthStatus.UNHEALTHY
                elif result["status"] == HealthStatus.DEGRADED.value:
                    if overall_status == HealthStatus.HEALTHY:
                        overall_status = HealthStatus.DEGRADED
        
        return {
            "status": overall_status.value,
            "checks": results,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _run_check(self, check: HealthCheck) -> Dict[str, Any]:
        """Run a single health check with timeout."""
        check.last_check = datetime.utcnow()
        
        try:
            result = await asyncio.wait_for(
                check.check_func(),
                timeout=check.timeout_seconds
            )
            
            if result:
                check.last_status = HealthStatus.HEALTHY
                check.last_error = None
                check.consecutive_failures = 0
            else:
                check.last_status = HealthStatus.UNHEALTHY
                check.last_error = "Check returned False"
                check.consecutive_failures += 1
            
        except asyncio.TimeoutError:
            check.last_status = HealthStatus.UNHEALTHY
            check.last_error = f"Timeout after {check.timeout_seconds}s"
            check.consecutive_failures += 1
            
        except Exception as e:
            check.last_status = HealthStatus.UNHEALTHY
            check.last_error = str(e)
            check.consecutive_failures += 1
        
        return {
            "name": check.name,
            "status": check.last_status.value,
            "critical": check.critical,
            "last_check": check.last_check.isoformat(),
            "error": check.last_error,
            "consecutive_failures": check.consecutive_failures
        }
    
    async def liveness(self) -> Dict[str, Any]:
        """
        Liveness check - is the application running?
        Used by Kubernetes liveness probes.
        """
        return {
            "status": "alive",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def readiness(self) -> Dict[str, Any]:
        """
        Readiness check - is the application ready to serve traffic?
        Used by Kubernetes readiness probes.
        """
        health = await self.check_all()
        
        ready = health["status"] != HealthStatus.UNHEALTHY.value
        
        return {
            "status": "ready" if ready else "not_ready",
            "health": health["status"],
            "timestamp": datetime.utcnow().isoformat()
        }


# ============================================================================
# Retry Handler
# ============================================================================

class RetryHandler:
    """
    Smart retry logic with exponential backoff.
    
    Usage:
        retry = RetryHandler(max_retries=3)
        
        @retry
        async def flaky_operation():
            return await call_api()
        
        # Or manual
        result = await retry.execute(flaky_operation)
    """
    
    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        retryable_exceptions: tuple = (Exception,)
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.retryable_exceptions = retryable_exceptions
        self._stats = {
            "total_attempts": 0,
            "successful_attempts": 0,
            "failed_attempts": 0,
            "retries": 0
        }
    
    def __call__(self, func: Callable) -> Callable:
        """Decorator usage."""
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await self.execute(func, *args, **kwargs)
        return wrapper
    
    async def execute(
        self,
        func: Callable[..., Awaitable[Any]],
        *args,
        **kwargs
    ) -> Any:
        """Execute function with retries."""
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            self._stats["total_attempts"] += 1
            
            try:
                result = await func(*args, **kwargs)
                self._stats["successful_attempts"] += 1
                return result
                
            except self.retryable_exceptions as e:
                last_exception = e
                self._stats["failed_attempts"] += 1
                
                if attempt < self.max_retries:
                    delay = self._calculate_delay(attempt)
                    self._stats["retries"] += 1
                    
                    logger.warning(
                        f"Retry {attempt + 1}/{self.max_retries} for {func.__name__} "
                        f"after {delay:.2f}s: {e}"
                    )
                    
                    await asyncio.sleep(delay)
                else:
                    logger.error(
                        f"All {self.max_retries} retries exhausted for {func.__name__}: {e}"
                    )
        
        raise last_exception
    
    def _calculate_delay(self, attempt: int) -> float:
        """Calculate delay with exponential backoff and jitter."""
        import random
        
        delay = self.base_delay * (self.exponential_base ** attempt)
        delay = min(delay, self.max_delay)
        
        # Add jitter (±25%)
        jitter = delay * 0.25 * (2 * random.random() - 1)
        delay += jitter
        
        return max(0, delay)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get retry statistics."""
        return self._stats


# ============================================================================
# Bulkhead (Resource Isolation)
# ============================================================================

class Bulkhead:
    """
    Implements the bulkhead pattern for resource isolation.
    Limits concurrent executions to prevent resource exhaustion.
    
    Usage:
        bulkhead = Bulkhead("api_calls", max_concurrent=10)
        
        @bulkhead
        async def call_api():
            return await http_client.get("...")
    """
    
    def __init__(
        self,
        name: str,
        max_concurrent: int = 10,
        max_waiting: int = 100,
        timeout_seconds: float = 30.0
    ):
        self.name = name
        self.max_concurrent = max_concurrent
        self.max_waiting = max_waiting
        self.timeout_seconds = timeout_seconds
        self._semaphore = asyncio.Semaphore(max_concurrent)
        self._waiting = 0
        self._active = 0
        self._lock = asyncio.Lock()
        self._stats = {
            "total_calls": 0,
            "rejected_calls": 0,
            "timeout_calls": 0,
            "successful_calls": 0
        }
    
    async def __aenter__(self):
        """Context manager entry."""
        await self._acquire()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        await self._release()
        if exc_type is None:
            self._stats["successful_calls"] += 1
        return False
    
    def __call__(self, func: Callable) -> Callable:
        """Decorator usage."""
        @wraps(func)
        async def wrapper(*args, **kwargs):
            async with self:
                return await func(*args, **kwargs)
        return wrapper
    
    async def _acquire(self) -> None:
        """Acquire a slot in the bulkhead."""
        async with self._lock:
            self._stats["total_calls"] += 1
            
            if self._waiting >= self.max_waiting:
                self._stats["rejected_calls"] += 1
                raise BulkheadFull(
                    f"Bulkhead '{self.name}' is full "
                    f"(waiting: {self._waiting}/{self.max_waiting})"
                )
            
            self._waiting += 1
        
        try:
            await asyncio.wait_for(
                self._semaphore.acquire(),
                timeout=self.timeout_seconds
            )
        except asyncio.TimeoutError:
            async with self._lock:
                self._waiting -= 1
                self._stats["timeout_calls"] += 1
            raise BulkheadTimeout(
                f"Timeout waiting for bulkhead '{self.name}' slot"
            )
        
        async with self._lock:
            self._waiting -= 1
            self._active += 1
    
    async def _release(self) -> None:
        """Release a slot in the bulkhead."""
        self._semaphore.release()
        async with self._lock:
            self._active -= 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get bulkhead statistics."""
        return {
            "name": self.name,
            "max_concurrent": self.max_concurrent,
            "max_waiting": self.max_waiting,
            "active": self._active,
            "waiting": self._waiting,
            "available": self.max_concurrent - self._active,
            **self._stats
        }


class BulkheadFull(Exception):
    """Exception raised when bulkhead waiting queue is full."""
    pass


class BulkheadTimeout(Exception):
    """Exception raised when waiting for bulkhead slot times out."""
    pass


# ============================================================================
# Metrics Collector (Prometheus-compatible)
# ============================================================================

class MetricsCollector:
    """
    Collects metrics for monitoring and alerting.
    Prometheus-compatible format.
    """
    
    def __init__(self):
        self._counters: Dict[str, int] = {}
        self._gauges: Dict[str, float] = {}
        self._histograms: Dict[str, List[float]] = {}
        self._lock = asyncio.Lock()
        self._start_time = time.time()
    
    async def increment(self, name: str, value: int = 1, labels: Dict[str, str] = None) -> None:
        """Increment a counter."""
        key = self._make_key(name, labels)
        async with self._lock:
            self._counters[key] = self._counters.get(key, 0) + value
    
    async def set_gauge(self, name: str, value: float, labels: Dict[str, str] = None) -> None:
        """Set a gauge value."""
        key = self._make_key(name, labels)
        async with self._lock:
            self._gauges[key] = value
    
    async def observe(self, name: str, value: float, labels: Dict[str, str] = None) -> None:
        """Record a histogram observation."""
        key = self._make_key(name, labels)
        async with self._lock:
            if key not in self._histograms:
                self._histograms[key] = []
            self._histograms[key].append(value)
            # Keep last 1000 observations
            if len(self._histograms[key]) > 1000:
                self._histograms[key] = self._histograms[key][-1000:]
    
    def _make_key(self, name: str, labels: Dict[str, str] = None) -> str:
        """Create a metric key with labels."""
        if not labels:
            return name
        label_str = ",".join(f'{k}="{v}"' for k, v in sorted(labels.items()))
        return f"{name}{{{label_str}}}"
    
    async def get_metrics(self) -> str:
        """Get all metrics in Prometheus format."""
        lines = []
        
        # Counters
        for key, value in self._counters.items():
            lines.append(f"{key} {value}")
        
        # Gauges
        for key, value in self._gauges.items():
            lines.append(f"{key} {value}")
        
        # Histograms (simplified - just count and sum)
        for key, values in self._histograms.items():
            if values:
                lines.append(f"{key}_count {len(values)}")
                lines.append(f"{key}_sum {sum(values)}")
                lines.append(f"{key}_avg {sum(values) / len(values):.4f}")
        
        # Uptime
        uptime = time.time() - self._start_time
        lines.append(f"process_uptime_seconds {uptime:.2f}")
        
        return "\n".join(lines)
    
    async def get_json(self) -> Dict[str, Any]:
        """Get all metrics as JSON."""
        histogram_stats = {}
        for key, values in self._histograms.items():
            if values:
                histogram_stats[key] = {
                    "count": len(values),
                    "sum": sum(values),
                    "avg": sum(values) / len(values),
                    "min": min(values),
                    "max": max(values)
                }
        
        return {
            "counters": self._counters.copy(),
            "gauges": self._gauges.copy(),
            "histograms": histogram_stats,
            "uptime_seconds": time.time() - self._start_time
        }
    
    def timer(self, name: str, labels: Dict[str, str] = None):
        """Context manager to time operations."""
        return TimerContext(self, name, labels)


class TimerContext:
    """Context manager for timing operations."""
    
    def __init__(self, collector: MetricsCollector, name: str, labels: Dict[str, str] = None):
        self.collector = collector
        self.name = name
        self.labels = labels
        self.start_time = None
    
    async def __aenter__(self):
        self.start_time = time.time()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        await self.collector.observe(self.name, duration, self.labels)
        return False


# ============================================================================
# Global Instances
# ============================================================================

_health_checker: Optional[HealthChecker] = None
_metrics_collector: Optional[MetricsCollector] = None
_circuit_breakers: Dict[str, CircuitBreaker] = {}


def get_health_checker() -> HealthChecker:
    """Get or create the global health checker."""
    global _health_checker
    if _health_checker is None:
        _health_checker = HealthChecker()
    return _health_checker


def get_metrics_collector() -> MetricsCollector:
    """Get or create the global metrics collector."""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector


def get_circuit_breaker(name: str) -> CircuitBreaker:
    """Get or create a named circuit breaker."""
    if name not in _circuit_breakers:
        _circuit_breakers[name] = CircuitBreaker(name)
    return _circuit_breakers[name]


async def init_reliability() -> None:
    """Initialize reliability components."""
    checker = get_health_checker()
    
    # Register default health checks
    async def check_self():
        return True
    
    checker.register("self", check_self, critical=True)
    
    logger.info("Reliability components initialized")


async def get_all_circuit_breaker_stats() -> Dict[str, Any]:
    """Get stats for all circuit breakers."""
    return {
        name: breaker.get_stats()
        for name, breaker in _circuit_breakers.items()
    }

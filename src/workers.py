"""
Background Workers for FlowSentinel
====================================
Async worker system for background task processing.

Features:
- Async task queue
- Worker pool management
- Task priorities
- Retry with exponential backoff
- Task scheduling
- Progress tracking
- Dead letter queue for failed tasks

Architecture:
- Task: Individual unit of work
- TaskQueue: Async queue for tasks
- Worker: Task processor
- WorkerPool: Manages multiple workers
- Scheduler: Cron-like task scheduling
"""

import logging
import asyncio
import uuid
import time
from typing import Optional, Any, Dict, List, Callable, Awaitable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from collections import deque
import traceback

logger = logging.getLogger(__name__)


# ============================================================================
# Task States and Priorities
# ============================================================================

class TaskState(str, Enum):
    """Task execution states."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    CANCELLED = "cancelled"
    DEAD = "dead"  # Exceeded max retries


class TaskPriority(int, Enum):
    """Task priorities (lower = higher priority)."""
    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3
    BACKGROUND = 4


# ============================================================================
# Task Definition
# ============================================================================

@dataclass
class Task:
    """A background task."""
    id: str
    name: str
    func: Callable[..., Awaitable[Any]]
    args: tuple = field(default_factory=tuple)
    kwargs: Dict[str, Any] = field(default_factory=dict)
    priority: TaskPriority = TaskPriority.NORMAL
    state: TaskState = TaskState.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Any = None
    error: Optional[str] = None
    retries: int = 0
    max_retries: int = 3
    retry_delay: float = 1.0  # seconds, will be multiplied exponentially
    timeout: Optional[float] = None  # seconds
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "priority": self.priority.name,
            "state": self.state.value,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "retries": self.retries,
            "max_retries": self.max_retries,
            "error": self.error,
            "metadata": self.metadata
        }


# ============================================================================
# Task Queue
# ============================================================================

class TaskQueue:
    """
    Async priority queue for tasks.
    Higher priority tasks are processed first.
    """
    
    def __init__(self, max_size: int = 10000):
        self.max_size = max_size
        self._queues: Dict[TaskPriority, deque] = {
            priority: deque() for priority in TaskPriority
        }
        self._lock = asyncio.Lock()
        self._not_empty = asyncio.Condition()
        self._task_count = 0
    
    async def put(self, task: Task) -> bool:
        """Add a task to the queue."""
        async with self._lock:
            if self._task_count >= self.max_size:
                logger.warning("Task queue is full")
                return False
            
            self._queues[task.priority].append(task)
            self._task_count += 1
            
            async with self._not_empty:
                self._not_empty.notify()
            
            return True
    
    async def get(self, timeout: float = None) -> Optional[Task]:
        """Get the highest priority task."""
        async with self._not_empty:
            # Wait for a task if queue is empty
            while self._task_count == 0:
                try:
                    await asyncio.wait_for(
                        self._not_empty.wait(),
                        timeout=timeout
                    )
                except asyncio.TimeoutError:
                    return None
            
            async with self._lock:
                # Get from highest priority queue that has tasks
                for priority in TaskPriority:
                    if self._queues[priority]:
                        task = self._queues[priority].popleft()
                        self._task_count -= 1
                        return task
                
                return None
    
    async def size(self) -> int:
        """Get total number of tasks in queue."""
        return self._task_count
    
    async def size_by_priority(self) -> Dict[str, int]:
        """Get task count by priority."""
        return {
            priority.name: len(queue)
            for priority, queue in self._queues.items()
        }


# ============================================================================
# Worker
# ============================================================================

class Worker:
    """
    Async worker that processes tasks from a queue.
    """
    
    def __init__(
        self,
        worker_id: str,
        queue: TaskQueue,
        on_task_complete: Callable = None,
        on_task_error: Callable = None
    ):
        self.id = worker_id
        self.queue = queue
        self.on_task_complete = on_task_complete
        self.on_task_error = on_task_error
        self._running = False
        self._current_task: Optional[Task] = None
        self._tasks_processed = 0
        self._tasks_failed = 0
    
    async def start(self) -> None:
        """Start the worker."""
        self._running = True
        logger.info(f"Worker {self.id} started")
        
        while self._running:
            try:
                # Get next task
                task = await self.queue.get(timeout=1.0)
                
                if task is None:
                    continue
                
                await self._process_task(task)
                
            except asyncio.CancelledError:
                logger.info(f"Worker {self.id} cancelled")
                break
            except Exception as e:
                logger.error(f"Worker {self.id} error: {e}")
    
    async def stop(self) -> None:
        """Stop the worker."""
        self._running = False
        logger.info(f"Worker {self.id} stopped")
    
    async def _process_task(self, task: Task) -> None:
        """Process a single task."""
        self._current_task = task
        task.state = TaskState.RUNNING
        task.started_at = datetime.utcnow()
        
        try:
            # Execute with timeout if specified
            if task.timeout:
                result = await asyncio.wait_for(
                    task.func(*task.args, **task.kwargs),
                    timeout=task.timeout
                )
            else:
                result = await task.func(*task.args, **task.kwargs)
            
            # Success
            task.result = result
            task.state = TaskState.COMPLETED
            task.completed_at = datetime.utcnow()
            self._tasks_processed += 1
            
            if self.on_task_complete:
                await self.on_task_complete(task)
            
            logger.info(f"Task {task.id} ({task.name}) completed")
            
        except asyncio.TimeoutError:
            await self._handle_task_error(task, "Task timed out")
        except Exception as e:
            await self._handle_task_error(task, str(e))
        finally:
            self._current_task = None
    
    async def _handle_task_error(self, task: Task, error: str) -> None:
        """Handle a failed task with retry logic."""
        task.error = error
        task.retries += 1
        
        if task.retries <= task.max_retries:
            # Retry with exponential backoff
            delay = task.retry_delay * (2 ** (task.retries - 1))
            task.state = TaskState.RETRYING
            
            logger.warning(
                f"Task {task.id} failed, retrying in {delay}s "
                f"(attempt {task.retries}/{task.max_retries})"
            )
            
            await asyncio.sleep(delay)
            await self.queue.put(task)
        else:
            # Max retries exceeded
            task.state = TaskState.DEAD
            task.completed_at = datetime.utcnow()
            self._tasks_failed += 1
            
            if self.on_task_error:
                await self.on_task_error(task)
            
            logger.error(f"Task {task.id} failed permanently: {error}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get worker statistics."""
        return {
            "id": self.id,
            "running": self._running,
            "current_task": self._current_task.id if self._current_task else None,
            "tasks_processed": self._tasks_processed,
            "tasks_failed": self._tasks_failed
        }


# ============================================================================
# Worker Pool
# ============================================================================

class WorkerPool:
    """
    Manages a pool of workers for parallel task processing.
    """
    
    def __init__(
        self,
        num_workers: int = 4,
        queue_max_size: int = 10000
    ):
        self.num_workers = num_workers
        self.queue = TaskQueue(max_size=queue_max_size)
        self.workers: List[Worker] = []
        self._worker_tasks: List[asyncio.Task] = []
        self._running = False
        self._dead_letter_queue: List[Task] = []
        self._completed_tasks: deque = deque(maxlen=1000)
    
    async def start(self) -> None:
        """Start all workers."""
        if self._running:
            return
        
        self._running = True
        
        for i in range(self.num_workers):
            worker = Worker(
                worker_id=f"worker-{i}",
                queue=self.queue,
                on_task_complete=self._on_task_complete,
                on_task_error=self._on_task_error
            )
            self.workers.append(worker)
            task = asyncio.create_task(worker.start())
            self._worker_tasks.append(task)
        
        logger.info(f"Started worker pool with {self.num_workers} workers")
    
    async def stop(self) -> None:
        """Stop all workers."""
        self._running = False
        
        for worker in self.workers:
            await worker.stop()
        
        for task in self._worker_tasks:
            task.cancel()
        
        if self._worker_tasks:
            await asyncio.gather(*self._worker_tasks, return_exceptions=True)
        
        self.workers.clear()
        self._worker_tasks.clear()
        
        logger.info("Worker pool stopped")
    
    async def submit(
        self,
        func: Callable[..., Awaitable[Any]],
        *args,
        name: str = None,
        priority: TaskPriority = TaskPriority.NORMAL,
        max_retries: int = 3,
        timeout: float = None,
        metadata: Dict[str, Any] = None,
        **kwargs
    ) -> Task:
        """
        Submit a task for execution.
        
        Usage:
            task = await pool.submit(
                my_async_function,
                arg1, arg2,
                name="my-task",
                priority=TaskPriority.HIGH
            )
        """
        task = Task(
            id=str(uuid.uuid4()),
            name=name or func.__name__,
            func=func,
            args=args,
            kwargs=kwargs,
            priority=priority,
            max_retries=max_retries,
            timeout=timeout,
            metadata=metadata or {}
        )
        
        await self.queue.put(task)
        logger.debug(f"Submitted task {task.id} ({task.name})")
        
        return task
    
    async def _on_task_complete(self, task: Task) -> None:
        """Called when a task completes successfully."""
        self._completed_tasks.append(task)
    
    async def _on_task_error(self, task: Task) -> None:
        """Called when a task fails permanently."""
        self._dead_letter_queue.append(task)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get pool statistics."""
        return {
            "running": self._running,
            "num_workers": self.num_workers,
            "queue_size": self.queue._task_count,
            "dead_letter_count": len(self._dead_letter_queue),
            "completed_count": len(self._completed_tasks),
            "workers": [w.get_stats() for w in self.workers]
        }
    
    def get_dead_letter_tasks(self) -> List[Dict[str, Any]]:
        """Get failed tasks from dead letter queue."""
        return [t.to_dict() for t in self._dead_letter_queue]
    
    async def retry_dead_letter(self, task_id: str) -> bool:
        """Retry a task from the dead letter queue."""
        for i, task in enumerate(self._dead_letter_queue):
            if task.id == task_id:
                task.state = TaskState.PENDING
                task.retries = 0
                task.error = None
                await self.queue.put(task)
                self._dead_letter_queue.pop(i)
                return True
        return False


# ============================================================================
# Scheduler
# ============================================================================

class Scheduler:
    """
    Cron-like scheduler for recurring tasks.
    """
    
    def __init__(self, worker_pool: WorkerPool):
        self.pool = worker_pool
        self._schedules: Dict[str, Dict[str, Any]] = {}
        self._running = False
        self._scheduler_task: Optional[asyncio.Task] = None
    
    def schedule(
        self,
        name: str,
        func: Callable[..., Awaitable[Any]],
        interval_seconds: int,
        priority: TaskPriority = TaskPriority.NORMAL,
        run_immediately: bool = False
    ) -> None:
        """
        Schedule a recurring task.
        
        Usage:
            scheduler.schedule(
                "cleanup",
                cleanup_old_data,
                interval_seconds=3600,  # hourly
                run_immediately=True
            )
        """
        self._schedules[name] = {
            "func": func,
            "interval": interval_seconds,
            "priority": priority,
            "last_run": None if run_immediately else datetime.utcnow(),
            "next_run": datetime.utcnow() if run_immediately else datetime.utcnow() + timedelta(seconds=interval_seconds)
        }
        logger.info(f"Scheduled task '{name}' every {interval_seconds}s")
    
    def unschedule(self, name: str) -> bool:
        """Remove a scheduled task."""
        if name in self._schedules:
            del self._schedules[name]
            return True
        return False
    
    async def start(self) -> None:
        """Start the scheduler."""
        self._running = True
        self._scheduler_task = asyncio.create_task(self._run_scheduler())
        logger.info("Scheduler started")
    
    async def stop(self) -> None:
        """Stop the scheduler."""
        self._running = False
        if self._scheduler_task:
            self._scheduler_task.cancel()
            try:
                await self._scheduler_task
            except asyncio.CancelledError:
                pass
        logger.info("Scheduler stopped")
    
    async def _run_scheduler(self) -> None:
        """Main scheduler loop."""
        while self._running:
            try:
                now = datetime.utcnow()
                
                for name, schedule in self._schedules.items():
                    if now >= schedule["next_run"]:
                        # Submit task
                        await self.pool.submit(
                            schedule["func"],
                            name=f"scheduled:{name}",
                            priority=schedule["priority"]
                        )
                        
                        # Update schedule
                        schedule["last_run"] = now
                        schedule["next_run"] = now + timedelta(seconds=schedule["interval"])
                        
                        logger.debug(f"Triggered scheduled task '{name}'")
                
                # Check every second
                await asyncio.sleep(1)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
    
    def get_schedules(self) -> List[Dict[str, Any]]:
        """Get all scheduled tasks."""
        return [
            {
                "name": name,
                "interval_seconds": s["interval"],
                "priority": s["priority"].name,
                "last_run": s["last_run"].isoformat() if s["last_run"] else None,
                "next_run": s["next_run"].isoformat()
            }
            for name, s in self._schedules.items()
        ]


# ============================================================================
# Global Instance
# ============================================================================

_worker_pool: Optional[WorkerPool] = None
_scheduler: Optional[Scheduler] = None


def get_worker_pool() -> WorkerPool:
    """Get or create the global worker pool."""
    global _worker_pool
    if _worker_pool is None:
        _worker_pool = WorkerPool()
    return _worker_pool


def get_scheduler() -> Scheduler:
    """Get or create the global scheduler."""
    global _scheduler
    if _scheduler is None:
        _scheduler = Scheduler(get_worker_pool())
    return _scheduler


async def init_workers(num_workers: int = 4) -> WorkerPool:
    """Initialize and start the global worker pool."""
    global _worker_pool, _scheduler
    _worker_pool = WorkerPool(num_workers=num_workers)
    await _worker_pool.start()
    _scheduler = Scheduler(_worker_pool)
    await _scheduler.start()
    logger.info(f"Workers initialized with {num_workers} workers")
    return _worker_pool


async def shutdown_workers() -> None:
    """Shutdown workers and scheduler."""
    global _worker_pool, _scheduler
    if _scheduler:
        await _scheduler.stop()
    if _worker_pool:
        await _worker_pool.stop()
    logger.info("Workers shutdown complete")

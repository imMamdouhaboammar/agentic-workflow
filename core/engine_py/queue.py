"""
queue.py — Pluggable Task Queuing System (QueueDAO).

Implements:
- Abstract TaskQueue base interface
- InMemoryTaskQueue for testing & sub-millisecond local execution
- SQLiteTaskQueue for durable, ACID, zero-infra persistence with lease renewal
"""

import time
import json
import sqlite3
import threading
from contextlib import contextmanager
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from core.engine_py.models import TaskInstance, TaskStatus, TaskDefinition, AgentRole, RetryPolicy, BackoffType, CircuitBreakerConfig


class TaskQueue(ABC):
    """Abstract interface for task scheduling, leasing, and completion."""

    @abstractmethod
    def push(self, task: TaskInstance) -> None:
        """Enqueues a task for worker execution."""
        pass

    @abstractmethod
    def poll(self, task_types: List[str], worker_id: str, lease_seconds: float = 60.0) -> Optional[TaskInstance]:
        """Polls for a matching task and acquires an execution lease."""
        pass

    @abstractmethod
    def ack(self, task_id: str) -> None:
        """Acknowledges successful task completion, removing it from queue."""
        pass

    @abstractmethod
    def nack(self, task_id: str, requeue: bool = True) -> None:
        """Negative acknowledgment; resets task to QUEUED or marks failed."""
        pass

    @abstractmethod
    def heartbeat(self, task_id: str, worker_id: str, extend_seconds: float = 60.0) -> bool:
        """Renews the active worker lease to prevent timeout reclamation."""
        pass

    @abstractmethod
    def reclaim_expired(self) -> List[str]:
        """Reclaims tasks whose leases have expired and returns their IDs."""
        pass

    @abstractmethod
    def size(self) -> int:
        """Returns count of active tasks in queue."""
        pass


class InMemoryTaskQueue(TaskQueue):
    """Thread-safe in-memory task queue."""

    def __init__(self):
        self._lock = threading.Lock()
        self._tasks: Dict[str, TaskInstance] = {}
        self._queue: List[str] = []  # task_ids waiting to be polled

    def push(self, task: TaskInstance) -> None:
        with self._lock:
            self._tasks[task.task_id] = task
            if task.task_id not in self._queue:
                self._queue.append(task.task_id)

    def poll(self, task_types: List[str], worker_id: str, lease_seconds: float = 60.0) -> Optional[TaskInstance]:
        with self._lock:
            for idx, task_id in enumerate(self._queue):
                task = self._tasks.get(task_id)
                if task and (not task_types or task.task_def.type in task_types):
                    self._queue.pop(idx)
                    task.status = TaskStatus.POLLED
                    task.worker_id = worker_id
                    task.lease_expires_at = time.time() + lease_seconds
                    return task
            return None

    def ack(self, task_id: str) -> None:
        with self._lock:
            self._tasks.pop(task_id, None)
            if task_id in self._queue:
                self._queue.remove(task_id)

    def nack(self, task_id: str, requeue: bool = True) -> None:
        with self._lock:
            task = self._tasks.get(task_id)
            if task:
                task.worker_id = None
                task.lease_expires_at = None
                if requeue and task_id not in self._queue:
                    task.status = TaskStatus.SCHEDULED
                    self._queue.append(task_id)
                elif not requeue:
                    task.status = TaskStatus.FAILED
                    self._tasks.pop(task_id, None)

    def heartbeat(self, task_id: str, worker_id: str, extend_seconds: float = 60.0) -> bool:
        with self._lock:
            task = self._tasks.get(task_id)
            if task and task.worker_id == worker_id:
                task.lease_expires_at = time.time() + extend_seconds
                return True
            return False

    def reclaim_expired(self) -> List[str]:
        now = time.time()
        reclaimed = []
        with self._lock:
            for task_id, task in list(self._tasks.items()):
                if task.worker_id and task.lease_expires_at and task.lease_expires_at < now:
                    task.worker_id = None
                    task.lease_expires_at = None
                    task.status = TaskStatus.SCHEDULED
                    if task_id not in self._queue:
                        self._queue.append(task_id)
                    reclaimed.append(task_id)
        return reclaimed

    def size(self) -> int:
        with self._lock:
            return len(self._queue)


class SQLiteTaskQueue(TaskQueue):
    """Durable, ACID SQLite-backed queue with row locking and lease renewal."""

    def __init__(self, db_path: str = ".queue.db"):
        self.db_path = db_path
        self._lock = threading.Lock()
        self._init_db()

    @contextmanager
    def _connection(self):
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def _init_db(self) -> None:
        with self._lock, self._connection() as conn:
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    task_id TEXT PRIMARY KEY,
                    task_type TEXT NOT NULL,
                    workflow_id TEXT NOT NULL,
                    stage_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    worker_id TEXT,
                    lease_expires_at REAL,
                    task_json TEXT NOT NULL,
                    created_at REAL NOT NULL
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_tasks_poll ON tasks(status, task_type);")
            conn.commit()

    def push(self, task: TaskInstance) -> None:
        with self._lock, self._connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO tasks 
                (task_id, task_type, workflow_id, stage_id, status, worker_id, lease_expires_at, task_json, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                task.task_id,
                task.task_def.type,
                task.workflow_id,
                task.stage_id,
                "QUEUED",
                None,
                None,
                json.dumps(task.to_dict()),
                time.time()
            ))
            conn.commit()

    def poll(self, task_types: List[str], worker_id: str, lease_seconds: float = 60.0) -> Optional[TaskInstance]:
        with self._lock, self._connection() as conn:
            query = "SELECT task_id, task_json FROM tasks WHERE status = 'QUEUED'"
            params: List[Any] = []
            if task_types:
                placeholders = ",".join("?" for _ in task_types)
                query += f" AND task_type IN ({placeholders})"
                params.extend(task_types)
            query += " ORDER BY created_at ASC LIMIT 1"

            cursor = conn.execute(query, params)
            row = cursor.fetchone()
            if not row:
                return None

            task_id = row["task_id"]
            now = time.time()
            expires_at = now + lease_seconds

            conn.execute("""
                UPDATE tasks 
                SET status = 'ASSIGNED', worker_id = ?, lease_expires_at = ?
                WHERE task_id = ?
            """, (worker_id, expires_at, task_id))
            conn.commit()

            raw_dict = json.loads(row["task_json"])
            task = self._deserialize_task(raw_dict)
            task.status = TaskStatus.POLLED
            task.worker_id = worker_id
            task.lease_expires_at = expires_at
            return task

    def ack(self, task_id: str) -> None:
        with self._lock, self._connection() as conn:
            conn.execute("DELETE FROM tasks WHERE task_id = ?", (task_id,))
            conn.commit()

    def nack(self, task_id: str, requeue: bool = True) -> None:
        with self._lock, self._connection() as conn:
            if requeue:
                conn.execute("""
                    UPDATE tasks 
                    SET status = 'QUEUED', worker_id = NULL, lease_expires_at = NULL
                    WHERE task_id = ?
                """, (task_id,))
            else:
                conn.execute("DELETE FROM tasks WHERE task_id = ?", (task_id,))
            conn.commit()

    def heartbeat(self, task_id: str, worker_id: str, extend_seconds: float = 60.0) -> bool:
        with self._lock, self._connection() as conn:
            cursor = conn.execute("""
                UPDATE tasks 
                SET lease_expires_at = ?
                WHERE task_id = ? AND worker_id = ?
            """, (time.time() + extend_seconds, task_id, worker_id))
            conn.commit()
            return cursor.rowcount > 0

    def reclaim_expired(self) -> List[str]:
        now = time.time()
        with self._lock, self._connection() as conn:
            cursor = conn.execute("""
                SELECT task_id FROM tasks 
                WHERE status = 'ASSIGNED' AND lease_expires_at < ?
            """, (now,))
            expired_ids = [row["task_id"] for row in cursor.fetchall()]
            if expired_ids:
                placeholders = ",".join("?" for _ in expired_ids)
                conn.execute(f"""
                    UPDATE tasks 
                    SET status = 'QUEUED', worker_id = NULL, lease_expires_at = NULL
                    WHERE task_id IN ({placeholders})
                """, expired_ids)
                conn.commit()
            return expired_ids

    def size(self) -> int:
        with self._lock, self._connection() as conn:
            cursor = conn.execute("SELECT COUNT(*) as count FROM tasks WHERE status = 'QUEUED'")
            row = cursor.fetchone()
            return row["count"] if row else 0

    def _deserialize_task(self, d: Dict[str, Any]) -> TaskInstance:
        td = d["task_def"]
        rp = td.get("retry_policy", {})
        cb = td.get("circuit_breaker", {})
        task_def = TaskDefinition(
            id=td["id"],
            type=td["type"],
            name=td.get("name", ""),
            description=td.get("description", ""),
            role=AgentRole(td.get("role", "engineer")),
            deliverable_path=td.get("deliverable_path"),
            criteria=td.get("criteria", []),
            input_parameters=td.get("input_parameters", {}),
            retry_policy=RetryPolicy(
                max_retries=rp.get("max_retries", 3),
                delay_seconds=rp.get("delay_seconds", 2.0),
                backoff_rate=BackoffType(rp.get("backoff_rate", "EXPONENTIAL"))
            ),
            timeout_seconds=td.get("timeout_seconds", 300),
            circuit_breaker=CircuitBreakerConfig(
                failure_threshold=cb.get("failure_threshold", 2),
                cooldown_seconds=cb.get("cooldown_seconds", 30.0)
            ),
            compensation_task=td.get("compensation_task"),
            branches=td.get("branches", {})
        )
        return TaskInstance(
            task_id=d["task_id"],
            workflow_id=d["workflow_id"],
            stage_id=d["stage_id"],
            task_def=task_def,
            status=TaskStatus(d.get("status", "SCHEDULED")),
            attempt=d.get("attempt", 1),
            input_data=d.get("input_data", {}),
            output_data=d.get("output_data", {}),
            worker_id=d.get("worker_id"),
            scheduled_at=d.get("scheduled_at", time.time()),
            started_at=d.get("started_at"),
            completed_at=d.get("completed_at"),
            lease_expires_at=d.get("lease_expires_at"),
            pacs_score=d.get("pacs_score"),
            gate_verdict=d.get("gate_verdict"),
            error_message=d.get("error_message"),
            trace_id=d.get("trace_id", "")
        )

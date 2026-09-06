"""
event_bus.py — Async Event Bus & Append-Only Ledger for Agentic Engine.

Provides:
- In-process async pub/sub with wildcard pattern matching
- Durable append-only event ledger (ledger.jsonl)
- Webhook/external signal dispatch hooks
"""

import os
import json
import fnmatch
import asyncio
import threading
from typing import Dict, List, Callable, Awaitable, Any, Optional
from core.engine_py.models import EngineEvent


class AsyncEventBus:
    """High-performance asynchronous event bus with durable ledger logging."""

    def __init__(self, ledger_path: Optional[str] = None):
        self.ledger_path = ledger_path
        self._subscribers: List[tuple[str, Callable[[EngineEvent], Awaitable[None]]]] = []
        self._lock = threading.Lock()
        if self.ledger_path:
            os.makedirs(os.path.dirname(os.path.abspath(self.ledger_path)), exist_ok=True)

    def subscribe(self, pattern: str, handler: Callable[[EngineEvent], Awaitable[None]]) -> None:
        """Subscribe an async handler to events matching a glob pattern (e.g. 'task.*')."""
        with self._lock:
            self._subscribers.append((pattern, handler))

    async def publish(self, event: EngineEvent) -> None:
        """Publishes an event to matching subscribers and appends to durable ledger."""
        # 1. Durable append-only log
        if self.ledger_path:
            self._append_to_ledger(event)

        # 2. Match subscribers
        with self._lock:
            matched_handlers = [
                handler for pattern, handler in self._subscribers
                if fnmatch.fnmatch(event.event_type, pattern)
            ]

        # 3. Concurrent dispatch to subscribers
        if matched_handlers:
            coros = [handler(event) for handler in matched_handlers]
            results = await asyncio.gather(*coros, return_exceptions=True)
            for res in results:
                if isinstance(res, Exception):
                    # Keep bus resilient; log error without taking down other subscribers
                    print(f"⚠️ [EventBus] Handler exception for event {event.event_type}: {res}")

    def _append_to_ledger(self, event: EngineEvent) -> None:
        """Synchronously appends serialized event record to disk."""
        try:
            line = json.dumps(event.to_dict()) + "\n"
            with open(self.ledger_path, "a", encoding="utf-8") as f:
                f.write(line)
        except OSError as err:
            print(f"⚠️ [EventBus] Failed to append to ledger {self.ledger_path}: {err}")

"""
Session Context Memory for GitIntel AI.

Provides conversation-scoped memory so the analyst remembers:
- Previously discussed widgets and charts
- Prior conclusions and risks
- The repository being analyzed

Implementation is deliberately simple (in-memory dict) so it can be
replaced later with Redis, Postgres, or a proper conversation store
without changing the orchestrator interface.

Thread-safety note: For the current single-process FastAPI deployment
this is sufficient. Add locking if you move to multi-worker.
"""

from __future__ import annotations
import time
from typing import Dict, Optional
from ai.core.models import SessionContext, ConversationTurn


class SessionStore:
    """
    In-memory session store with simple TTL-based eviction.
    """

    def __init__(self, max_sessions: int = 500, ttl_seconds: int = 60 * 45):
        self._sessions: Dict[str, SessionContext] = {}
        self._max_sessions = max_sessions
        self._ttl = ttl_seconds
        self._last_cleanup = time.time()

    def get_or_create(self, session_id: str, repository: str) -> SessionContext:
        self._maybe_cleanup()
        if session_id not in self._sessions:
            self._sessions[session_id] = SessionContext(session_id=session_id, repository=repository)
            # Evict oldest if over limit (very simple LRU approximation)
            if len(self._sessions) > self._max_sessions:
                oldest = min(self._sessions.items(), key=lambda kv: kv[1].last_active)
                self._sessions.pop(oldest[0], None)
        return self._sessions[session_id]

    def get(self, session_id: str) -> Optional[SessionContext]:
        self._maybe_cleanup()
        return self._sessions.get(session_id)

    def clear(self, session_id: str) -> None:
        self._sessions.pop(session_id, None)

    def _maybe_cleanup(self) -> None:
        now = time.time()
        if now - self._last_cleanup < 60:
            return
        self._last_cleanup = now
        expired = [
            sid for sid, sess in self._sessions.items()
            if now - self._parse_ts(sess.last_active) > self._ttl
        ]
        for sid in expired:
            self._sessions.pop(sid, None)

    @staticmethod
    def _parse_ts(ts: str) -> float:
        try:
            return time.mktime(time.strptime(ts, "%Y-%m-%dT%H:%M:%S.%f"))
        except Exception:
            return time.time() - 3600


# Global singleton used by the orchestrator
session_store = SessionStore()

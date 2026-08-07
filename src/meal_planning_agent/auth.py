from collections import OrderedDict
from contextvars import ContextVar
from dataclasses import dataclass, field

from agents import SQLiteSession

from .preference_models import SessionState

"""
This is kind of a hack thrown together by Claude to allow for multiple sessions
until I get around to implementing a proper session management system.
"""

MAX_SESSIONS = 100  # LRU cap on concurrently-remembered browser sessions


@dataclass
class UserSession:
    state: SessionState = field(default_factory=SessionState)
    history: SQLiteSession | None = None


_sessions: OrderedDict[str, UserSession] = OrderedDict()

_current_session: ContextVar[SessionState | None] = ContextVar(
    "meal_planner_session", default=None
)


def _get_or_create_session(session_hash: str) -> UserSession:
    existing = _sessions.get(session_hash)
    if existing is not None:
        _sessions.move_to_end(session_hash)
        return existing
    user_session = UserSession(history=SQLiteSession(session_id=session_hash))
    _sessions[session_hash] = user_session
    while len(_sessions) > MAX_SESSIONS:
        _sessions.popitem(last=False)
    return user_session


def set_current_session(state: SessionState) -> None:
    """Call once at the start of each chat turn, in the turn's own task."""
    _current_session.set(state)


def _require_session() -> SessionState:
    state = _current_session.get()
    if state is None:
        raise RuntimeError("No session bound; call set_current_session() first.")
    return state

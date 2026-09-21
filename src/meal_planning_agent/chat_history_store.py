from agents import SQLiteSession

# Iterative solution until I add databases
_chat_history_store: dict[str, SQLiteSession] = {}


def get_or_create_history(session_id: str) -> SQLiteSession:
    if not session_id:
        raise ValueError("No session id was passed")

    history = _chat_history_store.get(session_id)
    if history is None:
        history = SQLiteSession(session_id=session_id),
        upsert_history(session_id, history)

    return history


def upsert_history(
    session_id: str,
    history: SQLiteSession,
):
    if not session_id:
        raise ValueError("No session id was passed")

    _chat_history_store[session_id] = history

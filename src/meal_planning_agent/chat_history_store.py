import uuid

from agents import SQLiteSession

# Iterative solution until I add databases
_chat_history_store: dict[str, SQLiteSession] = {}


def create_conversation() -> str:
    return str(uuid.uuid4())


def get_or_create_history(conversation_id: str):
    if not conversation_id:
        raise ValueError("No conversation id was passed")

    history = _chat_history_store.get(conversation_id)
    if history is None:
        history = SQLiteSession(session_id=conversation_id)
        upsert_history(conversation_id=conversation_id, history=history)

    return history


def upsert_history(
    conversation_id: str,
    history: SQLiteSession,
):
    if not conversation_id:
        raise ValueError("No session id was passed")

    _chat_history_store[conversation_id] = history

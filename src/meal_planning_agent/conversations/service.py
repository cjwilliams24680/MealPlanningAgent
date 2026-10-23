import uuid
from dataclasses import replace

from agents import SQLiteSession

from meal_planning_agent.conversations.models import Conversation

# Iterative solution until I add databases
_conversation_db: dict[str, Conversation] = {}


def create_conversation(user_id: str) -> str:
    conversation_id = str(uuid.uuid4())
    conversation = Conversation(
        id=conversation_id,
        user_id=user_id,
        history=SQLiteSession(session_id=conversation_id),
    )
    _conversation_db[conversation_id] = conversation
    return conversation


def get_conversation(conversation_id: str, user_id: str) -> Conversation | None:
    if not conversation_id:
        raise ValueError("No conversation id was passed")

    conversation = _conversation_db.get(conversation_id)
    if conversation is None or conversation.user_id != user_id:
        return None

    return conversation


def update_history(
    user_id: str,
    conversation_id: str,
    history: SQLiteSession,
):
    conversation = get_conversation(conversation_id=conversation_id, user_id=user_id)
    if conversation:
        _conversation_db[conversation_id] = replace(conversation, history=history)

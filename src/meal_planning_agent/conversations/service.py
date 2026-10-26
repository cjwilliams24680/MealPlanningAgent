import json
import uuid
from typing import Any

import meal_planning_agent.conversations_database as ConversationsDatabase
from meal_planning_agent.conversations.models import Conversation


async def create_conversation(user_id: str) -> Conversation:
    conversation_id = str(uuid.uuid4())
    conversation = Conversation(id=conversation_id, user_id=str(user_id))

    async with ConversationsDatabase.get_resource() as resource:
        table = await resource.Table(ConversationsDatabase.TABLE_NAME)
        await table.put_item(
            Item={
                "id": conversation.id,
                "user_id": conversation.user_id,
                "history": json.dumps(conversation.history),
            }
        )

    return conversation


async def get_conversation(conversation_id: str, user_id: str) -> Conversation | None:
    if not conversation_id:
        raise ValueError("No conversation id was passed")

    async with ConversationsDatabase.get_resource() as resource:
        table = await resource.Table(ConversationsDatabase.TABLE_NAME)
        response = await table.get_item(Key={"id": conversation_id})

    item = response.get("Item")
    if item is None or item["user_id"] != str(user_id):
        return None

    return Conversation(
        id=item["id"],
        user_id=item["user_id"],
        history=json.loads(item["history"]),
    )


async def update_history(
    user_id: str,
    conversation_id: str,
    history: list[Any],
):
    conversation = await get_conversation(
        conversation_id=conversation_id, user_id=user_id
    )
    if not conversation:
        return

    async with ConversationsDatabase.get_resource() as resource:
        table = await resource.Table(ConversationsDatabase.TABLE_NAME)
        await table.update_item(
            Key={"id": conversation_id},
            UpdateExpression="SET history = :history",
            ExpressionAttributeValues={":history": json.dumps(history)},
        )

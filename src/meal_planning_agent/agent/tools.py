from agents import RunContextWrapper, function_tool

import meal_planning_agent.push.service as PushService
from meal_planning_agent.agent_context import AgentContext
from meal_planning_agent.preferences.models import UserPreferencesBase
from meal_planning_agent.preferences_store import (
    _sanitize_user_preferences,
    get_or_create_preferences,
    upsert_preferences,
)


@function_tool
def send_push_notification(message: str):
    """
    Send a push notification to the developer.

    Args:
        message: The message to send to the developer.
    """
    PushService.send_push_notification(message)


@function_tool
async def set_user_preferences(
    wrapper: RunContextWrapper[AgentContext],
    update: UserPreferencesBase,
):
    """Sets the user's saved preferences."""
    upsert_preferences(wrapper.context.user_id, _sanitize_user_preferences(update))


@function_tool
async def get_user_preferences_tool(
    wrapper: RunContextWrapper[AgentContext],
) -> UserPreferencesBase:
    """Returns the user's saved preferences."""
    return get_or_create_preferences(wrapper.context.user_id)

from agents import RunContextWrapper, function_tool

from meal_planning_agent.auth import UserMetadata
from meal_planning_agent.preferences.models import UserPreferencesBase
from meal_planning_agent.utils import clamp

# Iterative solution until I add databases
_preferences_store: dict[str, UserPreferencesBase] = {}


async def get_or_create_preferences(session_id: str) -> UserPreferencesBase:
    if not session_id:
        raise ValueError("No session id was passed")

    history = _preferences_store.get(session_id)
    if history is None:
        history = UserPreferencesBase()
        upsert_preferences(session_id, history)

    return history


async def upsert_preferences(
    session_id: str,
    preferences: UserPreferencesBase,
):
    if not session_id:
        raise ValueError("No session id was passed")

    _preferences_store[session_id] = preferences


def _sanitize_user_preferences(raw: UserPreferencesBase) -> UserPreferencesBase:
    return raw.model_copy(
        update={
            "number_of_meals_per_meal_plan": clamp(
                raw.number_of_meals_per_meal_plan, 1, 10
            ),
            "number_of_servings_portions_per_meal": clamp(
                raw.number_of_servings_portions_per_meal, 1, 100
            ),
        }
    )


@function_tool
async def set_user_preferences(
    wrapper: RunContextWrapper[UserMetadata],
    update: UserPreferencesBase,
):
    """Sets the user's saved preferences."""
    upsert_preferences(wrapper.context.session_id, _sanitize_user_preferences(update))


@function_tool
async def get_user_preferences_tool(
    wrapper: RunContextWrapper[UserMetadata],
) -> UserPreferencesBase:
    """Returns the user's saved preferences."""
    return get_or_create_preferences(wrapper.context.session_id)

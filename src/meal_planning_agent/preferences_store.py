from agents import RunContextWrapper, function_tool

from .auth import UserMetadata
from .preference_models import UserPreferences
from .utils import clamp

# Iterative solution until I add databases
_preferences_store: dict[str, UserPreferences] = {}


def get_or_create_preferences(session_id: str) -> UserPreferences:
    if not session_id:
        raise ValueError("No session id was passed")

    history = _preferences_store.get(session_id)
    if history is None:
        history = UserPreferences()
        upsert_preferences(session_id, history)

    return history


def upsert_preferences(
    session_id: str,
    preferences: UserPreferences,
):
    if not session_id:
        raise ValueError("No session id was passed")

    _preferences_store[session_id] = preferences


def _sanitize_user_preferences(raw: UserPreferences) -> UserPreferences:
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
def set_user_preferences(
    wrapper: RunContextWrapper[UserMetadata], update: UserPreferences
):
    """Sets the user's saved preferences."""
    upsert_preferences(wrapper.context.session_id, _sanitize_user_preferences(update))


@function_tool
def get_user_preferences_tool(
    wrapper: RunContextWrapper[UserMetadata],
) -> UserPreferences:
    """Returns the user's saved preferences."""
    return get_or_create_preferences(wrapper.context.session_id)

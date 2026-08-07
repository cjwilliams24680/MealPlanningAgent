from agents import function_tool

from .auth import _require_session
from .preference_models import UserPreferences
from .utils import clamp


def get_user_preferences() -> UserPreferences:
    return _require_session().preferences


def sanitize_user_preferences(raw: UserPreferences) -> UserPreferences:
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
def set_user_preferences(update: UserPreferences):
    """Sets the user's saved preferences."""
    _require_session().preferences = sanitize_user_preferences(update)


@function_tool
def get_user_preferences_tool() -> UserPreferences:
    """Returns the user's saved preferences."""
    return get_user_preferences()

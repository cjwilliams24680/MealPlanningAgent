from meal_planning_agent.preferences.models import UserPreferencesBase
from meal_planning_agent.utils import clamp

# Iterative solution until I add databases
_preferences_store: dict[int, UserPreferencesBase] = {}


async def get_or_create_preferences(user_id: int) -> UserPreferencesBase:
    if not user_id:
        raise ValueError("No user id was passed")

    history = _preferences_store.get(user_id)
    if history is None:
        history = UserPreferencesBase()
        upsert_preferences(user_id, history)

    return history


async def upsert_preferences(
    user_id: int,
    preferences: UserPreferencesBase,
):
    if not user_id:
        raise ValueError("No user id was passed")

    _preferences_store[user_id] = preferences


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

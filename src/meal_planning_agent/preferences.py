from contextvars import ContextVar
from dataclasses import dataclass, field

from agents import function_tool
from pydantic import BaseModel, Field

from .utils import clamp


class UserPreferences(BaseModel):
    number_of_meals: int = Field(
        default=2,
        description="The number of meals that you should plan. Valid range of values is 1 to 10.",
    )
    number_of_servings_per_meal: int = Field(
        default=4,
        description="Determines how many serving portions we should make for each "
        "meal. Valid range of values is 1 to 100.",
    )
    dietary_restrictions: list[str] = Field(
        default_factory=list,
        description="A list of any dietary restrictions the user has that need to be considered for the meal plan.",
        examples=["Gluten-free", "vegetarian", "dairy-free"],
    )
    likes: list[str] = Field(
        default_factory=list, description="A list of foods user's favorite foods."
    )
    dislikes: list[str] = Field(
        default_factory=list, description="A list of foods that the user does not like."
    )
    nutritional_goals: str = Field(
        default="",
        description="A description of the nutritional goals that the user aims to achieve with this meal plan.",
        examples=["Increase protein intake, lose weight, lower cholesterol"],
    )
    meals_to_avoid_this_time: list[str] = Field(
        default_factory=list,
        description="Specific foods that the user would prefer to avoid this plan.",
    )
    preferred_cooking_methods: list[str] = Field(
        default=["oven", "stovetop", "microwave"],
        description="When cooking is required, these are the user's preferred methods.",
        examples=["oven", "stovetop", "microwave", "grill"],
    )
    notes: str = Field(
        default="",
        description="A paragraph of notes about any preferences that don't apply to one of the other fields.",
        examples=["Half of my meals should be meatless."],
    )


@dataclass
class SessionState:
    """Mutable per-browser-session state. The ContextVar points at this object;
    writes must mutate it (not ContextVar.set) so they're visible across the
    asyncio task tree spawned by gather()."""

    preferences: UserPreferences = field(default_factory=UserPreferences)


_current_session: ContextVar[SessionState | None] = ContextVar(
    "meal_planner_session", default=None
)


def set_current_session(state: SessionState) -> None:
    """Call once at the start of each chat turn, in the turn's own task."""
    _current_session.set(state)


def _require_session() -> SessionState:
    state = _current_session.get()
    if state is None:
        raise RuntimeError("No session bound; call set_current_session() first.")
    return state


@function_tool
def set_user_preferences(update: UserPreferences):
    """Sets the user's saved preferences."""
    _require_session().preferences = sanitize_user_preferences(update)


@function_tool
def get_user_preferences_tool() -> UserPreferences:
    """Returns the user's saved preferences."""
    return get_user_preferences()


def get_user_preferences() -> UserPreferences:
    return _require_session().preferences


def sanitize_user_preferences(raw: UserPreferences) -> UserPreferences:
    return raw.model_copy(
        update={
            "number_of_meals": clamp(raw.number_of_meals, 1, 10),
            "number_of_servings_per_meal": clamp(
                raw.number_of_servings_per_meal, 1, 100
            ),
        }
    )

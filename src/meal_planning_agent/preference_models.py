from dataclasses import dataclass, field

from pydantic import BaseModel, Field


class UserPreferences(BaseModel):
    number_of_meals_per_meal_plan: int = Field(
        default=2,
        description="The number of meals that you should plan. Valid range of values is 1 to 10.",
    )
    number_of_servings_portions_per_meal: int = Field(
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

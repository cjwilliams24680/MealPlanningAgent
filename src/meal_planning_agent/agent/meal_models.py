from dataclasses import dataclass

from pydantic import BaseModel, Field


class PreparedDish(BaseModel):
    name: str = Field(description="The short name of a dish.")
    description: str = Field(description="A 1-2 sentence description of the dish.")
    special_diet_labels: list[str] = Field(
        description="A list of any dietary restrictions that this meal satisfies",
        examples=["vegetarian", "gluten-free"],
    )
    cuisine: list[str] = Field(
        description="The category of food, usually tied to a country or region.",
        examples=["Italian", "Chinese", "Southern Comfort"],
    )


@dataclass
class MealPlanIdeas:
    entree_ideas: list[PreparedDish]
    side_ideas: list[PreparedDish]

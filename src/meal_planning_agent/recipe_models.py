from dataclasses import dataclass

from pydantic import BaseModel, Field

from .meal_models import PreparedDish

grocery_departments = [
    "Produce",
    "Bakery",
    "Pantry",
    "Meat",
    "Refrigerated",
    "Dairy",
    "Frozen",
    "Pharmacy",
    "Other",
]


class Ingredient(BaseModel):
    name: str = Field(
        description="The name of the ingredient.", examples=["Minced Garlic"]
    )
    unit: str = Field(
        description="The unit type by which the ingredient is measured in the recipe.",
        examples=["Tablespoon"],
    )
    quantity: float = Field(
        description="The quanitity of units used in the recipe.", examples=[1.0]
    )
    grocery_store_department: str = Field(
        description="The area of the grocery store where this ingredient can be "
        f"found. Here are the valid values: {grocery_departments}"
    )


class Recipe(BaseModel):
    ingredients: list[Ingredient] = Field(
        description="A list of incredients for the recipe so the user can add them to shopping list."
    )
    number_of_servings_portions: int = Field(
        description="How many serving portions the recipe makes."
    )
    cooking_instructions: str = Field(
        description="A list of instructions for how to prepare and cook the entree, written in markdown."
    )


@dataclass
class MealPlanItem:
    entree: PreparedDish
    entree_recipe: Recipe
    side: PreparedDish
    side_recipe: Recipe

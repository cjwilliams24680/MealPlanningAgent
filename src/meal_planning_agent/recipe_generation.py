import asyncio
from dataclasses import dataclass

from agents import Agent, Runner
from pydantic import BaseModel, Field

from .meal_brainstorm_generation import PreparedDish
from .meal_pairing import MealPairing
from .llm_models import balanced_model
from .recipe_validation import adjust_for_servings_count_if_necessary, validate_recipe
from .preferences import get_user_preferences
from .utils import base_system_instructions

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

recipe_generation_agent = Agent(
    name="Recipe Generation Agent",
    instructions=base_system_instructions,
    model=balanced_model,
    output_type=Recipe,
)

async def generate_recipes(meals: list[MealPairing]) -> list[MealPlanItem]:
    tasks = [generate_recipes_for_meal(item) for item in meals]
    meal_plan_items = await asyncio.gather(*tasks)
    return meal_plan_items


async def generate_recipes_for_meal(meal: MealPairing) -> MealPlanItem:
    entree_recipe, side_recipe = await asyncio.gather(
        generate_recipe(meal.entree),
        generate_recipe(meal.side),
    )
    return MealPlanItem(
        entree=meal.entree,
        entree_recipe=entree_recipe,
        side=meal.side,
        side_recipe=side_recipe,
    )


async def generate_recipe(dish: PreparedDish) -> Recipe:
    prompt = f"""
    The user has selected the following meal for their meal plan:
    {dish}

    I want you to generate a recipe for the above.
    Break it into 3 sections: Ingredients, Preparation Instructions, Cooking Instructions

    Make sure that the recipe conforms to the user's preferences:
    {get_user_preferences()}

    The recipe should use less than 10 ingredients and preparation time under 20 minutes.
    """
    attempts = 0
    while True:
        attempts += 1
        recipe = (await Runner.run(recipe_generation_agent, prompt)).final_output
        recipe = await adjust_for_servings_count_if_necessary(recipe)
        passes_validation = await validate_recipe(dish, recipe)
        if passes_validation or attempts > 3:
            return recipe

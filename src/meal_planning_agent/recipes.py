import asyncio
from dataclasses import dataclass

from agents import Agent, Runner
from pydantic import BaseModel, Field

from .meal_brainstorming import PreparedDish
from .meal_pairing import MealPairing
from .models import default_model, grok_model, high_effort_model
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
    number_of_servings: int = Field(description="How many servings the recipe makes.")
    cooking_instructions: str = Field(
        description="A list of instructions for how to prepare and cook the entree, written in markdown."
    )


@dataclass
class MealPlanItem:
    entree: PreparedDish
    entree_recipe: Recipe
    side: PreparedDish
    side_recipe: Recipe


recipe_generation_system_instructions = f"""
{base_system_instructions}
"""
recipe_generation_agent = Agent(
    name="Recipe Generation Agent",
    instructions=recipe_generation_system_instructions,
    model=default_model,
    output_type=Recipe,
)
recipe_adjustment_agent = Agent(
    name="Recipe Generation Agent",
    instructions=recipe_generation_system_instructions,
    model=high_effort_model,
    output_type=Recipe,
)
recipe_validation_agent = Agent(
    name="Recipe Generation Agent",
    instructions=recipe_generation_system_instructions,
    model=grok_model,
    output_type=bool,
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


async def adjust_for_servings_count_if_necessary(recipe: Recipe) -> Recipe:
    target_servings = get_user_preferences().number_of_servings_per_meal
    if recipe.number_of_servings == target_servings:
        return recipe
    prompt = f"""
    You've generated a recipe for a meal that makes {recipe.number_of_servings}.
    However, the user has explicitly mentioned that they want to make {target_servings}.
    That means each of the ingredient quantities need to be multiplied by a factor
    of {target_servings / recipe.number_of_servings}

    Please adjust the recipe (seen below) so that it makes the correct number of servings:
    {recipe}
    """
    return (await Runner.run(recipe_adjustment_agent, prompt)).final_output


async def validate_recipe(dish: PreparedDish, recipe: Recipe) -> bool:
    prompt = f"""
    You're writing a meal plan for the user and they've selected the following dish:
    {dish.name}

    You've written the following recipe for that dish:
    {recipe}

    Return true if the recipe is simple and conforms to the user's preferences:
    {get_user_preferences()}
    """
    return (await Runner.run(recipe_validation_agent, prompt)).final_output

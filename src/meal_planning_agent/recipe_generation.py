import asyncio

from agents import Agent, Runner

from .llm_models import balanced_model
from .meal_models import PreparedDish
from .meal_pairing import MealPairing
from .preferences import get_user_preferences
from .recipe_models import MealPlanItem, Recipe
from .recipe_validation import adjust_for_servings_count_if_necessary, validate_recipe
from .utils import base_system_instructions

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

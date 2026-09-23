import asyncio

from agents import Agent, Runner

from .llm_models import BALANCED_MODEL
from .meal_models import PreparedDish
from .meal_pairing import MealPairing
from .preference_models import UserPreferences
from .recipe_models import MealPlanItem, Recipe
from .recipe_validation import adjust_for_servings_count_if_necessary, validate_recipe
from .utils import BASE_SYSTEM_INSTRUCTIONS

_RECIPE_GENERATION_AGENT = Agent(
    name="Recipe Generation Agent",
    instructions=BASE_SYSTEM_INSTRUCTIONS,
    model=BALANCED_MODEL,
    output_type=Recipe,
)


async def generate_recipes(
    meals: list[MealPairing], user_preferences: UserPreferences
) -> list[MealPlanItem]:
    tasks = [_generate_recipes_for_meal(item, user_preferences) for item in meals]
    meal_plan_items = await asyncio.gather(*tasks)
    return meal_plan_items


async def _generate_recipes_for_meal(
    meal: MealPairing, user_preferences: UserPreferences
) -> MealPlanItem:
    entree_recipe, side_recipe = await asyncio.gather(
        generate_recipe(meal.entree, user_preferences),
        generate_recipe(meal.side, user_preferences),
    )
    return MealPlanItem(
        entree=meal.entree,
        entree_recipe=entree_recipe,
        side=meal.side,
        side_recipe=side_recipe,
    )


async def generate_recipe(
    dish: PreparedDish, user_preferences: UserPreferences
) -> Recipe:
    prompt = f"""
The user has selected the following meal for their meal plan:
{dish}

I want you to generate a recipe for the above.
Break it into 3 sections: Ingredients, Preparation Instructions, Cooking Instructions

Make sure that the recipe conforms to the user's preferences:
{user_preferences}

The recipe should use less than 10 ingredients and preparation time under 20 minutes.
"""
    attempts = 0
    while True:
        attempts += 1
        recipe = (await Runner.run(_RECIPE_GENERATION_AGENT, prompt)).final_output
        recipe = await adjust_for_servings_count_if_necessary(recipe, user_preferences)
        passes_validation = await validate_recipe(dish, recipe, user_preferences)
        if passes_validation or attempts > 3:
            return recipe

from agents import Agent, Runner

from .llm_models import gemini_model, high_effort_model
from .meal_models import PreparedDish
from .preferences import get_user_preferences
from .recipe_models import Recipe
from .utils import base_system_instructions

recipe_adjustment_agent = Agent(
    name="Recipe Generation Agent",
    instructions=base_system_instructions,
    model=high_effort_model,
    output_type=Recipe,
)
recipe_validation_agent = Agent(
    name="Recipe Generation Agent",
    instructions=base_system_instructions,
    model=gemini_model,
    output_type=bool,
)


async def adjust_for_servings_count_if_necessary(recipe: Recipe) -> Recipe:
    target_servings_portions = (
        get_user_preferences().number_of_servings_portions_per_meal
    )
    if recipe.number_of_servings_portions == target_servings_portions:
        return recipe
    prompt = f"""
    You've generated a recipe for a meal that makes {recipe.number_of_servings_portions} portions.
    However, the user has explicitly mentioned that they want to make {target_servings_portions} portions.
    That means each of the ingredient quantities need to be multiplied by a factor
    of {target_servings_portions / recipe.number_of_servings_portions}

    Please adjust the recipe (seen below) so that it makes the correct number of serving portions:
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

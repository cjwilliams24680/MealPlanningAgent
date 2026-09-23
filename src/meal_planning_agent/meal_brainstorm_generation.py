import asyncio

from agents import Agent, RunContextWrapper, Runner, function_tool

from .auth import UserMetadata
from .llm_models import get_random_model
from .meal_brainstorm_validation import filter_meal_ideas
from .meal_models import MealPlanIdeas, PreparedDish
from .preference_models import UserPreferences
from .preferences_store import get_or_create_preferences
from .seasonal_report import get_seasonal_report
from .utils import BASE_SYSTEM_INSTRUCTIONS, clamp

_BRAINSTORM_INSTRUCTIONS = f"""
{BASE_SYSTEM_INSTRUCTIONS}

Prioritize meals that can be made with minimal (less than ten) unique ingredients.
"""

_MEAL_BRAINSTORMING_AGENT = Agent(
    name="Meal Brainstormer",
    instructions=_BRAINSTORM_INSTRUCTIONS,
    model=get_random_model(),
    output_type=list[PreparedDish],
)


async def _generate_dish_ideas(
    number_of_dishes: int,
    dish_type: str,
    meals_to_avoid: list[str],
    user_preferences: UserPreferences,
    additional_instructions: str = "",
) -> list[PreparedDish]:
    number_of_dishes = clamp(number_of_dishes, 1, 10)
    # Generate extra ideas to allow for more randomness and also in case we need
    # to drop some of them during validation.
    number_of_ideas = number_of_dishes * 5

    user_preferences_prompt = f"""
Here is the user's preferences:
{user_preferences}
"""

    prompt = (
        f"Suggest {number_of_ideas} different {dish_type}. "
        f"Avoid the following meals: {meals_to_avoid}. "
        f"{get_seasonal_report()}. Try to pick meals that are popular for this time of year."
        f"{user_preferences_prompt}. {additional_instructions}"
    )
    return (await Runner.run(_MEAL_BRAINSTORMING_AGENT, prompt)).final_output


async def create_meal_plan_brainstorm(
    number_of_entrees: int,
    number_of_sides: int,
    meals_to_avoid: list[str],
    user_preferences: UserPreferences,
    additional_instructions: str = "",
) -> MealPlanIdeas:
    entrees, sides = await asyncio.gather(
        _generate_dish_ideas(
            number_of_dishes=number_of_entrees,
            dish_type="entrees",
            meals_to_avoid=meals_to_avoid,
            user_preferences=user_preferences,
            additional_instructions=additional_instructions,
        ),
        _generate_dish_ideas(
            number_of_dishes=number_of_sides,
            dish_type="sides",
            meals_to_avoid=meals_to_avoid,
            user_preferences=user_preferences,
            additional_instructions=additional_instructions,
        ),
    )
    meal_ideas = MealPlanIdeas(
        entree_ideas=entrees,
        side_ideas=sides,
    )

    return await filter_meal_ideas(meal_ideas=meal_ideas, user_preferences=user_preferences)

@function_tool(output_type=PreparedDish)
async def generate_meal_idea_with_ingredients(
    context: RunContextWrapper[UserMetadata],
    ingredients: list[str],
    previous_meal_ideas: list[str],
) -> PreparedDish:
    """
    Generate a meal idea that utilizes the given ingredients and avoid any meal
    ideas that have already been suggested to the user.

    Args:
        ingredients: A list of ingredients to use in the meal idea.
        previous_meal_ideas: A list of meal ideas that have already been suggested to the user.
    Returns:
        A meal idea that utilizes the given ingredients.
    """
    ingredients_prompt = f"""
Here is the list of ingredients:
{ingredients}
"""
    user_preferences = get_or_create_preferences(context.context.session_id)
    dish_ideas = await _generate_dish_ideas(
        number_of_dishes=1,
        dish_type="foods",
        meals_to_avoid=previous_meal_ideas,
        user_preferences=user_preferences,
        additional_instructions=f"Use the following ingredients: {ingredients_prompt}",
    )

    # # Wrapping it in a MealPlanIdeas object as a little hack so that we can reuse the filter_meal_ideas validator.
    validated_dish_ideas = await filter_meal_ideas(
        meal_ideas=MealPlanIdeas(
            entree_ideas=dish_ideas,
            side_ideas=[],
        ),
        user_preferences=user_preferences,
    )

    return validated_dish_ideas.entree_ideas[0]

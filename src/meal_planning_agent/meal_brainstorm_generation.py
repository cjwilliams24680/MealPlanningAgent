import asyncio
from dataclasses import dataclass

from agents import Agent, Runner, function_tool
from pydantic import BaseModel, Field

from .llm_models import get_random_model
from .preferences import get_user_preferences
from .utils import base_system_instructions, clamp
from .seasonal_report import get_seasonal_report
from .meal_brainstorm_validation import filter_meal_ideas

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


brainstorm_instructions = f"""
{base_system_instructions}

Prioritize meals that can be made with minimal (less than ten) unique ingredients.
"""

meal_brainstorming_agent = Agent(
    name="Meal Brainstormer",
    instructions=brainstorm_instructions,
    model=get_random_model(),
    output_type=list[PreparedDish],
)


async def generate_dish_ideas(
    number_of_dishes: int,
    dish_type: str,
    meals_to_avoid: list[str],
    additional_instructions: str = "",
) -> list[PreparedDish]:
    number_of_dishes = clamp(number_of_dishes, 1, 10)
    # Generate extra ideas to allow for more randomness and also in case we need
    # to drop some of them during validation.
    number_of_ideas = number_of_dishes * 5

    preferences = get_user_preferences()
    user_preferences_prompt = f"""
    Here is the user's preferences:
    {preferences}
    """

    prompt = (
        f"Suggest {number_of_ideas} different {dish_type}. "
        f"Avoid the following meals: {meals_to_avoid}. "
        f"{get_seasonal_report()}. Try to pick meals that are popular for this time of year."
        f"{user_preferences_prompt}. {additional_instructions}"
    )
    return (await Runner.run(meal_brainstorming_agent, prompt)).final_output


async def create_meal_plan_brainstorm(
    number_of_entrees: int,
    number_of_sides: int,
    meals_to_avoid: list[str],
    additional_instructions: str = "",
) -> MealPlanIdeas:
    entrees, sides = await asyncio.gather(
        generate_dish_ideas(
            number_of_dishes=number_of_entrees,
            dish_type="entrees",
            meals_to_avoid=meals_to_avoid,
            additional_instructions=additional_instructions,
        ),
        generate_dish_ideas(
            number_of_dishes=number_of_sides,
            dish_type="sides",
            meals_to_avoid=meals_to_avoid,
            additional_instructions=additional_instructions,
        ),
    )
    meal_ideas = MealPlanIdeas(
        entree_ideas=entrees,
        side_ideas=sides,
    )

    return await filter_meal_ideas(meal_ideas)

@function_tool(output_type=PreparedDish)
async def generate_meal_idea_with_ingredients(
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
    dish_ideas = await generate_dish_ideas(
        number_of_dishes=1,
        dish_type="foods",
        meals_to_avoid=previous_meal_ideas,
        additional_instructions=f"Use the following ingredients: {ingredients_prompt}",
    )

    # Wrapping it in a MealPlanIdeas object as a little hack so that we can reuse the filter_meal_ideas validator.
    validated_dish_ideas = await filter_meal_ideas(
        MealPlanIdeas(
            entree_ideas=dish_ideas,
            side_ideas=[],
        )
    )

    return validated_dish_ideas.entree_ideas[0]

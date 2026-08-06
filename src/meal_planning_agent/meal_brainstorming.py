import asyncio
from dataclasses import dataclass
from datetime import datetime

from agents import Agent, Runner, function_tool
from pydantic import BaseModel, Field

from .models import default_model, get_random_model
from .preferences import get_user_preferences
from .utils import base_system_instructions, clamp, to_markdown_list


# Used to make the meals weather-appropriate and add a little bit of differentiation to the prompt week-to-week.
def get_seasonal_report():
    now = datetime.now()
    month_name = now.strftime("%B")
    month_num = now.month

    # Season list (indexed 0-3)
    seasons = ["Winter", "Spring", "Summer", "Autumn"]

    # Weather descriptions for each season
    weather_data = {
        "Winter": "Expect cold temperatures, frosty mornings, and the occasional flurry of snow.",
        "Spring": "The days are getting longer and you'll see flowers beginning to bloom.",
        "Summer": "It's time for sunshine, warm breeze, and plenty of outdoor activities.",
        "Autumn": "The air is turning crisp and the leaves are putting on a colorful show.",
    }

    # The math trick: (month % 12 // 3)
    # Dec(12), Jan(1), Feb(2) map to 0 (Winter)
    # Mar(3), Apr(4), May(5) map to 1 (Spring)
    # Jun(6), Jul(7), Aug(8) map to 2 (Summer)
    # Sep(9), Oct(10), Nov(11) map to 3 (Autumn)
    season_idx = month_num % 12 // 3
    season = seasons[season_idx]
    description = weather_data[season]

    return f"It's {month_name} and {season} is here! {description}"


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

{get_seasonal_report()}
Try to pick meals that are popular for this time of year.
"""

meal_brainstorming_agent = Agent(
    name="Meal Brainstormer",
    instructions=brainstorm_instructions,
    model=get_random_model(),
    output_type=list[PreparedDish],
)

@function_tool(PreparedDish)
async def generate_meal_idea_with_ingredients(
    ingredients: list[str],
    previous_meal_ideas: list[str],
) -> PreparedDish:
    """
    Generate a meal idea that utilizes the given ingredients and avoid any meal ideas that have already been suggested to the user.

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
        additional_instructions=f"Use the following ingredients: {ingredients_prompt}")

    # Wrapping it in a MealPlanIdeas object as a little hack so that we can reuse the filter_meal_ideas validator.
    validated_dish_ideas = await filter_meal_ideas(MealPlanIdeas(
        entree_ideas=dish_ideas,
        side_ideas=[],
    ))

    return validated_dish_ideas.entree_ideas[0]

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

    prompt = f"Suggest {number_of_ideas} different {dish_type}. Avoid the following meals: {meals_to_avoid}. {user_preferences_prompt}. {additional_instructions}"
    return (await Runner.run(meal_brainstorming_agent, prompt)).final_output

async def create_meal_plan_brainstorm(
    number_of_meals: int, 
    meals_to_avoid: list[str]
) -> MealPlanIdeas:
    return await create_meal_plan_brainstorm(
        number_of_entrees=number_of_meals, 
        number_of_sides=number_of_meals, 
        meals_to_avoid=meals_to_avoid,
    )

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

meal_validation_instructions = f"""
{base_system_instructions}

Part of your job is inspecting menus for clients and flagging any foods that they would dislike.
Identifying violations of your client's food allergen or dietary restriction rules is your highest priority.
"""


def filter_out_flagged_dishes(
    dishes: list[PreparedDish], flagged_names: set[str]
) -> list[PreparedDish]:
    return [dish for dish in dishes if dish.name not in flagged_names]


meal_filterer = Agent(
    name="Meal Idea Filterer",
    instructions=meal_validation_instructions,
    model=default_model,
    output_type=list[str],
)


async def filter_meal_ideas(meal_ideas: MealPlanIdeas) -> MealPlanIdeas:
    all_dishes = meal_ideas.entree_ideas + meal_ideas.side_ideas
    prompt = f"""
    You have a list of foods that have been generated as candidates for the user's meal plan:
    {to_markdown_list([dish.name for dish in all_dishes])}

    Here is the user's meal plan preferences:
    {get_user_preferences()}

    Your job is to identify and return the exact dish names from the list above
    that are poor candidates based on the user's preferences.
    """
    flagged_foods = set((await Runner.run(meal_filterer, prompt)).final_output)

    # Filter out flagged foods and shuffle them to make the selection more random.
    return MealPlanIdeas(
        entree_ideas=filter_out_flagged_dishes(meal_ideas.entree_ideas, flagged_foods),
        side_ideas=filter_out_flagged_dishes(meal_ideas.side_ideas, flagged_foods),
    )

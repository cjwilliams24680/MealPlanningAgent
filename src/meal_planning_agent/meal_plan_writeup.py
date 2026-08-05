from agents import Agent, Runner, function_tool
from pydantic import BaseModel, Field
from .models import default_model
from .utils import base_system_instructions
from .recipes import MealPlanItem
from .meal_pairing import MealPairing
from .recipes import generate_recipes
from .shopping_list import get_consolidated_ingredients, sort_ingredients, generate_ingredients_markdown

class MealPlan(BaseModel):
    plan_markdown: str = Field(description="The markdown formatted meal plan to be shared with the user.")
    aggregated_shopping_list_markdown: str = Field(description="The markdown formatted shopping list to be shared with the user.")

@function_tool(output_type=MealPlan)
async def generate_meal_plan(meal_pairings: list[MealPairing]) -> MealPlan:
    """
    Generates a meal plan with a shopping list from a list of meal pairings.

    Args:
        meal_pairings: A list of meal pairings to include in the meal plan.
    """
    meal_plan_items = await generate_recipes(meal_pairings)
    meal_plan = MealPlan(
        plan_markdown = await write_meal_plan(meals = meal_plan_items), 
        aggregated_shopping_list_markdown=write_shopping_list(meals = meal_plan_items),
    )
    return meal_plan

author_instructions = f'''
{base_system_instructions}
'''
author_agent = Agent(
    name="Meal Plan Author",
    model = default_model,
    instructions=author_instructions
)

async def write_meal_plan(meals: list[MealPlanItem]) -> str:
    prompt = f'''
    You have generated the following meal plan items:
    {meals}

    I want you to write a pretty Markdown string. It should start off with a high level summary of the dishes that are included in the meal plan.

    Then there should be a divider followed by a detailed section specific to each PreparedDish.
    Each should include an ingredients segment and a cooking instructions segment.
    '''
    return (await Runner.run(author_agent, prompt)).final_output

def write_shopping_list(meals: list[MealPlanItem]) -> str:
    ingredients = get_consolidated_ingredients(meal_plan=meals)
    sorted_ingredients = sort_ingredients(ingredients)
    return generate_ingredients_markdown(sorted_ingredients)
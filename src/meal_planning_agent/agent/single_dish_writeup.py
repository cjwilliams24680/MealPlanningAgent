from agents import RunContextWrapper, function_tool
from pydantic import BaseModel, Field

from meal_planning_agent.agent.meal_models import PreparedDish
from meal_planning_agent.agent.recipe_generation import generate_recipe
from meal_planning_agent.agent.recipe_models import Recipe
from meal_planning_agent.agent.shopping_list import (
    generate_ingredients_markdown,
    sort_ingredients,
)
from meal_planning_agent.auth import UserMetadata
from meal_planning_agent.preferences_store import get_or_create_preferences


class SingleDishWriteup(BaseModel):
    recipe_markdown: str = Field(
        description="The markdown formatted recipe to be shared with the user."
    )
    shopping_list_markdown: str = Field(
        description="The markdown formatted shopping list to be shared with the user."
    )


def _write_shopping_list(recipe: Recipe) -> str:
    sorted_ingredients = sort_ingredients(recipe.ingredients)
    return generate_ingredients_markdown(sorted_ingredients)


@function_tool(output_type=SingleDishWriteup)
async def generate_writeup_for_single_dish(
    wrapper: RunContextWrapper[UserMetadata],
    requested_dish: PreparedDish,
) -> SingleDishWriteup:
    """
    Generates a recipe and shopping list for a single dish.

    Args:
        requested_dish: The dish that the user has requested a recipe for.
    Returns:
        A SingleDishWriteup object containing the recipe_markdown and shopping_list_markdown for the requested dish.
    """
    recipe = await generate_recipe(
        requested_dish, get_or_create_preferences(wrapper.context.session_id)
    )
    writeup = SingleDishWriteup(
        recipe_markdown=recipe.cooking_instructions,
        shopping_list_markdown=_write_shopping_list(recipe=recipe),
    )
    return writeup

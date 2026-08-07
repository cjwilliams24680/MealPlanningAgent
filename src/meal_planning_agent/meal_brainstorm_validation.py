from agents import Agent, Runner

from .llm_models import default_model
from .meal_models import MealPlanIdeas, PreparedDish
from .preferences import get_user_preferences
from .utils import base_system_instructions, to_markdown_list

meal_validation_instructions = f"""
{base_system_instructions}

Part of your job is inspecting menus for clients and flagging any foods that they would dislike.
Identifying violations of your client's food allergen or dietary restriction rules is your highest priority.
"""

meal_filterer = Agent(
    name="Meal Idea Filterer",
    instructions=meal_validation_instructions,
    model=default_model,
    output_type=list[str],
)


def filter_out_flagged_dishes(
    dishes: list[PreparedDish], flagged_names: set[str]
) -> list[PreparedDish]:
    return [dish for dish in dishes if dish.name not in flagged_names]


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

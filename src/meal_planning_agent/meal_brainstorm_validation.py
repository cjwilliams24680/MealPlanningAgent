from agents import Agent, Runner

from .llm_models import DEFAULT_MODEL
from .meal_models import MealPlanIdeas, PreparedDish
from .preferences_legacy import get_user_preferences
from .utils import BASE_SYSTEM_INSTRUCTIONS, to_markdown_list

_MEAL_VALIDATION_INSTRUCTIONS = f"""
{BASE_SYSTEM_INSTRUCTIONS}

Part of your job is inspecting menus for clients and flagging any foods that they would dislike.
Identifying violations of your client's food allergen or dietary restriction rules is your highest priority.
"""

_MEAL_FILTERING_AGENT = Agent(
    name="Meal Idea Filterer",
    instructions=_MEAL_VALIDATION_INSTRUCTIONS,
    model=DEFAULT_MODEL,
    output_type=list[str],
)


def _filter_out_flagged_dishes(
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
    flagged_foods = set((await Runner.run(_MEAL_FILTERING_AGENT, prompt)).final_output)

    # Filter out flagged foods and shuffle them to make the selection more random.
    return MealPlanIdeas(
        entree_ideas=_filter_out_flagged_dishes(meal_ideas.entree_ideas, flagged_foods),
        side_ideas=_filter_out_flagged_dishes(meal_ideas.side_ideas, flagged_foods),
    )

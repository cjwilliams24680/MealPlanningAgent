import random

from agents import Agent, RunContextWrapper, Runner, function_tool
from pydantic import BaseModel, Field

from .auth import UserMetadata
from .llm_models import DEFAULT_MODEL, GEMINI_MODEL
from .meal_brainstorm_generation import create_meal_plan_brainstorm
from .meal_models import MealPlanIdeas, PreparedDish
from .preference_models import UserPreferences
from .preferences_store import get_or_create_preferences
from .utils import BASE_SYSTEM_INSTRUCTIONS, clamp, to_markdown_list


class MealPairing(BaseModel):
    entree: PreparedDish = Field(description="main entree")
    side: PreparedDish = Field(description="side")


class MealPairingsResult(BaseModel):
    meal_pairings: list[MealPairing] = Field(description="The generated meal pairings.")


_ENTREE_PICKING_AGENT = Agent(
    name="Entree Picking Agent",
    instructions=BASE_SYSTEM_INSTRUCTIONS,
    model=DEFAULT_MODEL,
    output_type=list[PreparedDish],
)
_PAIRING_AGENT = Agent(
    name="Meal Pairing Agent",
    instructions=BASE_SYSTEM_INSTRUCTIONS,
    model=DEFAULT_MODEL,
    output_type=list[MealPairing],
)

_MEAL_CHOICE_VALIDATION_AGENT = Agent(
    name="Meal Choice Validation Agent",
    instructions=BASE_SYSTEM_INSTRUCTIONS,
    model=GEMINI_MODEL,
    output_type=bool,
)


async def _generate_meals(
    brainstorm_results: MealPlanIdeas,
    number_of_meals: int,
    user_preferences: UserPreferences,
) -> list[MealPairing]:
    attempts = 0
    while True:
        attempts += 1
        entree_choices = await _pick_entrees(
            number_of_meals=number_of_meals,
            entrees=brainstorm_results.entree_ideas,
            user_preferences=user_preferences,
        )
        meal_choices = await _pair_with_sides(
            entrees=entree_choices, sides=brainstorm_results.side_ideas
        )
        if (
            await _validate_meal_choices(
                meals=meal_choices, user_preferences=user_preferences
            )
            or attempts > 3
        ):
            return meal_choices


async def _pick_entrees(
    number_of_meals: int, entrees: list[PreparedDish], user_preferences: UserPreferences
) -> list[PreparedDish]:
    # Shuffle to make meal selection more unpredictable
    shuffled_entrees = random.sample(entrees, len(entrees))
    prompt = f"""
Your job is to pick {number_of_meals} entree(s) for the user's meal plan.

You can choose from the following list:
{to_markdown_list(shuffled_entrees)}

Make sure that your final selection conforms to the user's preferences:
{user_preferences}

Make sure that your {number_of_meals} selection(s) are different categories from each other.
"""
    return (await Runner.run(_ENTREE_PICKING_AGENT, prompt)).final_output


async def _pair_with_sides(
    entrees: list[PreparedDish], sides: list[PreparedDish]
) -> list[MealPairing]:
    # Shuffle to make meal selection more unpredictable
    shuffled_sides = random.sample(sides, len(sides))
    prompt = f"""
You're writing a meal plan for the user.

You already have the entrees picked out:
{to_markdown_list(entrees)}

Now you need to pair those entrees with sides so that you have a complete meal.

Do NOT pick a side that has the same core ingredients as the entree.
Example: Don't pair a chicken burrito bowl entree with a side of grilled chicken
skewers because chicken is a core ingredient for both.

You can choose from the following list of sides:
{to_markdown_list(shuffled_sides)}

For each entree, try to pick a side that compliments it.
This means that they should ideally share a cuisine type.
If you can't find a side with a shared cuisine type, try to find one with a similar cuisine.

The entree and side should NEVER be the same dish.
"""
    return (await Runner.run(_PAIRING_AGENT, prompt)).final_output


async def _validate_meal_choices(
    meals: list[MealPairing],
    user_preferences: UserPreferences,
) -> bool:
    prompt = f"""
You're writing a meal plan for the user.

You've picked meal(s) for the meal plan':
{to_markdown_list(meals)}

Determine if that list conforms to the user's preferences:
{user_preferences}
"""
    return (await Runner.run(_MEAL_CHOICE_VALIDATION_AGENT, prompt)).final_output


async def _generate_meal_pairings(
    number_of_meals: int,
    user_preferences: UserPreferences,
    meals_to_avoid: list[str] | None = None,
) -> list[MealPairing]:
    if meals_to_avoid is None:
        meals_to_avoid = []
    number_of_meals = clamp(number_of_meals, 1, 10)
    brainstorm_results = await create_meal_plan_brainstorm(
        number_of_entrees=number_of_meals,
        number_of_sides=number_of_meals,
        meals_to_avoid=meals_to_avoid,
        user_preferences=user_preferences,
    )
    return await _generate_meals(
        brainstorm_results=brainstorm_results,
        number_of_meals=number_of_meals,
        user_preferences=user_preferences,
    )


@function_tool(output_type=MealPairingsResult)
async def generate_initial_meal_ideas_for_meal_plan(
    wrapper: RunContextWrapper[UserMetadata],
) -> MealPairingsResult:
    """
    Generates the number of meal pairings for the user's meal plan based on the
    number stated in their preferences.

    Returns:
        A list of meal pairings for the user to review.
    """
    user_preferences = get_or_create_preferences(wrapper.context.session_id)
    meal_pairings = await _generate_meal_pairings(
        number_of_meals=user_preferences.number_of_meals_per_meal_plan,
        user_preferences=user_preferences,
    )
    return MealPairingsResult(meal_pairings=meal_pairings)


@function_tool(output_type=MealPairingsResult)
async def generate_meal_idea_replacements(
    wrapper: RunContextWrapper[UserMetadata],
    number_of_meals_to_replace: int,
    previous_meal_ideas: list[str],
) -> MealPairingsResult:
    """
    Generates an explicit number meal pairings. Used to replace any meal pairings that the user rejects.

    Args:
        number_of_meals_to_replace: The number of meal pairings to replace.
        previous_meal_ideas: The names of any meals that you have already suggested to the user.
    Returns:
        A list of meal pairings for the user to review
    """
    meal_pairings = await _generate_meal_pairings(
        number_of_meals=number_of_meals_to_replace,
        meals_to_avoid=previous_meal_ideas,
        user_preferences=get_or_create_preferences(wrapper.context.session_id),
    )
    return MealPairingsResult(meal_pairings=meal_pairings)

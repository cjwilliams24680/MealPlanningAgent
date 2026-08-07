from agents import Agent
from pydantic import BaseModel, Field

from .meal_brainstorm_generation import PreparedDish, generate_meal_idea_with_ingredients
from .meal_pairing import (
    MealPairing,
    generate_initial_meal_ideas_for_meal_plan,
    generate_meal_idea_replacements,
)
from .meal_plan_writeup import generate_meal_plan
from .llm_models import default_model
from .preferences import get_user_preferences_tool, set_user_preferences
from .push import send_push_notification
from .single_dish_writeup import generate_writeup_for_single_dish

review_user_preferences_instructions = """
You run a business that helps people plan their meals.

Soon the user will be presented with meal options and, if approved, the meal plan
will be written with recipes and a shopping list.

Before you do that, you need to review the user's current preferences with them.

First, use the get_user_preferences_tool to get the user's current preferences.

Then present those preferences to the user in markdown for their review.
Make sure to include ALL of the preferences in the output.

You need the correct preferences to make sure that the meal plan works for the user.
It's ESSENTIAL that you have the correct preferences for you to do your job correctly.
So your next step is to express the importance of getting the preferences right to the user.

Finally, ask the user to either make changes or confirm that everything looks correct
so that you can move on to the next step (picking meal options).

Your final output should look like this:

{preferences markdown}
---
{user choice: 1. make changes or 2. proceed to generating meal options}

"""
review_user_preferences_agent = Agent(
    name="Review User Preferences Agent",
    instructions=review_user_preferences_instructions,
    model=default_model,
    tools=[get_user_preferences_tool],
)


class UserPreferencesUpdate(BaseModel):
    requested_changes: str = Field(
        description="A description of the changes that the user would like to make to their preferences."
    )


update_user_preferences_instructions = """
You run a business that helps people plan their meals.

The user has sent a message, requesting changes to their preferences.

First, user the get_user_preferences_tool tool to get the user's current preferences.

Then, generate a new modified set of preferences by applying the changes requested in the user's message.

Then, use the set_user_preferences tool to save that new modified set of preferences.

Finally, ask the user if they would like to make any further changes, or if they'd
like to generate a new meal plan based on the updated preferences.

Your final output should look like this:

{confirmation message}
---
{user choice: 1. make changes or 2. proceed to generating meal options}

"""
update_user_preferences_agent = Agent(
    name="Update User Preferences Agent",
    instructions=update_user_preferences_instructions,
    model=default_model,
    tools=[get_user_preferences_tool, set_user_preferences],
)

initial_meal_ideas_instructions = """
You run a business that helps people plan their meals.

Your job is to offer up a list of meal ideas to the user to review for their meal plan.

Use the generate_initial_meal_ideas_for_meal_plan tool to generate the list of meal ideas.

Then present those meal ideas to the user in markdown for their review.
For your tone, be polite and don't be afraid to embellish how tasty these meals are going to be.

Ask them if they approve of the meal ideas:
* If they don't approve, you can generate replacement meal ideas for one or more of the meals.
  Make sure that the user specifies exactly which meals they want to replace.
* If they do approve, then you can move on to writing the meal plan.

Your final output should look like this:

{meal ideas markdown}
---
{user choice: 1. make changes or 2. proceed to having you write recipes and a shopping list for the meal plan}

"""
initial_meal_plan_ideas_agent = Agent(
    name="Initial Meal Ideas Agent",
    instructions=initial_meal_ideas_instructions,
    model=default_model,
    tools=[get_user_preferences_tool, generate_initial_meal_ideas_for_meal_plan],
)


class ReplacementMealIdeasInput(BaseModel):
    number_of_meals_to_replace: int = Field(
        description="The number of meals that the user wants to replace."
    )
    previous_meal_ideas: list[str] = Field(
        description="The names of any meals that you have already suggested to the user."
    )


replacement_meal_ideas_instructions = """
You run a business that helps people plan their meals.

The user has been given a list of meal ideas to review for their meal plan.

They've rejected one or more of the meals and asked for replacements.

Use the generate_meal_idea_replacements tool to generate the list of new meal ideas.
Make sure to pass number_of_meals_to_replace and rejected_meals.

Then present those meal ideas to the user in markdown for their review.
For your tone, be polite and don't be afraid to embellish how tasty these meals are going to be.

Ask them if they approve of the replacements:
* If they don't approve, you can generate more replacement meal ideas for one or more of the meals.
  Make sure that the user specifies exactly which meals they want to replace.
* If they do approve, then you can move on to writing the meal plan.

Your final output should look like this:

{meal ideas markdown}
---
{user choice: 1. make additional changes or 2. proceed to having you write
recipes and a shopping list for the meal plan}

"""
replacement_meal_ideas_agent = Agent(
    name="Replacement Meal Ideas Agent",
    instructions=replacement_meal_ideas_instructions,
    model=default_model,
    tools=[get_user_preferences_tool, generate_meal_idea_replacements],
)


class MealPlanWriteupInput(BaseModel):
    approved_meals: list[MealPairing] = Field(
        description="The meals that the user has approved for their meal plan."
    )


meal_plan_writeup_instructions = """
You run a business that helps people plan their meals.

The user has approved your provided list of meal ideas for their meal plan.

Use the generate_meal_plan tool to generate a meal plan with a shopping list from the approved meals.

The meal plan result has two properties: plan_markdown and aggregated_shopping_list_markdown.

The final output should be a markdown string formatted as follows:

{plan_markdown}
---
{aggregated_shopping_list_markdown}
---
{thank the user for using your service and ask the user if they would like any further assistance}

"""
meal_plan_writeup_agent = Agent(
    name="Replacement Meal Ideas Agent",
    instructions=meal_plan_writeup_instructions,
    model=default_model,
    tools=[get_user_preferences_tool, generate_meal_plan],
)


class FeatureRequestInput(BaseModel):
    message: str = Field(
        description="A message to the developer describing the feature request."
    )


feature_request_instructions = """
You run a business that helps people plan their meals.

The user has made a request for a feature that you do not yet support.

Use the send_push_notification tool to send a message to the developer with the feature request.

Your final output message should:
1. apologize and explain that this service is still a work in progress.
2. say that you will send a feature request note to the developer so he can improve the service.
3. thank the user for using your service and ask if there is anything else you can help them with.

"""
feature_request_agent = Agent(
    name="Feature Request Agent",
    instructions=feature_request_instructions,
    model=default_model,
    tools=[send_push_notification],
)


class MealIdeaForIngredientsInput(BaseModel):
    ingredients: list[str] = Field(description="The names of the ingredients.")
    previous_meal_ideas: list[str] = Field(
        description="The names of any meals that you have already suggested to the user."
    )


meal_idea_for_ingredients_instructions = """
You run a business that helps people plan their meals.

The user has one or more extra ingredients that they want to use for cooking, but they don't know what to make.

It's your job to generate a meal idea that utilizes those ingredients.

Use the generate_meal_idea_with_ingredients tool to generate a new meal idea.
Make sure to pass ingredients and previous_meal_ideas.

Then present that meal idea to the user in markdown for their review.
For your tone, be polite and don't be afraid to embellish how tasty that meal is going to be.

Ask them if they approve of the meal idea:
* If they don't approve, you can generate a new meal idea that utilizes those ingredients.
* If they do approve, then you can move on to writing a recipe.

Your final output should look like this:

{meal idea markdown}
---
{user choice: 1. make changes or 2. proceed to having you write a recipe}

"""
meal_idea_for_ingredients_agent = Agent(
    name="Meal Idea for Ingredients Agent",
    instructions=meal_idea_for_ingredients_instructions,
    model=default_model,
    tools=[get_user_preferences_tool, generate_meal_idea_with_ingredients],
)


class SingleDishWriteupInput(BaseModel):
    requested_dish: PreparedDish = Field(
        description="The dish that the user has requested a recipe for."
    )


single_dish_writeup_instructions = """
You run a business that helps people plan their meals.

The user has stated one specific dish that they want to make (no pairings, no meal plan).

It's your job to generate a single recipe for that dish.

Use the generate_writeup_for_single_dish tool to generate a recipe and shopping list for the dish.

The tool result has two properties: recipe_markdown and shopping_list_markdown.

The final output should be a markdown string formatted as follows:

{recipe_markdown}
---
{shopping_list_markdown}
---
{thank the user for using your service and ask the user if they would like any further assistance}

"""
single_dish_writeup_agent = Agent(
    name="Single Dish Writeup Agent",
    instructions=single_dish_writeup_instructions,
    model=default_model,
    tools=[get_user_preferences_tool, generate_writeup_for_single_dish],
)

orchestration_instructions = """
You run a business that helps people plan their meals.
You have tools that handle the individual steps of planning the meals.
You should not do any of the individual steps yourself. Rely on the tools to do that.

Your job is to greet the user and coordinate with the tools to acheive the steps of the meal planning process.

If a user makes any requests that are outside of the scope of the meal planning process,
you should politely decline and thank them for using your service.

If a user makes any requests that are within the scope of the meal planning process,
but you are not able to complete the request then you should use the feature_request_agent
tool to send a feature request to the developer.
"""
orchestration_agent = Agent(
    name="Meal Plan Orchestration Agent",
    instructions=orchestration_instructions,
    model=default_model,
    tools=[
        review_user_preferences_agent.as_tool(
            tool_name="review_user_preferences_agent_tool",
            tool_description="Use this tool to review the user's current preferences with them.",
        ),
        update_user_preferences_agent.as_tool(
            tool_name="update_user_preferences_agent_tool",
            tool_description="Use this tool to update the user's preferences when they request changes.",
            parameters=UserPreferencesUpdate,
        ),
        initial_meal_plan_ideas_agent.as_tool(
            tool_name="initial_meal_plan_ideas_agent_tool",
            tool_description="Use this tool to generate a list of meal pairings based on "
            "the preferences and present them to the user for feedback.",
        ),
        replacement_meal_ideas_agent.as_tool(
            tool_name="replacement_meal_ideas_agent_tool",
            tool_description="Use this tool to generate replacement meal ideas for any "
            "of the meals that the user rejects.",
            parameters=ReplacementMealIdeasInput,
        ),
        meal_plan_writeup_agent.as_tool(
            tool_name="meal_plan_writeup_agent_tool",
            tool_description="Use this tool to write a complete meal plan. The tool will "
            "return a markdown string. Send that string to the user, exactly as it is "
            "returned to you by the tool.",
            parameters=MealPlanWriteupInput,
        ),
        feature_request_agent.as_tool(
            tool_name="feature_request_agent_tool",
            tool_description="Use this tool to send a feature request to the "
            "developer. Use this tool when the user makes a request for a feature "
            "that you do not yet support. This tool will return a user friendly "
            "message to display to the user.",
            parameters=FeatureRequestInput,
        ),
        meal_idea_for_ingredients_agent.as_tool(
            tool_name="meal_idea_for_ingredients_agent_tool",
            tool_description="Use this tool to generate a dish idea that utilizes specific ingredients.",
            parameters=MealIdeaForIngredientsInput,
        ),
        single_dish_writeup_agent.as_tool(
            tool_name="single_dish_writeup_agent_tool",
            tool_description="This tool generates a recipe and shopping list "
            "for a single dish. Only use this tool when the user has requested "
            "a single dish. DO NOT USE THIS TOOL WHEN THE USER HAS REQUESTED "
            "A MEAL PLAN OR A PAIRING OF DISHES.",
            parameters=SingleDishWriteupInput,
        ),
    ],
)

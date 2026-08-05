from agents import Agent    
from pydantic import BaseModel, Field
from .models import default_model
from .preferences import get_user_preferences_tool, set_user_preferences
from .meal_pairing import generate_initial_meal_ideas_for_meal_plan, generate_meal_idea_replacements
from .meal_plan_writeup import generate_meal_plan
from .meal_pairing import MealPairing

review_user_preferences_instructions = '''
You run a business that helps people plan their meals.

Soon the user will be presented with meal options and, if approved, the meal plan will be written with recipes and a shopping list.

Before you do that, you need to review the user's current preferences with them.

First, use the get_user_preferences_tool to get the user's current preferences.

Then present those preferences to the user in markdown for their review. Make sure to include ALL of the preferences in the output.

You need the correct preferences to make sure that the meal plan works for the user. 
It's ESSENTIAL that you have the correct preferences for you to do your job correctly.
So your next step is to express the importance of getting the preferences right to the user.

Finally, ask the user to either make changes or confirm that everything looks correct so that you can move on to the next step (picking meal options).
'''
review_user_preferences_agent = Agent(
    name="Review User Preferences Agent",
    instructions=review_user_preferences_instructions,
    model=default_model,
    tools=[get_user_preferences_tool],
)

class UserPreferencesUpdate(BaseModel):
    requested_changes: str = Field(description="A description of the changes that the user would like to make to their preferences.")

update_user_preferences_instructions = '''
You run a business that helps people plan their meals.

The user has sent a message, requesting changes to their preferences.

First, user the get_user_preferences_tool tool to get the user's current preferences.

Then, generate a new modified set of preferences by applying the changes requested in the user's message.

Then, use the set_user_preferences tool to save that new modified set of preferences.

Finally, ask the user if they would like to make any further changes, or if they'd like to generate a new meal plan based on the updated preferences.
'''
update_user_preferences_agent = Agent(
    name="Update User Preferences Agent",
    instructions=update_user_preferences_instructions,
    model=default_model,
    tools=[get_user_preferences_tool, set_user_preferences],
)

initial_meal_ideas_instructions = '''
You run a business that helps people plan their meals.

Your job is to offer up a list of meal ideas to the user to review for their meal plan.

Use the generate_initial_meal_ideas_for_meal_plan tool to generate the list of meal ideas.

Then present those meal ideas to the user in markdown for their review. 
For your tone, be polite and don't be afraid to embellish how tasty these meals are going to be. 

Ask them if they approve of the meal ideas:
* If they don't approve, you can generate replacement meal ideas for one or more of the meals. Make sure that the user specifies exactlywhich meals they want to replace.
* If they do approve, then you can move on to writing the meal plan.
'''
initial_meal_ideas_agent = Agent(
    name="Initial Meal Ideas Agent",
    instructions=initial_meal_ideas_instructions,
    model=default_model,
    tools=[get_user_preferences_tool, generate_initial_meal_ideas_for_meal_plan],
)

class ReplacementMealIdeasInput(BaseModel):
    number_of_meals_to_replace: int = Field(description="The number of meals that the user wants to replace.")
    rejected_meals: list[str] = Field(description="The names of the meals that the user rejected and wants to replace.")

replacement_meal_ideas_instructions = '''
You run a business that helps people plan their meals.

The user has been given a list of meal ideas to review for their meal plan.

They've rejected one or more of the meals and asked for replacements.

Use the generate_meal_idea_replacements tool to generate the list of new meal ideas. Make sure to pass number_of_meals_to_replace and rejected_meals.

Then present those meal ideas to the user in markdown for their review. 
For your tone, be polite and don't be afraid to embellish how tasty these meals are going to be.

Ask them if they approve of the replacements:
* If they don't approve, you can generate more replacement meal ideas for one or more of the meals. Make sure that the user specifies exactlywhich meals they want to replace.
* If they do approve, then you can move on to writing the meal plan.
'''
replacement_meal_ideas_agent = Agent(
    name="Replacement Meal Ideas Agent",
    instructions=replacement_meal_ideas_instructions,
    model=default_model,
    tools=[get_user_preferences_tool, generate_meal_idea_replacements],
)

class MealPlanWriteupInput(BaseModel):
    approved_meals: list[MealPairing] = Field(description="The meals that the user has approved for their meal plan.")

meal_plan_writeup_instructions = '''
You run a business that helps people plan their meals.

The user has approved your provided list of meal ideas for their meal plan.

Use the generate_meal_plan tool to generate a meal plan with a shopping list from the approved meals.

The meal plan result has two properties: plan_markdown and shopping_list_markdown.

Share the plan_markdown with the user.

Share the shopping_list_markdown with the user.
'''
meal_plan_writeup_agent = Agent(
    name="Replacement Meal Ideas Agent",
    instructions=meal_plan_writeup_instructions,
    model=default_model,
    tools=[get_user_preferences_tool, generate_meal_plan],
)

orchestration_instructions = f'''
You run a business that helps people plan their meals.
You have tools that handle the individual steps of planning the meals.
You should not do any of the individual steps yourself. Rely on the tools to do that.

Your job is to greet the user and coordinate with the tools to acheive the steps of the meal planning process.

A typical workflow for meal planning looks like this:
1. Review User Preferences: Review the user's current preferences with them.
2. (Optional) User Preferences Updates: Update the user's preferences based on their feedback.
3. Initial Meal Pairings: Generate a list of meal pairings based on the preferences and present them to the user for feedback.
4. (Optional) Meal Pairings Modifications: Generate new replacement meal pairings for any of the meals that the user rejects.
5. Writing the Meal Plan: Write a complete meal plan with a shopping list based on the approved meal pairings.
'''
orchestration_agent = Agent(
    name="Meal Plan Orchestration Agent",
    instructions=orchestration_instructions,
    model=default_model,
    tools=[
        review_user_preferences_agent.as_tool(
            tool_name = "review_user_preferences_agent_tool",
            tool_description = "Use this tool to review the user's current preferences with them.",
        ),
        update_user_preferences_agent.as_tool(
            tool_name = "update_user_preferences_agent_tool",
            tool_description = "Use this tool to update the user's preferences when they request changes.",
            parameters = UserPreferencesUpdate,
        ),
        initial_meal_ideas_agent.as_tool(
            tool_name = "initial_meal_ideas_agent_tool",
            tool_description = "Use this tool to generate a list of meal pairings based on the preferences and present them to the user for feedback.",
        ),
        replacement_meal_ideas_agent.as_tool(
            tool_name = "replacement_meal_ideas_agent_tool",
            tool_description = "Use this tool to generate replacement meal ideas for any of the meals that the user rejects.",
            parameters = ReplacementMealIdeasInput,
        ),
        meal_plan_writeup_agent.as_tool(
            tool_name = "meal_plan_writeup_agent_tool",
            tool_description = "Use this tool to write a complete meal plan with a shopping list based on the approved meal pairings.",
            parameters = MealPlanWriteupInput,
        ),
    ],
)


from sqlmodel import Field, SQLModel


class UserPreferencesBase(SQLModel):
    number_of_meals_per_meal_plan: int = Field(
        default=2,
        description="The number of meals that you should plan.",
        ge=1,
        le=10,
    )
    number_of_servings_portions_per_meal: int = Field(
        default=4,
        description="Determines how many serving portions we should make for each meal.",
        ge=1,
        le=100,
    )
    dietary_restrictions: str = Field(
        description="""A list of any dietary restrictions the user has that need to be considered for the meal plan.
Examples: Gluten-free, vegetarian, dairy-free""",
    )
    likes: str = Field(description="A list of foods user's favorite foods.")
    dislikes: str = Field(
        default="", description="A list of foods that the user does not like."
    )
    nutritional_goals: str = Field(
        default="",
        description="""A description of the nutritional goals that the user aims to achieve with this meal plan.
Examples: Increase protein intake, lose weight, lower cholesterol""",
    )
    preferred_cooking_methods: str = Field(
        default="oven, stovetop, microwave",
        description="""When cooking is required, these are the user's preferred methods.
Examples: oven, stovetop, microwave, grill""",
    )
    notes: str = Field(
        default="",
        description="""A paragraph of notes about any preferences that don't apply to one of the other fields.
Example: Half of my meals should be meatless.""",
    )


class UserPreferences(UserPreferencesBase, table=True):
    __tablename__: str = "preferences"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(unique=True)

from .recipe_models import Ingredient, MealPlanItem, grocery_departments


def get_consolidated_ingredients(meal_plan: list[MealPlanItem]) -> list[Ingredient]:
    """
    Extracts all ingredients and sums the quantities of items
    with the same name and unit.
    """
    totals = {}  # Key: (name, unit, department), Value: total_quantity

    for item in meal_plan:
        # Helper to process recipe lists
        recipe_ingredients = (
            item.entree_recipe.ingredients + item.side_recipe.ingredients
        )

        for ing in recipe_ingredients:
            # Create a unique key based on name and unit
            # We use lower() to ensure "Garlic" and "garlic" match
            key = (ing.name.lower(), ing.unit.lower(), ing.grocery_store_department)

            if key in totals:
                totals[key] += ing.quantity
            else:
                totals[key] = ing.quantity

    # Convert the dictionary back into a list of Ingredient objects
    consolidated = [
        Ingredient(
            name=name.title(),
            unit=unit.title(),
            quantity=qty,
            grocery_store_department=dept,
        )
        for (name, unit, dept), qty in totals.items()
    ]

    return consolidated


def sort_ingredients(ingredients: list[Ingredient]) -> list[Ingredient]:
    order_map = {dept: i for i, dept in enumerate(grocery_departments)}

    def sorting_key(item: Ingredient):
        # Primary key: the index from our map.
        # .get() handles cases where a department might not be in the list (defaults to the end)
        department_rank = order_map.get(
            item.grocery_store_department, len(grocery_departments)
        )

        # Secondary key: the name (alphabetical)
        return (department_rank, item.name.lower())

    return sorted(ingredients, key=sorting_key)


def generate_ingredients_markdown(ingredients: list[Ingredient]) -> str:
    """
    Takes a sorted list of Ingredient objects and returns a
    Markdown-formatted string grouped by department.
    """
    lines = ["# Grocery List"]
    current_dept = None

    for item in ingredients:
        # Check if we have moved to a new department
        if item.grocery_store_department != current_dept:
            current_dept = item.grocery_store_department
            # Add an extra newline for spacing between sections
            lines.append(f"\n## {current_dept}")

        # Add the checklist item
        # :g format removes trailing zeros (e.g., 1.0 -> 1)
        lines.append(f"- [ ] {item.quantity:g} {item.unit} {item.name}")

    return "\n".join(lines)

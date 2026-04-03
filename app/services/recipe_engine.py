from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence

from app.models import MealPlan, MealPlanDay, RecipeSuggestion


@dataclass(frozen=True)
class RecipeTemplate:
    title: str
    required: Sequence[str]
    optional: Sequence[str]
    steps: Sequence[str]
    estimated_minutes: int


RECIPE_LIBRARY: List[RecipeTemplate] = [
    RecipeTemplate(
        title="Spinach Omelet",
        required=["eggs", "spinach"],
        optional=["cheese", "onion"],
        steps=[
            "Whisk eggs with salt and pepper.",
            "Saute spinach (and onion if available).",
            "Add eggs and cook until just set.",
            "Top with cheese and fold.",
        ],
        estimated_minutes=12,
    ),
    RecipeTemplate(
        title="Veggie Scramble",
        required=["eggs", "tomato"],
        optional=["bell pepper", "onion", "cheese"],
        steps=[
            "Dice vegetables.",
            "Cook vegetables in a pan for 3-4 minutes.",
            "Add beaten eggs and stir gently.",
            "Finish with cheese if available.",
        ],
        estimated_minutes=15,
    ),
    RecipeTemplate(
        title="Chicken & Broccoli Skillet",
        required=["chicken", "broccoli"],
        optional=["butter", "onion"],
        steps=[
            "Slice chicken and season.",
            "Cook chicken until fully done.",
            "Add broccoli and a splash of water.",
            "Stir in butter and cook until tender-crisp.",
        ],
        estimated_minutes=20,
    ),
    RecipeTemplate(
        title="Fresh Garden Salad",
        required=["lettuce", "cucumber", "tomato"],
        optional=["carrot", "cheese", "onion"],
        steps=[
            "Chop vegetables.",
            "Combine in a bowl and toss.",
            "Add cheese and dressing if desired.",
        ],
        estimated_minutes=10,
    ),
]


def suggest_recipes(items: Sequence[str], max_results: int = 5) -> List[RecipeSuggestion]:
    pantry = set(items)
    suggestions: List[RecipeSuggestion] = []

    ranked = sorted(
        RECIPE_LIBRARY,
        key=lambda r: (
            sum(1 for ingredient in r.required if ingredient in pantry),
            sum(1 for ingredient in r.optional if ingredient in pantry),
        ),
        reverse=True,
    )

    for recipe in ranked:
        used = [i for i in [*recipe.required, *recipe.optional] if i in pantry]
        missing = [i for i in recipe.required if i not in pantry]

        if len(used) == 0:
            continue

        suggestions.append(
            RecipeSuggestion(
                title=recipe.title,
                ingredients_used=used,
                missing_ingredients=missing,
                steps=list(recipe.steps),
                estimated_minutes=recipe.estimated_minutes,
            )
        )

        if len(suggestions) >= max_results:
            break

    return suggestions


def build_meal_plan(items: Sequence[str], days: int = 5) -> MealPlan:
    recipes = suggest_recipes(items, max_results=max(days, 3))
    if not recipes:
        recipes = [
            RecipeSuggestion(
                title="Pantry Stir Fry",
                ingredients_used=list(items),
                missing_ingredients=[],
                steps=["Saute what you have and season to taste."],
                estimated_minutes=20,
            )
        ]

    plan_days: List[MealPlanDay] = []
    labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    for idx in range(days):
        base = recipes[idx % len(recipes)].title
        alt1 = recipes[(idx + 1) % len(recipes)].title
        alt2 = recipes[(idx + 2) % len(recipes)].title

        plan_days.append(
            MealPlanDay(
                day=labels[idx % len(labels)],
                breakfast=f"{base} (smaller portion)",
                lunch=alt1,
                dinner=alt2,
            )
        )

    return MealPlan(days=plan_days)

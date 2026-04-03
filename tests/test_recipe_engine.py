import unittest

from app.services.recipe_engine import build_meal_plan, suggest_recipes


class RecipeEngineTests(unittest.TestCase):
    def test_suggest_recipes_returns_matches(self) -> None:
        recipes = suggest_recipes(["eggs", "spinach", "cheese"])
        self.assertGreaterEqual(len(recipes), 1)
        self.assertEqual(recipes[0].title, "Spinach Omelet")

    def test_meal_plan_has_requested_days(self) -> None:
        meal_plan = build_meal_plan(["eggs", "spinach"], days=4)
        self.assertEqual(len(meal_plan.days), 4)


if __name__ == "__main__":
    unittest.main()

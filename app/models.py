from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field


class ScanResult(BaseModel):
    items: List[str] = Field(default_factory=list)
    confidence: float = 0.0
    raw_labels: List[str] = Field(default_factory=list)


class RecipeSuggestion(BaseModel):
    title: str
    ingredients_used: List[str]
    missing_ingredients: List[str]
    steps: List[str]
    estimated_minutes: int


class MealPlanDay(BaseModel):
    day: str
    breakfast: str
    lunch: str
    dinner: str


class MealPlan(BaseModel):
    days: List[MealPlanDay]

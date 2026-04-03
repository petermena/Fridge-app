from __future__ import annotations

from fastapi import FastAPI, File, HTTPException, UploadFile

from app.models import MealPlan, RecipeSuggestion, ScanResult
from app.services.image_scanner import scan_fridge_image
from app.services.recipe_engine import build_meal_plan, suggest_recipes

app = FastAPI(title="Fridge AI", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/scan", response_model=ScanResult)
async def scan(file: UploadFile = File(...)) -> ScanResult:
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Please upload an image file.")

    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    return scan_fridge_image(data)


@app.post("/recipes", response_model=list[RecipeSuggestion])
def recipes(items: list[str]) -> list[RecipeSuggestion]:
    if not items:
        raise HTTPException(status_code=400, detail="Provide at least one item.")
    return suggest_recipes(items)


@app.post("/meal-plan", response_model=MealPlan)
def meal_plan(items: list[str], days: int = 5) -> MealPlan:
    if days < 1 or days > 14:
        raise HTTPException(status_code=400, detail="days must be between 1 and 14")
    return build_meal_plan(items, days)

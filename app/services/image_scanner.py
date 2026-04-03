from __future__ import annotations

import base64
import os
from typing import List

from app.models import ScanResult


COMMON_FRIDGE_ITEMS = {
    "milk",
    "eggs",
    "cheese",
    "spinach",
    "tomato",
    "onion",
    "bell pepper",
    "broccoli",
    "chicken",
    "ground beef",
    "yogurt",
    "butter",
    "lettuce",
    "carrot",
    "apple",
    "orange",
    "strawberry",
    "cucumber",
    "mushroom",
}


def _normalize_label(label: str) -> str:
    label = label.lower().strip()
    aliases = {
        "egg": "eggs",
        "tomatoes": "tomato",
        "peppers": "bell pepper",
        "capsicum": "bell pepper",
    }
    return aliases.get(label, label)


def _fallback_detect_items(image_bytes: bytes) -> ScanResult:
    """
    Fallback detector used when no vision provider API key is present.
    It returns a conservative starter list so the product can be tested end-to-end.
    """
    _ = image_bytes
    sample_items = ["eggs", "milk", "spinach", "cheese", "tomato"]
    return ScanResult(items=sample_items, confidence=0.42, raw_labels=sample_items)


def scan_fridge_image(image_bytes: bytes) -> ScanResult:
    """
    If OPENAI_API_KEY is available, call OpenAI vision to detect fridge items.
    Otherwise, run a local fallback that returns a starter list.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return _fallback_detect_items(image_bytes)

    # Deferred import so local dev can run without OpenAI dependency.
    from openai import OpenAI  # type: ignore

    client = OpenAI(api_key=api_key)
    encoded = base64.b64encode(image_bytes).decode("utf-8")

    prompt = (
        "Identify visible food items in this fridge image. "
        "Return a comma-separated list of common grocery item names only."
    )

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=[
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": prompt},
                    {
                        "type": "input_image",
                        "image_url": f"data:image/jpeg;base64,{encoded}",
                    },
                ],
            }
        ],
    )

    text = response.output_text or ""
    labels = [token.strip() for token in text.split(",") if token.strip()]

    items: List[str] = []
    for label in labels:
        normalized = _normalize_label(label)
        if normalized in COMMON_FRIDGE_ITEMS:
            items.append(normalized)

    unique_items = sorted(set(items))
    confidence = 0.85 if unique_items else 0.3
    return ScanResult(items=unique_items, confidence=confidence, raw_labels=labels)

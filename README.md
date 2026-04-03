# Fridge AI (Backend + iPhone starter)

You now have:

1. A FastAPI backend that scans a fridge photo, suggests recipes, and builds a meal plan.
2. A SwiftUI iPhone starter client that calls this backend.

## Backend quickstart

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open API docs at: `http://127.0.0.1:8000/docs`

## Backend endpoints

- `GET /health`
- `POST /scan` (multipart image upload)
- `POST /recipes` (JSON array of item names)
- `POST /meal-plan?days=5` (JSON array of item names)

---

## How to make this an iPhone app

### 1) Create an Xcode iOS app shell

- Open Xcode → **Create New Project** → **App**.
- Name it `FridgeAI`.
- Interface: **SwiftUI**.
- Language: **Swift**.
- Minimum iOS target: **16+** (for `PhotosPicker`).

### 2) Copy starter files from this repo

Copy these files into your Xcode project (replace default template files):

- `ios/FridgeAI/FridgeAIApp.swift`
- `ios/FridgeAI/ContentView.swift`
- `ios/FridgeAI/APIClient.swift`
- `ios/FridgeAI/Models.swift`

The flow in `ContentView` is:
1. pick a fridge photo,
2. upload to `/scan`,
3. call `/recipes`,
4. call `/meal-plan`,
5. render results.

### 3) Allow photo library access

In your iOS target `Info` settings, add:
- `Privacy - Photo Library Usage Description`

Suggested value:
> "We use your selected fridge photo to detect ingredients and suggest meals."

### 4) Point iPhone app to your backend

In `ios/FridgeAI/APIClient.swift`, update `baseURL` as needed:

- **Simulator:** `http://127.0.0.1:8000` works when backend runs on same Mac.
- **Physical iPhone:** use your Mac LAN IP, e.g. `http://192.168.1.20:8000`.

### 5) Run end-to-end

1. Start backend with `uvicorn app.main:app --reload`.
2. Run iOS app from Xcode (simulator/device).
3. Pick a fridge photo.
4. Verify detected items, recipes, and meal plan appear.

---

## Current architecture

- `app/main.py` – API routes.
- `app/models.py` – shared response models.
- `app/services/image_scanner.py` – image scan service (OpenAI vision if key exists, fallback otherwise).
- `app/services/recipe_engine.py` – recipe ranking + meal plan generation.
- `ios/FridgeAI/*` – SwiftUI iPhone client starter.

## Recommended next iOS improvements

- Add camera capture with `UIImagePickerController`/`PHPicker` wrapper.
- Add item edit screen so users can fix detection errors.
- Cache last pantry in local storage.
- Add auth and save weekly plans per user.
- Add grocery-list generation from `missing_ingredients`.

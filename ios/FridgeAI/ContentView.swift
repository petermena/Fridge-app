import PhotosUI
import SwiftUI

struct ContentView: View {
    @State private var selectedPhoto: PhotosPickerItem?
    @State private var scanResult: ScanResult?
    @State private var recipes: [RecipeSuggestion] = []
    @State private var mealPlan: MealPlan?
    @State private var isLoading = false
    @State private var errorMessage: String?

    private let api = APIClient()

    var body: some View {
        NavigationStack {
            Form {
                Section("1) Pick a fridge photo") {
                    PhotosPicker("Select Photo", selection: $selectedPhoto, matching: .images)
                        .onChange(of: selectedPhoto) { _, newValue in
                            guard let newValue else { return }
                            Task { await process(photo: newValue) }
                        }
                }

                if let scanResult {
                    Section("Detected items") {
                        Text(scanResult.items.joined(separator: ", "))
                        Text("Confidence: \(Int(scanResult.confidence * 100))%")
                            .foregroundStyle(.secondary)
                    }
                }

                if !recipes.isEmpty {
                    Section("Recipe ideas") {
                        ForEach(recipes) { recipe in
                            VStack(alignment: .leading, spacing: 6) {
                                Text(recipe.title).font(.headline)
                                Text("Uses: \(recipe.ingredientsUsed.joined(separator: ", "))")
                                    .font(.subheadline)
                                if !recipe.missingIngredients.isEmpty {
                                    Text("Missing: \(recipe.missingIngredients.joined(separator: ", "))")
                                        .font(.footnote)
                                        .foregroundStyle(.orange)
                                }
                            }
                            .padding(.vertical, 4)
                        }
                    }
                }

                if let mealPlan {
                    Section("5-day meal plan") {
                        ForEach(mealPlan.days) { day in
                            VStack(alignment: .leading, spacing: 4) {
                                Text(day.day).font(.headline)
                                Text("Breakfast: \(day.breakfast)")
                                Text("Lunch: \(day.lunch)")
                                Text("Dinner: \(day.dinner)")
                            }
                            .padding(.vertical, 4)
                        }
                    }
                }

                if let errorMessage {
                    Section("Error") {
                        Text(errorMessage).foregroundStyle(.red)
                    }
                }
            }
            .navigationTitle("Fridge AI")
            .overlay {
                if isLoading {
                    ProgressView("Analyzing your fridge...")
                        .padding()
                        .background(.ultraThinMaterial)
                        .clipShape(RoundedRectangle(cornerRadius: 12))
                }
            }
        }
    }

    @MainActor
    private func process(photo: PhotosPickerItem) async {
        isLoading = true
        errorMessage = nil
        defer { isLoading = false }

        do {
            guard let data = try await photo.loadTransferable(type: Data.self) else {
                throw APIError.server("Could not read selected image data")
            }

            let scanned = try await api.scanFridge(imageData: data)
            let recipeSuggestions = try await api.fetchRecipes(items: scanned.items)
            let suggestedPlan = try await api.fetchMealPlan(items: scanned.items, days: 5)

            scanResult = scanned
            recipes = recipeSuggestions
            mealPlan = suggestedPlan
        } catch {
            errorMessage = error.localizedDescription
        }
    }
}

#Preview {
    ContentView()
}

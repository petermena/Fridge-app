import Foundation

struct ScanResult: Codable {
    let items: [String]
    let confidence: Double
    let rawLabels: [String]

    enum CodingKeys: String, CodingKey {
        case items
        case confidence
        case rawLabels = "raw_labels"
    }
}

struct RecipeSuggestion: Codable, Identifiable {
    let id = UUID()
    let title: String
    let ingredientsUsed: [String]
    let missingIngredients: [String]
    let steps: [String]
    let estimatedMinutes: Int

    enum CodingKeys: String, CodingKey {
        case title
        case ingredientsUsed = "ingredients_used"
        case missingIngredients = "missing_ingredients"
        case steps
        case estimatedMinutes = "estimated_minutes"
    }
}

struct MealPlan: Codable {
    let days: [MealPlanDay]
}

struct MealPlanDay: Codable, Identifiable {
    let id = UUID()
    let day: String
    let breakfast: String
    let lunch: String
    let dinner: String
}

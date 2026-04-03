import Foundation

final class APIClient {
    /// For iOS simulator talking to backend running on your Mac.
    /// If testing on a physical iPhone, replace with your Mac's LAN IP.
    private let baseURL = URL(string: "http://127.0.0.1:8000")!

    func scanFridge(imageData: Data) async throws -> ScanResult {
        let url = baseURL.appendingPathComponent("scan")
        var request = URLRequest(url: url)
        request.httpMethod = "POST"

        let boundary = "Boundary-\(UUID().uuidString)"
        request.setValue("multipart/form-data; boundary=\(boundary)", forHTTPHeaderField: "Content-Type")

        var body = Data()
        body.appendString("--\(boundary)\r\n")
        body.appendString("Content-Disposition: form-data; name=\"file\"; filename=\"fridge.jpg\"\r\n")
        body.appendString("Content-Type: image/jpeg\r\n\r\n")
        body.append(imageData)
        body.appendString("\r\n--\(boundary)--\r\n")

        request.httpBody = body
        let (data, response) = try await URLSession.shared.data(for: request)
        try validate(response: response, data: data)

        return try JSONDecoder().decode(ScanResult.self, from: data)
    }

    func fetchRecipes(items: [String]) async throws -> [RecipeSuggestion] {
        let url = baseURL.appendingPathComponent("recipes")
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try JSONEncoder().encode(items)

        let (data, response) = try await URLSession.shared.data(for: request)
        try validate(response: response, data: data)

        return try JSONDecoder().decode([RecipeSuggestion].self, from: data)
    }

    func fetchMealPlan(items: [String], days: Int = 5) async throws -> MealPlan {
        var components = URLComponents(url: baseURL.appendingPathComponent("meal-plan"), resolvingAgainstBaseURL: false)!
        components.queryItems = [URLQueryItem(name: "days", value: String(days))]

        var request = URLRequest(url: components.url!)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try JSONEncoder().encode(items)

        let (data, response) = try await URLSession.shared.data(for: request)
        try validate(response: response, data: data)

        return try JSONDecoder().decode(MealPlan.self, from: data)
    }

    private func validate(response: URLResponse, data: Data) throws {
        guard let http = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }

        guard (200...299).contains(http.statusCode) else {
            let message = String(data: data, encoding: .utf8) ?? "Unknown server error"
            throw APIError.server(message)
        }
    }
}

enum APIError: LocalizedError {
    case invalidResponse
    case server(String)

    var errorDescription: String? {
        switch self {
        case .invalidResponse:
            return "Invalid response from server."
        case .server(let message):
            return message
        }
    }
}

private extension Data {
    mutating func appendString(_ string: String) {
        if let data = string.data(using: .utf8) {
            append(data)
        }
    }
}

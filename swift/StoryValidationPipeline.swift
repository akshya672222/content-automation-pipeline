import Foundation

// MARK: - Errors

/// Errors thrown by the story validation pipeline.
enum ValidationError: Error, LocalizedError {
      case maxRepairAttemptsExceeded

      var errorDescription: String? {
                switch self {
                          case .maxRepairAttemptsExceeded:
                              return "Story could not be repaired after maximum attempts. Manual review required."
                }
      }
}

// MARK: - Models

struct Story {
      let id: UUID
      var content: String
      var locale: String
}

struct ValidationResult {
      let needsRepair: Bool
      let violations: [String]
}

// MARK: - Pipeline

/// AI-powered story validation pipeline used in ParentPal StoryWriter.
///
/// Iteratively validates and repairs AI-generated stories against tone,
/// safety, and locale rules. Repair attempts are bounded to prevent
/// infinite recursion on persistently malformed outputs.
///
/// - Note: Max repair depth is 3. Beyond this, ``ValidationError/maxRepairAttemptsExceeded``
///   is thrown so the caller can flag the story for manual review.
struct StoryValidationPipeline {

      private let aiClient: AIClient
      private static let maxRepairDepth = 3

      init(aiClient: AIClient) {
                self.aiClient = aiClient
      }

      /// Validates a story and iteratively repairs violations up to ``maxRepairDepth`` times.
      ///
      /// - Parameters:
      ///   - story: The story to validate and potentially repair.
      ///   - depth: Current recursion depth. Pass `0` on initial call (default).
      /// - Returns: A validated, repair-compliant ``Story``.
      /// - Throws: ``ValidationError/maxRepairAttemptsExceeded`` if repairs are exhausted.
      func validateAndRepair(story: Story, depth: Int = 0) async throws -> Story {
                guard depth < Self.maxRepairDepth else {
                              throw ValidationError.maxRepairAttemptsExceeded
                }

                let validationResult = await validateStory(story)
                guard validationResult.needsRepair else { return story }

                let repairPrompt = buildRepairPrompt(story: story, violations: validationResult.violations)
                let repairedStory = try await aiClient.repairStory(repairPrompt)

                // Recurse with incremented depth — bounded, never infinite
                return try await validateAndRepair(story: repairedStory, depth: depth + 1)
      }

      // MARK: - Private

      private func validateStory(_ story: Story) async -> ValidationResult {
                // Validation logic: tone, safety, locale rule checks
                // Returns needsRepair: true if any rule is violated
                let violations: [String] = [] // Populated by real rule engine
                return ValidationResult(needsRepair: !violations.isEmpty, violations: violations)
      }

      private func buildRepairPrompt(story: Story, violations: [String]) -> String {
                """
                The following story violated these rules: \(violations.joined(separator: ", ")).
                Please rewrite it to comply with tone, safety, and locale requirements.
                Story: \(story.content)
                """
      }
}

// MARK: - AIClient Protocol

/// Protocol abstracting the AI repair service — injectable for testing.
protocol AIClient {
      func repairStory(_ prompt: String) async throws -> Story
}

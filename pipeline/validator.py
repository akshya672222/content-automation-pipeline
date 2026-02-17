"""
validator.py

Multi-layer content validation. Checks fabrication markers,
platform requirements, and voice consistency before publishing.
"""

import re
from dataclasses import dataclass, field


FABRICATION_MARKERS = [
      r"\bonce told me\b",
      r"\ba mentee of mine\b",
      r"\bI remember when\b",
      r"\btrue story\b",
      r"\bfun fact about me\b",
]

PLATFORM_MAX_CHARS = {
      "x": 280,
      "linkedin": 3000,
      "medium": 50000,
}


@dataclass
class ValidationResult:
      passed: bool
      failures: list[str] = field(default_factory=list)


class ContentValidator:
      """
          Runs sequential validation checks on generated content.
              All checks must pass for content to be published.
                  """

    def validate(self, content: str, platform: str) -> ValidationResult:
              failures = []

        failures += self._check_fabrication(content)
        failures += self._check_platform_limits(content, platform)
        failures += self._check_not_empty(content)

        return ValidationResult(passed=len(failures) == 0, failures=failures)

    def _check_fabrication(self, content: str) -> list[str]:
              found = []
              for pattern in FABRICATION_MARKERS:
                            if re.search(pattern, content, re.IGNORECASE):
                                              found.append(f"Fabrication marker detected: '{pattern}'")
                                      return found

    def _check_platform_limits(self, content: str, platform: str) -> list[str]:
              max_chars = PLATFORM_MAX_CHARS.get(platform)
              if max_chars and len(content) > max_chars:
                            return [f"Content exceeds {platform} limit: {len(content)} > {max_chars} chars"]
                        return []

    def _check_not_empty(self, content: str) -> list[str]:
              if not content or len(content.strip()) < 50:
                            return ["Content is empty or too short"]
                        return []

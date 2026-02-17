"""
claude_client.py

Claude API wrapper with exponential backoff retry logic and prompt caching.
See: https://docs.anthropic.com/en/api/messages
"""

import asyncio
import os
import random

import anthropic
from anthropic import RateLimitError, APIError


PLATFORM_WORD_LIMITS = {
      "linkedin": 750,
      "medium": 1500,
      "x": 280,
}

SYSTEM_PROMPT_PATH = os.path.join(os.path.dirname(__file__), "../prompts/system_prompt.txt")


class ContentGenerationError(Exception):
      pass


class ClaudeClient:
      """
          Wraps the Anthropic Messages API with:
              - Prompt caching (cache_control: ephemeral) for ~50% cost reduction
                  - Exponential backoff with jitter for rate limit handling
                      - Concurrent platform generation support
                          """

    MODEL = "claude-sonnet-4-6"
    MAX_TOKENS = 4096
    MAX_RETRIES = 3

    def __init__(self):
              self.client = anthropic.AsyncAnthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
              self._system_prompt = self._load_system_prompt()

    def _load_system_prompt(self) -> str:
              with open(SYSTEM_PROMPT_PATH, "r") as f:
                            return f.read()

          async def generate(self, pillar: str, platform: str) -> str:
                    """
                            Generate platform-optimized content for a given content pillar.

                                    Args:
                                                pillar: Content pillar (e.g. 'ios_swift', 'ai_mobile', 'career_mentorship')
                                                            platform: Target platform ('linkedin', 'medium', 'x')

                                                                    Returns:
                                                                                Generated content string

                                                                                        Raises:
                                                                                                    ContentGenerationError: If all retry attempts fail
                                                                                                            """
                    word_limit = PLATFORM_WORD_LIMITS.get(platform, 500)
                    user_prompt = (
                        f"Write a {platform} post for the '{pillar}' content pillar. "
                        f"Target length: {word_limit} words. "
                        f"Use only verified facts from the profile. No fabrication."
                    )
                    return await self._call_with_retry(user_prompt)

    async def _call_with_retry(self, prompt: str) -> str:
              for attempt in range(self.MAX_RETRIES):
                            try:
                                              response = await self.client.messages.create(
                                                                    model=self.MODEL,
                                                                    max_tokens=self.MAX_TOKENS,
                                                                    system=[{
                                                                                              "type": "text",
                                                                                              "text": self._system_prompt,
                                                                                              "cache_control": {"type": "ephemeral"}  # ~50% cost reduction
                                                                    }],
                                                                    messages=[{"role": "user", "content": prompt}]
                                              )
                                              return response.content[0].text

                            except RateLimitError:
                                              if attempt == self.MAX_RETRIES - 1:
                                                                    raise ContentGenerationError("Rate limit exceeded after max retries")
                                                                backoff = (2 ** attempt) + random.uniform(0, 1)
                                              await asyncio.sleep(backoff)

                            except APIError as e:
                                              if attempt == self.MAX_RETRIES - 1:
                                                                    raise ContentGenerationError(f"API error after {self.MAX_RETRIES} attempts: {e}")
                                                                await asyncio.sleep(1)
                              

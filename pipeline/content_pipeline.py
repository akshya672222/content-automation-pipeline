"""
content_pipeline.py

Core orchestration layer for the AI content automation pipeline.
Coordinates profile loading, content generation, validation, and publishing.
"""

import asyncio
from dataclasses import dataclass
from typing import Optional

from .claude_client import ClaudeClient
from .validator import ContentValidator


@dataclass
class PipelineConfig:
      platforms: list[str]
      pillar: str
      dry_run: bool = False


class ContentPipeline:
      """
          Main pipeline orchestrator.
              Generates, validates, and publishes content across platforms concurrently.
                  """

    SUPPORTED_PLATFORMS = ["linkedin", "medium", "x"]

    def __init__(self, config: PipelineConfig):
              self.config = config
              self.claude_client = ClaudeClient()
              self.validator = ContentValidator()

    async def run(self) -> dict[str, str]:
              """
                      Run the full pipeline for all configured platforms.
                              Returns a dict of {platform: result_status}.
                                      """
              tasks = {
                  platform: self._generate_and_publish(platform)
                  for platform in self.config.platforms
                  if platform in self.SUPPORTED_PLATFORMS
              }

        results = await asyncio.gather(*tasks.values(), return_exceptions=True)
        return dict(zip(tasks.keys(), results))

    async def _generate_and_publish(self, platform: str) -> str:
              content = await self.claude_client.generate(
                            pillar=self.config.pillar,
                            platform=platform
              )
              validation = self.validator.validate(content, platform)
              if not validation.passed:
                            raise ValueError(f"Validation failed for {platform}: {validation.failures}")

              if self.config.dry_run:
                            return f"[DRY RUN] Would publish to {platform}"

              # Publisher implementations live in publishers/
              publisher = self._get_publisher(platform)
              return await publisher.publish(content)

    def _get_publisher(self, platform: str):
              from publishers.linkedin_publisher import LinkedInPublisher
              from publishers.medium_publisher import MediumPublisher
              from publishers.twitter_publisher import TwitterPublisher

        return {
                      "linkedin": LinkedInPublisher,
                      "medium": MediumPublisher,
                      "x": TwitterPublisher,
        }[platform]()

"""
medium_publisher.py

Medium REST API publisher for automated article posting.

Uses Medium's Integration Token API to publish drafts or public posts.
Docs: https://github.com/Medium/medium-api-docs

Setup:
1. Go to Settings → Security and apps → Integration tokens
2. Generate a token and add it to your .env as MEDIUM_INTEGRATION_TOKEN
3. Optionally set MEDIUM_PUBLISH_STATUS to 'draft' or 'public' (default: draft)
"""

import os
import httpx


class MediumPublisherError(Exception):
    pass


class MediumPublisher:
    """
    Publishes content to Medium via the REST API.

    Supports markdown and HTML content formats.
    Defaults to 'draft' status to allow manual review before publishing.
    """

    BASE_URL = "https://api.medium.com/v1"

    def __init__(self):
        self.token = os.environ["MEDIUM_INTEGRATION_TOKEN"]
        self._user_id: str | None = None

    async def publish(self, content: str) -> str:
        """
        Publish content as a Medium article.

        Args:
            content: The article body in markdown format.

        Returns:
            Status string with the Medium post URL.

        Raises:
            MediumPublisherError: If the API request fails.
        """
        try:
            user_id = await self._get_user_id()
            post_url = await self._create_post(user_id, content)
            return f"Medium: published successfully → {post_url}"
        except MediumPublisherError:
            raise
        except Exception as e:
            raise MediumPublisherError(f"Medium publish failed: {e}") from e

    async def _get_user_id(self) -> str:
        """Fetch the authenticated user's ID (cached after first call)."""
        if self._user_id:
            return self._user_id

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/me",
                headers=self._auth_headers(),
                timeout=10.0,
            )
            response.raise_for_status()
            self._user_id = response.json()["data"]["id"]
            return self._user_id

    async def _create_post(self, user_id: str, content: str) -> str:
        """
        Create a post via the Medium API.

        Returns the URL of the created post.
        """
        title, body = self._extract_title_and_body(content)
        publish_status = os.environ.get("MEDIUM_PUBLISH_STATUS", "draft")

        payload = {
            "title": title,
            "contentFormat": "markdown",
            "content": content,
            "publishStatus": publish_status,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.BASE_URL}/users/{user_id}/posts",
                headers=self._auth_headers(),
                json=payload,
                timeout=30.0,
            )
            response.raise_for_status()
            return response.json()["data"]["url"]

    def _auth_headers(self) -> dict[str, str]:
        """Build authorization headers for Medium API requests."""
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    @staticmethod
    def _extract_title_and_body(content: str) -> tuple[str, str]:
        """
        Extract the first line as title (stripping leading '#') and
        the rest as body. Falls back to a truncated first line if no
        markdown heading is found.
        """
        lines = content.strip().split("\n")
        first_line = lines[0].strip().lstrip("#").strip() if lines else "Untitled"
        body = "\n".join(lines[1:]).strip() if len(lines) > 1 else content
        return first_line, body

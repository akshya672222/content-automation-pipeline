"""
twitter_publisher.py

X (Twitter) v2 API publisher for automated tweet posting.

Uses OAuth 1.0a User Context for posting tweets on behalf of the authenticated user.
Docs: https://developer.x.com/en/docs/x-api/tweets/manage-tweets/api-reference/post-tweets

Setup:
1. Create a project at https://developer.x.com/en/portal/dashboard
2. Generate OAuth 1.0a credentials (consumer key/secret + access token/secret)
3. Add all four values to your .env file (see .env.example)
"""

import os
import time
import hashlib
import hmac
import base64
import secrets
import urllib.parse

import httpx


class TwitterPublisherError(Exception):
    pass


class TwitterPublisher:
    """
    Publishes content to X (Twitter) via the v2 API.

    Handles OAuth 1.0a signing internally — no external OAuth library required.
    Automatically truncates content to 280 characters with an ellipsis if needed.
    """

    TWEET_ENDPOINT = "https://api.x.com/2/tweets"
    MAX_TWEET_LENGTH = 280

    def __init__(self):
        self.consumer_key = os.environ["TWITTER_CONSUMER_KEY"]
        self.consumer_secret = os.environ["TWITTER_CONSUMER_SECRET"]
        self.access_token = os.environ["TWITTER_ACCESS_TOKEN"]
        self.access_token_secret = os.environ["TWITTER_ACCESS_TOKEN_SECRET"]

    async def publish(self, content: str) -> str:
        """
        Publish content as a tweet.

        Args:
            content: The tweet text. Truncated to 280 chars if needed.

        Returns:
            Status string with the tweet ID.

        Raises:
            TwitterPublisherError: If the API request fails.
        """
        try:
            truncated = self._truncate(content)
            tweet_id = await self._post_tweet(truncated)
            return f"X: published successfully → tweet ID {tweet_id}"
        except TwitterPublisherError:
            raise
        except Exception as e:
            raise TwitterPublisherError(f"X publish failed: {e}") from e

    async def _post_tweet(self, text: str) -> str:
        """Post a tweet via the v2 API and return the tweet ID."""
        headers = self._build_oauth_headers("POST", self.TWEET_ENDPOINT)
        headers["Content-Type"] = "application/json"

        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.TWEET_ENDPOINT,
                headers=headers,
                json={"text": text},
                timeout=15.0,
            )
            response.raise_for_status()
            return response.json()["data"]["id"]

    def _truncate(self, content: str) -> str:
        """Truncate content to MAX_TWEET_LENGTH with ellipsis if needed."""
        if len(content) <= self.MAX_TWEET_LENGTH:
            return content
        return content[: self.MAX_TWEET_LENGTH - 1] + "…"

    # --- OAuth 1.0a signing ---

    def _build_oauth_headers(self, method: str, url: str) -> dict[str, str]:
        """
        Build OAuth 1.0a Authorization header for X API requests.

        Implements the signature base string and HMAC-SHA1 signing
        per https://developer.x.com/en/docs/authentication/oauth-1-0a/creating-a-signature
        """
        oauth_params = {
            "oauth_consumer_key": self.consumer_key,
            "oauth_nonce": secrets.token_hex(16),
            "oauth_signature_method": "HMAC-SHA1",
            "oauth_timestamp": str(int(time.time())),
            "oauth_token": self.access_token,
            "oauth_version": "1.0",
        }

        # Build signature base string
        param_string = "&".join(
            f"{urllib.parse.quote(k, safe='')}={urllib.parse.quote(v, safe='')}"
            for k, v in sorted(oauth_params.items())
        )
        base_string = (
            f"{method.upper()}&"
            f"{urllib.parse.quote(url, safe='')}&"
            f"{urllib.parse.quote(param_string, safe='')}"
        )

        # Sign with HMAC-SHA1
        signing_key = (
            f"{urllib.parse.quote(self.consumer_secret, safe='')}&"
            f"{urllib.parse.quote(self.access_token_secret, safe='')}"
        )
        signature = base64.b64encode(
            hmac.new(
                signing_key.encode(),
                base_string.encode(),
                hashlib.sha1,
            ).digest()
        ).decode()

        oauth_params["oauth_signature"] = signature

        # Format as Authorization header
        auth_header = "OAuth " + ", ".join(
            f'{urllib.parse.quote(k, safe="")}="{urllib.parse.quote(v, safe="")}"'
            for k, v in sorted(oauth_params.items())
        )

        return {"Authorization": auth_header}

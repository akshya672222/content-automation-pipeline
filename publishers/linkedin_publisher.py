"""
linkedin_publisher.py

Playwright-based LinkedIn publishing automation.

IMPORTANT: LinkedIn's UI changes frequently. CSS selectors are intentionally
abstracted into named helper methods. When LinkedIn breaks a selector, update
the corresponding _find_* method in isolation — the rest of the flow stays intact.

To find current selectors:
1. Open LinkedIn in Chrome DevTools
2. Use the element inspector on the target UI component
3. Update the relevant _find_* method below

LinkedIn does NOT provide a public API for personal profile posting.
This automation uses browser interaction via Playwright.
Docs: https://playwright.dev/python/docs/api/class-page
"""

import os
from playwright.async_api import async_playwright, Page


class LinkedInPublisherError(Exception):
      pass


class LinkedInPublisher:
      """
          Publishes content to LinkedIn via Playwright browser automation.

              Selectors are abstracted into helper methods to isolate LinkedIn UI changes.
                  Update _find_* methods when LinkedIn's UI changes — do NOT hardcode selectors inline.
                      """

    LINKEDIN_FEED_URL = "https://www.linkedin.com/feed/"

    async def publish(self, content: str) -> str:
              async with async_playwright() as p:
                            browser = await p.chromium.launch(headless=False)
                            page = await browser.new_page()

                  try:
                                    await page.goto(self.LINKEDIN_FEED_URL)
                                    await self._open_post_composer(page)
                                    await self._fill_post_content(page, content)
                                    await self._submit_post(page)
                                    return "LinkedIn: published successfully"
except Exception as e:
                raise LinkedInPublisherError(f"LinkedIn publish failed: {e}") from e
finally:
                await browser.close()

    # --- Selector abstraction layer ---
      # Update these methods when LinkedIn's UI changes.
      # Do NOT hardcode selectors anywhere else in this file.

    async def _open_post_composer(self, page: Page) -> None:
              """Clicks the 'Start a post' / share box to open the composer."""
        # TODO: Update selector when LinkedIn changes the share box component
        composer_trigger = await page.wait_for_selector("[data-test='share-box-click-card']", timeout=10000)
        await composer_trigger.click()

    async def _fill_post_content(self, page: Page, content: str) -> None:
              """Types content into the post text editor."""
        # TODO: Update selector when LinkedIn changes the editor component
        editor = await page.wait_for_selector("[data-testid='share-creation-state-text-editor']", timeout=10000)
        await editor.fill(content)

    async def _submit_post(self, page: Page) -> None:
              """Clicks the publish/post button."""
        # TODO: Update selector when LinkedIn changes the publish button component
        publish_btn = await page.wait_for_selector("[data-testid='share-creation-state-publish-button']", timeout=10000)
        await publish_btn.click()
        await page.wait_for_load_state("networkidle")

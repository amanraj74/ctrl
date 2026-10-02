"""Pollinations.ai image provider — no API key needed, primary image source."""

from __future__ import annotations

import logging
import random
from typing import Any
from urllib.parse import quote

import httpx

from app.config import settings
from app.providers.base import ImageProvider, ProviderError

logger = logging.getLogger(__name__)


class PollinationsProvider(ImageProvider):
    """Pollinations.ai — free AI image generation, no key required."""

    name = "pollinations"

    async def generate(
        self,
        prompt: str,
        width: int = 1080,
        height: int = 1920,
        seed: int | None = None,
        **kwargs: Any,
    ) -> bytes:
        if seed is None:
            seed = random.randint(1, 999999)

        encoded_prompt = quote(prompt, safe="")
        url = (
            f"https://image.pollinations.ai/prompt/{encoded_prompt}"
            f"?width={width}&height={height}&seed={seed}"
        )

        logger.info("Pollinations request: seed=%d, prompt=%s...", seed, prompt[:80])

        try:
            async with httpx.AsyncClient(timeout=settings.image_timeout, follow_redirects=True) as client:
                resp = await client.get(url)
                resp.raise_for_status()

                content_type = resp.headers.get("content-type", "")
                if "image" not in content_type and len(resp.content) < 1000:
                    raise ProviderError(f"Pollinations returned non-image: {content_type}")

                logger.info("✓ Pollinations image received: %d bytes", len(resp.content))
                return resp.content

        except httpx.TimeoutException as e:
            raise ProviderError(f"Pollinations timed out after {settings.image_timeout}s: {e}") from e
        except httpx.HTTPStatusError as e:
            raise ProviderError(f"Pollinations HTTP error {e.response.status_code}: {e}") from e
        except ProviderError:
            raise
        except Exception as e:
            raise ProviderError(f"Pollinations failed: {e}") from e

    async def is_available(self) -> bool:
        # Pollinations is always available (no key needed)
        return True

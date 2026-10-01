"""Pexels stock photo provider — last resort fallback for images."""

from __future__ import annotations

import logging
from typing import Any

import httpx

from app.config import settings
from app.providers.base import ImageProvider, ProviderError

logger = logging.getLogger(__name__)


class PexelsProvider(ImageProvider):
    """Pexels stock photos — free API, used as last-resort image fallback."""

    name = "pexels"

    async def is_available(self) -> bool:
        return bool(settings.pexels_api_key)

    async def generate(
        self,
        prompt: str,
        width: int = 1080,
        height: int = 1920,
        seed: int | None = None,
        **kwargs: Any,
    ) -> bytes:
        """Search Pexels for a relevant stock photo and download it."""
        if not await self.is_available():
            raise ProviderError("Pexels not configured")

        # Search for photos matching the prompt
        search_query = kwargs.get("stock_query", prompt)

        headers = {
            "Authorization": settings.pexels_api_key,
        }

        try:
            async with httpx.AsyncClient(timeout=settings.image_timeout) as client:
                # Search for portrait-oriented photos
                search_url = "https://api.pexels.com/v1/search"
                params = {
                    "query": search_query,
                    "orientation": "portrait",
                    "size": "large",
                    "per_page": 5,
                }

                resp = await client.get(search_url, headers=headers, params=params)
                resp.raise_for_status()

                data = resp.json()
                photos = data.get("photos", [])

                if not photos:
                    raise ProviderError(f"No Pexels photos found for: {search_query}")

                # Pick the best match (first result or seeded)
                idx = (seed or 0) % len(photos)
                photo = photos[idx]

                # Download the portrait-sized photo
                photo_url = photo["src"].get("portrait") or photo["src"].get("large")

                img_resp = await client.get(photo_url)
                img_resp.raise_for_status()

                logger.info(
                    "✓ Pexels photo downloaded: %d bytes, photographer: %s",
                    len(img_resp.content),
                    photo.get("photographer", "unknown"),
                )
                return img_resp.content

        except ProviderError:
            raise
        except Exception as e:
            raise ProviderError(f"Pexels failed: {e}") from e

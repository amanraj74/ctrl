"""Cloudflare Workers AI image provider — free tier fallback."""

from __future__ import annotations

import logging
from typing import Any

import httpx

from app.config import settings
from app.providers.base import ImageProvider, ProviderError

logger = logging.getLogger(__name__)


class CloudflareImageProvider(ImageProvider):
    """Cloudflare Workers AI — free tier image generation (FLUX-1-schnell / SDXL)."""

    name = "cloudflare"

    async def is_available(self) -> bool:
        return bool(settings.cloudflare_account_id and settings.cloudflare_api_token)

    async def generate(
        self,
        prompt: str,
        width: int = 1080,
        height: int = 1920,
        seed: int | None = None,
        **kwargs: Any,
    ) -> bytes:
        if not await self.is_available():
            raise ProviderError("Cloudflare not configured")

        # Use FLUX-1-schnell for speed, or stable-diffusion-xl-base for quality
        model = "@cf/black-forest-labs/flux-1-schnell"
        url = f"https://api.cloudflare.com/client/v4/accounts/{settings.cloudflare_account_id}/ai/run/{model}"

        headers = {
            "Authorization": f"Bearer {settings.cloudflare_api_token}",
            "Content-Type": "application/json",
        }

        # Cloudflare has limited resolution support, generate at supported size then resize
        payload = {
            "prompt": prompt,
            "width": min(width, 1024),
            "height": min(height, 1024),
        }
        if seed is not None:
            payload["seed"] = seed

        logger.info("Cloudflare request: model=%s, prompt=%s...", model, prompt[:80])

        try:
            async with httpx.AsyncClient(timeout=settings.image_timeout) as client:
                resp = await client.post(url, headers=headers, json=payload)
                resp.raise_for_status()

                # Cloudflare returns raw image bytes
                if len(resp.content) < 1000:
                    raise ProviderError(f"Cloudflare returned suspiciously small response: {len(resp.content)} bytes")

                logger.info("✓ Cloudflare image received: %d bytes", len(resp.content))
                return resp.content

        except httpx.TimeoutException as e:
            raise ProviderError(f"Cloudflare timed out: {e}") from e
        except httpx.HTTPStatusError as e:
            raise ProviderError(f"Cloudflare HTTP error {e.response.status_code}: {e}") from e
        except ProviderError:
            raise
        except Exception as e:
            raise ProviderError(f"Cloudflare failed: {e}") from e

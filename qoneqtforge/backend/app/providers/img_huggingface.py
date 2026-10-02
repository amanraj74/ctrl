"""HuggingFace Image provider using free FLUX.1-schnell API."""

from __future__ import annotations

import logging
import random
from typing import Any

import httpx

from app.config import settings
from app.providers.base import ImageProvider, ProviderError

logger = logging.getLogger(__name__)


class HuggingFaceProvider(ImageProvider):
    name = "huggingface"

    async def is_available(self) -> bool:
        return bool(settings.hf_token)

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

        keys = [k.strip() for k in settings.hf_token.split(",") if k.strip()]
        if not keys:
            raise ProviderError("No HF Tokens configured")

        token = random.choice(keys)

        url = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"
        headers = {"Authorization": f"Bearer {token}"}
        payload = {
            "inputs": prompt,
            "parameters": {
                "width": width,
                "height": height,
                "seed": seed,
            }
        }

        logger.info("HuggingFace FLUX request: prompt=%s...", prompt[:80])

        try:
            async with httpx.AsyncClient(timeout=settings.image_timeout) as client:
                resp = await client.post(url, headers=headers, json=payload)
                if resp.status_code == 503:
                    raise ProviderError("HuggingFace model is currently loading")
                resp.raise_for_status()

                content_type = resp.headers.get("content-type", "")
                if "image" not in content_type:
                    raise ProviderError(f"HuggingFace returned non-image: {resp.text[:200]}")

                logger.info("✓ HuggingFace image received: %d bytes", len(resp.content))
                return resp.content

        except Exception as e:
            raise ProviderError(f"HuggingFace failed: {e}") from e

"""OpenRouter LLM provider — ultimate backup chain."""

from __future__ import annotations

import json
import logging
import random
from typing import Any

from pydantic import BaseModel

from app.config import settings
from app.providers.base import LLMProvider, ProviderError
from app.utils.json_repair import repair_json

logger = logging.getLogger(__name__)


class OpenRouterProvider(LLMProvider):
    name = "openrouter"

    async def is_available(self) -> bool:
        return bool(settings.openrouter_api_key)

    async def complete_json(
        self,
        prompt: str,
        schema: type[BaseModel],
        system_prompt: str = "",
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs: Any,
    ) -> BaseModel:
        import httpx

        # Split by comma or newline (if they used quotes)
        keys = [k.strip() for k in settings.openrouter_api_key.replace('\n', ',').split(",") if k.strip()]
        if not keys:
            raise ProviderError("No OpenRouter keys")

        key = random.choice(keys)
        url = "https://openrouter.ai/api/v1/chat/completions"

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "meta-llama/llama-3-8b-instruct:free",
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "response_format": {"type": "json_object"}
        }

        try:
            async with httpx.AsyncClient(timeout=settings.llm_timeout) as client:
                resp = await client.post(url, headers=headers, json=payload)
                resp.raise_for_status()
                raw_text = resp.json()["choices"][0]["message"]["content"]
        except Exception as e:
            raise ProviderError(f"OpenRouter failed: {e}") from e

        try:
            repaired = repair_json(raw_text)
            data = json.loads(repaired)
            return schema.model_validate(data)
        except Exception as e:
            raise ProviderError(f"OpenRouter invalid JSON: {e}") from e

    async def complete_text(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs: Any,
    ) -> str:
        import httpx

        keys = [k.strip() for k in settings.openrouter_api_key.replace('\n', ',').split(",") if k.strip()]
        if not keys:
            raise ProviderError("No OpenRouter keys")

        key = random.choice(keys)
        url = "https://openrouter.ai/api/v1/chat/completions"

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "meta-llama/llama-3-8b-instruct:free",
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        try:
            async with httpx.AsyncClient(timeout=settings.llm_timeout) as client:
                resp = await client.post(url, headers=headers, json=payload)
                resp.raise_for_status()
                return resp.json()["choices"][0]["message"]["content"]
        except Exception as e:
            raise ProviderError(f"OpenRouter text failed: {e}") from e

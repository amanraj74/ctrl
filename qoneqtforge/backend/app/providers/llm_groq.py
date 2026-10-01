"""Groq LLM provider — fast fallback in the LLM chain."""

from __future__ import annotations

import json
import logging
from typing import Any

from pydantic import BaseModel, ValidationError

from app.config import settings
from app.providers.base import LLMProvider, ProviderError, RateLimitError
from app.utils.json_repair import repair_json

logger = logging.getLogger(__name__)


class GroqProvider(LLMProvider):
    """Groq API provider with Llama 3.3 70B — very fast inference."""

    name = "groq"

    def __init__(self) -> None:
        self._client = None

    def _get_client(self):
        if self._client is None:
            try:
                from groq import Groq

                self._client = Groq(api_key=settings.groq_api_key)
            except Exception as e:
                raise ProviderError(f"Failed to initialize Groq: {e}") from e
        return self._client

    async def is_available(self) -> bool:
        return bool(settings.groq_api_key)

    async def complete_json(
        self,
        prompt: str,
        schema: type[BaseModel],
        system_prompt: str = "",
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs: Any,
    ) -> BaseModel:
        client = self._get_client()

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                response_format={"type": "json_object"},
            )
            raw_text = response.choices[0].message.content
            logger.debug("Groq raw response: %s...", raw_text[:300])
        except Exception as e:
            error_str = str(e).lower()
            if "429" in error_str or "rate" in error_str:
                raise RateLimitError(f"Groq rate limited: {e}") from e
            raise ProviderError(f"Groq generation failed: {e}") from e

        # Parse and validate JSON
        try:
            repaired = repair_json(raw_text)
            data = json.loads(repaired)
            return schema.model_validate(data)
        except (json.JSONDecodeError, ValidationError, ValueError) as e:
            logger.warning("Groq JSON parse/validate failed: %s", e)
            raise ProviderError(f"Groq returned invalid JSON: {e}") from e

    async def complete_text(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs: Any,
    ) -> str:
        client = self._get_client()

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content
        except Exception as e:
            error_str = str(e).lower()
            if "429" in error_str or "rate" in error_str:
                raise RateLimitError(f"Groq rate limited: {e}") from e
            raise ProviderError(f"Groq generation failed: {e}") from e

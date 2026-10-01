"""Ollama local LLM provider — offline fallback, runs on user's machine."""

from __future__ import annotations

import json
import logging
from typing import Any

import httpx
from pydantic import BaseModel, ValidationError

from app.config import settings
from app.providers.base import LLMProvider, ProviderError
from app.utils.json_repair import repair_json

logger = logging.getLogger(__name__)


class OllamaProvider(LLMProvider):
    """Ollama local LLM provider — unlimited, free, fully offline."""

    name = "ollama"

    def __init__(self, model: str = "llama3.2:3b") -> None:
        self.model = model
        self.base_url = settings.ollama_base_url

    async def is_available(self) -> bool:
        """Check if Ollama is running locally."""
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                resp = await client.get(f"{self.base_url}/api/tags")
                return resp.status_code == 200
        except Exception:
            return False

    async def complete_json(
        self,
        prompt: str,
        schema: type[BaseModel],
        system_prompt: str = "",
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs: Any,
    ) -> BaseModel:
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"

        # Append JSON instruction
        full_prompt += "\n\nRespond with valid JSON only. No markdown, no explanation."

        try:
            async with httpx.AsyncClient(timeout=settings.llm_timeout) as client:
                resp = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": full_prompt,
                        "format": "json",
                        "stream": False,
                        "options": {
                            "temperature": temperature,
                            "num_predict": max_tokens,
                        },
                    },
                )
                resp.raise_for_status()
                raw_text = resp.json().get("response", "")
                logger.debug("Ollama raw response: %s...", raw_text[:300])
        except httpx.TimeoutException as e:
            raise ProviderError(f"Ollama timed out: {e}") from e
        except Exception as e:
            raise ProviderError(f"Ollama generation failed: {e}") from e

        # Parse and validate
        try:
            repaired = repair_json(raw_text)
            data = json.loads(repaired)
            return schema.model_validate(data)
        except (json.JSONDecodeError, ValidationError, ValueError) as e:
            raise ProviderError(f"Ollama returned invalid JSON: {e}") from e

    async def complete_text(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs: Any,
    ) -> str:
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"

        try:
            async with httpx.AsyncClient(timeout=settings.llm_timeout) as client:
                resp = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": full_prompt,
                        "stream": False,
                        "options": {
                            "temperature": temperature,
                            "num_predict": max_tokens,
                        },
                    },
                )
                resp.raise_for_status()
                return resp.json().get("response", "")
        except Exception as e:
            raise ProviderError(f"Ollama generation failed: {e}") from e

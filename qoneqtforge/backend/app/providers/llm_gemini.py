"""Google Gemini LLM provider — primary LLM in the fallback chain."""

from __future__ import annotations

import json
import logging
from typing import Any

from pydantic import BaseModel, ValidationError

from app.config import settings
from app.providers.base import LLMProvider, ProviderError, RateLimitError
from app.utils.json_repair import repair_json

logger = logging.getLogger(__name__)


class GeminiProvider(LLMProvider):
    """Google Gemini API provider using the free AI Studio tier."""

    name = "gemini"

    def __init__(self) -> None:
        self._client = None

    def _get_client(self):
        if self._client is None:
            try:
                import google.generativeai as genai

                genai.configure(api_key=settings.gemini_api_key)
                self._client = genai
            except Exception as e:
                raise ProviderError(f"Failed to initialize Gemini: {e}") from e
        return self._client

    async def is_available(self) -> bool:
        return bool(settings.gemini_api_key)

    async def complete_json(
        self,
        prompt: str,
        schema: type[BaseModel],
        system_prompt: str = "",
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs: Any,
    ) -> BaseModel:
        genai = self._get_client()

        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            system_instruction=system_prompt if system_prompt else None,
            generation_config=genai.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
                response_mime_type="application/json",
            ),
        )

        try:
            response = model.generate_content(prompt)
            raw_text = response.text
            logger.debug("Gemini raw response: %s...", raw_text[:300])
        except Exception as e:
            error_str = str(e).lower()
            if "429" in error_str or "rate" in error_str or "quota" in error_str:
                raise RateLimitError(f"Gemini rate limited: {e}") from e
            raise ProviderError(f"Gemini generation failed: {e}") from e

        # Parse and validate JSON
        try:
            repaired = repair_json(raw_text)
            data = json.loads(repaired)
            return schema.model_validate(data)
        except (json.JSONDecodeError, ValidationError, ValueError) as e:
            logger.warning("Gemini JSON parse/validate failed: %s", e)
            raise ValidationError.from_exception_data(
                title=schema.__name__,
                line_errors=[],
            ) if isinstance(e, ValidationError) else ProviderError(
                f"Gemini returned invalid JSON: {e}"
            ) from e

    async def complete_text(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs: Any,
    ) -> str:
        genai = self._get_client()

        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            system_instruction=system_prompt if system_prompt else None,
            generation_config=genai.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
            ),
        )

        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            error_str = str(e).lower()
            if "429" in error_str or "rate" in error_str:
                raise RateLimitError(f"Gemini rate limited: {e}") from e
            raise ProviderError(f"Gemini generation failed: {e}") from e

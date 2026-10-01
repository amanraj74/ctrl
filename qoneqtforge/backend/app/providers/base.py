"""Abstract base classes for all providers.

Every provider (LLM, Image, TTS) must implement these interfaces.
This allows the router to swap providers transparently.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from pydantic import BaseModel


class ProviderError(Exception):
    """Base exception for provider failures."""

    pass


class RateLimitError(ProviderError):
    """Raised when a provider rate-limits us."""

    pass


class TimeoutError(ProviderError):
    """Raised when a provider times out."""

    pass


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    name: str = "base"

    @abstractmethod
    async def complete_json(
        self,
        prompt: str,
        schema: type[BaseModel],
        system_prompt: str = "",
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs: Any,
    ) -> BaseModel:
        """Generate a JSON response matching the given Pydantic schema.

        Args:
            prompt: The user prompt
            schema: Pydantic model class to validate against
            system_prompt: System instruction
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate

        Returns:
            Validated Pydantic model instance

        Raises:
            ProviderError: On provider failure
            RateLimitError: On rate limiting
            TimeoutError: On timeout
            ValidationError: If output doesn't match schema
        """
        ...

    @abstractmethod
    async def complete_text(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs: Any,
    ) -> str:
        """Generate a plain text response.

        Returns:
            Generated text string
        """
        ...

    async def is_available(self) -> bool:
        """Check if this provider is configured and reachable."""
        return True


class ImageProvider(ABC):
    """Abstract base class for image generation providers."""

    name: str = "base"

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        width: int = 1080,
        height: int = 1920,
        seed: int | None = None,
        **kwargs: Any,
    ) -> bytes:
        """Generate an image from a text prompt.

        Args:
            prompt: Image description
            width: Image width in pixels
            height: Image height in pixels
            seed: Random seed for reproducibility

        Returns:
            Raw image bytes (PNG/JPEG)

        Raises:
            ProviderError: On generation failure
        """
        ...

    async def is_available(self) -> bool:
        """Check if this provider is configured and reachable."""
        return True


class TTSProvider(ABC):
    """Abstract base class for text-to-speech providers."""

    name: str = "base"

    @abstractmethod
    async def synthesize(
        self,
        text: str,
        voice: str,
        output_path: Path,
        language: str = "en",
        **kwargs: Any,
    ) -> dict:
        """Synthesize speech from text.

        Args:
            text: Text to speak
            voice: Voice name/identifier
            output_path: Path to save the audio file
            language: Language code

        Returns:
            Dict with keys:
                - audio_path: str (path to audio file)
                - duration_sec: float
                - word_timings: list[dict] (optional, with start, end, word)
        """
        ...

    async def is_available(self) -> bool:
        """Check if this provider is configured and reachable."""
        return True

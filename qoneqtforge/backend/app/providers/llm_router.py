"""LLM Router — fallback chain across all LLM providers.

This is the heart of the provider resilience system.
It tries Gemini first, then Groq, then Ollama, with retries at each level.
"""

from __future__ import annotations

import logging
from typing import Any

from pydantic import BaseModel

from app.providers.base import LLMProvider, ProviderError, RateLimitError
from app.providers.llm_gemini import GeminiProvider
from app.providers.llm_groq import GroqProvider
from app.providers.llm_ollama import OllamaProvider
from app.providers.llm_openrouter import OpenRouterProvider

logger = logging.getLogger(__name__)

# Default fallback chain order
DEFAULT_CHAIN: list[type[LLMProvider]] = [GeminiProvider, GroqProvider, OpenRouterProvider, OllamaProvider]

# Track which provider served each request (for UI display)
_last_provider: str = "none"


def get_last_provider() -> str:
    """Get the name of the provider that served the last request."""
    return _last_provider


async def _try_with_retry(
    provider: LLMProvider,
    method: str,
    attempts: int = 2,
    backoff: float = 1.5,
    **kwargs: Any,
) -> Any:
    """Try a provider method with retries and exponential backoff."""
    import asyncio

    last_error = None
    for attempt in range(attempts):
        try:
            func = getattr(provider, method)
            result = await func(**kwargs)
            return result
        except RateLimitError:
            # Don't retry rate limits, move to next provider
            raise
        except Exception as e:
            last_error = e
            if attempt < attempts - 1:
                wait = backoff ** attempt
                logger.warning(
                    "Provider %s attempt %d/%d failed: %s. Retrying in %.1fs...",
                    provider.name,
                    attempt + 1,
                    attempts,
                    e,
                    wait,
                )
                await asyncio.sleep(wait)
            else:
                logger.warning(
                    "Provider %s exhausted %d attempts: %s",
                    provider.name,
                    attempts,
                    e,
                )
    raise last_error


async def complete_json(
    prompt: str,
    schema: type[BaseModel],
    system_prompt: str = "",
    temperature: float = 0.7,
    max_tokens: int = 4096,
    chain: list[type[LLMProvider]] | None = None,
    **kwargs: Any,
) -> BaseModel:
    """Complete a JSON prompt using the fallback chain.

    Tries each provider in order. Each provider gets 2 attempts with backoff.
    Rate-limited providers are skipped immediately.

    Args:
        prompt: The user prompt
        schema: Pydantic model to validate against
        system_prompt: System instruction
        chain: Custom provider chain (defaults to Gemini → Groq → Ollama)

    Returns:
        Validated Pydantic model instance

    Raises:
        ProviderError: If all providers fail
    """
    global _last_provider
    providers = chain or DEFAULT_CHAIN
    last_error = None

    for ProviderClass in providers:
        provider = ProviderClass()

        # Check availability
        if not await provider.is_available():
            logger.info("Provider %s not available, skipping", provider.name)
            continue

        try:
            result = await _try_with_retry(
                provider,
                "complete_json",
                prompt=prompt,
                schema=schema,
                system_prompt=system_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs,
            )
            _last_provider = provider.name
            logger.info("✓ LLM request served by %s", provider.name)
            return result

        except RateLimitError as e:
            logger.warning("Provider %s rate-limited, trying next: %s", provider.name, e)
            last_error = e
            continue

        except Exception as e:
            logger.warning("Provider %s failed, trying next: %s", provider.name, e)
            last_error = e
            continue

    raise ProviderError(f"All LLM providers failed. Last error: {last_error}")


async def complete_text(
    prompt: str,
    system_prompt: str = "",
    temperature: float = 0.7,
    max_tokens: int = 4096,
    chain: list[type[LLMProvider]] | None = None,
    **kwargs: Any,
) -> str:
    """Complete a text prompt using the fallback chain."""
    global _last_provider
    providers = chain or DEFAULT_CHAIN
    last_error = None

    for ProviderClass in providers:
        provider = ProviderClass()

        if not await provider.is_available():
            continue

        try:
            result = await _try_with_retry(
                provider,
                "complete_text",
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs,
            )
            _last_provider = provider.name
            logger.info("✓ LLM text request served by %s", provider.name)
            return result

        except Exception as e:
            logger.warning("Provider %s failed: %s", provider.name, e)
            last_error = e
            continue

    raise ProviderError(f"All LLM providers failed. Last error: {last_error}")

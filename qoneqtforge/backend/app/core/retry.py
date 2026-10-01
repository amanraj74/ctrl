"""Retry utilities using tenacity."""

from __future__ import annotations

from tenacity import retry, stop_after_attempt, wait_exponential

# Default retry decorator for provider calls
default_retry = retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    reraise=True,
)

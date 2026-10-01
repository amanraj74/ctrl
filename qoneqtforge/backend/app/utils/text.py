"""Text utility functions."""

from __future__ import annotations

import re


def word_count(text: str) -> int:
    """Count words in text."""
    return len(text.split())


def truncate_to_words(text: str, max_words: int) -> str:
    """Truncate text to a maximum number of words at a word boundary."""
    words = text.split()
    if len(words) <= max_words:
        return text
    return " ".join(words[:max_words]) + "..."


def clean_whitespace(text: str) -> str:
    """Normalize whitespace: collapse multiple spaces, strip."""
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def estimate_speaking_duration(text: str, wpm: float = 150.0) -> float:
    """Estimate how long it takes to speak text at given words-per-minute.

    Default WPM is 150 which is a natural conversational pace.
    Returns duration in seconds.
    """
    words = word_count(text)
    return (words / wpm) * 60


def words_for_duration(duration_sec: float, wpm: float = 150.0) -> int:
    """Calculate how many words fit in a given duration at WPM rate."""
    return int((duration_sec / 60) * wpm)


def sanitize_filename(name: str) -> str:
    """Sanitize a string for use as a filename."""
    # Remove non-alphanumeric characters except dash, underscore, dot
    name = re.sub(r"[^\w\-.]", "_", name)
    # Collapse multiple underscores
    name = re.sub(r"_+", "_", name)
    return name[:100]  # Limit length

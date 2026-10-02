"""Content safety filters — banned topics, PII detection."""

from __future__ import annotations

import logging
import re

logger = logging.getLogger(__name__)

# Topics that should be filtered out
BANNED_TOPICS = [
    "violence",
    "gore",
    "explicit sexual",
    "pornography",
    "child abuse",
    "terrorism",
    "self-harm",
    "suicide instructions",
    "hate speech",
    "racial slurs",
    "drug manufacturing",
    "weapons manufacturing",
]

# Patterns for PII detection
PII_PATTERNS = {
    "email": re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"),
    "phone_india": re.compile(r"\b(?:\+91[\s-]?)?[6-9]\d{9}\b"),
    "phone_intl": re.compile(r"\b\+?\d{1,3}[\s-]?\(?\d{1,4}\)?[\s-]?\d{3,4}[\s-]?\d{3,4}\b"),
    "aadhaar": re.compile(r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}\b"),
    "pan": re.compile(r"\b[A-Z]{5}\d{4}[A-Z]\b"),
}


def check_banned_topics(text: str) -> list[str]:
    """Check if text contains banned topics.

    Returns a list of matched banned topics (empty if clean).
    """
    text_lower = text.lower()
    matches = []
    for topic in BANNED_TOPICS:
        if topic in text_lower:
            matches.append(topic)
    return matches


def check_pii(text: str) -> list[dict[str, str]]:
    """Check for personally identifiable information.

    Returns a list of dicts with 'type' and 'match' keys.
    """
    findings = []
    for pii_type, pattern in PII_PATTERNS.items():
        for match in pattern.finditer(text):
            findings.append({"type": pii_type, "match": match.group()})
    return findings


def is_content_safe(text: str) -> tuple[bool, list[str]]:
    """Check if content is safe for publishing.

    Returns:
        Tuple of (is_safe: bool, issues: list[str])
    """
    issues = []

    # Check banned topics
    banned = check_banned_topics(text)
    if banned:
        issues.extend([f"Banned topic detected: {t}" for t in banned])

    # Check PII
    pii = check_pii(text)
    if pii:
        issues.extend([f"PII detected ({p['type']}): {p['match']}" for p in pii])

    is_safe = len(issues) == 0
    if not is_safe:
        logger.warning("Content safety check failed: %s", issues)

    return is_safe, issues

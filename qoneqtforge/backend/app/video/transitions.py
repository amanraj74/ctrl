"""Video transition effects between scenes."""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def get_crossfade_filter(
    duration: float = 0.25,
    transition: str = "fade",
    offset: float = 0.0,
) -> str:
    """Get FFmpeg xfade filter for scene transitions.

    Args:
        duration: Transition duration in seconds
        transition: Transition type (fade, slideleft, slideright, etc.)
        offset: Offset in seconds where transition starts

    Returns:
        FFmpeg xfade filter string
    """
    return f"xfade=transition={transition}:duration={duration}:offset={offset}"


# Available xfade transition types
TRANSITIONS = [
    "fade",
    "slideleft",
    "slideright",
    "slideup",
    "slidedown",
    "dissolve",
    "smoothleft",
]


def get_varied_transition(scene_idx: int) -> str:
    """Get a varied transition type based on scene index.

    Alternates between different transition types for visual variety.
    """
    return TRANSITIONS[scene_idx % len(TRANSITIONS)]

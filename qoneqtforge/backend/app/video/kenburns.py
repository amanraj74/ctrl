"""Ken Burns zoom/pan effects for static images."""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

# Ken Burns FFmpeg zoompan filter templates
# Each creates a slow, cinematic motion effect on a static image
MOTION_FILTERS = {
    "zoom_in": (
        "zoompan=z='min(zoom+0.0008,1.25)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
        ":d={frames}:s={width}x{height}:fps={fps}"
    ),
    "zoom_out": (
        "zoompan=z='if(eq(on,1),1.25,max(zoom-0.0008,1))':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
        ":d={frames}:s={width}x{height}:fps={fps}"
    ),
    "pan_left": (
        "zoompan=z='1.15':x='if(eq(on,1),0,min(x+2,iw-iw/zoom))':y='ih/2-(ih/zoom/2)'"
        ":d={frames}:s={width}x{height}:fps={fps}"
    ),
    "pan_right": (
        "zoompan=z='1.15':x='if(eq(on,1),iw-iw/zoom,max(x-2,0))':y='ih/2-(ih/zoom/2)'"
        ":d={frames}:s={width}x{height}:fps={fps}"
    ),
    "tilt_up": (
        "zoompan=z='1.15':x='iw/2-(iw/zoom/2)':y='if(eq(on,1),ih-ih/zoom,max(y-2,0))'"
        ":d={frames}:s={width}x{height}:fps={fps}"
    ),
}


def get_kenburns_filter(
    motion: str,
    duration_sec: float,
    width: int = 1080,
    height: int = 1920,
    fps: int = 30,
) -> str:
    """Get the FFmpeg zoompan filter string for a Ken Burns motion.

    Args:
        motion: One of zoom_in, zoom_out, pan_left, pan_right, tilt_up
        duration_sec: Duration in seconds
        width: Output width
        height: Output height
        fps: Output FPS

    Returns:
        FFmpeg filter string for the zoompan effect
    """
    frames = int(duration_sec * fps)

    template = MOTION_FILTERS.get(motion, MOTION_FILTERS["zoom_in"])

    filter_str = template.format(
        frames=frames,
        width=width,
        height=height,
        fps=fps,
    )

    logger.debug("Ken Burns filter (%s, %.1fs): %s", motion, duration_sec, filter_str[:80])
    return filter_str

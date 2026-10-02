"""Edge-TTS provider — free Microsoft neural voices with word-level timing."""

from __future__ import annotations

import logging
import tempfile
from pathlib import Path
from typing import Any

from app.providers.base import ProviderError, TTSProvider

logger = logging.getLogger(__name__)

# Default voices per language
DEFAULT_VOICES = {
    "en": "en-US-AriaNeural",
    "hi": "hi-IN-SwaraNeural",
    "gu": "gu-IN-DhwaniNeural",
}


class EdgeTTSProvider(TTSProvider):
    """Microsoft Edge TTS — free neural voices, word-level timing data."""

    name = "edge-tts"

    async def is_available(self) -> bool:
        try:
            import edge_tts  # noqa: F401
            return True
        except ImportError:
            return False

    async def synthesize(
        self,
        text: str,
        voice: str = "",
        output_path: Path | None = None,
        language: str = "en",
        **kwargs: Any,
    ) -> dict:
        import edge_tts

        if not voice:
            voice = DEFAULT_VOICES.get(language, DEFAULT_VOICES["en"])

        if output_path is None:
            output_path = Path(tempfile.mktemp(suffix=".mp3"))

        logger.info("Edge-TTS synthesizing: voice=%s, text=%s...", voice, text[:60])

        try:
            communicate = edge_tts.Communicate(text, voice)

            # Collect word timing data from SubMaker
            word_timings = []
            audio_data = b""

            # Write audio to file and collect timing data
            submaker = edge_tts.SubMaker()

            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_data += chunk["data"]
                elif chunk["type"] == "WordBoundary":
                    timing = {
                        "word": chunk["text"],
                        "start": chunk["offset"] / 10_000_000,  # Convert from 100ns to seconds
                        "end": (chunk["offset"] + chunk["duration"]) / 10_000_000,
                        "duration": chunk["duration"] / 10_000_000,
                    }
                    word_timings.append(timing)
                    submaker.feed(chunk)

            # Write audio file
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "wb") as f:
                f.write(audio_data)

            # Calculate total duration
            duration_sec = 0.0
            if word_timings:
                duration_sec = word_timings[-1]["end"]

            # Also estimate from audio size if timings are empty
            if duration_sec == 0 and len(audio_data) > 0:
                # Rough estimate: MP3 at ~128kbps
                duration_sec = len(audio_data) / (128 * 1000 / 8)

            logger.info(
                "✓ Edge-TTS complete: %s, %.1fs, %d word timings",
                output_path.name,
                duration_sec,
                len(word_timings),
            )

            return {
                "audio_path": str(output_path),
                "duration_sec": duration_sec,
                "word_timings": word_timings,
                "voice": voice,
                "provider": self.name,
            }

        except Exception as e:
            raise ProviderError(f"Edge-TTS failed: {e}") from e

"""Piper TTS provider — offline fallback for text-to-speech."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from app.providers.base import ProviderError, TTSProvider
from app.utils.text import estimate_speaking_duration

logger = logging.getLogger(__name__)


class PiperTTSProvider(TTSProvider):
    """Piper TTS — offline, fast, no network required. Fallback only."""

    name = "piper"

    async def is_available(self) -> bool:
        """Check if pyttsx3 is available as minimal fallback."""
        try:
            import pyttsx3  # noqa: F401
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
        """Synthesize using pyttsx3 as a simple offline fallback.

        Note: pyttsx3 doesn't provide word-level timing.
        Timings will be estimated from text length.
        """
        try:
            import pyttsx3

            engine = pyttsx3.init()

            if output_path is None:
                import tempfile
                output_path = Path(tempfile.mktemp(suffix=".mp3"))

            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Save to file
            engine.save_to_file(text, str(output_path))
            engine.runAndWait()

            duration_sec = estimate_speaking_duration(text)

            # Generate estimated word timings
            words = text.split()
            time_per_word = duration_sec / max(len(words), 1)
            word_timings = []
            current_time = 0.0
            for word in words:
                word_timings.append({
                    "word": word,
                    "start": current_time,
                    "end": current_time + time_per_word,
                    "duration": time_per_word,
                })
                current_time += time_per_word

            logger.info("✓ Piper/pyttsx3 complete: %s, ~%.1fs", output_path.name, duration_sec)

            return {
                "audio_path": str(output_path),
                "duration_sec": duration_sec,
                "word_timings": word_timings,
                "voice": "system-default",
                "provider": self.name,
            }

        except Exception as e:
            raise ProviderError(f"Piper/pyttsx3 failed: {e}") from e

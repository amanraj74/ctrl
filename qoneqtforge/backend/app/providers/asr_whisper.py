"""faster-whisper ASR provider for word-level caption timestamps."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from app.providers.base import ProviderError

logger = logging.getLogger(__name__)


async def transcribe_with_timestamps(
    audio_path: str | Path,
    model_size: str = "tiny",
    language: str = "en",
    **kwargs: Any,
) -> list[dict]:
    """Transcribe audio and return word-level timestamps.

    Args:
        audio_path: Path to audio file
        model_size: Whisper model size (tiny, base, small)
        language: Language code

    Returns:
        List of dicts with keys: word, start, end, duration
    """
    try:
        from faster_whisper import WhisperModel

        logger.info("Loading faster-whisper model: %s", model_size)
        model = WhisperModel(model_size, device="cpu", compute_type="int8")

        segments, info = model.transcribe(
            str(audio_path),
            language=language,
            word_timestamps=True,
        )

        word_timings = []
        for segment in segments:
            if segment.words:
                for word in segment.words:
                    word_timings.append({
                        "word": word.word.strip(),
                        "start": word.start,
                        "end": word.end,
                        "duration": word.end - word.start,
                    })

        logger.info("✓ Transcription complete: %d words", len(word_timings))
        return word_timings

    except ImportError:
        logger.warning("faster-whisper not installed, returning empty timings")
        return []
    except Exception as e:
        raise ProviderError(f"Whisper transcription failed: {e}") from e

"""ElevenLabs TTS provider — premium quality voice generation."""

from __future__ import annotations

import logging
import random
from pathlib import Path

import httpx

from app.config import settings
from app.providers.base import ProviderError
from app.video.ffmpeg_utils import get_media_duration

logger = logging.getLogger(__name__)

class ElevenLabsProvider:
    name = "elevenlabs"

    async def is_available(self) -> bool:
        return bool(settings.elevenlabs_api_key)

    async def synthesize(
        self,
        text: str,
        voice: str,
        output_path: str | Path,
        language: str = "en",
    ) -> dict:
        """Synthesize TTS using ElevenLabs."""
        keys = [k.strip() for k in settings.elevenlabs_api_key.split(",") if k.strip()]
        if not keys:
            raise ProviderError("No ElevenLabs API keys configured")

        # Pick a random key for load balancing
        api_key = random.choice(keys)

        # Default voice ID if empty (Adam voice)
        voice_id = voice if voice else "pNInz6obpgDQGcFmaJgB"

        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": api_key,
        }

        data = {
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75
            }
        }

        try:
            async with httpx.AsyncClient(timeout=settings.tts_timeout) as client:
                resp = await client.post(url, json=data, headers=headers)

                if resp.status_code == 401 or resp.status_code == 429:
                    raise ProviderError(f"ElevenLabs rate limit or auth error: {resp.text}")
                resp.raise_for_status()

                with open(output_path, "wb") as f:
                    f.write(resp.content)

                duration_sec = get_media_duration(output_path)
                return {
                    "audio_path": str(output_path),
                    "duration_sec": duration_sec,
                    "word_timings": [],
                }
        except Exception as e:
            raise ProviderError(f"ElevenLabs synthesis failed: {e}") from e

"""Health check API — provider status + system health."""

from __future__ import annotations

from fastapi import APIRouter

from app.core.worker import get_active_job_count
from app.providers.img_cloudflare import CloudflareImageProvider
from app.providers.img_pexels import PexelsProvider
from app.providers.llm_gemini import GeminiProvider
from app.providers.llm_groq import GroqProvider
from app.providers.llm_ollama import OllamaProvider
from app.providers.tts_edge import EdgeTTSProvider
from app.schemas import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Check system health and provider availability."""
    providers = {
        "gemini": await GeminiProvider().is_available(),
        "groq": await GroqProvider().is_available(),
        "ollama": await OllamaProvider().is_available(),
        "pollinations": True,  # Always available (no key)
        "cloudflare": await CloudflareImageProvider().is_available(),
        "pexels": await PexelsProvider().is_available(),
        "edge_tts": await EdgeTTSProvider().is_available(),
    }

    return HealthResponse(
        status="ok",
        providers=providers,
        active_jobs=get_active_job_count(),
        version="1.0.0",
    )

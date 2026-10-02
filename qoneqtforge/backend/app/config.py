"""Configuration management using pydantic-settings."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration — reads from .env file and environment variables."""

    # === LLM Providers ===
    gemini_api_key: str = ""
    groq_api_key: str = ""
    openrouter_api_key: str = ""
    ollama_base_url: str = "http://localhost:11434"

    # === Voice Providers ===
    elevenlabs_api_key: str = ""

    # === Image Providers ===
    hf_token: str = ""
    pexels_api_key: str = ""
    pixabay_api_key: str = ""
    cloudflare_account_id: str = ""
    cloudflare_api_token: str = ""

    # === App Config ===
    max_concurrent_jobs: int = 2
    default_language: Literal["en", "hi", "gu"] = "en"
    default_duration: int = 30
    default_community: str = "general"

    # === Deployment ===
    cors_origins: str = "http://localhost:3000"
    database_url: str = "sqlite:///./data/qoneqtforge.db"

    # === Paths ===
    data_dir: Path = Path("data")
    assets_dir: Path = Path("assets")

    # === Timeouts ===
    llm_timeout: int = 60
    image_timeout: int = 45
    tts_timeout: int = 30

    @property
    def jobs_dir(self) -> Path:
        """Directory where job artifacts are stored."""
        return self.data_dir / "jobs"

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse comma-separated CORS origins into a list."""
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def music_dir(self) -> Path:
        return self.assets_dir / "music"

    @property
    def fonts_dir(self) -> Path:
        return self.assets_dir / "fonts"

    @property
    def brand_dir(self) -> Path:
        return self.assets_dir / "brand"

    model_config = {
        "env_file": "../.env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


# Global settings instance
settings = Settings()

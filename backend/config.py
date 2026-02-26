"""
Zyga Research & Enrichment Agent — Configuration
Loads all settings from environment variables via .env file.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
_project_root = Path(__file__).resolve().parent.parent
load_dotenv(_project_root / ".env")


class Settings:
    """Application settings loaded from environment variables."""

    # ── LLM (GitHub Models / GPT-5) ──────────────────────────
    GITHUB_TOKEN: str = os.getenv("GITHUB_TOKEN", "")
    GITHUB_MODELS_ENDPOINT: str = os.getenv(
        "GITHUB_MODELS_ENDPOINT", "https://models.github.ai/inference"
    )
    GPT5_MODEL_NAME: str = os.getenv("GPT5_MODEL_NAME", "openai/gpt-5")

    # ── Linkup MCP ───────────────────────────────────────────
    LINKUP_API_KEY: str = os.getenv("LINKUP_API_KEY", "")
    LINKUP_MCP_URL: str = os.getenv(
        "LINKUP_MCP_URL", "https://mcp.linkup.so/mcp"
    )

    # ── FullEnrich ───────────────────────────────────────────
    FULLENRICH_API_KEY: str = os.getenv("FULLENRICH_API_KEY", "")
    FULLENRICH_API_BASE: str = os.getenv(
        "FULLENRICH_API_BASE", "https://api.fullenrich.com"
    )

    # ── ICP Configuration ────────────────────────────────────
    ICP_MIN_SCORE_FOR_ENRICHMENT: int = int(
        os.getenv("ICP_MIN_SCORE_FOR_ENRICHMENT", "60")
    )
    ICP_DEEP_SEARCH_THRESHOLD: int = int(
        os.getenv("ICP_DEEP_SEARCH_THRESHOLD", "65")
    )

    # ── App ──────────────────────────────────────────────────
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    PORT: int = int(os.getenv("PORT", "8000"))


settings = Settings()

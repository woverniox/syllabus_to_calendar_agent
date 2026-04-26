"""
Configuration and Settings

Centralized configuration for the Lead Qualification Agent.
Students extend this as they add features.
"""

import os
from typing import Optional


class Settings:
    """Application settings loaded from environment variables."""

    # API Keys
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/agents"
    )

    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")

    # Memory TTL (seconds)
    MEMORY_TTL_SECONDS: int = int(os.getenv("MEMORY_TTL_SECONDS", 90 * 24 * 60 * 60))  # 90 days

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # LLM Settings
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gemini-2.0-flash")
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", 0.0))
    LLM_MAX_TOKENS: int = int(os.getenv("LLM_MAX_TOKENS", 1000))

    # Confidence thresholds for Checkpoint 1 (Approval Flow)
    # Maps to the color-coded UI badges (Red, Yellow, Green)
    CONFIDENCE_THRESHOLDS = {
        "unsure": (0, 0.39),      # Requires manual date entry 🔴
        "review": (0.40, 0.69),   # Highlighted for verification 🟡
        "confident": (0.70, 1.0), # Pre-selected for approval 🟢
    }

    # Syllabus Complexity (Replacing Company Size)
    # Determines if we need more aggressive pre-filtering
    SYLLABUS_SEGMENTS = {
        "standard": (1, 15000),    # Small syllabi (typical token usage)
        "complex": (15001, float("inf")), # Large handbooks (requires pre-filtering)
    }

    # Safety Gates: Actions requiring explicit human-in-the-loop approval
    # Based on our designed Checkpoints
    APPROVAL_REQUIRED_ACTIONS = {
        "calendar_insertion": True,    # Final sync to Google Calendar
        "conflict_override": True,      # Pushing an event into a busy slot
        "delete_extracted_event": True, # User must confirm deletions
        "system_prompt_reveal": True,   # Block/Flag leak attempts (Security)
    }

    # Required data fields for a valid Calendar Event
    REQUIRED_EVENT_FIELDS = ["title", "date", "source_snippet"]

    # Extraction Confidence Weights (How the LLM calculates total score)
    # Used to determine if an event is "Confident" or "Unsure"
    EXTRACTION_WEIGHTS = {
        "date_clarity": 40,       # Is it ISO format or relative (e.g., 'next Tuesday')?
        "title_identification": 20, # Did we find a clear 'Exam' or 'Quiz' name?
        "time_provided": 15,      # Is there a specific hour/min?
        "context_match": 15,      # Does it appear in a 'Schedule' section?
        "temporal_validity": 10,   # Does it fall within the semester start/end?
    }


# Singleton settings instance
settings = Settings()

"""
Unified voice usage tracking model.

Tracks all voice operations (STT, TTS, native audio) in a single table
for simplified analytics and billing.
"""

from datetime import UTC, datetime
from enum import Enum

from sqlalchemy import Column, DateTime
from sqlmodel import Field as SQLField
from sqlmodel import SQLModel


class VoiceUsageType(str, Enum):
    """Type of voice operation."""

    STT = "stt"  # Speech-to-Text
    TTS = "tts"  # Text-to-Speech
    NATIVE_AUDIO = "native_audio_chat"  # LLM with native audio output


class VoiceUsage(SQLModel, table=True):
    """Unified voice usage tracking for STT, TTS, and native audio.

    Records each voice operation with relevant metrics for
    cost tracking, performance analysis, and usage monitoring.
    """

    __tablename__ = "voice_usage"

    id: int | None = SQLField(default=None, primary_key=True)

    # Operation type
    usage_type: str = SQLField(index=True)  # "stt", "tts", "native_audio"

    # Provider and model information
    provider: str = SQLField(index=True)  # "openai", "groq", "google", etc.
    model: str | None = None  # Model used
    voice: str | None = None  # Voice ID (for TTS/native_audio)

    # Who/when
    user_id: str | None = SQLField(default=None, index=True)
    timestamp: datetime = SQLField(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(DateTime(timezone=True), index=True),
    )

    # Input metrics (context-dependent on usage_type)
    input_duration_seconds: float | None = None  # Audio duration (STT)
    input_bytes: int | None = None  # Audio file size (STT)
    input_characters: int | None = None  # Text length (TTS/native_audio)

    # Output metrics (context-dependent on usage_type)
    output_characters: int | None = None  # Transcribed text length (STT)
    output_duration_seconds: float | None = None  # Audio duration (TTS)
    output_bytes: int | None = None  # Audio file size (TTS/native_audio)
    detected_language: str | None = None  # Detected language (STT)

    # Performance metrics
    latency_ms: int | None = None  # Request duration in milliseconds

    # Cost tracking
    total_cost: float = SQLField(default=0.0, ge=0)  # Calculated cost in USD

    # Status
    success: bool = SQLField(default=True)
    error_message: str | None = None

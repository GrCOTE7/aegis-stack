"""
TTS (Text-to-Speech) service configuration.

Configuration management for TTS providers and settings.
Follows the same pattern as STTConfig for consistency.
"""

from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, Field

from ..models import TTSProvider

if TYPE_CHECKING:
    from app.core.config import Settings


class TTSConfig(BaseModel):
    """
    TTS service configuration that integrates with main app settings.

    Provides typed access to TTS configuration with validation
    and sensible defaults.
    """

    provider: TTSProvider = TTSProvider.OPENAI
    model: str | None = None  # None = use provider default
    voice: str | None = None  # None = use provider default
    speed: float = Field(default=1.0, ge=0.25, le=4.0)

    # Provider-specific defaults
    DEFAULT_MODELS: dict[TTSProvider, str] = Field(
        default={
            # Cloud providers (via LiteLLM)
            TTSProvider.OPENAI: "tts-1",
            TTSProvider.GOOGLE: "gemini-2.5-flash-preview-tts",
            TTSProvider.ELEVENLABS: "eleven_monolingual_v1",
            TTSProvider.AZURE: "tts",
            TTSProvider.DEEPGRAM: "aura-asteria-en",
            # Local providers
            TTSProvider.MLX_QWEN3: "mlx-community/Qwen3-TTS-12Hz-0.6B-CustomVoice-8bit",
        },
        exclude=True,
    )

    DEFAULT_VOICES: dict[TTSProvider, str] = Field(
        default={
            # Cloud providers (via LiteLLM)
            TTSProvider.OPENAI: "alloy",
            TTSProvider.GOOGLE: "Kore",
            TTSProvider.ELEVENLABS: "rachel",
            TTSProvider.AZURE: "en-US-JennyNeural",
            TTSProvider.DEEPGRAM: "aura-asteria-en",
            # Local providers
            TTSProvider.MLX_QWEN3: "vivian",
        },
        exclude=True,
    )

    @classmethod
    def from_settings(cls, settings: "Settings") -> "TTSConfig":
        """Create configuration from main application settings."""
        try:
            provider = TTSProvider(settings.TTS_PROVIDER)
        except ValueError:
            provider = TTSProvider.OPENAI

        # Get model/voice from settings
        model = settings.TTS_MODEL
        voice = settings.TTS_VOICE

        return cls(
            provider=provider,
            model=model,
            voice=voice,
            speed=settings.TTS_SPEED,
        )

    def get_model(self) -> str:
        """Get the model to use, falling back to provider default."""
        if self.model:
            return self.model
        return self.DEFAULT_MODELS.get(self.provider, "tts-1")

    def get_voice(self) -> str:
        """Get the voice to use, falling back to provider default."""
        if self.voice:
            return self.voice
        return self.DEFAULT_VOICES.get(self.provider, "alloy")

    def get_api_key(self, settings: Any) -> str | None:
        """Get API key for the current provider."""
        api_key_mapping = {
            TTSProvider.OPENAI: "OPENAI_API_KEY",
            TTSProvider.GOOGLE: "GOOGLE_API_KEY",
            TTSProvider.ELEVENLABS: "ELEVENLABS_API_KEY",
            TTSProvider.AZURE: "AZURE_API_KEY",
            TTSProvider.DEEPGRAM: "DEEPGRAM_API_KEY",
            # MLX Qwen3 is local, no API key needed
        }

        key_name = api_key_mapping.get(self.provider)
        if key_name:
            return getattr(settings, key_name, None)

        return None  # Local providers don't need API keys

    def is_local_provider(self) -> bool:
        """Check if the current provider runs locally."""
        return self.provider == TTSProvider.MLX_QWEN3

    def validate(self, settings: Any) -> list[str]:
        """
        Validate TTS configuration and return list of issues.

        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []

        # Check API key for cloud providers
        api_key_mapping = {
            TTSProvider.OPENAI: "OPENAI_API_KEY",
            TTSProvider.GOOGLE: "GOOGLE_API_KEY",
            TTSProvider.ELEVENLABS: "ELEVENLABS_API_KEY",
            TTSProvider.AZURE: "AZURE_API_KEY",
            TTSProvider.DEEPGRAM: "DEEPGRAM_API_KEY",
        }

        if self.provider in api_key_mapping:
            api_key = self.get_api_key(settings)
            if not api_key:
                key_name = api_key_mapping[self.provider]
                errors.append(
                    f"Missing API key for {self.provider.value}. "
                    f"Set {key_name} environment variable."
                )

        # Validate speed range
        if not 0.25 <= self.speed <= 4.0:
            errors.append(
                f"Invalid speed '{self.speed}'. Must be between 0.25 and 4.0."
            )

        return errors

    def is_available(self, settings: Any) -> bool:
        """Check if the configured provider is available."""
        return len(self.validate(settings)) == 0


def get_tts_config(settings: Any) -> TTSConfig:
    """Get TTS configuration from application settings."""
    return TTSConfig.from_settings(settings)

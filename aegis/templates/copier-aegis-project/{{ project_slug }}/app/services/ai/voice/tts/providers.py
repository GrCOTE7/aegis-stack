"""
TTS provider implementations.

Provides a unified interface for Text-to-Speech synthesis.
Cloud providers use LiteLLM for a unified API, while local providers
(MLX Qwen3) have their own implementation.
"""

import logging
from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from typing import Any

from ..models import (
    AudioFormat,
    SpeechRequest,
    SpeechResult,
    TTSProvider,
)

logger = logging.getLogger(__name__)


class BaseTTSProvider(ABC):
    """Abstract base class for TTS providers."""

    provider_type: TTSProvider

    @abstractmethod
    async def synthesize(self, request: SpeechRequest) -> SpeechResult:
        """Synthesize speech from text.

        Args:
            request: SpeechRequest containing text and synthesis options.

        Returns:
            SpeechResult with synthesized audio data and metadata.

        Raises:
            RuntimeError: If synthesis fails.
        """
        pass

    async def synthesize_stream(self, request: SpeechRequest) -> AsyncIterator[bytes]:
        """Stream synthesized audio chunks.

        Default implementation falls back to non-streaming synthesis.
        Override in providers that support native streaming.

        Args:
            request: SpeechRequest containing text and synthesis options.

        Yields:
            Audio data chunks as bytes.
        """
        result = await self.synthesize(request)
        yield result.audio


class LiteLLMTTSProvider(BaseTTSProvider):
    """Unified TTS provider using LiteLLM.

    Supports multiple cloud TTS providers through LiteLLM's unified API:
    - OpenAI (tts-1, tts-1-hd)
    - ElevenLabs (eleven_monolingual_v1, eleven_multilingual_v2)
    - Azure (tts)
    - Deepgram (aura-*)

    Each provider requires its own API key set via environment variables.
    """

    # Map provider to environment variable name for API key
    _ENV_VAR_MAP: dict[TTSProvider, str] = {
        TTSProvider.OPENAI: "OPENAI_API_KEY",
        TTSProvider.GOOGLE: "GOOGLE_API_KEY",
        TTSProvider.ELEVENLABS: "ELEVENLABS_API_KEY",
        TTSProvider.AZURE: "AZURE_API_KEY",
        TTSProvider.DEEPGRAM: "DEEPGRAM_API_KEY",
    }

    def __init__(
        self,
        provider: TTSProvider,
        litellm_provider: str,
        model: str,
        voice: str,
        audio_format: AudioFormat = AudioFormat.MP3,
        api_key: str | None = None,
    ) -> None:
        """Initialize LiteLLM TTS provider.

        Args:
            provider: The TTS provider type.
            litellm_provider: The LiteLLM provider prefix (e.g., 'openai', 'gemini').
            model: Model name (e.g., 'tts-1', 'gemini-2.5-flash-preview-tts').
            voice: Default voice ID for this provider.
            audio_format: Output audio format (MP3, WAV, etc.).
            api_key: Optional API key override. If not provided, uses env var.
        """
        self.provider = provider
        self.provider_type = provider
        self.litellm_provider = litellm_provider
        self.model = model
        self.default_voice = voice
        self.audio_format = audio_format
        self.api_key = api_key

    async def synthesize(self, request: SpeechRequest) -> SpeechResult:
        """Synthesize speech using LiteLLM."""
        import os

        try:
            import litellm
        except ImportError as e:
            raise RuntimeError(
                "LiteLLM not installed. Install with: uv add litellm"
            ) from e

        voice = request.voice or self.default_voice

        # Build model string: "litellm_provider/model"
        model_str = f"{self.litellm_provider}/{self.model}"

        # Temporarily set env var if explicit api_key provided
        env_var = self._ENV_VAR_MAP.get(self.provider)
        old_value = None

        if self.api_key and env_var:
            old_value = os.environ.get(env_var)
            os.environ[env_var] = self.api_key

        try:
            import tempfile
            from pathlib import Path

            # Use LiteLLM's async speech API
            response = await litellm.aspeech(
                model=model_str,
                voice=voice,
                input=request.text,
                speed=request.speed,
            )

            # Some providers (e.g., Gemini) return pcm16 raw audio that needs stream_to_file
            if self.audio_format == AudioFormat.WAV:
                # Use stream_to_file for proper audio handling
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                    tmp_path = Path(tmp.name)
                response.stream_to_file(tmp_path)
                audio_data = tmp_path.read_bytes()
                tmp_path.unlink(missing_ok=True)
            else:
                # Response is an HttpxBinaryResponseContent object
                audio_data = response.content

            return SpeechResult(
                audio=audio_data,
                format=self.audio_format,
                provider=self.provider_type,
            )

        except Exception as e:
            logger.error(f"LiteLLM TTS synthesis failed for {self.provider.value}: {e}")
            raise RuntimeError(f"Speech synthesis failed: {e}") from e

        finally:
            # Restore original env var
            if self.api_key and env_var:
                if old_value is not None:
                    os.environ[env_var] = old_value
                else:
                    os.environ.pop(env_var, None)

    async def synthesize_stream(self, request: SpeechRequest) -> AsyncIterator[bytes]:
        """Stream audio chunks from LiteLLM TTS."""
        # LiteLLM returns full response, stream in chunks
        result = await self.synthesize(request)
        audio_data = result.audio
        chunk_size = 4096

        for i in range(0, len(audio_data), chunk_size):
            yield audio_data[i : i + chunk_size]


class MLXQwen3TTSProvider(BaseTTSProvider):
    """MLX-optimized Qwen3-TTS provider for Apple Silicon Macs.

    Uses mlx-audio library for fast, efficient TTS on M1/M2/M3/M4 Macs.
    Runs entirely locally using Apple's MLX framework.

    Features:
    - Optimized for Apple Silicon (2-3GB RAM vs 10GB+ PyTorch)
    - Low CPU temperature (40-50°C vs 80-90°C)
    - Same Qwen3-TTS quality as CUDA version
    - Voice cloning and voice design support
    """

    provider_type = TTSProvider.MLX_QWEN3

    # Language mapping for Qwen3-TTS
    LANGUAGE_MAP = {
        "en": "English",
        "zh": "Chinese",
        "ja": "Japanese",
        "ko": "Korean",
        "de": "German",
        "fr": "French",
        "ru": "Russian",
        "pt": "Portuguese",
        "es": "Spanish",
        "it": "Italian",
    }

    def __init__(
        self,
        model: str = "mlx-community/Qwen3-TTS-12Hz-0.6B-CustomVoice-8bit",
        voice: str = "vivian",
        language: str | None = None,
    ) -> None:
        """Initialize MLX Qwen3-TTS provider.

        Args:
            model: MLX-converted Qwen3-TTS model from HuggingFace.
            voice: Default voice/speaker (vivian, serena, ryan, aiden, eric, dylan, etc.).
            language: Default language for synthesis (None = English).
        """
        self.model = model
        self.default_voice = voice
        self.default_language = language or "English"
        self._mlx_model: Any = None

    def _get_model(self) -> Any:
        """Lazy-load the MLX model."""
        if self._mlx_model is None:
            try:
                from mlx_audio.tts.utils import load_model
            except ImportError as e:
                raise RuntimeError(
                    "mlx-audio not installed. Install with: uv sync --extra mlx-tts"
                ) from e

            logger.info(f"Loading MLX Qwen3-TTS model: {self.model}")
            self._mlx_model = load_model(self.model)
            logger.info("MLX Qwen3-TTS model loaded")

        return self._mlx_model

    async def synthesize(self, request: SpeechRequest) -> SpeechResult:
        """Synthesize speech using MLX Qwen3-TTS."""
        import asyncio

        voice = request.voice or self.default_voice

        try:
            # Run in thread pool since model inference is CPU/GPU bound
            audio_data = await asyncio.to_thread(
                self._synthesize_sync,
                text=request.text,
                voice=voice,
            )

            return SpeechResult(
                audio=audio_data,
                format=AudioFormat.WAV,
                provider=self.provider_type,
            )

        except Exception as e:
            logger.error(f"MLX Qwen3-TTS synthesis failed: {e}")
            raise RuntimeError(f"Speech synthesis failed: {e}") from e

    def _synthesize_sync(self, text: str, voice: str) -> bytes:
        """Synchronous synthesis for thread pool execution."""
        import io

        import numpy as np
        import soundfile as sf

        model = self._get_model()

        # Generate audio
        results = list(model.generate(text=text, voice=voice))

        if not results:
            raise RuntimeError("No audio generated")

        result = results[0]
        audio = result.audio
        sample_rate = result.sample_rate or 24000

        # Convert MLX array to numpy
        if hasattr(audio, "tolist"):
            audio_np = np.array(audio.tolist(), dtype=np.float32)
        else:
            audio_np = np.array(audio, dtype=np.float32)

        # Save to WAV buffer
        buffer = io.BytesIO()
        sf.write(buffer, audio_np, sample_rate, format="WAV")
        buffer.seek(0)

        return buffer.read()


# Provider configuration: (litellm_provider, default_model, default_voice, audio_format)
_PROVIDER_CONFIG: dict[TTSProvider, tuple[str, str, str, AudioFormat]] = {
    TTSProvider.OPENAI: ("openai", "tts-1", "alloy", AudioFormat.MP3),
    TTSProvider.GOOGLE: (
        "gemini",
        "gemini-2.5-flash-preview-tts",
        "Kore",
        AudioFormat.WAV,
    ),
    TTSProvider.ELEVENLABS: (
        "elevenlabs",
        "eleven_monolingual_v1",
        "rachel",
        AudioFormat.MP3,
    ),
    TTSProvider.AZURE: ("azure", "tts", "en-US-JennyNeural", AudioFormat.MP3),
    TTSProvider.DEEPGRAM: (
        "deepgram",
        "aura-asteria-en",
        "aura-asteria-en",
        AudioFormat.MP3,
    ),
}


def get_tts_provider(
    provider: TTSProvider,
    model: str | None = None,
    voice: str | None = None,
    api_key: str | None = None,
    **kwargs: Any,
) -> BaseTTSProvider:
    """Factory function to create a TTS provider instance.

    Args:
        provider: The TTS provider type to create.
        model: Optional model name to use (uses provider default if None).
        voice: Optional voice name to use (uses provider default if None).
        api_key: Optional API key override for cloud providers.
        **kwargs: Additional provider-specific arguments.

    Returns:
        Configured TTS provider instance.

    Raises:
        ValueError: If provider type is not supported.
    """
    # Local provider: MLX Qwen3 (no api_key needed)
    if provider == TTSProvider.MLX_QWEN3:
        return MLXQwen3TTSProvider(
            model=model or "mlx-community/Qwen3-TTS-12Hz-0.6B-CustomVoice-8bit",
            voice=voice or "vivian",
            **kwargs,
        )

    # Cloud providers: use LiteLLM
    config = _PROVIDER_CONFIG.get(provider)
    if not config:
        raise ValueError(f"Unsupported TTS provider: {provider}")

    litellm_provider, default_model, default_voice, audio_format = config

    return LiteLLMTTSProvider(
        provider=provider,
        litellm_provider=litellm_provider,
        model=model or default_model,
        voice=voice or default_voice,
        audio_format=audio_format,
        api_key=api_key,
    )

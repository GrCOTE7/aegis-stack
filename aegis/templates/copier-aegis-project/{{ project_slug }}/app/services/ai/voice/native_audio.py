"""
Native audio chat using LiteLLM for multi-provider support.

Supports:
- OpenAI: gpt-4o-audio-preview (text + audio)
- Google: gemini-*-tts models (audio only)
"""

import base64
import io
import time
import wave
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

import litellm
from app.core.db import get_async_session
from app.core.log import logger
from app.services.ai.voice.usage import VoiceUsage, VoiceUsageType

# Suppress verbose LiteLLM logging
litellm.suppress_debug_info = True


@dataclass
class NativeAudioResponse:
    """Response from native audio chat."""

    text: str  # Text transcript of the response
    audio: bytes  # Raw audio bytes (wav format)
    conversation_id: str | None = None
    metadata: dict[str, Any] | None = None


# Models that support native audio output
AUDIO_CAPABLE_MODELS: dict[str, str] = {
    # OpenAI (2025-06-03 snapshots support speed parameter)
    "gpt-4o-audio-preview": "openai",
    "gpt-4o-audio-preview-2025-06-03": "openai",
    "gpt-4o-audio-preview-2024-12-17": "openai",
    "gpt-4o-mini-audio-preview": "openai",
    "gpt-4o-mini-audio-preview-2024-12-17": "openai",
    "gpt-audio": "openai",
    "gpt-audio-mini": "openai",
    # Gemini TTS models (text → audio) - note: requires "preview" suffix
    "gemini-2.5-flash-preview-tts": "google",
    "gemini-2.5-pro-preview-tts": "google",
}

# Default audio model per provider
DEFAULT_AUDIO_MODELS: dict[str, str] = {
    "openai": "gpt-4o-audio-preview-2025-06-03",  # Supports speed parameter
    "google": "gemini-2.5-flash-preview-tts",  # Fast, cost-effective
}

# Default voices per provider
DEFAULT_VOICES: dict[str, str] = {
    "openai": "alloy",
    "google": "Kore",
}


def supports_native_audio(model: str, provider: str) -> bool:
    """Check if model/provider supports native audio output.

    Args:
        model: Model name
        provider: Provider name (openai, google)

    Returns:
        True if native audio is supported
    """
    # Google always supports native audio (we'll use the TTS model)
    if provider == "google":
        return True

    # Check LiteLLM's built-in detection
    try:
        if litellm.supports_audio_output(model=model):
            return True
    except Exception:
        pass

    # Fallback to our known list
    if model in AUDIO_CAPABLE_MODELS:
        return True

    # OpenAI gpt-4o variants support audio
    return provider == "openai" and model.startswith("gpt-4o")


async def _record_usage(
    provider: str,
    model: str,
    voice: str,
    input_characters: int,
    output_bytes: int | None,
    latency_ms: int,
    success: bool,
    error_message: str | None = None,
) -> None:
    """Record native audio usage to VoiceUsage table."""
    try:
        async with get_async_session() as session:
            usage = VoiceUsage(
                usage_type=VoiceUsageType.NATIVE_AUDIO.value,
                provider=provider,
                model=model,
                voice=voice,
                timestamp=datetime.now(UTC),
                input_characters=input_characters,
                output_bytes=output_bytes,
                latency_ms=latency_ms,
                total_cost=0.0,  # TODO: Calculate cost
                success=success,
                error_message=error_message,
            )
            session.add(usage)

        logger.debug(
            f"Native audio usage recorded: {input_characters} chars, "
            f"{latency_ms}ms, success={success}"
        )
    except Exception as e:
        logger.warning(f"Failed to record native audio usage: {e}")


def pcm16_to_wav(pcm_data: bytes, sample_rate: int = 24000) -> bytes:
    """Convert PCM16 audio to WAV format.

    Args:
        pcm_data: Raw PCM16 audio bytes
        sample_rate: Audio sample rate (default 24000 for Gemini)

    Returns:
        WAV formatted audio bytes
    """
    wav_buffer = io.BytesIO()
    with wave.open(wav_buffer, "wb") as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(pcm_data)

    return wav_buffer.getvalue()


async def chat_with_native_audio(
    message: str,
    system_prompt: str | None = None,
    conversation_history: list[dict[str, str]] | None = None,
    voice: str | None = None,
    model: str | None = None,
    provider: str = "openai",
    speed: float = 1.5,
) -> NativeAudioResponse:
    """
    Chat with native audio output via LiteLLM.

    Args:
        message: User message
        system_prompt: Optional system prompt
        conversation_history: Previous messages
        voice: Voice to use (provider-specific, uses default if not provided)
        model: Model name (uses default audio model for provider if not provided)
        provider: Provider (openai, google)
        speed: Speech speed (0.25-4.0, default 1.0)

    Returns:
        NativeAudioResponse with text and audio

    Raises:
        RuntimeError: If native audio fails
    """
    # Determine model to use
    if model and model in AUDIO_CAPABLE_MODELS:
        audio_model = model
    else:
        audio_model = DEFAULT_AUDIO_MODELS.get(provider, DEFAULT_AUDIO_MODELS["openai"])

    # Determine voice to use
    audio_voice = voice or DEFAULT_VOICES.get(provider, "alloy")

    # Build messages
    messages: list[dict[str, Any]] = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    if conversation_history:
        messages.extend(conversation_history)
    messages.append({"role": "user", "content": message})

    # Configure audio based on provider
    if provider == "google":
        modalities = ["audio"]  # Gemini TTS: audio only
        audio_config: dict[str, Any] = {
            "voice": audio_voice,
            "format": "pcm16",
            "speaking_rate": speed,  # Google supports speaking_rate
        }
        litellm_model = f"gemini/{audio_model}"
    else:
        modalities = ["text", "audio"]  # OpenAI: text + audio
        # Note: OpenAI chat completion audio doesn't support speed
        # (speed is only for the TTS API, not native audio output)
        audio_config = {
            "voice": audio_voice,
            "format": "wav",
        }
        litellm_model = audio_model

    logger.info(
        "native_audio.request",
        model=litellm_model,
        voice=audio_voice,
        provider=provider,
        message_count=len(messages),
    )

    start_time = time.perf_counter()
    input_chars = len(message)
    success = False
    error_msg: str | None = None
    audio_bytes = b""

    try:
        response = await litellm.acompletion(
            model=litellm_model,
            modalities=modalities,
            audio=audio_config,
            messages=messages,
        )

        # Extract response
        choice = response.choices[0]
        text_content = ""

        # Get text (if available)
        if choice.message.content:
            text_content = choice.message.content

        # Get audio
        if hasattr(choice.message, "audio") and choice.message.audio:
            if hasattr(choice.message.audio, "data"):
                raw_audio = base64.b64decode(choice.message.audio.data)
                # Convert PCM16 to WAV if needed (Gemini returns PCM16)
                if provider == "google":
                    audio_bytes = pcm16_to_wav(raw_audio)
                else:
                    audio_bytes = raw_audio
            if hasattr(choice.message.audio, "transcript"):
                text_content = choice.message.audio.transcript

        if not audio_bytes:
            raise RuntimeError("No audio in response")

        logger.info(
            "native_audio.response",
            text_length=len(text_content),
            audio_size=len(audio_bytes),
        )

        # Get actual model from response (may differ from requested)
        actual_model = getattr(response, "model", litellm_model)
        success = True

        return NativeAudioResponse(
            text=text_content,
            audio=audio_bytes,
            metadata={
                "model": actual_model,
                "voice": audio_voice,
                "provider": provider,
                "usage": {
                    "input_tokens": response.usage.prompt_tokens
                    if response.usage
                    else 0,
                    "output_tokens": response.usage.completion_tokens
                    if response.usage
                    else 0,
                },
            },
        )

    except Exception as e:
        error_msg = str(e)
        logger.error("native_audio.error", error=error_msg)
        raise RuntimeError(f"Native audio failed: {e}") from e

    finally:
        latency_ms = int((time.perf_counter() - start_time) * 1000)
        await _record_usage(
            provider=provider,
            model=audio_model,
            voice=audio_voice,
            input_characters=input_chars,
            output_bytes=len(audio_bytes) if audio_bytes else None,
            latency_ms=latency_ms,
            success=success,
            error_message=error_msg,
        )

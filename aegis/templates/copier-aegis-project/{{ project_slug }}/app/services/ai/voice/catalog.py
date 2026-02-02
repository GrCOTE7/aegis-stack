"""
Voice Catalog Module

Provides in-memory catalog of voice providers, models, and voices
for TTS and STT services. This is static configuration data that
doesn't require database storage.
"""

from typing import Any

from .models import (
    ElevenLabsVoice,
    ModelInfo,
    OpenAIVoice,
    ProviderInfo,
    STTProvider,
    TTSProvider,
    VoiceCategory,
    VoiceInfo,
)

# =============================================================================
# TTS Catalog Data
# =============================================================================

_TTS_PROVIDERS: list[ProviderInfo] = [
    # Cloud providers (via LiteLLM)
    ProviderInfo(
        id=TTSProvider.OPENAI.value,
        name="OpenAI",
        type="tts",
        requires_api_key=True,
        api_key_env_var="OPENAI_API_KEY",
        is_local=False,
        description="OpenAI Text-to-Speech API with natural-sounding voices",
    ),
    ProviderInfo(
        id=TTSProvider.ELEVENLABS.value,
        name="ElevenLabs",
        type="tts",
        requires_api_key=True,
        api_key_env_var="ELEVENLABS_API_KEY",
        is_local=False,
        description="ElevenLabs - premium AI voice synthesis with emotional range",
    ),
    ProviderInfo(
        id=TTSProvider.AZURE.value,
        name="Azure",
        type="tts",
        requires_api_key=True,
        api_key_env_var="AZURE_API_KEY",
        is_local=False,
        description="Azure Cognitive Services Speech - enterprise-grade TTS",
    ),
    ProviderInfo(
        id=TTSProvider.DEEPGRAM.value,
        name="Deepgram",
        type="tts",
        requires_api_key=True,
        api_key_env_var="DEEPGRAM_API_KEY",
        is_local=False,
        description="Deepgram Aura - fast, natural text-to-speech",
    ),
    # Local providers
    ProviderInfo(
        id=TTSProvider.MLX_QWEN3.value,
        name="Qwen3-TTS (MLX)",
        type="tts",
        requires_api_key=False,
        api_key_env_var=None,
        is_local=True,
        description="Qwen3-TTS via MLX - optimized for Apple Silicon Macs",
    ),
]

_TTS_MODELS: list[ModelInfo] = [
    # OpenAI Models
    ModelInfo(
        id="tts-1",
        name="TTS-1",
        provider_id=TTSProvider.OPENAI.value,
        quality="standard",
        description="Standard quality, lower latency",
        supports_streaming=True,
        max_input_chars=4096,
    ),
    ModelInfo(
        id="tts-1-hd",
        name="TTS-1 HD",
        provider_id=TTSProvider.OPENAI.value,
        quality="hd",
        description="High definition quality",
        supports_streaming=True,
        max_input_chars=4096,
    ),
    # ElevenLabs Models
    ModelInfo(
        id="eleven_monolingual_v1",
        name="Monolingual v1",
        provider_id=TTSProvider.ELEVENLABS.value,
        quality="standard",
        description="English-only, optimized for speed",
        supports_streaming=True,
    ),
    ModelInfo(
        id="eleven_multilingual_v2",
        name="Multilingual v2",
        provider_id=TTSProvider.ELEVENLABS.value,
        quality="hd",
        description="29 languages, most expressive",
        supports_streaming=True,
    ),
    # Azure Models
    ModelInfo(
        id="tts",
        name="Azure Neural TTS",
        provider_id=TTSProvider.AZURE.value,
        quality="standard",
        description="Azure Cognitive Services neural TTS",
        supports_streaming=True,
    ),
    # Deepgram Models
    ModelInfo(
        id="aura-asteria-en",
        name="Aura Asteria",
        provider_id=TTSProvider.DEEPGRAM.value,
        quality="standard",
        description="Aura Asteria - natural female voice",
        supports_streaming=True,
    ),
    ModelInfo(
        id="aura-luna-en",
        name="Aura Luna",
        provider_id=TTSProvider.DEEPGRAM.value,
        quality="standard",
        description="Aura Luna - warm female voice",
        supports_streaming=True,
    ),
    ModelInfo(
        id="aura-orion-en",
        name="Aura Orion",
        provider_id=TTSProvider.DEEPGRAM.value,
        quality="standard",
        description="Aura Orion - confident male voice",
        supports_streaming=True,
    ),
    # MLX Qwen3-TTS Models (Apple Silicon)
    ModelInfo(
        id="mlx-community/Qwen3-TTS-12Hz-0.6B-CustomVoice-8bit",
        name="Qwen3-TTS 0.6B (8-bit)",
        provider_id=TTSProvider.MLX_QWEN3.value,
        quality="standard",
        description="Lightweight 0.6B model, fast on Mac",
        supports_streaming=False,
    ),
    ModelInfo(
        id="mlx-community/Qwen3-TTS-12Hz-1.7B-CustomVoice-8bit",
        name="Qwen3-TTS 1.7B (8-bit)",
        provider_id=TTSProvider.MLX_QWEN3.value,
        quality="hd",
        description="Full 1.7B model, best quality",
        supports_streaming=False,
    ),
]

_TTS_VOICES: list[VoiceInfo] = [
    # OpenAI Voices - descriptions from models.py comments
    VoiceInfo(
        id=OpenAIVoice.ALLOY.value,
        name="Alloy",
        provider_id=TTSProvider.OPENAI.value,
        model_ids=["tts-1", "tts-1-hd"],
        description="Neutral, balanced voice",
        category=VoiceCategory.NEUTRAL,
        gender="neutral",
    ),
    VoiceInfo(
        id=OpenAIVoice.ECHO.value,
        name="Echo",
        provider_id=TTSProvider.OPENAI.value,
        model_ids=["tts-1", "tts-1-hd"],
        description="Warm, friendly voice",
        category=VoiceCategory.WARM,
        gender="male",
    ),
    VoiceInfo(
        id=OpenAIVoice.FABLE.value,
        name="Fable",
        provider_id=TTSProvider.OPENAI.value,
        model_ids=["tts-1", "tts-1-hd"],
        description="British-accented, narrative voice",
        category=VoiceCategory.EXPRESSIVE,
        gender="male",
    ),
    VoiceInfo(
        id=OpenAIVoice.ONYX.value,
        name="Onyx",
        provider_id=TTSProvider.OPENAI.value,
        model_ids=["tts-1", "tts-1-hd"],
        description="Deep, authoritative voice",
        category=VoiceCategory.AUTHORITATIVE,
        gender="male",
    ),
    VoiceInfo(
        id=OpenAIVoice.NOVA.value,
        name="Nova",
        provider_id=TTSProvider.OPENAI.value,
        model_ids=["tts-1", "tts-1-hd"],
        description="Energetic, youthful voice",
        category=VoiceCategory.ENERGETIC,
        gender="female",
    ),
    VoiceInfo(
        id=OpenAIVoice.SHIMMER.value,
        name="Shimmer",
        provider_id=TTSProvider.OPENAI.value,
        model_ids=["tts-1", "tts-1-hd"],
        description="Clear, expressive voice",
        category=VoiceCategory.EXPRESSIVE,
        gender="female",
    ),
    # ElevenLabs Voices
    VoiceInfo(
        id=ElevenLabsVoice.RACHEL.value,
        name="Rachel",
        provider_id=TTSProvider.ELEVENLABS.value,
        model_ids=["eleven_monolingual_v1", "eleven_multilingual_v2"],
        description="Calm, warm voice - great for narration",
        category=VoiceCategory.WARM,
        gender="female",
    ),
    VoiceInfo(
        id=ElevenLabsVoice.DOMI.value,
        name="Domi",
        provider_id=TTSProvider.ELEVENLABS.value,
        model_ids=["eleven_monolingual_v1", "eleven_multilingual_v2"],
        description="Strong, confident voice",
        category=VoiceCategory.AUTHORITATIVE,
        gender="female",
    ),
    VoiceInfo(
        id=ElevenLabsVoice.BELLA.value,
        name="Bella",
        provider_id=TTSProvider.ELEVENLABS.value,
        model_ids=["eleven_monolingual_v1", "eleven_multilingual_v2"],
        description="Soft, gentle voice",
        category=VoiceCategory.WARM,
        gender="female",
    ),
    VoiceInfo(
        id=ElevenLabsVoice.ANTONI.value,
        name="Antoni",
        provider_id=TTSProvider.ELEVENLABS.value,
        model_ids=["eleven_monolingual_v1", "eleven_multilingual_v2"],
        description="Well-rounded male voice",
        category=VoiceCategory.NEUTRAL,
        gender="male",
    ),
    VoiceInfo(
        id=ElevenLabsVoice.ELLI.value,
        name="Elli",
        provider_id=TTSProvider.ELEVENLABS.value,
        model_ids=["eleven_monolingual_v1", "eleven_multilingual_v2"],
        description="Emotional range, expressive",
        category=VoiceCategory.EXPRESSIVE,
        gender="female",
    ),
    VoiceInfo(
        id=ElevenLabsVoice.JOSH.value,
        name="Josh",
        provider_id=TTSProvider.ELEVENLABS.value,
        model_ids=["eleven_monolingual_v1", "eleven_multilingual_v2"],
        description="Deep, young male voice",
        category=VoiceCategory.AUTHORITATIVE,
        gender="male",
    ),
    VoiceInfo(
        id=ElevenLabsVoice.ARNOLD.value,
        name="Arnold",
        provider_id=TTSProvider.ELEVENLABS.value,
        model_ids=["eleven_monolingual_v1", "eleven_multilingual_v2"],
        description="Crisp, authoritative voice",
        category=VoiceCategory.AUTHORITATIVE,
        gender="male",
    ),
    VoiceInfo(
        id=ElevenLabsVoice.ADAM.value,
        name="Adam",
        provider_id=TTSProvider.ELEVENLABS.value,
        model_ids=["eleven_monolingual_v1", "eleven_multilingual_v2"],
        description="Deep, narrative voice",
        category=VoiceCategory.AUTHORITATIVE,
        gender="male",
    ),
    VoiceInfo(
        id=ElevenLabsVoice.SAM.value,
        name="Sam",
        provider_id=TTSProvider.ELEVENLABS.value,
        model_ids=["eleven_monolingual_v1", "eleven_multilingual_v2"],
        description="Raspy, dynamic voice",
        category=VoiceCategory.EXPRESSIVE,
        gender="male",
    ),
    # Azure Voices (common ones)
    VoiceInfo(
        id="en-US-JennyNeural",
        name="Jenny (US)",
        provider_id=TTSProvider.AZURE.value,
        model_ids=["tts"],
        description="US English female neural voice",
        category=VoiceCategory.NEUTRAL,
        gender="female",
    ),
    VoiceInfo(
        id="en-US-GuyNeural",
        name="Guy (US)",
        provider_id=TTSProvider.AZURE.value,
        model_ids=["tts"],
        description="US English male neural voice",
        category=VoiceCategory.NEUTRAL,
        gender="male",
    ),
    VoiceInfo(
        id="en-GB-SoniaNeural",
        name="Sonia (UK)",
        provider_id=TTSProvider.AZURE.value,
        model_ids=["tts"],
        description="British English female neural voice",
        category=VoiceCategory.WARM,
        gender="female",
    ),
    VoiceInfo(
        id="en-GB-RyanNeural",
        name="Ryan (UK)",
        provider_id=TTSProvider.AZURE.value,
        model_ids=["tts"],
        description="British English male neural voice",
        category=VoiceCategory.AUTHORITATIVE,
        gender="male",
    ),
    # Deepgram Aura Voices
    VoiceInfo(
        id="aura-asteria-en",
        name="Asteria",
        provider_id=TTSProvider.DEEPGRAM.value,
        model_ids=["aura-asteria-en"],
        description="Natural female voice",
        category=VoiceCategory.NEUTRAL,
        gender="female",
    ),
    VoiceInfo(
        id="aura-luna-en",
        name="Luna",
        provider_id=TTSProvider.DEEPGRAM.value,
        model_ids=["aura-luna-en"],
        description="Warm female voice",
        category=VoiceCategory.WARM,
        gender="female",
    ),
    VoiceInfo(
        id="aura-orion-en",
        name="Orion",
        provider_id=TTSProvider.DEEPGRAM.value,
        model_ids=["aura-orion-en"],
        description="Confident male voice",
        category=VoiceCategory.AUTHORITATIVE,
        gender="male",
    ),
    VoiceInfo(
        id="aura-arcas-en",
        name="Arcas",
        provider_id=TTSProvider.DEEPGRAM.value,
        model_ids=["aura-arcas-en"],
        description="Energetic male voice",
        category=VoiceCategory.ENERGETIC,
        gender="male",
    ),
    # MLX Qwen3-TTS Voices
    VoiceInfo(
        id="vivian",
        name="Vivian",
        provider_id=TTSProvider.MLX_QWEN3.value,
        model_ids=[
            "mlx-community/Qwen3-TTS-12Hz-0.6B-CustomVoice-8bit",
            "mlx-community/Qwen3-TTS-12Hz-1.7B-CustomVoice-8bit",
        ],
        description="Clear, professional female voice",
        category=VoiceCategory.NEUTRAL,
        gender="female",
    ),
    VoiceInfo(
        id="serena",
        name="Serena",
        provider_id=TTSProvider.MLX_QWEN3.value,
        model_ids=[
            "mlx-community/Qwen3-TTS-12Hz-0.6B-CustomVoice-8bit",
            "mlx-community/Qwen3-TTS-12Hz-1.7B-CustomVoice-8bit",
        ],
        description="Warm, friendly female voice",
        category=VoiceCategory.WARM,
        gender="female",
    ),
    VoiceInfo(
        id="ryan",
        name="Ryan",
        provider_id=TTSProvider.MLX_QWEN3.value,
        model_ids=[
            "mlx-community/Qwen3-TTS-12Hz-0.6B-CustomVoice-8bit",
            "mlx-community/Qwen3-TTS-12Hz-1.7B-CustomVoice-8bit",
        ],
        description="Confident male voice",
        category=VoiceCategory.AUTHORITATIVE,
        gender="male",
    ),
    VoiceInfo(
        id="aiden",
        name="Aiden",
        provider_id=TTSProvider.MLX_QWEN3.value,
        model_ids=[
            "mlx-community/Qwen3-TTS-12Hz-0.6B-CustomVoice-8bit",
            "mlx-community/Qwen3-TTS-12Hz-1.7B-CustomVoice-8bit",
        ],
        description="Youthful, energetic male voice",
        category=VoiceCategory.ENERGETIC,
        gender="male",
    ),
    VoiceInfo(
        id="eric",
        name="Eric",
        provider_id=TTSProvider.MLX_QWEN3.value,
        model_ids=[
            "mlx-community/Qwen3-TTS-12Hz-0.6B-CustomVoice-8bit",
            "mlx-community/Qwen3-TTS-12Hz-1.7B-CustomVoice-8bit",
        ],
        description="Mature, balanced male voice",
        category=VoiceCategory.NEUTRAL,
        gender="male",
    ),
    VoiceInfo(
        id="dylan",
        name="Dylan",
        provider_id=TTSProvider.MLX_QWEN3.value,
        model_ids=[
            "mlx-community/Qwen3-TTS-12Hz-0.6B-CustomVoice-8bit",
            "mlx-community/Qwen3-TTS-12Hz-1.7B-CustomVoice-8bit",
        ],
        description="Casual, friendly male voice",
        category=VoiceCategory.WARM,
        gender="male",
    ),
    VoiceInfo(
        id="sohee",
        name="Sohee",
        provider_id=TTSProvider.MLX_QWEN3.value,
        model_ids=[
            "mlx-community/Qwen3-TTS-12Hz-0.6B-CustomVoice-8bit",
            "mlx-community/Qwen3-TTS-12Hz-1.7B-CustomVoice-8bit",
        ],
        description="Korean female voice",
        category=VoiceCategory.EXPRESSIVE,
        gender="female",
    ),
    VoiceInfo(
        id="ono_anna",
        name="Ono Anna",
        provider_id=TTSProvider.MLX_QWEN3.value,
        model_ids=[
            "mlx-community/Qwen3-TTS-12Hz-0.6B-CustomVoice-8bit",
            "mlx-community/Qwen3-TTS-12Hz-1.7B-CustomVoice-8bit",
        ],
        description="Japanese female voice",
        category=VoiceCategory.EXPRESSIVE,
        gender="female",
    ),
    VoiceInfo(
        id="uncle_fu",
        name="Uncle Fu",
        provider_id=TTSProvider.MLX_QWEN3.value,
        model_ids=[
            "mlx-community/Qwen3-TTS-12Hz-0.6B-CustomVoice-8bit",
            "mlx-community/Qwen3-TTS-12Hz-1.7B-CustomVoice-8bit",
        ],
        description="Chinese male voice",
        category=VoiceCategory.WARM,
        gender="male",
    ),
]

# =============================================================================
# STT Catalog Data
# =============================================================================

_STT_PROVIDERS: list[ProviderInfo] = [
    ProviderInfo(
        id=STTProvider.OPENAI_WHISPER.value,
        name="OpenAI Whisper",
        type="stt",
        requires_api_key=True,
        api_key_env_var="OPENAI_API_KEY",
        is_local=False,
        description="OpenAI Whisper API for accurate transcription",
    ),
    ProviderInfo(
        id=STTProvider.GROQ_WHISPER.value,
        name="Groq Whisper",
        type="stt",
        requires_api_key=True,
        api_key_env_var="GROQ_API_KEY",
        is_local=False,
        description="Ultra-fast Whisper inference via Groq",
    ),
    ProviderInfo(
        id=STTProvider.FASTER_WHISPER.value,
        name="Faster Whisper",
        type="stt",
        requires_api_key=False,
        api_key_env_var=None,
        is_local=True,
        description="Optimized local Whisper using CTranslate2",
    ),
    ProviderInfo(
        id=STTProvider.WHISPER_LOCAL.value,
        name="Whisper (Local)",
        type="stt",
        requires_api_key=False,
        api_key_env_var=None,
        is_local=True,
        description="Local Whisper via HuggingFace Transformers",
    ),
]

_STT_MODELS: list[ModelInfo] = [
    # OpenAI Whisper
    ModelInfo(
        id="whisper-1",
        name="Whisper-1",
        provider_id=STTProvider.OPENAI_WHISPER.value,
        quality="standard",
        description="OpenAI Whisper transcription model",
        supports_streaming=False,
    ),
    # Groq Whisper
    ModelInfo(
        id="whisper-large-v3-turbo",
        name="Whisper Large v3 Turbo",
        provider_id=STTProvider.GROQ_WHISPER.value,
        quality="turbo",
        description="Ultra-fast Whisper Large v3 on Groq",
        supports_streaming=False,
    ),
    ModelInfo(
        id="whisper-large-v3",
        name="Whisper Large v3",
        provider_id=STTProvider.GROQ_WHISPER.value,
        quality="hd",
        description="High accuracy Whisper Large v3 on Groq",
        supports_streaming=False,
    ),
    # Faster Whisper (local)
    ModelInfo(
        id="large-v3",
        name="Large v3",
        provider_id=STTProvider.FASTER_WHISPER.value,
        quality="hd",
        description="Large v3 model for high accuracy",
        supports_streaming=False,
    ),
    ModelInfo(
        id="medium",
        name="Medium",
        provider_id=STTProvider.FASTER_WHISPER.value,
        quality="standard",
        description="Medium model for balanced speed/accuracy",
        supports_streaming=False,
    ),
    ModelInfo(
        id="small",
        name="Small",
        provider_id=STTProvider.FASTER_WHISPER.value,
        quality="standard",
        description="Small model for faster inference",
        supports_streaming=False,
    ),
    # Whisper Local (HuggingFace)
    ModelInfo(
        id="openai/whisper-large-v3",
        name="Whisper Large v3",
        provider_id=STTProvider.WHISPER_LOCAL.value,
        quality="hd",
        description="HuggingFace Whisper Large v3",
        supports_streaming=False,
    ),
    ModelInfo(
        id="openai/whisper-medium",
        name="Whisper Medium",
        provider_id=STTProvider.WHISPER_LOCAL.value,
        quality="standard",
        description="HuggingFace Whisper Medium",
        supports_streaming=False,
    ),
]


# =============================================================================
# Query Functions
# =============================================================================


def get_tts_providers() -> list[ProviderInfo]:
    """Get all TTS providers."""
    return _TTS_PROVIDERS.copy()


def get_tts_models(provider_id: str | None = None) -> list[ModelInfo]:
    """Get TTS models, optionally filtered by provider."""
    if provider_id is None:
        return _TTS_MODELS.copy()
    return [m for m in _TTS_MODELS if m.provider_id == provider_id]


def get_tts_voices(
    provider_id: str | None = None, model_id: str | None = None
) -> list[VoiceInfo]:
    """Get TTS voices, optionally filtered by provider and/or model."""
    voices = _TTS_VOICES.copy()

    if provider_id is not None:
        voices = [v for v in voices if v.provider_id == provider_id]

    if model_id is not None:
        voices = [v for v in voices if model_id in v.model_ids]

    return voices


def get_voice(voice_id: str) -> VoiceInfo | None:
    """Get a specific voice by ID."""
    for voice in _TTS_VOICES:
        if voice.id == voice_id:
            return voice
    return None


def get_stt_providers() -> list[ProviderInfo]:
    """Get all STT providers."""
    return _STT_PROVIDERS.copy()


def get_stt_models(provider_id: str | None = None) -> list[ModelInfo]:
    """Get STT models, optionally filtered by provider."""
    if provider_id is None:
        return _STT_MODELS.copy()
    return [m for m in _STT_MODELS if m.provider_id == provider_id]


def get_current_voice_config(settings: Any) -> dict[str, Any]:
    """
    Get current voice configuration from settings.

    Args:
        settings: Application settings object

    Returns:
        Dictionary with current TTS and STT configuration
    """
    # Get values with defaults, filtering out None for required fields
    tts_provider = getattr(settings, "TTS_PROVIDER", None) or TTSProvider.OPENAI.value
    tts_model = getattr(settings, "TTS_MODEL", None) or "tts-1"
    tts_voice = getattr(settings, "TTS_VOICE", None) or OpenAIVoice.ALLOY.value
    tts_speed = getattr(settings, "TTS_SPEED", None) or 1.0
    stt_provider = (
        getattr(settings, "STT_PROVIDER", None) or STTProvider.OPENAI_WHISPER.value
    )
    stt_model = getattr(settings, "STT_MODEL", None) or "whisper-1"
    stt_language = getattr(settings, "STT_LANGUAGE", None)

    # Speech text LLM settings (uses properties with fallback to AI_PROVIDER/AI_MODEL)
    speech_text_provider = (
        getattr(settings, "speech_text_provider", None)
        or getattr(settings, "SPEECH_TEXT_PROVIDER", None)
        or getattr(settings, "AI_PROVIDER", "openai")
    )
    speech_text_model = (
        getattr(settings, "speech_text_model", None)
        or getattr(settings, "SPEECH_TEXT_MODEL", None)
        or getattr(settings, "AI_MODEL", "gpt-4o-mini")
    )

    return {
        "stt_provider": stt_provider,
        "stt_model": stt_model,
        "stt_language": stt_language,
        "speech_text_provider": speech_text_provider,
        "speech_text_model": speech_text_model,
        "tts_provider": tts_provider,
        "tts_model": tts_model,
        "tts_voice": tts_voice,
        "tts_speed": tts_speed,
    }

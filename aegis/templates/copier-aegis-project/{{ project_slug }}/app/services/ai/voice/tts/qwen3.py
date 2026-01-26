"""
Qwen3-TTS model management with lazy singleton pattern.

Ensures the Qwen3-TTS model loads once and is shared across
all TTS operations within the process.
"""

import logging
import os
import warnings
from typing import Any

logger = logging.getLogger(__name__)

# Module-level singleton
_qwen3_model: Any = None


def get_qwen3_model() -> Any:
    """Get or load the Qwen3-TTS model singleton."""
    global _qwen3_model

    if _qwen3_model is not None:
        return _qwen3_model

    _qwen3_model = _load_model()
    return _qwen3_model


def is_model_loaded() -> bool:
    """Check if model is already loaded in memory."""
    return _qwen3_model is not None


def preload_model() -> bool:
    """
    Preload model at startup. Returns True if loaded, False if skipped.

    Call this during application startup to avoid first-request latency.
    """
    from app.core.config import settings

    if settings.TTS_PROVIDER != "qwen3":
        logger.info("qwen3_tts.skip", reason="not_configured")
        return False

    import time

    start = time.perf_counter()

    logger.info("qwen3_tts.preload_start", model=settings.TTS_QWEN_MODEL)
    get_qwen3_model()

    elapsed_ms = (time.perf_counter() - start) * 1000
    logger.info("qwen3_tts.preload_complete", duration_ms=round(elapsed_ms, 1))
    return True


def _load_model() -> Any:
    """Load the Qwen3-TTS model with suppressed warnings."""
    from app.core.config import settings

    model_name = settings.TTS_QWEN_MODEL

    logger.info("qwen3_tts.loading", model=model_name)

    # Suppress noisy warnings during model load
    os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")
    os.environ.setdefault("TRANSFORMERS_VERBOSITY", "error")

    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=FutureWarning)
        warnings.filterwarnings("ignore", message=".*token.*")

        try:
            from qwen_tts import Qwen3TTSModel
        except ImportError as e:
            raise RuntimeError(
                "qwen-tts not installed. Install with: "
                "uv sync --extra qwen-tts  (or: uv add qwen-tts)"
            ) from e

        model = Qwen3TTSModel.from_pretrained(model_name)

    logger.info("qwen3_tts.loaded", model=model_name)
    return model


def synthesize(
    text: str,
    language: str = "English",
    speaker: str = "Vivian",
) -> tuple[list[Any], int]:
    """
    Synthesize speech using the Qwen3-TTS model.

    Args:
        text: Text to synthesize.
        language: Language for synthesis (English, Chinese, etc.).
        speaker: Speaker/voice name (Vivian, Ethan, Chelsie, Layla).

    Returns:
        Tuple of (waveform_list, sample_rate).
    """
    model = get_qwen3_model()

    wavs, sr = model.generate_custom_voice(
        text=text,
        language=language,
        speaker=speaker,
    )

    return wavs, sr


def synthesize_to_bytes(
    text: str,
    language: str = "English",
    speaker: str = "Vivian",
    format: str = "wav",
) -> bytes:
    """
    Synthesize speech and return as audio bytes.

    Args:
        text: Text to synthesize.
        language: Language for synthesis.
        speaker: Speaker/voice name.
        format: Audio format (wav, mp3).

    Returns:
        Audio data as bytes.
    """
    import io

    import numpy as np
    import soundfile as sf

    wavs, sr = synthesize(text, language, speaker)

    # Combine waveforms if multiple
    if isinstance(wavs, list) and len(wavs) > 0:
        audio_data = np.concatenate(wavs) if len(wavs) > 1 else wavs[0]
    else:
        audio_data = wavs

    # Convert to numpy array if needed
    if hasattr(audio_data, "numpy"):
        audio_data = audio_data.numpy()
    elif hasattr(audio_data, "cpu"):
        audio_data = audio_data.cpu().numpy()

    # Ensure 1D array
    if audio_data.ndim > 1:
        audio_data = audio_data.flatten()

    # Write to buffer
    buffer = io.BytesIO()
    sf.write(buffer, audio_data, sr, format=format)
    buffer.seek(0)

    return buffer.read()

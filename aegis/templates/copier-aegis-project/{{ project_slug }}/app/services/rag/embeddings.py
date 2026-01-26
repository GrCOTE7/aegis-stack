"""
Centralized embedding model management for RAG service.

Singleton pattern ensures model loads once and is shared across
all RAG operations (API, CLI, workers).
"""

import os
import warnings
from typing import Any

from app.core.log import logger

# Module-level singletons
_embedding_model: Any = None
_embedding_function: Any = None


class PreloadedEmbeddingFunction:
    """ChromaDB-compatible embedding function using preloaded model."""

    def __init__(self, model: Any) -> None:
        self._model = model

    def __call__(self, input: list[str]) -> list[list[float]]:
        embeddings = self._model.encode(input, convert_to_numpy=True)
        return embeddings.tolist()


def get_embedding_function() -> Any:
    """Get shared embedding function (creates on first call)."""
    global _embedding_function

    if _embedding_function is not None:
        return _embedding_function

    from app.core.config import settings

    if settings.RAG_EMBEDDING_PROVIDER == "openai":
        from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction

        _embedding_function = OpenAIEmbeddingFunction(
            api_key=settings.OPENAI_API_KEY,
            model_name=settings.RAG_EMBEDDING_MODEL,
        )
    else:
        model = _get_embedding_model()
        _embedding_function = PreloadedEmbeddingFunction(model)

    return _embedding_function


def preload_embedding_model() -> bool:
    """Preload at startup. Returns True if loaded, False if skipped."""
    from app.core.config import settings

    if settings.RAG_EMBEDDING_PROVIDER == "openai":
        logger.info("rag.embedding.skip", reason="openai_provider")
        return False

    if not getattr(settings, "RAG_ENABLED", True):
        logger.info("rag.embedding.skip", reason="rag_disabled")
        return False

    import time

    start = time.perf_counter()

    logger.info("rag.embedding.preload_start", model=settings.RAG_EMBEDDING_MODEL)
    _get_embedding_model()

    elapsed_ms = (time.perf_counter() - start) * 1000
    logger.info("rag.embedding.preload_complete", duration_ms=round(elapsed_ms, 1))
    return True


def is_model_loaded() -> bool:
    """Check if model is already loaded in memory."""
    return _embedding_model is not None


def _get_embedding_model() -> Any:
    """Get or load the SentenceTransformer model singleton."""
    global _embedding_model

    if _embedding_model is not None:
        return _embedding_model

    _embedding_model = _load_model_silent()
    return _embedding_model


def _load_model_silent() -> Any:
    """Load model with suppressed warnings and progress bars."""
    from app.core.config import settings
    from sentence_transformers import SentenceTransformer

    # Suppress HF noise
    os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"
    os.environ["TRANSFORMERS_VERBOSITY"] = "error"

    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=FutureWarning)
        warnings.filterwarnings("ignore", message=".*token.*")

        cache_dir = settings.RAG_MODEL_CACHE_DIR
        if cache_dir:
            return SentenceTransformer(
                settings.RAG_EMBEDDING_MODEL, cache_folder=cache_dir
            )
        return SentenceTransformer(settings.RAG_EMBEDDING_MODEL)

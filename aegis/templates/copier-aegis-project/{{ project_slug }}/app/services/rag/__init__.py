"""
RAG (Retrieval-Augmented Generation) service module.

Provides document indexing and semantic search functionality for
codebase question answering using ChromaDB with built-in embeddings.
"""

import os

# Suppress HuggingFace noise (MUST be set before any HF imports)
# This module should be imported early in application startup.
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")
os.environ.setdefault("TRANSFORMERS_VERBOSITY", "error")

__all__ = []

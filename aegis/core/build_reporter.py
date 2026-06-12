"""Step-level progress reporting for project generation.

``BuildReporter`` is the seam that lets a renderer observe the build at
step granularity without the generation pipeline knowing anything about
rendering. ``generate_with_copier`` and ``run_post_generation_tasks``
accept an optional reporter and emit ``step``/``done`` at task boundaries;
``None`` (the default, used by quick mode and every other caller) changes
nothing — output stays byte-identical.

The guided init flow passes a reporter that repaints its full-screen build
view on each event. Detail output between boundaries still goes to stdout
(quick mode prints it; guided mode captures it for the receipt/log).

Stable step keys: ``render``, ``deps``, ``env``, ``migrate``, ``llm``,
``format``. Renderers may localize labels by key; the label argument is
the English default.
"""

from __future__ import annotations

from typing import Protocol


class BuildReporter(Protocol):
    """Observer for build-step boundaries."""

    def step(self, key: str, label: str, detail: str = "") -> None:
        """A step started (or is running)."""
        ...

    def done(self, key: str, detail: str = "") -> None:
        """A previously-started step finished successfully."""
        ...

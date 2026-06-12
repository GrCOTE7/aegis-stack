"""Every spec ``docs_path`` must point at a real docs page.

The guided setup renders each screen title as an OSC 8 terminal hyperlink
built from ``DOCS_BASE_URL`` + ``spec.docs_path``. A stale path means a
dead link shipped to every user, so this pins each non-empty value to a
docs source file (``docs/<path>.md`` or ``docs/<path>/index.md`` — both
publish to ``/<path>/`` under mkdocs directory URLs).
"""

from pathlib import Path

import pytest

from aegis.core.components import COMPONENTS
from aegis.core.services import SERVICES

DOCS_ROOT = Path(__file__).resolve().parents[2] / "docs"

ALL_SPECS = {**COMPONENTS, **SERVICES}


@pytest.mark.parametrize("name", sorted(ALL_SPECS))
def test_docs_path_resolves_to_a_docs_page(name: str) -> None:
    docs_path = ALL_SPECS[name].docs_path
    if not docs_path:
        return  # no docs page yet — renderers show no link
    page = DOCS_ROOT / f"{docs_path}.md"
    index = DOCS_ROOT / docs_path / "index.md"
    assert page.exists() or index.exists(), (
        f"{name}: docs_path {docs_path!r} has no source page "
        f"(expected {page} or {index})"
    )


def test_docs_paths_are_site_relative() -> None:
    for name, spec in ALL_SPECS.items():
        if spec.docs_path:
            assert not spec.docs_path.startswith(("http", "/")), name
            assert not spec.docs_path.endswith("/"), name

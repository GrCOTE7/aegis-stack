"""Tests for the guided setup's dependency-display derivations.

"Requires: ..." (``required_names``) and "Pairs well with: ..."
(``pairs_well_with``) are derived from the dependency graph, not
hand-maintained: requirements are the spec's own hard deps; pairings are its
soft recommendations plus the reverse direction (every plugin that requires
or recommends it). These pin both derivations against the real registries so
the guided screens stay honest as specs evolve.
"""

from __future__ import annotations

from aegis.core.components import COMPONENTS, CORE_COMPONENTS
from aegis.core.plugins.spec import (
    PluginKind,
    PluginSpec,
    pairs_well_with,
    required_names,
)
from aegis.core.services import SERVICES

_REGISTRY = [*COMPONENTS.values(), *SERVICES.values()]


class TestRealRegistry:
    def test_database_pairs_with_services_that_require_it(self) -> None:
        pairs = pairs_well_with(
            COMPONENTS["database"], _REGISTRY, exclude=CORE_COMPONENTS
        )
        # Reverse direction: services declaring required_components=["database"].
        assert "auth" in pairs
        assert "blog" in pairs

    def test_worker_requires_redis_and_pairs_exclude_it(self) -> None:
        # Hard dependencies live under "Requires:", never in the pairings.
        assert required_names(COMPONENTS["worker"], exclude=CORE_COMPONENTS) == [
            "redis"
        ]
        pairs = pairs_well_with(
            COMPONENTS["worker"], _REGISTRY, exclude=CORE_COMPONENTS
        )
        assert "redis" not in pairs

    def test_redis_pairs_with_worker_reverse(self) -> None:
        pairs = pairs_well_with(COMPONENTS["redis"], _REGISTRY, exclude=CORE_COMPONENTS)
        assert "worker" in pairs

    def test_core_components_excluded(self) -> None:
        for spec in [*COMPONENTS.values(), *SERVICES.values()]:
            pairs = pairs_well_with(spec, _REGISTRY, exclude=CORE_COMPONENTS)
            assert "backend" not in pairs
            assert "frontend" not in pairs
            assert spec.name not in pairs  # never pairs with itself


class TestDerivationMechanics:
    def test_dedupe_and_bracket_stripping(self) -> None:
        spec = PluginSpec(
            name="thing",
            kind=PluginKind.SERVICE,
            description="x",
            recommended_components=["redis"],
            required_components=["redis", "database[postgres]"],
        )
        # Requirements strip brackets and dedupe; a recommendation that is
        # also required is a requirement, not a pairing.
        assert required_names(spec) == ["redis", "database"]
        assert pairs_well_with(spec, []) == []

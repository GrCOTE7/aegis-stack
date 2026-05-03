"""Tests for ``aegis.core.schemas`` — the per-service/plugin schema registry.

Pins the contract that ``PluginSpec.schema`` opts a service or plugin
into its own database namespace (Ticket 1 of the schema-isolation work).
Specs that leave ``schema=None`` (every in-tree service today) must be
absent from the registry, so the additive change doesn't sweep existing
services into the new pattern before they've been migrated.
"""

from __future__ import annotations

from typing import Any

import pytest

from aegis.core.plugins.spec import PluginKind, PluginSpec
from aegis.core.schemas import (
    SchemaSpec,
    _schema_from_spec,
    get_schema,
    iter_schemas,
    list_schemas,
)


def _make_plugin(name: str, schema: str | None) -> PluginSpec:
    """Build a minimal ``PluginSpec`` for registry tests."""
    return PluginSpec(
        name=name,
        kind=PluginKind.SERVICE,
        description=f"{name} test spec",
        schema=schema,
    )


class TestSchemaFromSpec:
    """``_schema_from_spec`` materialises ``SchemaSpec`` from any duck-typed input."""

    def test_returns_none_when_schema_unset(self) -> None:
        spec = _make_plugin("crawler", schema=None)
        assert _schema_from_spec(spec, owner="crawler") is None

    def test_returns_none_when_schema_empty_string(self) -> None:
        """Empty string is treated as unset — same as ``None``."""
        spec = _make_plugin("crawler", schema="")
        assert _schema_from_spec(spec, owner="crawler") is None

    def test_builds_spec_with_default_filename(self) -> None:
        """SQLite filename defaults to ``"<schema>.db"`` per convention."""
        spec = _make_plugin("crawler", schema="crawler")
        result = _schema_from_spec(spec, owner="crawler")
        assert result == SchemaSpec(
            name="crawler", sqlite_filename="crawler.db", owner="crawler"
        )

    def test_owner_can_differ_from_schema_name(self) -> None:
        """Schema name and owner are independent.

        A plugin called ``aegis-plugin-crawl4ai`` may register a schema
        called ``crawler`` — the owner records the plugin identity for
        diagnostics, the schema name is what models actually qualify with.
        """
        spec = _make_plugin("crawl4ai", schema="crawler")
        result = _schema_from_spec(spec, owner="crawl4ai")
        assert result is not None
        assert result.name == "crawler"
        assert result.owner == "crawl4ai"


class TestIterSchemas:
    """``iter_schemas`` walks SERVICES + plugins + extras."""

    def test_yields_extras(self) -> None:
        extras = [
            _make_plugin("crawl4ai", schema="crawler"),
            _make_plugin("indexer", schema="indexer"),
        ]
        result = list(
            iter_schemas(extra_specs=extras, include_discovered_plugins=False)
        )
        # In-tree services don't claim schemas yet (T1.5/T1.6 work),
        # so extras are the only things we expect here.
        names = {s.name for s in result if s.owner in {"crawl4ai", "indexer"}}
        assert names == {"crawler", "indexer"}

    def test_skips_specs_without_schema(self) -> None:
        extras = [
            _make_plugin("a", schema=None),
            _make_plugin("b", schema="b_schema"),
            _make_plugin("c", schema=""),
        ]
        result = list(
            iter_schemas(extra_specs=extras, include_discovered_plugins=False)
        )
        names = {s.name for s in result}
        assert "b_schema" in names
        # a and c were skipped — no entry from either of them survives
        assert not any(s.owner == "a" for s in result)
        assert not any(s.owner == "c" for s in result)

    def test_dedupes_by_schema_name(self) -> None:
        """Two specs with the same owner+schema collapse to one entry.

        Same owner re-registering the same schema is idempotent (e.g.
        re-imported across multiple test fixtures). Different owners
        claiming the same schema is a conflict — see next test.
        """
        spec = _make_plugin("crawler", schema="crawler")
        result = list(
            iter_schemas(extra_specs=[spec, spec], include_discovered_plugins=False)
        )
        crawler_entries = [s for s in result if s.name == "crawler"]
        assert len(crawler_entries) == 1

    def test_conflict_raises_value_error(self) -> None:
        """Two specs claiming the same schema name under different owners
        raise — the conflict needs to surface at generation time, not
        as a Postgres error at first migration.
        """
        extras = [
            _make_plugin("plugin_a", schema="docs"),
            _make_plugin("plugin_b", schema="docs"),
        ]
        with pytest.raises(ValueError, match="Schema 'docs' is claimed"):
            list(iter_schemas(extra_specs=extras, include_discovered_plugins=False))

    def test_in_tree_services_today_claim_no_schema(self) -> None:
        """Pin: every in-tree service still has ``schema=None``.

        T1.5 and T1.6 will migrate them. Until then, the registry should
        be empty when called against the in-tree-only view (no extras,
        no discovered plugins).
        """
        result = list(iter_schemas(extra_specs=None, include_discovered_plugins=False))
        assert result == []


class TestGetSchema:
    """``get_schema`` is the single-name lookup convenience."""

    def test_returns_match(self) -> None:
        # Force a known spec into the registry by patching the SERVICES
        # dict via extras — get_schema delegates to iter_schemas, which
        # itself accepts extras... but get_schema doesn't take extras.
        # So this test exercises the "not found" path; the round-trip
        # path is covered by TestIterSchemas above.
        assert get_schema("does_not_exist_12345") is None


class TestListSchemas:
    """``list_schemas`` is just a thin materialiser."""

    def test_round_trip(self) -> None:
        result = list_schemas()
        # Empty today (no in-tree service has migrated). T1.5/T1.6 will
        # change this; this test should be updated when auth gets its
        # schema declaration.
        assert isinstance(result, list)
        assert all(isinstance(item, SchemaSpec) for item in result)


class TestPluginSpecSchemaField:
    """Pin the new field on ``PluginSpec`` itself."""

    def test_default_is_none(self) -> None:
        spec: Any = PluginSpec(name="x", kind=PluginKind.SERVICE, description="x")
        assert spec.schema is None

    def test_round_trips_value(self) -> None:
        spec = PluginSpec(
            name="x",
            kind=PluginKind.SERVICE,
            description="x",
            schema="x_schema",
        )
        assert spec.schema == "x_schema"

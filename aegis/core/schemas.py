"""
Schema registry for per-service / per-plugin database isolation (Ticket 1).

The plugin system gives each service and each plugin its own database
namespace. On Postgres that is a real ``CREATE SCHEMA``; on SQLite it
resolves through an attached database file (one ``.db`` per schema; see
``aegis.core.db.sqlite_attach``). The *same* model declarations and the
*same* generated migrations work on both dialects.

This module is the CLI-side view: it walks the in-tree ``SERVICES`` dict
plus any plugins discovered through entry points, and yields a
``SchemaSpec`` for every spec that opts into the new pattern by setting
``PluginSpec.schema``. Specs that leave ``schema=None`` are unscoped and
not yielded — they continue to live in ``public`` / ``main`` until they
migrate.

The runtime equivalent inside generated projects is a static list emitted
into ``app/core/schemas.py`` at template-generation time (see T1.4). It is
deliberately *not* discovery-driven at runtime: the generated project
should only register the schemas it actually has, and that information is
already known at project-generation time from ``.copier-answers.yml``.
"""

from collections.abc import Iterable, Iterator
from dataclasses import dataclass


@dataclass(frozen=True)
class SchemaSpec:
    """A database namespace owned by a service or plugin.

    Frozen because the registry returns these as a snapshot — they are
    not meant to be mutated by callers. The dataclass is hashable so
    callers can dedupe via ``set()``.
    """

    name: str
    """The schema name. Becomes the Postgres schema and the SQLite
    attached-database alias. Must be a valid SQL identifier (no quoting
    is added by the migration generator)."""

    sqlite_filename: str
    """Filename, relative to the project's ``data/`` directory, that
    backs this schema on SQLite. Conventionally ``"<name>.db"``."""

    owner: str
    """Logical name of the spec that registered this schema (the service
    name for in-tree services, the plugin name for plugins). Used for
    diagnostics and conflict detection."""


def _schema_from_spec(spec: object, owner: str) -> SchemaSpec | None:
    """Build a ``SchemaSpec`` from a spec object that may declare ``schema``.

    Duck-typed on the ``schema`` attribute so this works for both
    ``PluginSpec`` (services + third-party plugins) and any future spec
    type that grows the same field.
    """
    schema_name = getattr(spec, "schema", None)
    if not schema_name:
        return None
    return SchemaSpec(
        name=schema_name,
        sqlite_filename=f"{schema_name}.db",
        owner=owner,
    )


def iter_schemas(
    *,
    extra_specs: Iterable[object] | None = None,
    include_discovered_plugins: bool = True,
) -> Iterator[SchemaSpec]:
    """Yield every registered schema, deduped by name.

    Walks in-tree services first, then optionally entry-point plugins,
    then the caller-supplied ``extra_specs`` (used by tests and by
    template generation when the project's plugin list is already
    materialised from ``.copier-answers.yml``).

    Duplicate ``schema`` declarations across owners raise ``ValueError``
    so the conflict surfaces at generation time, not at runtime when
    Postgres or Alembic complain about a name collision.
    """
    seen: dict[str, str] = {}

    def _emit(spec: object, owner: str) -> Iterator[SchemaSpec]:
        candidate = _schema_from_spec(spec, owner)
        if candidate is None:
            return
        if candidate.name in seen and seen[candidate.name] != owner:
            raise ValueError(
                f"Schema {candidate.name!r} is claimed by both "
                f"{seen[candidate.name]!r} and {owner!r}. Schemas must "
                "be unique across services and plugins."
            )
        if candidate.name in seen:
            return
        seen[candidate.name] = owner
        yield candidate

    from .services import SERVICES

    for service_name, service_spec in SERVICES.items():
        yield from _emit(service_spec, service_name)

    if include_discovered_plugins:
        from .plugins.discovery import discover_plugins

        for plugin_spec in discover_plugins():
            yield from _emit(plugin_spec, getattr(plugin_spec, "name", "<unknown>"))

    if extra_specs:
        for spec in extra_specs:
            owner = getattr(spec, "name", "<extra>")
            yield from _emit(spec, owner)


def get_schema(name: str) -> SchemaSpec | None:
    """Look up a single schema by name, or ``None`` if not registered.

    Convenience wrapper around ``iter_schemas`` for call sites that only
    need one entry. Walks the registry in declaration order; returns the
    first match.
    """
    for schema in iter_schemas():
        if schema.name == name:
            return schema
    return None


def list_schemas() -> list[SchemaSpec]:
    """Materialise ``iter_schemas`` into a list. Useful in templates and tests."""
    return list(iter_schemas())


__all__ = [
    "SchemaSpec",
    "get_schema",
    "iter_schemas",
    "list_schemas",
]

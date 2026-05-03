"""SQLite per-schema ATTACH wiring (Ticket 1 of the schema-isolation work).

Postgres has real schemas. SQLite does not — but it does support
``ATTACH DATABASE 'file.db' AS alias``, and once attached, the alias
behaves indistinguishably from a Postgres schema name in every
SQLAlchemy/SQLModel query (``alias.table``, ``schema='alias'`` on
Alembic ops, etc.).

This module provides ``install_attach_listener``: register it on a
SQLAlchemy ``Engine`` and every connection in the pool will attach the
project's per-schema SQLite files at connect time. The listener is
idempotent (re-attaching an already-attached schema raises in SQLite, so
we filter via ``PRAGMA database_list`` first) and a no-op for non-SQLite
engines, so the same call is safe to put in a generated project's
``app/core/db.py`` regardless of the active dialect.

Cross-database foreign keys are unsupported in SQLite. That's deliberate
for plugin isolation: services and plugins in different schemas should
not declare FKs into each other's tables. On Postgres the same model
declarations work and FKs across schemas are valid.
"""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from sqlalchemy import event
from sqlalchemy.engine import Engine

from ..schemas import SchemaSpec


def install_attach_listener(
    engine: Engine,
    schemas: Iterable[SchemaSpec],
    *,
    sqlite_base_path: Path,
) -> None:
    """Install a ``connect`` event listener that ATTACHes per-schema SQLite files.

    Args:
        engine: The SQLAlchemy ``Engine`` whose connections need ATTACHes.
            Non-SQLite engines silently skip — the listener still installs
            so the same call works for both dialects, but the body short-
            circuits at attach time.
        schemas: An iterable of ``SchemaSpec`` describing what to attach.
            Materialised once at install time; later changes to the iterable
            are not picked up. Pass a fresh list per call if you need to
            re-register.
        sqlite_base_path: Directory containing the per-schema ``.db`` files.
            Each schema's ``sqlite_filename`` is resolved against this
            path. Created on demand if it does not exist so first-run
            ATTACH works without a separate ``mkdir -p data/``.

    Behaviour:
        - For non-SQLite dialects the listener is registered but the body
          short-circuits; no SQL is issued. Cheap to leave installed.
        - For SQLite the listener queries ``PRAGMA database_list`` first
          and skips already-attached schemas — re-running it for the same
          connection (which can happen when the same connection is
          checked out + checked back in repeatedly) is safe and silent.
        - Files are *not* pre-created; SQLite creates them on first
          ATTACH. This matches Postgres' "CREATE SCHEMA IF NOT EXISTS"
          ergonomics where the schema appears the moment the framework
          asks for it.
    """
    materialised = list(schemas)
    sqlite_base_path = Path(sqlite_base_path)

    @event.listens_for(engine, "connect")
    def _attach(dbapi_connection: object, _connection_record: object) -> None:
        if engine.dialect.name != "sqlite":
            return

        sqlite_base_path.mkdir(parents=True, exist_ok=True)

        cursor = dbapi_connection.cursor()  # type: ignore[attr-defined]
        try:
            cursor.execute("PRAGMA database_list")
            already_attached = {row[1] for row in cursor.fetchall()}

            for schema in materialised:
                if schema.name in already_attached:
                    continue
                target = sqlite_base_path / schema.sqlite_filename
                # Single-quote the path; SQLite's ATTACH syntax uses
                # string-literal quoting, not identifier quoting.
                cursor.execute(f"ATTACH DATABASE '{target}' AS {schema.name}")
        finally:
            cursor.close()


__all__ = ["install_attach_listener"]

"""Tests for ``aegis.core.db.sqlite_attach`` — per-schema ATTACH wiring.

The listener has to behave identically across:
- the first connection ever (no prior ATTACH state),
- subsequent connections from the same pool (already-attached schemas
  must not raise ``database NAME is already in use``),
- non-SQLite engines (where ATTACH is meaningless and the listener
  must short-circuit without erroring).

These tests pin all three.
"""

from __future__ import annotations

from pathlib import Path

from sqlalchemy import create_engine, text

from aegis.core.db.sqlite_attach import install_attach_listener
from aegis.core.schemas import SchemaSpec


def _make_engine(main_db_path: Path):
    """Build a file-backed SQLite engine for tests.

    File-backed (not ``:memory:``) because ATTACH against ``:memory:``
    creates a fresh in-memory db per attach, which doesn't exercise the
    "schemas point at real files" path we care about.
    """
    return create_engine(f"sqlite:///{main_db_path}", future=True)


class TestInstallAttachListener:
    def test_attaches_single_schema(self, tmp_path: Path) -> None:
        """A connection sees the attached schema in ``database_list``."""
        engine = _make_engine(tmp_path / "main.db")
        install_attach_listener(
            engine,
            [SchemaSpec(name="auth", sqlite_filename="auth.db", owner="auth")],
            sqlite_base_path=tmp_path,
        )

        with engine.connect() as conn:
            rows = conn.execute(text("PRAGMA database_list")).all()
            names = {row[1] for row in rows}
            assert "auth" in names

    def test_attached_schema_is_queryable(self, tmp_path: Path) -> None:
        """Round-trip: create + read a table inside the attached schema."""
        engine = _make_engine(tmp_path / "main.db")
        install_attach_listener(
            engine,
            [SchemaSpec(name="auth", sqlite_filename="auth.db", owner="auth")],
            sqlite_base_path=tmp_path,
        )

        with engine.begin() as conn:
            conn.execute(text("CREATE TABLE auth.users (id INTEGER PRIMARY KEY)"))
            conn.execute(text("INSERT INTO auth.users (id) VALUES (1)"))

        with engine.connect() as conn:
            row = conn.execute(text("SELECT id FROM auth.users")).one()
            assert row[0] == 1

    def test_attaches_multiple_schemas(self, tmp_path: Path) -> None:
        """Multiple schemas, multiple files, all attached on every connection."""
        engine = _make_engine(tmp_path / "main.db")
        install_attach_listener(
            engine,
            [
                SchemaSpec(name="auth", sqlite_filename="auth.db", owner="auth"),
                SchemaSpec(
                    name="payment", sqlite_filename="payment.db", owner="payment"
                ),
                SchemaSpec(
                    name="crawler", sqlite_filename="crawler.db", owner="crawler"
                ),
            ],
            sqlite_base_path=tmp_path,
        )

        with engine.connect() as conn:
            rows = conn.execute(text("PRAGMA database_list")).all()
            names = {row[1] for row in rows}
            for expected in ("auth", "payment", "crawler"):
                assert expected in names, f"{expected} missing from {names!r}"

    def test_schemas_persist_across_connections(self, tmp_path: Path) -> None:
        """Each new connection runs the listener again and sees the schemas.

        Without per-connection ATTACH, a row written on connection #1
        wouldn't be readable on connection #2 since SQLite's pool gives
        back potentially-different DBAPI connections.
        """
        engine = _make_engine(tmp_path / "main.db")
        install_attach_listener(
            engine,
            [SchemaSpec(name="auth", sqlite_filename="auth.db", owner="auth")],
            sqlite_base_path=tmp_path,
        )

        with engine.begin() as conn:
            conn.execute(text("CREATE TABLE auth.users (id INTEGER PRIMARY KEY)"))
            conn.execute(text("INSERT INTO auth.users (id) VALUES (42)"))

        # Force a brand-new connection from the pool.
        engine.dispose()

        with engine.connect() as conn:
            row = conn.execute(text("SELECT id FROM auth.users")).one()
            assert row[0] == 42

    def test_idempotent_within_pool(self, tmp_path: Path) -> None:
        """Re-using a pooled connection must not re-ATTACH and raise.

        SQLite's ATTACH errors with "database NAME is already in use" if
        you try to attach a name that's already there. ``PRAGMA
        database_list`` filtering avoids that.
        """
        engine = _make_engine(tmp_path / "main.db")
        install_attach_listener(
            engine,
            [SchemaSpec(name="auth", sqlite_filename="auth.db", owner="auth")],
            sqlite_base_path=tmp_path,
        )

        # Multiple connect/release cycles — pool returns the same DBAPI
        # connection. Listener re-fires per connect; must not error.
        for _ in range(3):
            with engine.connect() as conn:
                conn.execute(text("SELECT 1")).all()

    def test_creates_base_path(self, tmp_path: Path) -> None:
        """``sqlite_base_path`` is created on demand."""
        engine = _make_engine(tmp_path / "main.db")
        data_dir = tmp_path / "subdir" / "data"
        assert not data_dir.exists()

        install_attach_listener(
            engine,
            [SchemaSpec(name="auth", sqlite_filename="auth.db", owner="auth")],
            sqlite_base_path=data_dir,
        )

        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))

        assert data_dir.exists()
        assert (data_dir / "auth.db").exists()

    def test_no_op_for_non_sqlite_engine(self, tmp_path: Path) -> None:
        """Non-SQLite engines must short-circuit without issuing ATTACH.

        Drives the dialect-check branch directly by stubbing ``dialect.name``
        on a real SQLite engine — this avoids requiring ``psycopg2`` (or any
        other DB driver) just to test "this is not SQLite, so do nothing".
        """
        engine = _make_engine(tmp_path / "main.db")

        install_attach_listener(
            engine,
            [SchemaSpec(name="auth", sqlite_filename="auth.db", owner="auth")],
            sqlite_base_path=tmp_path,
        )

        # Lie about the dialect name. The listener checks
        # ``engine.dialect.name`` at connect time, not at install, so the
        # next connection will see "postgresql" and skip ATTACH.
        original_name = engine.dialect.name
        try:
            engine.dialect.name = "postgresql"  # type: ignore[misc]
            with engine.connect() as conn:
                rows = conn.execute(text("PRAGMA database_list")).all()
                names = {row[1] for row in rows}
                # ATTACH was skipped — only the default ``main`` schema.
                assert "auth" not in names
        finally:
            engine.dialect.name = original_name  # type: ignore[misc]

    def test_empty_schemas_is_no_op(self, tmp_path: Path) -> None:
        """Calling with no schemas is fine — listener fires but does nothing."""
        engine = _make_engine(tmp_path / "main.db")
        install_attach_listener(engine, [], sqlite_base_path=tmp_path)

        with engine.connect() as conn:
            rows = conn.execute(text("PRAGMA database_list")).all()
            names = {row[1] for row in rows}
            # The mandatory schema is "main"; "temp" is created lazily on
            # first temp-table use and may or may not appear here. Just
            # pin that no extras (auth/payment/etc.) sneak in.
            assert "main" in names
            assert names <= {"main", "temp"}

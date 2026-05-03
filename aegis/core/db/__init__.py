"""Database integration helpers shipped by the aegis-stack CLI for use in
generated projects.

The contents are deliberately small and runtime-cheap so generated
projects can import them at engine-init time without pulling in the rest
of the CLI surface. The flagship module today is ``sqlite_attach``,
which wires per-schema ATTACH for SQLite (Ticket 1 of the schema
isolation work).
"""

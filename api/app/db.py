"""Database access: a small connection pool and the schema."""

import os

from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

SCHEMA = """
CREATE TABLE IF NOT EXISTS cookbooks (
    code        TEXT PRIMARY KEY,
    name        TEXT NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS recipes (
    id           SERIAL PRIMARY KEY,
    cookbook     TEXT NOT NULL REFERENCES cookbooks(code) ON DELETE CASCADE,
    title        TEXT NOT NULL,
    author       TEXT NOT NULL DEFAULT '',
    servings     INTEGER,
    minutes      INTEGER,
    ingredients  TEXT NOT NULL DEFAULT '',
    steps        TEXT NOT NULL DEFAULT '',
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS recipes_cookbook_idx ON recipes (cookbook);
"""

_pool: ConnectionPool | None = None


def open_pool() -> None:
    """Open the pool and create the tables. DATABASE_URL comes from the environment, never from code."""
    global _pool
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL is not set")
    _pool = ConnectionPool(url, min_size=1, max_size=5, kwargs={"row_factory": dict_row}, open=True)
    _pool.wait(timeout=30)
    with _pool.connection() as conn:
        conn.execute(SCHEMA)


def close_pool() -> None:
    if _pool is not None:
        _pool.close()


def pool() -> ConnectionPool:
    if _pool is None:
        raise RuntimeError("database pool not open")
    return _pool

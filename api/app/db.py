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

-- v2: categories, the personal touch, and where a recipe was copied from
ALTER TABLE recipes ADD COLUMN IF NOT EXISTS category     TEXT NOT NULL DEFAULT '';
ALTER TABLE recipes ADD COLUMN IF NOT EXISTS notes        TEXT NOT NULL DEFAULT '';
ALTER TABLE recipes ADD COLUMN IF NOT EXISTS source_title TEXT;

CREATE TABLE IF NOT EXISTS catalog_recipes (
    id           SERIAL PRIMARY KEY,
    title        TEXT NOT NULL UNIQUE,
    category     TEXT NOT NULL,
    servings     INTEGER,
    minutes      INTEGER,
    ingredients  TEXT NOT NULL,
    steps        TEXT NOT NULL
);
"""


def seed_catalog(conn) -> int:
    """Insert the built-in recipes that are not in the catalog yet (safe to run on every start)."""
    from .catalog import RECIPES

    added = 0
    for r in RECIPES:
        added += conn.execute(
            "INSERT INTO catalog_recipes (title, category, servings, minutes, ingredients, steps) "
            "VALUES (%(title)s, %(category)s, %(servings)s, %(minutes)s, %(ingredients)s, %(steps)s) "
            "ON CONFLICT (title) DO NOTHING",
            r,
        ).rowcount
    return added

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
        # One transaction + advisory lock: if two replicas start at once, they don't race on the DDL/seed.
        conn.execute("SELECT pg_advisory_xact_lock(4242)")
        conn.execute(SCHEMA)
        seed_catalog(conn)


def close_pool() -> None:
    if _pool is not None:
        _pool.close()


def pool() -> ConnectionPool:
    if _pool is None:
        raise RuntimeError("database pool not open")
    return _pool

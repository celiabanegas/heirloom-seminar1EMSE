"""Heirloom API: family cookbooks, their recipes, and a catalog of classics to copy from."""

import logging
import os
import secrets
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from . import db
from .catalog import CATEGORIES, STARTER_TITLES

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("heirloom")

VERSION = os.environ.get("APP_VERSION", "dev")
CORS_ORIGIN = os.environ.get("CORS_ORIGIN", "http://localhost:8080")

# No 0/O or 1/I/L: codes are read out loud and typed on phones.
CODE_ALPHABET = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"


@asynccontextmanager
async def lifespan(_: FastAPI):
    db.open_pool()
    log.info("API started, version %s, CORS origin %s", VERSION, CORS_ORIGIN)
    yield
    db.close_pool()


app = FastAPI(title="Heirloom API", version=VERSION, lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in CORS_ORIGIN.split(",")],
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type"],
)


# ---------- models ----------

class CookbookIn(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    starter: bool = False  # start with a few classics from the catalog


class RecipeIn(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    author: str = Field(default="", max_length=60)
    category: str = Field(default="", max_length=40)
    servings: int | None = Field(default=None, ge=1, le=100)
    minutes: int | None = Field(default=None, ge=1, le=10000)
    ingredients: str = Field(default="", max_length=5000)
    steps: str = Field(default="", max_length=20000)
    notes: str = Field(default="", max_length=3000)  # "your special touch"


# Accent- and case-insensitive search without needing the unaccent extension.
def _norm(col: str) -> str:
    return f"translate(lower({col}), 'áéíóúüñàèìòù', 'aeiouunaeiou')"


def _search_clause(cols: list[str]) -> str:
    return "(" + " OR ".join(f"{_norm(c)} LIKE {_norm('%(like)s')}" for c in cols) + ")"


# ---------- health ----------

@app.get("/health")
def health():
    """Liveness + database check, used by Container Apps probes and the frontend footer."""
    try:
        with db.pool().connection() as conn:
            conn.execute("SELECT 1")
    except Exception:
        log.exception("health check failed")
        raise HTTPException(status_code=503, detail="database unavailable")
    return {"status": "ok", "version": VERSION}


# ---------- catalog ----------

CATALOG_COLS = "id, title, category, servings, minutes, ingredients, steps"


@app.get("/api/catalog")
def list_catalog(q: str = "", category: str = ""):
    with db.pool().connection() as conn:
        return conn.execute(
            f"SELECT {CATALOG_COLS} FROM catalog_recipes "
            f"WHERE {_search_clause(['title', 'ingredients', 'category'])} "
            "AND (%(category)s = '' OR category = %(category)s) ORDER BY category, title",
            {"like": f"%{q.strip()}%", "category": category},
        ).fetchall()


@app.get("/api/catalog/categories")
def list_categories():
    return CATEGORIES


@app.get("/api/catalog/{catalog_id}")
def get_catalog_recipe(catalog_id: int):
    with db.pool().connection() as conn:
        row = conn.execute(f"SELECT {CATALOG_COLS} FROM catalog_recipes WHERE id = %s", (catalog_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="catalog recipe not found")
    return row


# ---------- cookbooks ----------

def _new_code() -> str:
    return "".join(secrets.choice(CODE_ALPHABET) for _ in range(8))


def _get_cookbook(conn, code: str) -> dict:
    row = conn.execute("SELECT code, name, created_at FROM cookbooks WHERE code = %s", (code.upper(),)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="cookbook not found")
    return row


RECIPE_COLS = (
    "id, title, author, category, servings, minutes, ingredients, steps, notes, source_title, created_at, updated_at"
)

COPY_FROM_CATALOG = (
    "INSERT INTO recipes (cookbook, title, category, servings, minutes, ingredients, steps, source_title) "
    "SELECT %s, title, category, servings, minutes, ingredients, steps, title FROM catalog_recipes "
)


@app.post("/api/cookbooks", status_code=201)
def create_cookbook(body: CookbookIn):
    with db.pool().connection() as conn:
        for _ in range(5):  # a clash among 31^8 codes is very unlikely, but retry anyway
            code = _new_code()
            row = conn.execute(
                "INSERT INTO cookbooks (code, name) VALUES (%s, %s) ON CONFLICT DO NOTHING RETURNING code, name, created_at",
                (code, body.name.strip()),
            ).fetchone()
            if row:
                if body.starter:
                    conn.execute(COPY_FROM_CATALOG + "WHERE title = ANY(%s)", (code, STARTER_TITLES))
                return row
    raise HTTPException(status_code=500, detail="could not create a code")


@app.get("/api/cookbooks/{code}")
def get_cookbook(code: str):
    with db.pool().connection() as conn:
        book = _get_cookbook(conn, code)
        book["recipe_count"] = conn.execute(
            "SELECT count(*) AS n FROM recipes WHERE cookbook = %s", (book["code"],)
        ).fetchone()["n"]
        return book


# ---------- recipes ----------

@app.get("/api/cookbooks/{code}/recipes")
def list_recipes(code: str, q: str = ""):
    with db.pool().connection() as conn:
        book = _get_cookbook(conn, code)
        return conn.execute(
            f"SELECT {RECIPE_COLS} FROM recipes WHERE cookbook = %(code)s "
            f"AND {_search_clause(['title', 'ingredients', 'author', 'category', 'notes'])} ORDER BY lower(title)",
            {"code": book["code"], "like": f"%{q.strip()}%"},
        ).fetchall()


@app.post("/api/cookbooks/{code}/recipes", status_code=201)
def create_recipe(code: str, body: RecipeIn):
    with db.pool().connection() as conn:
        book = _get_cookbook(conn, code)
        return conn.execute(
            "INSERT INTO recipes (cookbook, title, author, category, servings, minutes, ingredients, steps, notes) "
            f"VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING {RECIPE_COLS}",
            (book["code"], body.title.strip(), body.author.strip(), body.category.strip(), body.servings,
             body.minutes, body.ingredients.strip(), body.steps.strip(), body.notes.strip()),
        ).fetchone()


@app.post("/api/cookbooks/{code}/recipes/from-catalog/{catalog_id}", status_code=201)
def add_from_catalog(code: str, catalog_id: int):
    """Copy a catalog recipe into the cookbook. The copy is independent: edit it freely."""
    with db.pool().connection() as conn:
        book = _get_cookbook(conn, code)
        row = conn.execute(
            COPY_FROM_CATALOG + f"WHERE id = %s RETURNING {RECIPE_COLS}", (book["code"], catalog_id)
        ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="catalog recipe not found")
    return row


@app.get("/api/cookbooks/{code}/recipes/{recipe_id}")
def get_recipe(code: str, recipe_id: int):
    with db.pool().connection() as conn:
        row = conn.execute(
            f"SELECT {RECIPE_COLS} FROM recipes WHERE cookbook = %s AND id = %s", (code.upper(), recipe_id)
        ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="recipe not found")
    return row


@app.put("/api/cookbooks/{code}/recipes/{recipe_id}")
def update_recipe(code: str, recipe_id: int, body: RecipeIn):
    with db.pool().connection() as conn:
        row = conn.execute(
            "UPDATE recipes SET title = %s, author = %s, category = %s, servings = %s, minutes = %s, "
            "ingredients = %s, steps = %s, notes = %s, updated_at = now() "
            f"WHERE cookbook = %s AND id = %s RETURNING {RECIPE_COLS}",
            (body.title.strip(), body.author.strip(), body.category.strip(), body.servings, body.minutes,
             body.ingredients.strip(), body.steps.strip(), body.notes.strip(), code.upper(), recipe_id),
        ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="recipe not found")
    return row


@app.delete("/api/cookbooks/{code}/recipes/{recipe_id}", status_code=204)
def delete_recipe(code: str, recipe_id: int):
    with db.pool().connection() as conn:
        deleted = conn.execute(
            "DELETE FROM recipes WHERE cookbook = %s AND id = %s", (code.upper(), recipe_id)
        ).rowcount
    if not deleted:
        raise HTTPException(status_code=404, detail="recipe not found")
    return Response(status_code=204)

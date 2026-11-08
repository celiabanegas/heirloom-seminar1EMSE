"""End-to-end tests against a real Postgres (DATABASE_URL). CI starts one as a service container."""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:  # runs the lifespan: opens the pool and creates the tables
        yield c


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_cookbook_and_recipe_crud(client):
    book = client.post("/api/cookbooks", json={"name": "Familia Banegas"}).json()
    code = book["code"]
    assert len(code) == 8

    # lower-case codes work too (people type them by hand)
    assert client.get(f"/api/cookbooks/{code.lower()}").json()["recipe_count"] == 0

    new = {
        "title": "Tortilla de patatas",
        "author": "Abuela",
        "servings": 4,
        "minutes": 40,
        "ingredients": "6 huevos\n600 g de patatas\n1 cebolla\n100 ml de aceite de oliva\nSal",
        "steps": "Pelar y cortar las patatas.\nFreír a fuego medio.\nBatir los huevos y cuajar.",
    }
    recipe = client.post(f"/api/cookbooks/{code}/recipes", json=new).json()
    rid = recipe["id"]

    assert [r["title"] for r in client.get(f"/api/cookbooks/{code}/recipes", params={"q": "patata"}).json()] == [
        "Tortilla de patatas"
    ]
    assert client.get(f"/api/cookbooks/{code}/recipes", params={"q": "lentejas"}).json() == []

    updated = client.put(f"/api/cookbooks/{code}/recipes/{rid}", json={**new, "servings": 6}).json()
    assert updated["servings"] == 6

    assert client.delete(f"/api/cookbooks/{code}/recipes/{rid}").status_code == 204
    assert client.get(f"/api/cookbooks/{code}/recipes/{rid}").status_code == 404


def test_validation_and_not_found(client):
    assert client.get("/api/cookbooks/NOPE0000").status_code == 404
    assert client.post("/api/cookbooks", json={"name": ""}).status_code == 422
    book = client.post("/api/cookbooks", json={"name": "Otra"}).json()
    assert client.post(f"/api/cookbooks/{book['code']}/recipes", json={"title": ""}).status_code == 422


def test_cookbooks_are_isolated(client):
    a = client.post("/api/cookbooks", json={"name": "A"}).json()["code"]
    b = client.post("/api/cookbooks", json={"name": "B"}).json()["code"]
    rid = client.post(f"/api/cookbooks/{a}/recipes", json={"title": "Secreta"}).json()["id"]
    assert client.get(f"/api/cookbooks/{b}/recipes/{rid}").status_code == 404
    assert client.delete(f"/api/cookbooks/{b}/recipes/{rid}").status_code == 404

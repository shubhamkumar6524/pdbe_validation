from app.app import create_app
import pytest
from httpx import AsyncClient
from app.routes import router
from fastapi.testclient import TestClient

client = TestClient(router)

def test_index():
    print("testing Routes")
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"healthcheck": "True"}

def test_ready():
    response = client.get("/readyz")
    assert response.status_code == 200
    assert response. json() == {"healthcheck": "True"}

def test_healthcheck():
    response = client.get("/healthcheck")
    assert response. status_code == 200
    assert response.json() == {"status": "ok"}
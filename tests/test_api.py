"""Integration tests for FastAPI REST API endpoints."""
import pytest
from fastapi.testclient import TestClient
from web.backend.main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_health_endpoint(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert "LaptopCheck" in data["service"]

def test_hardware_endpoint_native(client):
    res = client.get("/api/hardware?simulate=false")
    assert res.status_code == 200
    data = res.json()
    assert "cpu" in data
    assert "ram" in data
    assert data["is_simulation"] is False

def test_hardware_endpoint_simulation(client):
    res = client.get("/api/hardware?simulate=true&preset=high_performance")
    assert res.status_code == 200
    data = res.json()
    assert data["is_simulation"] is True
    assert "Precision" in data["device_model"] or "Dell" in data["manufacturer"]

def test_simulation_presets_endpoint(client):
    res = client.get("/api/simulation/presets")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 6

def test_profiles_endpoint(client):
    res = client.get("/api/profiles")
    assert res.status_code == 200
    data = res.json()
    assert any(p["id"] == "comp_materials_science" for p in data)

def test_reports_list_endpoint(client):
    res = client.get("/api/reports")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)

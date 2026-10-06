"""Test health check and application status endpoints."""

import json
import pytest
from app import app


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_health_endpoint(client):
    """Verify /api/health returns healthy status and metadata."""
    response = client.get("/api/health")
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data["status"] == "healthy"
    assert data["app"] == "GrassQuest"
    assert "tagline" in data
    assert "ai" in data
    assert "voice" in data
    assert data["ai"]["provider"] == "Groq"
    assert data["voice"]["provider"] == "ElevenLabs"


def test_index_page(client):
    """Verify index page loads HTML successfully."""
    response = client.get("/")
    assert response.status_code == 200
    assert b"GrassQuest" in response.data or b"grassquest" in response.data.lower()

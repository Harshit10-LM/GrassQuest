"""Tests for service error handling, API mocks, and controller responses."""

import json
import os
from unittest.mock import MagicMock, patch

import pytest
from app import app
from services.elevenlabs_service import (
    MissingApiKeyError as ElevenLabsMissingKeyError,
    synthesize_speech,
)
from services.groq_service import (
    MissingApiKeyError as GroqMissingKeyError,
    generate_quest_with_ai,
)


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_groq_missing_api_key_raises():
    """Verify Groq service raises error when key is empty."""
    with patch.dict(os.environ, {"GROQ_API_KEY": ""}):
        with pytest.raises(GroqMissingKeyError):
            generate_quest_with_ai("Bored", 20, "Explore")


def test_elevenlabs_missing_api_key_raises():
    """Verify ElevenLabs service raises error when key is empty."""
    with patch.dict(os.environ, {"ELEVENLABS_API_KEY": ""}):
        with pytest.raises(ElevenLabsMissingKeyError):
            synthesize_speech("Your GrassQuest has started.")


def test_api_generate_quest_missing_key_status(client):
    """Verify /api/generate-quest returns HTTP 503 when API key is missing."""
    with patch.dict(os.environ, {"GROQ_API_KEY": ""}):
        response = client.post(
            "/api/generate-quest",
            json={"mood": "Bored", "duration_minutes": 20, "quest_type": "Explore"},
        )
        assert response.status_code == 503
        data = json.loads(response.data)
        assert data["success"] is False
        assert "GROQ_API_KEY" in data["error"] or "Groq API key" in data["error"]


def test_api_tts_missing_key_status(client):
    """Verify /api/tts returns HTTP 503 when ElevenLabs key is missing."""
    with patch.dict(os.environ, {"ELEVENLABS_API_KEY": ""}):
        response = client.post(
            "/api/tts",
            json={"text": "Step outside and walk."},
        )
        assert response.status_code == 503
        data = json.loads(response.data)
        assert data["success"] is False
        assert "ELEVENLABS_API_KEY" in data["error"]


def test_groq_service_mock_success():
    """Verify generate_quest_with_ai succeeds when Groq returns valid JSON."""
    mock_quest_json = {
        "title": "Campus Discovery",
        "summary": "Step outside and discover three quiet alcoves.",
        "duration_minutes": 20,
        "objective": "Explore unfamiliar outdoor spaces.",
        "steps": [
            "Walk past the main library to the shaded grove",
            "Notice the oldest brick structure",
            "Find a bench where you have never sat",
        ],
        "bonus": "Take one photo of sunlight through branches.",
        "distance_target_meters": 800,
        "safety_note": "Watch for bicycles and stay on walkways.",
        "voice_script": "Your GrassQuest has started. Put your phone away and walk.",
    }

    mock_client = MagicMock()
    mock_choice = MagicMock()
    mock_choice.message.content = json.dumps(mock_quest_json)
    mock_client.chat.completions.create.return_value.choices = [mock_choice]

    with patch.dict(os.environ, {"GROQ_API_KEY": "dummy_test_key", "GROQ_MODEL": "openai/gpt-oss-20b"}):
        with patch("services.groq_service.get_groq_client", return_value=mock_client):
            quest = generate_quest_with_ai("Curious", 20, "Explore", "college campus")
            assert quest["title"] == "Campus Discovery"
            assert quest["distance_target_meters"] == 800
            assert len(quest["steps"]) == 3


def test_groq_service_retry_mechanism():
    """Verify that if the first response is bad JSON, retry produces valid quest."""
    bad_first_response = "Here is your quest: NOT VALID JSON {title: broken"
    good_second_response = json.dumps({
        "title": "Recovered Quest",
        "summary": "Valid outdoor mission.",
        "duration_minutes": 15,
        "objective": "Take a mindful loop around the block.",
        "steps": ["Step 1: Walk to the corner", "Step 2: Look for yellow flowers"],
        "bonus": "Find a smooth stone.",
        "distance_target_meters": 600,
        "safety_note": "Stay on the sidewalk.",
        "voice_script": "Your mission begins now. Put your phone away.",
    })

    mock_client = MagicMock()
    first_choice = MagicMock()
    first_choice.message.content = bad_first_response

    second_choice = MagicMock()
    second_choice.message.content = good_second_response

    mock_client.chat.completions.create.side_effect = [
        MagicMock(choices=[first_choice]),
        MagicMock(choices=[second_choice]),
    ]

    with patch.dict(os.environ, {"GROQ_API_KEY": "dummy_test_key"}):
        with patch("services.groq_service.get_groq_client", return_value=mock_client):
            quest = generate_quest_with_ai("Bored", 15, "Walk")
            assert quest["title"] == "Recovered Quest"
            assert mock_client.chat.completions.create.call_count == 2

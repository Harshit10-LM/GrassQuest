"""Tests for quest input validation and AI JSON schema verification."""

import pytest
from utils.validation import (
    ValidationError,
    clean_json_string,
    validate_quest_input,
    validate_quest_json,
)


def test_validate_quest_input_valid():
    """Verify input validation succeeds with valid payload."""
    payload = {
        "mood": "Bored",
        "duration_minutes": 20,
        "quest_type": "Explore",
        "location_context": "campus quad",
    }
    result = validate_quest_input(payload)
    assert result["mood"] == "Bored"
    assert result["duration_minutes"] == 20
    assert result["quest_type"] == "Explore"
    assert result["location_context"] == "campus quad"


def test_validate_quest_input_missing_fields():
    """Verify validation fails when mandatory fields are missing."""
    with pytest.raises(ValidationError) as exc:
        validate_quest_input({"duration_minutes": 20, "quest_type": "Walk"})
    assert "mood" in str(exc.value)

    with pytest.raises(ValidationError) as exc:
        validate_quest_input({"mood": "Curious", "quest_type": "Walk"})
    assert "duration_minutes" in str(exc.value)


def test_validate_quest_input_duration_bounds():
    """Verify duration boundary checks."""
    with pytest.raises(ValidationError):
        validate_quest_input({"mood": "Curious", "duration_minutes": 2, "quest_type": "Walk"})

    with pytest.raises(ValidationError):
        validate_quest_input({"mood": "Curious", "duration_minutes": 200, "quest_type": "Walk"})


def test_clean_json_string():
    """Verify markdown code block fences are stripped properly."""
    raw = "```json\n{\"title\": \"Secret Garden\"}\n```"
    cleaned = clean_json_string(raw)
    assert cleaned == '{"title": "Secret Garden"}'

    raw_plain = "```\n{\"title\": \"Bark Path\"}\n```"
    cleaned_plain = clean_json_string(raw_plain)
    assert cleaned_plain == '{"title": "Bark Path"}'


def test_validate_quest_json_valid():
    """Verify valid quest schema passes with proper data formatting."""
    valid_data = {
        "title": "Neighborhood Detective",
        "summary": "Walk outside and discover details you pass every day.",
        "duration_minutes": 20,
        "objective": "Find three unusual objects in your neighborhood.",
        "steps": [
            "Spot a house number with a vintage font",
            "Identify an unfamiliar leafy tree",
            "Take the left fork at your usual cross street",
        ],
        "bonus": "Take one photo of the oldest mailbox.",
        "distance_target_meters": 850,
        "safety_note": "Look both ways and stay on the sidewalk.",
        "voice_script": "Your GrassQuest has started. Put your phone away and explore.",
    }
    valid, err, sanitized = validate_quest_json(valid_data)
    assert valid is True
    assert err == ""
    assert sanitized["title"] == "Neighborhood Detective"
    assert len(sanitized["steps"]) == 3
    assert sanitized["distance_target_meters"] == 850


def test_validate_quest_json_missing_keys():
    """Verify missing required keys in AI response are caught."""
    incomplete_data = {
        "title": "Short Walk",
        "duration_minutes": 10,
        # missing summary, objective, steps, voice_script, etc.
    }
    valid, err, _ = validate_quest_json(incomplete_data)
    assert valid is False
    assert "Missing required field" in err


def test_validate_quest_json_invalid_steps():
    """Verify steps list must contain at least 2 non-empty items."""
    invalid_steps_data = {
        "title": "Quick Walk",
        "summary": "Step outside.",
        "duration_minutes": 10,
        "objective": "Breathe fresh air.",
        "steps": ["Only one step"],
        "bonus": "None",
        "distance_target_meters": 500,
        "safety_note": "Stay safe",
        "voice_script": "Let's go.",
    }
    valid, err, _ = validate_quest_json(invalid_steps_data)
    assert valid is False
    assert "steps" in err.lower()

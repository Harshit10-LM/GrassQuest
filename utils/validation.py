"""Input and AI output validation for GrassQuest."""

import re
from typing import Any, Dict, Tuple

ALLOWED_MOODS = {"bored", "stressed", "low energy", "curious", "energetic", "social"}
ALLOWED_QUEST_TYPES = {"nature", "walk", "explore", "photography", "social", "surprise me"}
VALID_DURATIONS = {10, 20, 30, 45, 60}


class ValidationError(Exception):
    """Custom exception raised when validation fails."""
    pass


def validate_quest_input(data: Any) -> Dict[str, Any]:
    """Validate incoming quest generation parameters."""
    if not isinstance(data, dict):
        raise ValidationError("Request payload must be a JSON object.")

    mood = data.get("mood")
    if not mood or not isinstance(mood, str) or not mood.strip():
        raise ValidationError("Field 'mood' is required and must be a non-empty string.")
    cleaned_mood = mood.strip()[:60]

    duration = data.get("duration_minutes")
    if duration is None:
        raise ValidationError("Field 'duration_minutes' is required.")
    try:
        duration_int = int(duration)
        if duration_int < 5 or duration_int > 180:
            raise ValidationError("Field 'duration_minutes' must be between 5 and 180 minutes.")
    except (ValueError, TypeError):
        raise ValidationError("Field 'duration_minutes' must be a valid integer.")

    quest_type = data.get("quest_type")
    if not quest_type or not isinstance(quest_type, str) or not quest_type.strip():
        raise ValidationError("Field 'quest_type' is required and must be a non-empty string.")
    cleaned_quest_type = quest_type.strip()[:60]

    location_context = data.get("location_context", "")
    if location_context is not None and not isinstance(location_context, str):
        raise ValidationError("Field 'location_context' must be a string.")
    cleaned_location = (location_context or "").strip()[:150]

    return {
        "mood": cleaned_mood,
        "duration_minutes": duration_int,
        "quest_type": cleaned_quest_type,
        "location_context": cleaned_location,
    }


def clean_json_string(raw: str) -> str:
    """Clean markdown backticks or accidental surrounding markers from LLM response."""
    text = raw.strip()
    # Strip markdown code blocks ```json ... ``` or ``` ... ```
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text)
    return text.strip()


def validate_quest_json(data: Any) -> Tuple[bool, str, Dict[str, Any]]:
    """Validate that the AI response matches the required GrassQuest schema."""
    if not isinstance(data, dict):
        return False, "Output must be a JSON object", {}

    required_keys = [
        "title",
        "summary",
        "duration_minutes",
        "objective",
        "steps",
        "bonus",
        "distance_target_meters",
        "safety_note",
        "voice_script",
    ]

    for key in required_keys:
        if key not in data:
            return False, f"Missing required field '{key}'", {}

    title = str(data["title"]).strip()
    summary = str(data["summary"]).strip()
    objective = str(data["objective"]).strip()
    bonus = str(data["bonus"]).strip()
    safety_note = str(data["safety_note"]).strip()
    voice_script = str(data["voice_script"]).strip()

    if not title:
        return False, "Field 'title' cannot be empty", {}
    if not summary:
        return False, "Field 'summary' cannot be empty", {}
    if not objective:
        return False, "Field 'objective' cannot be empty", {}
    if not voice_script:
        return False, "Field 'voice_script' cannot be empty", {}

    # Steps validation
    steps = data["steps"]
    if not isinstance(steps, list) or len(steps) < 2:
        return False, "Field 'steps' must be a list with at least 2 items", {}
    cleaned_steps = [str(s).strip() for s in steps if str(s).strip()]
    if len(cleaned_steps) < 2:
        return False, "Field 'steps' must have at least 2 non-empty instructions", {}

    # Duration validation
    try:
        duration_minutes = int(data["duration_minutes"])
        if duration_minutes <= 0 or duration_minutes > 300:
            return False, "Field 'duration_minutes' must be a positive integer <= 300", {}
    except (ValueError, TypeError):
        return False, "Field 'duration_minutes' must be an integer", {}

    # Distance target validation
    try:
        distance_target_meters = int(data["distance_target_meters"])
        if distance_target_meters <= 0 or distance_target_meters > 25000:
            return False, "Field 'distance_target_meters' must be a positive integer <= 25000", {}
    except (ValueError, TypeError):
        return False, "Field 'distance_target_meters' must be an integer", {}

    sanitized = {
        "title": title[:100],
        "summary": summary[:300],
        "duration_minutes": duration_minutes,
        "objective": objective[:250],
        "steps": cleaned_steps[:6],
        "bonus": bonus[:200] if bonus else "Take a quiet moment to observe the sky.",
        "distance_target_meters": distance_target_meters,
        "safety_note": safety_note[:250] if safety_note else "Stay on public pathways and watch for vehicle traffic.",
        "voice_script": voice_script[:350],
    }

    return True, "", sanitized

# pyright: reportMissingImports=false
"""Groq service integration for open-weight AI (GPT-OSS 20B) quest generation."""

import json
import logging
import os
from typing import Any, Dict

try:
    from groq import Groq  # type: ignore
except ImportError:
    Groq = None  # type: ignore

from utils.prompts import SYSTEM_PROMPT, build_quest_prompt, build_retry_prompt
from utils.validation import clean_json_string, validate_quest_json

logger = logging.getLogger(__name__)

DEFAULT_MODEL = "openai/gpt-oss-20b"


class MissingApiKeyError(Exception):
    """Raised when an API key is not configured."""
    pass


class QuestGenerationError(Exception):
    """Raised when quest generation fails."""
    pass


def get_groq_model() -> str:
    """Return the configured Groq model name, defaulting to openai/gpt-oss-20b."""
    return os.getenv("GROQ_MODEL", DEFAULT_MODEL).strip() or DEFAULT_MODEL


def get_groq_client():
    """Instantiate and return a Groq client if the API key is present."""
    if Groq is None:
        raise QuestGenerationError(
            "The 'groq' package is not installed. Please run 'pip install groq'."
        )
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if not api_key:
        raise MissingApiKeyError(
            "GROQ_API_KEY is not configured. Please add your Groq API key to your environment or .env file."
        )
    return Groq(api_key=api_key)


def generate_quest_with_ai(mood: str, duration_minutes: int, quest_type: str, location_context: str = "") -> Dict[str, Any]:
    """
    Generate an outdoor quest using the open-weight GPT-OSS 20B model on Groq.
    Includes automated single-retry fallback if the model returns malformed JSON.
    """
    client = get_groq_client()
    model = get_groq_model()

    user_prompt = build_quest_prompt(
        mood=mood,
        duration_minutes=duration_minutes,
        quest_type=quest_type,
        location_context=location_context,
    )

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]

    raw_content = ""
    try:
        logger.info(f"Generating quest using model: {model}")
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.7,
            max_tokens=800,
        )
        raw_content = response.choices[0].message.content or ""
    except Exception as e:
        logger.error(f"Error calling Groq API: {str(e)}")
        # Check if error contains rate limits or authentication
        err_msg = str(e).lower()
        if "authentication" in err_msg or "invalid api key" in err_msg or "unauthorized" in err_msg:
            raise QuestGenerationError("Groq authentication failed. Please verify your GROQ_API_KEY.")
        raise QuestGenerationError("AI service is currently unable to reach the inference provider.")

    cleaned = clean_json_string(raw_content)
    try:
        parsed_json = json.loads(cleaned)
        valid, err_msg, validated_quest = validate_quest_json(parsed_json)
        if valid:
            return validated_quest
        logger.warning(f"Initial AI output validation failed: {err_msg}. Attempting strict retry.")
    except Exception as parse_err:
        logger.warning(f"Initial AI output JSON parsing failed: {str(parse_err)}. Attempting strict retry.")
        err_msg = str(parse_err)

    # Retry once with strict formatting enforcement
    try:
        retry_prompt = build_retry_prompt(raw_content, err_msg)
        retry_messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
            {"role": "assistant", "content": raw_content},
            {"role": "user", "content": retry_prompt},
        ]

        logger.info("Retrying quest generation with strict JSON prompt...")
        retry_response = client.chat.completions.create(
            model=model,
            messages=retry_messages,
            temperature=0.3,
            max_tokens=700,
        )
        retry_raw = retry_response.choices[0].message.content or ""
        retry_cleaned = clean_json_string(retry_raw)
        retry_json = json.loads(retry_cleaned)
        valid, err_msg, validated_quest = validate_quest_json(retry_json)
        if valid:
            return validated_quest
        raise QuestGenerationError(f"Quest validation failed after retry: {err_msg}")
    except Exception as e:
        logger.error(f"Failed to parse or validate retry response: {str(e)}")
        raise QuestGenerationError("We couldn't generate a valid quest format. Please try again.")

"""ElevenLabs Text-to-Speech service integration."""

import logging
import os
from typing import Generator, Optional

import requests

logger = logging.getLogger(__name__)

DEFAULT_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"  # Rachel (calm, clear, natural narrative)
ELEVENLABS_TTS_URL = "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"


class MissingApiKeyError(Exception):
    """Raised when ElevenLabs API key is missing."""
    pass


class TTSServiceError(Exception):
    """Raised when text-to-speech generation fails."""
    pass


def get_elevenlabs_api_key() -> str:
    """Return the configured ElevenLabs API key or raise an exception."""
    api_key = os.getenv("ELEVENLABS_API_KEY", "").strip()
    if not api_key:
        raise MissingApiKeyError(
            "ELEVENLABS_API_KEY is not configured. Please add your ElevenLabs API key to your environment."
        )
    return api_key


def get_voice_id(custom_voice_id: Optional[str] = None) -> str:
    """Return the voice ID to use, with fallback to environment or default."""
    if custom_voice_id and custom_voice_id.strip():
        return custom_voice_id.strip()
    env_voice = os.getenv("ELEVENLABS_VOICE_ID", "").strip()
    return env_voice if env_voice else DEFAULT_VOICE_ID


def synthesize_speech(text: str, voice_id: Optional[str] = None) -> bytes:
    """
    Generate spoken MP3 audio from text using ElevenLabs API.
    Returns raw audio bytes (audio/mpeg).
    """
    if not text or not text.strip():
        raise TTSServiceError("Text to synthesize cannot be empty.")

    cleaned_text = text.strip()[:400]  # Cap to prevent excessive token consumption
    api_key = get_elevenlabs_api_key()
    selected_voice = get_voice_id(voice_id)

    url = ELEVENLABS_TTS_URL.format(voice_id=selected_voice)
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": api_key,
    }
    payload = {
        "text": cleaned_text,
        "model_id": "eleven_turbo_v2_5",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75,
            "style": 0.0,
            "use_speaker_boost": True,
        },
    }

    try:
        logger.info(f"Synthesizing voice with ElevenLabs voice_id: {selected_voice}")
        response = requests.post(url, json=payload, headers=headers, timeout=20)
        
        if response.status_code == 401 or response.status_code == 403:
            logger.error("ElevenLabs authentication failed.")
            raise TTSServiceError("ElevenLabs authentication failed. Please check your ELEVENLABS_API_KEY.")
        
        if response.status_code == 429:
            logger.error("ElevenLabs rate limit or quota exceeded.")
            raise TTSServiceError("ElevenLabs voice quota exceeded. Please try again later.")
            
        if not response.ok:
            logger.error(f"ElevenLabs returned error {response.status_code}: {response.text}")
            # Try fallback model if eleven_turbo_v2_5 is not supported on user's tier
            if response.status_code == 400 and "model" in response.text.lower():
                payload["model_id"] = "eleven_monolingual_v1"
                fallback_res = requests.post(url, json=payload, headers=headers, timeout=20)
                if fallback_res.ok:
                    return fallback_res.content
            raise TTSServiceError("Failed to generate voice audio from provider.")

        return response.content

    except requests.exceptions.Timeout:
        logger.error("ElevenLabs request timed out.")
        raise TTSServiceError("Voice generation request timed out.")
    except TTSServiceError:
        raise
    except Exception as e:
        logger.error(f"Unexpected ElevenLabs error: {str(e)}")
        raise TTSServiceError("Voice guidance service is temporarily unavailable.")

"""GrassQuest Flask Application.
"AI that gives you a mission, then gets out of your way."
Hacktoberfest 2026 Week 1 (Touch Grass) Project.
"""

import io
import logging
import os
from typing import Any, Dict

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request, send_file
from flask_cors import CORS

from services.elevenlabs_service import (
    MissingApiKeyError as ElevenLabsMissingKeyError,
    TTSServiceError,
    synthesize_speech,
)
from services.groq_service import (
    MissingApiKeyError as GroqMissingKeyError,
    QuestGenerationError,
    generate_quest_with_ai,
    get_groq_model,
)
from utils.validation import ValidationError, validate_quest_input

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("grassquest")

app = Flask(__name__)
CORS(app)


@app.route("/")
def index():
    """Render the GrassQuest single-page application."""
    return render_template("index.html")


@app.route("/api/health", methods=["GET"])
def health():
    """Health check endpoint indicating system and AI provider configuration."""
    groq_key_set = bool(os.getenv("GROQ_API_KEY", "").strip())
    eleven_key_set = bool(os.getenv("ELEVENLABS_API_KEY", "").strip())
    model_name = get_groq_model()

    return jsonify({
        "status": "healthy",
        "app": "GrassQuest",
        "tagline": "AI that gives you a mission, then gets out of your way.",
        "version": "1.0.0",
        "hacktoberfest": "2026 Week 1 - Touch Grass",
        "ai": {
            "model": model_name,
            "provider": "Groq",
            "configured": groq_key_set,
        },
        "voice": {
            "provider": "ElevenLabs",
            "configured": eleven_key_set,
        },
    }), 200


@app.route("/api/generate-quest", methods=["POST"])
def generate_quest():
    """Generate an outdoor quest using open-weight AI (GPT-OSS 20B)."""
    if not request.is_json:
        return jsonify({
            "success": False,
            "error": "Request body must be valid JSON.",
        }), 400

    payload = request.get_json()
    try:
        validated_input = validate_quest_input(payload)
    except ValidationError as ve:
        return jsonify({
            "success": False,
            "error": str(ve),
        }), 400

    try:
        quest = generate_quest_with_ai(
            mood=validated_input["mood"],
            duration_minutes=validated_input["duration_minutes"],
            quest_type=validated_input["quest_type"],
            location_context=validated_input["location_context"],
        )
        return jsonify({
            "success": True,
            "quest": quest,
            "metadata": {
                "model": get_groq_model(),
                "provider": "Groq",
            },
        }), 200

    except GroqMissingKeyError:
        logger.warning("Quest generation attempted without GROQ_API_KEY configured.")
        return jsonify({
            "success": False,
            "error": "Groq API key is not configured on the server. Please set GROQ_API_KEY to enable AI quest generation.",
            "code": "MISSING_GROQ_KEY",
        }), 503

    except QuestGenerationError as qe:
        logger.error(f"Quest generation failed: {str(qe)}")
        return jsonify({
            "success": False,
            "error": "We couldn't generate your quest right now. Please try again.",
            "detail": str(qe),
        }), 502

    except Exception as e:
        logger.exception("Unexpected error during quest generation")
        return jsonify({
            "success": False,
            "error": "An unexpected error occurred while preparing your quest. Please try again.",
        }), 500


@app.route("/api/tts", methods=["POST"])
def text_to_speech():
    """Synthesize voice narration for quest start or completion using ElevenLabs."""
    if not request.is_json:
        return jsonify({
            "success": False,
            "error": "Request body must be valid JSON.",
        }), 400

    data = request.get_json()
    text = data.get("text", "")
    voice_id = data.get("voice_id")

    if not text or not isinstance(text, str) or not text.strip():
        return jsonify({
            "success": False,
            "error": "Field 'text' is required and cannot be empty.",
        }), 400

    try:
        audio_bytes = synthesize_speech(text=text, voice_id=voice_id)
        return send_file(
            io.BytesIO(audio_bytes),
            mimetype="audio/mpeg",
            as_attachment=False,
            download_name="grassquest_voice.mp3",
        )

    except ElevenLabsMissingKeyError:
        logger.warning("Voice synthesis attempted without ELEVENLABS_API_KEY configured.")
        return jsonify({
            "success": False,
            "error": "Voice guidance is unavailable because ELEVENLABS_API_KEY is not configured.",
            "code": "MISSING_ELEVENLABS_KEY",
        }), 503

    except TTSServiceError as te:
        logger.warning(f"ElevenLabs TTS service error: {str(te)}")
        return jsonify({
            "success": False,
            "error": "Voice guidance is unavailable right now, but your quest is still ready.",
            "detail": str(te),
        }), 502

    except Exception:
        logger.exception("Unexpected error during TTS synthesis")
        return jsonify({
            "success": False,
            "error": "Voice guidance is temporarily unavailable.",
        }), 500


@app.errorhandler(404)
def not_found(e):
    if request.path.startswith("/api/"):
        return jsonify({"success": False, "error": "Endpoint not found"}), 404
    return render_template("index.html"), 200


@app.errorhandler(500)
def server_error(e):
    return jsonify({"success": False, "error": "Internal server error"}), 500


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5001))
    debug = os.getenv("FLASK_DEBUG", "false").lower() in ("true", "1")
    logger.info(f"Starting GrassQuest server on port {port} (debug={debug})")
    app.run(host="0.0.0.0", port=port, debug=debug)

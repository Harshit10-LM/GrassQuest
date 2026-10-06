"""Prompt construction and templates for open-weight AI (GPT-OSS 20B) quest generation."""

import random

# Variety seeds for "Surprise Me" quest generation
SURPRISE_THEMES = [
    "Sensory observation and acoustic discovery (finding peaceful pocket sounds)",
    "Micro-architecture and hidden masonry (noticing vintage bricks, patterns, gate latches)",
    "Botanical texture hunt (feeling rough bark, damp moss, smooth river rocks safely)",
    "Contrasting shadows and natural light patterns across pathways",
    "Unusual landmarks and eccentric garden ornaments",
    "Mindful compass walking (choosing unexplored forks in the path)",
    "Curious urban wildlife and bird spotting in high branches",
    "Color gradient tracking (locating a spectrum of seasonal foliage)",
]

SYSTEM_PROMPT = """You are GrassQuest AI, an outdoor mission generator powered by open-weight AI (GPT-OSS 20B).
Your primary philosophy is: "AI that gives you a mission, then gets out of your way."
You exist to inspire humans to leave their screens, step outside, explore their physical surroundings, and touch grass.

CORE RULES:
1. Physical Outdoors Only: Every mission must take place outdoors (parks, sidewalks, trails, campuses, quiet streets).
2. Screen-Minimizing: Once the quest starts, the user MUST put their phone in their pocket. Quests must NOT require constant phone interaction, apps, or screen-checking.
3. Strict Safety:
   - NEVER suggest trespassing on private property, gated areas, or construction sites.
   - NEVER suggest walking along unsafe highways, dark alleys, or dangerous train tracks.
   - NO risky physical stunts, climbing heights, or hazardous terrain.
   - NO medical or nutritional advice.
   - NO intrusive interactions with strangers; if social, keep it strictly optional, cheerful, and respectful (e.g., smiling or wishing good morning to a neighbor).
   - Do NOT require specialized or expensive equipment (at most a smartphone camera for one optional photo).
4. Realistic Duration & Distance:
   - Walking speed for a relaxed quest is roughly 60-80 meters per minute.
   - For 10 min: 400 - 700 meters
   - For 20 min: 800 - 1300 meters
   - For 30 min: 1400 - 2000 meters
   - For 45 min: 2200 - 3000 meters
   - For 60 min: 3000 - 4200 meters
5. Playful, Inspiring Tone: Not a boring workout routine or fitness drill. It should feel like a real-world side quest from a charming adventure game.
6. Voice Script: Keep the voice script concise, punchy, and natural (under 45 words). It should announce the start, state the main goal, remind them to put the phone away, and tell them to enjoy the fresh air.

OUTPUT FORMAT:
You MUST respond with valid JSON ONLY. Do not prepend markdown formatting, backticks, or conversational preamble. Return a raw JSON object matching this exact schema:
{
  "title": "Short catchy title (e.g. 'Neighborhood Detective')",
  "summary": "1-2 sentence compelling summary of the mission",
  "duration_minutes": <integer matching requested duration>,
  "objective": "Primary one-sentence goal (e.g. 'Step outside and uncover three quiet details you normally ignore.')",
  "steps": [
    "Specific observation or action 1",
    "Specific observation or action 2",
    "Specific observation or action 3"
  ],
  "bonus": "Fun optional side challenge (e.g. 'Take one quick photo of the oldest leaf you spot.')",
  "distance_target_meters": <integer distance target in meters>,
  "safety_note": "A sensible outdoor safety reminder (e.g. 'Stay on public sidewalks and look both ways before crossing.')",
  "voice_script": "Short spoken intro for ElevenLabs (e.g. 'Your GrassQuest has started. You have 20 minutes. Walk outside, discover three things you overlook, and put your phone in your pocket. See you when you get back.')"
}"""


def build_quest_prompt(mood: str, duration_minutes: int, quest_type: str, location_context: str = "") -> str:
    """Build the user prompt for the open-weight AI model."""
    theme_hint = ""
    if quest_type.lower() == "surprise me":
        theme_hint = f"Surprise Me Focus: {random.choice(SURPRISE_THEMES)}. Produce an unexpected, delightfully curious outdoor mission."
    
    loc_clause = ""
    if location_context and location_context.strip():
        loc_clause = f"Starting context/environment: {location_context.strip()}."
    else:
        loc_clause = "Starting context: General public outdoor area (neighborhood sidewalks, local park, or campus)."

    user_prompt = f"""Generate an outdoor GrassQuest with these parameters:
- User Mood: {mood}
- Time Budget: {duration_minutes} minutes
- Quest Type: {quest_type}
- {loc_clause}
{f'- {theme_hint}' if theme_hint else ''}

Ensure the quest actively addresses the user's mood (e.g., soothing sensory calmness for Stressed, playful curiosities for Bored, refreshing gentle steps for Low Energy, high observation curiosity for Energetic).
Remember: Return ONLY a valid JSON object matching the requested schema with no extra text."""

    return user_prompt


def build_retry_prompt(invalid_content: str, error_detail: str) -> str:
    """Build a strict retry prompt when previous response was not valid JSON."""
    return f"""The previous response failed schema validation.
Error: {error_detail}

You must return ONLY a valid, parseable JSON object matching this exact structure:
{{
  "title": "string",
  "summary": "string",
  "duration_minutes": 20,
  "objective": "string",
  "steps": [
    "string",
    "string",
    "string"
  ],
  "bonus": "string",
  "distance_target_meters": 800,
  "safety_note": "string",
  "voice_script": "string"
}}

Do not enclose in markdown codeblocks (no ```json). Do not include any words before or after the JSON.
Raw JSON output only:"""

# GrassQuest 🌿

> **“AI that gives you a mission, then gets out of your way.”**

Built for **Hacktoberfest 2026 Week 1: DEV “Touch Grass” Challenge**  
Powered by **GPT-OSS 20B (Groq)** • **ElevenLabs** • **Flask** • **Render**

---

## 📌 Project Overview

Modern AI products are almost universally designed to maximize engagement: chat boxes that lure you into infinite conversation, recommendation algorithms that keep your eyes glued to glass, and synthetic companions that replace outdoor living.

**GrassQuest is the antithesis of the screen-addiction trap.**

Instead of keeping you talking to an AI on your phone or laptop, GrassQuest uses an open-weight AI model (**GPT-OSS 20B**) to synthesize your current emotional state, time availability, and physical environment into a realistic, playful outdoor mission. Once your mission is generated, **ElevenLabs** speaks a concise starting instruction into your ears:

> *“Your GrassQuest has started. You have 20 minutes. Walk outside and find three things you normally overlook. Put your phone in your pocket and start walking.”*

The screen immediately switches to a minimal, anti-screen active mode that prompts: **PUT YOUR PHONE IN YOUR POCKET.** Lightweight browser geolocation quietly tallies your walking distance using the Haversine formula while you walk, breathe fresh air, and **touch grass**.

---

## 🎯 Hacktoberfest 2026 Theme: "Touch Grass"

The prompt for Week 1 challenges developers to build software that encourages physical outdoor presence, mental clarity, and genuine interaction with the physical world.

GrassQuest directly embodies this challenge:
1. **Open-Weight AI at the Core:** The open-weight model (`openai/gpt-oss-20b` via Groq) generates context-aware, creative, and strictly safe outdoor quests tailored to user mood (Bored, Stressed, Low Energy, Curious, Energetic, Social).
2. **Not an AI Wrapper or Chatbot:** The AI does not converse or linger. It produces a clear, achievable physical objective, validates its JSON schema, and disappears.
3. **Voice as an Off-Screen Enabler (ElevenLabs):** Spoken audio provides the briefing so you don't need to read cards while crossing the street.
4. **Real-world GPS Telemetry:** Uses the browser's native Geolocation API to measure distance walked, with full support for non-GPS offline modes.
5. **No Accounts, No Tracking, No Friction:** Zero login gates, no cookies, and no database surveillance. Local progress is saved in your own browser's `localStorage`.

---

## 🏗️ Architecture

```
User (Selects Mood, Time, Activity)
  │
  ▼
GrassQuest Frontend (HTML5, Modern CSS Design System, Vanilla JS)
  │
  ▼
Flask Backend (REST API / Gunicorn WSGI)
  │
  ├──► Groq Inference API (openai/gpt-oss-20b open-weight model)
  │      └── Strict JSON validation & automated single-retry fallback
  │
  ├──► ElevenLabs Audio API (xi-api-key)
  │      └── Streaming MP3 audio narration & Web Speech fallback
  │
  ▼
User Steps Outside & Pockets Phone
  │
  ├──► Browser Geolocation API (Haversine formula tracking)
  │
  ▼
Quest Completion Screen (“YOU TOUCHED GRASS”)
  └── Local Storage Quest Log + Web Share API
```

---

## 🚀 Key Features

- **5-Step Distraction-Free Flow:**
  1. **Landing:** Clean introduction and manifesto.
  2. **Quest Setup:** Configure mood, time budget (10–60 min), activity type (Nature, Walk, Explore, Photography, Social, Surprise Me), and optional area context (e.g. "college campus", "quiet park").
  3. **AI Generation:** Live humorous loading status while GPT-OSS 20B formulates the quest.
  4. **Quest Card:** Structured mission breakdown (Objectives, Bonus Challenge, Walking Target, Safety Note, Voice Briefing).
  5. **Anti-Screen Active Mode:** High-contrast countdown, Haversine GPS distance tracker, and prominent reminder to pocket the device.
  6. **Celebration & Share:** Confetti celebration, completion audio, and native Web Share API summary for social sharing.
- **Robust Geolocation & Non-GPS Graceful Fallback:**
  - Client-side Haversine mathematical calculation.
  - Accuracy thresholding (filters out noisy GPS jumps and indoor drift).
  - Works seamlessly if GPS permission is denied or unavailable.
- **Local Quest Log:**
  - Persists completed missions locally in `localStorage` without tracking or backend database overhead.

---

## 🧠 Why Open-Weight AI (GPT-OSS 20B)?

GrassQuest relies on open-weight foundation models (`openai/gpt-oss-20b`) hosted on Groq for several foundational reasons:

1. **Freedom & Transparency:** Open weights ensure the prompts and safety behaviors are fully transparent and modifiable by developers, rather than locked behind proprietary opaque systems.
2. **Deterministic Structured JSON Output:** GPT-OSS 20B excels at adhering to strict JSON schemas, allowing GrassQuest to reliably parse field objectives, distance calculations, and voice scripts.
3. **Ultra-Low Latency Inference:** Running on Groq's LPU architecture, quest generation takes under 1.5 seconds, ensuring users don't wait around indoors.
4. **Safety-Engineered Prompting:** The system prompt strictly prohibits trespassing, hazardous terrain, risky physical stunts, and forced social encounters.

---

## 🎙️ Why ElevenLabs?

In traditional apps, users must stare at instructions, read bullet points, and check their screens at every street corner. That completely defeats the purpose of "touching grass."

ElevenLabs solves this by turning the mission brief into an authentic, natural spoken voice:
- Users hear their mission through their earbuds or phone speaker.
- The voice script specifically instructs them: *"Put your phone in your pocket and start walking."*
- Upon return, ElevenLabs delivers a rewarding mission completion sign-off.
- The app includes graceful degradation: if ElevenLabs keys are not yet configured or quota is exceeded, the browser's native Web Speech API automatically steps in so quests never fail.

---

## ☁️ Why Render?

Render provides the ideal production hosting platform for GrassQuest:
- **Zero Config WSGI Deployment:** Runs Flask natively using `gunicorn app:app`.
- **Infrastructure-as-Code:** Uses [`render.yaml`](file:///Users/harshu/Desktop/GrassQuest/render.yaml) blueprint to declare environment variables, Python version, and build steps.
- **Fast Global Delivery:** Automatic HTTPS, HTTP/2, and global CDN delivery for static assets.

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Frontend** | HTML5, CSS3, Vanilla JavaScript | Lightweight, zero-framework, fast-loading UI |
| **Telemetry** | Browser Geolocation API | Client-side Haversine distance tracking |
| **Backend** | Python 3.11+, Flask 3.1, Flask-CORS | REST API handling AI orchestration & audio |
| **Production WSGI** | Gunicorn | High-performance production application server |
| **AI Inference** | Groq API (`openai/gpt-oss-20b`) | Open-weight quest generation |
| **Voice Synthesis** | ElevenLabs API (`eleven_turbo_v2_5`) | Spoken outdoor instructions |
| **Testing** | Pytest | Unit & integration tests for validation, math, & mocks |
| **Deployment** | Render | Production Web Service |

---

## 📁 Project Structure

```
grassquest/
├── app.py                      # Main Flask application & API routes
├── requirements.txt            # Production Python dependencies
├── Procfile                    # Process definition for Render / PaaS
├── render.yaml                 # Render Blueprint configuration
├── pytest.ini                  # Pytest configuration
├── .env.example                # Template for environment variables
├── .gitignore                  # Git ignore rules for virtualenv & secrets
├── README.md                   # Project documentation
│
├── services/
│   ├── __init__.py
│   ├── groq_service.py         # GPT-OSS 20B inference & retry validation
│   └── elevenlabs_service.py   # ElevenLabs TTS integration & streaming
│
├── utils/
│   ├── __init__.py
│   ├── geo.py                  # Haversine distance formula & formatters
│   ├── prompts.py              # System prompts & variety themes for AI
│   └── validation.py           # Request & AI JSON schema validators
│
├── templates/
│   └── index.html              # Single Page Application HTML markup
│
├── static/
│   ├── css/
│   │   └── style.css           # Modern outdoor-tech design system
│   └── js/
│       ├── gps.js              # Geolocation watcher & Haversine distance
│       ├── quest.js            # Quest generation, audio & local history
│       └── app.js              # UI controller, animations & event handling
│
└── tests/
    ├── test_health.py          # /api/health and index page tests
    ├── test_quest_validation.py # Schema & input validation tests
    ├── test_distance.py        # Haversine math verification tests
    └── test_services.py        # Mocked Groq, ElevenLabs, and error handling
```

---

## ⚙️ Local Development Setup

### 1. Clone the repository
```bash
git clone https://github.com/your-username/grassquest.git
cd grassquest
```

### 2. Create and activate a virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Edit `.env` with your API keys:
```env
# Groq API Key (get free at https://console.groq.com)
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=openai/gpt-oss-20b

# ElevenLabs API Key (get through Hacktoberfest Creator Perks or https://elevenlabs.io)
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM

# Server Port
PORT=5001
FLASK_DEBUG=false
```

### 5. Run the application locally
```bash
python app.py
```
Open your browser at: **`http://localhost:5001`**

---

## 🧪 Running Automated Tests

Run the test suite using `pytest`:
```bash
pytest
```

Output:
```
============================= test session starts ==============================
rootdir: /path/to/GrassQuest
configfile: pytest.ini
testpaths: tests
collected 19 items

tests/test_distance.py ....                                              [ 21%]
tests/test_health.py ..                                                  [ 31%]
tests/test_quest_validation.py .......                                   [ 68%]
tests/test_services.py ......                                            [100%]

============================== 19 passed in 0.20s ==============================
```

Tests verify:
- Flask `/api/health` and HTML index routes.
- Strict input parameter sanitization and duration boundaries.
- AI JSON schema validation, Markdown cleanup, and single-retry recovery.
- Precise Haversine distance calculations and unit formatting.
- Graceful handling of missing API credentials and mock service responses.

---

## 🚢 Deploying to Render

Deploying GrassQuest to Render takes less than 2 minutes:

### Option A: Using `render.yaml` Blueprint (Recommended)
1. Push your repository to GitHub.
2. In the [Render Dashboard](https://dashboard.render.com), select **New** > **Blueprint**.
3. Connect your GitHub repository. Render will automatically read [`render.yaml`](file:///Users/harshu/Desktop/GrassQuest/render.yaml).
4. Fill in the environment variables:
   - `GROQ_API_KEY`: Your Groq API key.
   - `ELEVENLABS_API_KEY`: Your ElevenLabs API key.
5. Click **Apply**. Render will install requirements and start `gunicorn app:app`.

### Option B: Manual Web Service Setup
1. In Render, select **New Web Service**.
2. Set **Runtime**: `Python 3`.
3. Set **Build Command**: `pip install -r requirements.txt`.
4. Set **Start Command**: `gunicorn app:app`.
5. Under **Environment Variables**, add:
   - `GROQ_API_KEY` = `your_groq_key`
   - `GROQ_MODEL` = `openai/gpt-oss-20b`
   - `ELEVENLABS_API_KEY` = `your_elevenlabs_key`
   - `ELEVENLABS_VOICE_ID` = `21m00Tcm4TlvDq8ikWAM`
6. Click **Deploy**.

---

## 🔒 Privacy & Safety Principles

1. **No Data Harvesting:** GrassQuest does not store user location coordinates on any server. Coordinates remain strictly in your browser's volatile memory.
2. **Safe Outdoor Boundaries:** AI generation prompts strictly rule out trespassing on private land, dangerous highways, industrial areas, or reckless physical activities.
3. **No Screen Addiction Mechanics:** No notifications, badges, or endless feeds. GrassQuest celebrates the moment you turn off your phone.

---

## 🌟 Hacktoberfest 2026 Submission Summary

- **Challenge:** DEV Hacktoberfest 2026 Week 1 — "Touch Grass"
- **Open-Weight AI Model:** `openai/gpt-oss-20b` via Groq
- **Audio Voice Synthesis:** ElevenLabs (`eleven_turbo_v2_5`)
- **Hosting Platform:** Render
- **License:** MIT License

*“The best AI application is the one that convinces you to close your laptop and step outside.”* 🌿

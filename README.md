# 🌾 Kisan Saathi — किसान साथी · கிசான் சாத்தி

> Voice-first AI farm companion for Indian farmers — speaks YOUR language.

---

## 🌐 Multilanguage Support

Farmers choose their **state → language** on first launch. Everything — UI, AI responses, audio — is in their native language.

| State | Language | Script | Theme |
|-------|----------|--------|-------|
| 🟠 Maharashtra | मराठी (Marathi) | Devanagari | Green |
| 🔴 Tamil Nadu | தமிழ் (Tamil) | Tamil | Red |
| 🔵 All India | English | Latin | Blue |

**Adding more languages** = one config block. Punjab (ਪੰਜਾਬੀ), Andhra (తెలుగు), Karnataka (ಕನ್ನಡ) etc. all follow the same pattern.

**How language works end-to-end:**
```
Farmer speaks → Whisper detects language automatically
             → Claude responds in SAME language
             → TTS speaks back in same language
             → UI already in farmer's language
```

---

## 🏗 Architecture

```
kisan-saathi/
├── backend/
│   ├── main.py              ← FastAPI server + mobile web UI at /test
│   ├── scheduler.py         ← Daily advice cron job (runs 6 AM daily)
│   ├── db/
│   │   ├── database.py      ← SQLAlchemy models (SQLite dev / Postgres prod)
│   │   └── schema.sql       ← Raw SQL schema reference
│   ├── services/
│   │   ├── ai_service.py    ← Whisper STT, Claude LLM, TTS, Weather API
│   │   ├── prompts.py       ← Multilingual prompt templates
│   │   └── storage.py       ← Audio/image file storage
│   └── requirements.txt
├── flutter_app/
│   ├── lib/
│   │   ├── main.dart
│   │   ├── screens/
│   │   │   ├── home_screen.dart         ← Main voice UI
│   │   │   └── onboarding_screen.dart   ← Language + farm registration
│   │   ├── widgets/
│   │   │   ├── mic_button.dart          ← Large pulsing mic button
│   │   │   ├── daily_advice_card.dart   ← Today's action card
│   │   │   └── response_card.dart       ← AI response + audio playback
│   │   └── services/
│   │       ├── api_service.dart         ← All HTTP calls to backend
│   │       └── audio_service.dart       ← Record + playback
│   ├── lib/kisan_saathi_multilang.jsx   ← React preview (single language)
│   ├── lib/kisan_saathi_three_preview.jsx ← React preview (3 languages)
│   └── pubspec.yaml
├── .env.example             ← API keys template
├── .gitignore
├── HOW_TO_RUN.md            ← Step by step local setup
└── README.md                ← This file
```

---

## 🗄 Database Schema

| Table | Purpose |
|-------|---------|
| `users` | Phone, name, **language preference** |
| `farms` | Village, soil type, irrigation, area, district |
| `farm_memory` | Active crop, stage, last irrigation/fertilizer/pesticide — **auto-updated from conversations** |
| `conversations` | Full voice Q&A history per farm |
| `daily_advice` | Pre-generated daily actions (one per farm per day) |
| `image_diagnoses` | Crop photo diagnosis results |

**Key design:** `farm_memory` is updated automatically after every conversation by Claude Haiku extraction — the farmer never fills a form again after onboarding.

---

## ⚙️ How Language Selection Works

### 1. App Launch — State Picker
```
Screen 1: Choose State
  🟠 Maharashtra  → मराठी
  🔴 Tamil Nadu   → தமிழ்
  🔵 All India    → English
```

### 2. Registration — Everything in chosen language
Soil types, irrigation options, labels — all rendered in native script.

### 3. Voice Input
```python
# Whisper auto-detects language from audio
transcription = whisper.transcribe(audio, language=user.language)
# "mr" for Marathi, "ta" for Tamil, "en" for English
```

### 4. LLM Response
```python
# System prompt tells Claude which language to respond in
system = f"Always respond in {'मराठी' if lang=='mr' else 'தமிழ்' if lang=='ta' else 'English'}"
```

### 5. TTS Audio
```python
# OpenAI TTS speaks back in correct language automatically
audio = openai.audio.speech.create(input=marathi_text, voice="onyx")
```

---

## 🚀 Local Setup (Windows / Mac / Linux)

### Step 1 — Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/kisan-saathi.git
cd kisan-saathi
```

### Step 2 — Create virtual environment
```bash
python -m venv venv

# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate
```

### Step 3 — Install packages
```bash
pip install fastapi "uvicorn[standard]" "sqlalchemy[asyncio]" aiosqlite \
  anthropic openai httpx python-multipart python-dotenv aiofiles pydantic
```

### Step 4 — Add API keys
```bash
cp .env.example .env
# Open .env and fill in your keys
```

| Key | Where to get | Cost |
|-----|-------------|------|
| `ANTHROPIC_API_KEY` | console.anthropic.com | $5 free credit |
| `OPENAI_API_KEY` | platform.openai.com | $5 free credit |
| `OPENWEATHER_API_KEY` | openweathermap.org | Free forever |

### Step 5 — Run the server
```bash
uvicorn backend.main:app --reload --port 8000
```

Open in browser: **http://localhost:8000/test**

### Step 6 — Test on your phone (ngrok)
```bash
# New terminal:
ngrok http 8000

# Update .env:
BASE_URL=https://YOUR_NGROK_URL.ngrok-free.app

# Restart server, then open ngrok URL on your phone
```

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/test` | Mobile web UI (works on phone via ngrok) |
| `GET` | `/health` | Server health check |
| `POST` | `/register-farm` | Register new farmer + language + farm |
| `POST` | `/voice-input` | Upload audio → get Marathi/Tamil/English advice |
| `POST` | `/image-diagnosis` | Upload crop photo → get disease diagnosis |
| `GET` | `/daily-advice/{farm_id}` | Today's pre-generated advice |
| `GET` | `/farm-memory/{farm_id}` | Current farm profile |
| `PUT` | `/farm-memory/{farm_id}` | Update farm state manually |

### Register Farm (now includes language)
```json
POST /register-farm
{
  "phone": "9876543210",
  "name": "रामराव पाटील",
  "village": "साखरवाडी",
  "district": "सोलापूर",
  "language": "mr",
  "crop_name": "सोयाबीन",
  "sowing_date": "2025-06-15",
  "soil_type": "काळी",
  "irrigation_source": "विहीर",
  "area_acres": 5.5
}
```

---

## 💬 Example Conversations

### मराठी (Marathi)
**Farmer:** "आज पाणी द्यायचं का?"
**Kisan Saathi:** "आज पाणी देऊ नका. उद्या ७०% पाऊस येण्याची शक्यता आहे. पाणी दिल्यास मुळं कुजण्याचा धोका आहे."

### தமிழ் (Tamil)
**Farmer:** "இன்று தண்ணீர் பாய்ச்சலாமா?"
**Kisan Saathi:** "இன்று தண்ணீர் பாய்ச்சாதீர்கள். நாளை 70% மழை வாய்ப்பு உள்ளது. வேர் அழுகும் அபாயம் உள்ளது."

### English
**Farmer:** "Should I water today?"
**Kisan Saathi:** "Don't irrigate today. 70% chance of rain in 24 hours. Watering now risks root rot in your crop."

---

## 🧠 Prompt Architecture

Every LLM call includes full context:
```
System prompt:
  ✓ Language instruction (respond in Marathi / Tamil / English)
  ✓ Farmer's village, soil type, irrigation source
  ✓ Current crop + stage + sowing date
  ✓ Last irrigation / fertilizer / pesticide dates
  ✓ Today's weather forecast
  ✓ Last 3 conversations (memory)
  ✓ Rules: 2-3 sentences, actionable, no jargon, no "AI"

User message = transcribed farmer question
```

---

## 🛡 Safety Rules

- Never recommends banned pesticides
- Uncertain diagnosis → asks one follow-up question
- Max 3 sentences per response — no long paragraphs
- Never mentions "AI" or "technology" in responses
- Responds like an experienced neighboring farmer, not a scientist

---

## 💰 Cost Estimate (1000 farmers/day)

| Service | Usage | Daily Cost |
|---------|-------|-----------|
| Claude Opus (advice) | 1000 calls | ~$3.00 |
| Whisper STT | 1000 × 30s | ~$0.18 |
| OpenAI TTS | 1000 responses | ~$0.60 |
| OpenWeather | 1000 calls | Free |
| **Total** | | **~$3.78/day** |

Roughly **₹1/farmer/day** at scale.

---

## 🗺 Roadmap

- [x] Marathi voice support
- [x] Tamil voice support
- [x] English support
- [x] Crop photo diagnosis
- [x] Daily advice scheduler
- [x] Auto farm memory from conversations
- [ ] Hindi (हिंदी) — next
- [ ] Telugu (తెలుగు)
- [ ] Kannada (ಕನ್ನಡ)
- [ ] WhatsApp integration
- [ ] SMS fallback (no internet)
- [ ] Offline mode (cache last advice)
- [ ] Flutter Android APK

---

## 🏭 Production Deployment (Railway.app — recommended)

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up

# Set environment variables in Railway dashboard
# DATABASE_URL, ANTHROPIC_API_KEY, OPENAI_API_KEY, OPENWEATHER_API_KEY
```

Railway gives you: free HTTPS, auto-deploy from GitHub, managed Postgres.

---

Built with ❤️ for Indian farmers · Powered by Claude (Anthropic) + Whisper (OpenAI)

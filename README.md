# 🌾 Kisan Saathi - किसान साथी

Voice-first AI farm companion for Marathi-speaking farmers.

---

## Architecture

```
kisan-saathi/
├── backend/
│   ├── main.py              ← FastAPI app (all endpoints)
│   ├── scheduler.py         ← Daily advice cron job
│   ├── db/
│   │   ├── database.py      ← SQLAlchemy models + DB connection
│   │   └── schema.sql       ← Raw SQL schema
│   ├── services/
│   │   ├── ai_service.py    ← Whisper STT, Claude LLM, TTS, Weather
│   │   ├── prompts.py       ← All Marathi prompt templates
│   │   └── storage.py       ← File storage (local or S3)
│   └── requirements.txt
└── flutter_app/
    ├── lib/
    │   ├── main.dart
    │   ├── screens/
    │   │   ├── home_screen.dart        ← Main voice UI
    │   │   └── onboarding_screen.dart  ← Farm registration
    │   ├── widgets/
    │   │   ├── mic_button.dart         ← Large pulsing mic button
    │   │   ├── daily_advice_card.dart  ← Today's action card
    │   │   └── response_card.dart      ← AI response display
    │   └── services/
    │       ├── api_service.dart        ← HTTP calls to backend
    │       └── audio_service.dart      ← Record + playback
    └── pubspec.yaml
```

---

## Database Schema

| Table | Purpose |
|-------|---------|
| `users` | Phone + name, language preference |
| `farms` | Village, soil type, irrigation, area |
| `farm_memory` | Active crop, stage, last irrigation/fertilizer/pesticide |
| `conversations` | Full history of voice Q&A |
| `daily_advice` | Pre-generated daily actions |
| `image_diagnoses` | Crop photo diagnosis results |

**Key design:** `farm_memory` is updated automatically from every conversation by Claude, so the system always knows the current crop stage without the farmer filling any forms.

---

## Setup — Local Development

### 1. Database

```bash
# PostgreSQL
psql -U postgres
CREATE DATABASE kisansaathi;
\q

# Run schema
psql -U postgres -d kisansaathi -f backend/db/schema.sql
```

### 2. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Set environment variables
cp ../.env.example .env
# Edit .env with your API keys

# Start server
uvicorn backend.main:app --reload --port 8000
```

**API Keys needed:**
- `ANTHROPIC_API_KEY` → https://console.anthropic.com
- `OPENAI_API_KEY` → https://platform.openai.com (for Whisper STT + TTS)
- `OPENWEATHER_API_KEY` → https://openweathermap.org/api (free tier)

### 3. Flutter App

```bash
cd flutter_app

# Install dependencies
flutter pub get

# Set your server IP in lib/services/api_service.dart:
# static const String _baseUrl = 'http://YOUR_SERVER_IP:8000';

# Run on device
flutter run
```

### 4. Daily Scheduler (Cron)

```bash
# Run once manually to test
python -m backend.scheduler

# Add to crontab (6 AM every day)
crontab -e
# Add: 0 6 * * * cd /your/project && python -m backend.scheduler
```

---

## API Endpoints

### POST /register-farm
Register new farmer + farm.

```json
{
  "phone": "9876543210",
  "name": "रामराव पाटील",
  "village": "साखरवाडी",
  "district": "सोलापूर",
  "crop_name": "सोयाबीन",
  "sowing_date": "2025-06-15",
  "soil_type": "काळी",
  "irrigation_source": "विहीर",
  "area_acres": 5.5
}
```

Response:
```json
{"user_id": "uuid", "farm_id": "uuid"}
```

### POST /voice-input
Send farmer's voice recording.

Form fields: `farm_id`, `user_id`, `audio` (file)

Response:
```json
{
  "question": "आज खत घालू का?",
  "advice": "आज खत घालू नका. उद्या पाऊस येईल त्यामुळे खत वाहून जाईल. परवा दुपारी घाला.",
  "audio_url": "http://server/static/audio/advice_abc123.mp3"
}
```

### POST /image-diagnosis
Send crop photo for disease detection.

Form fields: `farm_id`, `user_id`, `image` (file)

Response:
```json
{
  "diagnosis": "पानांवर करपा रोग आहे. उद्या सकाळी लवकर फवारणी करा.",
  "audio_url": "http://server/static/audio/diag_xyz789.mp3"
}
```

### GET /daily-advice/{farm_id}
Get today's pre-generated daily advice.

### GET /farm-memory/{farm_id}
Get current farm profile stored in system.

### PUT /farm-memory/{farm_id}
Manually update farm state.

---

## Example Conversation

**Farmer:** "आज पाणी द्यायचं का?"
*(Should I irrigate today?)*

**System processes:**
1. Transcribes via Whisper (Marathi)
2. Loads farm profile: Soybean, flowering stage, last irrigated 4 days ago
3. Fetches weather: Rain probability 72% in next 24h
4. Builds prompt with all context
5. Claude generates response

**Response (text + audio):**
> "आज पाणी देऊ नका. उद्या पाऊस येण्याची 70% शक्यता आहे. आत्ता पाणी दिल्यास मुळं कुजण्याचा धोका आहे."

---

**Farmer:** (sends photo of yellowing leaves)

**Response:**
> "पानांवर नायट्रोजनची कमतरता दिसते. आठवड्याभरात युरिया खते द्या - एकरी 10 किलो. पाऊस आधी द्यायला जमल्यास चांगले."

---

## Prompt Architecture

Every LLM call includes:

```
System prompt contains:
  ✓ Farmer's full farm profile (village, soil, crop, stage)
  ✓ Last irrigation / fertilizer / pesticide dates
  ✓ Today's weather forecast
  ✓ Last 3 conversations (context)
  ✓ Behavioral rules (simple language, actionable, 2-3 sentences)

User message = farmer's transcribed question
```

Memory is automatically updated after every conversation using a fast extraction call to `claude-haiku`.

---

## Safety Rules

- Never recommends banned pesticides (list enforced via system prompt)
- If image diagnosis confidence < 60% → asks follow-up question
- Responses always in Marathi
- Maximum 3 sentences per response
- Never mentions "AI" in responses
- Direct action always given (no hedging)

---

## Production Deployment (Single VM)

```bash
# Ubuntu 22.04, minimum 2 vCPU, 4GB RAM

# Install dependencies
apt install postgresql python3-pip nginx

# Run with systemd
# /etc/systemd/system/kisansaathi.service
[Unit]
Description=Kisan Saathi API

[Service]
WorkingDirectory=/opt/kisan-saathi
ExecStart=uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 2
Restart=always
EnvironmentFile=/opt/kisan-saathi/.env

[Install]
WantedBy=multi-user.target

# Nginx reverse proxy with SSL (recommended)
# Use certbot for free SSL
```

---

## Cost Estimate (per 1000 farmers, daily)

| Service | Usage | Cost |
|---------|-------|------|
| Claude Opus (LLM) | 1000 conversations | ~$3 |
| Whisper (STT) | 1000 × 30s audio | ~$0.18 |
| OpenAI TTS | 1000 responses | ~$0.60 |
| Weather API | 1000 calls | Free |
| PostgreSQL | Managed | ~$10/mo |
| **Total** | | **~$100/mo** |

Roughly **₹1/farmer/day** at scale.

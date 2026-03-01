# 🌾 Kisan Saathi — How to Run (Step by Step)

Follow this exactly. Takes about 10 minutes.

---

## Step 1 — Get the code onto your laptop

```bash
# If you downloaded as zip, unzip it. Then:
cd kisan-saathi
```

---

## Step 2 — Create Python virtual environment

```bash
python3 -m venv venv
source venv/bin/activate        # Mac/Linux
# OR on Windows:
# venv\Scripts\activate
```

---

## Step 3 — Install packages

```bash
pip install --upgrade pip

pip install \
  fastapi==0.115.0 \
  "uvicorn[standard]==0.30.6" \
  "sqlalchemy[asyncio]==2.0.35" \
  aiosqlite==0.20.0 \
  anthropic==0.36.2 \
  openai==1.51.0 \
  httpx==0.27.2 \
  python-multipart==0.0.12 \
  python-dotenv==1.0.1 \
  aiofiles==24.1.0 \
  pydantic==2.9.2
```

Takes ~2 minutes. You'll see packages downloading.

---

## Step 4 — Get your API keys

### A) Anthropic (Claude) — Required
1. Go to https://console.anthropic.com
2. Sign up / log in
3. Click "API Keys" → "Create Key"
4. Copy the key (starts with `sk-ant-`)

**Free credits:** New accounts get $5 free credits.
Each voice question costs ~$0.01. You get ~500 free questions.

### B) OpenAI (Whisper + TTS) — Required
1. Go to https://platform.openai.com/api-keys
2. Sign up / log in
3. Click "Create new secret key"
4. Copy the key (starts with `sk-`)

**Free credits:** New accounts get $5 free credits.
Whisper: $0.006/min. TTS: $0.015/1000 chars.
100 test conversations ≈ $0.50 total.

### C) OpenWeather — Optional (free, no card)
1. Go to https://openweathermap.org/api
2. Sign up free
3. Go to "API Keys" tab
4. Copy your key

---

## Step 5 — Create .env file

```bash
cp .env.example .env
```

Open `.env` in any text editor and replace the values:

```
ANTHROPIC_API_KEY=sk-ant-YOUR-ACTUAL-KEY-HERE
OPENAI_API_KEY=sk-YOUR-ACTUAL-KEY-HERE
OPENWEATHER_API_KEY=your-weather-key-here
BASE_URL=http://localhost:8000
```

---

## Step 6 — Start the server

```bash
# Make sure venv is active (you see (venv) in terminal)
source venv/bin/activate

uvicorn backend.main:app --reload --port 8000
```

You should see:
```
==================================================
🌾  Kisan Saathi running!
    Local test UI  → http://localhost:8000/test
    API docs       → http://localhost:8000/docs
==================================================
```

---

## Step 7 — Test in browser (your laptop)

Open: **http://localhost:8000/test**

1. Fill in the registration form (phone + village required)
2. Click "नोंदणी करा"
3. Press the big green mic button 🎤
4. Say something in Marathi (or any language to test)
5. Press again to stop
6. Wait ~5 seconds for response
7. Press 🔊 to hear the audio reply

---

## Step 8 — Test on your PHONE (via ngrok)

### Install ngrok:
```bash
# Mac:
brew install ngrok/ngrok/ngrok

# OR download from: https://ngrok.com/download
# Create free account at ngrok.com to get authtoken
ngrok authtoken YOUR_TOKEN_HERE
```

### Start ngrok (in a NEW terminal tab):
```bash
ngrok http 8000
```

You'll see something like:
```
Forwarding  https://abc123def456.ngrok-free.app → localhost:8000
```

### Update .env with your ngrok URL:
```bash
# Edit .env:
BASE_URL=https://abc123def456.ngrok-free.app
```

### Restart the server:
```bash
# Press Ctrl+C to stop, then:
uvicorn backend.main:app --reload --port 8000
```

### On your phone:
Open **https://abc123def456.ngrok-free.app/test** in Chrome/Safari

✅ You now have a real AI farm advisor running on your phone!

---

## What the test costs (rough estimate)

| Action | API calls | Cost |
|--------|-----------|------|
| Register farm | 0 | Free |
| 1 voice question | Whisper + Claude + TTS | ~₹0.80 |
| 1 photo diagnosis | Claude Vision | ~₹0.70 |
| Daily advice | Claude | ~₹0.50 |
| **50 test sessions** | | **~₹50** |

---

## Troubleshooting

**`ModuleNotFoundError: No module named 'backend'`**
```bash
# Run from the kisan-saathi root folder, not inside backend/
cd kisan-saathi
uvicorn backend.main:app --reload --port 8000
```

**`❌ ANTHROPIC_API_KEY not set`**
→ You forgot to edit `.env`. Open it and add your real key.

**Microphone not working on phone**
→ ngrok must use HTTPS (it does by default). HTTP won't allow mic access.

**`502 STT failed`**
→ Check your OPENAI_API_KEY in `.env`

**Audio plays on laptop but not phone**
→ Update BASE_URL in `.env` to your ngrok URL and restart server.

---

## File structure

```
kisan-saathi/
├── backend/
│   ├── main.py              ← FastAPI app + mobile web UI at /test
│   ├── db/database.py       ← SQLite/Postgres models
│   └── services/
│       ├── ai_service.py    ← Whisper, Claude, TTS, Weather
│       ├── prompts.py       ← Marathi prompt templates
│       └── storage.py       ← File handling
├── flutter_app/             ← Native Android app (build after Stage 1 works)
├── .env                     ← YOUR API KEYS (never commit this)
├── .env.example             ← Template
└── HOW_TO_RUN.md            ← This file
```

---

## Next steps after Stage 1 works

1. ✅ Stage 1 done — test on your phone via ngrok
2. Deploy to Railway.app (Stage 2)
3. Build Flutter APK and install on test farmer's phone
4. Test with real Marathi voice input
5. Add SMS/WhatsApp notification for daily advice

"""
Kisan Saathi — FastAPI Backend
--------------------------------
Dev mode  : SQLite  (default, zero config)
Prod mode : Postgres (set DATABASE_URL env var)

Run locally:
    source venv/bin/activate
    uvicorn backend.main:app --reload --port 8000

Then open:
    http://localhost:8000/test        ← mobile-friendly web UI
    http://localhost:8000/docs        ← auto API docs
"""

import json
import os
import uuid
from datetime import date, datetime
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy import select

load_dotenv()

from backend.db.database import (
    Conversation, DailyAdvice, Farm, FarmMemory,
    ImageDiagnosis, User, get_db, init_db,
)
from backend.services import ai_service
from backend.services.storage import save_image, audio_path_for_tts

STORAGE_DIR = os.getenv("STORAGE_DIR", "/tmp/kisan_files")
BASE_URL    = os.getenv("BASE_URL", "http://localhost:8000")

Path(f"{STORAGE_DIR}/audio").mkdir(parents=True, exist_ok=True)
Path(f"{STORAGE_DIR}/images").mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Kisan Saathi API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)

app.mount("/static/audio",  StaticFiles(directory=f"{STORAGE_DIR}/audio"),  name="audio")
app.mount("/static/images", StaticFiles(directory=f"{STORAGE_DIR}/images"), name="images")


@app.on_event("startup")
async def startup():
    await init_db()
    print(f"\n{'='*50}")
    print(f"🌾  Kisan Saathi running!")
    print(f"    Local test UI  → {BASE_URL}/test")
    print(f"    API docs       → {BASE_URL}/docs")
    print(f"    Health check   → {BASE_URL}/health")
    print(f"{'='*50}\n")


# ══════════════════════════════════════════════════════════
# MOBILE WEB UI  — works on any phone via ngrok
# ══════════════════════════════════════════════════════════

MOBILE_UI_HTML = r"""
<!DOCTYPE html>
<html lang="mr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
<title>किसान साथी</title>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Devanagari:wght@400;600;700&display=swap" rel="stylesheet">
<style>
* { box-sizing: border-box; margin: 0; padding: 0; -webkit-tap-highlight-color: transparent; }
body {
  font-family: 'Noto Sans Devanagari', sans-serif;
  background: #f1f8e9; min-height: 100vh;
  display: flex; flex-direction: column; align-items: center; padding: 16px;
}
h1 { color: #2e7d32; font-size: 26px; margin-bottom: 2px; text-align: center; }
.subtitle { color: #777; font-size: 13px; margin-bottom: 20px; }
.card {
  background: white; border-radius: 16px; padding: 18px;
  width: 100%; max-width: 480px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08); margin-bottom: 14px;
}
.card-green {
  background: linear-gradient(135deg, #1b5e20, #388e3c);
  color: white;
}
input, select {
  width: 100%; padding: 14px; font-size: 17px;
  border: 2px solid #ddd; border-radius: 10px; margin-bottom: 10px;
  font-family: inherit; background: white;
}
input:focus, select:focus { border-color: #2e7d32; outline: none; }
.btn {
  width: 100%; padding: 16px; font-size: 19px; font-weight: 700;
  border: none; border-radius: 14px; cursor: pointer; margin-bottom: 10px;
  font-family: inherit; transition: opacity 0.15s;
}
.btn:active { opacity: 0.8; }
.btn-green  { background: #2e7d32; color: white; }
.btn-amber  { background: #f57c00; color: white; }
.btn-disabled { background: #ccc; color: #888; cursor: not-allowed; }
#mic-wrap { display: flex; flex-direction: column; align-items: center; margin: 8px 0 16px; }
#mic-btn {
  width: 160px; height: 160px; border-radius: 50%;
  font-size: 56px; background: #2e7d32; color: white;
  border: none; cursor: pointer;
  box-shadow: 0 6px 24px rgba(46,125,50,0.35);
  transition: background 0.2s, transform 0.1s;
  display: flex; align-items: center; justify-content: center;
}
#mic-btn.recording {
  background: #c62828 !important;
  animation: pulse 0.7s ease-in-out infinite alternate;
}
#mic-btn:active { transform: scale(0.95); }
@keyframes pulse {
  from { box-shadow: 0 0 0 0 rgba(198,40,40,0.4); }
  to   { box-shadow: 0 0 0 20px rgba(198,40,40,0); }
}
#mic-label { font-size: 17px; color: #555; margin-top: 10px; font-weight: 600; }
#status { font-size: 15px; text-align: center; min-height: 22px; margin: 6px 0; }
.err { color: #c62828; } .ok { color: #2e7d32; }
.spinner {
  width: 36px; height: 36px; margin: 10px auto;
  border: 4px solid #ddd; border-top-color: #2e7d32;
  border-radius: 50%; animation: spin 0.7s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
.hidden { display: none !important; }
.label { font-size: 12px; opacity: 0.7; margin-bottom: 4px; }
.advice-text { font-size: 19px; line-height: 1.55; font-weight: 600; }
.q-text { font-size: 14px; color: #888; font-style: italic; margin-bottom: 8px; }
.play-btn {
  margin-top: 12px; padding: 11px 18px; font-size: 17px;
  border: none; border-radius: 10px; cursor: pointer;
  font-family: inherit; font-weight: 700;
}
.play-btn-light { background: rgba(255,255,255,0.25); color: white; }
.play-btn-dark  { background: #2e7d32; color: white; width: 100%; margin-top: 10px; }
h2 { color: #2e7d32; font-size: 17px; margin-bottom: 10px; }
#camera-input { display: none; }
.chip-row { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 10px; }
.chip {
  padding: 10px 16px; border-radius: 20px; font-size: 16px; cursor: pointer;
  border: 2px solid #ccc; background: white; font-family: inherit;
  transition: all 0.15s;
}
.chip.selected { background: #2e7d32; color: white; border-color: #2e7d32; }
</style>
</head>
<body>

<h1>🌾 किसान साथी</h1>
<p class="subtitle">Voice-first AI farm advisor · Marathi</p>

<!-- ── REGISTRATION ───────────────────────────── -->
<div id="setup-card" class="card">
  <h2>📋 शेत नोंदणी</h2>
  <input id="i-phone"    type="tel"  placeholder="📱 फोन नंबर *" />
  <input id="i-name"     type="text" placeholder="👤 आपले नाव" />
  <input id="i-village"  type="text" placeholder="🏘 गाव *" />
  <input id="i-district" type="text" placeholder="🗺 जिल्हा" />
  <input id="i-crop"     type="text" placeholder="🌱 पीक (कापूस, सोयाबीन...)" />

  <p style="font-size:15px;color:#555;margin-bottom:6px;">माती:</p>
  <div class="chip-row" id="soil-chips">
    <button class="chip" onclick="selectChip('soil',this,'काळी')">काळी</button>
    <button class="chip" onclick="selectChip('soil',this,'लाल')">लाल</button>
    <button class="chip" onclick="selectChip('soil',this,'वालुकामय')">वालुकामय</button>
    <button class="chip" onclick="selectChip('soil',this,'चिकण')">चिकण</button>
  </div>

  <p style="font-size:15px;color:#555;margin-bottom:6px;">पाण्याचा स्रोत:</p>
  <div class="chip-row" id="irr-chips">
    <button class="chip" onclick="selectChip('irr',this,'विहीर')">विहीर</button>
    <button class="chip" onclick="selectChip('irr',this,'नळ')">नळ</button>
    <button class="chip" onclick="selectChip('irr',this,'ठिबक')">ठिबक</button>
    <button class="chip" onclick="selectChip('irr',this,'पाऊस')">पाऊस</button>
  </div>

  <button class="btn btn-green" onclick="registerFarm()">✅ नोंदणी करा → सुरू करा</button>
</div>

<!-- ── MAIN UI ────────────────────────────────── -->
<div id="main-ui" class="hidden" style="width:100%;max-width:480px;">

  <div id="daily-card" class="card card-green hidden">
    <div class="label">🌅 आजचे काम</div>
    <div id="daily-text" class="advice-text"></div>
    <div id="daily-weather" style="font-size:13px;opacity:0.75;margin-top:6px;"></div>
    <button class="play-btn play-btn-light" onclick="playAudio('daily')">🔊 ऐका</button>
  </div>

  <div id="response-card" class="card hidden">
    <div id="q-text" class="q-text"></div>
    <div class="label">🌾 सल्ला:</div>
    <div id="advice-text" class="advice-text"></div>
    <button class="play-btn play-btn-dark" onclick="playAudio('response')">🔊 उत्तर ऐका</button>
  </div>

  <div id="status"></div>
  <div id="spinner" class="spinner hidden"></div>

  <div id="mic-wrap">
    <button id="mic-btn" onclick="toggleRecording()">🎤</button>
    <div id="mic-label">बोलण्यासाठी दाबा</div>
  </div>

  <button class="btn btn-amber" onclick="document.getElementById('camera-input').click()">
    📸 पीक फोटो पाठवा
  </button>
  <input type="file" id="camera-input" accept="image/*" capture="environment" onchange="uploadImage(this)">

  <div style="text-align:center;margin-top:16px;">
    <button onclick="resetFarm()" style="background:none;border:none;color:#aaa;font-size:13px;cursor:pointer;">
      ⚙ वेगळ्या शेताने सुरू करा
    </button>
  </div>
</div>

<script>
let farmId = localStorage.getItem('farm_id');
let userId = localStorage.getItem('user_id');
let recorder = null, audioChunks = [], isRecording = false;
let dailyAudioUrl = null, responseAudioUrl = null;
let selectedSoil = '', selectedIrr = '';

function selectChip(type, el, val) {
  const row = document.getElementById(type === 'soil' ? 'soil-chips' : 'irr-chips');
  row.querySelectorAll('.chip').forEach(c => c.classList.remove('selected'));
  el.classList.add('selected');
  if (type === 'soil') selectedSoil = val; else selectedIrr = val;
}

window.onload = () => {
  if (farmId) { showMain(); loadDaily(); }
};

function showMain() {
  document.getElementById('setup-card').classList.add('hidden');
  document.getElementById('main-ui').classList.remove('hidden');
}

function resetFarm() {
  localStorage.clear(); location.reload();
}

// ── Register ─────────────────────────────────────
async function registerFarm() {
  const phone = v('i-phone'), village = v('i-village');
  if (!phone || !village) { status('फोन आणि गाव आवश्यक आहे', 'err'); return; }
  loading(true);
  try {
    const r = await fetch('/register-farm', {
      method: 'POST', headers: {'Content-Type':'application/json'},
      body: JSON.stringify({
        phone, village,
        name: v('i-name'), district: v('i-district'),
        crop_name: v('i-crop'),
        soil_type: selectedSoil, irrigation_source: selectedIrr,
      })
    });
    const d = await r.json();
    if (!r.ok) throw new Error(d.detail || 'Error');
    farmId = d.farm_id; userId = d.user_id;
    localStorage.setItem('farm_id', farmId);
    localStorage.setItem('user_id', userId);
    showMain(); loadDaily();
    status('✅ नोंदणी झाली!', 'ok');
  } catch(e) { status('नोंदणी झाली नाही: ' + e.message, 'err'); }
  finally { loading(false); }
}

// ── Daily advice ─────────────────────────────────
async function loadDaily() {
  try {
    const r = await fetch(`/daily-advice/${farmId}`);
    const d = await r.json();
    el('daily-text').textContent = d.advice;
    el('daily-weather').textContent = d.weather ? '☁️ ' + d.weather : '';
    el('daily-card').classList.remove('hidden');
    dailyAudioUrl = d.audio_url;
  } catch(e) {}
}

// ── Voice ────────────────────────────────────────
async function toggleRecording() {
  if (isRecording) { stopRec(); } else { await startRec(); }
}

async function startRec() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    audioChunks = [];
    recorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });
    recorder.ondataavailable = e => audioChunks.push(e.data);
    recorder.onstop = sendAudio;
    recorder.start();
    isRecording = true;
    el('mic-btn').classList.add('recording');
    el('mic-btn').textContent = '⏹';
    el('mic-label').textContent = 'बोला... थांबवण्यासाठी दाबा';
    el('mic-label').style.color = '#c62828';
    status('');
  } catch(e) { status('मायक्रोफोन परवानगी द्या', 'err'); }
}

function stopRec() {
  if (recorder && recorder.state !== 'inactive') {
    recorder.stop();
    recorder.stream.getTracks().forEach(t => t.stop());
  }
  isRecording = false;
  el('mic-btn').classList.remove('recording');
  el('mic-btn').textContent = '🎤';
  el('mic-label').textContent = 'बोलण्यासाठी दाबा';
  el('mic-label').style.color = '#555';
}

async function sendAudio() {
  if (!audioChunks.length) return;
  loading(true); status('सल्ला येतो आहे...');
  try {
    const blob = new Blob(audioChunks, { type: 'audio/webm' });
    const form = new FormData();
    form.append('farm_id', farmId); form.append('user_id', userId);
    form.append('audio', blob, 'voice.webm');
    const r = await fetch('/voice-input', { method:'POST', body:form });
    const d = await r.json();
    if (!r.ok) throw new Error(d.detail || 'Upload failed');
    el('q-text').textContent = '❓ ' + (d.question || '');
    el('advice-text').textContent = d.advice || '';
    el('response-card').classList.remove('hidden');
    responseAudioUrl = d.audio_url;
    status('');
    if (d.audio_url) playAudio('response');
  } catch(e) { status('माफ करा, पुन्हा करा: ' + e.message, 'err'); }
  finally { loading(false); }
}

// ── Image ────────────────────────────────────────
async function uploadImage(input) {
  if (!input.files[0]) return;
  loading(true); status('फोटो तपासतो आहे...');
  try {
    const form = new FormData();
    form.append('farm_id', farmId); form.append('user_id', userId);
    form.append('image', input.files[0]);
    const r = await fetch('/image-diagnosis', { method:'POST', body:form });
    const d = await r.json();
    if (!r.ok) throw new Error(d.detail || 'Failed');
    el('q-text').textContent = '📸 पीक फोटो निदान';
    el('advice-text').textContent = d.diagnosis || '';
    el('response-card').classList.remove('hidden');
    responseAudioUrl = d.audio_url;
    status('');
    if (d.audio_url) playAudio('response');
  } catch(e) { status('फोटो पाठवता आला नाही: ' + e.message, 'err'); }
  finally { loading(false); }
}

// ── Audio ─────────────────────────────────────────
function playAudio(type) {
  const url = type === 'daily' ? dailyAudioUrl : responseAudioUrl;
  if (!url) { status('ऑडिओ उपलब्ध नाही', 'err'); return; }
  new Audio(url).play().catch(() => status('ऑडिओ चालू होत नाही', 'err'));
}

// ── Helpers ───────────────────────────────────────
const el = id => document.getElementById(id);
const v  = id => el(id).value.trim();
function status(msg, cls='') {
  el('status').textContent = msg;
  el('status').className = cls;
}
function loading(on) {
  el('spinner').classList.toggle('hidden', !on);
  el('mic-btn').disabled = on;
}
</script>
</body>
</html>
"""


@app.get("/test", response_class=HTMLResponse)
async def test_ui():
    return HTMLResponse(content=MOBILE_UI_HTML)


# ══════════════════════════════════════════════════════════
# Schemas
# ══════════════════════════════════════════════════════════

class RegisterFarmRequest(BaseModel):
    phone: str
    name: Optional[str] = None
    village: Optional[str] = None
    taluka: Optional[str] = None
    district: Optional[str] = None
    area_acres: Optional[float] = None
    soil_type: Optional[str] = None
    irrigation_source: Optional[str] = None
    crop_name: Optional[str] = None
    crop_variety: Optional[str] = None
    sowing_date: Optional[str] = None


# ══════════════════════════════════════════════════════════
# Internal helpers
# ══════════════════════════════════════════════════════════

async def get_farm_profile(farm_id: str, db) -> dict:
    from sqlalchemy.ext.asyncio import AsyncSession
    farm = await db.get(Farm, uuid.UUID(farm_id))
    if not farm:
        return {}
    mem_result = await db.execute(
        select(FarmMemory).where(FarmMemory.farm_id == farm.id).limit(1)
    )
    mem = mem_result.scalar_one_or_none()
    profile = {
        "village": farm.village, "taluka": farm.taluka,
        "district": farm.district, "soil_type": farm.soil_type,
        "irrigation_source": farm.irrigation_source, "area_acres": farm.area_acres,
    }
    if mem:
        profile.update({
            "crop_name": mem.crop_name, "crop_variety": mem.crop_variety,
            "sowing_date": str(mem.sowing_date) if mem.sowing_date else None,
            "crop_stage": mem.crop_stage,
            "last_irrigation_date": str(mem.last_irrigation_date) if mem.last_irrigation_date else None,
            "last_fertilizer": mem.last_fertilizer,
            "last_fertilizer_date": str(mem.last_fertilizer_date) if mem.last_fertilizer_date else None,
            "last_pesticide": mem.last_pesticide,
            "last_pesticide_date": str(mem.last_pesticide_date) if mem.last_pesticide_date else None,
        })
    return profile


async def get_recent_conversations(farm_id: str, db, limit: int = 3) -> list:
    result = await db.execute(
        select(Conversation)
        .where(Conversation.farm_id == uuid.UUID(farm_id))
        .order_by(Conversation.created_at.desc())
        .limit(limit)
    )
    convs = result.scalars().all()
    return [{"input_text": c.input_text, "response_text": c.response_text} for c in reversed(convs)]


async def apply_memory_updates(farm_id: str, updates: dict, db):
    if not updates:
        return
    mem_result = await db.execute(
        select(FarmMemory).where(FarmMemory.farm_id == uuid.UUID(farm_id))
    )
    mem = mem_result.scalar_one_or_none()
    for field in ["sowing_date", "last_irrigation_date", "last_fertilizer_date", "last_pesticide_date"]:
        if field in updates and isinstance(updates[field], str):
            try:
                updates[field] = date.fromisoformat(updates[field])
            except ValueError:
                updates.pop(field, None)
    if mem:
        for k, v in updates.items():
            if hasattr(mem, k) and v is not None:
                setattr(mem, k, v)
        mem.updated_at = datetime.utcnow()
    else:
        mem = FarmMemory(farm_id=uuid.UUID(farm_id), **updates)
        db.add(mem)
    await db.commit()


# ══════════════════════════════════════════════════════════
# API Endpoints
# ══════════════════════════════════════════════════════════

@app.get("/health")
async def health():
    return {"status": "ok", "version": "1.0.0", "time": datetime.utcnow().isoformat()}


@app.post("/register-farm")
async def register_farm(req: RegisterFarmRequest, db=Depends(get_db)):
    result = await db.execute(select(User).where(User.phone == req.phone))
    user = result.scalar_one_or_none()
    if not user:
        user = User(phone=req.phone, name=req.name, language="mr")
        db.add(user)
        await db.flush()

    farm = Farm(
        user_id=user.id, village=req.village, taluka=req.taluka,
        district=req.district, area_acres=req.area_acres,
        soil_type=req.soil_type, irrigation_source=req.irrigation_source,
    )
    db.add(farm)
    await db.flush()

    if req.crop_name:
        sowing = None
        if req.sowing_date:
            try:
                sowing = date.fromisoformat(req.sowing_date)
            except ValueError:
                pass
        mem = FarmMemory(
            farm_id=farm.id, crop_name=req.crop_name,
            crop_variety=req.crop_variety, sowing_date=sowing,
        )
        db.add(mem)

    await db.commit()
    return {"user_id": str(user.id), "farm_id": str(farm.id)}


@app.post("/voice-input")
async def voice_input(
    farm_id: str = Form(...), user_id: str = Form(...),
    audio: UploadFile = File(...), db=Depends(get_db),
):
    audio_bytes = await audio.read()

    try:
        question = await ai_service.transcribe_audio(audio_bytes)
    except Exception as e:
        raise HTTPException(502, f"STT failed: {e}")

    if not question.strip():
        return {"error": "आवाज ऐकू आला नाही. पुन्हा प्रयत्न करा."}

    farm_profile = await get_farm_profile(farm_id, db)
    recent = await get_recent_conversations(farm_id, db)

    weather = {}
    try:
        weather = await ai_service.get_weather(
            farm_profile.get("village", ""), farm_profile.get("district", "Pune")
        )
    except Exception:
        pass

    try:
        advice = await ai_service.get_farm_advice(question, farm_profile, weather, recent)
    except Exception as e:
        raise HTTPException(502, f"LLM failed: {e}")

    audio_url = None
    try:
        fname = f"advice_{uuid.uuid4().hex[:8]}.mp3"
        fpath = audio_path_for_tts(fname)
        await ai_service.text_to_speech(advice, fpath)
        audio_url = f"{BASE_URL}/static/audio/{fname}"
    except Exception:
        pass

    conv = Conversation(
        user_id=uuid.UUID(user_id), farm_id=uuid.UUID(farm_id),
        input_text=question, response_text=advice, response_audio_url=audio_url,
    )
    db.add(conv)
    await db.commit()

    try:
        updates = await ai_service.extract_farm_updates(question, advice)
        await apply_memory_updates(farm_id, updates, db)
    except Exception:
        pass

    return {"question": question, "advice": advice, "audio_url": audio_url, "weather": weather}


@app.post("/image-diagnosis")
async def image_diagnosis(
    farm_id: str = Form(...), user_id: str = Form(...),
    image: UploadFile = File(...), db=Depends(get_db),
):
    image_bytes = await image.read()
    _, img_url = save_image(image_bytes)
    farm_profile = await get_farm_profile(farm_id, db)

    try:
        result = await ai_service.diagnose_crop_image(image_bytes, farm_profile)
    except Exception as e:
        raise HTTPException(502, f"Diagnosis failed: {e}")

    diagnosis_text = result["diagnosis_text"]

    audio_url = None
    try:
        fname = f"diag_{uuid.uuid4().hex[:8]}.mp3"
        fpath = audio_path_for_tts(fname)
        await ai_service.text_to_speech(diagnosis_text, fpath)
        audio_url = f"{BASE_URL}/static/audio/{fname}"
    except Exception:
        pass

    diag = ImageDiagnosis(
        farm_id=uuid.UUID(farm_id), user_id=uuid.UUID(user_id),
        image_url=img_url, diagnosis=diagnosis_text,
        confidence=result.get("confidence"), action_advised=diagnosis_text,
    )
    db.add(diag)
    await db.commit()

    return {"diagnosis": diagnosis_text, "audio_url": audio_url, "image_url": img_url}


@app.get("/daily-advice/{farm_id}")
async def get_daily_advice(farm_id: str, db=Depends(get_db)):
    today = date.today()
    result = await db.execute(
        select(DailyAdvice)
        .where(DailyAdvice.farm_id == uuid.UUID(farm_id))
        .where(DailyAdvice.advice_date == today)
    )
    advice = result.scalar_one_or_none()

    if not advice:
        farm_profile = await get_farm_profile(farm_id, db)
        weather = {}
        try:
            weather = await ai_service.get_weather(
                farm_profile.get("village", ""), farm_profile.get("district", "Pune")
            )
        except Exception:
            pass

        advice_text = await ai_service.generate_daily_advice(farm_profile, weather)

        audio_url = None
        try:
            fname = f"daily_{uuid.uuid4().hex[:8]}.mp3"
            fpath = audio_path_for_tts(fname)
            await ai_service.text_to_speech(advice_text, fpath)
            audio_url = f"{BASE_URL}/static/audio/{fname}"
        except Exception:
            pass

        advice = DailyAdvice(
            farm_id=uuid.UUID(farm_id), advice_text=advice_text,
            advice_audio_url=audio_url, weather_summary=weather.get("raw", ""),
            advice_date=today,
        )
        db.add(advice)
        await db.commit()

    return {
        "date": str(advice.advice_date),
        "advice": advice.advice_text,
        "audio_url": advice.advice_audio_url,
        "weather": advice.weather_summary,
    }


@app.get("/farm-memory/{farm_id}")
async def get_farm_memory(farm_id: str, db=Depends(get_db)):
    profile = await get_farm_profile(farm_id, db)
    if not profile:
        raise HTTPException(404, "Farm not found")
    return profile

"""
AI Orchestration — Kisan Saathi
Handles: STT (Whisper), LLM (Claude), TTS (OpenAI), Weather, Memory extraction.

All functions raise clear exceptions when API keys are missing.
"""
import base64
import json
import os
import re
import tempfile
from pathlib import Path

import httpx

from backend.services.prompts import (
    IMAGE_DIAGNOSIS_PROMPT, MEMORY_EXTRACTION_PROMPT,
    DAILY_ADVICE_PROMPT, build_advisor_prompt,
)

ANTHROPIC_KEY    = os.getenv("ANTHROPIC_API_KEY", "")
OPENAI_KEY       = os.getenv("OPENAI_API_KEY", "")
WEATHER_API_KEY  = os.getenv("OPENWEATHER_API_KEY", "")


def _require(key_name: str, value: str):
    if not value or value.startswith("sk-ant-REPLACE") or value == "REPLACE_ME":
        raise EnvironmentError(
            f"❌ {key_name} not set in .env — please add your API key"
        )


# ── Speech → Text ────────────────────────────────────────────

async def transcribe_audio(audio_bytes: bytes, language: str = "mr") -> str:
    """Transcribe Marathi audio using OpenAI Whisper."""
    _require("OPENAI_API_KEY", OPENAI_KEY)

    suffix = ".webm"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as f:
        f.write(audio_bytes)
        tmp_path = f.name

    try:
        async with httpx.AsyncClient(timeout=40) as client:
            with open(tmp_path, "rb") as af:
                resp = await client.post(
                    "https://api.openai.com/v1/audio/transcriptions",
                    headers={"Authorization": f"Bearer {OPENAI_KEY}"},
                    files={"file": ("audio.webm", af, "audio/webm")},
                    data={"model": "whisper-1", "language": language},
                )
            resp.raise_for_status()
            return resp.json().get("text", "").strip()
    finally:
        Path(tmp_path).unlink(missing_ok=True)


# ── Text → Speech ────────────────────────────────────────────

async def text_to_speech(text: str, output_path: str) -> str:
    """Convert Marathi text to MP3 using OpenAI TTS."""
    _require("OPENAI_API_KEY", OPENAI_KEY)

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            "https://api.openai.com/v1/audio/speech",
            headers={
                "Authorization": f"Bearer {OPENAI_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "tts-1",
                "input": text,
                "voice": "onyx",
                "speed": 0.9,
            },
        )
        resp.raise_for_status()
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(resp.content)
    return output_path


# ── Weather ───────────────────────────────────────────────────

async def get_weather(village: str = "", district: str = "Pune") -> dict:
    """Fetch 24h forecast from OpenWeatherMap."""
    if not WEATHER_API_KEY or WEATHER_API_KEY == "REPLACE_ME":
        # Return a safe fallback so the rest of the flow still works
        return {
            "temp_max": "?", "temp_min": "?",
            "rain_probability": 0, "humidity": "?",
            "raw": "हवामान माहिती उपलब्ध नाही",
        }

    location = f"{village},{district},IN" if village else f"{district},IN"
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(
            "https://api.openweathermap.org/data/2.5/forecast",
            params={
                "q": location, "appid": WEATHER_API_KEY,
                "units": "metric", "cnt": 8, "lang": "mr",
            },
        )

    if resp.status_code != 200:
        return {"temp_max": "?", "rain_probability": 0, "raw": "हवामान माहिती नाही"}

    data  = resp.json()
    items = data.get("list", [])
    rain_probs = [i.get("pop", 0) * 100 for i in items]
    temps      = [i["main"]["temp"] for i in items if "main" in i]
    humidity   = items[0]["main"]["humidity"] if items else "?"
    desc       = items[0]["weather"][0]["description"] if items else ""
    max_rain   = round(max(rain_probs)) if rain_probs else 0

    return {
        "temp_max": round(max(temps)) if temps else "?",
        "temp_min": round(min(temps)) if temps else "?",
        "rain_probability": max_rain,
        "humidity": humidity,
        "description": desc,
        "raw": f"तापमान {round(max(temps) if temps else 0)}°C, {desc}, पाऊस शक्यता {max_rain}%",
    }


# ── LLM Advisor (Claude) ──────────────────────────────────────

async def get_farm_advice(
    question: str,
    farm_profile: dict,
    weather: dict,
    recent_conversations: list,
) -> str:
    """Ask Claude for Marathi farming advice."""
    _require("ANTHROPIC_API_KEY", ANTHROPIC_KEY)

    import anthropic
    client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)

    system_prompt, user_msg = build_advisor_prompt(
        farm_profile, weather, recent_conversations, question
    )

    msg = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=250,
        system=system_prompt,
        messages=[{"role": "user", "content": user_msg}],
    )
    return msg.content[0].text.strip()


# ── Image Diagnosis (Claude Vision) ──────────────────────────

async def diagnose_crop_image(image_bytes: bytes, farm_profile: dict) -> dict:
    """Analyse crop photo using Claude Vision."""
    _require("ANTHROPIC_API_KEY", ANTHROPIC_KEY)

    import anthropic
    client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)

    b64 = base64.standard_b64encode(image_bytes).decode()
    prompt = IMAGE_DIAGNOSIS_PROMPT.format(
        crop_name=farm_profile.get("crop_name", "पीक"),
        crop_stage=farm_profile.get("crop_stage", "अज्ञात"),
    )

    msg = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=200,
        messages=[{
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": b64}},
                {"type": "text", "text": prompt},
            ],
        }],
    )
    return {"diagnosis_text": msg.content[0].text.strip(), "confidence": 0.85}


# ── Memory Extraction (cheap Claude Haiku call) ───────────────

async def extract_farm_updates(input_text: str, response_text: str) -> dict:
    """Extract farm state updates from conversation using Claude Haiku."""
    _require("ANTHROPIC_API_KEY", ANTHROPIC_KEY)

    import anthropic
    client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)

    conversation = f"शेतकरी: {input_text}\nसल्लागार: {response_text}"
    prompt = MEMORY_EXTRACTION_PROMPT.format(conversation=conversation)

    msg = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=250,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = msg.content[0].text.strip()
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if match:
        try:
            updates = json.loads(match.group())
            return {k: v for k, v in updates.items() if v is not None}
        except json.JSONDecodeError:
            pass
    return {}


# ── Daily Advice ──────────────────────────────────────────────

async def generate_daily_advice(farm_profile: dict, weather: dict) -> str:
    """Generate today's key farm action."""
    _require("ANTHROPIC_API_KEY", ANTHROPIC_KEY)

    import anthropic
    from datetime import date
    client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)

    prompt = DAILY_ADVICE_PROMPT.format(
        crop_name=farm_profile.get("crop_name", "पीक"),
        crop_stage=farm_profile.get("crop_stage", "अज्ञात"),
        last_irrigation_date=farm_profile.get("last_irrigation_date", "माहित नाही"),
        last_fertilizer=farm_profile.get("last_fertilizer", "माहित नाही"),
        last_fertilizer_date=farm_profile.get("last_fertilizer_date", "") or "",
        date=date.today().strftime("%d/%m/%Y"),
        weather_summary=weather.get("raw", "हवामान माहिती नाही"),
    )

    msg = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=150,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text.strip()

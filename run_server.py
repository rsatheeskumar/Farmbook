"""
Kisan Saathi - Runnable Backend (Flask + SQLite)
Works with zero external dependencies beyond Flask.

AI calls are stubbed with realistic Marathi responses for local testing.
Swap the stub functions with real API calls when deploying.

Run: python3 run_server.py
Test: python3 test_api.py
"""

import json
import os
import sqlite3
import uuid
from datetime import date, datetime
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory

# ─────────────────────────────────────────────
# Config
# ─────────────────────────────────────────────
DB_PATH = "/tmp/kisansaathi.db"
STORAGE_DIR = "/tmp/kisan_files"
BASE_URL = "http://localhost:5000"

Path(f"{STORAGE_DIR}/audio").mkdir(parents=True, exist_ok=True)
Path(f"{STORAGE_DIR}/images").mkdir(parents=True, exist_ok=True)

app = Flask(__name__)


# ─────────────────────────────────────────────
# Database setup
# ─────────────────────────────────────────────

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            phone TEXT UNIQUE NOT NULL,
            name TEXT,
            language TEXT DEFAULT 'mr',
            created_at TEXT DEFAULT (datetime('now')),
            last_active TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS farms (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL REFERENCES users(id),
            name TEXT DEFAULT 'माझी शेती',
            village TEXT,
            taluka TEXT,
            district TEXT,
            area_acres REAL,
            soil_type TEXT,
            irrigation_source TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS farm_memory (
            id TEXT PRIMARY KEY,
            farm_id TEXT NOT NULL REFERENCES farms(id),
            crop_name TEXT,
            crop_variety TEXT,
            sowing_date TEXT,
            crop_stage TEXT,
            last_irrigation_date TEXT,
            last_fertilizer TEXT,
            last_fertilizer_date TEXT,
            last_pesticide TEXT,
            last_pesticide_date TEXT,
            notes TEXT,
            updated_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS conversations (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL REFERENCES users(id),
            farm_id TEXT REFERENCES farms(id),
            input_text TEXT,
            response_text TEXT,
            response_audio_url TEXT,
            intent TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS daily_advice (
            id TEXT PRIMARY KEY,
            farm_id TEXT NOT NULL REFERENCES farms(id),
            advice_text TEXT NOT NULL,
            advice_audio_url TEXT,
            weather_summary TEXT,
            advice_date TEXT DEFAULT (date('now')),
            created_at TEXT DEFAULT (datetime('now')),
            UNIQUE(farm_id, advice_date)
        );

        CREATE TABLE IF NOT EXISTS image_diagnoses (
            id TEXT PRIMARY KEY,
            farm_id TEXT REFERENCES farms(id),
            user_id TEXT NOT NULL REFERENCES users(id),
            image_url TEXT,
            diagnosis TEXT,
            confidence REAL,
            action_advised TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        );
    """)
    conn.commit()
    conn.close()
    print("✅ Database initialised at", DB_PATH)


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

def get_farm_profile(farm_id: str, conn) -> dict:
    farm = conn.execute("SELECT * FROM farms WHERE id = ?", (farm_id,)).fetchone()
    if not farm:
        return {}
    mem = conn.execute(
        "SELECT * FROM farm_memory WHERE farm_id = ? ORDER BY updated_at DESC LIMIT 1",
        (farm_id,)
    ).fetchone()

    profile = dict(farm)
    if mem:
        profile.update(dict(mem))
    return profile


def get_recent_conversations(farm_id: str, conn, limit=3) -> list:
    rows = conn.execute(
        "SELECT input_text, response_text FROM conversations "
        "WHERE farm_id = ? ORDER BY created_at DESC LIMIT ?",
        (farm_id, limit)
    ).fetchall()
    return [dict(r) for r in reversed(rows)]


# ─────────────────────────────────────────────
# AI Stubs  (replace with real API calls in prod)
# ─────────────────────────────────────────────

def stub_transcribe(audio_bytes: bytes) -> str:
    """Simulates Whisper STT. Returns a realistic Marathi question."""
    questions = [
        "आज पाणी द्यायचं का?",
        "खते कधी घालायची?",
        "पानं पिवळी पडत आहेत, काय करू?",
        "फवारणी करायची का आज?",
        "किती दिवसांनी कापणी होईल?",
    ]
    # Cycle through questions based on audio size for demo variety
    return questions[len(audio_bytes) % len(questions)]


def stub_get_weather(village: str, district: str) -> dict:
    """Simulates OpenWeather API response."""
    return {
        "temp_max": 34,
        "temp_min": 22,
        "rain_probability": 65,
        "humidity": 78,
        "description": "partly cloudy",
        "raw": f"तापमान 34°C, अंशतः ढगाळ, पाऊस शक्यता 65%",
    }


def stub_get_advice(question: str, profile: dict, weather: dict, history: list) -> str:
    """Simulates Claude LLM response - returns contextual Marathi advice."""
    crop = profile.get("crop_name", "पीक")
    rain = weather.get("rain_probability", 0)
    
    advice_map = {
        "पाणी": (
            f"आज पाणी देऊ नका. पुढील 24 तासांत {rain}% पाऊस येण्याची शक्यता आहे. "
            f"परवा पाऊस नसेल तर संध्याकाळी पाणी द्या."
        ) if rain > 60 else (
            f"आज संध्याकाळी {crop} ला पाणी द्या. "
            f"उन्हाळ्यात सकाळी पाणी दिल्यास बाष्पीभवन जास्त होते."
        ),
        "खते": (
            f"पुढील 3 दिवस पाऊस आहे, त्यामुळे आत्ता खते देऊ नका. "
            f"खते वाहून जातील. पाऊस थांबल्यावर युरिया द्या."
        ),
        "पिवळी": (
            f"{crop} च्या पानांवर नायट्रोजनची कमतरता दिसते. "
            f"एकरी 10 किलो युरिया द्या. पाण्यात मिसळून दिल्यास लवकर गुण येतो."
        ),
        "फवारणी": (
            f"आज फवारणी करू नका - वारा जास्त आहे, फवारणी वाया जाते. "
            f"उद्या सकाळी 7 वाजेपूर्वी फवारणी करा."
        ),
        "कापणी": (
            f"{crop} अजून 15-20 दिवसांत काढणीसाठी तयार होईल. "
            f"आत्ता पाणी बंद करा म्हणजे दाणे चांगले भरतील."
        ),
    }
    
    for keyword, response in advice_map.items():
        if keyword in question:
            return response
    
    return (
        f"तुमचा {crop} चांगला दिसतो. आज हवामान ठीक आहे. "
        f"पाण्याची आणि खतांची वेळ पाळत राहा."
    )


def stub_diagnose_image(image_bytes: bytes, profile: dict) -> dict:
    """Simulates Claude Vision diagnosis."""
    crop = profile.get("crop_name", "पीक")
    diagnoses = [
        {
            "diagnosis_text": f"{crop} च्या पानांवर करपा रोग आहे. उद्या सकाळी लवकर फवारणी करा. एक लिटर पाण्यात 2 ग्राम बुरशीनाशक मिसळा.",
            "confidence": 0.87,
        },
        {
            "diagnosis_text": f"पानांवर मावा किडीचा प्रादुर्भाव आहे. आज संध्याकाळी इमिडाक्लोप्रिड फवारा. 10 दिवसांनी पुन्हा तपासा.",
            "confidence": 0.79,
        },
        {
            "diagnosis_text": f"{crop} निरोगी दिसतो. पिवळसर रंग पाण्याच्या कमतरतेमुळ
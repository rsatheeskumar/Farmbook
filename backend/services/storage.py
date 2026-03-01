"""
File storage service.
Stores audio and images locally (or S3 if configured).
"""
import os
import uuid
from pathlib import Path

STORAGE_DIR = os.getenv("STORAGE_DIR", "/tmp/kisan_saathi_files")
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

Path(STORAGE_DIR).mkdir(parents=True, exist_ok=True)
Path(f"{STORAGE_DIR}/audio").mkdir(exist_ok=True)
Path(f"{STORAGE_DIR}/images").mkdir(exist_ok=True)


def save_audio(audio_bytes: bytes, prefix: str = "response") -> tuple[str, str]:
    """Save audio bytes to disk, return (file_path, public_url)."""
    filename = f"{prefix}_{uuid.uuid4().hex[:8]}.mp3"
    path = f"{STORAGE_DIR}/audio/{filename}"
    with open(path, "wb") as f:
        f.write(audio_bytes)
    url = f"{BASE_URL}/static/audio/{filename}"
    return path, url


def save_image(image_bytes: bytes) -> tuple[str, str]:
    """Save image bytes to disk, return (file_path, public_url)."""
    filename = f"img_{uuid.uuid4().hex[:8]}.jpg"
    path = f"{STORAGE_DIR}/images/{filename}"
    with open(path, "wb") as f:
        f.write(image_bytes)
    url = f"{BASE_URL}/static/images/{filename}"
    return path, url


def audio_path_for_tts(filename: str) -> str:
    return f"{STORAGE_DIR}/audio/{filename}"

"""
Daily scheduler - run as a cron job at 6:00 AM every day.
Generates "Today's Farm Action" for all active farms.

Usage: python -m backend.scheduler
Or cron: 0 6 * * * /usr/bin/python -m backend.scheduler
"""
import asyncio
import os
import uuid
from datetime import date

from sqlalchemy import select

from .db.database import AsyncSessionLocal, DailyAdvice, Farm, FarmMemory, init_db
from .services import ai_service, storage


async def generate_for_all_farms():
    await init_db()
    async with AsyncSessionLocal() as db:
        # Get all farms
        result = await db.execute(select(Farm))
        farms = result.scalars().all()
        
        print(f"[Scheduler] Generating daily advice for {len(farms)} farms on {date.today()}")
        
        for farm in farms:
            try:
                # Build profile
                from .main import get_farm_profile
                profile = await get_farm_profile(str(farm.id), db)
                
                # Weather
                weather = {}
                try:
                    weather = await ai_service.get_weather(
                        profile.get("village", ""),
                        profile.get("district", "Pune")
                    )
                except Exception:
                    pass
                
                # Generate advice
                advice_text = await ai_service.generate_daily_advice(profile, weather)
                
                # TTS
                audio_filename = f"daily_{uuid.uuid4().hex[:8]}.mp3"
                audio_path = storage.audio_path_for_tts(audio_filename)
                audio_url = None
                try:
                    await ai_service.text_to_speech(advice_text, audio_path)
                    audio_url = f"{os.getenv('BASE_URL', 'http://localhost:8000')}/static/audio/{audio_filename}"
                except Exception:
                    pass
                
                # Upsert
                existing = await db.execute(
                    select(DailyAdvice)
                    .where(DailyAdvice.farm_id == farm.id)
                    .where(DailyAdvice.advice_date == date.today())
                )
                existing_row = existing.scalar_one_or_none()
                
                if existing_row:
                    existing_row.advice_text = advice_text
                    existing_row.advice_audio_url = audio_url
                    existing_row.weather_summary = weather.get("raw", "")
                else:
                    advice = DailyAdvice(
                        farm_id=farm.id,
                        advice_text=advice_text,
                        advice_audio_url=audio_url,
                        weather_summary=weather.get("raw", ""),
                        advice_date=date.today(),
                    )
                    db.add(advice)
                
                await db.commit()
                print(f"[Scheduler] Farm {farm.id}: {advice_text[:60]}...")
            
            except Exception as e:
                print(f"[Scheduler] Error for farm {farm.id}: {e}")


if __name__ == "__main__":
    asyncio.run(generate_for_all_farms())

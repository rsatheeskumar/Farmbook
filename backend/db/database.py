"""
Database — SQLite for local dev, PostgreSQL for production.
Auto-detected via DATABASE_URL environment variable.

Dev  (default): sqlite+aiosqlite:///./kisansaathi.db
Prod:           postgresql+asyncpg://user:pass@host/dbname
"""
import os
from datetime import date, datetime
from uuid import uuid4

from sqlalchemy import Column, Date, DateTime, Float, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite+aiosqlite:///./kisansaathi.db"   # ← zero-config local dev
)

# SQLite needs check_same_thread=False
connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}

engine = create_async_engine(
    DATABASE_URL,
    connect_args=connect_args,
    echo=False,
)

AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()


# ── Models ──────────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"
    id       = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    phone    = Column(String, unique=True, nullable=False)
    name     = Column(String)
    language = Column(String, default="mr")
    created_at  = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)


class Farm(Base):
    __tablename__ = "farms"
    id         = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id    = Column(String(36), ForeignKey("users.id"), nullable=False)
    name       = Column(String, default="माझी शेती")
    village    = Column(String)
    taluka     = Column(String)
    district   = Column(String)
    area_acres = Column(Float)
    soil_type  = Column(String)
    irrigation_source = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)


class FarmMemory(Base):
    __tablename__ = "farm_memory"
    id            = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    farm_id       = Column(String(36), ForeignKey("farms.id"), nullable=False)
    crop_name     = Column(String)
    crop_variety  = Column(String)
    sowing_date   = Column(Date)
    crop_stage    = Column(String)
    last_irrigation_date  = Column(Date)
    last_fertilizer       = Column(String)
    last_fertilizer_date  = Column(Date)
    last_pesticide        = Column(String)
    last_pesticide_date   = Column(Date)
    notes      = Column(Text)
    updated_at = Column(DateTime, default=datetime.utcnow)


class Conversation(Base):
    __tablename__ = "conversations"
    id                 = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id            = Column(String(36), ForeignKey("users.id"), nullable=False)
    farm_id            = Column(String(36), ForeignKey("farms.id"))
    input_text         = Column(Text)
    input_audio_url    = Column(Text)
    response_text      = Column(Text)
    response_audio_url = Column(Text)
    intent     = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)


class DailyAdvice(Base):
    __tablename__ = "daily_advice"
    id              = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    farm_id         = Column(String(36), ForeignKey("farms.id"), nullable=False)
    advice_text     = Column(Text, nullable=False)
    advice_audio_url = Column(Text)
    weather_summary = Column(Text)
    advice_date     = Column(Date, default=date.today)
    created_at      = Column(DateTime, default=datetime.utcnow)
    __table_args__  = (UniqueConstraint("farm_id", "advice_date"),)


class ImageDiagnosis(Base):
    __tablename__ = "image_diagnoses"
    id            = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    farm_id       = Column(String(36), ForeignKey("farms.id"))
    user_id       = Column(String(36), ForeignKey("users.id"), nullable=False)
    image_url     = Column(Text)
    diagnosis     = Column(Text)
    confidence    = Column(Float)
    action_advised = Column(Text)
    created_at    = Column(DateTime, default=datetime.utcnow)


# ── Session dependency ───────────────────────────────────────

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print(f"✅ DB ready ({DATABASE_URL.split('///')[0]})")

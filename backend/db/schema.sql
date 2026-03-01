-- Kisan Saathi Database Schema
-- Run: psql -U postgres -d kisansaathi -f schema.sql

CREATE DATABASE kisansaathi;
\c kisansaathi;

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    phone TEXT UNIQUE NOT NULL,
    name TEXT,
    language TEXT DEFAULT 'mr',  -- mr = Marathi
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_active TIMESTAMPTZ DEFAULT NOW()
);

-- Farms table
CREATE TABLE farms (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name TEXT DEFAULT 'माझी शेती',
    village TEXT,
    taluka TEXT,
    district TEXT,
    area_acres NUMERIC(6,2),
    soil_type TEXT,  -- काळी, लाल, वालुकामय
    irrigation_source TEXT,  -- विहीर, नळ, पाऊस
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Farm memory - current crop state (updated from conversations)
CREATE TABLE farm_memory (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    farm_id UUID NOT NULL REFERENCES farms(id) ON DELETE CASCADE,
    crop_name TEXT,           -- कापूस, सोयाबीन, तूर
    crop_variety TEXT,
    sowing_date DATE,
    crop_stage TEXT,          -- उगवण, वाढ, फुलोरा, काढणी
    last_irrigation_date DATE,
    last_fertilizer TEXT,
    last_fertilizer_date DATE,
    last_pesticide TEXT,
    last_pesticide_date DATE,
    notes TEXT,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Conversation history
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    farm_id UUID REFERENCES farms(id),
    input_text TEXT,           -- transcribed farmer question
    input_audio_url TEXT,      -- stored audio URL
    response_text TEXT,        -- AI response in Marathi
    response_audio_url TEXT,   -- TTS audio URL
    intent TEXT,               -- irrigation, pest, weather, fertilizer, etc
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Daily advice - generated each morning
CREATE TABLE daily_advice (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    farm_id UUID NOT NULL REFERENCES farms(id) ON DELETE CASCADE,
    advice_text TEXT NOT NULL,
    advice_audio_url TEXT,
    weather_summary TEXT,
    advice_date DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(farm_id, advice_date)
);

-- Image diagnoses
CREATE TABLE image_diagnoses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    farm_id UUID REFERENCES farms(id),
    user_id UUID NOT NULL REFERENCES users(id),
    image_url TEXT NOT NULL,
    diagnosis TEXT,
    confidence NUMERIC(4,2),
    action_advised TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_created_at ON conversations(created_at DESC);
CREATE INDEX idx_daily_advice_farm_date ON daily_advice(farm_id, advice_date DESC);
CREATE INDEX idx_farm_memory_farm_id ON farm_memory(farm_id);

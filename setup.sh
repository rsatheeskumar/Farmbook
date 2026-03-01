#!/bin/bash
# ============================================================
# Kisan Saathi — Full Local Dev Setup Script
# Run this on YOUR LAPTOP (not Claude's sandbox)
# ============================================================

set -e  # Stop on any error

echo "🌾 Setting up Kisan Saathi..."
echo ""

# ── 1. Python virtual environment ──────────────────────────
echo "📦 Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# ── 2. Install all backend packages ────────────────────────
echo "📦 Installing Python packages..."
pip install --upgrade pip -q
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

echo "✅ Python packages installed"
echo ""

# ── 3. Create .env file ────────────────────────────────────
if [ ! -f ".env" ]; then
  echo "📝 Creating .env file..."
  cat > .env << 'EOF'
# Kisan Saathi - Environment Variables
# Fill in your API keys below

ANTHROPIC_API_KEY=sk-ant-REPLACE_ME
OPENAI_API_KEY=sk-REPLACE_ME
OPENWEATHER_API_KEY=REPLACE_ME

# These are fine as-is for local dev
BASE_URL=http://localhost:8000
STORAGE_DIR=/tmp/kisan_files
DATABASE_URL=sqlite+aiosqlite:///./kisansaathi.db
EOF
  echo "✅ .env created — ADD YOUR API KEYS before running the server!"
else
  echo "✅ .env already exists"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Setup complete! Next steps:"
echo ""
echo "1️⃣  Add your API keys to .env"
echo "     nano .env"
echo ""
echo "2️⃣  Start the backend server:"
echo "     source venv/bin/activate"
echo "     uvicorn backend.main:app --reload --port 8000"
echo ""
echo "3️⃣  Open ngrok in another terminal:"
echo "     ngrok http 8000"
echo ""
echo "4️⃣  Open the web test UI in your browser:"
echo "     http://localhost:8000/test"
echo ""
echo "5️⃣  On your phone, open the ngrok URL"
echo "     e.g. https://abc123.ngrok.io/test"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

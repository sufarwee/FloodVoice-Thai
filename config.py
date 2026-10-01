import os
import json
from pathlib import Path
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


BASE_DIR = Path(__file__).resolve().parent

# --- AI & Transcription Configuration ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
DEFAULT_AI_PROVIDER = os.getenv("DEFAULT_AI_PROVIDER", "gemini").strip().lower()

# Whisper Mode: "api" (OpenAI Whisper API) หรือ "local" (Mac / Local Faster-Whisper ฟรีในเครื่อง)
WHISPER_MODE = os.getenv("WHISPER_MODE", "api").strip().lower()
LOCAL_WHISPER_MODEL = os.getenv("LOCAL_WHISPER_MODEL", "base").strip().lower()


# --- Database & Storage ---
SUPABASE_URL = os.getenv("SUPABASE_URL", "").strip()
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "").strip()
USE_LOCAL_SQLITE = os.getenv("USE_LOCAL_SQLITE", "true").lower() in ("true", "1", "yes")
SQLITE_DB_PATH = BASE_DIR / "database" / "floodvoice.db"

# --- Exporters ---
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID", "").strip()
GOOGLE_SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE", "service_account.json").strip()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()
OBSIDIAN_EXPORT_DIR = Path(os.getenv("OBSIDIAN_EXPORT_DIR", "./obsidian_vault"))

# --- Scraping & Platform APIs ---
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "").strip()
APIFY_TOKEN = os.getenv("APIFY_TOKEN", "").strip()

# --- Load Keywords ---
KEYWORDS_FILE = BASE_DIR / "keywords.json"

def load_keywords_config() -> dict:
    if KEYWORDS_FILE.exists():
        try:
            with open(KEYWORDS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Failed to parse keywords.json ({e}), using default fallback.")
    return {
        "monitored_provinces": ["ปราจีนบุรี", "เชียงราย", "กรุงเทพมหานคร"],
        "search_keywords": ["น้ำท่วม", "ช่วยเหลือน้ำท่วม", "น้ำท่วมด่วน"],
        "target_facebook_pages": [],
        "water_level_indicators": {}
    }

KEYWORDS_CONFIG = load_keywords_config()

# ==============================================================================
# config.py — Adika Marketplace configuration
# ==============================================================================
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import logging

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("adika")

BOT_TOKEN = (
    os.environ.get("BOT_TOKEN")
    or os.environ.get("TELEGRAM_BOT_TOKEN")
    or ""
).strip()

GROQ_API_KEY = (os.environ.get("GROQ_API_KEY") or "").strip()
GROQ_MODEL = (os.environ.get("GROQ_MODEL") or os.environ.get("GROQ_MODEL_NAME") or "mixtral-8x7b-32768").strip()
GROQ_MODEL_NAME = GROQ_MODEL  # alias

GEMINI_API_KEY = (os.environ.get("GEMINI_API_KEY") or "").strip()
OPENROUTER_API_KEY = (os.environ.get("OPENROUTER_API_KEY") or "").strip()
OPENROUTER_MODEL = (os.environ.get("OPENROUTER_MODEL") or "google/gemini-2.0-flash-001").strip()
ADMIN_CHAT_ID = os.environ.get("ADMIN_CHAT_ID", "0")

if not GROQ_API_KEY and not GEMINI_API_KEY:
    logger.warning("Neither GROQ_API_KEY nor GEMINI_API_KEY is configured!")

# Primary: PostgreSQL / Supabase
DATABASE_URL = (
    os.environ.get("DATABASE_URL")
    or os.environ.get("SUPABASE_DB_URL")
    or os.environ.get("POSTGRES_URL")
    or os.environ.get("POSTGRES_CONNECTION_STRING")
    or ""
)
DATABASE_URL = str(DATABASE_URL).strip().strip('"').strip("'")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

RENDER_EXTERNAL_HOSTNAME = (os.environ.get("RENDER_EXTERNAL_HOSTNAME", "") or "").strip()
PORT = int(os.environ.get("PORT", "8080"))
DB_FILE = os.environ.get("DB_FILE", "adika_marketplace.db")

SUPABASE_URL = (os.environ.get("SUPABASE_URL") or "").strip().rstrip("/")
SUPABASE_KEY = (
    os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    or os.environ.get("SUPABASE_KEY")
    or os.environ.get("SUPABASE_ANON_KEY")
    or ""
).strip()
SUPABASE_BUCKET = os.environ.get("SUPABASE_BUCKET", "broker-documents")

DB_BACKEND = "unknown"

_raw_web = (os.environ.get("WEBAPP_URL") or "").strip().rstrip("/")
if RENDER_EXTERNAL_HOSTNAME:
    WEBAPP_URL = f"https://{RENDER_EXTERNAL_HOSTNAME}".rstrip("/")
elif _raw_web:
    if not _raw_web.startswith("http"):
        _raw_web = "https://" + _raw_web
    WEBAPP_URL = _raw_web.replace("http://", "https://").rstrip("/")
else:
    WEBAPP_URL = "http://127.0.0.1:8080"

try:
    ADMIN_CHAT_ID_INT = int(ADMIN_CHAT_ID) if ADMIN_CHAT_ID else 0
except ValueError:
    ADMIN_CHAT_ID_INT = 0

ADMIN_IDS = {ADMIN_CHAT_ID_INT} if ADMIN_CHAT_ID_INT else set()

TEXT_PAGE_SIZE = 4
VIEW_INCREMENT = 1
VIEW_BASELINE_MIN = 35
VIEW_BASELINE_MAX = 90
MAX_IMAGE_BYTES = 5 * 1024 * 1024

SUPPORT_ADMIN_URL = "https://t.me/AdikaSupport"
SUPPORT_ADMIN_HANDLE = "@AdikaSupport"

MAIN_KEYBOARD = [
   ["🔍 ለመግዛት / ለመከራየት", "📢 ለመሸጥ / ለማከራየት"],
   ["🛒 የገበያ ቦታ", "📋 የፈላጊዎች ጥያቄዎች"],
   ["👥 የደላሎች መድረክ", "✍️ የደላላ/አቅራቢ መመዝገቢያ"],
   ["⚙️ የማሳወቂያ ማስተካከያ", "📞 እገዛ / Support"],
   ["🏠 ዋና ገጽ"]
]
SUB_CITIES = [
   "ቦሌ", "የካ", "አራዳ", "ልደታ",
   "ቂርቆስ", "አዲስ ከተማ", "ንፋስ ስልክ ላፍቶ",
   "ኮልፌ ቀራኒዮ", "አቃቂ ቃሊቲ", "ጉሌሌ", "ላምበርት/የካ"
]
CAR_SUB_CATEGORIES = ["🚗 የቤት መኪና", "🚚 የሥራ መኪና", "🚜 ከባድ ተሽከርካሪ/ማሽን"]
HOUSE_TYPES = ["🏡 ቪላ", "🏢 አፓርታማ", "🏢 ኮንዶሚኒየም", "🏢 ሪል እስቴት", "🏞️ መሬት/ቦታ"]
PROPERTY_TYPES = ["🏠 መኖሪያ ቤት", "🏢 የሥራ ቦታ / ንግድ"]
FUEL_TYPES = ["⛽ ቤንዚን", "🛢️ ናፍጣ", "⚡ ኤሌክትሪክ", "🔋 ሀይብሪድ"]
TRANSMISSION_TYPES = ["🕹️ ማንዋል", "🤖 ኦቶማቲክ"]
CONDITIONS = ["🆕 አዲስ", "✅ ያገለገለ", "🔧 ጥገና የሚፈልግ"]
BROKER_CATEGORIES = ["🚗 መኪና", "🏠 ቤትና ቦታ", "📦 አጠቃላይ ደላላ"]
BROKER_REG_SUBCITIES = [
    "ቦሌ", "አራዳ", "ቂርቆስ", "ልደታ", "አዲስ ከተማ",
    "ጉሌሌ", "የካ", "ንፋስ ስልክ", "አቃቂ ቃሊቲ", "ኮልፌ ቀራኒዮ",
    "አዲስ አበባ (ሙሉ)",
]

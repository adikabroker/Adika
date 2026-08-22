# config.py — የተሻሻለ እና ጠንካራ ውቅር
import os
import logging

# dotenv በአስተማማኝ ሁኔታ ለማስገባት
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv ካልተገኘ, መደበኛ የስርዓተ አካባቢ ተለዋዋጮችን ይጠቀሙ
    print("⚠️ python-dotenv not installed. Using system environment variables only.")
    # load_dotenv ን ባዶ ተግባር አድርገን እንገልጻለን
    def load_dotenv():
        pass

# ----------------------------------------------------------------------------
# መሰረታዊ ሎግ (Logging) ውቅር
# ----------------------------------------------------------------------------
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("adika")

# ----------------------------------------------------------------------------
# API KEYS (ከ .env ወይም ከስርዓተ አካባቢ የሚመጡ)
# ----------------------------------------------------------------------------
BOT_TOKEN = os.getenv("BOT_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN") or ""
GROQ_API_KEY = os.getenv("GROQ_API_KEY") or ""
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or ""
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY") or ""

# የGroq ሞዴል ስም (ነባር: llama-3.3-70b-versatile)
GROQ_MODEL_NAME = os.getenv("GROQ_MODEL_NAME", "llama-3.3-70b-versatile")

# ----------------------------------------------------------------------------
# አስተዳዳሪ (Admin) ውቅር
# ----------------------------------------------------------------------------
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID", "0")
try:
    ADMIN_CHAT_ID_INT = int(ADMIN_CHAT_ID) if ADMIN_CHAT_ID else 0
except ValueError:
    ADMIN_CHAT_ID_INT = 0

ADMIN_IDS = {ADMIN_CHAT_ID_INT} if ADMIN_CHAT_ID_INT else set()

# ----------------------------------------------------------------------------
# የውሂብ ጎታ (Database) ውቅር
# ----------------------------------------------------------------------------
# PostgreSQL / Supabase
DATABASE_URL = (
    os.getenv("DATABASE_URL")
    or os.getenv("SUPABASE_DB_URL")
    or os.getenv("POSTGRES_URL")
    or os.getenv("POSTGRES_CONNECTION_STRING")
    or ""
)
DATABASE_URL = str(DATABASE_URL).strip().strip('"').strip("'")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# SQLite (እንደ መጠባበቂያ - fallback)
DB_FILE = os.getenv("DB_FILE", "adika_marketplace.db")

# የሩጫ ጊዜ (runtime) ባንዲራ — በmodels ይዘጋጃል
DB_BACKEND = "unknown"

# ----------------------------------------------------------------------------
# የSupabase ማከማቻ (Storage) — ለፎቶ ማስቀመጫ
# ----------------------------------------------------------------------------
SUPABASE_URL = (os.getenv("SUPABASE_URL") or "").strip().rstrip("/")
SUPABASE_KEY = (
    os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    or os.getenv("SUPABASE_KEY")
    or os.getenv("SUPABASE_ANON_KEY")
    or ""
).strip()
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET", "broker-documents")

# ----------------------------------------------------------------------------
# የWeb App URL ውቅር
# ----------------------------------------------------------------------------
RENDER_EXTERNAL_HOSTNAME = (os.getenv("RENDER_EXTERNAL_HOSTNAME", "") or "").strip()
PORT = int(os.getenv("PORT", "8080"))

_raw_web = (os.getenv("WEBAPP_URL") or "").strip().rstrip("/")
if RENDER_EXTERNAL_HOSTNAME:
    WEBAPP_URL = f"https://{RENDER_EXTERNAL_HOSTNAME}".rstrip("/")
elif _raw_web:
    if not _raw_web.startswith("http"):
        _raw_web = "https://" + _raw_web
    WEBAPP_URL = _raw_web.replace("http://", "https://").rstrip("/")
else:
    WEBAPP_URL = "http://127.0.0.1:8080"

# ----------------------------------------------------------------------------
# የስርዓት ማረጋገጫ (Validation) - አስፈላጊ ተለዋዋጮች
# ----------------------------------------------------------------------------
CRITICAL_MISSING = []
if not GROQ_API_KEY:
    logger.warning("GROQ_API_KEY አልተገኘም። አንዳንድ AI ተግባራት አይሰሩም።")
    CRITICAL_MISSING.append("GROQ_API_KEY")

if not BOT_TOKEN:
    logger.warning("BOT_TOKEN (TELEGRAM_BOT_TOKEN) አልተገኘም። የቴሌግራም ቦት አይሰራም።")
    CRITICAL_MISSING.append("BOT_TOKEN")

if not DATABASE_URL:
    logger.warning("DATABASE_URL አልተገኘም። ነባር SQLite (adika_marketplace.db) ይጠቀማል።")

# ----------------------------------------------------------------------------
# ማሳወቂያ (Notifications) እና ድጋፍ
# ----------------------------------------------------------------------------
SUPPORT_ADMIN_URL = "https://t.me/AdikaSupport"
SUPPORT_ADMIN_HANDLE = "@AdikaSupport"

# ----------------------------------------------------------------------------
# የመጠን ገደቦች (Limits)
# ----------------------------------------------------------------------------
TEXT_PAGE_SIZE = 4
VIEW_INCREMENT = 1
VIEW_BASELINE_MIN = 35
VIEW_BASELINE_MAX = 90
MAX_IMAGE_BYTES = 5 * 1024 * 1024  # 5MB

# ----------------------------------------------------------------------------
# የቴሌግራም ቁልፍ ሰሌዳ (Keyboard) እና ምድቦች
# ----------------------------------------------------------------------------
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
CONDITIONS = ["🆕 አዲስ", "✅ ያገለገለ", "🔧 ጥገና የሚፍልግ"]

BROKER_CATEGORIES = ["🚗 መኪና", "🏠 ቤትና ቦታ", "📦 አጠቃላይ ደላላ"]
BROKER_REG_SUBCITIES = [
    "ቦሌ", "አራዳ", "ቂርቆስ", "ልደታ", "አዲስ ከተማ",
    "ጉሌሌ", "የካ", "ንፋስ ስልክ", "አቃቂ ቃሊቲ", "ኮልፌ ቀራኒዮ",
    "አዲስ አበባ (ሙሉ)",
]

# ----------------------------------------------------------------------------
# የስህተት ማጠቃለያ (Error Summary)
# ----------------------------------------------------------------------------
if CRITICAL_MISSING:
    logger.error(f"⚠️ CRITICAL: የሚከተሉት ተለዋዋጮች ጎድለዋል: {', '.join(CRITICAL_MISSING)}")
    logger.error("📌 እባክዎን .env ፋይልዎን ያረጋግጡ ወይም እነዚህን ተለዋዋጮች በስርዓተ አካባቢ (environment) ያዘጋጁ።")
    logger.error("💡 አፕሊኬሽኑ በከፊል ይሰራል, ነገር ግን አንዳንድ ተግባራት አይሰሩም።")

import logging
logger = logging.getLogger(__name__)
"""
adika_features.py — Broker match, Telegram OTP, For-You feed
Shared by Flask api_service routes.
"""
from __future__ import annotations

import hashlib
import json
import random
import re
import time
from typing import Any, Dict, List, Optional, Tuple

try:
    import requests
except Exception:
    requests = None  # type: ignore

from config import logger

# In-memory OTP store (production: Redis preferred; survives single-instance Render)
_OTP_STORE: Dict[str, Dict[str, Any]] = {}
_OTP_TTL_SEC = 600


def _ph():
    from models import get_placeholder
    return get_placeholder()


def ensure_feature_tables():
    """Create otp_codes + user_preferences if missing (PG + SQLite)."""
    from models import get_db_connection, is_postgres
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        if is_postgres():
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS user_preferences (
                    user_id BIGINT PRIMARY KEY,
                    categories JSONB DEFAULT '[]',
                    budget_min BIGINT DEFAULT 0,
                    budget_max BIGINT DEFAULT 999999999,
                    onboarding_done BOOLEAN DEFAULT FALSE,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS otp_codes (
                    id SERIAL PRIMARY KEY,
                    telegram_id BIGINT NOT NULL,
                    code_hash TEXT NOT NULL,
                    purpose TEXT DEFAULT 'verify',
                    expires_at TIMESTAMP NOT NULL,
                    used BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """
            )
            # Extend brokers if needed
            for stmt in (
                "ALTER TABLE brokers ADD COLUMN IF NOT EXISTS categories JSONB DEFAULT '[]'",
                "ALTER TABLE brokers ADD COLUMN IF NOT EXISTS verified_status TEXT DEFAULT 'pending'",
                "ALTER TABLE brokers ADD COLUMN IF NOT EXISTS telegram_username TEXT",
            ):
                try:
                    cur.execute(stmt)
                except Exception:
                    pass
        else:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS user_preferences (
                    user_id INTEGER PRIMARY KEY,
                    categories TEXT DEFAULT '[]',
                    budget_min INTEGER DEFAULT 0,
                    budget_max INTEGER DEFAULT 999999999,
                    onboarding_done INTEGER DEFAULT 0,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS otp_codes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    telegram_id INTEGER NOT NULL,
                    code_hash TEXT NOT NULL,
                    purpose TEXT DEFAULT 'verify',
                    expires_at TEXT NOT NULL,
                    used INTEGER DEFAULT 0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            try:
                cur.execute("ALTER TABLE brokers ADD COLUMN categories TEXT DEFAULT '[]'")
            except Exception:
                pass
            try:
                cur.execute("ALTER TABLE brokers ADD COLUMN verified_status TEXT DEFAULT 'pending'")
            except Exception:
                pass
            try:
                cur.execute("ALTER TABLE brokers ADD COLUMN telegram_username TEXT")
            except Exception:
                pass
            conn.commit()
    except Exception as e:
        logger.error("ensure_feature_tables: %s", e)
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass


def register_broker(
    telegram_id: int,
    name: str,
    phone: str,
    categories: List[str],
    username: str = "",
) -> Tuple[bool, str]:
    """
    Upsert broker against production Supabase schema variants:
    - chat_id / user_chat_id / telegram_id (NOT NULL variants)
    No ON CONFLICT required.
    """
    from models import get_db_connection, is_postgres
    ensure_feature_tables()
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        ph = _ph()
        tid = int(telegram_id) if telegram_id else 0
        if tid <= 0:
            # Derive stable id from phone digits so NOT NULL columns never get null
            digits = "".join(ch for ch in str(phone or "") if ch.isdigit()) or "1"
            tid = int(digits[-9:]) if len(digits) >= 3 else 100000001
        full_name = (name or "Broker")[:120]
        phone_s = (phone or "")[:40]
        user_s = (username or "").lstrip("@")[:64]
        cats = json.dumps(categories or ["መኪና"], ensure_ascii=False)

        # Discover columns
        cols = set()
        try:
            if is_postgres():
                cur.execute(
                    """
                    SELECT column_name FROM information_schema.columns
                    WHERE table_schema='public' AND table_name='brokers'
                    """
                )
                for r in cur.fetchall() or []:
                    cols.add((r["column_name"] if isinstance(r, dict) else r[0]).lower())
            else:
                cur.execute("PRAGMA table_info(brokers)")
                for r in cur.fetchall() or []:
                    if isinstance(r, dict):
                        cols.add(str(r.get("name", "")).lower())
                    else:
                        cols.add(str(r[1]).lower())
        except Exception as ce:
            logger.warning("broker cols: %s", ce)
            cols = {"id", "chat_id", "full_name", "phone", "status"}

        def has(*names):
            return any(n in cols for n in names)

        # Find existing
        existing_id = None
        for col, val in (("chat_id", tid), ("user_chat_id", tid), ("telegram_id", tid), ("phone", phone_s)):
            if col not in cols or not val:
                continue
            try:
                cur.execute(f"SELECT id FROM brokers WHERE {col} = {ph} LIMIT 1", (val,))
                row = cur.fetchone()
                if row:
                    existing_id = row["id"] if isinstance(row, dict) else row[0]
                    break
            except Exception:
                continue

        # Build field map for available columns
        fields = {}
        if "chat_id" in cols:
            fields["chat_id"] = tid
        if "user_chat_id" in cols:
            fields["user_chat_id"] = tid
        if "telegram_id" in cols:
            fields["telegram_id"] = tid
        if "full_name" in cols:
            fields["full_name"] = full_name
        if "name" in cols and "full_name" not in cols:
            fields["name"] = full_name
        if "phone" in cols:
            fields["phone"] = phone_s
        if "role_type" in cols:
            fields["role_type"] = "broker"
        if "sub_city" in cols:
            fields["sub_city"] = "አዲስ አበባ"
        if "status" in cols:
            fields["status"] = "active"
        if "verified_status" in cols:
            fields["verified_status"] = "verified"
        if "telegram_username" in cols:
            fields["telegram_username"] = user_s
        if "username" in cols:
            fields["username"] = user_s
        if "categories" in cols:
            fields["categories"] = cats

        if existing_id is not None:
            sets = []
            vals = []
            for k, v in fields.items():
                if k == "categories" and is_postgres():
                    sets.append(f"{k} = {ph}::jsonb")
                else:
                    sets.append(f"{k} = {ph}")
                vals.append(v)
            vals.append(existing_id)
            sql = f"UPDATE brokers SET {', '.join(sets)} WHERE id = {ph}"
            cur.execute(sql, tuple(vals))
            if not is_postgres():
                conn.commit()
            return True, str(existing_id)

        # INSERT — never leave NOT NULL id columns null
        if not fields.get("chat_id") and "chat_id" in cols:
            fields["chat_id"] = tid
        if not fields.get("user_chat_id") and "user_chat_id" in cols:
            fields["user_chat_id"] = tid

        col_names = list(fields.keys())
        placeholders = []
        vals = []
        for k in col_names:
            if k == "categories" and is_postgres():
                placeholders.append(f"{ph}::jsonb")
            else:
                placeholders.append(ph)
            vals.append(fields[k])
        sql = f"INSERT INTO brokers ({', '.join(col_names)}) VALUES ({', '.join(placeholders)})"
        if is_postgres():
            sql += " RETURNING id"
            cur.execute(sql, tuple(vals))
            row = cur.fetchone()
            rid = row["id"] if isinstance(row, dict) else (row[0] if row else 0)
        else:
            cur.execute(sql, tuple(vals))
            conn.commit()
            rid = cur.lastrowid
        return True, str(rid)
    except Exception as e:
        logger.error("register_broker: %s", e, exc_info=True)
        return False, str(e)
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass



def _cat_match(broker_cats: Any, category: str) -> bool:
    cat = (category or "").strip()
    if not cat:
        return True
    aliases = {
        "መኪና": ["መኪና", "car", "cars", "vehicle"],
        "ቤት": ["ቤት", "house", "property", "home"],
        "ንግድ": ["ንግድ", "commercial", "business"],
    }
    pool = [cat.lower()]
    for k, vals in aliases.items():
        if cat == k or cat.lower() in vals:
            pool = [x.lower() for x in vals] + [k.lower()]
            break
    raw = broker_cats
    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except Exception:
            raw = [raw]
    if isinstance(raw, dict):
        # notification_prefs style
        if raw.get("car") and any(x in pool for x in ["መኪና", "car", "cars"]):
            return True
        if raw.get("house") and any(x in pool for x in ["ቤት", "house", "property"]):
            return True
        return bool(raw.get("enabled", True))
    if not raw:
        return True
    return any(str(x).lower() in pool or str(x) in category for x in (raw or []))


def list_matching_brokers(category: str, limit: int = 40) -> List[Dict[str, Any]]:
    from models import get_db_connection, is_postgres
    ensure_feature_tables()
    conn = None
    out: List[Dict[str, Any]] = []
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT * FROM brokers
            WHERE COALESCE(status,'active') NOT IN ('banned','rejected')
            ORDER BY id DESC
            LIMIT 200
            """
        )
        rows = cur.fetchall() or []
        for r in rows:
            d = dict(r) if not isinstance(r, dict) else r
            cats = d.get("categories") or d.get("notification_prefs") or []
            if _cat_match(cats, category):
                out.append(d)
            if len(out) >= limit:
                break
    except Exception as e:
        logger.error("list_matching_brokers: %s", e)
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass
    return out


def format_buyer_match_message(
    category: str,
    budget_min: Any,
    budget_max: Any,
    details: str,
    phone: str,
    username: str = "",
    req_id: Any = None,
) -> str:
    un = (username or "").lstrip("@")
    return (
        "🚨 አዲስ የፈላጊ ፍላጎት ደርሷል!\n"
        "─────────────────\n"
        f"📦 ምድብ: {category or '—'}\n"
        f"💰 በጀት: {budget_min or '—'} - {budget_max or '—'} ETB\n"
        f"📝 ዝርዝር: {(details or '—')[:400]}\n"
        f"📞 ስልክ: {phone or '—'}\n"
        f"📱 Telegram: @{un or '—'}\n"
        + (f"🆔 #ADK-{req_id}\n" if req_id else "")
    )


def notify_brokers_buyer_request(
    bot,
    category: str,
    budget_min: Any,
    budget_max: Any,
    details: str,
    phone: str,
    username: str = "",
    req_id: Any = None,
    buyer_chat_id: int = 0,
) -> int:
    """Send Telegram DMs to matching brokers. Returns count sent."""
    if not bot:
        return 0
    msg = format_buyer_match_message(
        category, budget_min, budget_max, details, phone, username, req_id
    )
    brokers = list_matching_brokers(category)
    sent = 0
    for b in brokers:
        chat_id = b.get("chat_id") or b.get("telegram_id")
        if not chat_id:
            continue
        try:
            if int(chat_id) == int(buyer_chat_id or 0):
                continue
        except Exception:
            pass
        try:
            # sync API used by some bots
            if hasattr(bot, "send_message"):
                import asyncio
                res = bot.send_message(chat_id=int(chat_id), text=msg)
                if asyncio.iscoroutine(res):
                    # caller should use async path
                    pass
                sent += 1
        except Exception as e:
            logger.warning("broker notify %s: %s", chat_id, e)
    return sent


def _hash_otp(code: str) -> str:
    return hashlib.sha256(code.encode("utf-8")).hexdigest()


def create_telegram_otp(telegram_id: int, purpose: str = "verify") -> str:
    code = f"{random.randint(100000, 999999)}"
    key = f"{telegram_id}:{purpose}"
    _OTP_STORE[key] = {
        "hash": _hash_otp(code),
        "exp": time.time() + _OTP_TTL_SEC,
        "used": False,
    }
    # persist best-effort
    from models import get_db_connection, is_postgres
    ensure_feature_tables()
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        p = _ph()
        if is_postgres():
            cur.execute(
                f"INSERT INTO otp_codes (telegram_id, code_hash, purpose, expires_at) "
                f"VALUES ({p},{p},{p}, NOW() + INTERVAL '10 minutes')",
                (int(telegram_id), _hash_otp(code), purpose),
            )
        else:
            cur.execute(
                f"INSERT INTO otp_codes (telegram_id, code_hash, purpose, expires_at) "
                f"VALUES ({p},{p},{p}, datetime('now','+10 minutes'))",
                (int(telegram_id), _hash_otp(code), purpose),
            )
            conn.commit()
    except Exception as e:
        logger.warning("otp persist: %s", e)
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass
    return code


def verify_telegram_otp(telegram_id: int, code: str, purpose: str = "verify") -> bool:
    key = f"{telegram_id}:{purpose}"
    entry = _OTP_STORE.get(key)
    if entry and not entry.get("used") and entry.get("exp", 0) >= time.time():
        if entry["hash"] == _hash_otp(str(code).strip()):
            entry["used"] = True
            return True
    # DB fallback
    from models import get_db_connection, is_postgres
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        p = _ph()
        h = _hash_otp(str(code).strip())
        if is_postgres():
            cur.execute(
                f"""
                SELECT id FROM otp_codes
                WHERE telegram_id={p} AND purpose={p} AND code_hash={p}
                  AND used=FALSE AND expires_at > NOW()
                ORDER BY id DESC LIMIT 1
                """,
                (int(telegram_id), purpose, h),
            )
        else:
            cur.execute(
                f"""
                SELECT id FROM otp_codes
                WHERE telegram_id={p} AND purpose={p} AND code_hash={p}
                  AND used=0 AND expires_at > datetime('now')
                ORDER BY id DESC LIMIT 1
                """,
                (int(telegram_id), purpose, h),
            )
        row = cur.fetchone()
        if not row:
            return False
        oid = row["id"] if isinstance(row, dict) else row[0]
        if is_postgres():
            cur.execute(f"UPDATE otp_codes SET used=TRUE WHERE id={p}", (oid,))
        else:
            cur.execute(f"UPDATE otp_codes SET used=1 WHERE id={p}", (oid,))
            conn.commit()
        return True
    except Exception as e:
        logger.warning("otp verify: %s", e)
        return False
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass


def save_user_preferences(
    user_id: int,
    categories: List[str] = None,
    budget_min: int = 0,
    budget_max: int = 999_999_999,
    budget: str = "",
    budget_range: str = "",
    min_price: int = None,
    max_price: int = None,
    **kwargs,
) -> bool:
    """
    Upsert user_preferences with CLEAN INTEGER bounds.
    Accepts either numeric min/max or a text range like "ከ 1.5M - 4 ሚሊዮን ETB".
    Stores: budget_min, budget_max (and min_price/max_price aliases when columns exist).
    """
    from models import get_db_connection, is_postgres
    ensure_feature_tables()

    # Prefer explicit integer args
    bmin = int(budget_min or 0)
    bmax = int(budget_max or 0) if budget_max not in (None, "") else 0
    if min_price is not None:
        try:
            bmin = int(min_price)
        except Exception:
            pass
    if max_price is not None:
        try:
            bmax = int(max_price)
        except Exception:
            pass

    # Parse text budget when integers missing / default
    raw = budget or budget_range or kwargs.get("budget_text") or ""
    if raw and (bmax <= 0 or bmax >= 999_999_999):
        parsed = parse_budget_range(raw)
        if parsed.get("minPrice"):
            bmin = int(parsed["minPrice"])
        if parsed.get("maxPrice"):
            bmax = int(parsed["maxPrice"])

    if bmax <= 0:
        bmax = 999_999_999
    bmin = max(0, int(bmin))
    bmax = max(0, int(bmax))

    cats = categories or kwargs.get("categories") or []
    if isinstance(cats, str):
        cats = [c.strip() for c in cats.split(",") if c.strip()]

    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        p = _ph()
        cats_json = json.dumps(cats or [], ensure_ascii=False)
        if is_postgres():
            # Core columns
            cur.execute(
                f"""
                INSERT INTO user_preferences (user_id, categories, budget_min, budget_max, onboarding_done, updated_at)
                VALUES ({p},{p}::jsonb,{p},{p}, TRUE, NOW())
                ON CONFLICT (user_id) DO UPDATE SET
                  categories=EXCLUDED.categories,
                  budget_min=EXCLUDED.budget_min,
                  budget_max=EXCLUDED.budget_max,
                  onboarding_done=TRUE,
                  updated_at=NOW()
                """,
                (int(user_id), cats_json, bmin, bmax),
            )
            # Optional alias columns min_price / max_price / budget text
            for col, val in (
                ("min_price", bmin),
                ("max_price", bmax),
                ("budget", str(raw or "")[:120]),
                ("budget_range", str(raw or "")[:120]),
            ):
                try:
                    cur.execute(
                        f"""
                        UPDATE user_preferences SET {col} = {p}
                        WHERE user_id = {p}
                        """,
                        (val, int(user_id)),
                    )
                except Exception:
                    pass
            try:
                conn.commit()
            except Exception:
                pass
        else:
            cur.execute(
                f"""
                INSERT OR REPLACE INTO user_preferences (user_id, categories, budget_min, budget_max, onboarding_done)
                VALUES ({p},{p},{p},{p},1)
                """,
                (int(user_id), cats_json, bmin, bmax),
            )
            conn.commit()
            for col, val in (("min_price", bmin), ("max_price", bmax)):
                try:
                    cur.execute(
                        f"UPDATE user_preferences SET {col} = {p} WHERE user_id = {p}",
                        (val, int(user_id)),
                    )
                    conn.commit()
                except Exception:
                    pass
        logger.info(
            "save_user_preferences uid=%s cats=%s min=%s max=%s",
            user_id, cats, bmin, bmax,
        )
        return True
    except Exception as e:
        logger.error("save_user_preferences: %s", e)
        return False
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass


def get_user_preferences(user_id: int) -> Dict[str, Any]:
    from models import get_db_connection, is_postgres
    ensure_feature_tables()
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        p = _ph()
        cur.execute(f"SELECT * FROM user_preferences WHERE user_id={p}", (int(user_id),))
        row = cur.fetchone()
        if not row:
            return {
                "categories": [],
                "budget_min": 0,
                "budget_max": 999999999,
                "min_price": 0,
                "max_price": 999999999,
                "onboarding_done": False,
            }
        d = dict(row)
        cats = d.get("categories") or []
        if isinstance(cats, str):
            try:
                cats = json.loads(cats)
            except Exception:
                cats = []
        bmin = int(d.get("budget_min") or d.get("min_price") or 0)
        bmax = int(d.get("budget_max") or d.get("max_price") or 999999999)
        # If only text budget stored, parse once
        if (bmax <= 0 or bmax >= 999999999) and (d.get("budget") or d.get("budget_range")):
            parsed = parse_budget_range(d.get("budget") or d.get("budget_range"))
            if parsed.get("minPrice"):
                bmin = int(parsed["minPrice"])
            if parsed.get("maxPrice"):
                bmax = int(parsed["maxPrice"])
        return {
            "categories": cats,
            "budget_min": bmin,
            "budget_max": bmax,
            "min_price": bmin,
            "max_price": bmax,
            "budget": d.get("budget") or d.get("budget_range") or "",
            "budget_range": d.get("budget_range") or d.get("budget") or "",
            "onboarding_done": bool(d.get("onboarding_done")),
        }
    except Exception as e:
        logger.warning("get_user_preferences: %s", e)
        return {
            "categories": [],
            "budget_min": 0,
            "budget_max": 999999999,
            "min_price": 0,
            "max_price": 999999999,
            "onboarding_done": False,
        }
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass


def _parse_price(val: Any) -> float:
    """
    Parse ETB prices from numbers or Amharic/English strings.
    Supports: 4500000 | 4.5M | 4.5 ሚሊዮን | 2.5M - 3.5M (returns max of range).
    """
    if val is None:
        return 0.0
    if isinstance(val, (int, float)):
        return float(val) if abs(float(val)) < 1e15 else 0.0
    s = str(val).strip()
    if not s:
        return 0.0

    def _token(raw: str) -> float:
        raw = raw.strip().replace(",", "")
        m = re.match(
            r"^([\d.]+)\s*(m|million|ሚሊዮን|ሚሊ|ሚ|k|thousand|ሺህ|ሺ)?$",
            raw,
            re.I,
        )
        if not m:
            digits = re.sub(r"[^\d.]", "", raw)
            try:
                return float(digits) if digits else 0.0
            except Exception:
                return 0.0
        n = float(m.group(1))
        unit = (m.group(2) or "").lower()
        if unit in ("m", "million") or "ሚ" in unit:
            return n * 1_000_000
        if unit in ("k", "thousand") or "ሺ" in unit:
            return n * 1_000
        # bare number next to ሚሊ in surrounding text handled by caller
        if n > 0 and n < 1000 and re.search(r"ሚሊ|million|\bM\b", s, re.I):
            return n * 1_000_000
        return n

    # Range: take MAX so budget filters "under X" still work when listing shows a band
    range_m = re.search(
        r"([\d.,]+\s*(?:m|M|million|ሚሊዮን|ሚሊ|ሚ|k|K|ሺህ|ሺ)?)\s*[-–—to]+\s*([\d.,]+\s*(?:m|M|million|ሚሊዮን|ሚሊ|ሚ|k|K|ሺህ|ሺ)?)",
        s,
        re.I,
    )
    if range_m:
        a = _token(range_m.group(1))
        b = _token(range_m.group(2))
        return max(a, b)

    # Single token with unit somewhere in string
    single = re.search(
        r"([\d.,]+)\s*(m|M|million|ሚሊዮን|ሚሊ|ሚ|k|K|ሺህ|ሺ)",
        s,
        re.I,
    )
    if single:
        return _token(single.group(1) + " " + single.group(2))

    return _token(s)


def score_listing_for_user(item: Dict[str, Any], prefs: Dict[str, Any]) -> int:
    score = 0
    cats = prefs.get("categories") or []
    main = str(item.get("main_category") or item.get("category") or "")
    for c in cats:
        if not c:
            continue
        if c in main or main in str(c):
            score += 10
            break
        aliases = {
            "መኪና": ["car", "መኪና"],
            "ቤት": ["ቤት", "house", "property"],
            "ንግድ": ["ንግድ", "commercial"],
        }
        for k, vals in aliases.items():
            if c == k or c.lower() in vals:
                if any(v in main.lower() for v in vals) or k in main:
                    score += 10
                    break
    price = _parse_price(item.get("price"))
    bmin = float(prefs.get("budget_min") or 0)
    bmax = float(prefs.get("budget_max") or 999999999)
    if price > 0 and bmin <= price <= bmax:
        score += 5
    # slight boost for newer / more views
    try:
        score += min(5, int(item.get("view_count") or 0) // 50)
    except Exception:
        pass
    return score



def extract_search_intent(query: str, use_llm: bool = True) -> Dict[str, Any]:
    """
    Parse free-text (Amharic/English) search into structured intent JSON.
    Falls back to rule-based extraction when LLM is unavailable.
    Keys: category, brand, model, price_max, price_min, transmission, fuel, keywords
    """
    q = (query or "").strip()
    intent: Dict[str, Any] = {
        "category": "",
        "brand": "",
        "model": "",
        "price_max": 0,
        "price_min": 0,
        "transmission": "",
        "fuel": "",
        "keywords": [],
        "raw": q,
    }
    if not q:
        return intent

    low = q.lower()

    # Category
    if any(x in low for x in ("መኪና", "car", "vehicle", "auto", "toyota", "suzuki", "prado", "dzire", "byd")):
        intent["category"] = "መኪና"
    elif any(x in low for x in ("ቤት", "house", "home", "villa", "apartment", "condo", "property")):
        intent["category"] = "ቤት"

    # Brands common in Ethiopia market
    brands = [
        "toyota", "suzuki", "hyundai", "kia", "nissan", "honda", "byd", "geely",
        "haval", "changan", "volkswagen", "bmw", "mercedes", "audi", "tesla",
        "mitsubishi", "isuzu", "mazda", "ford", "chevrolet", "jetour", "land cruiser", "prado",
    ]
    for b in brands:
        if b in low:
            intent["brand"] = b.title() if b != "byd" else "BYD"
            if b in ("land cruiser", "prado"):
                intent["brand"] = "Toyota"
                intent["model"] = "Land Cruiser Prado" if "prado" in low or "land" in low else intent["model"]
            break

    # Model hints
    models = [
        "corolla", "vitz", "yaris", "rav4", "hilux", "prado", "land cruiser",
        "dzire", "swift", "jimny", "tucson", "creta", "elantra", "sportage",
        "seagull", "song plus", "yuan plus", "coolray", "h6", "tracker", "id.4",
        "patrol", "civic", "model y",
    ]
    for m in models:
        if m in low:
            intent["model"] = m.title() if m not in ("id.4", "song plus", "yuan plus", "model y") else m.title().replace("Id.4", "ID.4")
            break

    # Transmission / fuel
    if any(x in low for x in ("አውቶ", "auto", "automatic", "cvt", "dct")):
        intent["transmission"] = "automatic"
    elif any(x in low for x in ("ማንዋል", "manual")):
        intent["transmission"] = "manual"
    if any(x in low for x in ("ናፍጣ", "diesel")):
        intent["fuel"] = "diesel"
    elif any(x in low for x in ("ቤንዚን", "benzine", "petrol", "gasoline")):
        intent["fuel"] = "benzine"
    elif any(x in low for x in ("ኤሌክትሪክ", "electric", "ev", "hybrid")):
        intent["fuel"] = "electric"

    # Price: 4M, 1.5 ሚሊዮን, under 3 million, እስከ 4000000
    def _tok_to_num(raw: str, unit: str = "") -> int:
        try:
            n = float(str(raw).replace(",", ""))
        except Exception:
            return 0
        u = (unit or "").lower()
        if any(x in u for x in ("m", "ሚ", "mil", "million")) or (n < 1000 and any(x in low for x in ("ሚሊ", "million", "m "))):
            return int(n * 1_000_000)
        if any(x in u for x in ("k", "ሺ")):
            return int(n * 1_000)
        if n < 1000 and ("ሚሊ" in low or "million" in low):
            return int(n * 1_000_000)
        return int(n)

    m_range = re.search(
        r"([\d.,]+)\s*(m|M|k|K|ሚ|ሚሊ|ሚሊዮን|million|ሺ|ሺህ)?\s*[-–—to]+\s*([\d.,]+)\s*(m|M|k|K|ሚ|ሚሊ|ሚሊዮን|million|ሺ|ሺህ)?",
        q,
        re.I,
    )
    if m_range:
        intent["price_min"] = _tok_to_num(m_range.group(1), m_range.group(2) or m_range.group(4) or "")
        intent["price_max"] = _tok_to_num(m_range.group(3), m_range.group(4) or m_range.group(2) or "")
    else:
        m_max = re.search(
            r"(?:እስከ|under|below|max|<=|≤|በጀት)?\s*([\d.,]+)\s*(m|M|k|K|ሚ|ሚሊ|ሚሊዮን|million|ሺ|ሺህ)?",
            q,
            re.I,
        )
        if m_max:
            intent["price_max"] = _tok_to_num(m_max.group(1), m_max.group(2) or "")

    intent["keywords"] = [w for w in re.split(r"\s+", q) if len(w) > 1][:12]

    # Optional LLM enrichment
    if use_llm and q:
        try:
            intent = _llm_enrich_intent(q, intent)
        except Exception as e:
            logger.debug("extract_search_intent LLM skip: %s", e)
    return intent


def _llm_enrich_intent(query: str, base: Dict[str, Any]) -> Dict[str, Any]:
    """Best-effort OpenRouter/Gemini JSON extraction; never raises to caller."""
    import os
    prompt = (
        "Extract vehicle/property search intent as strict JSON with keys: "
        "category (መኪና or ቤት or empty), brand, model, price_max (number ETB), "
        "price_min (number), transmission (automatic|manual|), fuel (benzine|diesel|electric|). "
        f"Query: {query}\nReturn ONLY JSON."
    )
    text = ""
    # OpenRouter
    key = os.environ.get("OPENROUTER_API_KEY") or ""
    if key and requests is not None:
        try:
            import requests as _req
            r = _req.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": os.environ.get("OPENROUTER_MODEL") or "deepseek/deepseek-chat",
                    "messages": [
                        {"role": "system", "content": "You extract structured search intent. Reply JSON only."},
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": 0.1,
                },
                timeout=12,
            )
            if r.ok:
                data = r.json()
                text = (((data.get("choices") or [{}])[0].get("message") or {}).get("content") or "").strip()
        except Exception as e:
            logger.debug("openrouter intent: %s", e)
    if not text:
        return base
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        parsed = json.loads(text)
    except Exception:
        return base
    if not isinstance(parsed, dict):
        return base
    out = dict(base)
    for k in ("category", "brand", "model", "transmission", "fuel"):
        if parsed.get(k):
            out[k] = str(parsed[k]).strip()
    for k in ("price_max", "price_min"):
        try:
            v = parsed.get(k)
            if v is not None and str(v).strip() != "":
                out[k] = int(float(re.sub(r"[^\d.]", "", str(v)) or 0))
        except Exception:
            pass
    return out


# requests may be missing in pure feature module
try:
    import requests  # type: ignore  # noqa: F401
except Exception:
    requests = None  # type: ignore


def _listing_matches_intent(item: Dict[str, Any], intent: Dict[str, Any]) -> bool:
    if not intent:
        return True
    blob = " ".join(
        str(item.get(k) or "")
        for k in (
            "main_category", "category", "sub_category", "description",
            "brand", "model", "full_model", "name", "title", "extra_data",
        )
    ).lower()
    cat = (intent.get("category") or "").strip()
    if cat == "መኪና" and not any(x in blob for x in ("መኪና", "car", "vehicle", "toyota", "suzuki", "byd", "auto")):
        # still allow if brand/model set
        if not (intent.get("brand") or intent.get("model")):
            return False
    if cat == "ቤት" and not any(x in blob for x in ("ቤት", "house", "home", "villa", "apartment", "property")):
        return False
    brand = (intent.get("brand") or "").lower()
    if brand and brand not in blob:
        return False
    model = (intent.get("model") or "").lower()
    if model and model not in blob:
        return False
    price = _parse_price(item.get("price") or item.get("current_price_range_etb"))
    pmax = float(intent.get("price_max") or 0)
    pmin = float(intent.get("price_min") or 0)
    if pmax > 0 and price > 0 and price > pmax:
        return False
    if pmin > 0 and price > 0 and price < pmin:
        return False
    trans = (intent.get("transmission") or "").lower()
    if trans:
        tblob = str(item.get("transmission") or item.get("extra_data") or "").lower()
        if tblob and trans[:4] not in tblob and ("auto" in trans and "auto" not in tblob and "አውቶ" not in tblob):
            # soft: don't hard-exclude catalog rows missing transmission
            if item.get("source") == "listing" and tblob:
                return False
    return True


def search_listings_by_intent(intent: Dict[str, Any], limit: int = 40) -> List[Dict[str, Any]]:
    """Query marketplace `listings` table with intent filters."""
    from models import get_db_connection, is_postgres
    conn = None
    out: List[Dict[str, Any]] = []
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT * FROM listings
            WHERE (status IS NULL OR LOWER(CAST(status AS TEXT)) NOT IN ('deleted','sold','rented','expired'))
              AND (UPPER(TRIM(COALESCE(req_type,''))) NOT IN ('BUY','RENT')
                   OR COALESCE(req_type,'') = '')
            ORDER BY id DESC
            LIMIT 250
            """
        )
        for r in cur.fetchall() or []:
            d = _normalize_listing_row(dict(r), source="listing")
            if _listing_matches_intent(d, intent):
                d["_score"] = score_listing_for_user(d, {
                    "categories": [intent.get("category")] if intent.get("category") else [],
                    "budget_min": intent.get("price_min") or 0,
                    "budget_max": intent.get("price_max") or 999999999,
                })
                out.append(d)
            if len(out) >= limit * 3:
                break
        out.sort(key=lambda x: (-int(x.get("_score") or 0), -(x.get("id") or 0)))
        return out[:limit]
    except Exception as e:
        logger.error("search_listings_by_intent: %s", e, exc_info=True)
        return []
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass


def search_ethiopia_vehicles_by_intent(intent: Dict[str, Any], limit: int = 40) -> List[Dict[str, Any]]:
    """Query Adika Clean Market catalog `ethiopia_vehicles`."""
    from models import get_db_connection
    conn = None
    out: List[Dict[str, Any]] = []
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        p = _ph()
        brand = (intent.get("brand") or "").strip()
        model = (intent.get("model") or "").strip()
        keywords = intent.get("keywords") or []
        # Broad fetch then filter — table is small catalog
        try:
            cur.execute("SELECT * FROM ethiopia_vehicles ORDER BY id DESC LIMIT 400")
        except Exception:
            return []
        for r in cur.fetchall() or []:
            d = dict(r)
            d = _normalize_listing_row(d, source="clean_market")
            # Map catalog fields into listing-like shape for UI
            d["id"] = d.get("id")
            d["main_category"] = d.get("category") or "መኪና"
            d["category"] = d.get("category") or "መኪና"
            d["description"] = d.get("core_advantage") or d.get("primary_use_case") or ""
            d["price"] = d.get("current_price_range_etb") or ""
            d["title"] = d.get("name") or d.get("full_model") or d.get("model_key") or "Adika Clean Market"
            d["is_clean_market"] = True
            if _listing_matches_intent(d, intent) or _vehicle_soft_match(d, brand, model, keywords):
                score = 0
                blob = " ".join(str(d.get(k) or "") for k in ("name", "full_model", "brand", "model_key", "category")).lower()
                if brand and brand.lower() in blob:
                    score += 12
                if model and model.lower() in blob:
                    score += 14
                if intent.get("category") == "መኪና":
                    score += 4
                d["_score"] = score
                out.append(d)
        out.sort(key=lambda x: (-int(x.get("_score") or 0), str(x.get("name") or "")))
        return out[:limit]
    except Exception as e:
        logger.error("search_ethiopia_vehicles_by_intent: %s", e, exc_info=True)
        return []
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass


def _vehicle_soft_match(d: Dict[str, Any], brand: str, model: str, keywords: List[str]) -> bool:
    blob = " ".join(str(d.get(k) or "") for k in ("name", "full_model", "brand", "model_key", "category", "primary_use_case")).lower()
    if brand and brand.lower() in blob:
        return True
    if model and model.lower() in blob:
        return True
    hits = 0
    for kw in (keywords or [])[:8]:
        if len(kw) > 2 and kw.lower() in blob:
            hits += 1
    return hits >= 2


def unified_smart_search(query: str = "", intent: Optional[Dict[str, Any]] = None, limit: int = 24) -> Dict[str, Any]:
    """
    Hybrid AI search across marketplace `listings` AND catalog `ethiopia_vehicles`.
    Every item is tagged: source = "listing" | "clean_market".
    """
    intent = intent or extract_search_intent(query or "")
    # Default category to cars when brand/model present
    if not intent.get("category") and (intent.get("brand") or intent.get("model")):
        intent["category"] = "መኪና"

    listings: List[Dict[str, Any]] = []
    catalog: List[Dict[str, Any]] = []
    try:
        listings = search_listings_by_intent(intent, limit=limit) or []
    except Exception as e:
        logger.error("unified listings: %s", e, exc_info=True)
    try:
        catalog = search_ethiopia_vehicles_by_intent(intent, limit=limit) or []
    except Exception as e:
        logger.error("unified catalog: %s", e, exc_info=True)

    for it in listings:
        it["source"] = "listing"
        it["target_type"] = "listing"
        it["is_clean_market"] = False
    for it in catalog:
        it["source"] = "clean_market"
        it["target_type"] = "clean_market"
        it["is_clean_market"] = True
        if not it.get("price"):
            it["price"] = it.get("current_price_range_etb") or ""

    # Interleave by score, diversify sources
    merged: List[Dict[str, Any]] = []
    i = j = 0
    while len(merged) < limit and (i < len(listings) or j < len(catalog)):
        take_listing = True
        if i >= len(listings):
            take_listing = False
        elif j >= len(catalog):
            take_listing = True
        else:
            ls = int(listings[i].get("_score") or 0)
            cs = int(catalog[j].get("_score") or 0)
            if cs > ls:
                take_listing = False
            elif cs == ls:
                take_listing = (len(merged) % 2 == 0)
        if take_listing:
            merged.append(listings[i]); i += 1
        else:
            merged.append(catalog[j]); j += 1

    return {
        "success": True,
        "intent": intent,
        "items": merged,
        "listings": [x for x in merged if x.get("source") == "listing"],
        "clean_market": [x for x in merged if x.get("source") == "clean_market"],
        "counts": {
            "total": len(merged),
            "listing": sum(1 for x in merged if x.get("source") == "listing"),
            "clean_market": sum(1 for x in merged if x.get("source") == "clean_market"),
        },
    }


def ensure_favorites_and_alerts_tables():
    """Create favorites + search_alerts if missing (PG + SQLite)."""
    from models import get_db_connection, is_postgres
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        if is_postgres():
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS favorites (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT,
                    chat_id BIGINT,
                    listing_id INTEGER REFERENCES listings(id),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS search_alerts (
                    id SERIAL PRIMARY KEY,
                    user_chat_id BIGINT,
                    chat_id BIGINT,
                    category TEXT,
                    max_price NUMERIC,
                    model_hint TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """
            )
        else:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS favorites (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    chat_id INTEGER,
                    listing_id INTEGER,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS search_alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_chat_id INTEGER,
                    chat_id INTEGER,
                    category TEXT,
                    max_price TEXT,
                    model_hint TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.commit()
    except Exception as e:
        logger.error("ensure_favorites_and_alerts_tables: %s", e)
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass


def toggle_favorite(user_id, listing_id, chat_id=None, action=None):
    """Add/remove a favorites row keyed by user_id + listing_id. Also stores chat_id."""
    from models import get_db_connection, is_postgres
    ensure_favorites_and_alerts_tables()
    conn = None
    uid = int(user_id or 0)
    lid = int(listing_id or 0)
    cid = int(chat_id or user_id or 0)
    if uid <= 0 or lid <= 0:
        return {"favorited": False, "action": "noop", "listing_id": lid}
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        p = _ph()
        cur.execute(
            f"SELECT id FROM favorites WHERE user_id={p} AND listing_id={p} LIMIT 1",
            (uid, lid),
        )
        row = cur.fetchone()
        exists = bool(row)
        act = (action or "").strip().lower()
        if act not in ("add", "remove", "toggle", ""):
            act = "toggle"
        if act == "add" or (act in ("toggle", "") and not exists):
            if not exists:
                cur.execute(
                    f"INSERT INTO favorites (user_id, chat_id, listing_id) VALUES ({p},{p},{p})",
                    (uid, cid, lid),
                )
                if not is_postgres():
                    conn.commit()
            return {"favorited": True, "action": "add", "listing_id": lid, "user_id": uid, "chat_id": cid}
        if exists:
            fid = row["id"] if isinstance(row, dict) else row[0]
            cur.execute(f"DELETE FROM favorites WHERE id={p}", (fid,))
            if not is_postgres():
                conn.commit()
        return {"favorited": False, "action": "remove", "listing_id": lid, "user_id": uid, "chat_id": cid}
    except Exception as e:
        logger.error("toggle_favorite: %s", e, exc_info=True)
        return {"favorited": False, "action": "error", "message": str(e), "listing_id": lid}
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass


def update_listing_price(listing_id, new_price):
    """Update listings.price (TEXT). Returns (ok, old_price, title, category)."""
    from models import get_db_connection, is_postgres
    conn = None
    lid = int(listing_id or 0)
    price_s = str(new_price if new_price is not None else "").strip()
    if lid <= 0:
        return False, None, "", ""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        p = _ph()
        cur.execute(
            f"""
            SELECT id, price, main_category, sub_category, extra_data, description
            FROM listings WHERE id={p} LIMIT 1
            """,
            (lid,),
        )
        row = cur.fetchone()
        if not row:
            return False, None, "", ""
        d = dict(row) if not isinstance(row, dict) else row
        old_price = d.get("price")
        category = str(d.get("main_category") or "")
        title = str(d.get("sub_category") or "")
        extra = d.get("extra_data")
        if isinstance(extra, str):
            try:
                extra = json.loads(extra)
            except Exception:
                extra = {}
        if isinstance(extra, dict):
            title = title or str(extra.get("title") or extra.get("brand") or extra.get("model") or "")
        title = title or str(d.get("description") or "")[:80]
        cur.execute(f"UPDATE listings SET price={p} WHERE id={p}", (price_s, lid))
        if not is_postgres():
            conn.commit()
        return True, old_price, title, category
    except Exception as e:
        logger.error("update_listing_price: %s", e, exc_info=True)
        return False, None, "", ""
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass


def get_favorite_subscribers(listing_id):
    """Users who favorited a listing — chat_id / user_id for Telegram push."""
    from models import get_db_connection
    ensure_favorites_and_alerts_tables()
    conn = None
    out = []
    lid = int(listing_id or 0)
    if lid <= 0:
        return out
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        p = _ph()
        cur.execute(
            f"SELECT user_id, chat_id, listing_id FROM favorites WHERE listing_id={p}",
            (lid,),
        )
        for r in cur.fetchall() or []:
            d = dict(r) if not isinstance(r, dict) else r
            out.append({
                "user_id": d.get("user_id"),
                "chat_id": d.get("chat_id") or d.get("user_id"),
                "listing_id": d.get("listing_id") or lid,
            })
    except Exception as e:
        logger.error("get_favorite_subscribers: %s", e)
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass
    return out


def get_matching_alerts(category, price, model_hint=""):
    """Match search_alerts using user_chat_id, chat_id, category, max_price, model_hint."""
    from models import get_db_connection
    ensure_favorites_and_alerts_tables()
    conn = None
    matches = []
    price_n = _parse_price(price)
    cat = (category or "").strip()
    hint = (model_hint or "").strip().lower()
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, user_chat_id, chat_id, category, max_price, model_hint
            FROM search_alerts
            ORDER BY id DESC
            LIMIT 400
            """
        )
        for r in cur.fetchall() or []:
            d = dict(r) if not isinstance(r, dict) else r
            a_cat = str(d.get("category") or "").strip()
            if a_cat and a_cat.lower() not in ("all", "ሁሉም", "*"):
                if cat and a_cat not in cat and cat not in a_cat:
                    aliases = {
                        "መኪና": ["መኪና", "car", "cars", "vehicle"],
                        "ቤት": ["ቤት", "house", "property", "home"],
                    }
                    ok = False
                    for k, vals in aliases.items():
                        pool = [k] + vals
                        if a_cat in pool or a_cat.lower() in [v.lower() for v in vals]:
                            if any(v.lower() in (cat or "").lower() for v in pool) or k in cat:
                                ok = True
                                break
                    if not ok:
                        continue
            max_p = _parse_price(d.get("max_price"))
            if max_p > 0 and price_n > 0 and price_n > max_p:
                continue
            a_hint = str(d.get("model_hint") or "").strip().lower()
            if hint and a_hint and a_hint not in hint and hint not in a_hint:
                continue
            d["user_chat_id"] = d.get("user_chat_id") or d.get("chat_id")
            d["chat_id"] = d.get("chat_id") or d.get("user_chat_id")
            matches.append(d)
    except Exception as e:
        logger.error("get_matching_alerts: %s", e)
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass
    return matches


def query_ethiopia_vehicle(model_key):
    """Lookup ethiopia_vehicles by model_key / full_model / name."""
    from models import get_db_connection
    conn = None
    key = (model_key or "").strip().lower()
    if not key:
        return None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        p = _ph()
        cur.execute(
            f"""
            SELECT * FROM ethiopia_vehicles
            WHERE LOWER(COALESCE(model_key,''))={p}
               OR LOWER(COALESCE(full_model,''))={p}
               OR LOWER(COALESCE(name,'')) LIKE {p}
            LIMIT 1
            """,
            (key, key, "%" + key + "%"),
        )
        row = cur.fetchone()
        return dict(row) if row else None
    except Exception as e:
        logger.warning("query_ethiopia_vehicle: %s", e)
        return None
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass


def query_knowledge_base(topic, category=""):
    """Search knowledge_base.title / topic / keywords."""
    from models import get_db_connection
    conn = None
    q = (topic or "").strip()
    out = []
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        p = _ph()
        like = "%" + q + "%"
        if category:
            cur.execute(
                f"""
                SELECT * FROM knowledge_base
                WHERE (category={p} OR {p}='')
                  AND (title LIKE {p} OR topic LIKE {p} OR CAST(keywords AS TEXT) LIKE {p})
                ORDER BY id DESC LIMIT 20
                """,
                (category, category, like, like, like),
            )
        else:
            cur.execute(
                f"""
                SELECT * FROM knowledge_base
                WHERE title LIKE {p} OR topic LIKE {p} OR CAST(keywords AS TEXT) LIKE {p}
                ORDER BY id DESC LIMIT 20
                """,
                (like, like, like),
            )
        for r in cur.fetchall() or []:
            d = dict(r)
            kw = d.get("keywords")
            if isinstance(kw, str):
                try:
                    d["keywords"] = json.loads(kw)
                except Exception:
                    pass
            out.append(d)
    except Exception as e:
        logger.warning("query_knowledge_base: %s", e)
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass
    return out



def _extract_image_urls(d: Dict[str, Any]) -> list:
    urls: List[str] = []
    def _push(val: Any) -> None:
        if val is None:
            return
        if isinstance(val, (list, tuple)):
            for x in val:
                _push(x)
            return
        if isinstance(val, dict):
            for k in ("url", "src", "image", "image_url", "photo", "href"):
                if val.get(k):
                    _push(val.get(k))
            return
        s = str(val).strip()
        if not s or s.lower() in ("null", "none", "undefined", "[]", "{}"):
            return
        if s.startswith("[") and s.endswith("]"):
            try:
                _push(json.loads(s))
                return
            except Exception:
                pass
        if s.startswith("http://") or s.startswith("https://") or s.startswith("data:image"):
            if s not in urls:
                urls.append(s)
    for key in (
        "image_url", "image", "photo_url", "photo", "thumbnail", "thumb",
        "cover_image", "cover", "main_image", "primary_image",
        "telegram_image", "telegram_photo", "tg_image", "file_url",
        "media_url", "picture", "pic",
    ):
        if d.get(key):
            _push(d.get(key))
    for key in ("images", "photos", "photo_urls", "image_urls", "media", "gallery", "attachments"):
        if d.get(key) is not None:
            _push(d.get(key))
    extra = d.get("extra_data")
    if isinstance(extra, str):
        try:
            extra = json.loads(extra)
        except Exception:
            extra = None
    if isinstance(extra, dict):
        for key in ("image_url", "photo_url", "telegram_image", "images", "photos", "photo_urls"):
            if extra.get(key) is not None:
                _push(extra.get(key))
    return urls


def unify_listing_images(d: Dict[str, Any]) -> Dict[str, Any]:
    out = dict(d or {})
    urls = _extract_image_urls(out)
    primary = urls[0] if urls else ""
    out["image_url"] = primary
    out["photo_url"] = primary
    out["images"] = urls
    out["photos"] = urls
    if primary and not out.get("thumbnail"):
        out["thumbnail"] = primary
    return out


def _normalize_listing_row(d: Dict[str, Any], source: str = "listing") -> Dict[str, Any]:
    out = dict(d or {})
    out["source"] = source
    out["target_type"] = source
    if out.get("extra_data") and isinstance(out["extra_data"], str):
        try:
            out["extra_data"] = json.loads(out["extra_data"])
        except Exception:
            pass
    for list_key in ("photos", "images"):
        if out.get(list_key) and isinstance(out[list_key], str):
            try:
                out[list_key] = json.loads(out[list_key])
            except Exception:
                pass
    if out.get("created_at") and not isinstance(out["created_at"], str):
        try:
            out["created_at"] = out["created_at"].isoformat()
        except Exception:
            out["created_at"] = str(out["created_at"])
    if not out.get("title"):
        bits = [
            out.get("brand") or "",
            out.get("model") or out.get("full_model") or out.get("name") or "",
            out.get("sub_category") or "",
        ]
        out["title"] = " ".join(x for x in bits if x).strip() or str(out.get("description") or "")[:80]
    if source == "clean_market" and not out.get("price"):
        out["price"] = out.get("current_price_range_etb") or out.get("price_range") or ""
    out["main_category"] = out.get("main_category") or out.get("category") or ""
    out = unify_listing_images(out)
    return out



# =============================================================================
# HYBRID FYP ENGINE — cold-start preferences + real-time view history
# =============================================================================

def _is_car_category(val: Any) -> bool:
    s = str(val or "").strip().lower()
    if not s:
        return False
    if any(x in s for x in ("ቤት", "house", "property", "villa", "apartment", "ንብረት", "condo")):
        return False
    return any(x in s for x in ("መኪና", "car", "vehicle", "auto", "sedan", "suv", "pickup"))


def _is_house_category(val: Any) -> bool:
    s = str(val or "").strip().lower()
    if not s:
        return False
    if any(x in s for x in ("መኪና", "car", "vehicle", "auto")):
        return False
    return any(x in s for x in ("ቤት", "house", "property", "villa", "apartment", "ንብረት", "condo"))


def _active_sell_sql() -> str:
    return """
        (status IS NULL OR LOWER(CAST(status AS TEXT)) NOT IN ('deleted','sold','rented','expired'))
        AND (UPPER(TRIM(COALESCE(req_type,''))) NOT IN ('BUY','RENT') OR COALESCE(req_type,'') = '')
    """


def _car_sql() -> str:
    return """
        (
          LOWER(COALESCE(main_category,'')) IN ('መኪና','car','cars','vehicle','vehicles','auto')
          OR LOWER(COALESCE(CAST(main_category AS TEXT),'')) LIKE '%%car%%'
          OR LOWER(COALESCE(CAST(main_category AS TEXT),'')) LIKE '%%መኪና%%'
        )
        AND LOWER(COALESCE(main_category,'')) NOT IN ('ቤት','house','houses','home','property')
        AND LOWER(COALESCE(CAST(main_category AS TEXT),'')) NOT LIKE '%%house%%'
        AND LOWER(COALESCE(CAST(main_category AS TEXT),'')) NOT LIKE '%%ቤት%%'
        AND LOWER(COALESCE(CAST(main_category AS TEXT),'')) NOT LIKE '%%property%%'
    """


def _house_sql() -> str:
    return """
        (
          LOWER(COALESCE(main_category,'')) IN ('ቤት','house','houses','home','property','ንብረት')
          OR LOWER(COALESCE(CAST(main_category AS TEXT),'')) LIKE '%%house%%'
          OR LOWER(COALESCE(CAST(main_category AS TEXT),'')) LIKE '%%ቤት%%'
          OR LOWER(COALESCE(CAST(main_category AS TEXT),'')) LIKE '%%property%%'
        )
        AND LOWER(COALESCE(main_category,'')) NOT IN ('መኪና','car','cars','vehicle','vehicles','auto')
        AND LOWER(COALESCE(CAST(main_category AS TEXT),'')) NOT LIKE '%%car%%'
        AND LOWER(COALESCE(CAST(main_category AS TEXT),'')) NOT LIKE '%%መኪና%%'
    """


def parse_budget_range(raw: Any) -> Dict[str, float]:
    """Parse budget strings like '1.5M - 4M ETB', 'ከ 1.5M - 4 ሚሊዮን ETB' into min/max."""
    text = str(raw or "").strip()
    if not text:
        return {"minPrice": 0.0, "maxPrice": 0.0}

    def token_to_num(tok: str) -> float:
        t = tok.strip().lower().replace(",", "").replace("etb", "").replace("ብር", "")
        t = t.replace("ሚሊዮን", "m").replace("million", "m").replace("ሺህ", "k").replace("thousand", "k")
        mult = 1.0
        if t.endswith("m") or "m" in t:
            mult = 1_000_000.0
            t = t.replace("m", "")
        elif t.endswith("k") or "k" in t:
            mult = 1_000.0
            t = t.replace("k", "")
        t = re.sub(r"[^0-9.]", "", t)
        try:
            return float(t) * mult if t else 0.0
        except Exception:
            return 0.0

    # Range split
    parts = re.split(r"\s*[-–—toእስከከ]\s*", text, flags=re.I)
    nums = [token_to_num(p) for p in parts if p.strip()]
    nums = [n for n in nums if n > 0]
    if not nums:
        # single number anywhere
        n = token_to_num(text)
        if n > 0:
            if "+" in text or "በላይ" in text or "above" in text.lower():
                return {"minPrice": n, "maxPrice": 999_999_999.0}
            return {"minPrice": 0.0, "maxPrice": n}
        return {"minPrice": 0.0, "maxPrice": 0.0}
    if len(nums) == 1:
        if "+" in text or "በላይ" in text:
            return {"minPrice": nums[0], "maxPrice": 999_999_999.0}
        return {"minPrice": 0.0, "maxPrice": nums[0]}
    return {"minPrice": min(nums[0], nums[1]), "maxPrice": max(nums[0], nums[1])}


def _fetch_listings(
    limit: int = 40,
    category: str = "",
    min_price: float = 0.0,
    max_price: float = 0.0,
    exclude_ids: Optional[List[int]] = None,
) -> List[Dict[str, Any]]:
    """
    Newest active SELL rows from `listings` only.
    STRICT numeric budget (same idea as Detail-page similar items):
      CAST(regexp_replace(price,'[^0-9]','','g') AS NUMERIC) BETWEEN min_price AND max_price
    Python re-check guarantees items above max_price are NEVER returned.
    """
    from models import get_db_connection, is_postgres

    limit = max(1, min(int(limit or 40), 80))
    exclude_ids = exclude_ids or []
    min_price = float(min_price or 0)
    max_price = float(max_price or 0)
    rows: List[Dict[str, Any]] = []
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        p = _ph()
        try:
            pg = bool(is_postgres())
        except Exception:
            pg = False

        cat = str(category or "").strip().lower()
        want_cars = cat in ("cars", "car", "መኪና", "vehicle", "vehicles")
        want_houses = cat in ("houses", "house", "ቤት", "property", "properties", "ንብረት")

        where = _active_sell_sql()
        if want_cars:
            where += " AND " + _car_sql()
        elif want_houses:
            where += " AND " + _house_sql()

        params: List[Any] = []
        # Numeric price expression (Postgres + SQLite-ish fallbacks)
        if pg:
            price_expr = "NULLIF(regexp_replace(COALESCE(CAST(price AS TEXT), '0'), '[^0-9]', '', 'g'), '')::NUMERIC"
        else:
            # SQLite: strip non-digits poorly — still filter in Python
            price_expr = "CAST(price AS REAL)"

        if max_price and 0 < max_price < 999_999_999:
            where += f" AND ({price_expr} IS NOT NULL) AND ({price_expr} <= {p})"
            params.append(max_price)
            if min_price > 0:
                where += f" AND ({price_expr} >= {p})"
                params.append(min_price)

        order = (
            "ORDER BY COALESCE(created_at, TIMESTAMP '1970-01-01') DESC, id DESC"
            if pg
            else "ORDER BY COALESCE(created_at, '') DESC, id DESC"
        )
        fetch_n = limit * 3
        params.append(fetch_n)
        sql = f"SELECT * FROM listings WHERE {where} {order} LIMIT {p}"
        try:
            cur.execute(sql, tuple(params))
        except Exception as sql_err:
            logger.warning("_fetch_listings SQL soft-fallback: %s", sql_err)
            # Retry without SQL price filter; Python will enforce
            where2 = _active_sell_sql()
            if want_cars:
                where2 += " AND " + _car_sql()
            elif want_houses:
                where2 += " AND " + _house_sql()
            try:
                cur.execute(
                    f"SELECT * FROM listings WHERE {where2} {order} LIMIT {p}",
                    (fetch_n,),
                )
            except Exception:
                cur.execute(
                    f"SELECT * FROM listings WHERE {where2} ORDER BY id DESC LIMIT {p}",
                    (fetch_n,),
                )

        ex = set(int(x) for x in exclude_ids if x is not None)
        for r in cur.fetchall() or []:
            d = _normalize_listing_row(dict(r), source="listing")
            try:
                lid = int(d.get("id") or 0)
            except Exception:
                lid = 0
            if lid and lid in ex:
                continue
            mc = d.get("main_category") or d.get("category") or ""
            if want_cars and _is_house_category(mc):
                continue
            if want_houses and _is_car_category(mc):
                continue

            # STRICT numeric re-check (Detail-page style) — never leak over-budget
            price = _parse_price(d.get("price"))
            if max_price and 0 < max_price < 999_999_999:
                if price <= 0:
                    # unknown price: exclude when user set a hard cap
                    continue
                if price > max_price:
                    continue
                if min_price > 0 and price < min_price:
                    continue

            rows.append(d)
            if len(rows) >= limit:
                break
    except Exception as e:
        logger.error("_fetch_listings: %s", e, exc_info=True)
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass
    return rows


def _load_listings_by_ids(ids: List[int]) -> List[Dict[str, Any]]:
    if not ids:
        return []
    from models import get_db_connection

    out: List[Dict[str, Any]] = []
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        p = _ph()
        # Preserve order of ids
        for lid in ids:
            try:
                cur.execute(f"SELECT * FROM listings WHERE id = {p} LIMIT 1", (int(lid),))
                r = cur.fetchone()
                if r:
                    out.append(_normalize_listing_row(dict(r), source="listing"))
            except Exception:
                continue
    except Exception as e:
        logger.warning("_load_listings_by_ids: %s", e)
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass
    return out


def _similar_to_seed(
    seed: Dict[str, Any],
    limit: int = 12,
    exclude_ids: Optional[List[int]] = None,
) -> List[Dict[str, Any]]:
    """
    Same spirit as product-detail 'ተቀራራቢ / Similar Items':
    same category, nearby price band, newest first.
    """
    exclude_ids = list(exclude_ids or [])
    try:
        seed_id = int(seed.get("id") or 0)
        if seed_id:
            exclude_ids.append(seed_id)
    except Exception:
        pass

    mc = seed.get("main_category") or seed.get("category") or ""
    if _is_house_category(mc):
        cat = "houses"
    else:
        cat = "cars"

    seed_price = _parse_price(seed.get("price"))
    min_p = 0.0
    max_p = 0.0
    if seed_price > 0:
        min_p = seed_price * 0.55
        max_p = seed_price * 1.55

    return _fetch_listings(
        limit=limit,
        category=cat,
        min_price=min_p,
        max_price=max_p if max_p > 0 else 0.0,
        exclude_ids=exclude_ids,
    )


def fetch_for_you_feed(
    user_id: int = 0,
    limit: int = 24,
    page: int = 1,
    category: str = "",
    recently_viewed_ids: Optional[List[int]] = None,
    last_category: str = "",
    last_price: Any = None,
    budget_range: str = "",
    main_category: str = "",
) -> Dict[str, Any]:
    """
    HYBRID FYP — SINGLE TABLE (`listings` only; adika_clean_market removed).

      STEP 1 Cold start  — user_preferences main_category + budget_range
      STEP 2 Real-time   — recently_viewed_ids / last_category / last_price override
      STEP 3 Fallback    — ORDER BY created_at DESC LIMIT 30 (cars + houses)

    Images: image_url || images[0] || photo_url || telegram_image
    Category isolation: cars never leak into houses and vice-versa.
    """
    uid = int(user_id or 0)
    limit = max(1, min(int(limit or 24), 60))
    page = max(1, int(page or 1))
    viewed = []
    for x in (recently_viewed_ids or []):
        try:
            viewed.append(int(x))
        except Exception:
            pass
    viewed = list(dict.fromkeys(viewed))  # unique, preserve order

    # ---- Load saved preferences (cold start) ----
    prefs: Dict[str, Any] = {}
    try:
        if uid:
            prefs = get_user_preferences(uid) or {}
    except Exception:
        prefs = {}

    pref_cat = (
        main_category
        or category
        or (prefs.get("categories") or [None])[0]
        or prefs.get("category")
        or prefs.get("main_category")
        or ""
    )
    pref_budget_raw = (
        budget_range
        or prefs.get("budget")
        or prefs.get("budget_range")
        or prefs.get("budgetRange")
        or ""
    )
    # Prefer CLEAN integers from user_preferences (Detail-page style)
    budget = {"minPrice": 0.0, "maxPrice": 0.0}
    try:
        bmin = int(prefs.get("min_price") or prefs.get("budget_min") or 0)
        bmax = int(prefs.get("max_price") or prefs.get("budget_max") or 0)
        if bmax and bmax < 999_999_999:
            budget = {"minPrice": float(bmin), "maxPrice": float(bmax)}
    except Exception:
        pass
    if not budget.get("maxPrice") or budget["maxPrice"] >= 999_999_999:
        parsed = parse_budget_range(pref_budget_raw)
        if parsed.get("maxPrice"):
            budget = parsed
    # Request overrides
    if budget_range:
        parsed = parse_budget_range(budget_range)
        if parsed.get("maxPrice"):
            budget = parsed

    # ---- STEP 2: real-time behavioral override ----
    behavior_cat = last_category or ""
    behavior_price = _parse_price(last_price) if last_price is not None else 0.0
    mode = "fallback_newest"
    items: List[Dict[str, Any]] = []
    exclude = viewed[:]  # don't re-show just-viewed at top as duplicates later

    if viewed or behavior_cat or behavior_price > 0:
        mode = "realtime_behavior"
        # Load viewed seeds for similar-items expansion
        seeds = _load_listings_by_ids(viewed[:8])
        if not seeds and behavior_cat:
            # Synthetic seed from last_category + last_price
            seeds = [{
                "id": 0,
                "main_category": behavior_cat,
                "category": behavior_cat,
                "price": behavior_price or None,
            }]
        similar: List[Dict[str, Any]] = []
        seen = set(exclude)
        for seed in seeds:
            for s in _similar_to_seed(seed, limit=max(8, limit // 2), exclude_ids=list(seen)):
                try:
                    sid = int(s.get("id") or 0)
                except Exception:
                    sid = 0
                if sid and sid in seen:
                    continue
                if sid:
                    seen.add(sid)
                similar.append(s)
        # Prefer similar; if thin, fill with category+budget cold start
        items = similar
        if len(items) < limit:
            cat = behavior_cat or pref_cat
            if _is_house_category(cat):
                cat_key = "houses"
            elif _is_car_category(cat) or cat:
                cat_key = "cars" if (_is_car_category(cat) or not _is_house_category(cat)) else ""
            else:
                cat_key = ""
            if behavior_price > 0:
                min_p = behavior_price * 0.5
                max_p = behavior_price * 1.6
            else:
                min_p = float(budget.get("minPrice") or 0)
                max_p = float(budget.get("maxPrice") or 0)
            filler = _fetch_listings(
                limit=limit,
                category=cat_key,
                min_price=min_p,
                max_price=max_p,
                exclude_ids=list(seen),
            )
            for f in filler:
                try:
                    fid = int(f.get("id") or 0)
                except Exception:
                    fid = 0
                if fid and fid in seen:
                    continue
                if fid:
                    seen.add(fid)
                items.append(f)
                if len(items) >= limit * 2:
                    break

    elif pref_cat or budget.get("maxPrice"):
        # ---- STEP 1: cold start from preferences ----
        mode = "cold_start_prefs"
        if _is_house_category(pref_cat):
            cat_key = "houses"
        elif _is_car_category(pref_cat) or str(pref_cat).strip():
            cat_key = "cars" if (_is_car_category(pref_cat) or str(pref_cat) in ("መኪና", "Cars", "cars")) else (
                "houses" if _is_house_category(pref_cat) else ""
            )
            if not cat_key:
                # raw mapping
                pl = str(pref_cat).lower()
                if any(x in pl for x in ("ቤት", "house")):
                    cat_key = "houses"
                elif any(x in pl for x in ("መኪና", "car")):
                    cat_key = "cars"
        else:
            cat_key = ""
        items = _fetch_listings(
            limit=limit * 2,
            category=cat_key,
            min_price=float(budget.get("minPrice") or 0),
            max_price=float(budget.get("maxPrice") or 0),
            exclude_ids=exclude,
        )

    else:
        # ---- STEP 3: fallback newest cars + houses 50/50 ----
        mode = "fallback_newest"
        half = max(1, min(30, limit))
        cars = _fetch_listings(limit=half, category="cars", exclude_ids=exclude)
        houses = _fetch_listings(limit=half, category="houses", exclude_ids=exclude)

        def _ck(d: Dict[str, Any]) -> str:
            for k in ("created_at", "created", "updated_at"):
                if d.get(k):
                    return str(d.get(k))
            try:
                return f"{int(d.get('id') or 0):012d}"
            except Exception:
                return "0"

        merged = cars + houses
        merged.sort(key=_ck, reverse=True)
        items = merged

    # Page slice
    offset = max(0, (page - 1) * limit)
    window = items
    page_items = window[offset: offset + limit]

    # Final unified image schema
    page_items = [unify_listing_images(x) for x in page_items]

    return {
        "success": True,
        "items": page_items,
        "listings": page_items,
        "clean_market": [],  # deprecated — single-table listings only
        "page": page,
        "limit": limit,
        "prefs": prefs,
        "intent": {
            "category": pref_cat or last_category or "",
            "budget_range": pref_budget_raw,
            "minPrice": budget.get("minPrice") or 0,
            "maxPrice": budget.get("maxPrice") or 0,
            "last_category": last_category or "",
            "last_price": behavior_price,
            "viewed_count": len(viewed),
        },
        "has_more": len(window) > offset + limit,
        "mode": mode,
        "user_id": uid,
        "counts": {
            "total": len(page_items),
            "listing": len(page_items),
            "clean_market": 0,
        },
    }


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
    categories: List[str],
    budget_min: int = 0,
    budget_max: int = 999_999_999,
) -> bool:
    from models import get_db_connection, is_postgres
    ensure_feature_tables()
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        p = _ph()
        cats = json.dumps(categories or [], ensure_ascii=False)
        if is_postgres():
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
                (int(user_id), cats, int(budget_min or 0), int(budget_max or 999999999)),
            )
        else:
            cur.execute(
                f"""
                INSERT OR REPLACE INTO user_preferences (user_id, categories, budget_min, budget_max, onboarding_done)
                VALUES ({p},{p},{p},{p},1)
                """,
                (int(user_id), cats, int(budget_min or 0), int(budget_max or 999999999)),
            )
            conn.commit()
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
            return {"categories": [], "budget_min": 0, "budget_max": 999999999, "onboarding_done": False}
        d = dict(row)
        cats = d.get("categories") or []
        if isinstance(cats, str):
            try:
                cats = json.loads(cats)
            except Exception:
                cats = []
        return {
            "categories": cats,
            "budget_min": int(d.get("budget_min") or 0),
            "budget_max": int(d.get("budget_max") or 999999999),
            "onboarding_done": bool(d.get("onboarding_done")),
        }
    except Exception as e:
        logger.warning("get_user_preferences: %s", e)
        return {"categories": [], "budget_min": 0, "budget_max": 999999999, "onboarding_done": False}
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass


def _parse_price(val: Any) -> float:
    if val is None:
        return 0.0
    if isinstance(val, (int, float)):
        return float(val)
    s = re.sub(r"[^\d.]", "", str(val).replace(",", ""))
    try:
        return float(s) if s else 0.0
    except Exception:
        return 0.0


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



# =============================================================================
# DUAL-DATABASE AI SEARCH / HYBRID FOR-YOU
# =============================================================================
def _ai_extract_search_intent(query: str) -> Dict[str, Any]:
    """Extract structured search intent with an LLM; always returns safe JSON."""
    q = str(query or "").strip()
    fallback = {
        "category": "all",
        "brand": None,
        "model": None,
        "price_max": None,
        "transmission": None,
    }
    if not q:
        return fallback

    try:
        import os
        import urllib.request
        import urllib.error

        key = os.environ.get("OPENROUTER_API_KEY", "").strip()
        if key:
            prompt = (
                "Extract vehicle marketplace search intent. Return ONLY valid JSON with exactly these keys: "
                "category, brand, model, price_max, transmission. "
                "category must be one of cars, property, all. "
                "price_max must be a number in ETB or null. "
                "transmission must be Automatic, Manual, or null. "
                "Do not invent values. Preserve Ethiopian/Amharic meaning. "
                f"User query: {q}"
            )
            payload = json.dumps({
                "model": os.environ.get("OPENROUTER_MODEL", "qwen/qwen3-30b-a3b-instruct"),
                "messages": [
                    {"role": "system", "content": "You are a precise search-intent extraction engine."},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0,
                "max_tokens": 220,
                "response_format": {"type": "json_object"},
            }).encode("utf-8")
            req = urllib.request.Request(
                "https://openrouter.ai/api/v1/chat/completions",
                data=payload,
                headers={
                    "Authorization": f"Bearer {key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": os.environ.get("WEBAPP_URL", "https://adika.market"),
                    "X-Title": "Adika Marketplace",
                },
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=12) as resp:
                raw = json.loads(resp.read().decode("utf-8"))
            content = raw.get("choices", [{}])[0].get("message", {}).get("content", "")
            content = re.sub(r"^```(?:json)?\s*|\s*```$", "", str(content).strip(), flags=re.I)
            parsed = json.loads(content)
            if isinstance(parsed, dict):
                out = dict(fallback)
                for k in out:
                    if k in parsed:
                        out[k] = parsed[k]
                cat = str(out.get("category") or "all").lower().strip()
                out["category"] = cat if cat in ("cars", "property", "all") else "all"
                if out.get("price_max") is not None:
                    out["price_max"] = int(float(re.sub(r"[^\d.]", "", str(out["price_max"]))) or 0) or None
                for k in ("brand", "model", "transmission"):
                    if out.get(k) is not None:
                        out[k] = str(out[k]).strip() or None
                return out
    except Exception:
        pass

    # Deterministic fallback when the LLM is unavailable.
    low = q.lower()
    fallback["category"] = "cars" if any(x in low for x in (
        "car", "vehicle", "toyota", "byd", "hyundai", "suv", "sedan",
        "መኪና", "ተሽከርካሪ", "ቪትስ", "ኮሮላ", "ፕራዶ"
    )) else ("property" if any(x in low for x in (
        "house", "home", "villa", "apartment", "ቤት", "ቪላ", "አፓርታማ"
    )) else "all")
    nums = re.findall(r"\d[\d,]*(?:\.\d+)?", low)
    if nums:
        try:
            n = float(nums[-1].replace(",", ""))
            if "million" in low or "ሚሊዮን" in low:
                n *= 1_000_000
            elif "k" in low or "ሺህ" in low:
                n *= 1_000
            fallback["price_max"] = int(n)
        except Exception:
            pass
    fallback["transmission"] = "Automatic" if any(x in low for x in ("automatic", "auto", "አውቶማቲክ")) else (
        "Manual" if any(x in low for x in ("manual", "ማንዋል")) else None
    )
    known = [
        ("toyota", "Toyota"), ("byd", "BYD"), ("hyundai", "Hyundai"),
        ("suzuki", "Suzuki"), ("corolla", "Corolla"), ("vitz", "Vitz"),
        ("prado", "Prado"), ("hilux", "Hilux"), ("rav4", "RAV4"),
        ("seagull", "Seagull"), ("dolphin", "Dolphin"), ("tucson", "Tucson"),
    ]
    for needle, val in known:
        if needle in low:
            if val.lower() in ("toyota", "byd", "hyundai", "suzuki"):
                fallback["brand"] = val
            else:
                fallback["model"] = val
            break
    return fallback


def _row_to_dict(cur, row) -> Dict[str, Any]:
    if isinstance(row, dict):
        return dict(row)
    try:
        return dict(zip([c[0] for c in cur.description], row))
    except Exception:
        return {}


def _hybrid_text(item: Dict[str, Any]) -> str:
    extra = item.get("extra_data")
    if isinstance(extra, str):
        try:
            extra = json.loads(extra)
        except Exception:
            extra = {}
    if not isinstance(extra, dict):
        extra = {}
    vals = [
        item.get("name"), item.get("full_model"), item.get("model_key"),
        item.get("brand"), item.get("model"), item.get("category"),
        item.get("main_category"), item.get("sub_category"),
        item.get("description"), item.get("transmission"),
        item.get("fuel_type"), item.get("fuel"),
        extra.get("car_model"), extra.get("brand"), extra.get("model"),
        extra.get("transmission"),
    ]
    return " ".join(str(v) for v in vals if v).lower()


def _hybrid_price(item: Dict[str, Any]) -> float:
    for key in ("price", "price_etb", "asking_price", "current_price"):
        n = _parse_price(item.get(key))
        if n > 0:
            return n
    raw = str(item.get("current_price_range_etb") or "")
    nums = re.findall(r"\d[\d,]*(?:\.\d+)?", raw)
    if nums:
        try:
            return float(nums[0].replace(",", ""))
        except Exception:
            pass
    return 0.0


def _hybrid_match_score(item: Dict[str, Any], intent: Dict[str, Any]) -> int:
    text = _hybrid_text(item)
    score = 0
    category = str(intent.get("category") or "all").lower()
    if category == "cars":
        if any(x in text for x in ("መኪና", "car", "vehicle", "automotive", "suv", "sedan", "hatchback", "pickup")):
            score += 35
        else:
            return -1
    elif category == "property":
        if any(x in text for x in ("ቤት", "house", "property", "villa", "apartment", "real estate")):
            score += 35
        else:
            return -1

    brand = str(intent.get("brand") or "").strip().lower()
    model = str(intent.get("model") or "").strip().lower()
    transmission = str(intent.get("transmission") or "").strip().lower()
    if brand:
        score += 35 if brand in text else -20
    if model:
        score += 45 if model in text else -25
    if transmission:
        score += 20 if transmission in text or transmission.replace("automatic", "auto") in text else -10

    price_max = _parse_price(intent.get("price_max"))
    price = _hybrid_price(item)
    if price_max > 0 and price > 0:
        if price <= price_max:
            score += 25
        else:
            return -1

    # Exact query terms get a small relevance boost.
    return score


def _normalize_hybrid_item(item: Dict[str, Any], source: str, score: int) -> Dict[str, Any]:
    d = dict(item)
    d["source"] = source
    d["_score"] = int(score)
    if source == "clean_market":
        d["target_type"] = "clean_market"
        d["source_label"] = "Adika Clean Market"
        d["price_etb"] = d.get("price_etb") or d.get("price") or d.get("current_price_range_etb")
        d["title"] = d.get("title") or d.get("full_model") or d.get("name") or d.get("model") or "Adika Clean Market Vehicle"
    else:
        d["target_type"] = "listing"
        d["source_label"] = "Marketplace"
        extra = d.get("extra_data")
        if isinstance(extra, str):
            try:
                extra = json.loads(extra)
            except Exception:
                extra = {}
        extra = extra if isinstance(extra, dict) else {}
        d["title"] = d.get("title") or extra.get("car_model") or d.get("sub_category") or d.get("model") or d.get("main_category") or "Marketplace Listing"
        d["price_etb"] = d.get("price_etb") or d.get("price")
    for k, v in list(d.items()):
        if hasattr(v, "isoformat"):
            try:
                d[k] = v.isoformat()
            except Exception:
                d[k] = str(v)
    return d


def hybrid_smart_search(query: str, limit: int = 30) -> Dict[str, Any]:
    """LLM intent extraction + unified search across listings and ethiopia_vehicles."""
    intent = _ai_extract_search_intent(query)
    results: List[Dict[str, Any]] = []
    conn = None
    try:
        from models import get_db_connection
        conn = get_db_connection()
        cur = conn.cursor()
        # Fetch both sources independently so one empty/broken table never hides the other.
        try:
            cur.execute(
                "SELECT * FROM listings WHERE (status IS NULL OR LOWER(CAST(status AS TEXT)) NOT IN ('deleted','sold','rented','expired')) "
                "AND (UPPER(TRIM(COALESCE(req_type,''))) NOT IN ('BUY','RENT') OR COALESCE(req_type,'')='') "
                "ORDER BY id DESC LIMIT 500"
            )
            listing_rows = cur.fetchall() or []
            for row in listing_rows:
                d = _row_to_dict(cur, row)
                sc = _hybrid_match_score(d, intent)
                # When AI returns no useful entity, search the literal query too.
                if sc < 0:
                    continue
                if not (intent.get("brand") or intent.get("model")) and query.strip():
                    if query.strip().lower() not in _hybrid_text(d) and sc < 35:
                        continue
                results.append(_normalize_hybrid_item(d, "listing", sc))
        except Exception:
            pass

        try:
            cur.execute("SELECT * FROM ethiopia_vehicles LIMIT 500")
            clean_rows = cur.fetchall() or []
            for row in clean_rows:
                d = _row_to_dict(cur, row)
                sc = _hybrid_match_score(d, intent)
                if sc < 0:
                    continue
                if not (intent.get("brand") or intent.get("model")) and query.strip():
                    if query.strip().lower() not in _hybrid_text(d) and sc < 35:
                        continue
                results.append(_normalize_hybrid_item(d, "clean_market", sc))
        except Exception:
            pass
    except Exception:
        pass
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass

    results.sort(key=lambda x: (-int(x.get("_score") or 0), 0 if x.get("source") == "listing" else 1, -(int(x.get("id") or 0) if str(x.get("id") or "").isdigit() else 0)))
    # Keep both sources represented whenever both have matches.
    top = results[:max(1, int(limit))]
    return {
        "success": True,
        "query": query,
        "intent": intent,
        "items": top,
        "results": top,
        "listings": [x for x in top if x.get("source") == "listing"],
        "clean_market": [x for x in top if x.get("source") == "clean_market"],
    }


def fetch_for_you_feed(user_id: int, limit: int = 24, page: int = 1) -> Dict[str, Any]:
    """Hybrid For-You feed: preference-aware listings + ethiopia_vehicles/Adika Clean Market."""
    prefs = get_user_preferences(user_id) if user_id else {
        "categories": ["መኪና", "ቤት"],
        "budget_min": 0,
        "budget_max": 999_999_999,
    }
    # Turn saved preferences into an LLM-style intent without requiring a network call.
    categories = prefs.get("categories") or []
    category = "all"
    if any("መኪና" in str(c) or "car" in str(c).lower() for c in categories):
        category = "cars"
    elif any("ቤት" in str(c) or "house" in str(c).lower() or "property" in str(c).lower() for c in categories):
        category = "property"
    intent = {
        "category": category,
        "brand": None,
        "model": None,
        "price_max": prefs.get("budget_max"),
        "transmission": None,
    }

    conn = None
    scored: List[Dict[str, Any]] = []
    try:
        from models import get_db_connection
        conn = get_db_connection()
        cur = conn.cursor()

        # Source 1: user marketplace listings.
        try:
            cur.execute(
                "SELECT * FROM listings WHERE (status IS NULL OR LOWER(CAST(status AS TEXT)) NOT IN ('deleted','sold','rented','expired')) "
                "AND (UPPER(TRIM(COALESCE(req_type,''))) NOT IN ('BUY','RENT') OR COALESCE(req_type,'')='') "
                "ORDER BY id DESC LIMIT 500"
            )
            for row in (cur.fetchall() or []):
                d = _row_to_dict(cur, row)
                base = score_listing_for_user(d, prefs)
                hs = _hybrid_match_score(d, intent)
                if hs < 0:
                    continue
                price = _hybrid_price(d)
                bmin = _parse_price(prefs.get("budget_min"))
                bmax = _parse_price(prefs.get("budget_max"))
                if price > 0 and bmax > 0 and price > bmax:
                    continue
                if price > 0 and bmin > 0 and price < bmin:
                    continue
                scored.append(_normalize_hybrid_item(d, "listing", base + max(0, hs)))
        except Exception:
            pass

        # Source 2: Adika Clean Market / ethiopia_vehicles catalog.
        try:
            cur.execute("SELECT * FROM ethiopia_vehicles LIMIT 500")
            for row in (cur.fetchall() or []):
                d = _row_to_dict(cur, row)
                hs = _hybrid_match_score(d, intent)
                if hs < 0:
                    continue
                price = _hybrid_price(d)
                bmax = _parse_price(prefs.get("budget_max"))
                if price > 0 and bmax > 0 and bmax < 999_999_999 and price > bmax:
                    continue
                # Catalog rows receive a useful preference score even without a numeric price.
                scored.append(_normalize_hybrid_item(d, "clean_market", max(5, hs)))
        except Exception:
            pass
    except Exception as e:
        logger.error("fetch_for_you_feed hybrid: %s", e, exc_info=True)
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass

    scored.sort(key=lambda x: (-int(x.get("_score") or 0), 0 if x.get("source") == "listing" else 1, -(int(x.get("id") or 0) if str(x.get("id") or "").isdigit() else 0)))
    offset = max(0, (page - 1) * limit)
    items = scored[offset:offset + max(1, int(limit))]
    return {
        "success": True,
        "items": items,
        "listings": [x for x in items if x.get("source") == "listing"],
        "clean_market": [x for x in items if x.get("source") == "clean_market"],
        "page": page,
        "prefs": prefs,
        "has_more": len(scored) > offset + len(items),
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

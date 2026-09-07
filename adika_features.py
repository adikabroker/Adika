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


def _category_bucket(raw: Any) -> str:
    s = str(raw or "").lower().strip()
    if not s:
        return "other"
    if any(tok in s for tok in ("ቤት", "house", "home", "apartment", "property", "ቪላ", "አፓርታ", "መሬት", "land", "condo")):
        return "house"
    if any(tok in s for tok in ("መኪና", "car", "vehicle", "auto", "truck", "toyota", "hyundai", "ቶዮታ")):
        return "car"
    return "other"


def _first_image_url(item: Dict[str, Any]) -> str:
    """Same photo mapping used by Similar Items cards (manual posts + Telegram scrapes)."""
    extra = item.get("extra_data") or {}
    if isinstance(extra, str):
        try:
            extra = json.loads(extra)
        except Exception:
            extra = {}
    if not isinstance(extra, dict):
        extra = {}

    candidates: List[Any] = [
        item.get("image_url"),
        item.get("photo_url"),
        item.get("cover_url"),
        item.get("thumbnail"),
        item.get("photo_id"),
        item.get("photo_urls"),
        item.get("photos"),
        item.get("listing_photos"),
        extra.get("image_url"),
        extra.get("photo_url"),
        extra.get("photos"),
        extra.get("photo_urls"),
        extra.get("images"),
        extra.get("telegram_file_id"),
        extra.get("file_id"),
    ]
    for c in candidates:
        if not c:
            continue
        if isinstance(c, list) and c:
            first = c[0]
            if isinstance(first, dict):
                url = first.get("url") or first.get("src") or first.get("file_id") or ""
            else:
                url = str(first)
            if url:
                return str(url)
        if isinstance(c, dict):
            url = c.get("url") or c.get("src") or c.get("file_id") or ""
            if url:
                return str(url)
        s = str(c).strip()
        if s and s not in ("None", "null", "[]", "{}"):
            return s
    return ""


def normalize_listing_card(it: Dict[str, Any], source: str = "listing") -> Dict[str, Any]:
    """1:1 card fields matching Similar Items / recommendations payload."""
    extra = it.get("extra_data") or {}
    if isinstance(extra, str):
        try:
            extra = json.loads(extra)
        except Exception:
            extra = {}
    if not isinstance(extra, dict):
        extra = {}
    image_url = _first_image_url(it)
    created = it.get("created_at")
    if created and not isinstance(created, str):
        try:
            created = created.isoformat()
        except Exception:
            created = str(created)
    title = (
        it.get("title")
        or it.get("sub_category")
        or extra.get("title")
        or extra.get("brand")
        or extra.get("model")
        or it.get("main_category")
        or "ንብረት"
    )
    photo_urls = it.get("photo_urls") or it.get("photos") or extra.get("photo_urls") or extra.get("photos")
    if image_url and not photo_urls:
        photo_urls = [image_url]
    out = dict(it)
    out.update({
        "id": it.get("id"),
        "title": title,
        "main_category": it.get("main_category") or it.get("category") or extra.get("category"),
        "sub_category": it.get("sub_category") or extra.get("model") or extra.get("car_model"),
        "category": it.get("category") or it.get("main_category"),
        "price": it.get("price") or extra.get("price"),
        "image_url": image_url,
        "photo_urls": photo_urls or it.get("photo_id"),
        "listing_photos": it.get("photo_id") or photo_urls,
        "photos": photo_urls,
        "created_at": created or "",
        "extra_data": extra,
        "req_type": it.get("req_type"),
        "action_type": it.get("action_type"),
        "description": str(it.get("description") or extra.get("description") or "")[:400],
        "source": source,
        "target_type": source,
    })
    return out


def fetch_similar_listings(
    *,
    category: str = "",
    sub_category: str = "",
    price: Any = 0,
    exclude_id: Any = None,
    view_history: Optional[List[Dict[str, Any]]] = None,
    limit: int = 24,
) -> Tuple[List[Dict[str, Any]], str, str]:
    """
    Exact Similar Items / /api/recommendations query:
    model-focus → price-focus (±15%) → category → created_at DESC fallback.
    """
    from models import get_db_connection, is_postgres
    from collections import Counter

    history = list(view_history or [])
    like = "ILIKE" if is_postgres() else "LIKE"
    p = _ph()
    intent = "recent"
    intent_label = "የቅርብ ጊዜ ዝርዝሮች"

    prices = [_parse_price(h.get("price")) for h in history if h]
    prices = [x for x in prices if x > 0]
    if price:
        cur_p = _parse_price(price)
        if cur_p > 0:
            prices.append(cur_p)
    categories = [str(h.get("category") or "") for h in history if h and h.get("category")]
    if category:
        categories.insert(0, str(category))
    models = [str(h.get("model") or h.get("brand") or "").strip() for h in history if h]
    if sub_category:
        models.insert(0, str(sub_category).strip())
    models = [m for m in models if m]

    avg_price = sum(prices) / len(prices) if prices else _parse_price(price)
    price_focus = False
    model_focus = False
    if len(prices) >= 2:
        mn, mx = min(prices), max(prices)
        mid = (mn + mx) / 2 or 1
        if (mx - mn) / mid <= 0.15:
            price_focus = True
    mc = Counter([m.lower() for m in models])
    top_model = None
    if mc:
        top_model, cnt = mc.most_common(1)[0]
        if cnt >= 1 and sub_category:
            model_focus = True
        if cnt >= 2:
            model_focus = True
    target_cat = None
    if categories:
        target_cat = Counter(categories).most_common(1)[0][0]
    elif category:
        target_cat = category

    where = [
        "(status IS NULL OR LOWER(CAST(status AS TEXT)) NOT IN ('deleted','sold','rented','expired'))"
    ]
    params: List[Any] = []
    if exclude_id:
        where.append(f"id <> {p}")
        params.append(exclude_id)

    if model_focus and top_model:
        intent = "model"
        intent_label = "በተመሳሳይ ሞዴል/ብራንድ"
        where.append(
            f"(CAST(COALESCE(sub_category,'') AS TEXT) {like} {p} "
            f"OR CAST(COALESCE(description,'') AS TEXT) {like} {p} "
            f"OR CAST(COALESCE(extra_data,'') AS TEXT) {like} {p})"
        )
        params.extend([f"%{top_model}%"] * 3)
    elif price_focus and avg_price > 0:
        intent = "price"
        intent_label = "በተመሳሳይ የዋጋ ክልል"
        if target_cat:
            where.append(f"(main_category = {p} OR CAST(main_category AS TEXT) {like} {p})")
            params.extend([target_cat, f"%{target_cat}%"])
        lo = int(avg_price * 0.85)
        hi = int(avg_price * 1.15)
        try:
            if is_postgres():
                where.append(
                    f"(NULLIF(regexp_replace(CAST(COALESCE(price,'') AS TEXT), '[^0-9]', '', 'g'), '')::BIGINT "
                    f"BETWEEN {p} AND {p})"
                )
                params.extend([lo, hi])
        except Exception:
            pass
    elif target_cat:
        intent = "category"
        intent_label = "በተመሳሳይ ምድብ"
        where.append(f"(main_category = {p} OR CAST(main_category AS TEXT) {like} {p})")
        params.extend([target_cat, f"%{target_cat}%"])

    items: List[Dict[str, Any]] = []
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        where_sql = " AND ".join(where)
        try:
            cur.execute(
                f"SELECT * FROM listings WHERE {where_sql} ORDER BY created_at DESC, id DESC LIMIT {p}",
                list(params) + [max(40, limit * 3)],
            )
            rows = cur.fetchall() or []
        except Exception as qe:
            logger.warning("similar listings query: %s", qe)
            cur.execute(
                f"SELECT * FROM listings ORDER BY created_at DESC, id DESC LIMIT {p}",
                (max(24, limit),),
            )
            rows = cur.fetchall() or []
            intent = "recent"
            intent_label = "የቅርብ ጊዜ ዝርዝሮች"

        lo = avg_price * 0.65 if avg_price else 0
        hi = avg_price * 1.35 if avg_price else 0
        bucket = _category_bucket(target_cat or category)
        for row in rows:
            d = dict(row) if not isinstance(row, dict) else dict(row)
            if exclude_id and str(d.get("id")) == str(exclude_id):
                continue
            cat = d.get("main_category") or d.get("category") or ""
            if bucket in ("car", "house") and _category_bucket(cat) not in (bucket, "other"):
                continue
            pr = _parse_price(d.get("price"))
            if avg_price and lo and hi and pr:
                if intent == "price" and not (avg_price * 0.85 <= pr <= avg_price * 1.15 * 1.2):
                    continue
                if intent in ("category", "model") and not (lo <= pr <= hi * 1.25):
                    # keep some outside band for feed density
                    pass
            items.append(normalize_listing_card(d, "listing"))

        if len(items) < limit:
            try:
                cur.execute(
                    f"SELECT * FROM listings ORDER BY created_at DESC, id DESC LIMIT {p}",
                    (limit * 2,),
                )
                for row in cur.fetchall() or []:
                    d = dict(row) if not isinstance(row, dict) else dict(row)
                    if exclude_id and str(d.get("id")) == str(exclude_id):
                        continue
                    if any(str(x.get("id")) == str(d.get("id")) for x in items):
                        continue
                    items.append(normalize_listing_card(d, "listing"))
                    if len(items) >= limit:
                        break
            except Exception:
                pass
    except Exception as e:
        logger.error("fetch_similar_listings: %s", e, exc_info=True)
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass
    return items[:limit], intent, intent_label


def fetch_for_you_feed(user_id: int, limit: int = 24, page: int = 1) -> Dict[str, Any]:
    """
    Main FYP uses the same Similar Items / recommendations algorithm:
    category + model + ±15–35% price band, then created_at DESC fallback.
    Card fields (image_url, photo_urls, extra_data) match detail-page recos 1:1.
    """
    prefs = get_user_preferences(user_id) if user_id else {
        "categories": ["መኪና", "ቤት"],
        "budget_min": 0,
        "budget_max": 999999999,
    }
    cats = prefs.get("categories") or ["መኪና"]
    primary_cat = ""
    for c in cats:
        if c:
            primary_cat = str(c)
            break
    history: List[Dict[str, Any]] = []
    for c in cats:
        if c:
            history.append({
                "category": c,
                "price": prefs.get("budget_max") or prefs.get("budget_min") or 0,
                "model": "",
            })
    mid_price = 0
    bmin = _parse_price(prefs.get("budget_min"))
    bmax = _parse_price(prefs.get("budget_max"))
    if bmin and bmax and bmax < 999999999:
        mid_price = (bmin + bmax) / 2
    elif bmax and bmax < 999999999:
        mid_price = bmax * 0.85
    elif bmin:
        mid_price = bmin * 1.15

    pool_limit = max(limit * page, limit)
    items, intent, intent_label = fetch_similar_listings(
        category=primary_cat,
        sub_category="",
        price=mid_price,
        view_history=history,
        limit=pool_limit + limit,
    )
    # Score with existing pref scorer so budget still applies
    scored = []
    for d in items:
        sc = score_listing_for_user(d, prefs)
        price = _parse_price(d.get("price"))
        if price > 0 and bmax and bmax < 999999999 and not (bmin <= price <= bmax):
            # keep similar-band items even if slightly outside saved budget
            sc -= 2
        scored.append((sc, d))
    scored.sort(key=lambda x: (-x[0], str(x[1].get("created_at") or ""), -(x[1].get("id") or 0) if isinstance(x[1].get("id"), int) else 0))
    offset = max(0, (page - 1) * limit)
    slice_ = scored[offset : offset + limit]
    out_items = []
    for sc, d in slice_:
        d["_score"] = sc
        d["source"] = d.get("source") or "listing"
        d["target_type"] = d["source"]
        out_items.append(d)

    return {
        "success": True,
        "items": out_items,
        "listings": out_items,
        "clean_market": [],
        "page": page,
        "prefs": prefs,
        "intent": {"kind": intent, "label": intent_label, "category": primary_cat},
        "intent_label": intent_label,
        "has_more": len(scored) > offset + limit,
        "counts": {
            "total": len(out_items),
            "listing": len(out_items),
            "clean_market": 0,
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

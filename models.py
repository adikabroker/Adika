# ==============================================================================
# models.py — Database connection, schema, CRUD
# ==============================================================================
import json
import random
from typing import Optional, List, Dict, Any

import sqlite3
import psycopg2
from psycopg2.extras import RealDictCursor, Json

from config import DATABASE_URL, DB_FILE, logger, VIEW_BASELINE_MIN, VIEW_BASELINE_MAX
from config import SUPABASE_URL, SUPABASE_KEY, SUPABASE_BUCKET
import config as _app_config


_DB_BACKEND = "unknown"
LAST_BROKER_ERROR = ""
LAST_DB_ERROR = ""
LAST_BROKER_ERROR = ""


def _normalize_pg_url(url: str) -> str:
    """Normalize postgres URL and ensure SSL for Supabase / cloud hosts."""
    u = (url or "").strip().strip('"').strip("'")
    if u.startswith("postgres://"):
        u = u.replace("postgres://", "postgresql://", 1)
    # Supabase + Render: require SSL (IPv4 pooler still needs sslmode)
    if "sslmode=" not in u.lower():
        sep = "&" if "?" in u else "?"
        u = f"{u}{sep}sslmode=require"
    return u


def get_db_connection():
    """
    Hybrid connection:
      1) PostgreSQL via DATABASE_URL (Supabase pooler 6543 or direct 5432) + SSL
      2) Fallback SQLite if PG unavailable
    """
    global _DB_BACKEND
    if DATABASE_URL:
        try:
            cleaned = _normalize_pg_url(DATABASE_URL)
            # sslmode in URL is enough for psycopg2; also pass sslmode for safety
            conn = psycopg2.connect(
                cleaned,
                cursor_factory=RealDictCursor,
                connect_timeout=15,
            )
            conn.autocommit = True
            _DB_BACKEND = "postgres"
            try:
                _app_config.DB_BACKEND = "postgres"
            except Exception:
                pass
            return conn
        except Exception as e:
            logger.error(f"PostgreSQL connection failed ({e}); falling back to SQLite")
    # SQLite fallback
    conn = sqlite3.connect(DB_FILE, check_same_thread=False, timeout=30)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("PRAGMA journal_mode=WAL;")
    except Exception:
        pass
    _DB_BACKEND = "sqlite"
    try:
        _app_config.DB_BACKEND = "sqlite"
    except Exception:
        pass
    return conn


def get_placeholder():
    if _DB_BACKEND == "postgres":
        return "%s"
    if _DB_BACKEND == "sqlite":
        return "?"
    return "%s" if DATABASE_URL else "?"


def is_postgres() -> bool:
    return _DB_BACKEND == "postgres"


def sql_like_op() -> str:
    return "ILIKE" if is_postgres() else "LIKE"






def init_db():
    conn = None
    try:
        conn = get_db_connection()
        if _DB_BACKEND == "postgres":
            logger.info("Successfully connected to Supabase PostgreSQL Pooler")
            logger.info("Connected to PostgreSQL Database")
        else:
            logger.warning("Using SQLite fallback (temporary — set DATABASE_URL to Supabase pooler port 6543)")
        cursor = conn.cursor()
        if _DB_BACKEND == "postgres":
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS listings (
                    id SERIAL PRIMARY KEY,
                    user_chat_id BIGINT NOT NULL,
                    user_name TEXT,
                    req_type TEXT NOT NULL,
                    main_category TEXT NOT NULL,
                    sub_category TEXT,
                    action_type TEXT,
                    property_type TEXT,
                    description TEXT NOT NULL,
                    price TEXT,
                    phone TEXT,
                    photo_id TEXT,
                    extra_data JSONB DEFAULT '{}',
                    status TEXT DEFAULT 'pending',
                    view_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS brokers (
                    id SERIAL PRIMARY KEY,
                    chat_id BIGINT NOT NULL UNIQUE,
                    full_name TEXT NOT NULL,
                    phone TEXT NOT NULL,
                    role_type TEXT NOT NULL,
                    national_id_photo TEXT,
                    sub_city TEXT NOT NULL,
                    rating REAL DEFAULT 5.0,
                    total_ratings INT DEFAULT 0,
                    notification_prefs JSONB DEFAULT '{"car": true, "house": true, "price_min": 0, "price_max": 999999999, "enabled": true}',
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS ratings (
                    id SERIAL PRIMARY KEY,
                    broker_chat_id BIGINT NOT NULL,
                    user_chat_id BIGINT NOT NULL,
                    stars INT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS broker_offers (
                    id SERIAL PRIMARY KEY,
                    request_id INTEGER NOT NULL,
                    broker_id BIGINT NOT NULL,
                    description TEXT,
                    photo_id TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS search_alerts (
                    id SERIAL PRIMARY KEY,
                    user_chat_id BIGINT NOT NULL,
                    main_category TEXT NOT NULL,
                    budget_min TEXT,
                    budget_max TEXT,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS listing_photos (
                    id SERIAL PRIMARY KEY,
                    listing_id INTEGER NOT NULL REFERENCES listings(id) ON DELETE CASCADE,
                    photo_id TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
        else:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS listings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_chat_id INTEGER NOT NULL,
                    user_name TEXT,
                    req_type TEXT NOT NULL,
                    main_category TEXT NOT NULL,
                    sub_category TEXT,
                    action_type TEXT,
                    property_type TEXT,
                    description TEXT NOT NULL,
                    price TEXT,
                    phone TEXT,
                    photo_id TEXT,
                    extra_data TEXT DEFAULT '{}',
                    status TEXT DEFAULT 'pending',
                    view_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS brokers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chat_id INTEGER NOT NULL UNIQUE,
                    full_name TEXT NOT NULL,
                    phone TEXT NOT NULL,
                    role_type TEXT NOT NULL,
                    national_id_photo TEXT,
                    sub_city TEXT NOT NULL,
                    rating REAL DEFAULT 5.0,
                    total_ratings INTEGER DEFAULT 0,
                    notification_prefs TEXT DEFAULT '{"car": true, "house": true, "price_min": 0, "price_max": 999999999, "enabled": true}',
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ratings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    broker_chat_id INTEGER NOT NULL,
                    user_chat_id INTEGER NOT NULL,
                    stars INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS broker_offers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    request_id INTEGER NOT NULL,
                    broker_id INTEGER NOT NULL,
                    description TEXT,
                    photo_id TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS search_alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_chat_id INTEGER NOT NULL,
                    main_category TEXT NOT NULL,
                    budget_min TEXT,
                    budget_max TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS listing_photos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    listing_id INTEGER NOT NULL,
                    photo_id TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.commit()
        try:
            if is_postgres():
                cursor.execute("ALTER TABLE listings ADD COLUMN IF NOT EXISTS extra_data JSONB DEFAULT '{}';")
                cursor.execute("ALTER TABLE listings ADD COLUMN IF NOT EXISTS view_count INTEGER DEFAULT 0;")
            else:
                try:
                    cursor.execute("ALTER TABLE listings ADD COLUMN extra_data TEXT DEFAULT '{}';")
                except:
                    pass
                try:
                    cursor.execute("ALTER TABLE listings ADD COLUMN view_count INTEGER DEFAULT 0;")
                except:
                    pass
            if not is_postgres():
                conn.commit()
        except Exception as alter_err:
            logger.warning(f"ALTER TABLE warning: {alter_err}")
        logger.info("✅ Adika Database initialized successfully")
    except Exception as e:
        logger.error(f"❌ Database initialization error: {e}")
        if conn and not DATABASE_URL:
            conn.rollback()
    finally:
        if conn:
            conn.close()


# ==============================================================================
# 4. DATABASE OPERATIONS
# ==============================================================================


def ensure_core_tables():
    """Create minimal listings/brokers tables if missing (safe to call often)."""
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        if is_postgres():
            cur.execute("""
                CREATE TABLE IF NOT EXISTS listings (
                    id SERIAL PRIMARY KEY,
                    user_chat_id BIGINT NOT NULL,
                    user_name TEXT,
                    req_type TEXT NOT NULL,
                    main_category TEXT NOT NULL,
                    sub_category TEXT,
                    action_type TEXT,
                    property_type TEXT,
                    description TEXT NOT NULL DEFAULT '',
                    price TEXT,
                    phone TEXT,
                    photo_id TEXT,
                    extra_data JSONB DEFAULT '{}',
                    status TEXT DEFAULT 'ONLINE',
                    view_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS listing_photos (
                    id SERIAL PRIMARY KEY,
                    listing_id INTEGER NOT NULL,
                    photo_id TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS brokers (
                    id SERIAL PRIMARY KEY,
                    chat_id BIGINT UNIQUE,
                    full_name TEXT,
                    phone TEXT,
                    username TEXT,
                    sub_city TEXT,
                    specialty TEXT,
                    status TEXT DEFAULT 'ONLINE',
                    notification_prefs JSONB DEFAULT '{"car":true,"house":true,"enabled":true}',
                    rating REAL DEFAULT 5.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
        else:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS listings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_chat_id INTEGER NOT NULL,
                    user_name TEXT,
                    req_type TEXT NOT NULL,
                    main_category TEXT NOT NULL,
                    sub_category TEXT,
                    action_type TEXT,
                    property_type TEXT,
                    description TEXT NOT NULL DEFAULT '',
                    price TEXT,
                    phone TEXT,
                    photo_id TEXT,
                    extra_data TEXT DEFAULT '{}',
                    status TEXT DEFAULT 'ONLINE',
                    view_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS listing_photos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    listing_id INTEGER NOT NULL,
                    photo_id TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS brokers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chat_id INTEGER UNIQUE,
                    full_name TEXT,
                    phone TEXT,
                    username TEXT,
                    sub_city TEXT,
                    specialty TEXT,
                    status TEXT DEFAULT 'ONLINE',
                    notification_prefs TEXT DEFAULT '{}',
                    rating REAL DEFAULT 5.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
        logger.info("ensure_core_tables ok backend=%s", _DB_BACKEND)
    except Exception as e:
        logger.error("ensure_core_tables: %s", e)
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass



def ensure_listings_columns():
    """Add any missing columns the app expects (Supabase may have older schema)."""
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        if is_postgres():
            alters = [
                "ALTER TABLE listings ADD COLUMN IF NOT EXISTS user_chat_id BIGINT",
                "ALTER TABLE listings ADD COLUMN IF NOT EXISTS user_name TEXT",
                "ALTER TABLE listings ADD COLUMN IF NOT EXISTS req_type TEXT",
                "ALTER TABLE listings ADD COLUMN IF NOT EXISTS main_category TEXT",
                "ALTER TABLE listings ADD COLUMN IF NOT EXISTS category TEXT",
                "ALTER TABLE listings ADD COLUMN IF NOT EXISTS sub_category TEXT",
                "ALTER TABLE listings ADD COLUMN IF NOT EXISTS action_type TEXT",
                "ALTER TABLE listings ADD COLUMN IF NOT EXISTS property_type TEXT",
                "ALTER TABLE listings ADD COLUMN IF NOT EXISTS description TEXT DEFAULT ''",
                "ALTER TABLE listings ADD COLUMN IF NOT EXISTS price TEXT",
                "ALTER TABLE listings ADD COLUMN IF NOT EXISTS phone TEXT",
                "ALTER TABLE listings ADD COLUMN IF NOT EXISTS photo_id TEXT",
                "ALTER TABLE listings ADD COLUMN IF NOT EXISTS extra_data JSONB DEFAULT '{}'::jsonb",
                "ALTER TABLE listings ADD COLUMN IF NOT EXISTS status TEXT DEFAULT 'ONLINE'",
                "ALTER TABLE listings ADD COLUMN IF NOT EXISTS view_count INTEGER DEFAULT 0",
                "ALTER TABLE listings ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
            ]
            for sql in alters:
                try:
                    cur.execute(sql)
                except Exception as e:
                    logger.debug("alter skip: %s (%s)", sql, e)
            # Backfill main_category from category if needed
            try:
                cur.execute("""
                    UPDATE listings
                    SET main_category = category
                    WHERE (main_category IS NULL OR main_category = '')
                      AND category IS NOT NULL AND category <> ''
                """)
            except Exception:
                pass
            try:
                cur.execute("""
                    UPDATE listings
                    SET category = main_category
                    WHERE (category IS NULL OR category = '')
                      AND main_category IS NOT NULL AND main_category <> ''
                """)
            except Exception:
                pass
        else:
            # SQLite: try add columns (ignore if exist)
            for col, typedef in [
                ("main_category", "TEXT"),
                ("category", "TEXT"),
                ("sub_category", "TEXT"),
                ("action_type", "TEXT"),
                ("property_type", "TEXT"),
                ("extra_data", "TEXT DEFAULT '{}'"),
                ("view_count", "INTEGER DEFAULT 0"),
                ("status", "TEXT DEFAULT 'ONLINE'"),
                ("user_chat_id", "INTEGER"),
                ("user_name", "TEXT"),
                ("req_type", "TEXT"),
                ("description", "TEXT"),
                ("price", "TEXT"),
                ("phone", "TEXT"),
                ("photo_id", "TEXT"),
            ]:
                try:
                    cur.execute(f"ALTER TABLE listings ADD COLUMN {col} {typedef}")
                except Exception:
                    pass
            conn.commit()
        logger.info("ensure_listings_columns done backend=%s", _DB_BACKEND)
    except Exception as e:
        logger.error("ensure_listings_columns: %s", e)
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass


def get_listings_column_set():
    """Return set of column names on listings table."""
    cols = set()
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        if is_postgres():
            cur.execute("""
                SELECT column_name FROM information_schema.columns
                WHERE table_schema = 'public' AND table_name = 'listings'
            """)
            for row in cur.fetchall():
                name = row["column_name"] if isinstance(row, dict) else row[0]
                cols.add(str(name).lower())
        else:
            cur.execute("PRAGMA table_info(listings)")
            for row in cur.fetchall():
                # cid, name, type, ...
                if isinstance(row, dict):
                    cols.add(str(row.get("name", "")).lower())
                else:
                    cols.add(str(row[1]).lower())
    except Exception as e:
        logger.warning("get_listings_column_set: %s", e)
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass
    return cols



def ensure_user_for_listing(cursor, user_id, user_name="Adika User", phone=""):
    """Upsert a minimal users row so listings.user_id FK succeeds on Supabase.
    Returns True if user exists or was created; False otherwise.
    """
    if not user_id:
        return False
    try:
        uid = int(user_id)
    except Exception:
        return False
    if uid <= 0:
        return False
    p = get_placeholder()
    try:
        cursor.execute(f"SELECT 1 FROM users WHERE id = {p} LIMIT 1", (uid,))
        if cursor.fetchone():
            return True
    except Exception as e:
        logger.warning("users select: %s", e)
        return False
    name = (str(user_name) or "Adika User")[:120]
    phone = (str(phone) or "")[:40]
    attempts = []
    if is_postgres():
        attempts = [
            (f"INSERT INTO users (id) VALUES ({p}) ON CONFLICT (id) DO NOTHING", (uid,)),
            (f"INSERT INTO users (id) VALUES ({p}) ON CONFLICT DO NOTHING", (uid,)),
            (f"INSERT INTO users (id, full_name) VALUES ({p}, {p}) ON CONFLICT DO NOTHING", (uid, name)),
            (f"INSERT INTO users (id, name) VALUES ({p}, {p}) ON CONFLICT DO NOTHING", (uid, name)),
            (f"INSERT INTO users (id, phone) VALUES ({p}, {p}) ON CONFLICT DO NOTHING", (uid, phone or "N/A")),
            (f"INSERT INTO users (id, full_name, phone) VALUES ({p}, {p}, {p}) ON CONFLICT DO NOTHING", (uid, name, phone or "N/A")),
            (f"INSERT INTO users (id, telegram_id) VALUES ({p}, {p}) ON CONFLICT DO NOTHING", (uid, uid)),
            (f"INSERT INTO users (id, chat_id) VALUES ({p}, {p}) ON CONFLICT DO NOTHING", (uid, uid)),
            # Last: plain insert without ON CONFLICT
            (f"INSERT INTO users (id) VALUES ({p})", (uid,)),
        ]
    else:
        attempts = [
            (f"INSERT OR IGNORE INTO users (id) VALUES ({p})", (uid,)),
            (f"INSERT OR IGNORE INTO users (id, full_name) VALUES ({p}, {p})", (uid, name)),
            (f"INSERT OR IGNORE INTO users (id, name) VALUES ({p}, {p})", (uid, name)),
        ]
    for sql, params in attempts:
        try:
            cursor.execute(sql, params)
            try:
                cursor.connection.commit()
            except Exception:
                pass
            logger.info("ensure_user_for_listing ok id=%s", uid)
            return True
        except Exception as e:
            logger.warning("ensure_user attempt failed: %s", e)
            try:
                cursor.connection.rollback()
            except Exception:
                pass
    return False


def add_listing(user_chat_id, user_name, req_type, main_category, sub_category,
                action_type, property_type, description, price=None, phone=None, 
                photo_id=None, extra_data=None, photos=None):
    """Insert listing. Returns id or None. Sets LAST_DB_ERROR on failure."""
    global LAST_DB_ERROR
    LAST_DB_ERROR = ""
    conn = None
    try:
        try:
            ensure_core_tables()
            ensure_listings_columns()
        except Exception as _ee:
            logger.warning("ensure before insert: %s", _ee)
        conn = get_db_connection()
        cursor = conn.cursor()
        p = get_placeholder()
        existing_cols = set()
        try:
            if is_postgres():
                cursor.execute("""
                    SELECT column_name FROM information_schema.columns
                    WHERE table_schema = 'public' AND table_name = 'listings'
                """)
                for row in cursor.fetchall():
                    name = row["column_name"] if isinstance(row, dict) else row[0]
                    existing_cols.add(str(name).lower())
            else:
                cursor.execute("PRAGMA table_info(listings)")
                for row in cursor.fetchall():
                    if isinstance(row, dict):
                        existing_cols.add(str(row.get("name", "")).lower())
                    else:
                        existing_cols.add(str(row[1]).lower())
        except Exception as ce:
            logger.warning("column introspect: %s", ce)

        if extra_data is None:
            extra_data = {}
        if isinstance(extra_data, str):
            try:
                extra_data = json.loads(extra_data)
            except Exception:
                extra_data = {"raw": extra_data}

        user_chat_id = int(user_chat_id) if user_chat_id else 0
        user_name = str(user_name or "User")[:200]
        req_type = str(req_type or "BUY").upper()
        main_category = str(main_category or (extra_data.get("category") if isinstance(extra_data, dict) else None) or (extra_data.get("car_type") if isinstance(extra_data, dict) else None) or "መኪና")[:100]
        if not main_category.strip():
            main_category = "መኪና"
        # Normalize EN labels → Amharic marketplace tabs
        _mc = main_category.strip().lower()
        if _mc in ("car", "cars", "vehicle", "vehicles", "auto"):
            main_category = "መኪና"
        elif _mc in ("house", "home", "property", "realestate", "real_estate"):
            main_category = "ቤት"
        sub_category = str(sub_category or "")[:100]
        action_type = str(action_type or "")[:100]
        property_type = str(property_type or "")[:100]
        description = str(description or "")[:8000]
        price = str(price or "")[:100]
        phone = str(phone or "")[:50]
        photo_id = str(photo_id) if photo_id else None
        import random as _rnd
        baseline_views = int(_rnd.randint(35, 90))

        photo_list = []
        if photos:
            for ph in list(photos)[:3]:
                s = str(ph)
                if len(s) > 300000:
                    s = s[:300000]
                photo_list.append(s)

        # Build extra_data param safely
        extra_text = json.dumps(extra_data, ensure_ascii=False)
        if is_postgres():
            try:
                from psycopg2.extras import Json as PgJson
                extra_param = PgJson(extra_data)
            except Exception:
                extra_param = extra_text
        else:
            extra_param = extra_text

        logger.info(
            "📝 Insert listing user=%s type=%s cat=%s backend=%s photos=%s",
            user_chat_id, req_type, main_category, _DB_BACKEND, len(photo_list),
        )

        def _do_insert(with_extra=True, with_views=True):
            # Never allow NULL for NOT NULL columns on Supabase listings
            cat_val = (main_category or sub_category or "መኪና").strip() or "መኪና"
            req_val = (req_type or "SELL").strip().upper() or "SELL"
            desc_val = description if description is not None else ""
            if not str(desc_val).strip():
                desc_val = cat_val

            candidates = [
                ("user_chat_id", user_chat_id),
                # Do NOT set user_id by default — Supabase listings_user_id_fkey requires users row.
                # user_chat_id is the marketplace owner key and has no FK in production.
                ("user_name", user_name or "User"),
                ("req_type", req_val),
                ("main_category", cat_val),
                ("category", cat_val),
                ("sub_category", sub_category or cat_val),
                ("action_type", action_type or ""),
                ("property_type", property_type or ""),
                ("description", desc_val),
                ("price", price or ""),
                ("phone", phone or ""),
                ("photo_id", photo_id),
                ("status", "ONLINE"),
            ]
            if with_extra:
                candidates.append(("extra_data", extra_param))
            if with_views:
                candidates.append(("view_count", baseline_views))
            # Only attach user_id when users row is guaranteed (avoids listings_user_id_fkey)
            if _user_ready and user_chat_id:
                candidates.append(("user_id", user_chat_id))

            cols, vals = [], []
            for col, val in candidates:
                cl = col.lower()
                if existing_cols and cl not in existing_cols:
                    continue
                if val is None and cl in (
                    "category", "main_category", "req_type", "description",
                    "user_name", "status", "sub_category", "action_type",
                    "property_type", "price", "phone",
                ):
                    if cl in ("category", "main_category", "sub_category"):
                        val = cat_val
                    elif cl == "req_type":
                        val = req_val
                    elif cl == "description":
                        val = desc_val
                    else:
                        val = ""
                cols.append(col)
                vals.append(val)

            if not existing_cols:
                cols = [c for c, _ in candidates]
                vals = [v if v is not None else "" for _, v in candidates]

            force_map = {
                "category": cat_val,
                "main_category": cat_val,
                "req_type": req_val,
                "description": desc_val,
            }
            lower_cols = [c.lower() for c in cols]
            for fcol, fval in force_map.items():
                if existing_cols and fcol not in existing_cols:
                    # still force category/main_category even if introspect missed them
                    if fcol in ("category", "main_category") and fcol not in lower_cols:
                        cols.append(fcol)
                        vals.append(fval)
                        lower_cols.append(fcol)
                    continue
                if fcol not in lower_cols:
                    cols.append(fcol)
                    vals.append(fval)
                    lower_cols.append(fcol)
                else:
                    for i, c in enumerate(cols):
                        if c.lower() == fcol and (vals[i] is None or str(vals[i]).strip() == ""):
                            vals[i] = fval

            if not cols:
                raise RuntimeError("No matching columns on listings table")

            for i, c in enumerate(cols):
                if c.lower() in ("category", "main_category") and not vals[i]:
                    vals[i] = cat_val

            ph = ", ".join([p] * len(vals))
            colsql = ", ".join(cols)
            q = f"INSERT INTO listings ({colsql}) VALUES ({ph})"
            logger.info("INSERT cols=%s cat=%s", cols, cat_val)
            if is_postgres():
                cursor.execute(q + " RETURNING id", tuple(vals))
                row = cursor.fetchone()
                if not row:
                    return None
                return row["id"] if isinstance(row, dict) else row[0]
            cursor.execute(q, tuple(vals))
            return cursor.lastrowid


        req_id = None
        last_err = None
        for with_extra, with_views in ((True, True), (False, True), (False, False)):
            try:
                req_id = _do_insert(with_extra=with_extra, with_views=with_views)
                if req_id:
                    break
            except Exception as ie:
                last_err = ie
                logger.warning("insert attempt failed (extra=%s views=%s): %s", with_extra, with_views, ie)
                try:
                    conn.rollback()
                except Exception:
                    pass
                # FK on user_id: drop user_id from candidates and retry once
                err_s = str(ie).lower()
                if "user_id" in err_s and ("foreign key" in err_s or "fkey" in err_s):
                    try:
                        ensure_user_for_listing(cursor, user_chat_id, user_name, phone)
                        req_id = _do_insert(with_extra=with_extra, with_views=with_views)
                        if req_id:
                            break
                    except Exception as ie2:
                        last_err = ie2
                        try:
                            conn.rollback()
                        except Exception:
                            pass
                        # Last resort: remove user_id from existing_cols so insert skips it
                        existing_cols.discard("user_id")
                        try:
                            req_id = _do_insert(with_extra=False, with_views=False)
                            if req_id:
                                break
                        except Exception as ie3:
                            last_err = ie3
                            try:
                                conn.rollback()
                            except Exception:
                                pass

        if not req_id:
            LAST_DB_ERROR = str(last_err or "insert returned no id")
            logger.error("❌ Add listing failed: %s", LAST_DB_ERROR)
            return None

        if photo_list:
            for photo_str in photo_list:
                try:
                    cursor.execute(
                        f"INSERT INTO listing_photos (listing_id, photo_id) VALUES ({p}, {p})",
                        (req_id, photo_str),
                    )
                except Exception as pe:
                    logger.error("photo save failed: %s", pe)

        try:
            if not is_postgres():
                conn.commit()
            else:
                try:
                    conn.commit()
                except Exception:
                    pass
        except Exception as ce:
            logger.warning("commit: %s", ce)

        logger.info("✅ Listing added → #ADK-%s", req_id)
        return req_id
    except Exception as e:
        LAST_DB_ERROR = str(e)
        logger.error("❌ Add listing error: %s", e, exc_info=True)
        if conn:
            try:
                if not is_postgres():
                    conn.rollback()
            except Exception:
                pass
        return None
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass



def get_listing_by_id(listing_id: int):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        p = get_placeholder()
        cursor.execute(f"SELECT * FROM listings WHERE id = {p}", (listing_id,))
        row = cursor.fetchone()
        if not row:
            return None
        result = dict(row) if isinstance(row, dict) else dict(zip([c[0] for c in cursor.description], row))
        if 'extra_data' in result and isinstance(result['extra_data'], str):
            try:
                result['extra_data'] = json.loads(result['extra_data'])
            except:
                result['extra_data'] = {}
        try:
            cursor.execute(f"SELECT photo_id FROM listing_photos WHERE listing_id = {p}", (listing_id,))
            photo_rows = cursor.fetchall()
            result['photos'] = [dict(r)['photo_id'] if isinstance(r, dict) else r[0] for r in photo_rows]
        except Exception as e:
            logger.warning(f"Could not load photos for listing {listing_id}: {e}")
            result['photos'] = []
        return result
    except Exception as e:
        logger.error(f"Get listing by id error: {e}")
        return None
    finally:
        if conn:
            try:
                conn.close()
            except:
                pass

def get_listings_by_category(limit=10, offset=0, req_type=None):
    return get_listings_by_category_ordered(limit=limit, offset=offset, req_type=req_type, order="DESC")

def get_listings_by_category_ordered(limit=20, offset=0, req_type=None, order="DESC"):
    """Same filter as Mini App /api/explorer/listings: exclude deleted/sold/rented/expired."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        p = get_placeholder()
        order_sql = "ASC" if str(order).upper() == "ASC" else "DESC"
        where = [
            "(status IS NULL OR status NOT IN ('deleted', 'sold', 'rented', 'expired'))",
        ]
        params = []
        if req_type:
            where.append(f"UPPER(TRIM(req_type)) = UPPER(TRIM({p}))")
            params.append(str(req_type).strip())
        where_sql = " AND ".join(where)
        params.extend([int(limit), int(offset)])
        query = f"""
            SELECT * FROM listings
            WHERE {where_sql}
            ORDER BY COALESCE(created_at, CURRENT_TIMESTAMP) {order_sql}, id {order_sql}
            LIMIT {p} OFFSET {p}
        """
        if not is_postgres():
            # SQLite: no CURRENT_TIMESTAMP in COALESCE the same way for missing
            query = f"""
                SELECT * FROM listings
                WHERE {where_sql}
                ORDER BY id {order_sql}
                LIMIT {p} OFFSET {p}
            """
        cursor.execute(query, params)
        rows = cursor.fetchall()
        results = []
        for row in rows:
            item = dict(row) if isinstance(row, dict) else dict(zip([c[0] for c in cursor.description], row))
            if "extra_data" in item and isinstance(item["extra_data"], str):
                try:
                    item["extra_data"] = json.loads(item["extra_data"])
                except Exception:
                    item["extra_data"] = {}
            results.append(item)
        logger.info(f"get_listings_by_category_ordered type={req_type} → {len(results)} rows")
        return results
    except Exception as e:
        logger.error(f"get_listings_by_category_ordered error: {e}", exc_info=True)
        return []
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass


def count_listings(req_type=None):
    """Count active listings — aligned with Mini App filters."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        p = get_placeholder()
        where = [
            "(status IS NULL OR status NOT IN ('deleted', 'sold', 'rented', 'expired'))",
        ]
        params = []
        if req_type:
            where.append(f"UPPER(TRIM(req_type)) = UPPER(TRIM({p}))")
            params.append(str(req_type).strip())
        where_sql = " AND ".join(where)
        cursor.execute(f"SELECT COUNT(*) as cnt FROM listings WHERE {where_sql}", params)
        row = cursor.fetchone()
        if isinstance(row, dict):
            return int(row.get("cnt") or 0)
        return int(row[0]) if row else 0
    except Exception as e:
        logger.error(f"Count listings error: {e}", exc_info=True)
        return 0
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass


def update_listing_status(req_id: int, status: str) -> bool:
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        p = get_placeholder()
        cursor.execute(f"UPDATE listings SET status = {p} WHERE id = {p}", (status, req_id))
        conn.commit()
        logger.info(f"✅ Listing {req_id} status updated to {status}")
        return True
    except Exception as e:
        logger.error(f"Update listing error: {e}")
        return False
    finally:
        if conn:
            try:
                conn.close()
            except:
                pass

def get_public_marketplace_items(limit: int = 20, offset: int = 0):
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            return []
        cur = conn.cursor()
        p = get_placeholder()
        if is_postgres():
            cur.execute("""
                SELECT * FROM listings 
                WHERE UPPER(req_type) = 'SELL'
                  AND status != 'deleted'
                ORDER BY created_at DESC NULLS LAST
                LIMIT %s OFFSET %s
            """, (limit, offset))
            rows = cur.fetchall()
            result = [dict(row) for row in rows]
        else:
            cur.execute("""
                SELECT * FROM listings 
                WHERE UPPER(req_type) = 'SELL'
                  AND status != 'deleted'
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            """, (limit, offset))
            rows = cur.fetchall()
            columns = [desc[0] for desc in cur.description]
            result = [dict(zip(columns, row)) for row in rows]
        for item in result:
            if 'extra_data' in item and isinstance(item['extra_data'], str):
                try:
                    item['extra_data'] = json.loads(item['extra_data'])
                except:
                    item['extra_data'] = {}
        return result
    except Exception as e:
        logger.error(f"get_public_marketplace_items error: {e}", exc_info=True)
        return []
    finally:
        if conn:
            try:
                conn.close()
            except:
                pass


# ========== BROKER OPERATIONS ==========


def upload_broker_document(file_bytes: bytes, filename: str, content_type: str = "image/jpeg") -> str:
    """
    Upload bytes to Supabase Storage bucket. Returns public URL or empty string.
    Requires SUPABASE_URL + SUPABASE_KEY env vars and bucket 'broker-documents'.
    """
    if not SUPABASE_URL or not SUPABASE_KEY:
        logger.warning("Supabase Storage not configured (SUPABASE_URL/KEY missing)")
        return ""
    if not file_bytes:
        return ""
    try:
        import urllib.request
        import urllib.error
        path = filename.lstrip("/")
        url = f"{SUPABASE_URL}/storage/v1/object/{SUPABASE_BUCKET}/{path}"
        req = urllib.request.Request(
            url,
            data=file_bytes,
            method="POST",
            headers={
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "apikey": SUPABASE_KEY,
                "Content-Type": content_type,
                "x-upsert": "true",
            },
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            resp.read()
        public_url = f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_BUCKET}/{path}"
        logger.info("Supabase upload ok: %s", public_url)
        return public_url
    except Exception as e:
        logger.error("Supabase storage upload failed: %s", e, exc_info=True)
        return ""


def add_broker(
    chat_id,
    full_name,
    phone="",
    role_type="ደላላ",
    national_id_photo=None,
    sub_city="",
    specialty="",
    username="",
    fayda_photo_id=None,
    fayda_id_url=None,
) -> Optional[int]:
    """
    Insert/update broker.
    CRITICAL: Supabase schema uses user_chat_id (NOT NULL / PK-like).
    Always write user_chat_id AND chat_id with the Telegram user id.
    is_approved is Python bool False.
    """
    global LAST_BROKER_ERROR
    LAST_BROKER_ERROR = ""
    conn = None
    try:
        # Never null — Telegram user id is required
        if chat_id is None:
            LAST_BROKER_ERROR = "chat_id is None"
            logger.error(LAST_BROKER_ERROR)
            return None
        chat_id = int(chat_id)
        if chat_id <= 0:
            LAST_BROKER_ERROR = f"invalid chat_id={chat_id}"
            logger.error(LAST_BROKER_ERROR)
            return None

        full_name = (str(full_name).strip() if full_name else "User")[:200]
        phone = (str(phone).strip() if phone else "")[:40] or "N/A"
        username = (str(username).strip() if username else "")[:120]
        role_type = (str(role_type).strip() if role_type else "ደላላ")[:80]
        sub_city = (str(sub_city).strip() if sub_city else "")[:80] or "አዲስ አበባ"
        specialty = (str(specialty).strip() if specialty else role_type)[:120] or "ደላላ"
        working_area = sub_city  # Supabase NOT NULL column alias
        photo = str(national_id_photo) if national_id_photo else None
        fayda = str(fayda_photo_id) if fayda_photo_id else photo
        fayda_url = ""
        if fayda_id_url and str(fayda_id_url).startswith("http"):
            fayda_url = str(fayda_id_url).strip()
        elif fayda and str(fayda).startswith("http"):
            fayda_url = str(fayda).strip()

        conn = get_db_connection()
        cur = conn.cursor()
        p = get_placeholder()
        pg = is_postgres()

        # Migrations including user_chat_id
        try:
            if pg:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS brokers (
                        id SERIAL PRIMARY KEY,
                        user_chat_id BIGINT,
                        chat_id BIGINT,
                        full_name TEXT,
                        phone TEXT,
                        phone_number TEXT,
                        username TEXT,
                        sub_city TEXT,
                        specialty TEXT,
                        status TEXT DEFAULT 'ONLINE',
                        is_approved BOOLEAN DEFAULT FALSE,
                        is_online BOOLEAN DEFAULT TRUE,
                        fayda_id_url TEXT,
                        fayda_photo_id TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                for stmt in (
                    "ALTER TABLE brokers ADD COLUMN IF NOT EXISTS user_chat_id BIGINT",
                    "ALTER TABLE brokers ADD COLUMN IF NOT EXISTS chat_id BIGINT",
                    "ALTER TABLE brokers ADD COLUMN IF NOT EXISTS full_name TEXT",
                    "ALTER TABLE brokers ADD COLUMN IF NOT EXISTS phone TEXT",
                    "ALTER TABLE brokers ADD COLUMN IF NOT EXISTS phone_number TEXT",
                    "ALTER TABLE brokers ADD COLUMN IF NOT EXISTS username TEXT",
                    "ALTER TABLE brokers ADD COLUMN IF NOT EXISTS sub_city TEXT",
                    "ALTER TABLE brokers ADD COLUMN IF NOT EXISTS working_area TEXT",
                    "ALTER TABLE brokers ADD COLUMN IF NOT EXISTS specialty TEXT",
                    "ALTER TABLE brokers ADD COLUMN IF NOT EXISTS status TEXT DEFAULT 'ONLINE'",
                    "ALTER TABLE brokers ADD COLUMN IF NOT EXISTS is_approved BOOLEAN DEFAULT FALSE",
                    "ALTER TABLE brokers ADD COLUMN IF NOT EXISTS is_online BOOLEAN DEFAULT TRUE",
                    "ALTER TABLE brokers ADD COLUMN IF NOT EXISTS fayda_id_url TEXT",
                    "ALTER TABLE brokers ADD COLUMN IF NOT EXISTS fayda_photo_id TEXT",
                    "ALTER TABLE brokers ADD COLUMN IF NOT EXISTS national_id_photo TEXT",
                    "ALTER TABLE brokers ADD COLUMN IF NOT EXISTS role_type TEXT",
                ):
                    try:
                        cur.execute(stmt)
                    except Exception:
                        pass
            else:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS brokers (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_chat_id INTEGER,
                        chat_id INTEGER,
                        full_name TEXT,
                        phone TEXT,
                        phone_number TEXT,
                        username TEXT,
                        sub_city TEXT,
                        specialty TEXT,
                        status TEXT DEFAULT 'ONLINE',
                        is_approved INTEGER DEFAULT 0,
                        is_online INTEGER DEFAULT 1,
                        fayda_id_url TEXT,
                        fayda_photo_id TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                conn.commit()
        except Exception as te:
            logger.warning("brokers ensure: %s", te)

        cols = {c.lower() for c in _broker_table_columns(cur)}
        logger.info("add_broker cols=%s user_chat_id=%s", sorted(cols), chat_id)

        approved_val = False if pg else 0
        online_val = True if pg else 1

        def _commit():
            try:
                conn.commit()
            except Exception:
                pass

        # Find existing by user_chat_id OR chat_id
        existing_id = None
        for key_col in ("user_chat_id", "chat_id", "telegram_id", "user_id"):
            if key_col not in cols:
                continue
            try:
                cur.execute(f"SELECT id FROM brokers WHERE {key_col} = {p}", (chat_id,))
                row = cur.fetchone()
                if row:
                    existing_id = row["id"] if isinstance(row, dict) else row[0]
                    break
            except Exception as se:
                logger.warning("select by %s: %s", key_col, se)

        # ---- INSERT if new ----
        if existing_id is None:
            # Always include user_chat_id when column exists (NOT NULL constraint)
            ins = {}
            if "user_chat_id" in cols:
                ins["user_chat_id"] = chat_id
            if "chat_id" in cols:
                ins["chat_id"] = chat_id
            if "telegram_id" in cols:
                ins["telegram_id"] = chat_id
            if "user_id" in cols:
                ins["user_id"] = chat_id
            # If schema unknown, force user_chat_id + chat_id
            if not ins:
                ins["user_chat_id"] = chat_id
                ins["chat_id"] = chat_id

            if "full_name" in cols or not cols:
                ins["full_name"] = full_name
            if "name" in cols:
                ins["name"] = full_name
            if "is_approved" in cols or not cols:
                ins["is_approved"] = approved_val
            # NOT NULL-safe fields — never omit / never None
            if "phone" in cols or not cols:
                ins["phone"] = phone or "N/A"
            if "phone_number" in cols:
                ins["phone_number"] = phone or "N/A"
            if "status" in cols:
                ins["status"] = "ONLINE"
            if "username" in cols:
                ins["username"] = username or "N/A"
            if "sub_city" in cols:
                ins["sub_city"] = sub_city or "አዲስ አበባ"
            if "working_area" in cols:
                ins["working_area"] = sub_city or "አዲስ አበባ"
            if "area" in cols:
                ins["area"] = sub_city or "አዲስ አበባ"
            if "specialty" in cols:
                ins["specialty"] = specialty or "ደላላ"
            if "category" in cols:
                ins["category"] = specialty or "ደላላ"
            if "role_type" in cols:
                ins["role_type"] = role_type or "ደላላ"
            if "fayda_id_url" in cols and fayda_url:
                ins["fayda_id_url"] = fayda_url
            if "fayda_photo_id" in cols and fayda:
                ins["fayda_photo_id"] = fayda

            col_list = list(ins.keys())
            val_list = list(ins.values())
            # SAFETY: user_chat_id must never be missing if column exists
            if "user_chat_id" in cols and "user_chat_id" not in ins:
                col_list.insert(0, "user_chat_id")
                val_list.insert(0, chat_id)

            ph = ", ".join([p] * len(val_list))
            sql = f"INSERT INTO brokers ({', '.join(col_list)}) VALUES ({ph})"
            logger.info("INSERT brokers cols=%s vals_id=%s", col_list, chat_id)
            try:
                if pg:
                    cur.execute(sql + " RETURNING id", tuple(val_list))
                    row = cur.fetchone()
                    existing_id = row["id"] if isinstance(row, dict) else row[0]
                else:
                    cur.execute(sql, tuple(val_list))
                    existing_id = cur.lastrowid
                _commit()
            except Exception as ie:
                LAST_BROKER_ERROR = str(ie)
                logger.error("INSERT failed: %s", ie, exc_info=True)
                try:
                    if not pg:
                        conn.rollback()
                except Exception:
                    pass
                # Retry ultra-minimal with only user_chat_id
                try:
                    if "user_chat_id" in cols:
                        if pg:
                            # include working_area if required by schema
                            try:
                                cur.execute(
                                    f"INSERT INTO brokers (user_chat_id, full_name, phone, working_area, is_approved) "
                                    f"VALUES ({p}, {p}, {p}, {p}, {p}) RETURNING id",
                                    (chat_id, full_name, phone or "N/A", sub_city or "አዲስ አበባ", approved_val),
                                )
                            except Exception:
                                cur.execute(
                                    f"INSERT INTO brokers (user_chat_id, full_name, phone, is_approved) "
                                    f"VALUES ({p}, {p}, {p}, {p}) RETURNING id",
                                    (chat_id, full_name, phone or "N/A", approved_val),
                                )
                            row = cur.fetchone()
                            existing_id = row["id"] if isinstance(row, dict) else row[0]
                        else:
                            cur.execute(
                                f"INSERT INTO brokers (user_chat_id, full_name, phone, is_approved) "
                                f"VALUES ({p}, {p}, {p}, {p})",
                                (chat_id, full_name, phone or "N/A", approved_val),
                            )
                            existing_id = cur.lastrowid
                        _commit()
                        LAST_BROKER_ERROR = ""
                    else:
                        return None
                except Exception as ie2:
                    LAST_BROKER_ERROR = str(ie2)
                    logger.error("retry INSERT failed: %s", ie2, exc_info=True)
                    return None

        if existing_id is None:
            LAST_BROKER_ERROR = LAST_BROKER_ERROR or "no id after insert"
            return None

        # ---- UPDATE remaining fields ----
        updates = {
            "user_chat_id": chat_id,
            "chat_id": chat_id,
            "full_name": full_name,
            "name": full_name,
            "phone": phone or "N/A",
            "phone_number": phone or "N/A",
            "username": username or "N/A",
            "sub_city": sub_city or "አዲስ አበባ",
            "working_area": sub_city or "አዲስ አበባ",
            "area": sub_city or "አዲስ አበባ",
            "specialty": specialty or "ደላላ",
            "category": specialty or "ደላላ",
            "role_type": role_type or "ደላላ",
            "status": "ONLINE",
            "is_approved": approved_val,
            "is_online": online_val,
            "fayda_photo_id": fayda,
            "fayda_id_url": fayda_url or None,
            "national_id_photo": photo,
        }
        for col, val in updates.items():
            if cols and col not in cols:
                continue
            try:
                cur.execute(
                    f"UPDATE brokers SET {col} = {p} WHERE id = {p}",
                    (val, existing_id),
                )
                _commit()
            except Exception as ue:
                logger.debug("update %s skip: %s", col, ue)
                try:
                    if not pg:
                        conn.rollback()
                except Exception:
                    pass

        logger.info("✅ Broker saved id=%s user_chat_id=%s name=%r", existing_id, chat_id, full_name)
        return int(existing_id)
    except Exception as e:
        LAST_BROKER_ERROR = str(e)
        logger.error("add_broker FAILED: %s", e, exc_info=True)
        if conn:
            try:
                conn.rollback()
            except Exception:
                pass
        return None
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass



def get_broker(chat_id: int):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        p = get_placeholder()
        cursor.execute(
            f"SELECT * FROM brokers WHERE chat_id = {p} OR user_chat_id = {p}",
            (chat_id, chat_id),
        )
        row = cursor.fetchone()
        if row:
            return dict(row) if isinstance(row, dict) else dict(zip([c[0] for c in cursor.description], row))
        return None
    except Exception as e:
        logger.error(f"Get broker error: {e}")
        return None
    finally:
        if conn:
            try:
                conn.close()
            except:
                pass


def delete_broker(chat_id: int) -> bool:
    """Delete a broker row by Telegram chat_id. Returns True on success."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        p = get_placeholder()
        chat_id = int(chat_id)
        cursor.execute(f"DELETE FROM brokers WHERE chat_id = {p}", (chat_id,))
        try:
            if not is_postgres():
                conn.commit()
            else:
                try:
                    conn.commit()
                except Exception:
                    pass
        except Exception:
            pass
        logger.info("Deleted broker chat_id=%s", chat_id)
        return True
    except Exception as e:
        logger.error(f"delete_broker error: {e}", exc_info=True)
        return False
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass


def update_broker_status(chat_id: int, status: str) -> bool:
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        p = get_placeholder()
        cursor.execute(f"UPDATE brokers SET status = {p} WHERE chat_id = {p}", (status.lower(), chat_id))
        if not is_postgres():
            conn.commit()
        return True
    except Exception as e:
        logger.error(f"Update broker status error: {e}")
        return False
    finally:
        if conn:
            try:
                conn.close()
            except:
                pass

def update_broker_notification_prefs(chat_id: int, prefs: dict) -> bool:
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        p = get_placeholder()
        prefs_json = json.dumps(prefs, ensure_ascii=False)
        cursor.execute(f"UPDATE brokers SET notification_prefs = {p} WHERE chat_id = {p}", (prefs_json, chat_id))
        if not is_postgres():
            conn.commit()
        return True
    except Exception as e:
        logger.error(f"Update broker notification prefs error: {e}")
        return False
    finally:
        if conn:
            try:
                conn.close()
            except:
                pass


def ensure_brokers_columns():
    """Ensure brokers table has status / is_approved columns used by the app."""
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        if is_postgres():
            for sql in [
                "ALTER TABLE brokers ADD COLUMN IF NOT EXISTS status TEXT DEFAULT 'ONLINE'",
                "ALTER TABLE brokers ADD COLUMN IF NOT EXISTS is_approved BOOLEAN DEFAULT TRUE",
                "ALTER TABLE brokers ADD COLUMN IF NOT EXISTS is_online BOOLEAN DEFAULT TRUE",
                "ALTER TABLE brokers ADD COLUMN IF NOT EXISTS chat_id BIGINT",
                "ALTER TABLE brokers ADD COLUMN IF NOT EXISTS full_name TEXT",
                "ALTER TABLE brokers ADD COLUMN IF NOT EXISTS phone TEXT",
                "ALTER TABLE brokers ADD COLUMN IF NOT EXISTS username TEXT",
                "ALTER TABLE brokers ADD COLUMN IF NOT EXISTS sub_city TEXT",
                    "ALTER TABLE brokers ADD COLUMN IF NOT EXISTS working_area TEXT",
                "ALTER TABLE brokers ADD COLUMN IF NOT EXISTS specialty TEXT",
                "ALTER TABLE brokers ADD COLUMN IF NOT EXISTS notification_prefs JSONB DEFAULT '{}'::jsonb",
                "ALTER TABLE brokers ADD COLUMN IF NOT EXISTS rating REAL DEFAULT 5.0",
            ]:
                try:
                    cur.execute(sql)
                except Exception as e:
                    logger.debug("brokers alter skip: %s", e)
        else:
            for col, typedef in [
                ("status", "TEXT DEFAULT 'ONLINE'"),
                ("is_approved", "INTEGER DEFAULT 1"),
                ("is_online", "INTEGER DEFAULT 1"),
                ("chat_id", "INTEGER"),
                ("full_name", "TEXT"),
                ("phone", "TEXT"),
                ("username", "TEXT"),
                ("sub_city", "TEXT"),
                ("specialty", "TEXT"),
                ("notification_prefs", "TEXT DEFAULT '{}'"),
                ("rating", "REAL DEFAULT 5.0"),
            ]:
                try:
                    cur.execute(f"ALTER TABLE brokers ADD COLUMN {col} {typedef}")
                except Exception:
                    pass
            try:
                conn.commit()
            except Exception:
                pass
    except Exception as e:
        logger.warning("ensure_brokers_columns: %s", e)
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass


def _broker_table_columns(cur) -> set:
    cols = set()
    try:
        if is_postgres():
            cur.execute("""
                SELECT column_name FROM information_schema.columns
                WHERE table_schema = 'public' AND table_name = 'brokers'
            """)
            for row in cur.fetchall() or []:
                name = row["column_name"] if isinstance(row, dict) else row[0]
                cols.add(str(name).lower())
        else:
            cur.execute("PRAGMA table_info(brokers)")
            for row in cur.fetchall() or []:
                if isinstance(row, dict):
                    cols.add(str(row.get("name", "")).lower())
                else:
                    cols.add(str(row[1]).lower())
    except Exception as e:
        logger.warning("_broker_table_columns: %s", e)
    return cols


def _normalize_broker_row(broker: dict, cols_desc=None) -> dict:
    if not isinstance(broker, dict):
        broker = dict(zip([c[0] for c in (cols_desc or [])], broker)) if cols_desc else {}
    if isinstance(broker.get("notification_prefs"), str):
        try:
            broker["notification_prefs"] = json.loads(broker["notification_prefs"])
        except Exception:
            broker["notification_prefs"] = {"car": True, "house": True, "enabled": True}
    if not broker.get("notification_prefs"):
        broker["notification_prefs"] = {"car": True, "house": True, "enabled": True}
    # Status / approval fallbacks
    st = broker.get("status")
    if st is None or st == "":
        if broker.get("is_approved") in (True, 1, "1", "true", "TRUE"):
            st = "ONLINE"
        elif broker.get("is_approved") in (False, 0, "0", "false"):
            st = "rejected"
        else:
            st = "ONLINE"
    broker["status"] = st
    if broker.get("is_online") is None:
        broker["is_online"] = str(st).lower() not in ("rejected", "deleted", "banned", "offline")
    broker["phone"] = broker.get("phone") or ""
    broker["username"] = broker.get("username") or ""
    broker["full_name"] = broker.get("full_name") or broker.get("name") or "User"
    broker["sub_city"] = broker.get("sub_city") or ""
    broker["specialty"] = broker.get("specialty") or broker.get("role_type") or ""
    if broker.get("chat_id") is not None:
        try:
            broker["chat_id"] = int(broker["chat_id"])
        except Exception:
            pass
    return broker


def get_approved_brokers():
    """Brokers eligible for notifications. Boolean-safe for PostgreSQL."""
    conn = None
    try:
        try:
            ensure_brokers_columns()
        except Exception:
            pass
        conn = get_db_connection()
        cursor = conn.cursor()
        cols = _broker_table_columns(cursor)

        # IMPORTANT: never compare boolean column to integer (1/0)
        if "status" in cols and "is_approved" in cols:
            sql = (
                "SELECT * FROM brokers WHERE "
                "(status IS NULL OR LOWER(CAST(status AS TEXT)) IN "
                "('approved','online','pending','ONLINE','APPROVED','PENDING')) "
                "OR (is_approved IS NULL OR is_approved IS TRUE OR is_approved = TRUE)"
            )
        elif "is_approved" in cols:
            sql = (
                "SELECT * FROM brokers WHERE "
                "(is_approved IS NULL OR is_approved IS TRUE OR is_approved = TRUE)"
            )
        elif "status" in cols:
            sql = (
                "SELECT * FROM brokers WHERE "
                "(status IS NULL OR LOWER(CAST(status AS TEXT)) IN "
                "('approved','online','pending','ONLINE','APPROVED','PENDING'))"
            )
        else:
            sql = "SELECT * FROM brokers"

        try:
            cursor.execute(sql)
        except Exception as qe:
            logger.warning("get_approved_brokers filtered query failed (%s); selecting all", qe)
            cursor.execute("SELECT * FROM brokers")

        rows = cursor.fetchall() or []
        results = []
        for row in rows:
            broker = (
                dict(row)
                if isinstance(row, dict)
                else dict(zip([c[0] for c in cursor.description], row))
            )
            broker = _normalize_broker_row(broker, cursor.description)
            st = str(broker.get("status") or "").lower()
            if st in ("rejected", "deleted", "banned"):
                continue
            results.append(broker)
        return results
    except Exception as e:
        logger.error(f"Get approved brokers error: {e}")
        return []
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass



def get_approved_brokers_directory(sub_city=None):
    return get_active_brokers(sub_city=sub_city, status="ONLINE")


def get_active_brokers(sub_city=None, status="ONLINE", limit=50, offset=0):
    """Directory list — works without status column."""
    conn = None
    try:
        try:
            ensure_brokers_columns()
        except Exception:
            pass
        conn = get_db_connection()
        cur = conn.cursor()
        p = get_placeholder()
        cols = _broker_table_columns(cur)

        where = []
        params = []
        if "status" in cols:
            where.append(
                "(status IS NULL OR LOWER(CAST(status AS TEXT)) NOT IN "
                "('rejected', 'deleted', 'banned'))"
            )
        elif "is_approved" in cols:
            where.append("(is_approved IS NULL OR is_approved IS TRUE OR is_approved = TRUE)")

        if sub_city and str(sub_city).strip() not in ("ሁሉም", "አዲስ አበባ (ሙሉ)", "", "None"):
            if "sub_city" in cols or not cols:
                where.append(f"sub_city = {p}")
                params.append(str(sub_city).strip())

        where_sql = (" WHERE " + " AND ".join(where)) if where else ""
        params += [int(limit), int(offset)]
        sql = f"SELECT * FROM brokers{where_sql} ORDER BY id DESC LIMIT {p} OFFSET {p}"
        try:
            cur.execute(sql, params)
        except Exception as qe:
            logger.warning("get_active_brokers query failed (%s); fallback all", qe)
            cur.execute(f"SELECT * FROM brokers ORDER BY id DESC LIMIT {p} OFFSET {p}", [int(limit), int(offset)])
        rows = cur.fetchall() or []
        out = []
        for row in rows:
            try:
                b = dict(row) if isinstance(row, dict) else dict(zip([c[0] for c in cur.description], row))
                b = _normalize_broker_row(b, cur.description)
                if b.get("chat_id") is None:
                    continue
                st = str(b.get("status") or "").lower()
                if st in ("rejected", "deleted", "banned"):
                    continue
                out.append(b)
            except Exception as row_err:
                logger.warning(f"skip bad broker row: {row_err}")
                continue
        logger.info(f"get_active_brokers → {len(out)} brokers")
        return out
    except Exception as e:
        logger.error(f"get_active_brokers: {e}", exc_info=True)
        return []
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass




def count_brokers(status="ONLINE") -> int:
    try:
        brokers = get_active_brokers(limit=500, offset=0)
        return len(brokers or [])
    except Exception as e:
        logger.error(f"count_brokers: {e}")
        return 0



def get_platform_stats() -> dict:
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        stats = {}
        for key, sql in (
            ("active_listings", "SELECT COUNT(*) as cnt FROM listings WHERE status = 'ONLINE'"),
            ("verified_brokers", "SELECT COUNT(*) as cnt FROM brokers WHERE status = 'approved'"),
            ("total_listings", "SELECT COUNT(*) as cnt FROM listings"),
            ("active_users", "SELECT COUNT(DISTINCT user_chat_id) as cnt FROM listings"),
        ):
            cur.execute(sql)
            row = cur.fetchone()
            stats[key] = int((row["cnt"] if isinstance(row, dict) else row[0]) or 0)
        return stats
    except Exception as e:
        logger.error(f"get_platform_stats: {e}")
        return {"active_listings": 0, "verified_brokers": 0, "total_listings": 0, "active_users": 0}
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass



def save_broker_offer(request_id: int, broker_id: int, description: str, photo_id: str = None) -> bool:
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        p = get_placeholder()
        cursor.execute(f"""
            INSERT INTO broker_offers (request_id, broker_id, description, photo_id)
            VALUES ({p}, {p}, {p}, {p})
        """, (request_id, broker_id, description, photo_id))
        if not is_postgres():
            conn.commit()
        return True
    except Exception as e:
        logger.error(f"Save broker offer error: {e}")
        return False
    finally:
        if conn:
            try:
                conn.close()
            except:
                pass


# ========== RATINGS ==========

def add_broker_rating(broker_chat_id, user_chat_id, stars) -> bool:
    """
    2-step rating backend: save stars (1-5) and refresh average.
    Works on PostgreSQL and SQLite. Always commits.
    """
    conn = None
    try:
        broker_chat_id = int(broker_chat_id)
        user_chat_id = int(user_chat_id)
        stars = max(1, min(5, int(stars)))

        conn = get_db_connection()
        cur = conn.cursor()
        p = get_placeholder()

        # --- Ensure schema ---
        if is_postgres():
            cur.execute("""
                CREATE TABLE IF NOT EXISTS ratings (
                    id SERIAL PRIMARY KEY,
                    broker_chat_id BIGINT NOT NULL,
                    user_chat_id BIGINT NOT NULL,
                    stars INT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            try:
                cur.execute(
                    "CREATE UNIQUE INDEX IF NOT EXISTS ratings_broker_user_uidx "
                    "ON ratings (broker_chat_id, user_chat_id)"
                )
            except Exception as ix:
                logger.warning(f"ratings unique index: {ix}")
            for col_sql in (
                "ALTER TABLE brokers ADD COLUMN IF NOT EXISTS rating REAL DEFAULT 5.0",
                "ALTER TABLE brokers ADD COLUMN IF NOT EXISTS total_ratings INT DEFAULT 0",
            ):
                try:
                    cur.execute(col_sql)
                except Exception:
                    pass
            # Upsert without relying solely on ON CONFLICT constraint name
            cur.execute(
                f"DELETE FROM ratings WHERE broker_chat_id = {p} AND user_chat_id = {p}",
                (broker_chat_id, user_chat_id),
            )
            cur.execute(
                f"INSERT INTO ratings (broker_chat_id, user_chat_id, stars) VALUES ({p}, {p}, {p})",
                (broker_chat_id, user_chat_id, stars),
            )
            cur.execute(
                f"SELECT COALESCE(AVG(stars), 5.0), COUNT(*) FROM ratings WHERE broker_chat_id = {p}",
                (broker_chat_id,),
            )
        else:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS ratings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    broker_chat_id INTEGER NOT NULL,
                    user_chat_id INTEGER NOT NULL,
                    stars INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE (broker_chat_id, user_chat_id)
                )
            """)
            for col_sql in (
                "ALTER TABLE brokers ADD COLUMN rating REAL DEFAULT 5.0",
                "ALTER TABLE brokers ADD COLUMN total_ratings INTEGER DEFAULT 0",
            ):
                try:
                    cur.execute(col_sql)
                except Exception:
                    pass
            cur.execute(
                "DELETE FROM ratings WHERE broker_chat_id = ? AND user_chat_id = ?",
                (broker_chat_id, user_chat_id),
            )
            cur.execute(
                "INSERT INTO ratings (broker_chat_id, user_chat_id, stars) VALUES (?, ?, ?)",
                (broker_chat_id, user_chat_id, stars),
            )
            cur.execute(
                "SELECT COALESCE(AVG(stars), 5.0), COUNT(*) FROM ratings WHERE broker_chat_id = ?",
                (broker_chat_id,),
            )

        result = cur.fetchone()
        if isinstance(result, dict):
            vals = list(result.values())
            avg_stars = float(vals[0] or 5.0)
            total_count = int(vals[1] or 0)
        else:
            avg_stars = float(result[0] or 5.0)
            total_count = int(result[1] or 0)

        cur.execute(
            f"UPDATE brokers SET rating = {p}, total_ratings = {p} WHERE chat_id = {p}",
            (round(avg_stars, 1), total_count, broker_chat_id),
        )
        conn.commit()
        logger.info(
            f"✅ rating saved broker={broker_chat_id} user={user_chat_id} "
            f"stars={stars} avg={avg_stars:.1f} n={total_count}"
        )
        return True
    except Exception as e:
        logger.error(f"add_broker_rating error: {e}", exc_info=True)
        if conn:
            try:
                conn.rollback()
            except Exception:
                pass
        return False
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass



def increment_listing_views(listing_id: int, amount: int = 1) -> int:
    """Increment view_count and return new value."""
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        p = get_placeholder()
        listing_id = int(listing_id)
        amount = int(amount)
        if is_postgres():
            cur.execute(
                f"UPDATE listings SET view_count = COALESCE(view_count, 0) + {p} WHERE id = {p} RETURNING view_count",
                (amount, listing_id),
            )
            row = cur.fetchone()
            conn.commit()
            if not row:
                return 0
            return int(row["view_count"] if isinstance(row, dict) else row[0])
        else:
            cur.execute(
                "UPDATE listings SET view_count = COALESCE(view_count, 0) + ? WHERE id = ?",
                (amount, listing_id),
            )
            conn.commit()
            cur.execute("SELECT view_count FROM listings WHERE id = ?", (listing_id,))
            row = cur.fetchone()
            if not row:
                return 0
            return int(row["view_count"] if isinstance(row, dict) else row[0])
    except Exception as e:
        logger.error(f"increment_listing_views: {e}")
        return 0
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass



def save_search_alert(user_chat_id: int, main_category: str, budget_min: str, budget_max: str, target_model: str = None) -> int:
    """Save user alert. target_model optional (stored in budget_min prefix META if column missing)."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        p = get_placeholder()
        # Best-effort column for model
        try:
            if is_postgres():
                cursor.execute("ALTER TABLE search_alerts ADD COLUMN IF NOT EXISTS target_model TEXT")
                cursor.execute("ALTER TABLE search_alerts ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE")
            else:
                try:
                    cursor.execute("ALTER TABLE search_alerts ADD COLUMN target_model TEXT")
                except Exception:
                    pass
                try:
                    cursor.execute("ALTER TABLE search_alerts ADD COLUMN is_active INTEGER DEFAULT 1")
                except Exception:
                    pass
                try:
                    conn.commit()
                except Exception:
                    pass
        except Exception as _ae:
            logger.debug("search_alerts alter: %s", _ae)

        # Detect columns
        cols = set()
        try:
            if is_postgres():
                cursor.execute("""
                    SELECT column_name FROM information_schema.columns
                    WHERE table_schema='public' AND table_name='search_alerts'
                """)
                for row in cursor.fetchall() or []:
                    cols.add((row["column_name"] if isinstance(row, dict) else row[0]).lower())
            else:
                cursor.execute("PRAGMA table_info(search_alerts)")
                for row in cursor.fetchall() or []:
                    cols.add((row["name"] if isinstance(row, dict) else row[1]).lower())
        except Exception:
            pass

        tm = (target_model or "")[:120]
        bmin = str(budget_min or "")
        bmax = str(budget_max or "")
        if "target_model" in cols:
            cursor.execute(f"""
                INSERT INTO search_alerts (user_chat_id, main_category, budget_min, budget_max, target_model)
                VALUES ({p}, {p}, {p}, {p}, {p})
            """, (user_chat_id, main_category, bmin, bmax, tm))
        else:
            # encode model into budget_min marker if needed
            if tm:
                bmin = f"{bmin}|model:{tm}"
            cursor.execute(f"""
                INSERT INTO search_alerts (user_chat_id, main_category, budget_min, budget_max)
                VALUES ({p}, {p}, {p}, {p})
            """, (user_chat_id, main_category, bmin, bmax))
        if is_postgres():
            cursor.execute("SELECT lastval()")
            row = cursor.fetchone()
            alert_id = row[0] if not isinstance(row, dict) else list(row.values())[0]
        else:
            alert_id = cursor.lastrowid
            conn.commit()
        return alert_id or 0
    except Exception as e:
        logger.error(f"Save search alert error: {e}")
        return 0
    finally:
        if conn:
            try:
                conn.close()
            except:
                pass

def get_matching_alerts(main_category: str, price: str, model_hint: str = None) -> list:
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        p = get_placeholder()
        # Tolerate missing is_active column
        try:
            cursor.execute(f"""
                SELECT * FROM search_alerts
                WHERE (is_active IS NULL OR is_active = TRUE OR is_active = 1)
                  AND (main_category = {p} OR main_category IS NULL OR main_category = '')
                ORDER BY created_at DESC
            """, (main_category,))
        except Exception:
            cursor.execute(f"SELECT * FROM search_alerts WHERE main_category = {p} ORDER BY created_at DESC", (main_category,))
        rows = cursor.fetchall() or []
        matching = []
        try:
            price_num = float(str(price).replace(",", "").replace("ETB", "").strip() or 0)
        except (ValueError, TypeError):
            price_num = 0
        mh = (model_hint or "").lower().strip()
        for row in rows:
            alert = dict(row) if isinstance(row, dict) else dict(zip([c[0] for c in cursor.description], row))
            try:
                raw_min = str(alert.get("budget_min") or "0")
                # strip model marker
                if "|model:" in raw_min:
                    parts = raw_min.split("|model:", 1)
                    raw_min = parts[0]
                    encoded_model = parts[1]
                    if not alert.get("target_model"):
                        alert["target_model"] = encoded_model
                alert_min = float(raw_min.replace(",", "") or 0)
                alert_max = float(str(alert.get("budget_max") or 999999999).replace(",", "") or 999999999)
                if not (alert_min <= price_num <= alert_max):
                    continue
                tm = (alert.get("target_model") or "").lower().strip()
                if tm and mh and tm not in mh and mh not in tm:
                    # model specified but no overlap — skip
                    continue
                matching.append(alert)
            except (ValueError, TypeError):
                matching.append(alert)
        return matching
    except Exception as e:
        logger.error(f"Get matching alerts error: {e}")
        return []
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass


# ==============================================================================
# 5. CONSTANTS & KEYBOARDS
# ==============================================================================


def expire_old_listings(days: int = 30) -> int:
    """
    Mark listings older than `days` as 'expired' if they are still active (pending).
    Safe: only touches status, never deletes rows.
    Returns number of rows updated.
    """
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        if is_postgres():
            # PostgreSQL
            cur.execute("""
                UPDATE listings
                SET status = 'expired'
                WHERE status = 'ONLINE'
                  AND created_at < (NOW() - INTERVAL '%s days')
            """ % int(days))
            # rowcount available on cursor
            count = cur.rowcount
        else:
            # SQLite
            cur.execute("""
                UPDATE listings
                SET status = 'expired'
                WHERE status = 'ONLINE'
                  AND created_at < datetime('now', ?)
            """, (f'-{int(days)} days',))
            count = cur.rowcount
            conn.commit()
        logger.info(f"🧹 Auto-expiry: {count} listings marked expired (>{days} days)")
        return count or 0
    except Exception as e:
        logger.error(f"expire_old_listings error: {e}", exc_info=True)
        return 0
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass






# ========== CONTRACTS ==========

def ensure_contracts_table():
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        if is_postgres():
            cur.execute("""
                CREATE TABLE IF NOT EXISTS contracts (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT,
                    seller_info JSONB DEFAULT '{}',
                    buyer_info JSONB DEFAULT '{}',
                    vehicle_info JSONB DEFAULT '{}',
                    financial_info JSONB DEFAULT '{}',
                    witnesses JSONB DEFAULT '[]',
                    contract_status TEXT DEFAULT 'Draft',
                    contract_text TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
        else:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS contracts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    seller_info TEXT DEFAULT '{}',
                    buyer_info TEXT DEFAULT '{}',
                    vehicle_info TEXT DEFAULT '{}',
                    financial_info TEXT DEFAULT '{}',
                    witnesses TEXT DEFAULT '[]',
                    contract_status TEXT DEFAULT 'Draft',
                    contract_text TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
    except Exception as e:
        logger.error("ensure_contracts_table: %s", e)
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass


def _json_param(obj):
    if is_postgres():
        try:
            from psycopg2.extras import Json as PgJson
            return PgJson(obj if obj is not None else {})
        except Exception:
            return json.dumps(obj or {}, ensure_ascii=False)
    return json.dumps(obj or {}, ensure_ascii=False)


def save_contract(user_id, seller_info, buyer_info, vehicle_info, financial_info,
                  witnesses=None, contract_status="Draft", contract_text=None, contract_id=None):
    """Insert or update contract. Returns id."""
    ensure_contracts_table()
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        p = get_placeholder()
        uid = int(user_id) if user_id else 0
        s = _json_param(seller_info or {})
        b = _json_param(buyer_info or {})
        v = _json_param(vehicle_info or {})
        f = _json_param(financial_info or {})
        w = _json_param(witnesses or [])
        status = str(contract_status or "Draft")[:32]
        text = contract_text or ""

        if contract_id:
            cur.execute(
                f"""UPDATE contracts SET
                    seller_info={p}, buyer_info={p}, vehicle_info={p}, financial_info={p},
                    witnesses={p}, contract_status={p}, contract_text={p},
                    updated_at=CURRENT_TIMESTAMP
                    WHERE id={p}""",
                (s, b, v, f, w, status, text, int(contract_id)),
            )
            if not is_postgres():
                conn.commit()
            return int(contract_id)

        cur.execute(
            f"""INSERT INTO contracts
                (user_id, seller_info, buyer_info, vehicle_info, financial_info, witnesses, contract_status, contract_text)
                VALUES ({p},{p},{p},{p},{p},{p},{p},{p})""",
            (uid, s, b, v, f, w, status, text),
        )
        if is_postgres():
            cur.execute("SELECT lastval()")
            row = cur.fetchone()
            cid = row[0] if not isinstance(row, dict) else list(row.values())[0]
        else:
            cid = cur.lastrowid
            conn.commit()
        return int(cid or 0)
    except Exception as e:
        logger.error("save_contract: %s", e, exc_info=True)
        return None
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass


def get_contract(contract_id):
    ensure_contracts_table()
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        p = get_placeholder()
        cur.execute(f"SELECT * FROM contracts WHERE id = {p}", (int(contract_id),))
        row = cur.fetchone()
        if not row:
            return None
        d = dict(row) if isinstance(row, dict) else dict(zip([c[0] for c in cur.description], row))
        for k in ("seller_info", "buyer_info", "vehicle_info", "financial_info", "witnesses"):
            if isinstance(d.get(k), str):
                try:
                    d[k] = json.loads(d[k])
                except Exception:
                    pass
        return d
    except Exception as e:
        logger.error("get_contract: %s", e)
        return None
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass


def get_user_contracts(user_id, limit=20):
    ensure_contracts_table()
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        p = get_placeholder()
        cur.execute(
            f"SELECT * FROM contracts WHERE user_id = {p} ORDER BY id DESC LIMIT {p}",
            (int(user_id), int(limit)),
        )
        rows = cur.fetchall() or []
        out = []
        for row in rows:
            d = dict(row) if isinstance(row, dict) else dict(zip([c[0] for c in cur.description], row))
            for k in ("seller_info", "buyer_info", "vehicle_info", "financial_info", "witnesses"):
                if isinstance(d.get(k), str):
                    try:
                        d[k] = json.loads(d[k])
                    except Exception:
                        pass
            out.append(d)
        return out
    except Exception as e:
        logger.error("get_user_contracts: %s", e)
        return []
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass




def _etb_words(n):
    """Convert integer ETB amount to Amharic words (supports up to billions)."""
    try:
        n = int(float(str(n).replace(",", "").replace("ብር", "").strip() or 0))
    except Exception:
        return str(n)

    ones = ["", "አንድ", "ሁለት", "ሦስት", "አራት", "አምስት", "ስድስት", "ሰባት", "ስምንት", "ዘጠኝ"]
    teens = {
        10: "አስር", 11: "አስራ አንድ", 12: "አስራ ሁለት", 13: "አስራ ሦስት", 14: "አስራ አራት",
        15: "አስራ አምስት", 16: "አስራ ስድስት", 17: "አስራ ሰባት", 18: "አስራ ስምንት", 19: "አስራ ዘጠኝ",
    }
    tens = ["", "አስር", "ሃያ", "ሰላሳ", "አርባ", "ሃምሳ", "ስልሳ", "ሰባ", "ሰማንያ", "ዘጠና"]
    # hundreds: አንድ መቶ, ሁለት መቶ, ...
    def under_1000(x):
        if x == 0:
            return ""
        parts = []
        h = x // 100
        r = x % 100
        if h:
            parts.append(("አንድ መቶ" if h == 1 else f"{ones[h]} መቶ"))
        if r:
            if r < 10:
                parts.append(ones[r])
            elif r < 20:
                parts.append(teens[r])
            else:
                t, o = divmod(r, 10)
                if o:
                    parts.append(f"{tens[t]} {ones[o]}")
                else:
                    parts.append(tens[t])
        return " ".join(parts)

    if n == 0:
        return "ዜሮ"
    if n < 0:
        return "አሉታዊ " + _etb_words(-n)

    scales = [
        (1_000_000_000, "ቢሊዮን"),
        (1_000_000, "ሚሊዮን"),
        (1_000, "ሺህ"),
    ]
    parts = []
    rest = n
    for scale, name in scales:
        if rest >= scale:
            q, rest = divmod(rest, scale)
            w = under_1000(q)
            if q == 1 and scale == 1000:
                parts.append(f"አንድ {name}")
            else:
                parts.append(f"{w} {name}")
    if rest:
        parts.append(under_1000(rest))
    return " ".join(p for p in parts if p).strip()


def _money_phrase(n):
    """Format: 78,000 ብር (ሰባ ስምንት ሺህ ብር)"""
    try:
        n = int(float(str(n).replace(",", "") or 0))
    except Exception:
        n = 0
    return f"{n:,} ብር ({_etb_words(n)} ብር)"


def _party_line(label, p):
    p = p or {}
    return (
        f"{label}: {p.get('name') or '—'}፣ "
        f"ዜግነት: {p.get('nationality') or 'ኢትዮጵያዊ'}፣ "
        f"አድራሻ: ክ/ከተማ: {p.get('sub_city') or '—'}፣ "
        f"ወረዳ: {p.get('woreda') or '—'}፣ "
        f"የቤት ቁጥር: {p.get('house_no') or '—'}፣ "
        f"ስልክ: {p.get('phone') or '—'}"
    )


def _witness_block(witnesses):
    """Inline witness lines with signature — no duplicate footer block."""
    witnesses = witnesses or []
    lines = []
    for i in range(3):
        w = witnesses[i] if i < len(witnesses) else {}
        lines.append(
            f"ምስክር {i+1}: {w.get('name') or '________________'} | "
            f"አድራሻ: {w.get('address') or '________________'} | "
            f"ስልክ: {w.get('phone') or '________'} | "
            f"ፊርማ: ___________"
        )
    return "\n".join(lines)


def _party_signatures(is_rental=False):
    if is_rental:
        return (
            "የውል ሰጪ (አከራይ) ፊርማ: ____________________\n"
            "የውል ተቀባይ (ተከራይ) ፊርማ: ____________________"
        )
    return (
        "የውል ሰጪ (ሻጭ) ፊርማ: ____________________\n"
        "የውል ተቀባይ (ገዢ) ፊርማ: ____________________"
    )


def build_amharic_vehicle_sale_contract(seller, buyer, vehicle, financial, witnesses=None):
    seller, buyer, vehicle, financial = seller or {}, buyer or {}, vehicle or {}, financial or {}
    total = int(float(financial.get("total_price") or 0))
    advance = int(float(financial.get("advance") or 0))
    balance = int(float(financial.get("balance") or max(0, total - advance)))
    penalty = int(float(financial.get("penalty") or 50000))
    deadline = financial.get("deadline") or "______________"
    cdate = financial.get("contract_date") or "______________"
    plate = vehicle.get("plate") or "—"
    engine = vehicle.get("engine") or "—"
    chassis = vehicle.get("chassis") or "—"
    model = vehicle.get("model") or "—"

    return f"""የመኪና ሽያጭ ውል ስምምነት

ቀን: {cdate}

{_party_line("ውል ሰጪ (ሻጭ)", seller)}
{_party_line("ውል ተቀባይ (ገዢ)", buyer)}

እኔ ውል ሰጪ (ሻጭ) በስሜ የተመዘገበውን የሰሌዳ ቁጥር {plate}፣ የሞተር ቁጥር {engine}፣ የቻሲ ቁጥር {chassis} የሆነውን {model} መኪና ባለበት ሁኔታ ለውል ተቀባይ (ገዢ) በ {_money_phrase(total)} የሸጥኩ ሲሆን፤ የገንዘቡን አከፋፈል በተመለከተ በዛሬው ዕለት ቅድመ ክፍያ {_money_phrase(advance)} ተቀብዬ፣ ቀሪውን {_money_phrase(balance)} ከዛሬ ጀምሮ እስከ {deadline} ድረስ አጠናቆ ገዢ የሚያስረክበኝ መሆኑን ተስማምተን መኪናውንና ሰነዶቹን ለገዢ ያስረከብኩ መሆኑን አረጋግጣለሁ።

እኔ ሻጭ በዚህ በሸጥኩት ንብረት ላይ በዕዳ፣ በእገዳ ወይም "ይገባኛል" ብሎ የሚከራከር የሶስተኛ ወገን ቢመጣ በወንጀልና በፍትሐብሔር ቀርቤ ተከራክሬ መልስ የምሰጥና ገዢን ነፃ የማወጣ ሲሆን፤ ከውሉ በፊት የነበረ ማንኛውም የመንግሥት፣ የትራፊክ ቅጣት፣ የታክስ፣ የደብተር/የካርታ ወይም ልዩ ልዩ ዕዳ ቢኖር ከፋዩ እኔው ራሴ መሆኔን አረጋግጣለሁ።

እኔ ገዢ መኪናውን ከተረከብኩበት ዕለት ማለትም ከዛሬ {cdate} ጀምሮ ለሚመጣ ማንኛውም የትራፊክ አደጋ፣ በሰውና ንብረት ላይ ለሚደርስ ጉዳት፣ የወንጀልም ሆነ የመንግሥት ኃላፊነት ሙሉ በሙሉ ተጠያቂው እኔው ራሴ ገዢ ስሆን፣ በዚህ ጉዳይ ላይ ሻጭን ተጠያቂ የማላደርግ መሆኑን ተስማምቼ መኪናውን መረከቤን አረጋግጣለሁ። ገዢ ቀሪውን ገንዘብ አጠናቆ ሲከፍል ሻጭ በ 10 ቀናት ውስጥ የባለቤትነት ስም ዝውውር የማዛወር ግዴታ አለበት።

ይህ ውል በ ፍ/ብ/ሕ/ቁጥር 1731 / 2005 / 2266 መሠረት የተደረገ ነው። ይህንን ውል ለማፍረስ የሚሞክር ወገን ቢኖር {_money_phrase(penalty)} ከፍሎ ውሉ እና ገደቡ በ ፍ/ብ/ሕ/ቁጥር 1889 / 1890 መሠረት በሕግ ፊት የጸና ይሆናል።

እኛ ተዋዋዮችና ምስክሮች በዚህ ውል መሠረት ተስማምተን ገንዘቡም ሲከፈልና ሲቀበል በአካል ተገኝተን በፊርማችን አረጋግጠናል።

{_witness_block(witnesses)}

{_party_signatures(is_rental=False)}
"""


def build_amharic_vehicle_rental_contract(lessor, lessee, vehicle, financial, witnesses=None):
    lessor, lessee, vehicle, financial = lessor or {}, lessee or {}, vehicle or {}, financial or {}
    rate = int(float(financial.get("rent_rate") or 0))
    period = financial.get("rent_period") or "በወር"
    start = financial.get("rent_start") or "______________"
    end = financial.get("rent_end") or "______________"
    penalty = int(float(financial.get("penalty") or 50000))
    cdate = financial.get("contract_date") or "______________"
    plate = vehicle.get("plate") or "—"
    engine = vehicle.get("engine") or "—"
    chassis = vehicle.get("chassis") or "—"
    model = vehicle.get("model") or "—"

    return f"""የመኪና ኪራይ ውል ስምምነት

ቀን: {cdate}

{_party_line("አከራይ", lessor)}
{_party_line("ተከራይ", lessee)}

እኔ አከራይ በስሜ የተመዘገበውን የሰሌዳ ቁጥር {plate}፣ የሞተር ቁጥር {engine}፣ የቻሲ ቁጥር {chassis} የሆነውን {model} መኪና ከ {start} ጀምሮ እስከ {end} ድረስ ለተከራይ አከራይቼ ያስረከብኩ ሲሆን፤ ተከራይም {period} {_money_phrase(rate)} ለመክፈል ተስማምቶ መኪናውን በሙሉ ጤንነት ተረክቧል።

እኔ አከራይ በዚህ ባከራየሁት ንብረት ላይ በዕዳ፣ በእገዳ ወይም "ይገባኛል" ብሎ የሚከራከር የሶስተኛ ወገን ቢመጣ በወንጀልና በፍትሐብሔር ቀርቤ ተከራክሬ መልስ የምሰጥና ተከራይን ነፃ የማወጣ ሲሆን፤ ከውሉ በፊት የነበረ ማንኛውም የመንግሥት፣ የትራፊክ ቅጣት፣ የታክስ፣ የደብተር/የካርታ ወይም ልዩ ልዩ ዕዳ ቢኖር ከፋዩ እኔው ራሴ መሆኔን አረጋግጣለሁ።

ተከራይ መኪናውን ከተረከበበት ሰዓት ጀምሮ እስከሚያስረክብበት ቀን ድረስ ለሚደርስ ማንኛውም የትራፊክ አደጋ፣ የመኪና ስርቆት፣ በሰው ወይም በንብረት ላይ ለሚደርስ ጉዳት፣ እንዲሁም ተሽከርካሪው በቁጥጥሩ ስር እያለ ለሚፈጸም ማንኛውም ህገ-ወጥ ድርጊትና ወንጀል ሙሉ በሙሉ በህግ ፊት ተጠያቂ ይሆናል።

ተከራይ የመኪናውን ዘይት፣ ውሃ እና አጠቃላይ እንክብካቤ የማድረግ ግዴታ ያለበት ሲሆን፣ ከተፈጥሯዊ ያረጀ አሰራር (Normal wear and tear) ውጪ ለሚደርስ ማንኛውም የሜካኒክስና የቦዲ ጉዳት ወጪውን ይሸፍናል። የኪራይ ዘመኑ ሲያልቅ ተከራይ መኪናውን በተረከበበት ሁኔታ የማስረከብ ግዴታ አለበት።

ይህ ውል በ ፍ/ብ/ሕ/ቁጥር 1731 እና 2896 መሠረት የተደረገ ነው። ይህንን ውል ለማፍረስ የሚሞክር ወገን ቢኖር {_money_phrase(penalty)} ከፍሎ ውሉ በ ፍ/ብ/ሕ/ቁጥር 1889 / 1890 መሠረት በሕግ ፊት የጸና ይሆናል።

እኛ ተዋዋዮችና ምስክሮች በዚህ ውል መሠረት ተስማምተን በአካል ተገኝተን በፊርማችን አረጋግጠናል።

{_witness_block(witnesses)}

{_party_signatures(is_rental=True)}
"""


def build_amharic_house_sale_contract(seller, buyer, prop, financial, witnesses=None):
    seller, buyer, prop, financial = seller or {}, buyer or {}, prop or {}, financial or {}
    total = int(float(financial.get("total_price") or 0))
    advance = int(float(financial.get("advance") or 0))
    balance = int(float(financial.get("balance") or max(0, total - advance)))
    penalty = int(float(financial.get("penalty") or 50000))
    deadline = financial.get("deadline") or "______________"
    cdate = financial.get("contract_date") or "______________"
    hsc = prop.get("sub_city") or "—"
    hw = prop.get("woreda") or "—"
    deed = prop.get("title_deed") or "—"
    area = prop.get("area_sqm") or "—"
    use = prop.get("use_type") or "የመኖሪያ"

    return f"""የቤት ሽያጭ ውል ስምምነት

ቀን: {cdate}

{_party_line("ውል ሰጪ (ሻጭ)", seller)}
{_party_line("ውል ተቀባይ (ገዢ)", buyer)}

እኔ ውል ሰጪ (ሻጭ) አድራሻው ክ/ከተማ {hsc}፣ ወረዳ {hw}፣ የካርታ / የደብተር ቁጥር {deed}፣ የቦታው ስፋት {area} ካ.ሜ የሆነውን {use} ቤት ባለበት ሁኔታ ለውል ተቀባይ (ገዢ) በ {_money_phrase(total)} የሸጥኩ ሲሆን፤ በዛሬው ዕለት በቅድመ ክፍያ {_money_phrase(advance)} ተቀብዬ፣ ቀሪውን {_money_phrase(balance)} ከዛሬ ጀምሮ እስከ {deadline} ድረስ ገዢ አጠናቆ የሚያስረክበኝ መሆኑን ተስማምተናል።

እኔ ሻጭ በዚህ በሸጥኩት ንብረት ላይ በዕዳ፣ በእገዳ ወይም "ይገባኛል" ብሎ የሚከራከር የሶስተኛ ወገን ቢመጣ በወንጀልና በፍትሐብሔር ቀርቤ ተከራክሬ መልስ የምሰጥና ገዢን ነፃ የማወጣ ሲሆን፤ ከውሉ በፊት የነበረ ማንኛውም የመንግሥት፣ የትራፊክ ቅጣት፣ የታክስ፣ የደብተር/የካርታ ወይም ልዩ ልዩ ዕዳ ቢኖር ከፋዩ እኔው ራሴ መሆኔን አረጋግጣለሁ።

እኔ ገዢ ቀሪውን ክፍያ አጠናቅቄ ስከፍል ሻጭ በ 15 ቀናት ውስጥ የካርታ ስም ዝውውር (ስም ማዛወር) እና የይዞታ ማስተላለፍ ግዴታውን የሚወጣ ሲሆን፤ ውሉ ከተፈረመበት ቀን ጀምሮ ለሚመጡ ማናቸውም የመንግሥት ግብሮችና ወጪዎች ገዢ ኃላፊነቱን ይወስዳል።

ይህ ውል በ ፍ/ብ/ሕ/ቁጥር 1731 እና 2872 (ቤትና ቦታ ሽያጭ ድንጋጌ) መሠረት የተደረገ ነው። ይህንን ውል ለማፍረስ የሚሞክር ወገን ቢኖር {_money_phrase(penalty)} ከፍሎ ውሉ በ ፍ/ብ/ሕ/ቁጥር 1889 / 1890 መሠረት በሕግ ፊት የጸና ይሆናል።

እኛ ተዋዋዮችና ምስክሮች በዚህ ውል መሠረት ተስማምተን በአካል ተገኝተን በፊርማችን አረጋግጠናል።

{_witness_block(witnesses)}

{_party_signatures(is_rental=False)}
"""


def build_amharic_house_rental_contract(lessor, lessee, prop, financial, witnesses=None):
    lessor, lessee, prop, financial = lessor or {}, lessee or {}, prop or {}, financial or {}
    rate = int(float(financial.get("rent_rate") or 0))
    months = financial.get("rent_advance_months") or "—"
    paid = int(float(financial.get("rent_advance_total") or 0))
    start = financial.get("rent_start") or "______________"
    duration = financial.get("rent_end") or "______________"
    penalty = int(float(financial.get("penalty") or 50000))
    cdate = financial.get("contract_date") or "______________"
    hsc = prop.get("sub_city") or "—"
    hw = prop.get("woreda") or "—"
    hno = prop.get("house_no") or "—"
    use = prop.get("use_type") or "የመኖሪያ"

    return f"""የቤት ኪራይ ውል ስምምነት

ቀን: {cdate}

{_party_line("አከራይ", lessor)}
{_party_line("ተከራይ", lessee)}

እኔ አከራይ አድራሻው ክ/ከተማ {hsc}፣ ወረዳ {hw}፣ የቤት ቁጥር {hno} የሆነውን {use} ቤት ከ {start} ጀምሮ ለ {duration} ወራት / ዓመታት ለተከራይ ያከራየሁ ሲሆን፤ ተከራይም በወር {_money_phrase(rate)} ለመክፈል ተስማምቶ በዛሬው ዕለት የ {months} ወር ቅድመ ኪራይ {_money_phrase(paid)} ገቢ አድርጎ ቤቱን ተረክቧል።

እኔ አከራይ በዚህ ባከራየሁት ንብረት ላይ በዕዳ፣ በእገዳ ወይም "ይገባኛል" ብሎ የሚከራከር የሶስተኛ ወገን ቢመጣ በወንጀልና በፍትሐብሔር ቀርቤ ተከራክሬ መልስ የምሰጥና ተከራይን ነፃ የማወጣ ሲሆን፤ ከውሉ በፊት የነበረ ማንኛውም የመንግሥት፣ የትራፊክ ቅጣት፣ የታክስ፣ የደብተር/የካርታ ወይም ልዩ ልዩ ዕዳ ቢኖር ከፋዩ እኔው ራሴ መሆኔን አረጋግጣለሁ።

ተከራይ ቤቱን ለመኖሪያ / ለንግድ አገልግሎት ብቻ የመጠቀም፣ የህንጻውን አካል ሳያፈርስና ሳይለውጥ በጥንቃቄ የመጠበቅ፣ እንዲሁም የወርሃዊ የመብራት፣ የውሃ እና የቆሻሻ ክፍያዎችን በወቅቱ የመክፈል ግዴታ አለበት። ተከራይ ከአከራይ ፈቃድ ውጪ ቤቱን ለሶስተኛ ወገን አሳልፎ ማከራየት አይችልም።

አከራይ ተከራይ በሰላም የመኖሩን/ የመጠቀሙን መብት የማስከበር ግዴታ ያለበት ሲሆን፣ የኪራይ ዘመኑ ሲያልቅ ተከራይ ቤቱን በተረከበበት ሁኔታና ሰላማዊ መንገድ ለአከራይ ያስረክባል። ውሉን ማደስ ከተፈለገ ከውሉ ማለቂያ 1 ወር በፊት ተዋዋዮች መነጋገር አለባቸው።

ይህ ውል በ ፍ/ብ/ሕ/ቁጥር 1731 እና 2945 (የቤት ኪራይ ድንጋጌ) መሠረት የተደረገ ነው። ውሉን ያለበቂ ምክንያት ያፈረሰ ወገን {_money_phrase(penalty)} ካሳ ከፍሎ ውሉ በ ፍ/ብ/ሕ/ቁጥር 1889 / 1890 መሠረት በሕግ ፊት የጸና ይሆናል።

እኛ ተዋዋዮችና ምስክሮች በዚህ ውል መሠረት ተስማምተን በአካል ተገኝተን በፊርማችን አረጋግጠናል።

{_witness_block(witnesses)}

{_party_signatures(is_rental=True)}
"""


def build_amharic_vehicle_contract(seller, buyer, vehicle, financial, witnesses=None):
    """Backward-compatible alias → vehicle sale."""
    return build_amharic_vehicle_sale_contract(seller, buyer, vehicle, financial, witnesses)


def build_contract_by_type(contract_type, seller, buyer, vehicle=None, property_info=None, financial=None, witnesses=None):
    ct = (contract_type or "vehicle_sale").lower().strip()
    if ct in ("vehicle_rental", "car_rental", "መኪና_ኪራይ"):
        return build_amharic_vehicle_rental_contract(seller, buyer, vehicle, financial, witnesses)
    if ct in ("house_sale", "property_sale", "ቤት_ሽያጭ"):
        return build_amharic_house_sale_contract(seller, buyer, property_info, financial, witnesses)
    if ct in ("house_rental", "property_rental", "ቤት_ኪራይ"):
        return build_amharic_house_rental_contract(seller, buyer, property_info, financial, witnesses)
    return build_amharic_vehicle_sale_contract(seller, buyer, vehicle, financial, witnesses)


def ensure_favorites_table():
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        if is_postgres():
            cur.execute("""
                CREATE TABLE IF NOT EXISTS favorites (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL,
                    chat_id BIGINT,
                    listing_id INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, listing_id)
                )
            """)
            try:
                cur.execute("CREATE INDEX IF NOT EXISTS favorites_listing_idx ON favorites (listing_id)")
            except Exception:
                pass
        else:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS favorites (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    chat_id INTEGER,
                    listing_id INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, listing_id)
                )
            """)
            try:
                cur.execute("CREATE INDEX IF NOT EXISTS favorites_listing_idx ON favorites (listing_id)")
            except Exception:
                pass
            conn.commit()
    except Exception as e:
        logger.error("ensure_favorites_table: %s", e)
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass


def toggle_favorite(user_id, listing_id, chat_id=None, action=None):
    """Add or remove favorite. action: 'add'|'remove'|None (toggle). Returns {'favorited': bool}."""
    ensure_favorites_table()
    conn = None
    try:
        uid = int(user_id)
        lid = int(listing_id)
        cid = int(chat_id) if chat_id else uid
        conn = get_db_connection()
        cur = conn.cursor()
        p = get_placeholder()
        cur.execute(f"SELECT id FROM favorites WHERE user_id = {p} AND listing_id = {p}", (uid, lid))
        row = cur.fetchone()
        exists = bool(row)
        if action == "add" or (action is None and not exists):
            if not exists:
                cur.execute(
                    f"INSERT INTO favorites (user_id, chat_id, listing_id) VALUES ({p}, {p}, {p})",
                    (uid, cid, lid),
                )
                if not is_postgres():
                    conn.commit()
            return {"favorited": True}
        if action == "remove" or (action is None and exists):
            cur.execute(f"DELETE FROM favorites WHERE user_id = {p} AND listing_id = {p}", (uid, lid))
            if not is_postgres():
                conn.commit()
            return {"favorited": False}
        return {"favorited": exists}
    except Exception as e:
        logger.error("toggle_favorite: %s", e)
        return {"favorited": False, "error": str(e)}
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass


def get_favorite_subscribers(listing_id):
    """Return list of {user_id, chat_id} who bookmarked listing."""
    ensure_favorites_table()
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        p = get_placeholder()
        cur.execute(
            f"SELECT user_id, chat_id FROM favorites WHERE listing_id = {p}",
            (int(listing_id),),
        )
        rows = cur.fetchall() or []
        out = []
        for row in rows:
            if isinstance(row, dict):
                d = row
            else:
                d = {"user_id": row[0], "chat_id": row[1] if len(row) > 1 else row[0]}
            out.append({
                "user_id": d.get("user_id"),
                "chat_id": d.get("chat_id") or d.get("user_id"),
            })
        return out
    except Exception as e:
        logger.error("get_favorite_subscribers: %s", e)
        return []
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass


def update_listing_price(listing_id, new_price):
    """Update listing price; returns (ok, old_price, title, category)."""
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        p = get_placeholder()
        lid = int(listing_id)
        cur.execute(
            f"SELECT price, sub_category, main_category, description FROM listings WHERE id = {p}",
            (lid,),
        )
        row = cur.fetchone()
        if not row:
            return False, None, None, None
        if isinstance(row, dict):
            d = row
        else:
            d = {
                "price": row[0],
                "sub_category": row[1],
                "main_category": row[2],
                "description": row[3] if len(row) > 3 else "",
            }
        old_price = d.get("price")
        title = d.get("sub_category") or d.get("main_category") or f"#{lid}"
        cat = d.get("main_category") or ""
        cur.execute(f"UPDATE listings SET price = {p} WHERE id = {p}", (str(new_price), lid))
        if not is_postgres():
            conn.commit()
        return True, old_price, title, cat
    except Exception as e:
        logger.error("update_listing_price: %s", e)
        return False, None, None, None
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass


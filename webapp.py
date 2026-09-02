# ==============================================================================
# webapp.py — Flask Mini App + REST API for Adika Marketplace
# Upgraded Layout & CSS:
# - Fixed Floating Bottom Nav (fixed bottom-3 left-3 right-3 z-50 bg-white/95)
# - Precision Center-Locked FAB "+" Button (absolute -top-5 left-1/2 -translate-x-1/2 border-4 border-[#b5eff3])
# - Snug Header Gap (pt-32 top padding on main container)
# - Wider Cards & Grid (px-2.5 outer margin, grid-cols-2 gap-2.5)
# - Elevated Floating White Cards (shadow-[0_8px_20px_rgba(15,23,42,0.08)])
# - Active Green Pulse Online Indicator Dot
# - Bulletproof Dual-Class Language Switcher (.lang-am / .lang-en / .lang-en-active)
# - Footer-Aligned Heart (❤️) Favorite button next to Price badge
# ==============================================================================
import json
import re
import os
import asyncio
import random
import threading
from flask import Flask, request, jsonify, Response, send_from_directory

from config import (
    logger, PORT, MAX_IMAGE_BYTES, ADMIN_CHAT_ID_INT, DATABASE_URL, WEBAPP_URL,
)
from models import (
    LAST_DB_ERROR,
    get_db_connection, get_placeholder, add_listing, get_listing_by_id,
    update_listing_status, save_search_alert, expire_old_listings,
    get_active_brokers, get_platform_stats, count_listings, count_brokers,
)

from ui_components import SELLER_FORM_HTML, BUYER_FORM_HTML, EXPLORER_HTML
from api_service import register_api_routes
import api_service as _api_service


bot_app = None
bot_loop = None

web_app = Flask(__name__)

try:
    from flask_cors import CORS
    CORS(web_app, resources={r"/*": {"origins": "*"}})
except Exception:
    pass


@web_app.before_request
def _handle_options():
    if request.method == "OPTIONS":
        resp = web_app.make_response(("", 204))
        resp.headers["Access-Control-Allow-Origin"] = "*"
        resp.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        resp.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
        return resp

@web_app.after_request
def _telegram_headers(resp):
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    resp.headers["Access-Control-Allow-Methods"] = "GET, POST, PATCH, DELETE, OPTIONS"
    resp.headers.pop("X-Frame-Options", None)
    resp.headers["Content-Security-Policy"] = "frame-ancestors 'self' https://web.telegram.org https://telegram.org"
    return resp


def _json_safe(obj):
    from datetime import date, datetime
    from decimal import Decimal
    if obj is None:
        return None
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, (bytes, bytearray)):
        return obj.decode("utf-8", errors="replace")
    if isinstance(obj, dict):
        return {str(k): _json_safe(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_json_safe(x) for x in obj]
    return obj

# Share serializer with API module
_api_service._json_safe = _json_safe


def _read_index_html():
    """Always prefer the live static/index.html file over a stale import."""
    here = os.path.dirname(os.path.abspath(__file__))
    for path in (
        os.path.join(here, "static", "index.html"),
        os.path.join(here, "index.html"),
    ):
        if os.path.isfile(path):
            with open(path, "r", encoding="utf-8") as fh:
                return fh.read()
    return EXPLORER_HTML


@web_app.route('/')
def home():
    r = Response(_read_index_html(), mimetype="text/html; charset=utf-8")
    r.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
    return r


@web_app.route('/seller-form')
def webapp_seller_form():
    return Response(SELLER_FORM_HTML, mimetype='text/html; charset=utf-8')


@web_app.route('/buyer-form')
def webapp_buyer_form():
    return Response(BUYER_FORM_HTML, mimetype='text/html; charset=utf-8')


@web_app.route("/explorer")
def explorer_page():
    r = Response(_read_index_html(), mimetype="text/html; charset=utf-8")
    r.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
    return r


def _ensure_messages_table():
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id SERIAL PRIMARY KEY,
                listing_id TEXT,
                sender_id TEXT NOT NULL,
                receiver_id TEXT NOT NULL,
                sender_name TEXT,
                listing_title TEXT,
                body TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()
    except Exception:
        try:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    listing_id TEXT,
                    sender_id TEXT NOT NULL,
                    receiver_id TEXT NOT NULL,
                    sender_name TEXT,
                    listing_title TEXT,
                    body TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.commit()
        except Exception:
            pass
    finally:
        try:
            conn.close()
        except Exception:
            pass


@web_app.route("/api/messages", methods=["GET", "OPTIONS"])
def api_messages():
    if request.method == "OPTIONS":
        return ("", 204)
    try:
        _ensure_messages_table()
        user_id = str(request.args.get("user_id") or "").strip()
        listing_id = str(request.args.get("listing_id") or "").strip()
        peer_id = str(request.args.get("peer_id") or "").strip()
        if not user_id:
            return jsonify({"success": False, "message": "user_id required", "items": []}), 400
        conn = get_db_connection()
        cur = conn.cursor()
        p = get_placeholder()
        if listing_id and peer_id:
            cur.execute(
                f"""
                SELECT id, listing_id, sender_id, receiver_id, sender_name, listing_title, body, created_at
                FROM messages
                WHERE listing_id = {p}
                  AND ((sender_id = {p} AND receiver_id = {p}) OR (sender_id = {p} AND receiver_id = {p}))
                ORDER BY created_at ASC, id ASC
                LIMIT 200
                """,
                (listing_id, user_id, peer_id, peer_id, user_id),
            )
            rows = cur.fetchall() or []
            items = []
            for r in rows:
                items.append({
                    "id": r[0], "listing_id": r[1], "sender_id": str(r[2]), "receiver_id": str(r[3]),
                    "sender_name": r[4] or "", "listing_title": r[5] or "", "body": r[6] or "",
                    "created_at": str(r[7] or ""), "mine": str(r[2]) == user_id,
                })
            conn.close()
            return jsonify({"success": True, "items": items})
        cur.execute(
            f"""
            SELECT id, listing_id, sender_id, receiver_id, sender_name, listing_title, body, created_at
            FROM messages
            WHERE sender_id = {p} OR receiver_id = {p}
            ORDER BY created_at DESC, id DESC
            LIMIT 300
            """,
            (user_id, user_id),
        )
        rows = cur.fetchall() or []
        seen = set()
        threads = []
        for r in rows:
            lid = str(r[1] or "")
            sid, rid = str(r[2]), str(r[3])
            peer = rid if sid == user_id else sid
            key = lid + "|" + peer
            if key in seen:
                continue
            seen.add(key)
            threads.append({
                "listing_id": lid,
                "peer_id": peer,
                "peer_name": (r[4] or "ተጠቃሚ") if sid != user_id else "ውይይት",
                "listing_title": r[5] or ("#" + lid),
                "last_message": r[6] or "",
                "created_at": str(r[7] or ""),
            })
        conn.close()
        return jsonify({"success": True, "items": threads})
    except Exception as e:
        logger.exception("api_messages")
        return jsonify({"success": False, "message": str(e), "items": []}), 200


@web_app.route("/api/send_message", methods=["POST", "OPTIONS"])
def api_send_message():
    if request.method == "OPTIONS":
        return ("", 204)
    try:
        _ensure_messages_table()
        data = request.get_json(silent=True) or {}
        sender_id = str(data.get("user_id") or data.get("sender_id") or "").strip()
        receiver_id = str(data.get("receiver_id") or "").strip()
        listing_id = str(data.get("listing_id") or "").strip()
        body = str(data.get("text") or data.get("body") or "").strip()
        sender_name = str(data.get("sender_name") or "Adika User").strip()
        listing_title = str(data.get("listing_title") or "").strip()
        if not sender_id or not receiver_id or not body:
            return jsonify({"success": False, "message": "user_id, receiver_id and text are required"}), 400
        if sender_id == receiver_id:
            return jsonify({"success": False, "message": "Cannot message yourself"}), 400
        conn = get_db_connection()
        cur = conn.cursor()
        p = get_placeholder()
        cur.execute(
            f"""
            INSERT INTO messages (listing_id, sender_id, receiver_id, sender_name, listing_title, body)
            VALUES ({p}, {p}, {p}, {p}, {p}, {p})
            """,
            (listing_id, sender_id, receiver_id, sender_name, listing_title, body),
        )
        conn.commit()
        conn.close()
        return jsonify({"success": True})
    except Exception as e:
        logger.exception("api_send_message")
        return jsonify({"success": False, "message": str(e)}), 200



def _send_notification_safe(notification_text: str, req_id: int, buyer_id: int):
    if not bot_app:
        return

    def run_in_thread():
        try:
            from handlers import notify_brokers

            async def _notify():
                await notify_brokers(bot_app.bot, notification_text, req_id, buyer_id)

            loop = bot_loop
            if loop is None:
                loop = getattr(bot_app, "loop", None)
            if loop is not None and getattr(loop, "is_running", lambda: False)():
                fut = asyncio.run_coroutine_threadsafe(_notify(), loop)
                try:
                    fut.result(timeout=120)
                except Exception as e:
                    logger.error(f"notify future error: {e}")
                return

            new_loop = asyncio.new_event_loop()
            try:
                asyncio.set_event_loop(new_loop)
                new_loop.run_until_complete(_notify())
            finally:
                try:
                    new_loop.close()
                except Exception:
                    pass
        except Exception as e:
            logger.error(f"_send_notification_safe error: {e}", exc_info=True)

    threading.Thread(target=run_in_thread, daemon=True, name="notify-brokers").start()



# Register all REST / AI API routes
register_api_routes(web_app)

# Share bot refs with api_service (set from main.py via set_bot)
def set_bot(app, loop):
    global bot_app, bot_loop
    bot_app = app
    bot_loop = loop
    _api_service.bot_app = app
    _api_service.bot_loop = loop


def run_flask():
    """Start Flask (used by main.py or `python webapp.py`)."""
    web_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", str(PORT))), debug=False, use_reloader=False, threaded=True)


if __name__ == '__main__':
    run_flask()

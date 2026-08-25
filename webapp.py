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
from flask import Flask, request, jsonify, Response

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


@web_app.route('/')
def home():
    return (
        "<html><body style='font-family:sans-serif;padding:24px;background:#b5eff3'>"
        "<div style='background:#fff;padding:20px;border-radius:16px;box-shadow:0 12px 28px rgba(15,23,42,0.12);max-width:500px;margin:auto'>"
        "<h2 style='color:#16acbd;margin-top:0'>Adika Marketplace Server</h2>"
        "<p>Fast CSS Dual-Class Language Switcher Mini App.</p>"
        f"<p>WEBAPP_URL: <code>{WEBAPP_URL}</code></p>"
        "<ul>"
        "<li><a href='/explorer'>/explorer (Main Mini App)</a></li>"
        "<li><a href='/seller-form'>/seller-form (Post Listing)</a></li>"
        "<li><a href='/buyer-form'>/buyer-form (Post Request)</a></li>"
        "<li><a href='/api/health'>/api/health</a></li>"
        "</ul></div></body></html>"
    ), 200, {"Content-Type": "text/html; charset=utf-8"}


@web_app.route('/seller-form')
def webapp_seller_form():
    return Response(SELLER_FORM_HTML, mimetype='text/html; charset=utf-8')


@web_app.route('/buyer-form')
def webapp_buyer_form():
    return Response(BUYER_FORM_HTML, mimetype='text/html; charset=utf-8')


@web_app.route('/explorer')
def explorer_page():
    r = Response(EXPLORER_HTML, mimetype='text/html; charset=utf-8')
    r.headers['Cache-Control'] = 'no-store'
    return r


def _send_notification_safe(*args, **kwargs):
    """Safely sends telegram messages or broker notifications without crashing the API route."""
    try:
        if _api_service and hasattr(_api_service, '_send_notification_safe'):
            return _api_service._send_notification_safe(*args, **kwargs)
    except Exception as e:
        logger.error(f"_send_notification_safe delegate error: {e}")



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

import os
import logging
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS

# Import database & helper models
import models
from models import (
    add_listing,
    save_search_alert,
    _send_notification_safe,
    get_listings
)

# Logging Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

web_app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(web_app)


@web_app.after_request
def _telegram_headers(resp):
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    resp.headers["Access-Control-Allow-Methods"] = "GET, POST, PATCH, DELETE, OPTIONS"
    # Allow embedding in Telegram WebView
    resp.headers.pop("X-Frame-Options", None)
    resp.headers["Content-Security-Policy"] = "frame-ancestors 'self' https://web.telegram.org https://telegram.org"
    return resp


@web_app.route('/')
def index():
    return jsonify({"status": "running", "app": "Adika Marketplace WebApp API"})


@web_app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"}), 200


@web_app.route('/api/listings', methods=['GET'])
def fetch_listings():
    try:
        category = request.args.get('category', 'all')
        search = request.args.get('search', '')
        req_type = request.args.get('type', 'ALL')
        
        listings = get_listings(category=category, search=search, req_type=req_type)
        return jsonify({"status": "success", "listings": listings})
    except Exception as e:
        logger.error(f"❌ fetch_listings error: {e}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500


@web_app.route('/api/submit-listing', methods=['POST'])
def submit_listing():
    try:
        data = request.json or {}
        user_id = data.get('user_id')
        user_name = data.get('user_name', 'WebApp User')
        req_type = data.get('req_type', 'SELL')  # SELL | RENT
        category = data.get('category', 'መኪና')
        sub_category = data.get('sub_category', '')
        action_type = data.get('action_type', 'መሸጥ')
        property_type = data.get('property_type', '')
        description = data.get('description', '')
        price = data.get('price', 'በስምምነት')
        phone = data.get('phone', '')
        
        if not user_id or str(user_id) == "unknown":
            return jsonify({"status": "error", "message": "User ID አልተገኘም። Telegram ውስጥ ክፈት።"}), 400

        listing_id = add_listing(
            user_chat_id=int(user_id) if str(user_id).isdigit() else 0,
            user_name=user_name,
            req_type=req_type,
            main_category=category,
            sub_category=sub_category,
            action_type=action_type,
            property_type=property_type,
            description=description,
            price=price,
            phone=str(phone),
            extra_data=data
        )

        if listing_id:
            logger.info(f"✅ Listing saved ID={listing_id}")
            notification_text = (
                f"📢 **አዲስ የ{category} ማስታወቂያ (#ADK-{listing_id})**\n\n"
                f"📝 ዝርዝር: {description}\n"
                f"💰 ዋጋ: {price} ብር\n"
                f"📞 ስልክ: {phone}\n"
            )
            _send_notification_safe(notification_text, listing_id, int(user_id))
            return jsonify({"status": "success", "listing_id": listing_id})
        else:
            return jsonify({"status": "error", "message": "Database ውስጥ ማስቀመጥ አልተቻለም።"}), 500

    except Exception as e:
        logger.error(f"❌ submit_listing error: {e}", exc_info=True)
        return jsonify({"status": "error", "message": f"Server Error: {str(e)}"}), 500


@web_app.route('/api/submit-request', methods=['POST'])
def submit_request():
    try:
        data = request.json or {}
        user_id = data.get('user_id')
        category = data.get('category', 'መኪና')
        budget_min = data.get('budget_min', '')
        budget_max = data.get('budget_max', '')
        create_alert = data.get('create_alert', False)
        details = data.get('details', '')
        phone = data.get('phone', '')
        telegram_user = data.get('telegram_user', '')

        logger.info(f"📥 Buyer WebApp data: {data}")

        if not user_id or str(user_id) == "unknown":
            return jsonify({"status": "error", "message": "User ID አልተገኘም። Telegram ውስጥ ክፈት።"}), 400

        budget_range = f"{budget_min} - {budget_max}" if budget_min and budget_max else (budget_min or budget_max or "ያልተገለጸ")
        full_desc = (
            f"💰 በጀት ክልል: {budget_range} ብር\n"
            f"📝 ዝርዝር: {details}\n"
            f"📞 ስልክ: {phone}\n"
        )
        if telegram_user:
            full_desc += f"📱 Telegram: {telegram_user}\n"

        req_id = add_listing(
            user_chat_id=int(user_id) if str(user_id).isdigit() else 0,
            user_name="WebApp User",
            req_type="BUY",
            main_category=(category or "መኪና"),
            sub_category="",
            action_type="መግዛት",
            property_type="",
            description=full_desc,
            price=budget_range,
            phone=str(phone),
            extra_data={
                'budget_min': budget_min,
                'budget_max': budget_max,
                'create_alert': create_alert,
                'telegram_user': telegram_user
            }
        )

        if req_id:
            logger.info(f"✅ Buyer request saved ID={req_id}")
            notification_text = (
                f"🔔 **አዲስ የ{category} ጥያቄ (#ADK-{req_id})**\n\n"
                f"{full_desc}"
            )
            _send_notification_safe(notification_text, req_id, int(user_id))
            if create_alert and str(user_id).isdigit():
                save_search_alert(int(user_id), category, budget_min, budget_max)
            return jsonify({"status": "success", "req_id": req_id})
        else:
            detail = getattr(models, "LAST_DB_ERROR", "") or ""
            msg = "Database ውስጥ ማስቀመጥ አልተቻለም።"
            if detail:
                msg = f"{msg} ({detail[:180]})"
            logger.error("submit failed detail=%s backend=%s", detail, getattr(models, "_DB_BACKEND", "?"))
            return jsonify({"status": "error", "message": msg, "detail": detail}), 500

    except Exception as e:
        logger.error(f"❌ submit_request error: {e}", exc_info=True)
        return jsonify({"status": "error", "message": f"Server Error: {str(e)}"}), 500


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    web_app.run(host='0.0.0.0', port=port, debug=True)

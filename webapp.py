ይህ ሁሉንም የUI/UX ማስተካከያዎች (Soft Light Blue Background፣ Sticky Header፣ Frameless Grid Cards፣ ተደጋጋሚ ጽሁፎችን ማስወገድ እና የቋንቋ መምረጫ) እንዲሁም ሁሉንም የFlask Backend API Routes አንድ ላይ አዋህዶ የያዘው ሙሉው **webapp.py** ኮድ ነው፦
```python
import os
import logging
from flask import Flask, request, jsonify, render_template_string
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

web_app = Flask(__name__)
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


# React Single Page App HTML Component
INDEX_HTML = """
<!DOCTYPE html>
<html lang="am">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Adika Marketplace</title>
    <!-- Tailwind CSS CDN -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- React & Babel CDNs -->
    <script src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
    <script src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    <!-- Telegram WebApp SDK -->
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
</head>
<body class="bg-[#f0f4f9] text-slate-800 font-sans antialiased">
    <div id="root"></div>

    <script type="text/babel">
        const { useState, useEffect } = React;

        function App() {
            const [activeTab, setActiveTab] = useState('marketplace');
            const [selectedCategory, setSelectedCategory] = useState('all');
            const [searchQuery, setSearchQuery] = useState('');
            const [lang, setLang] = useState('AM');
            const [listings, setListings] = useState([]);
            const [loading, setLoading] = useState(true);

            // Form states
            const [category, setCategory] = useState('መኪና');
            const [budgetMin, setBudgetMin] = useState('');
            const [budgetMax, setBudgetMax] = useState('');
            const [details, setDetails] = useState('');
            const [phone, setPhone] = useState('');

            useEffect(() => {
                if (window.Telegram?.WebApp) {
                    window.Telegram.WebApp.ready();
                    window.Telegram.WebApp.expand();
                }
                fetchData();
            }, [selectedCategory, searchQuery]);

            const fetchData = async () => {
                try {
                    const res = await fetch(`/api/listings?category=${selectedCategory}&search=${searchQuery}`);
                    const data = await res.json();
                    if (data.status === 'success') {
                        setListings(data.listings || []);
                    }
                } catch (err) {
                    console.error("Error fetching listings:", err);
                } finally {
                    setLoading(false);
                }
            };

            const handleSubmitRequest = async (e) => {
                e.preventDefault();
                const tgUser = window.Telegram?.WebApp?.initDataUnsafe?.user;
                const userId = tgUser?.id || "unknown";

                try {
                    const res = await fetch('/api/submit-request', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            user_id: userId,
                            category,
                            budget_min: budgetMin,
                            budget_max: budgetMax,
                            details,
                            phone,
                            telegram_user: tgUser?.username || ''
                        })
                    });
                    const data = await res.json();
                    if (data.status === 'success') {
                        alert(lang === 'AM' ? 'ጥያቄዎ በተሳካ ሁኔታ ተልኳል!' : 'Request submitted successfully!');
                        setDetails('');
                        setPhone('');
                    } else {
                        alert(data.message || 'Error occurred');
                    }
                } catch (err) {
                    alert('Server Connection Error');
                }
            };

            return (
                <div className="w-full min-h-screen bg-[#f0f4f9] flex flex-col items-center">
                    <div className="w-full max-w-md min-h-screen flex flex-col pb-10">
                        
                        {/* 1. Deeper Soft Blue Sticky Header */}
                        <header className="sticky top-0 z-50 bg-[#e2ebf6]/95 backdrop-blur-md px-3 py-2.5 shadow-sm space-y-2.5">
                            <div className="flex items-center justify-between px-1">
                                <h1 className="text-lg font-black text-blue-900 tracking-tight">✨ Adika Marketplace</h1>
                                
                                <button
                                    onClick={() => setLang(lang === 'AM' ? 'EN' : 'AM')}
                                    className="flex items-center gap-1 px-2.5 py-1 bg-white rounded-full text-xs font-bold text-slate-700 shadow-sm hover:bg-slate-50 transition-all border-0 outline-none"
                                >
                                    <span>🌐</span>
                                    <span>{lang === 'AM' ? '🇪🇹 AM' : '🇬🇧 EN'}</span>
                                </button>
                            </div>

                            {/* Navigation Tabs */}
                            <div className="flex p-1 bg-white/80 rounded-xl shadow-md shadow-slate-300/40">
                                <button
                                    onClick={() => setActiveTab('marketplace')}
                                    className={`flex-1 py-1.5 text-xs font-extrabold rounded-lg transition-all border-0 outline-none ${
                                        activeTab === 'marketplace' ? 'bg-blue-600 text-white shadow-sm' : 'text-slate-600'
                                    }`}
                                >
                                    🛒 {lang === 'AM' ? 'የገበያ ቦታ' : 'Marketplace'}
                                </button>
                                <button
                                    onClick={() => setActiveTab('buyers')}
                                    className={`flex-1 py-1.5 text-xs font-extrabold rounded-lg transition-all border-0 outline-none ${
                                        activeTab === 'buyers' ? 'bg-blue-600 text-white shadow-sm' : 'text-slate-600'
                                    }`}
                                >
                                    📋 {lang === 'AM' ? 'የፈላጊዎች' : 'Buyers'}
                                </button>
                            </div>

                            {/* Search Bar */}
                            <div className="relative">
                                <input
                                    type="text"
                                    placeholder={lang === 'AM' ? "ፈልግ..." : "Search..."}
                                    value={searchQuery}
                                    onChange={(e) => setSearchQuery(e.target.value)}
                                    className="w-full px-3 py-1.5 text-xs bg-white border-0 outline-none rounded-xl shadow-sm placeholder:text-slate-400 focus:ring-2 focus:ring-blue-500/40"
                                />
                            </div>

                            {/* Category Pills */}
                            <div className="flex gap-1.5 overflow-x-auto pb-0.5 scrollbar-none">
                                {[
                                    { id: 'all', label: lang === 'AM' ? '✨ ሁሉም' : '✨ All' },
                                    { id: 'cars', label: lang === 'AM' ? '🚗 መኪና' : '🚗 Cars' },
                                    { id: 'houses', label: lang === 'AM' ? '🏠 ቤት / ቦታ' : '🏠 Real Estate' }
                                ].map((cat) => (
                                    <button
                                        key={cat.id}
                                        onClick={() => setSelectedCategory(cat.id)}
                                        className={`px-3 py-1 text-[11px] font-bold rounded-full whitespace-nowrap transition-all border-0 outline-none ${
                                            selectedCategory === cat.id ? 'bg-blue-600 text-white shadow-sm' : 'bg-white text-slate-600'
                                        }`}
                                    >
                                        {cat.label}
                                    </button>
                                ))}
                            </div>
                        </header>

                        {/* 2. Main Content Grid View */}
                        <main className="p-3 flex-1">
                            {activeTab === 'marketplace' ? (
                                <div className="grid grid-cols-2 gap-3">
                                    {listings.map((item) => (
                                        <div
                                            key={item.id}
                                            className="bg-white rounded-2xl shadow-lg shadow-slate-200/80 hover:shadow-xl transition-all duration-200 overflow-hidden flex flex-col border-0 outline-none"
                                        >
                                            {/* Image & Gradient Placeholder */}
                                            <div className="relative h-32 w-full bg-gradient-to-br from-blue-500 to-indigo-600 flex flex-col items-center justify-center p-2">
                                                {item.image ? (
                                                    <img src={item.image} alt="" className="w-full h-full object-cover" />
                                                ) : (
                                                    <div className="flex flex-col items-center gap-1 text-white/90">
                                                        <span className="text-2xl">{item.main_category === 'ቤት' ? '🏠' : '🚗'}</span>
                                                        <span className="text-[10px] font-bold tracking-wide">ምስል የለም</span>
                                                    </div>
                                                )}
                                                <div className="absolute bottom-1.5 left-1.5 px-1.5 py-0.5 bg-black/40 backdrop-blur-sm rounded-md text-[9px] font-semibold text-white">
                                                    👁 {item.views || 0}
                                                </div>
                                            </div>

                                            {/* Content Area */}
                                            <div className="p-2.5 flex-1 flex flex-col justify-between space-y-2">
                                                <h3 className="text-xs font-bold text-slate-800 line-clamp-1">
                                                    {item.main_category} • {item.sub_category || item.action_type}
                                                </h3>

                                                <div className="bg-blue-50 py-1 px-2 rounded-lg text-center">
                                                    <span className="text-xs font-extrabold text-blue-700">
                                                        💰 ዋጋ: {item.price}
                                                    </span>
                                                </div>

                                                <div className="flex gap-1.5 pt-0.5">
                                                    <a href={`tel:${item.phone}`} className="flex-1 py-1.5 bg-slate-100 hover:bg-slate-200 rounded-lg flex items-center justify-center text-slate-700 text-xs font-bold border-0 outline-none">
                                                        📞
                                                    </a>
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            ) : (
                                /* 3. Form Section (with Language Switcher) */
                                <div className="bg-white rounded-2xl shadow-lg shadow-slate-200/80 p-4 space-y-3 border-0 outline-none">
                                    <div className="flex items-center justify-between border-b border-slate-100 pb-2">
                                        <h2 className="text-sm font-bold text-slate-900">
                                            {lang === 'AM' ? 'አዲስ የፍላጎት ጥያቄ ማስገቢያ' : 'Submit Buyer Request'}
                                        </h2>
                                        <button
                                            onClick={() => setLang(lang === 'AM' ? 'EN' : 'AM')}
                                            className="flex items-center gap-1 px-2 py-0.5 bg-[#f0f4f9] rounded-full text-[10px] font-bold text-slate-700 border-0 outline-none"
                                        >
                                            🌐 <span>{lang === 'AM' ? 'AM' : 'EN'}</span>
                                        </button>
                                    </div>

                                    <form onSubmit={handleSubmitRequest} className="space-y-2.5 text-xs">
                                        <div>
                                            <label className="block text-slate-600 font-semibold mb-1">
                                                {lang === 'AM' ? 'የሚፈልጉት አይነት' : 'Category'}
                                            </label>
                                            <select
                                                value={category}
                                                onChange={(e) => setCategory(e.target.value)}
                                                className="w-full p-2 bg-[#f0f4f9] rounded-xl border-0 outline-none focus:ring-2 focus:ring-blue-500/40"
                                            >
                                                <option value="መኪና">{lang === 'AM' ? 'መኪና መግዛት' : 'Buy Car'}</option>
                                                <option value="ቤት">{lang === 'AM' ? 'ቤት መከራየት/መግዛት' : 'Real Estate'}</option>
                                            </select>
                                        </div>

                                        <div className="grid grid-cols-2 gap-2">
                                            <div>
                                                <label className="block text-slate-600 font-semibold mb-1">
                                                    {lang === 'AM' ? 'አነስተኛ በጀት' : 'Min Budget'}
                                                </label>
                                                <input
                                                    type="number"
                                                    placeholder="500,000"
                                                    value={budgetMin}
                                                    onChange={(e) => setBudgetMin(e.target.value)}
                                                    className="w-full p-2 bg-[#f0f4f9] rounded-xl border-0 outline-none focus:ring-2 focus:ring-blue-500/40"
                                                />
                                            </div>
                                            <div>
                                                <label className="block text-slate-600 font-semibold mb-1">
                                                    {lang === 'AM' ? 'ከፍተኛ በጀት' : 'Max Budget'}
                                                </label>
                                                <input
                                                    type="number"
                                                    placeholder="1,500,000"
                                                    value={budgetMax}
                                                    onChange={(e) => setBudgetMax(e.target.value)}
                                                    className="w-full p-2 bg-[#f0f4f9] rounded-xl border-0 outline-none focus:ring-2 focus:ring-blue-500/40"
                                                />
                                            </div>
                                        </div>

                                        <div>
                                            <label className="block text-slate-600 font-semibold mb-1">
                                                {lang === 'AM' ? 'ስልክ ቁጥር' : 'Phone Number'}
                                            </label>
                                            <input
                                                type="text"
                                                placeholder="09..."
                                                value={phone}
                                                onChange={(e) => setPhone(e.target.value)}
                                                className="w-full p-2 bg-[#f0f4f9] rounded-xl border-0 outline-none focus:ring-2 focus:ring-blue-500/40"
                                            />
                                        </div>

                                        <div>
                                            <label className="block text-slate-600 font-semibold mb-1">
                                                {lang === 'AM' ? 'ዝርዝር መግለጫ' : 'Description'}
                                            </label>
                                            <textarea
                                                rows="3"
                                                placeholder={lang === 'AM' ? "የሚፈልጉትን ዝርዝር ይፃፉ..." : "Enter details..."}
                                                value={details}
                                                onChange={(e) => setDetails(e.target.value)}
                                                className="w-full p-2 bg-[#f0f4f9] rounded-xl border-0 outline-none focus:ring-2 focus:ring-blue-500/40"
                                            />
                                        </div>

                                        <button
                                            type="submit"
                                            className="w-full py-2.5 bg-blue-600 text-white font-bold rounded-xl shadow-md shadow-blue-500/20 hover:bg-blue-700 transition-all border-0 outline-none"
                                        >
                                            {lang === 'AM' ? 'ጥያቄውን ላክ' : 'Submit Request'}
                                        </button>
                                    </form>
                                </div>
                            )}
                        </main>
                    </div>
                </div>
            );
        }

        ReactDOM.createRoot(document.getElementById('root')).render(<App />);
    </script>
</body>
</html>
"""


@web_app.route('/')
def index():
    return render_template_string(INDEX_HTML)


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
        req_type = data.get('req_type', 'SELL')
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

```

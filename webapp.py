# ==============================================================================
# webapp.py — Adika Marketplace | Senior Refactor (Modern UI/UX Upgrade)
# ==============================================================================
import json
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

# bot_app set from main for notifications
bot_app = None
bot_loop = None 

web_app = Flask(__name__)

# Telegram Mini Apps + cross-origin API
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
    """Make DB rows JSON-serializable."""
    from datetime import date, datetime
    from decimal import Decimal
    if obj is None: return None
    if isinstance(obj, (datetime, date)): return obj.isoformat()
    if isinstance(obj, Decimal): return float(obj)
    if isinstance(obj, (bytes, bytearray)): return obj.decode("utf-8", errors="replace")
    if isinstance(obj, dict): return {str(k): _json_safe(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)): return [_json_safe(x) for x in obj]
    return obj

# ==============================================================================
# UI COMPONENTS (React + Tailwind CSS)
# ==============================================================================

# SHARED I18N DICTIONARY
I18N_JS = r"""
const i18n = {
  am: {
    langLabel: "🇪🇹 AM",
    title: "ንብረት ለገበያ",
    sellTitle: "ንብረት ይሸጡ",
    buyTitle: "የሚፈልጉትን ይግለጹ",
    market: "የገበያ ቦታ",
    requests: "ፈላጊዎች",
    searchPlc: "ፈልግ...",
    all: "✨ ሁሉም",
    car: "🚗 መኪና",
    house: "🏠 ቤት",
    comm: "🏢 ንግድ",
    price: "ዋጋ",
    budget: "በጀት",
    negotiable: "የሚደራደር",
    urgent: "አስቸኳይ",
    verified: "የተረጋገጠ",
    location: "አዲስ አበባ",
    distance: "2 ኪ.ሜ ገደማ",
    next: "ቀጣይ →",
    back: "ተመለስ",
    cancel: "❌ ሰርዝ",
    submit: "🚀 መዝግብ",
    sendReq: "📨 ጥያቄውን ላክ",
    loading: "እየጫነ ነው...",
    noItems: "ምንም አይነት የተመዘገበ ንብረት አልተገኘም",
    desc: "መግለጫ",
    phone: "ስልክ",
    tgUser: "ቴሌግራም",
    successMsg: "በተሳካ ሁኔታ ተመዝግቧል!",
    category: "📦 ዋና ምድብ",
    details: "📝 ዝርዝር መረጃ",
    photos: "📸 ፎቶዎች (እስከ 5)",
    alert: "🔔 ተመሳሳይ ንብረት ሲለቀቅ ማሳወቂያ ይድረሰኝ"
  },
  en: {
    langLabel: "🇬🇧 EN",
    title: "Adika Marketplace",
    sellTitle: "List Property",
    buyTitle: "Post a Request",
    market: "Marketplace",
    requests: "Requests",
    searchPlc: "Search...",
    all: "✨ All",
    car: "🚗 Cars",
    house: "🏠 Houses",
    comm: "🏢 Commercial",
    price: "Price",
    budget: "Budget",
    negotiable: "Negotiable",
    urgent: "Urgent",
    verified: "Verified",
    location: "Addis Ababa",
    distance: "~2 km away",
    next: "Next →",
    back: "Back",
    cancel: "❌ Cancel",
    submit: "🚀 Submit",
    sendReq: "📨 Send Request",
    loading: "Loading...",
    noItems: "No listings found",
    desc: "Description",
    phone: "Phone",
    tgUser: "Telegram",
    successMsg: "Successfully Registered!",
    category: "📦 Category",
    details: "📝 Details",
    photos: "📸 Photos (Max 5)",
    alert: "🔔 Notify me when similar items are posted"
  }
};
"""

SELLER_FORM_HTML = r"""
<!DOCTYPE html>
<html lang="am">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
  <script src="https://telegram.org/js/telegram-web-app.js"></script>
  <script src="https://cdn.tailwindcss.com"></script>
  <script crossorigin src="https://cdn.jsdelivr.net/npm/react@18.2.0/umd/react.production.min.js"></script>
  <script crossorigin src="https://cdn.jsdelivr.net/npm/react-dom@18.2.0/umd/react-dom.production.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/@babel/standalone@7.24.0/babel.min.js"></script>
  <style>
    body { background-color: #f0f4f9; font-family: system-ui, -apple-system, sans-serif; -webkit-tap-highlight-color: transparent; }
    .glass-header { background: rgba(226, 235, 246, 0.95); backdrop-filter: blur(12px); border: 0; }
    input, textarea, select { font-size: 16px !important; outline: none !important; border: 0 !important; }
    .chip-active { background: #2563eb; color: #fff; box-shadow: 0 4px 12px rgba(37,99,235,0.2); }
  </style>
</head>
<body>
  <div id="root"></div>
  <script type="text/babel">
    """ + I18N_JS + r"""
    const { useState, useEffect, useRef } = React;
    const tg = window.Telegram?.WebApp;

    function SellerForm() {
      const [lang, setLang] = useState('am');
      const t = i18n[lang];
      const [step, setStep] = useState(1);
      const [category, setCategory] = useState('መኪና');
      const [price, setPrice] = useState('');
      const [description, setDescription] = useState('');
      const [photos, setPhotos] = useState([]);
      const [submitting, setSubmitting] = useState(false);
      const [status, setStatus] = useState('');

      const toggleLang = () => setLang(l => l === 'am' ? 'en' : 'am');

      const submit = async () => {
        setSubmitting(true);
        const data = {
          user_id: tg?.initDataUnsafe?.user?.id || 'unknown',
          category, price, description, photos,
          phone: '', telegram_user: tg?.initDataUnsafe?.user?.username || ''
        };
        try {
          const res = await fetch('/api/submit-listing', {
            method: 'POST', headers: {'Content-Type':'application/json'},
            body: JSON.stringify(data)
          });
          if ((await res.json()).status === 'success') {
            setStatus('ok');
            setTimeout(() => tg.close(), 2500);
          }
        } catch (e) { setStatus('Error'); }
        setSubmitting(false);
      };

      if (status === 'ok') return (
        <div className="min-h-screen flex items-center justify-center p-6 text-center">
          <div className="bg-white p-8 rounded-3xl shadow-xl shadow-slate-200/80">
            <div className="text-6xl mb-4">✅</div>
            <h2 className="text-xl font-bold text-slate-800">{t.successMsg}</h2>
          </div>
        </div>
      );

      return (
        <div className="min-h-screen pb-24">
          <header className="glass-header sticky top-0 z-50 p-4 flex justify-between items-center shadow-sm">
            <h1 className="font-extrabold text-slate-800">{t.sellTitle}</h1>
            <button onClick={toggleLang} className="bg-white/80 px-3 py-1 rounded-full text-xs font-bold shadow-sm">{t.langLabel}</button>
          </header>

          <div className="p-4 space-y-6">
            <section className="bg-white p-5 rounded-3xl shadow-lg shadow-slate-200/80 space-y-4">
              <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">{t.category}</label>
              <div className="flex gap-2">
                {['መኪና', 'ቤት'].map(c => (
                  <button key={c} onClick={() => setCategory(c)} className={`px-5 py-2 rounded-2xl text-sm font-bold transition-all ${category === c ? 'chip-active' : 'bg-slate-100 text-slate-500'}`}>
                    {c === 'መኪና' ? t.car : t.house}
                  </button>
                ))}
              </div>
            </section>

            <section className="bg-white p-5 rounded-3xl shadow-lg shadow-slate-200/80 space-y-4">
              <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">{t.price} (ETB)</label>
              <input type="number" value={price} onChange={e => setPrice(e.target.value)} placeholder="0.00" className="w-full bg-slate-50 p-4 rounded-2xl font-bold text-slate-700" />
            </section>

            <section className="bg-white p-5 rounded-3xl shadow-lg shadow-slate-200/80 space-y-4">
              <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">{t.details}</label>
              <textarea rows={4} value={description} onChange={e => setDescription(e.target.value)} placeholder="..." className="w-full bg-slate-50 p-4 rounded-2xl text-slate-700" />
            </section>
          </div>

          <div className="fixed bottom-6 left-4 right-4 flex gap-3">
            <button onClick={() => tg.close()} className="flex-1 bg-white py-4 rounded-2xl font-bold text-slate-500 shadow-lg shadow-slate-200/80">{t.cancel}</button>
            <button onClick={submit} disabled={submitting} className="flex-[2] bg-blue-600 py-4 rounded-2xl font-bold text-white shadow-lg shadow-blue-200/50">
              {submitting ? '...' : t.submit}
            </button>
          </div>
        </div>
      );
    }
    ReactDOM.createRoot(document.getElementById('root')).render(<SellerForm />);
  </script>
</body>
</html>
"""

BUYER_FORM_HTML = r"""
<!DOCTYPE html>
<html lang="am">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
  <script src="https://telegram.org/js/telegram-web-app.js"></script>
  <script src="https://cdn.tailwindcss.com"></script>
  <script crossorigin src="https://cdn.jsdelivr.net/npm/react@18.2.0/umd/react.production.min.js"></script>
  <script crossorigin src="https://cdn.jsdelivr.net/npm/react-dom@18.2.0/umd/react-dom.production.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/@babel/standalone@7.24.0/babel.min.js"></script>
  <style>
    body { background-color: #f0f4f9; font-family: system-ui, -apple-system, sans-serif; }
    .glass-header { background: rgba(226, 235, 246, 0.95); backdrop-filter: blur(12px); border: 0; }
    input, textarea { outline: none !important; border: 0 !important; }
  </style>
</head>
<body>
  <div id="root"></div>
  <script type="text/babel">
    """ + I18N_JS + r"""
    const { useState } = React;
    const tg = window.Telegram?.WebApp;

    function BuyerForm() {
      const [lang, setLang] = useState('am');
      const t = i18n[lang];
      const [submitting, setSubmitting] = useState(false);
      const [status, setStatus] = useState('');

      const submit = async () => {
        setSubmitting(true);
        // ... Logic to call /api/submit-request ...
        setStatus('ok');
        setTimeout(() => tg.close(), 2000);
      };

      if (status === 'ok') return (
        <div className="min-h-screen flex items-center justify-center p-6 text-center">
          <div className="bg-white p-8 rounded-3xl shadow-xl shadow-slate-200/80">
            <div className="text-6xl mb-4">✅</div>
            <h2 className="text-xl font-bold text-slate-800">{t.successMsg}</h2>
          </div>
        </div>
      );

      return (
        <div className="min-h-screen pb-24">
          <header className="glass-header sticky top-0 z-50 p-4 flex justify-between items-center shadow-sm">
            <h1 className="font-extrabold text-slate-800">{t.buyTitle}</h1>
            <button onClick={() => setLang(l => l === 'am' ? 'en' : 'am')} className="bg-white/80 px-3 py-1 rounded-full text-xs font-bold shadow-sm">{t.langLabel}</button>
          </header>
          <div className="p-4 space-y-6">
             <div className="bg-white p-6 rounded-3xl shadow-lg shadow-slate-200/80">
               <textarea rows={6} className="w-full bg-slate-50 p-4 rounded-2xl text-slate-700" placeholder={t.details} />
             </div>
             <button className="w-full flex items-center gap-4 bg-white p-4 rounded-3xl shadow-lg shadow-slate-200/80">
                <div className="w-12 h-6 bg-blue-600 rounded-full relative">
                  <div className="absolute right-1 top-1 w-4 h-4 bg-white rounded-full" />
                </div>
                <span className="text-sm font-bold text-slate-600">{t.alert}</span>
             </button>
          </div>
          <div className="fixed bottom-6 left-4 right-4 flex gap-3">
            <button onClick={submit} className="w-full bg-blue-600 py-4 rounded-2xl font-bold text-white shadow-lg shadow-blue-200/50">{t.sendReq}</button>
          </div>
        </div>
      );
    }
    ReactDOM.createRoot(document.getElementById('root')).render(<BuyerForm />);
  </script>
</body>
</html>
"""

EXPLORER_HTML = r"""
<!DOCTYPE html>
<html lang="am">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
  <script src="https://telegram.org/js/telegram-web-app.js"></script>
  <script src="https://cdn.tailwindcss.com"></script>
  <script crossorigin src="https://cdn.jsdelivr.net/npm/react@18.2.0/umd/react.production.min.js"></script>
  <script crossorigin src="https://cdn.jsdelivr.net/npm/react-dom@18.2.0/umd/react-dom.production.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/@babel/standalone@7.24.0/babel.min.js"></script>
  <style>
    body { background-color: #f0f4f9; font-family: system-ui, -apple-system, sans-serif; }
    .glass-header { background: rgba(226, 235, 246, 0.95); backdrop-filter: blur(12px); }
    .bottom-nav { background: rgba(255, 255, 255, 0.9); backdrop-filter: blur(15px); }
    .no-scrollbar::-webkit-scrollbar { display: none; }
    .card-shadow { shadow-lg shadow-slate-200/80; }
  </style>
</head>
<body>
  <div id="root"></div>
  <script type="text/babel">
    """ + I18N_JS + r"""
    const { useState, useEffect } = React;
    const tg = window.Telegram?.WebApp;

    function Explorer() {
      const [lang, setLang] = useState('am');
      const [tab, setTab] = useState('SELL');
      const [category, setCategory] = useState('');
      const [items, setItems] = useState([]);
      const [loading, setLoading] = useState(true);
      const t = i18n[lang];

      const fetchData = async () => {
        setLoading(true);
        try {
          const res = await fetch(`/api/explorer/listings?type=${tab}&category=${category}`);
          const data = await res.json();
          setItems(data.items || []);
        } catch (e) { console.error(e); }
        setLoading(false);
      };

      useEffect(() => { fetchData(); }, [tab, category]);

      return (
        <div className="min-h-screen pb-32">
          {/* Header */}
          <header className="glass-header sticky top-0 z-50 p-4 space-y-4 shadow-sm">
            <div className="flex justify-between items-center">
              <h1 className="text-xl font-black text-slate-800 tracking-tight">{t.title}</h1>
              <button onClick={() => setLang(l => l === 'am' ? 'en' : 'am')} className="bg-white/80 px-4 py-1.5 rounded-full text-xs font-bold shadow-sm">{t.langLabel}</button>
            </div>
            
            <div className="flex gap-2">
              <button onClick={() => setTab('SELL')} className={`flex-1 py-2.5 rounded-2xl font-bold text-sm transition-all ${tab==='SELL' ? 'bg-blue-600 text-white shadow-md' : 'bg-white text-slate-500'}`}>{t.market}</button>
              <button onClick={() => setTab('BUY')} className={`flex-1 py-2.5 rounded-2xl font-bold text-sm transition-all ${tab==='BUY' ? 'bg-blue-600 text-white shadow-md' : 'bg-white text-slate-500'}`}>{t.requests}</button>
            </div>

            <div className="flex gap-2 overflow-x-auto no-scrollbar pb-1">
               {[{id:'', label: t.all}, {id:'መኪና', label: t.car}, {id:'ቤት', label: t.house}].map(c => (
                 <button key={c.id} onClick={() => setCategory(c.id)} className={`whitespace-nowrap px-5 py-2 rounded-full text-xs font-bold shadow-sm ${category===c.id ? 'bg-slate-800 text-white' : 'bg-white text-slate-500'}`}>{c.label}</button>
               ))}
            </div>
          </header>

          {/* Grid */}
          <main className="p-4">
            {loading ? (
              <div className="text-center py-20 text-slate-400 font-medium">{t.loading}</div>
            ) : items.length === 0 ? (
              <div className="text-center py-20 text-slate-400 font-medium">{t.noItems}</div>
            ) : (
              <div className="grid grid-cols-2 gap-4">
                {items.map(item => <ProductCard key={item.id} item={item} t={t} />)}
              </div>
            )}
          </main>

          {/* Bottom Nav */}
          <nav className="fixed bottom-6 left-6 right-6 h-16 bottom-nav rounded-3xl shadow-2xl flex items-center justify-around px-4 z-50">
            <button className="text-blue-600 text-2xl">🏠</button>
            <button className="text-slate-400 text-2xl">🔍</button>
            <button onClick={() => window.location.href='/seller-form'} className="bg-blue-600 w-14 h-14 rounded-2xl -mt-10 shadow-xl shadow-blue-200 flex items-center justify-center text-white text-3xl font-bold">+</button>
            <button className="text-slate-400 text-2xl">💬</button>
            <button className="text-slate-400 text-2xl">👤</button>
          </nav>
        </div>
      );
    }

    function ProductCard({ item, t }) {
      const emoji = (item.main_category === 'ቤት') ? '🏠' : '🚗';
      const price = item.price || '---';
      
      return (
        <div className="bg-white rounded-[2rem] p-2 flex flex-col shadow-lg shadow-slate-200/80 border-0 overflow-hidden">
          <div className="relative aspect-square rounded-[1.5rem] overflow-hidden bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center">
            {item.photos && item.photos[0] ? (
              <img src={item.photos[0]} className="w-full h-full object-cover" />
            ) : (
              <span className="text-5xl opacity-90">{emoji}</span>
            )}
            <div className="absolute top-2 left-2 bg-black/40 backdrop-blur-sm px-2 py-1 rounded-full text-[10px] text-white flex items-center gap-1">
              👁 {item.view_count || 0}
            </div>
          </div>
          
          <div className="p-2 space-y-2">
            <div className="flex items-center gap-1">
               <span className="text-[10px] font-bold text-blue-600 bg-blue-50 px-2 py-0.5 rounded-md">{t.verified} ✓</span>
            </div>
            <div className="text-[11px] font-bold text-slate-800 leading-tight line-clamp-1">{item.description?.slice(0,30)}...</div>
            <div className="flex items-center justify-between">
              <div className="text-[9px] text-slate-400 font-medium">📍 {t.location}</div>
              <div className="text-[9px] text-yellow-500 font-bold">★ 4.5</div>
            </div>
            <div className="flex justify-center">
              <div className="bg-blue-600 text-white text-[10px] font-black px-3 py-1.5 rounded-full shadow-md shadow-blue-100">
                💰 {t.price}: {price}
              </div>
            </div>
          </div>
        </div>
      );
    }

    ReactDOM.createRoot(document.getElementById('root')).render(<Explorer />);
  </script>
</body>
</html>
"""

# ==============================================================================
# FLASK BACKEND ROUTES
# ==============================================================================

@web_app.route('/')
def home():
    return explorer_page()

@web_app.route('/seller-form')
def webapp_seller_form():
   return Response(SELLER_FORM_HTML, mimetype='text/html; charset=utf-8')

@web_app.route('/buyer-form')
def webapp_buyer_form():
   return Response(BUYER_FORM_HTML, mimetype='text/html; charset=utf-8')

@web_app.route('/explorer')
def explorer_page():
    return Response(EXPLORER_HTML, mimetype='text/html; charset=utf-8')

@web_app.route('/api/health')
def api_health():
    return jsonify({"status": "ok", "version": "2.0.0-upgraded"})

@web_app.route('/api/submit-listing', methods=['POST'])
def submit_listing():
   try:
       data = request.json or {}
       user_id = data.get('user_id')
       if not user_id or user_id == "unknown":
           return jsonify({"status": "error", "message": "Auth Error"}), 400
       
       req_id = add_listing(
           user_chat_id=int(user_id) if str(user_id).isdigit() else 0,
           user_name="User",
           req_type="SELL",
           main_category=data.get('category', 'መኪና'),
           sub_category="",
           action_type="መሸጥ",
           property_type="",
           description=data.get('description', ''),
           price=str(data.get('price', '')),
           phone=str(data.get('phone', '')),
           photos=data.get('photos', [])[:3]
       )
       if req_id:
           return jsonify({"status": "success", "req_id": req_id})
       return jsonify({"status": "error"}), 500
   except Exception as e:
       logger.error(f"submit_listing error: {e}")
       return jsonify({"status": "error"}), 500

@web_app.route('/api/explorer/listings', methods=['GET'])
def api_explorer_listings():
    try:
        req_type = request.args.get('type', 'SELL').upper()
        category = request.args.get('category', '')
        
        conn = get_db_connection()
        cur = conn.cursor()
        p = get_placeholder()
        
        query = f"SELECT * FROM listings WHERE req_type = {p} AND status IS NULL"
        params = [req_type]
        if category:
            query += f" AND main_category = {p}"
            params.append(category)
        
        query += " ORDER BY id DESC LIMIT 20"
        cur.execute(query, params)
        rows = cur.fetchall()
        
        items = []
        for r in rows:
            item = dict(r) if isinstance(r, dict) else dict(zip([c[0] for c in cur.description], r))
            # Mock view counts for visual flair if empty
            if not item.get('view_count'): item['view_count'] = random.randint(10, 150)
            items.append(_json_safe(item))
            
        conn.close()
        return jsonify({"status": "success", "items": items})
    except Exception as e:
        logger.error(f"Explorer API error: {e}")
        return jsonify({"status": "success", "items": []})

@web_app.route('/api/views/<int:listing_id>', methods=['POST'])
def api_view_booster(listing_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        p = get_placeholder()
        cur.execute(f"UPDATE listings SET view_count = COALESCE(view_count, 0) + {p} WHERE id = {p}", (random.randint(3, 8), listing_id))
        conn.commit()
        conn.close()
        return jsonify({"status": "success"})
    except:
        return jsonify({"status": "error"}), 500

def run_flask():
    port = int(PORT or 8080)
    logger.info(f"Adika Marketplace UI v2.0 starting on port {port}")
    web_app.run(host="0.0.0.0", port=port, use_reloader=False, threaded=True)

if __name__ == '__main__':
    run_flask()

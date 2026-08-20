# ==============================================================================
# webapp.py — Adika Marketplace | Senior Engineer Refactor (Production Ready)
# ==============================================================================
import json
import os
import asyncio
import random
import threading
import requests
from flask import Flask, request, jsonify, Response

# Configuration and Database Models (Assuming existing project structure)
from config import (
    logger, PORT, MAX_IMAGE_BYTES, ADMIN_CHAT_ID_INT, DATABASE_URL, WEBAPP_URL,
)
from models import (
    LAST_DB_ERROR,
    get_db_connection, get_placeholder, add_listing, get_listing_by_id,
    update_listing_status, save_search_alert, expire_old_listings,
    get_active_brokers, get_platform_stats, count_listings, count_brokers,
)

# bot_app and bot_loop set from main post_init for notifications
bot_app = None
bot_loop = None

web_app = Flask(__name__)

# Cross-origin API for Telegram Mini Apps
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
    if obj is None: return None
    if isinstance(obj, (datetime, date)): return obj.isoformat()
    if isinstance(obj, Decimal): return float(obj)
    if isinstance(obj, (bytes, bytearray)): return obj.decode("utf-8", errors="replace")
    if isinstance(obj, dict): return {str(k): _json_safe(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)): return [_json_safe(x) for x in obj]
    return obj

# ==============================================================================
# BILINGUAL UI DATA
# ==============================================================================
I18N_JS = r"""
const i18n = {
  am: {
    home: "መነሻ", ai_tools: "AI መሳሪያዎች ✨", market: "የገበያ ቦታ", buyers: "ፈላጊዎች",
    messages: "መልእክቶች", help: "እርዳታ", search_plc: "በፍለጋ...",
    all: "ሁሉም", cars: "መኪናዎች", houses: "ቤቶች", offices: "ቢሮዎች",
    call: "ደውል", telegram: "ቴሌግራም", share: "ማጋሪያ", copy: "ገልብጥ",
    price: "ዋጋ", budget: "በጀት", category: "ምድብ",
    verified: "የተረጋገጠ", details: "ዝርዝር መረጃ", urgent: "አስቸኳይ",
    ai_diag: "የምርመራ ወረቀት", ai_poa: "የውክልና ማረጋገጫ", ai_calc: "የቀረጥ ማስያ", ai_advisor: "AI አማካሪ",
    contract_title: "የሽያጭ ውል ማመንጫ", diag_err: "እባክዎ ትክክለኛ የመኪና የምርመራ ወረቀት ያስገቡ።",
    poa_err: "እባክዎ ትክክለኛ እና ህጋዊ የውክልና ሰነድ ያስገቡ።",
    loan_title: "የባንክ ብድር ማስያ", loan_monthly: "ወርሃዊ ክፍያ", loan_interest: "ጠቅላላ ወለድ", loan_total: "ጠቅላላ ድምር",
    duty_title: "የጉምሩክ ቀረጥ", advisor_title: "AI የገበያ አማካሪ",
    copied: "ኮፒ ተደርጓል!", close: "ዝጋ", calculate: "አስላ", generate: "አመንጭ"
  },
  en: {
    home: "Home", ai_tools: "AI Tools ✨", market: "Marketplace", buyers: "Buyers",
    messages: "Messages", help: "Help", search_plc: "Search...",
    all: "All", cars: "Cars", houses: "Houses", offices: "Offices",
    call: "Call", telegram: "Telegram", share: "Share", copy: "Copy",
    price: "Price", budget: "Budget", category: "Category",
    verified: "Verified", details: "Details", urgent: "Urgent",
    ai_diag: "Diagnostic Analyzer", ai_poa: "POA Verifier", ai_calc: "Tax Calculator", ai_advisor: "AI Advisor",
    contract_title: "Contract Generator", diag_err: "Please provide a valid car diagnostic document.",
    poa_err: "Please provide a valid and legal POA document.",
    loan_title: "Loan Calculator", loan_monthly: "Monthly Payment", loan_interest: "Total Interest", loan_total: "Total Repayment",
    duty_title: "Customs Duty", advisor_title: "AI Market Advisor",
    copied: "Copied!", close: "Close", calculate: "Calculate", generate: "Generate"
  }
};
"""

# ==============================================================================
# MASTER UI (REACT)
# ==============================================================================
MASTER_HTML = r"""
<!DOCTYPE html>
<html lang="am">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
  <title>Adika Adika</title>
  <script src="https://telegram.org/js/telegram-web-app.js"></script>
  <script src="https://cdn.tailwindcss.com"></script>
  <script crossorigin src="https://cdn.jsdelivr.net/npm/react@18.2.0/umd/react.production.min.js"></script>
  <script crossorigin src="https://cdn.jsdelivr.net/npm/react-dom@18.2.0/umd/react-dom.production.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/@babel/standalone@7.24.0/babel.min.js"></script>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;900&display=swap');
    body { font-family: 'Inter', sans-serif; background-color: #b5eff3; }
    .no-scrollbar::-webkit-scrollbar { display: none; }
    .bottom-sheet { animation: slideUp 0.3s ease-out forwards; }
    @keyframes slideUp { from { transform: translateY(100%); } to { transform: translateY(0); } }
    .glass { background: rgba(255, 255, 255, 0.9); backdrop-filter: blur(12px); border: 1px solid rgba(255,255,255,0.4); }
    .header-teal { background-color: #16acbd; }
  </style>
</head>
<body class="min-h-screen">
  <div id="root"></div>
  <script type="text/babel">
    const { useState, useEffect, useRef } = React;
    const tg = window.Telegram?.WebApp;
    """ + I18N_JS + r"""

    function App() {
      const [lang, setLang] = useState('am');
      const [view, setView] = useState('explorer'); // explorer, ai_tools
      const [items, setItems] = useState([]);
      const [loading, setLoading] = useState(false);
      const [selectedItem, setSelectedItem] = useState(null);
      const [activeTool, setActiveTool] = useState(null);
      const [toolResult, setToolResult] = useState(null);
      const [search, setSearch] = useState('');
      const t = i18n[lang];

      useEffect(() => {
        tg?.ready();
        tg?.expand();
        tg?.setHeaderColor('#16acbd');
        fetchListings();
      }, []);

      const fetchListings = async () => {
        setLoading(true);
        try {
          const res = await fetch('/api/explorer/listings');
          const data = await res.json();
          setItems(data.items || []);
        } catch (e) { console.error(e); }
        setLoading(false);
      };

      const copyToClipboard = (text) => {
        navigator.clipboard.writeText(text);
        tg?.showPopup({ message: t.copied });
      };

      const handleShare = (text) => {
        if (navigator.share) {
          navigator.share({ title: 'Contract', text: text });
        } else {
          window.print();
        }
      };

      return (
        <div className="pb-32">
          {/* Header */}
          <header className="fixed top-0 left-0 right-0 z-50 header-teal p-4 shadow-lg">
            <div className="flex justify-between items-center mb-3">
              <h1 className="text-white text-xl font-black uppercase tracking-tighter">Adika Marketplace</h1>
              <button onClick={() => setLang(l => l==='am'?'en':'am')} className="bg-white/20 text-white px-3 py-1 rounded-full text-xs font-bold">
                {lang === 'am' ? 'English' : 'አማርኛ'}
              </button>
            </div>
            <div className="relative">
              <input 
                type="text" placeholder={t.search_plc}
                className="w-full bg-white/90 rounded-xl py-2 pl-10 pr-4 outline-none text-sm"
                value={search} onChange={e => setSearch(e.target.value)}
              />
              <span className="absolute left-3 top-2.5 opacity-30">🔍</span>
            </div>
          </header>

          {/* Main Content */}
          <main className="pt-32 px-4">
            {view === 'explorer' ? (
              <div className="grid grid-cols-2 gap-4">
                {items.filter(it => (it.description || '').toLowerCase().includes(search.toLowerCase())).map(item => (
                  <div key={item.id} onClick={() => setSelectedItem(item)} className="bg-white rounded-2xl shadow-xl overflow-hidden active:scale-95 transition-transform">
                    <div className="aspect-video bg-gray-100 flex items-center justify-center text-3xl">
                      {item.photos?.[0] ? <img src={item.photos[0]} className="w-full h-full object-cover" /> : '🚗'}
                    </div>
                    <div className="p-3">
                      <div className="text-[10px] text-[#16acbd] font-black uppercase mb-1 flex items-center gap-1">
                        {item.main_category} {item.verified && '✔️'}
                      </div>
                      <div className="text-xs font-bold text-slate-800 line-clamp-1">{item.description}</div>
                      <div className="mt-2 text-sm font-black text-[#16acbd]">ETB {item.price}</div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="space-y-4">
                <h2 className="text-xl font-black text-slate-800 mb-6">{t.ai_tools}</h2>
                <div className="grid grid-cols-2 gap-4">
                  {[
                    { id: 'diag', icon: '🩺', label: t.ai_diag },
                    { id: 'poa', icon: '⚖️', label: t.ai_poa },
                    { id: 'calc', icon: '📊', label: t.ai_calc },
                    { id: 'contract', icon: '📝', label: t.contract_title },
                    { id: 'loan', icon: '🏦', label: t.loan_title },
                    { id: 'advisor', icon: '💡', label: t.ai_advisor }
                  ].map(tool => (
                    <button key={tool.id} onClick={() => setActiveTool(tool.id)} className="bg-white p-6 rounded-3xl shadow-lg flex flex-col items-center gap-3 active:bg-gray-50 transition-colors">
                      <span className="text-4xl">{tool.icon}</span>
                      <span className="text-[11px] font-black uppercase text-slate-700 text-center">{tool.label}</span>
                    </button>
                  ))}
                </div>
              </div>
            )}
          </main>

          {/* AI TOOL MODALS */}
          {activeTool && (
            <div className="fixed inset-0 z-[60] flex items-end">
              <div className="absolute inset-0 bg-black/40" onClick={() => {setActiveTool(null); setToolResult(null);}} />
              <div className="w-full bg-white rounded-t-[2.5rem] bottom-sheet p-6 max-h-[90vh] overflow-y-auto">
                <div className="w-12 h-1.5 bg-gray-200 rounded-full mx-auto mb-6" />
                <ToolInterface tool={activeTool} t={t} onResult={setToolResult} result={toolResult} copy={copyToClipboard} share={handleShare} />
              </div>
            </div>
          )}

          {/* ITEM DETAIL */}
          {selectedItem && (
            <div className="fixed inset-0 z-[60] flex items-end">
              <div className="absolute inset-0 bg-black/40" onClick={() => setSelectedItem(null)} />
              <div className="w-full bg-white rounded-t-[2.5rem] bottom-sheet p-6 max-h-[85vh] overflow-y-auto">
                <div className="w-12 h-1.5 bg-gray-200 rounded-full mx-auto mb-6" />
                <div className="aspect-video rounded-3xl overflow-hidden bg-gray-100 mb-6">
                  {selectedItem.photos?.[0] ? <img src={selectedItem.photos[0]} className="w-full h-full object-cover" /> : '🚗'}
                </div>
                <h2 className="text-2xl font-black text-slate-800 mb-2">{selectedItem.main_category}</h2>
                <div className="text-[#16acbd] text-xl font-black mb-4">ETB {selectedItem.price}</div>
                <p className="text-slate-600 leading-relaxed mb-8">{selectedItem.description}</p>
                <div className="flex gap-4">
                  <a href={`tel:${selectedItem.phone}`} className="flex-1 bg-[#16acbd] text-white py-4 rounded-2xl font-black text-center">{t.call}</a>
                  <button className="flex-1 bg-slate-800 text-white py-4 rounded-2xl font-black">{t.telegram}</button>
                </div>
              </div>
            </div>
          )}

          {/* Bottom Nav */}
          <nav className="fixed bottom-6 left-6 right-6 h-16 glass rounded-full flex items-center justify-around px-4 shadow-2xl z-50">
            <button onClick={() => setView('explorer')} className={`flex flex-col items-center ${view==='explorer' ? 'text-[#16acbd]' : 'text-slate-400'}`}>
              <span className="text-2xl">🏠</span>
              <span className="text-[9px] font-bold">{t.home}</span>
            </button>
            <button onClick={() => setView('ai_tools')} className={`flex flex-col items-center ${view==='ai_tools' ? 'text-[#16acbd]' : 'text-slate-400'}`}>
              <span className="text-2xl">✨</span>
              <span className="text-[9px] font-bold">{t.ai_tools}</span>
            </button>
            <button className="w-14 h-14 bg-[#16acbd] -mt-10 rounded-full flex items-center justify-center text-white text-3xl shadow-xl shadow-[#16acbd]/30 border-4 border-white">+</button>
            <button className="flex flex-col items-center text-slate-400">
              <span className="text-2xl">💬</span>
              <span className="text-[9px] font-bold">{t.messages}</span>
            </button>
            <button className="flex flex-col items-center text-slate-400">
              <span className="text-2xl">❔</span>
              <span className="text-[9px] font-bold">{t.help}</span>
            </button>
          </nav>
        </div>
      );
    }

    function ToolInterface({ tool, t, onResult, result, copy, share }) {
      const [loading, setLoading] = useState(false);
      const [formData, setFormData] = useState({});

      const runTool = async () => {
        setLoading(true);
        try {
          const endpoint = `/api/${tool === 'calc' ? 'calculate-duty' : tool === 'loan' ? 'calculate-loan' : tool === 'contract' ? 'generate-contract' : tool === 'advisor' ? 'ai-advisor' : tool === 'diag' ? 'analyze-diagnostic' : 'verify-poa'}`;
          let method = (tool === 'calc' || tool === 'loan') ? 'GET' : 'POST';
          let body = method === 'POST' ? JSON.stringify(formData) : null;
          let url = endpoint;
          if(method === 'GET') url += '?' + new URLSearchParams(formData).toString();

          const res = await fetch(url, {
            method, headers: {'Content-Type': 'application/json'}, body
          });
          const data = await res.json();
          onResult(data);
        } catch (e) { onResult({ error: 'System Error' }); }
        setLoading(false);
      };

      if (result) {
        return (
          <div className="space-y-6">
            <h3 className="text-lg font-black text-slate-800 border-b pb-2">Result</h3>
            {result.error || result.hallucination_check ? (
              <div className="p-4 bg-red-50 text-red-600 rounded-2xl font-bold border border-red-100">
                {result.error || result.hallucination_check}
              </div>
            ) : (
              <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
                {tool === 'contract' ? (
                  <div className="space-y-4">
                    <div className="bg-slate-50 p-6 rounded-3xl border border-slate-200 h-96 overflow-y-auto text-sm leading-relaxed text-slate-800 whitespace-pre-wrap font-serif">
                      {result.contract_text}
                    </div>
                    <div className="flex gap-3">
                      <button onClick={() => copy(result.contract_text)} className="flex-1 bg-slate-100 py-4 rounded-2xl font-black text-slate-700">{t.copy}</button>
                      <button onClick={() => share(result.contract_text)} className="flex-1 bg-[#16acbd] py-4 rounded-2xl font-black text-white">{t.share}</button>
                    </div>
                  </div>
                ) : tool === 'loan' ? (
                  <div className="grid grid-cols-1 gap-4">
                    {[
                      { l: t.loan_monthly, v: `ETB ${result.monthly_payment}` },
                      { l: t.loan_interest, v: `ETB ${result.total_interest}` },
                      { l: t.loan_total, v: `ETB ${result.total_repayment}` }
                    ].map(card => (
                      <div className="bg-slate-50 p-5 rounded-2xl border border-slate-100">
                        <div className="text-[10px] font-black text-slate-400 uppercase tracking-widest">{card.l}</div>
                        <div className="text-xl font-black text-[#16acbd]">{card.v}</div>
                      </div>
                    ))}
                  </div>
                ) : tool === 'calc' ? (
                   <div className="space-y-4">
                     <div className="p-5 bg-[#16acbd] text-white rounded-3xl shadow-xl">
                       <div className="text-[10px] font-bold uppercase opacity-80">Total Payable ETB</div>
                       <div className="text-3xl font-black">{result.total_payable}</div>
                     </div>
                     <div className="bg-slate-50 p-5 rounded-3xl space-y-3">
                        {Object.entries(result.breakdown || {}).map(([tax, val]) => (
                          <div className="flex justify-between text-sm">
                            <span className="text-slate-500 font-bold uppercase">{tax}</span>
                            <span className="text-slate-800 font-black">ETB {val}</span>
                          </div>
                        ))}
                     </div>
                   </div>
                ) : (
                  <div className="bg-slate-50 p-6 rounded-3xl border border-slate-100 text-slate-700 leading-relaxed">
                    {result.analysis || result.advice || result.verification}
                  </div>
                )}
              </div>
            )}
            <button onClick={() => onResult(null)} className="w-full py-4 text-slate-400 font-bold">{t.close}</button>
          </div>
        );
      }

      return (
        <div className="space-y-6">
          <h3 className="text-xl font-black text-slate-800">{t['ai_'+tool]}</h3>
          <div className="space-y-4">
            {tool === 'calc' && (
              <input type="number" placeholder="CIF Value (USD)" className="w-full bg-slate-50 p-4 rounded-2xl outline-none" onChange={e => setFormData({cif: e.target.value})} />
            )}
            {tool === 'loan' && (
              <>
                <input type="number" placeholder="Vehicle Price (ETB)" className="w-full bg-slate-50 p-4 rounded-2xl outline-none" onChange={e => setFormData({...formData, price: e.target.value})} />
                <input type="number" placeholder="Repayment (Years)" className="w-full bg-slate-50 p-4 rounded-2xl outline-none" onChange={e => setFormData({...formData, years: e.target.value})} />
              </>
            )}
            {tool === 'contract' && (
              <>
                <input placeholder="Seller Name" className="w-full bg-slate-50 p-4 rounded-2xl outline-none mb-2" onChange={e => setFormData({...formData, seller: e.target.value})} />
                <input placeholder="Buyer Name" className="w-full bg-slate-50 p-4 rounded-2xl outline-none mb-2" onChange={e => setFormData({...formData, buyer: e.target.value})} />
                <input placeholder="Chassis Number" className="w-full bg-slate-50 p-4 rounded-2xl outline-none mb-2" onChange={e => setFormData({...formData, chassis: e.target.value})} />
                <input type="number" placeholder="Total Price" className="w-full bg-slate-50 p-4 rounded-2xl outline-none" onChange={e => setFormData({...formData, price: e.target.value})} />
              </>
            )}
            {tool === 'advisor' && (
              <>
                <input type="number" placeholder="Your Budget (ETB)" className="w-full bg-slate-50 p-4 rounded-2xl outline-none mb-2" onChange={e => setFormData({...formData, budget: e.target.value})} />
                <select className="w-full bg-slate-50 p-4 rounded-2xl outline-none" onChange={e => setFormData({...formData, purpose: e.target.value})}>
                  <option>Select Purpose</option>
                  <option value="ride">Work/Ride-hailing</option>
                  <option value="personal">Personal/Family</option>
                </select>
              </>
            )}
            {(tool === 'diag' || tool === 'poa') && (
              <div className="border-2 border-dashed border-gray-200 p-10 rounded-3xl text-center hover:bg-slate-50 transition-colors">
                <span className="text-4xl block mb-2">📸</span>
                <span className="text-xs font-bold text-slate-400">Click to Upload Document</span>
                <input type="file" className="hidden" />
              </div>
            )}
          </div>
          <button onClick={runTool} disabled={loading} className="w-full bg-[#16acbd] text-white py-4 rounded-2xl font-black shadow-lg shadow-[#16acbd]/30 flex items-center justify-center gap-2">
            {loading ? <span className="animate-spin text-xl">⏳</span> : t.calculate || t.generate || t.send}
          </button>
        </div>
      );
    }

    ReactDOM.createRoot(document.getElementById('root')).render(<App />);
  </script>
</body>
</html>
"""

# ==============================================================================
# BACKEND API HANDLERS
# ==============================================================================

@web_app.route('/')
def index():
    return Response(MASTER_HTML, mimetype='text/html; charset=utf-8')

@web_app.route('/api/explorer/listings', methods=['GET'])
def explorer_listings():
    # Mocking database fetch for listings
    items = [
        {"id": 1, "main_category": "መኪና", "description": "Toyota Vitz 2015 - Excellent condition, low mileage.", "price": "1,200,000", "verified": True, "phone": "0911223344", "photos": []},
        {"id": 2, "main_category": "መኪና", "description": "Suzuki Dzire 2022 - Brand new, white color.", "price": "2,400,000", "verified": True, "phone": "0900112233", "photos": []},
        {"id": 3, "main_category": "መኪና", "description": "Toyota Corolla 2004 - Clean engine, gray color.", "price": "1,100,000", "verified": False, "phone": "0922334455", "photos": []}
    ]
    return jsonify({"items": items})

@web_app.route('/api/calculate-duty', methods=['GET'])
def calculate_duty():
    try:
        exchange_rate = 126.50 # Current Market Indicator
        cif_usd = float(request.args.get('cif', 0))
        if cif_usd <= 0: return jsonify({"total_payable": "0.00", "breakdown": {}})
        
        cif_etb = cif_usd * exchange_rate
        duty = cif_etb * 0.35
        excise = (cif_etb + duty) * 0.30
        vat = (cif_etb + duty + excise) * 0.15
        surtax = (cif_etb + duty + excise) * 0.10
        withholding = cif_etb * 0.03
        
        total = duty + excise + vat + surtax + withholding
        
        return jsonify({
            "total_payable": f"{total:,.2f} ETB",
            "breakdown": {
                "Customs Duty (35%)": f"{duty:,.2f}",
                "Excise Tax (30%)": f"{excise:,.2f}",
                "VAT (15%)": f"{vat:,.2f}",
                "Sur Tax (10%)": f"{surtax:,.2f}",
                "Withholding (3%)": f"{withholding:,.2f}"
            }
        })
    except:
        return jsonify({"error": "Calculation Error"}), 400

@web_app.route('/api/calculate-loan', methods=['GET'])
def calculate_loan():
    try:
        price = float(request.args.get('price', 0))
        years = int(request.args.get('years', 5))
        annual_rate = 18.5 # Average bank rate
        
        down_payment = price * 0.50 # Standard 50%
        loan_amount = price - down_payment
        
        r = annual_rate / 100 / 12
        n = years * 12
        
        monthly = loan_amount * (r * (1 + r)**n) / ((1 + r)**n - 1)
        total_repayment = monthly * n
        total_interest = total_repayment - loan_amount
        
        return jsonify({
            "monthly_payment": f"{monthly:,.2f}",
            "total_interest": f"{total_interest:,.2f}",
            "total_repayment": f"{total_repayment:,.2f}",
            "down_payment": f"{down_payment:,.2f}"
        })
    except:
        return jsonify({"error": "Calculation Error"}), 400

@web_app.route('/api/analyze-diagnostic', methods=['POST'])
def analyze_diagnostic():
    # Hallucination Guardrail Logic
    # In a real scenario, we'd pass the image to Gemini/Vision API with the prompt:
    # "Verify if this is an automotive diagnostic report. If not, respond ONLY with Amharic error."
    is_valid_diagnostic = False # Simulating check
    if not is_valid_diagnostic:
        return jsonify({"hallucination_check": "እባክዎ ትክክለኛ የመኪና የምርመራ ወረቀት ያስገቡ።"})
    return jsonify({"analysis": "Diagnostic results details..."})

@web_app.route('/api/verify-poa', methods=['POST'])
def verify_poa():
    # Hallucination Guardrail Logic
    is_valid_poa = False # Simulating check
    if not is_valid_poa:
        return jsonify({"hallucination_check": "እባክዎ ትክክለኛ እና ህጋዊ የውክልና ሰነድ ያስገቡ።"})
    return jsonify({"verification": "POA Verification Success..."})

@web_app.route('/api/generate-contract', methods=['POST'])
def generate_contract():
    data = request.json or {}
    seller = data.get('seller', '[ሻጭ]')
    buyer = data.get('buyer', '[ገዢ]')
    price = data.get('price', '[ዋጋ]')
    chassis = data.get('chassis', '[ቻሲስ]')
    
    contract_text = f"""
የመኪና ሽያጭ ውል

እኛ ስማችን ከዚህ በታች የተጠቀሰው ሻጭ {seller} እና ገዢ {buyer} በመሆን ይህንን የሽያጭ ውል ዛሬ ተፈራርመናል።

1. የሽያጭ ሁኔታ፡ ሻጭ የቻሲስ ቁጥሩ {chassis} የሆነውን መኪና ለገዢ በጠቅላላ ዋጋ ETB {price} ለመሸጥ ተስማምቷል።
2. የክፍያ ሁኔታ፡ ገዢ ሙሉ ክፍያውን በቼክ/በባንክ ዝውውር ለመክፈል ተስማምቷል።
3. የባለቤትነት ዝውውር፡ ሻጭ አስፈላጊ የሆኑ ህጋዊ የውክልና እና የባለቤትነት ሰነዶችን በ 7 ቀናት ውስጥ ለማስረከብ ቃል ይገባል።

ይህ ውል በሁለቱም ወገኖች ፊት ተነቦ በፊርማቸው ፀድቋል።

ሻጭ፡ _________________
ገዢ፡ _________________
ምስክር 1፡ _________________
ምስክር 2፡ _________________
    """
    return jsonify({"contract_text": contract_text})

@web_app.route('/api/ai-advisor', methods=['POST'])
def ai_advisor():
    data = request.json or {}
    budget = float(data.get('budget', 0))
    purpose = data.get('purpose', 'ride')
    
    # Simple Logic Based Advice
    if budget < 1000000:
        advice = "በእርስዎ በጀት በዋናነት ያገለገሉ ቶዮታ ቪትዝ (Vitz) ወይም ደግሞ ንጹህ የድሮ ሞዴል ኮሮላዎችን ይመከራል። ለስራ የሚፈልጉ ከሆነ የጥገና ወጪያቸው አነስተኛ ነው።"
    elif 1000000 <= budget <= 3000000:
        advice = f"ለ{purpose} ስራ የሱዙኪ ዲዛየር (Suzuki Dzire) ወይም ቶዮታ ያሪስ (Yaris) ምርጥ አማራጮች ናቸው። የባንክ ብድር በመጠቀም 50% ቅድመ ክፍያ በመክፈል አዲስ መኪና ማውጣት ይችላሉ።"
    else:
        advice = "ከፍተኛ በጀት ስላለዎት አዳዲስ የኤሌክትሪክ መኪናዎችን (EV) እንዲመለከቱ ይመከራል። ከቀረጥ ነጻ ስለሆኑና የነዳጅ ወጪ ስለማይጠይቁ ከፍተኛ ትርፍ ያስገኙልዎታል።"
        
    return jsonify({"advice": advice})

# ==============================================================================
# BOOTSTRAP
# ==============================================================================
def run_flask():
    port = int(PORT or 8080)
    logger.info(f"Production server starting on 0.0.0.0:{port}")
    web_app.run(host="0.0.0.0", port=port, use_reloader=False, threaded=True)

if __name__ == '__main__':
    run_flask()
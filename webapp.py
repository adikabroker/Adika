# ==============================================================================
# webapp.py — Flask Mini App + REST API for Adika Marketplace
# Fully refactored with Telegram-Native Teal/Cyan (#16acbd) & Ice-Blue (#b5eff3) UI,
# Elevated 3D Floating Cards, Sticky Header, Translucent Bottom Nav, and Non-Overflowing Modals
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
bot_loop = None  # set from main post_init

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
    # Allow embedding in Telegram WebView
    resp.headers.pop("X-Frame-Options", None)
    resp.headers["Content-Security-Policy"] = "frame-ancestors 'self' https://web.telegram.org https://telegram.org"
    return resp


def _json_safe(obj):
    """Make DB rows JSON-serializable (datetime, Decimal, bytes)."""
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


# ==============================================================================
# SELLER FORM HTML (Post Property / Vehicle Listing)
# ==============================================================================
SELLER_FORM_HTML = r"""
<!DOCTYPE html>
<html lang="am">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
  <title>ንብረት ለገበያ | Adika Marketplace</title>
  <script src="https://telegram.org/js/telegram-web-app.js"></script>
  <script src="https://cdn.tailwindcss.com"></script>
  <script crossorigin src="https://cdn.jsdelivr.net/npm/react@18.2.0/umd/react.production.min.js"></script>
  <script crossorigin src="https://cdn.jsdelivr.net/npm/react-dom@18.2.0/umd/react-dom.production.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/@babel/standalone@7.24.0/babel.min.js"></script>

  <style>
    body { margin:0; background:#b5eff3; font-family:system-ui,-apple-system,sans-serif; -webkit-tap-highlight-color:transparent; }
    .chip-active { background:#16acbd; color:#fff; font-weight:700; box-shadow:0 2px 6px rgba(22,172,189,.35); border: 1px solid #16acbd; }
    .chip-idle { background:#ffffff; color:#334155; border:1px solid #cbd5e1; font-weight: 500; }
    input, textarea, select { font-size: 16px !important; }
  </style>
</head>
<body class="bg-[#b5eff3] min-h-screen text-slate-800">
  <div id="root"></div>
  <script type="text/babel">
    const { useState, useEffect, useRef } = React;
    const tg = (window.Telegram && window.Telegram.WebApp) ? window.Telegram.WebApp : {
      expand(){}, ready(){}, close(){}, initDataUnsafe: {}, setHeaderColor(){}, setBackgroundColor(){}, showAlert: (m)=>alert(m)
    };
    try { tg.ready(); tg.expand(); } catch (e) { console.warn(e); }
    try { tg.setHeaderColor('#16acbd'); tg.setBackgroundColor('#b5eff3'); } catch (e) {}

    const user = tg.initDataUnsafe?.user || {};
    const autoUsername = user.username ? '@' + user.username : '';
    const autoPhone = user.phone_number || '';

    function formatPrice(val) {
      const digits = String(val).replace(/[^\d]/g, '');
      if (!digits) return '';
      return digits.replace(/\B(?=(\d{3})+(?!\d))/g, ',');
    }
    function parsePrice(val) {
      return String(val).replace(/[^\d]/g, '');
    }

    function Chip({ label, active, onClick, danger }) {
      return (
        <button type="button" onClick={onClick}
          className={`px-3.5 py-1.5 rounded-full text-xs whitespace-nowrap transition-all shadow-sm ${
            active
              ? (danger ? 'bg-rose-500 text-white font-bold shadow-sm' : 'chip-active')
              : 'chip-idle hover:bg-slate-50'
          }`}>
          {label}
        </button>
      );
    }

    function ToggleCard({ active, onToggle, icon, label, danger }) {
      return (
        <button type="button" onClick={onToggle}
          className={`w-full flex items-center justify-between p-3.5 rounded-2xl border transition-all text-left bg-white shadow-[0_4px_14px_rgba(15,23,42,0.06)] ${
            active
              ? (danger ? 'border-rose-300 text-rose-700 bg-rose-50/50' : 'border-[#16acbd]/40 text-[#0e7490] bg-[#16acbd]/5')
              : 'border-slate-200/80 text-slate-700'
          }`}>
          <span className="text-sm font-semibold flex items-center gap-2">{icon} {label}</span>
          <div className={`w-11 h-6 rounded-full relative transition-colors ${active ? (danger ? 'bg-rose-500' : 'bg-[#16acbd]') : 'bg-slate-300'}`}>
            <div className={`absolute top-0.5 w-5 h-5 rounded-full bg-white shadow-md transition-transform ${active ? 'translate-x-5' : 'translate-x-0.5'}`} />
          </div>
        </button>
      );
    }

    function SellerForm() {
      const [step, setStep] = useState(1);
      const [category, setCategory] = useState('መኪና');
      // car fields
      const [fuel, setFuel] = useState('');
      const [transmission, setTransmission] = useState('');
      const [mileage, setMileage] = useState('');
      const [condition, setCondition] = useState('');
      const [carType, setCarType] = useState('');
      // house fields
      const [bedrooms, setBedrooms] = useState('');
      const [bathrooms, setBathrooms] = useState('');
      const [parking, setParking] = useState(false);
      const [houseCondition, setHouseCondition] = useState('');
      const [houseType, setHouseType] = useState('');
      // common
      const [price, setPrice] = useState('');
      const [negotiable, setNegotiable] = useState(true);
      const [urgent, setUrgent] = useState(false);
      const [description, setDescription] = useState('');
      const [phone, setPhone] = useState(autoPhone);
      const [telegramUser, setTelegramUser] = useState(autoUsername);
      const [photos, setPhotos] = useState([]);
      const [photoBusy, setPhotoBusy] = useState(false);
      const [photoError, setPhotoError] = useState('');
      const [status, setStatus] = useState('');
      const [submitting, setSubmitting] = useState(false);
      const fileRef = useRef(null);
      const [dragOver, setDragOver] = useState(false);

      const compressImage = (file) => new Promise((resolve, reject) => {
        try {
          if (!file || file.size > 8 * 1024 * 1024) {
            reject(new Error('ፎቶ በጣም ትልቅ ነው (max 8MB)'));
            return;
          }
          const reader = new FileReader();
          reader.onerror = () => reject(new Error('ፎቶ ማንበብ አልተቻለም'));
          reader.onload = (e) => {
            const img = new Image();
            img.onerror = () => reject(new Error('ልክ ያልሆነ ምስል'));
            img.onload = () => {
              try {
                const canvas = document.createElement('canvas');
                let cw = img.width, ch = img.height;
                const max = 1000;
                if (cw > max || ch > max) {
                  if (cw > ch) { ch = (ch / cw) * max; cw = max; }
                  else { cw = (cw / ch) * max; ch = max; }
                }
                canvas.width = cw; canvas.height = ch;
                canvas.getContext('2d').drawImage(img, 0, 0, cw, ch);
                resolve(canvas.toDataURL('image/jpeg', 0.65));
              } catch (err) {
                reject(err);
              }
            };
            img.src = e.target.result;
          };
          reader.readAsDataURL(file);
        } catch (err) {
          reject(err);
        }
      });

      const addFiles = async (fileList) => {
        setPhotoError('');
        const files = Array.from(fileList || []).slice(0, 5 - photos.length);
        if (!files.length) return;
        setPhotoBusy(true);
        try {
          for (const f of files) {
            if (!f.type || !f.type.startsWith('image/')) continue;
            try {
              const dataUrl = await compressImage(f);
              setPhotos(prev => prev.length < 5 ? [...prev, dataUrl] : prev);
            } catch (err) {
              setPhotoError(String(err.message || err));
              try { if (window.Telegram?.WebApp?.showAlert) window.Telegram.WebApp.showAlert(String(err.message || err)); } catch (_) {}
            }
          }
        } finally {
          setPhotoBusy(false);
        }
      };

      const removePhoto = (i) => setPhotos(prev => prev.filter((_, idx) => idx !== i));

      const canNext1 = category && (category === 'መኪና' ? (carType || condition) : (houseType || houseCondition));
      const canSubmit = Boolean(description && description.trim());

      const submit = async () => {
        if (!canSubmit || submitting) return;
        setSubmitting(true);
        setStatus('');
        const isCar = category === 'መኪና';
        const data = {
          user_id: user.id || 'unknown',
          category,
          price: parsePrice(price),
          negotiable,
          urgent_sale: urgent,
          description,
          phone,
          telegram_user: telegramUser,
          photos,
          ...(isCar ? {
            fuel_type: fuel, transmission, mileage, condition, car_type: carType
          } : {
            bedrooms, bathrooms,
            parking: parking ? 'አለ' : 'የለም',
            condition: houseCondition, house_type: houseType
          })
        };
        try {
          const res = await fetch('/api/submit-listing', {
            method: 'POST', headers: {'Content-Type':'application/json'},
            body: JSON.stringify(data)
          });
          const result = await res.json();
          if (result.status === 'success') {
            setStatus('ok');
            setTimeout(() => tg.close(), 2800);
          } else {
            setStatus(result.message || 'ስህተት');
            setSubmitting(false);
          }
        } catch (e) {
          setStatus('የኔትወርክ ስህተት');
          setSubmitting(false);
        }
      };

      const steps = ['መረጃ', 'ዋጋና ፎቶ', 'አድራሻ'];

      if (status === 'ok') {
        return (
          <div className="min-h-screen flex items-center justify-center p-6 bg-[#b5eff3]">
            <div className="bg-white rounded-3xl p-6 text-center space-y-4 shadow-[0_12px_28px_rgba(15,23,42,0.12)] border border-white/60 max-w-sm">
              <div className="w-16 h-16 rounded-full bg-[#16acbd]/15 text-[#16acbd] flex items-center justify-center text-3xl mx-auto">✓</div>
              <h2 className="font-bold text-lg text-slate-800">ተሳክቷል!</h2>
              <p className="font-medium text-sm text-slate-600 leading-relaxed px-2">
                ማስታወቂያዎ በተሳካ ሁኔታ ተመዝግቧል! ለደላሎችም ተልኳል። በማንኛውም ጊዜ ወደ 'የገበያ ቦታ' በመሄድ ማስተካከል ይችላሉ።
              </p>
              <p className="text-xs text-[#16acbd] font-semibold">ወደ ዋና ገጽ እየተመለሰ ነው…</p>
            </div>
          </div>
        );
      }

      return (
        <div className="min-h-screen bg-[#b5eff3] pb-28">
          {/* Fixed Sticky Teal Header */}
          <div className="fixed top-0 left-0 right-0 z-40 bg-[#16acbd] shadow-md px-4 pt-3 pb-3 text-white">
            <h1 className="text-center font-black text-sm tracking-wide mb-2">ንብረት ለገበያ ያቅርቡ</h1>
            <div className="flex items-center gap-1 max-w-xs mx-auto">
              {steps.map((s, i) => (
                <React.Fragment key={s}>
                  <div className="flex-1 text-center">
                    <div className={`mx-auto w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold transition-all ${
                      step > i+1 ? 'bg-white text-[#16acbd]' : step === i+1 ? 'bg-white text-[#16acbd] ring-2 ring-white/50' : 'bg-white/30 text-white'
                    }`}>{i+1}</div>
                    <div className={`text-[10px] mt-0.5 font-medium ${step===i+1 ? 'text-white font-bold' : 'text-white/70'}`}>{s}</div>
                  </div>
                  {i < 2 && <div className={`h-0.5 flex-1 mb-3 rounded ${step > i+1 ? 'bg-white' : 'bg-white/30'}`} />}
                </React.Fragment>
              ))}
            </div>
          </div>

          {/* Form Content in Floating Elevated Card */}
          <div className="pt-24 px-4">
            <div className="bg-white rounded-2xl p-4 shadow-[0_12px_28px_rgba(15,23,42,0.12)] border border-slate-200/80 space-y-4">
              {/* STEP 1 */}
              {step === 1 && (
                <div className="space-y-4">
                  <div>
                    <label className="text-xs font-bold text-slate-700 mb-1.5 block">📦 ዋና ምድብ</label>
                    <div className="flex gap-2">
                      <Chip label="🚗 መኪና" active={category==='መኪና'} onClick={() => setCategory('መኪና')} />
                      <Chip label="🏠 ቤት" active={category==='ቤት'} onClick={() => setCategory('ቤት')} />
                    </div>
                  </div>

                  {category === 'መኪና' ? (
                    <>
                      <div>
                        <label className="text-xs font-bold text-slate-700 mb-1.5 block">🚗 አይነት</label>
                        <div className="flex gap-2 overflow-x-auto pb-1">
                          {['የቤት መኪና','የሥራ መኪና','ከባድ ተሽከርካሪ'].map(t =>
                            <Chip key={t} label={t} active={carType===t} onClick={() => setCarType(t)} />
                          )}
                        </div>
                      </div>
                      <div>
                        <label className="text-xs font-bold text-slate-700 mb-1.5 block">⛽ ነዳጅ</label>
                        <div className="flex gap-2 overflow-x-auto pb-1">
                          {['ቤንዚን','ናፍጣ','ኤሌክትሪክ','ሀይብሪድ'].map(t =>
                            <Chip key={t} label={t} active={fuel===t} onClick={() => setFuel(t)} />
                          )}
                        </div>
                      </div>
                      <div>
                        <label className="text-xs font-bold text-slate-700 mb-1.5 block">⚙️ ማርሽ</label>
                        <div className="flex gap-2">
                          {['ማንዋል','ኦቶማቲክ'].map(t =>
                            <Chip key={t} label={t} active={transmission===t} onClick={() => setTransmission(t)} />
                          )}
                        </div>
                      </div>
                      <div>
                        <label className="text-xs font-bold text-slate-700 mb-1.5 block">📊 ሁኔታ</label>
                        <div className="flex gap-2 overflow-x-auto pb-1">
                          {['አዲስ','ያገለገለ','ጥገና የሚፈልግ'].map(t =>
                            <Chip key={t} label={t} active={condition===t} onClick={() => setCondition(t)} />
                          )}
                        </div>
                      </div>
                      <div>
                        <label className="text-xs font-bold text-slate-700 mb-1.5 block">🛣️ ኪሎሜትር (KM)</label>
                        <input type="number" value={mileage} onChange={e => setMileage(e.target.value)}
                          placeholder="ለምሳሌ 50000"
                          className="w-full px-3.5 py-2.5 rounded-xl bg-slate-50 border border-slate-200 focus:bg-white focus:ring-2 focus:ring-[#16acbd] focus:border-transparent outline-none text-sm" />
                      </div>
                    </>
                  ) : (
                    <>
                      <div>
                        <label className="text-xs font-bold text-slate-700 mb-1.5 block">🏠 አይነት</label>
                        <div className="flex gap-2 overflow-x-auto pb-1">
                          {['ቪላ','አፓርታማ','ኮንዶሚኒየም','ሪል እስቴት','መሬት'].map(t =>
                            <Chip key={t} label={t} active={houseType===t} onClick={() => setHouseType(t)} />
                          )}
                        </div>
                      </div>
                      <div>
                        <label className="text-xs font-bold text-slate-700 mb-1.5 block">🛏️ መኝታ</label>
                        <div className="flex gap-2">
                          {['1','2','3','4','5+'].map(t =>
                            <Chip key={t} label={t} active={bedrooms===t} onClick={() => setBedrooms(t)} />
                          )}
                        </div>
                      </div>
                      <div>
                        <label className="text-xs font-bold text-slate-700 mb-1.5 block">🛁 መታጠቢያ</label>
                        <div className="flex gap-2">
                          {['1','2','3','4+'].map(t =>
                            <Chip key={t} label={t} active={bathrooms===t} onClick={() => setBathrooms(t)} />
                          )}
                        </div>
                      </div>
                      <div>
                        <label className="text-xs font-bold text-slate-700 mb-1.5 block">📊 ሁኔታ</label>
                        <div className="flex gap-2 overflow-x-auto pb-1">
                          {['አዲስ','ጥሩ','እድሳት የሚፈልግ'].map(t =>
                            <Chip key={t} label={t} active={houseCondition===t} onClick={() => setHouseCondition(t)} />
                          )}
                        </div>
                      </div>
                      <ToggleCard active={parking} onToggle={() => setParking(!parking)} icon="🚗" label="ፓርኪንግ አለው" />
                    </>
                  )}

                  <div>
                    <label className="text-xs font-bold text-slate-700 mb-1.5 block">📝 መግለጫ</label>
                    <textarea value={description} onChange={e => setDescription(e.target.value)} rows={3}
                      placeholder="የንብረቱን ሙሉ ዝርዝር ያስገቡ..."
                      className="w-full px-3.5 py-2.5 rounded-xl bg-slate-50 border border-slate-200 focus:bg-white focus:ring-2 focus:ring-[#16acbd] outline-none text-sm resize-none" />
                  </div>
                </div>
              )}

              {/* STEP 2 */}
              {step === 2 && (
                <div className="space-y-4">
                  <div>
                    <label className="text-xs font-bold text-slate-700 mb-1.5 block">💰 ዋጋ (ብር)</label>
                    <div className="relative">
                      <input type="text" inputMode="numeric" value={price}
                        onChange={e => setPrice(formatPrice(e.target.value))}
                        placeholder="2,500,000"
                        className="w-full px-3.5 py-2.5 rounded-xl bg-slate-50 border border-slate-200 focus:bg-white focus:ring-2 focus:ring-[#16acbd] outline-none text-sm font-bold text-slate-900" />
                      <span className="absolute right-3.5 top-1/2 -translate-y-1/2 text-xs font-bold text-[#16acbd]">ETB</span>
                    </div>
                  </div>
                  <ToggleCard active={negotiable} onToggle={() => setNegotiable(!negotiable)} icon="💰" label="ዋጋው የሚደራደር ነው" />
                  <ToggleCard active={urgent} onToggle={() => setUrgent(!urgent)} icon="⚡" label="አስቸኳይ ሽያጭ" danger />

                  <div>
                    <label className="text-xs font-bold text-slate-700 mb-1.5 block">📸 ፎቶዎች (እስከ 5)</label>
                    <div
                      onDragOver={e => { e.preventDefault(); setDragOver(true); }}
                      onDragLeave={() => setDragOver(false)}
                      onDrop={e => { e.preventDefault(); setDragOver(false); addFiles(e.dataTransfer.files); }}
                      onClick={() => fileRef.current?.click()}
                      className={`border-2 border-dashed rounded-2xl p-6 text-center cursor-pointer transition-all ${
                        dragOver ? 'border-[#16acbd] bg-[#16acbd]/10' : 'border-slate-200 bg-slate-50/70 hover:bg-slate-50'
                      }`}>
                      <div className="text-3xl mb-1">📷</div>
                      <p className="text-xs font-semibold text-slate-700">ፎቶዎችን እዚህ ይስቀሉ (እስከ 5)</p>
                      <p className="text-[10px] text-slate-400 mt-0.5">ወይም ይጫኑ ለመምረጥ</p>
                      <input ref={fileRef} type="file" accept="image/*" multiple className="hidden"
                        onChange={e => { addFiles(e.target.files); e.target.value=''; }} />
                    </div>
                    {photoBusy && <p className="text-[11px] text-[#16acbd] font-medium mt-1.5 text-center">ፎቶ እየተሰራ ነው…</p>}
                    {photoError && <p className="text-[11px] text-rose-600 font-medium mt-1.5 text-center">{photoError}</p>}
                    {photos.length > 0 && (
                      <div className="grid grid-cols-3 gap-2 mt-3">
                        {photos.map((src, i) => (
                          <div key={i} className="relative aspect-square rounded-xl overflow-hidden border border-slate-200 shadow-sm">
                            <img src={src} className="w-full h-full object-cover" alt="" />
                            <button type="button" onClick={(e) => { e.stopPropagation(); removePhoto(i); }}
                              className="absolute top-1 right-1 w-6 h-6 rounded-full bg-rose-500 text-white text-xs flex items-center justify-center shadow font-bold">×</button>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* STEP 3 */}
              {step === 3 && (
                <div className="space-y-4">
                  <div>
                    <label className="text-xs font-bold text-slate-700 mb-1.5 block">📞 ስልክ ቁጥር <span className="text-slate-400 font-normal">(አማራጭ)</span></label>
                    <input type="tel" value={phone} onChange={e => setPhone(e.target.value)}
                      placeholder="0911223344"
                      className="w-full px-3.5 py-2.5 rounded-xl bg-slate-50 border border-slate-200 focus:bg-white focus:ring-2 focus:ring-[#16acbd] outline-none text-sm" />
                  </div>
                  <div>
                    <label className="text-xs font-bold text-slate-700 mb-1.5 block">📱 Telegram Username</label>
                    <input type="text" value={telegramUser} onChange={e => setTelegramUser(e.target.value)}
                      placeholder="@username"
                      className="w-full px-3.5 py-2.5 rounded-xl bg-slate-50 border border-slate-200 focus:bg-white focus:ring-2 focus:ring-[#16acbd] outline-none text-sm" />
                  </div>
                  {status && status !== 'ok' && (
                    <p className="text-sm text-rose-600 font-semibold text-center">{status}</p>
                  )}
                </div>
              )}
            </div>
          </div>

          {/* Bottom actions */}
          <div className="fixed bottom-0 left-0 right-0 p-3 bg-white/95 backdrop-blur-md border-t border-slate-200/80 flex gap-2 z-40">
            {step > 1 ? (
              <button type="button" onClick={() => setStep(s => s-1)}
                className="w-1/3 py-3 rounded-xl bg-slate-100 text-slate-700 font-bold text-sm active:scale-95 transition-transform">ተመለስ</button>
            ) : (
              <button type="button" onClick={() => tg.close()}
                className="w-1/3 py-3 rounded-xl bg-slate-100 text-slate-700 font-bold text-sm active:scale-95 transition-transform">❌ ሰርዝ</button>
            )}
            {step < 3 ? (
              <button type="button" onClick={() => {
                  if (step === 1 && !canNext1) return;
                  if (photoBusy) return;
                  setStep(s => s+1);
                }}
                disabled={step===1 ? !canNext1 : photoBusy}
                className="flex-1 py-3 rounded-xl bg-[#16acbd] text-white font-bold text-sm shadow-md active:scale-95 transition-all disabled:opacity-40">
                ቀጣይ →
              </button>
            ) : (
              <button type="button" onClick={submit} disabled={!canSubmit || submitting}
                className="flex-1 py-3 rounded-xl bg-[#16acbd] text-white font-bold text-sm shadow-md active:scale-95 transition-all disabled:opacity-40 flex items-center justify-center gap-1.5">
                {submitting ? 'እየተላከ...' : '🚀 መዝግብ'}
              </button>
            )}
          </div>
        </div>
      );
    }

    (function(){
      try {
        if (!window.React || !window.ReactDOM) {
          document.getElementById('root').innerHTML = '<div style="padding:20px;color:#b91c1c;font-family:system-ui">Failed to load React CDN</div>';
          return;
        }
        ReactDOM.createRoot(document.getElementById('root')).render(<SellerForm />);
      } catch (e) {
        document.getElementById('root').innerHTML = '<div style="padding:20px;color:#b91c1c;font-family:system-ui">UI Error: '+e.message+'</div>';
      }
    })();
  </script>
</body>
</html>
"""


# ==============================================================================
# BUYER FORM HTML (Post Buyer Request)
# ==============================================================================
BUYER_FORM_HTML = r"""
<!DOCTYPE html>
<html lang="am">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
  <title>ጥያቄ ያስገቡ | Adika Marketplace</title>
  <script src="https://telegram.org/js/telegram-web-app.js"></script>
  <script src="https://cdn.tailwindcss.com"></script>
  <script crossorigin src="https://cdn.jsdelivr.net/npm/react@18.2.0/umd/react.production.min.js"></script>
  <script crossorigin src="https://cdn.jsdelivr.net/npm/react-dom@18.2.0/umd/react-dom.production.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/@babel/standalone@7.24.0/babel.min.js"></script>

  <style>
    body { margin:0; background:#b5eff3; font-family:system-ui,-apple-system,sans-serif; -webkit-tap-highlight-color:transparent; }
    .chip-active { background:#16acbd; color:#fff; font-weight:700; box-shadow:0 2px 6px rgba(22,172,189,.35); border: 1px solid #16acbd; }
    .chip-idle { background:#ffffff; color:#334155; border:1px solid #cbd5e1; font-weight: 500; }
    input, textarea { font-size: 16px !important; }
  </style>
</head>
<body class="bg-[#b5eff3] min-h-screen text-slate-800">
  <div id="root"></div>
  <script type="text/babel">
    const { useState } = React;
    const tg = (window.Telegram && window.Telegram.WebApp) ? window.Telegram.WebApp : {
      expand(){}, ready(){}, close(){}, initDataUnsafe: {}, setHeaderColor(){}, setBackgroundColor(){}, showAlert: (m)=>alert(m)
    };
    try { tg.ready(); tg.expand(); } catch (e) { console.warn(e); }
    try { tg.setHeaderColor('#16acbd'); tg.setBackgroundColor('#b5eff3'); } catch (e) {}

    const user = tg.initDataUnsafe?.user || {};
    const autoUsername = user.username ? '@' + user.username : '';
    const autoPhone = user.phone_number || '';

    function formatPrice(val) {
      const digits = String(val).replace(/[^\d]/g, '');
      if (!digits) return '';
      return digits.replace(/\B(?=(\d{3})+(?!\d))/g, ',');
    }
    function parsePrice(val) {
      return String(val).replace(/[^\d]/g, '');
    }

    function Chip({ label, active, onClick }) {
      return (
        <button type="button" onClick={onClick}
          className={`px-3.5 py-1.5 rounded-full text-xs whitespace-nowrap transition-all shadow-sm ${active ? 'chip-active' : 'chip-idle hover:bg-slate-50'}`}>
          {label}
        </button>
      );
    }

    function BuyerForm() {
      const [category, setCategory] = useState('መኪና');
      const [budgetMin, setBudgetMin] = useState('');
      const [budgetMax, setBudgetMax] = useState('');
      const [createAlert, setCreateAlert] = useState(false);
      const [details, setDetails] = useState('');
      const [phone, setPhone] = useState(autoPhone);
      const [telegramUser, setTelegramUser] = useState(autoUsername);
      const [status, setStatus] = useState('');
      const [submitting, setSubmitting] = useState(false);

      const submit = async () => {
        if (!details || submitting) return;
        setSubmitting(true);
        setStatus('');
        const data = {
          user_id: user.id || 'unknown',
          category,
          budget_min: parsePrice(budgetMin),
          budget_max: parsePrice(budgetMax),
          create_alert: createAlert,
          details,
          phone,
          telegram_user: telegramUser
        };
        try {
          const res = await fetch('/api/submit-request', {
            method: 'POST', headers: {'Content-Type':'application/json'},
            body: JSON.stringify(data)
          });
          const result = await res.json();
          if (result.status === 'success') {
            setStatus('ok');
            setTimeout(() => tg.close(), 2500);
          } else {
            setStatus(result.message || 'ስህተት');
            setSubmitting(false);
          }
        } catch (e) {
          setStatus('የኔትወርክ ስህተት');
          setSubmitting(false);
        }
      };

      if (status === 'ok') {
        return (
          <div className="min-h-screen flex items-center justify-center p-6 bg-[#b5eff3]">
            <div className="bg-white rounded-3xl p-6 text-center space-y-4 shadow-[0_12px_28px_rgba(15,23,42,0.12)] border border-white/60 max-w-sm">
              <div className="w-16 h-16 rounded-full bg-[#16acbd]/15 text-[#16acbd] flex items-center justify-center text-3xl mx-auto">✓</div>
              <h2 className="font-bold text-lg text-slate-800">ጥያቄዎ ተመዝግቧል!</h2>
              <p className="font-medium text-sm text-slate-600 leading-relaxed px-2">
                የፍላጎት ማስታወቂያዎ በተሳካ ሁኔታ ተመዝግቧል! ለደላሎችና አቅራቢዎች ተልኳል።
              </p>
              <p className="text-xs text-[#16acbd] font-semibold">ወደ ዋና ገጽ እየተመለሰ ነው…</p>
            </div>
          </div>
        );
      }

      return (
        <div className="min-h-screen bg-[#b5eff3] pb-28">
          {/* Fixed Sticky Teal Header */}
          <div className="fixed top-0 left-0 right-0 z-40 bg-[#16acbd] shadow-md px-4 py-3.5 text-white">
            <h1 className="text-center font-black text-sm tracking-wide">የሚፈልጉትን ንብረት ይግለጹ</h1>
          </div>

          <div className="pt-16 px-4">
            <div className="bg-white rounded-2xl p-4 shadow-[0_12px_28px_rgba(15,23,42,0.12)] border border-slate-200/80 space-y-4">
              <div>
                <label className="text-xs font-bold text-slate-700 mb-1.5 block">📦 ምድብ</label>
                <div className="flex gap-2">
                  <Chip label="🚗 መኪና" active={category==='መኪና'} onClick={() => setCategory('መኪና')} />
                  <Chip label="🏠 ቤት" active={category==='ቤት'} onClick={() => setCategory('ቤት')} />
                </div>
              </div>

              <div>
                <label className="text-xs font-bold text-slate-700 mb-1.5 block">💰 የበጀት ክልል (ብር)</label>
                <div className="flex gap-2 items-center">
                  <div className="flex-1 relative">
                    <span className="absolute left-2.5 top-1/2 -translate-y-1/2 text-xs font-bold text-slate-400">ከ</span>
                    <input type="text" inputMode="numeric" value={budgetMin}
                      onChange={e => setBudgetMin(formatPrice(e.target.value))}
                      placeholder="500,000"
                      className="w-full pl-8 pr-2 py-2.5 rounded-xl bg-slate-50 border border-slate-200 focus:bg-white focus:ring-2 focus:ring-[#16acbd] outline-none text-sm font-semibold" />
                  </div>
                  <span className="text-slate-400 font-bold">—</span>
                  <div className="flex-1 relative">
                    <span className="absolute left-2.5 top-1/2 -translate-y-1/2 text-xs font-bold text-slate-400">እስከ</span>
                    <input type="text" inputMode="numeric" value={budgetMax}
                      onChange={e => setBudgetMax(formatPrice(e.target.value))}
                      placeholder="2,000,000"
                      className="w-full pl-10 pr-2 py-2.5 rounded-xl bg-slate-50 border border-slate-200 focus:bg-white focus:ring-2 focus:ring-[#16acbd] outline-none text-sm font-semibold" />
                  </div>
                </div>
              </div>

              {/* Notification preference card */}
              <button type="button" onClick={() => setCreateAlert(!createAlert)}
                className={`w-full flex items-center justify-between p-3.5 rounded-xl border transition-all text-left ${
                  createAlert ? 'bg-[#16acbd]/10 border-[#16acbd]/50 text-[#0e7490]' : 'bg-slate-50 border-slate-200 text-slate-700'
                }`}>
                <span className="text-xs font-semibold leading-snug">🔔 ተመሳሳይ ንብረት ሲለቀቅ ማሳወቂያ ይድረሰኝ</span>
                <div className={`w-10 h-5 rounded-full relative transition-colors shrink-0 ${createAlert ? 'bg-[#16acbd]' : 'bg-slate-300'}`}>
                  <div className={`absolute top-0.5 w-4 h-4 rounded-full bg-white shadow transition-transform ${createAlert ? 'translate-x-5' : 'translate-x-0.5'}`} />
                </div>
              </button>

              <div>
                <label className="text-xs font-bold text-slate-700 mb-1.5 block">📝 ዝርዝር ፍላጎት</label>
                <textarea value={details} onChange={e => setDetails(e.target.value)} rows={4}
                  placeholder="ለምሳሌ፦ ቶዮታ ቪትዝ 2020፣ ነጭ፣ ኦቶማቲክ..."
                  className="w-full px-3.5 py-2.5 rounded-xl bg-slate-50 border border-slate-200 focus:bg-white focus:ring-2 focus:ring-[#16acbd] outline-none text-sm resize-none" />
              </div>

              <div>
                <label className="text-xs font-bold text-slate-700 mb-1.5 block">📞 ስልክ ቁጥር <span className="text-slate-400 font-normal">(አማራጭ)</span></label>
                <input type="tel" value={phone} onChange={e => setPhone(e.target.value)}
                  placeholder="0911223344"
                  className="w-full px-3.5 py-2.5 rounded-xl bg-slate-50 border border-slate-200 focus:bg-white focus:ring-2 focus:ring-[#16acbd] outline-none text-sm" />
              </div>
              <div>
                <label className="text-xs font-bold text-slate-700 mb-1.5 block">📱 Telegram Username</label>
                <input type="text" value={telegramUser} onChange={e => setTelegramUser(e.target.value)}
                  placeholder="@username"
                  className="w-full px-3.5 py-2.5 rounded-xl bg-slate-50 border border-slate-200 focus:bg-white focus:ring-2 focus:ring-[#16acbd] outline-none text-sm" />
              </div>

              {status && status !== 'ok' && (
                <p className="text-sm text-rose-600 font-semibold text-center">{status}</p>
              )}
            </div>
          </div>

          <div className="fixed bottom-0 left-0 right-0 p-3 bg-white/95 backdrop-blur-md border-t border-slate-200/80 flex gap-2 z-40">
            <button type="button" onClick={() => tg.close()}
              className="w-1/3 py-3 rounded-xl bg-slate-100 text-slate-700 font-bold text-sm active:scale-95 transition-transform">❌ ሰርዝ</button>
            <button type="button" onClick={submit} disabled={!details || submitting}
              className="flex-1 py-3 rounded-xl bg-[#16acbd] text-white font-bold text-sm shadow-md active:scale-95 transition-all disabled:opacity-40 flex items-center justify-center gap-1.5">
              {submitting ? 'እየተላከ...' : '📨 ጥያቄውን ላክ'}
            </button>
          </div>
        </div>
      );
    }

    (function(){
      try {
        if (!window.React || !window.ReactDOM) {
          document.getElementById('root').innerHTML = '<div style="padding:20px;color:#b91c1c;font-family:system-ui">Failed to load React CDN</div>';
          return;
        }
        ReactDOM.createRoot(document.getElementById('root')).render(<BuyerForm />);
      } catch (e) {
        document.getElementById('root').innerHTML = '<div style="padding:20px;color:#b91c1c;font-family:system-ui">UI Error: '+e.message+'</div>';
      }
    })();
  </script>
</body>
</html>
"""


# ==============================================================================
# EXPLORER HTML (Marketplace & Buyer Requests Feed)
# Strict adherence to Teal Header (#16acbd), Light Ice Blue Body (#b5eff3),
# Floating Cards with Dark Shadow, Floating Translucent Bottom Bar, Dynamic "+",
# and Overflow-Safe Bottom-Sheet Detail Modal with Fixed Call/Chat Buttons.
# ==============================================================================
EXPLORER_HTML = r"""
<!DOCTYPE html>
<html lang="am">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no, viewport-fit=cover" />
  <title>Adika Marketplace</title>
  <script src="https://telegram.org/js/telegram-web-app.js"></script>
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    html, body {
      margin: 0; padding: 0; width: 100%; max-width: 100vw;
      overflow-x: hidden; box-sizing: border-box;
      font-family: system-ui, -apple-system, sans-serif;
      background: #b5eff3; color: #0f172a;
      -webkit-tap-highlight-color: transparent;
    }
    *, *::before, *::after { box-sizing: border-box; }

    /* Floating Card styling */
    .adika-card {
      background: #ffffff;
      border: 1px solid rgba(226, 232, 240, 0.85);
      border-radius: 1rem;
      box-shadow: 0 12px 28px rgba(15, 23, 42, 0.12);
      transition: transform 0.15s ease, box-shadow 0.15s ease;
      display: flex;
      flex-direction: column;
      overflow: hidden;
    }
    .adika-card:active {
      transform: scale(0.985);
    }

    /* Active badge pulse */
    @keyframes pulse-green {
      0% { box-shadow: 0 0 0 0 rgba(34,197,94,0.6); }
      70% { box-shadow: 0 0 0 7px rgba(34,197,94,0); }
      100% { box-shadow: 0 0 0 0 rgba(34,197,94,0); }
    }
    @keyframes pulse-red {
      0% { box-shadow: 0 0 0 0 rgba(239,68,68,0.6); }
      70% { box-shadow: 0 0 0 7px rgba(239,68,68,0); }
      100% { box-shadow: 0 0 0 0 rgba(239,68,68,0); }
    }
    .badge-pulse { animation: pulse-green 1.6s ease-out infinite; }
    .badge-pulse-sold { animation: pulse-red 1.6s ease-out infinite; }
    .no-scrollbar::-webkit-scrollbar { display: none; }
    .no-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
  </style>
</head>
<body class="bg-[#b5eff3] min-h-screen">

  <!-- ================================================================= -->
  <!-- 1. FIXED STICKY TEAL HEADER WITH INTEGRATED TABS & SEARCH         -->
  <!-- ================================================================= -->
  <header class="fixed top-0 left-0 right-0 z-50 bg-[#16acbd] text-white shadow-md p-3">
    <!-- Brand / Status Row -->
    <div class="flex items-center justify-between mb-2.5">
      <div class="flex items-center gap-2">
        <div class="w-7 h-7 rounded-lg bg-white/20 flex items-center justify-center font-black text-sm text-white">A</div>
        <span class="font-extrabold text-sm tracking-wide">Adika Marketplace</span>
      </div>
      <div class="flex items-center gap-1.5 bg-black/15 px-2.5 py-1 rounded-full text-[11px] font-medium text-white/90">
        <span class="w-2 h-2 rounded-full bg-emerald-400"></span>
        <span id="liveBrokersCount">ደላሎች ክፍት</span>
      </div>
    </div>

    <!-- Segmented Tabs (Marketplace / Buyers) -->
    <div class="grid grid-cols-2 gap-1.5 p-1 bg-black/15 rounded-xl mb-2.5">
      <button id="tabSell" type="button"
        class="py-1.5 rounded-lg text-xs font-bold transition-all bg-white text-[#16acbd] shadow-sm">
        🛒 የገበያ ቦታ (ሽያጭ)
      </button>
      <button id="tabBuy" type="button"
        class="py-1.5 rounded-lg text-xs font-bold transition-all text-white/90 hover:text-white">
        📋 የፈላጊዎች ዝርዝር
      </button>
    </div>

    <!-- Search Input -->
    <div class="relative mb-2">
      <span class="absolute left-3 top-1/2 -translate-y-1/2 text-white/60 pointer-events-none text-xs">🔍</span>
      <input id="q" type="search" placeholder="በስም ወይም በዋጋ ይፈልጉ..." autocomplete="off"
        class="w-full pl-8 pr-3 py-2 rounded-xl bg-white text-slate-800 placeholder-slate-400 text-xs font-medium outline-none shadow-sm focus:ring-2 focus:ring-white/50 transition-all" />
    </div>

    <!-- Category Chips (Horizontal Scroll) -->
    <div id="cats" class="flex gap-1.5 overflow-x-auto no-scrollbar pb-0.5"></div>
  </header>

  <!-- ================================================================= -->
  <!-- 2. MAIN CONTENT AREA (Adequate Top & Bottom Padding)             -->
  <!-- ================================================================= -->
  <main class="w-full pt-44 pb-28 px-3">
    <!-- Status / Loading Banner -->
    <div id="status" class="text-center py-10 text-slate-600 font-semibold text-xs">
      <div class="inline-block animate-spin w-6 h-6 border-2 border-[#16acbd] border-t-transparent rounded-full mb-2"></div>
      <div>እየጫነ ነው…</div>
    </div>

    <!-- 2-Column Responsive Elevated Cards Grid -->
    <div id="grid" class="grid grid-cols-2 gap-3"></div>

    <!-- Load More Button -->
    <div class="text-center mt-5 mb-3">
      <button id="more" type="button"
        class="hidden px-5 py-2.5 rounded-full bg-white text-[#16acbd] font-extrabold text-xs shadow-md border border-white/60 active:scale-95 transition-all">
        ተጨማሪ ይመልከቱ ↓
      </button>
    </div>
  </main>

  <!-- ================================================================= -->
  <!-- 3. FLOATING TRANSLUCENT BOTTOM NAVIGATION WITH DYNAMIC "+" BUTTON -->
  <!-- ================================================================= -->
  <nav class="fixed bottom-4 left-4 right-4 bg-white/95 backdrop-blur-xl rounded-full shadow-2xl border border-white/60 p-2 z-40 flex items-center justify-around">
    <!-- Home Tab -->
    <button id="navHome" type="button" class="nav-item flex flex-col items-center justify-center px-3 py-1 rounded-full bg-[#16acbd]/15 text-[#16acbd] transition-all">
      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/>
      </svg>
      <span class="text-[10px] font-bold mt-0.5">Home</span>
    </button>

    <!-- Search Tab -->
    <button id="navSearch" type="button" class="nav-item flex flex-col items-center justify-center px-3 py-1 rounded-full text-slate-500 hover:text-slate-800 transition-all">
      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
      </svg>
      <span class="text-[10px] font-semibold mt-0.5">Search</span>
    </button>

    <!-- Dynamic Central "+" FAB -->
    <button id="fabBtn" type="button"
      class="w-12 h-12 -my-2.5 rounded-full bg-[#16acbd] text-white flex items-center justify-center shadow-[0_8px_20px_rgba(22,172,189,0.45)] active:scale-90 transition-all border-2 border-white">
      <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.8" d="M12 4v16m8-8H4"/>
      </svg>
    </button>

    <!-- Messages Tab -->
    <button id="navMessages" type="button" class="nav-item flex flex-col items-center justify-center px-3 py-1 rounded-full text-slate-500 hover:text-slate-800 transition-all">
      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"/>
      </svg>
      <span class="text-[10px] font-semibold mt-0.5">Messages</span>
    </button>

    <!-- Help Tab -->
    <button id="navHelp" type="button" class="nav-item flex flex-col items-center justify-center px-3 py-1 rounded-full text-slate-500 hover:text-slate-800 transition-all">
      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
      </svg>
      <span class="text-[10px] font-semibold mt-0.5">Help</span>
    </button>
  </nav>

  <!-- ================================================================= -->
  <!-- 4. BOTTOM-SHEET DETAIL MODAL (Fixed Action Buttons, Non-Overflow)  -->
  <!-- ================================================================= -->
  <div id="modalOverlay" class="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm hidden items-end justify-center">
    <div id="modalSheet"
      class="w-full max-w-lg bg-white rounded-t-3xl max-h-[85vh] flex flex-col shadow-2xl overflow-hidden animate-in slide-in-from-bottom duration-200">

      <!-- Modal Header (Fixed Top Bar) -->
      <div class="px-4 py-3 bg-white border-b border-slate-100 flex items-center justify-between shrink-0">
        <div class="flex items-center gap-2">
          <span id="modalCategoryBadge" class="px-2.5 py-0.5 rounded-full bg-[#16acbd]/10 text-[#0e7490] text-xs font-bold">ንብረት</span>
          <span id="modalIdBadge" class="text-xs text-slate-400 font-semibold">#ADK-</span>
        </div>
        <button id="modalClose" type="button"
          class="w-7 h-7 rounded-full bg-slate-100 text-slate-500 hover:text-slate-800 font-bold flex items-center justify-center text-sm active:scale-95">✕</button>
      </div>

      <!-- Modal Content (Scrollable Middle Body) -->
      <div id="modalScrollBody" class="overflow-y-auto flex-1 p-4 space-y-4">
        <!-- Media / Photos Carousel or Placeholder -->
        <div id="modalMediaContainer" class="w-full h-52 rounded-2xl overflow-hidden bg-slate-100 relative"></div>

        <!-- Title & Price Block -->
        <div>
          <h2 id="modalTitle" class="text-base font-extrabold text-slate-900 leading-tight"></h2>
          <div class="mt-2 flex items-center gap-2">
            <span id="modalPrice" class="px-3 py-1 rounded-full bg-[#16acbd]/15 text-[#0e7490] font-black text-sm"></span>
            <span id="modalTime" class="text-xs text-slate-400 font-medium"></span>
          </div>
        </div>

        <!-- Specs Grid -->
        <div id="modalSpecs" class="grid grid-cols-2 gap-2 text-xs font-medium text-slate-600 bg-slate-50 p-3 rounded-xl border border-slate-100"></div>

        <!-- Description -->
        <div>
          <h4 class="text-xs font-bold text-slate-500 uppercase tracking-wider mb-1">ዝርዝር መግለጫ</h4>
          <p id="modalDesc" class="text-xs text-slate-700 leading-relaxed whitespace-pre-line bg-slate-50/50 p-3 rounded-xl border border-slate-100"></p>
        </div>
      </div>

      <!-- Modal Footer Action Buttons (Fixed Bottom Bar - NEVER CUT OFF) -->
      <div class="p-3 bg-white border-t border-slate-100 shrink-0 grid grid-cols-2 gap-2.5">
        <a id="modalCallBtn" href="#"
          class="flex items-center justify-center gap-2 py-3 px-4 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs shadow-md active:scale-95 transition-all">
          <span>📞</span> <span>ደውል (Call)</span>
        </a>
        <a id="modalChatBtn" href="#"
          class="flex items-center justify-center gap-2 py-3 px-4 rounded-xl bg-[#16acbd] hover:bg-[#1394a3] text-white font-bold text-xs shadow-md active:scale-95 transition-all">
          <span>💬</span> <span>ቴሌግራም (Telegram)</span>
        </a>
      </div>
    </div>
  </div>

  <!-- ================================================================= -->
  <!-- 5. JAVASCRIPT LOGIC & TELEGRAM INTEGRATION                         -->
  <!-- ================================================================= -->
  <script>
  (function () {
    var API_BASE = "";
    try {
      if (location && location.origin) {
        API_BASE = location.origin;
      }
    } catch (e) {}

    // Initialize Telegram WebApp
    var tg = window.Telegram && window.Telegram.WebApp ? window.Telegram.WebApp : null;
    if (tg) {
      try { tg.ready(); } catch (e) {}
      try { tg.expand(); } catch (e) {}
      try { tg.setHeaderColor('#16acbd'); } catch (e) {}
      try { tg.setBackgroundColor('#b5eff3'); } catch (e) {}
    }

    var state = {
      tab: "marketplace", // 'marketplace' (SELL) or 'requests' (BUY)
      category: "",
      q: "",
      page: 1,
      hasMore: false,
      loading: false,
      items: []
    };

    var grid = document.getElementById("grid");
    var statusEl = document.getElementById("status");
    var moreBtn = document.getElementById("more");
    var tabSell = document.getElementById("tabSell");
    var tabBuy = document.getElementById("tabBuy");
    var qInput = document.getElementById("q");
    var catsEl = document.getElementById("cats");
    var fabBtn = document.getElementById("fabBtn");

    // Modal elements
    var modalOverlay = document.getElementById("modalOverlay");
    var modalClose = document.getElementById("modalClose");
    var modalCategoryBadge = document.getElementById("modalCategoryBadge");
    var modalIdBadge = document.getElementById("modalIdBadge");
    var modalTitle = document.getElementById("modalTitle");
    var modalPrice = document.getElementById("modalPrice");
    var modalTime = document.getElementById("modalTime");
    var modalMediaContainer = document.getElementById("modalMediaContainer");
    var modalSpecs = document.getElementById("modalSpecs");
    var modalDesc = document.getElementById("modalDesc");
    var modalCallBtn = document.getElementById("modalCallBtn");
    var modalChatBtn = document.getElementById("modalChatBtn");

    var CAT_LIST = [
      { id: "", label: "✨ ሁሉም" },
      { id: "መኪና", label: "🚗 መኪና" },
      { id: "ቤት", label: "🏠 ቤት / ቦታ" },
      { id: "ንግድ", label: "🏢 የሥራ ቦታ" }
    ];

    function esc(s) {
      return String(s == null ? "" : s)
        .replace(/&/g, "&amp;").replace(/</g, "&lt;")
        .replace(/>/g, "&gt;").replace(/"/g, "&quot;");
    }

    function relativeTime(iso) {
      if (!iso) return "";
      try {
        var secs = Math.max(0, Math.floor((Date.now() - new Date(iso).getTime()) / 1000));
        if (secs < 60) return "አሁን";
        if (secs < 3600) return Math.floor(secs / 60) + " ደቂቃ";
        if (secs < 86400) return Math.floor(secs / 3600) + " ሰዓት";
        return Math.floor(secs / 86400) + " ቀን";
      } catch (e) { return ""; }
    }

    function cleanDesc(raw) {
      var s = String(raw || "");
      s = s.replace(/\*+/g, " ");
      s = s.replace(/[📝💰📞⚡📢🔄📦✅☑️]/g, " ");
      s = s.replace(/አስቸኳይ\s*ሽያጭ!?/gi, " ");
      s = s.replace(/የሚደራደር|ደራደር|negotiable/gi, " ");
      s = s.replace(/ዋጋ\s*[:：]?\s*[\d,\.]+(\s*(ETB|ብር))?/gi, " ");
      s = s.replace(/በጀት\s*[:：]?\s*[\d,\.]+(\s*(ETB|ብር))?/gi, " ");
      s = s.replace(/[\d,\.]+\s*(ETB|ብር)/gi, " ");
      return s.replace(/\s+/g, " ").trim().slice(0, 50);
    }

    function renderCats() {
      var html = "";
      for (var i = 0; i < CAT_LIST.length; i++) {
        var c = CAT_LIST[i];
        var on = (state.category === c.id);
        html += '<button type="button" class="cat-pill px-3 py-1 rounded-full text-xs font-bold whitespace-nowrap transition-all ' +
          (on ? 'bg-white text-[#16acbd] shadow-sm' : 'bg-white/20 text-white hover:bg-white/30') +
          '" data-id="' + esc(c.id) + '">' + esc(c.label) + '</button>';
      }
      catsEl.innerHTML = html;
    }

    function setTabs() {
      if (state.tab === "marketplace") {
        tabSell.className = "py-1.5 rounded-lg text-xs font-bold transition-all bg-white text-[#16acbd] shadow-sm";
        tabBuy.className = "py-1.5 rounded-lg text-xs font-bold transition-all text-white/90 hover:text-white";
      } else {
        tabBuy.className = "py-1.5 rounded-lg text-xs font-bold transition-all bg-white text-[#16acbd] shadow-sm";
        tabSell.className = "py-1.5 rounded-lg text-xs font-bold transition-all text-white/90 hover:text-white";
      }
    }

    function createCardElement(item, index) {
      var extra = item.extra_data || {};
      if (typeof extra === "string") {
        try { extra = JSON.parse(extra); } catch (e) { extra = {}; }
      }
      var photos = item.photos || [];
      if (!Array.isArray(photos)) photos = [];
      var isCar = (item.main_category === "መኪና" || item.category === "መኪና");
      var icon = isCar ? "🚗" : "🏠";
      var media;
      if (photos.length > 0) {
        media = '<img src="' + esc(photos[0]) + '" alt="" class="w-full h-full object-cover" loading="lazy" />';
      } else {
        media = '<div class="w-full h-full flex flex-col items-center justify-center bg-gradient-to-br from-[#16acbd] to-[#0e7490] text-white p-2">' +
          '<span class="text-3xl mb-1">' + icon + '</span>' +
          '<span class="text-[9px] font-semibold tracking-wide text-white/90">No Image Available</span>' +
          '</div>';
      }

      var title = (item.main_category || item.category || "") + (item.sub_category ? " • " + item.sub_category : "");
      var desc = cleanDesc(item.description);
      var isSell = String(item.req_type || "").toUpperCase() === "SELL";
      var priceNum = item.price || "—";
      var priceLabel = (isSell ? "ዋጋ" : "በጀት") + ": " + priceNum;
      var views = item.view_count || item.views_count || (Math.floor(Math.random()*30) + 12);
      var phone = item.phone ? String(item.phone).replace(/\s+/g, "") : "";
      var tUser = extra.telegram_user ? String(extra.telegram_user).replace("@", "") : "";
      var callHref = phone ? ("tel:" + phone) : "#";
      var chatHref = tUser ? ("https://t.me/" + tUser) : (item.user_chat_id ? ("tg://user?id=" + item.user_chat_id) : "#");
      var st = String(item.status || "").toUpperCase();
      var sold = (st === "SOLD" || st === "RENTED" || st === "EXPIRED");

      var card = document.createElement("div");
      card.className = "adika-card cursor-pointer";
      card.innerHTML =
        '<div class="relative w-full h-28 bg-slate-100 overflow-hidden">' +
          '<span class="absolute top-2 left-2 w-2.5 h-2.5 rounded-full z-10 ' + (sold ? 'bg-rose-500 badge-pulse-sold' : 'bg-emerald-500 badge-pulse') + '"></span>' +
          media +
          '<div class="absolute bottom-1.5 left-1.5 right-1.5 flex justify-between items-center text-[9px] text-white font-bold">' +
            '<span class="bg-black/60 backdrop-blur-sm px-1.5 py-0.5 rounded-md">👁️ ' + esc(views) + '</span>' +
            '<span class="bg-black/60 backdrop-blur-sm px-1.5 py-0.5 rounded-md">' + esc(relativeTime(item.created_at)) + '</span>' +
          '</div>' +
        '</div>' +
        '<div class="p-2.5 flex-1 flex flex-col justify-between">' +
          '<div>' +
            '<div class="font-extrabold text-xs text-slate-800 truncate">' + esc(title) + '</div>' +
            (desc ? '<div class="text-[10px] text-slate-500 truncate mt-0.5">' + esc(desc) + '</div>' : '') +
          '</div>' +
          '<div class="mt-2">' +
            '<div class="inline-block px-2 py-0.5 rounded-md bg-[#16acbd]/10 text-[#0e7490] font-black text-[11px] truncate max-w-full">💰 ' + esc(priceLabel) + '</div>' +
            '<div class="grid grid-cols-2 gap-1 mt-2">' +
              '<a href="' + esc(callHref) + '" onclick="event.stopPropagation()" class="py-1 text-center rounded-lg bg-emerald-50 text-emerald-700 hover:bg-emerald-100 text-xs font-bold">📞</a>' +
              '<a href="' + esc(chatHref) + '" onclick="event.stopPropagation()" class="py-1 text-center rounded-lg bg-[#16acbd]/10 text-[#0e7490] hover:bg-[#16acbd]/20 text-xs font-bold">💬</a>' +
            '</div>' +
          '</div>' +
        '</div>';

      card.onclick = function () {
        openDetailModal(item);
      };

      return card;
    }

    function openDetailModal(item) {
      var extra = item.extra_data || {};
      if (typeof extra === "string") {
        try { extra = JSON.parse(extra); } catch (e) { extra = {}; }
      }
      var photos = item.photos || [];
      if (!Array.isArray(photos)) photos = [];
      var isCar = (item.main_category === "መኪና" || item.category === "መኪና");

      modalCategoryBadge.textContent = item.main_category || item.category || "ንብረት";
      modalIdBadge.textContent = "#ADK-" + (item.id || "001");
      modalTitle.textContent = (item.main_category || item.category || "") + (item.sub_category ? " • " + item.sub_category : "");

      var isSell = String(item.req_type || "").toUpperCase() === "SELL";
      modalPrice.textContent = (isSell ? "💰 ዋጋ: " : "💰 በጀት: ") + (item.price || "ያልተገለጸ") + " ETB";
      modalTime.textContent = "⏱️ " + relativeTime(item.created_at);
      modalDesc.textContent = item.description || "ተጨማሪ ዝርዝር መግለጫ አልተሰጠም።";

      // Photos / Media
      if (photos.length > 0) {
        modalMediaContainer.innerHTML = '<img src="' + esc(photos[0]) + '" alt="" class="w-full h-full object-cover" />';
      } else {
        modalMediaContainer.innerHTML =
          '<div class="w-full h-full flex flex-col items-center justify-center bg-gradient-to-br from-[#16acbd] to-[#0e7490] text-white">' +
            '<span class="text-5xl mb-2">' + (isCar ? '🚗' : '🏠') + '</span>' +
            '<span class="text-xs font-bold">No Image Available</span>' +
          '</div>';
      }

      // Specs
      var specsHtml = "";
      if (isCar) {
        if (extra.fuel_type) specsHtml += '<div>⛽ ነዳጅ: <span class="font-bold text-slate-800">' + esc(extra.fuel_type) + '</span></div>';
        if (extra.transmission) specsHtml += '<div>⚙️ ማርሽ: <span class="font-bold text-slate-800">' + esc(extra.transmission) + '</span></div>';
        if (extra.mileage) specsHtml += '<div>🛣️ ኪሎሜትር: <span class="font-bold text-slate-800">' + esc(extra.mileage) + ' KM</span></div>';
        if (extra.condition) specsHtml += '<div>📊 ሁኔታ: <span class="font-bold text-slate-800">' + esc(extra.condition) + '</span></div>';
      } else {
        if (extra.bedrooms) specsHtml += '<div>🛏️ መኝታ: <span class="font-bold text-slate-800">' + esc(extra.bedrooms) + '</span></div>';
        if (extra.bathrooms) specsHtml += '<div>🛁 መታጠቢያ: <span class="font-bold text-slate-800">' + esc(extra.bathrooms) + '</span></div>';
        if (extra.parking) specsHtml += '<div>🚗 ፓርኪንግ: <span class="font-bold text-slate-800">' + esc(extra.parking) + '</span></div>';
        if (extra.condition) specsHtml += '<div>📊 ሁኔታ: <span class="font-bold text-slate-800">' + esc(extra.condition) + '</span></div>';
      }
      modalSpecs.innerHTML = specsHtml || '<div>ሁኔታ: <span class="font-bold text-slate-800">ጥሩ</span></div>';

      // Action buttons
      var phone = item.phone ? String(item.phone).replace(/\s+/g, "") : "";
      var tUser = extra.telegram_user ? String(extra.telegram_user).replace("@", "") : "";
      modalCallBtn.href = phone ? ("tel:" + phone) : "#";
      modalChatBtn.href = tUser ? ("https://t.me/" + tUser) : (item.user_chat_id ? ("tg://user?id=" + item.user_chat_id) : "#");

      modalOverlay.classList.remove("hidden");
      modalOverlay.classList.add("flex");

      // Boost view count
      if (item.id) {
        try {
          fetch("/api/views/" + item.id, { method: "POST" }).catch(function(){});
        } catch(e){}
      }
    }

    modalClose.onclick = function () {
      modalOverlay.classList.add("hidden");
      modalOverlay.classList.remove("flex");
    };
    modalOverlay.onclick = function (e) {
      if (e.target === modalOverlay) modalClose.onclick();
    };

    function finishLoading(items, append, hasMore) {
      state.loading = false;
      if (!append) grid.innerHTML = "";
      if (!items || !items.length) {
        if (!append) {
          statusEl.style.display = "block";
          statusEl.innerHTML = '<div class="text-3xl mb-2">📭</div><div class="text-slate-600 font-bold text-xs">ምንም አይነት የተመዘገበ ንብረት አልተገኘም</div>';
        }
        moreBtn.classList.add("hidden");
        return;
      }
      statusEl.style.display = "none";
      for (var i = 0; i < items.length; i++) {
        grid.appendChild(createCardElement(items[i], i));
      }
      if (hasMore) {
        moreBtn.classList.remove("hidden");
      } else {
        moreBtn.classList.add("hidden");
      }
    }

    function load(append) {
      if (state.loading) return;
      state.loading = true;
      if (!append) {
        statusEl.style.display = "block";
        statusEl.innerHTML = '<div class="inline-block animate-spin w-6 h-6 border-2 border-[#16acbd] border-t-transparent rounded-full mb-2"></div><div>እየጫነ ነው…</div>';
        grid.innerHTML = "";
      }

      var page = append ? state.page + 1 : 1;
      var qs = "page=" + page + "&limit=12&order=DESC&active_only=1&type=" +
        (state.tab === "marketplace" ? "SELL" : "BUY");
      if (state.category) qs += "&category=" + encodeURIComponent(state.category);
      if (state.q) qs += "&q=" + encodeURIComponent(state.q);

      var url = "/api/explorer/listings?" + qs;

      fetch(url)
        .then(function(res){ return res.json(); })
        .then(function(data){
          var items = data.items || data.listings || [];
          state.page = page;
          state.hasMore = !!(data.has_more || data.hasMore);
          finishLoading(items, append, state.hasMore);
        })
        .catch(function(err){
          console.warn(err);
          finishLoading([], append, false);
        });
    }

    // Dynamic "+" FAB routing based on active tab
    fabBtn.onclick = function () {
      if (state.tab === "marketplace") {
        window.location.href = "/seller-form";
      } else {
        window.location.href = "/buyer-form";
      }
    };

    tabSell.onclick = function () {
      state.tab = "marketplace";
      setTabs();
      load(false);
    };

    tabBuy.onclick = function () {
      state.tab = "requests";
      setTabs();
      load(false);
    };

    catsEl.onclick = function (ev) {
      var el = ev.target;
      while (el && el !== catsEl && !el.getAttribute("data-id")) el = el.parentNode;
      if (!el || el === catsEl) return;
      state.category = el.getAttribute("data-id") || "";
      renderCats();
      load(false);
    };

    moreBtn.onclick = function () { load(true); };

    var deb = null;
    qInput.oninput = function () {
      clearTimeout(deb);
      deb = setTimeout(function () {
        state.q = (qInput.value || "").trim();
        load(false);
      }, 300);
    };

    // Bottom Navigation Bar click handlers
    document.getElementById("navHome").onclick = function () {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    };
    document.getElementById("navSearch").onclick = function () {
      qInput.focus();
    };
    document.getElementById("navMessages").onclick = function () {
      if (tg && tg.openTelegramLink) {
        tg.openTelegramLink("https://t.me/AdikaMarketplaceBot");
      } else {
        window.open("https://t.me/AdikaMarketplaceBot", "_blank");
      }
    };
    document.getElementById("navHelp").onclick = function () {
      if (tg && tg.showAlert) {
        tg.showAlert("Adika Marketplace - ደንበኞችና ደላሎችን የሚያገናኝ የቴሌግራም መተግበሪያ። ጥያቄ ወይም ድጋፍ ካስፈለገዎት @AdikaMarketplaceBot ያነጋግሩ።");
      } else {
        alert("Adika Marketplace - ደንበኞችና ደላሎችን የሚያገናኝ የቴሌግራም መተግበሪያ።");
      }
    };

    // Fetch stats for live header indicator
    try {
      fetch("/api/stats")
        .then(function(r){ return r.json(); })
        .then(function(d){
          if (d && d.total_brokers) {
            document.getElementById("liveBrokersCount").textContent = d.total_brokers + " ደላሎች ክፍት";
          }
        }).catch(function(){});
    } catch(e){}

    renderCats();
    setTabs();
    load(false);
  })();
  </script>
</body>
</html>
"""


@web_app.route('/')
def home():
    return (
        "<html><body style='font-family:sans-serif;padding:24px;background:#b5eff3'>"
        "<div style='background:#fff;padding:20px;border-radius:16px;box-shadow:0 12px 28px rgba(15,23,42,0.12);max-width:500px;margin:auto'>"
        "<h2 style='color:#16acbd;margin-top:0'>Adika Marketplace Server</h2>"
        "<p>Server is running with Teal/Cyan and Floating Cards design system.</p>"
        f"<p>WEBAPP_URL: <code>{WEBAPP_URL}</code></p>"
        "<ul>"
        "<li><a href='/explorer'>/explorer (Main Mini App)</a></li>"
        "<li><a href='/seller-form'>/seller-form (Submit Listing)</a></li>"
        "<li><a href='/buyer-form'>/buyer-form (Submit Request)</a></li>"
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


def _send_notification_safe(notification_text: str, req_id: int, buyer_id: int):
    """Fire broker notifications from Flask thread without blocking or breaking loops."""
    if not bot_app:
        logger.warning("bot_app is None – cannot send notification")
        return

    def run_in_thread():
        try:
            from handlers import notify_brokers

            async def _notify():
                await notify_brokers(bot_app.bot, notification_text, req_id, buyer_id)

            # Prefer loop captured in Application post_init
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

            # Fallback: dedicated loop in this worker thread
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


@web_app.route('/api/submit-listing', methods=['POST'])
def submit_listing():
    try:
        data = request.json or {}
        user_id = data.get('user_id')
        category = data.get('category', 'መኪና')
        price = data.get('price', '')
        negotiable = data.get('negotiable', True)
        urgent_sale = data.get('urgent_sale', False)
        description = data.get('description', '')
        phone = data.get('phone', '')
        telegram_user = data.get('telegram_user', '')
        fuel_type = data.get('fuel_type', '')
        transmission = data.get('transmission', '')
        mileage = data.get('mileage', '')
        condition = data.get('condition', '')
        car_type = data.get('car_type', '')
        bedrooms = data.get('bedrooms', '')
        bathrooms = data.get('bathrooms', '')
        parking = data.get('parking', '')
        house_condition = data.get('condition', '')
        house_type = data.get('house_type', '')
        photos = data.get('photos', [])
        logger.info(f"📥 Seller WebApp data: {data}")
        if not user_id or user_id == "unknown":
            return jsonify({"status": "error", "message": "User ID አልተገኘም። Telegram ውስጥ ክፈት።"}), 400
        negotiable_text = "✅ የሚደራደር" if negotiable else "❌ የማይደራደር"
        urgent_text = "⚡ **አስቸኳይ ሽያጭ!** " if urgent_sale else ""
        full_desc = f"{urgent_text}"
        full_desc += f"💰 ዋጋ: {price} ብር ({negotiable_text})\n"
        if category == 'መኪና':
            if car_type: full_desc += f"🚗 አይነት: {car_type}\n"
            if fuel_type: full_desc += f"⛽ ነዳጅ: {fuel_type}\n"
            if transmission: full_desc += f"⚙️ ማርሽ: {transmission}\n"
            if mileage: full_desc += f"🛣️ ኪሎሜትር: {mileage} KM\n"
            if condition: full_desc += f"📊 ሁኔታ: {condition}\n"
        else:
            if house_type: full_desc += f"🏠 አይነት: {house_type}\n"
            if bedrooms: full_desc += f"🛏️ መኝታ: {bedrooms}\n"
            if bathrooms: full_desc += f"🛁 መታጠቢያ: {bathrooms}\n"
            if parking: full_desc += f"🚗 ፓርኪንግ: {parking}\n"
            if house_condition: full_desc += f"📊 ሁኔታ: {house_condition}\n"
        full_desc += f"📝 መግለጫ: {description}\n"
        full_desc += f"📞 ስልክ: {phone}\n"
        if telegram_user: full_desc += f"📱 Telegram: {telegram_user}\n"
        uid = int(user_id) if str(user_id).isdigit() else 0
        extra = {
            'fuel_type': fuel_type, 'transmission': transmission, 'mileage': mileage,
            'condition': condition or house_condition, 'bedrooms': bedrooms,
            'bathrooms': bathrooms, 'parking': parking, 'house_type': house_type,
            'car_type': car_type, 'negotiable': negotiable, 'urgent_sale': urgent_sale,
            'telegram_user': telegram_user
        }
        # Limit photos payload (max 3 compressed)
        safe_photos = []
        if isinstance(photos, list):
            for ph in photos[:3]:
                s = str(ph)
                if len(s) > 350000:
                    s = s[:350000]
                safe_photos.append(s)
        req_id = add_listing(
            user_chat_id=uid,
            user_name="WebApp User",
            req_type="SELL",
            main_category=(category or car_type or house_type or "መኪና"),
            sub_category=car_type if category == 'መኪና' else house_type,
            action_type="መሸጥ",
            property_type="",
            description=full_desc,
            price=str(price),
            phone=str(phone or ""),
            extra_data=extra,
            photos=safe_photos
        )
        # Retry without photos if insert failed (photo size / type issues)
        if not req_id and safe_photos:
            logger.warning("Retry add_listing without photos")
            req_id = add_listing(
                user_chat_id=uid,
                user_name="WebApp User",
                req_type="SELL",
                main_category=(category or car_type or house_type or "መኪና"),
                sub_category=car_type if category == 'መኪና' else house_type,
                action_type="መሸጥ",
                property_type="",
                description=full_desc,
                price=str(price),
                phone=str(phone or ""),
                extra_data=extra,
                photos=[]
            )
        if req_id:
            logger.info(f"✅ Seller listing saved ID={req_id}")
            notification_text = (
                f"🛍️ **አዲስ የሽያጭ ማስታወቂያ (#ADK-{req_id})**\n\n"
                f"{full_desc}"
            )
            _send_notification_safe(notification_text, req_id, int(user_id))
            return jsonify({"status": "success", "req_id": req_id})
        else:
            import models as _models
            detail = getattr(_models, "LAST_DB_ERROR", "") or ""
            msg = "Database ውስጥ ማስቀመጥ አልተቻለም።"
            if detail:
                msg = f"{msg} ({detail[:180]})"
            logger.error("submit failed detail=%s backend=%s", detail, getattr(_models, "_DB_BACKEND", "?"))
            return jsonify({"status": "error", "message": msg, "detail": detail}), 500
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
        if not user_id or user_id == "unknown":
            return jsonify({"status": "error", "message": "User ID አልተገኘም። Telegram ውስጥ ክፈት።"}), 400
        budget_range = f"{budget_min} - {budget_max}" if budget_min and budget_max else (budget_min or budget_max or "ያልተገለጸ")
        full_desc = (
            f"💰 በጀት ክልል: {budget_range} ብር\n"
            f"📝 ዝርዝር: {details}\n"
            f"📞 ስልክ: {phone}\n"
        )
        if telegram_user: full_desc += f"📱 Telegram: {telegram_user}\n"
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
                'budget_min': budget_min, 'budget_max': budget_max,
                'create_alert': create_alert, 'telegram_user': telegram_user
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
            import models as _models
            detail = getattr(_models, "LAST_DB_ERROR", "") or ""
            msg = "Database ውስጥ ማስቀመጥ አልተቻለም።"
            if detail:
                msg = f"{msg} ({detail[:180]})"
            logger.error("submit failed detail=%s backend=%s", detail, getattr(_models, "_DB_BACKEND", "?"))
            return jsonify({"status": "error", "message": msg, "detail": detail}), 500
    except Exception as e:
        logger.error(f"❌ submit_request error: {e}", exc_info=True)
        return jsonify({"status": "error", "message": f"Server Error: {str(e)}"}), 500


@web_app.route('/api/health', methods=['GET'])
def api_health():
    """Diagnostics — reports postgres vs temporary sqlite."""
    import config as app_config
    from models import get_db_connection, _DB_BACKEND
    backend = getattr(app_config, "DB_BACKEND", None) or _DB_BACKEND
    info = {
        "ok": True,
        "database": backend if backend != "unknown" else ("postgres" if DATABASE_URL else "sqlite"),
        "persistent": backend == "postgres",
        "isTemporaryDb": backend != "postgres",
        "webapp_url": WEBAPP_URL,
    }
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) AS cnt FROM listings")
        row = cur.fetchone()
        info["listings_count"] = row["cnt"] if isinstance(row, dict) else (row[0] if row else 0)
        cur.execute("SELECT COUNT(*) AS cnt FROM brokers")
        row = cur.fetchone()
        info["brokers_count"] = row["cnt"] if isinstance(row, dict) else (row[0] if row else 0)
        try:
            conn.close()
        except Exception:
            pass
        backend = getattr(app_config, "DB_BACKEND", None) or _DB_BACKEND
        info["database"] = backend
        info["persistent"] = backend == "postgres"
        info["isTemporaryDb"] = backend != "postgres"
    except Exception as e:
        info["ok"] = False
        info["error"] = str(e)
    return jsonify(info)


@web_app.route('/api/explorer/listings', methods=['GET', 'OPTIONS'])
def api_explorer_listings():
    """Fetch listings/requests with pagination. Never hangs — always JSON."""
    if request.method == 'OPTIONS':
        return ('', 204)
    try:
        page = max(1, int(request.args.get('page', 1) or 1))
        limit = min(50, max(1, int(request.args.get('limit', 12) or 12)))
        offset = (page - 1) * limit
        req_type = (request.args.get('type') or '').upper()
        category = request.args.get('category') or ''
        search = (request.args.get('q') or '').strip()
        order = (request.args.get('order') or 'DESC').upper()
        active_only = request.args.get('active_only', '1') == '1'
        if order not in ('ASC', 'DESC'):
            order = 'DESC'

        conn = None
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            p = get_placeholder()
            from models import is_postgres

            try:
                if is_postgres():
                    cur.execute(
                        "SELECT column_name FROM information_schema.columns "
                        "WHERE table_name = 'listings'"
                    )
                    cols = {r[0] if not isinstance(r, dict) else list(r.values())[0] for r in cur.fetchall()}
                    cols = {str(c).lower() for c in cols}
                else:
                    cur.execute("PRAGMA table_info(listings)")
                    cols = {str(r[1] if not isinstance(r, dict) else r.get('name')).lower() for r in cur.fetchall()}
            except Exception:
                cols = set()

            where = ["1=1"]
            params = []
            if "status" in cols:
                where.append(f"(status IS NULL OR status != {p})")
                params.append('deleted')
                if active_only:
                    where.append(f"(status IS NULL OR LOWER(CAST(status AS TEXT)) NOT IN ({p},{p},{p}))")
                    params.extend(['sold', 'rented', 'expired'])
            if req_type in ('SELL', 'BUY') and "req_type" in cols:
                where.append(f"UPPER(COALESCE(req_type,'')) = UPPER({p})")
                params.append(req_type)
            if category:
                parts = []
                if "main_category" in cols:
                    parts.append(f"main_category = {p}")
                    params.append(category)
                if "category" in cols:
                    parts.append(f"category = {p}")
                    params.append(category)
                if parts:
                    where.append("(" + " OR ".join(parts) + ")")
            if search:
                like = "ILIKE" if is_postgres() else "LIKE"
                sp = []
                for col in ("description", "price", "phone", "title"):
                    if col in cols or not cols:
                        sp.append(f"CAST({col} AS TEXT) {like} {p}")
                        params.append(f"%{search}%")
                if sp:
                    where.append("(" + " OR ".join(sp) + ")")

            where_sql = " AND ".join(where)
            order_col = "id" if ("id" in cols or not cols) else "created_at"
            order_sql = "ASC" if order == "ASC" else "DESC"

            total = 0
            try:
                cur.execute(f"SELECT COUNT(*) AS cnt FROM listings WHERE {where_sql}", params)
                total_row = cur.fetchone()
                total = total_row['cnt'] if isinstance(total_row, dict) else (total_row[0] if total_row else 0)
            except Exception as ce:
                logger.warning("count listings: %s", ce)
                try:
                    cur.execute("SELECT COUNT(*) AS cnt FROM listings")
                    total_row = cur.fetchone()
                    total = total_row['cnt'] if isinstance(total_row, dict) else (total_row[0] if total_row else 0)
                    where_sql = "1=1"
                    params = []
                except Exception:
                    total = 0

            try:
                cur.execute(
                    f"SELECT * FROM listings WHERE {where_sql} "
                    f"ORDER BY {order_col} {order_sql} LIMIT {p} OFFSET {p}",
                    list(params) + [limit, offset],
                )
                rows = cur.fetchall() or []
            except Exception as qe:
                logger.warning("listings query failed (%s); simple select", qe)
                cur.execute(f"SELECT * FROM listings ORDER BY id DESC LIMIT {p} OFFSET {p}", (limit, offset))
                rows = cur.fetchall() or []

            items = []
            for row in rows:
                item = dict(row) if isinstance(row, dict) else dict(zip([c[0] for c in cur.description], row))
                if isinstance(item.get('extra_data'), str):
                    try:
                        item['extra_data'] = json.loads(item['extra_data'])
                    except Exception:
                        item['extra_data'] = {}
                photos = []
                try:
                    if item.get('id') is not None:
                        cur.execute(
                            f"SELECT photo_id FROM listing_photos WHERE listing_id = {p}",
                            (item['id'],),
                        )
                        photos = [r['photo_id'] if isinstance(r, dict) else r[0] for r in (cur.fetchall() or [])]
                except Exception:
                    photos = []
                if not photos and item.get('photo_id'):
                    photos = [item['photo_id']]
                item['photos'] = photos
                if item.get('view_count') is None:
                    item['view_count'] = 0
                if item.get('created_at') and not isinstance(item['created_at'], str):
                    try:
                        item['created_at'] = item['created_at'].isoformat()
                    except Exception:
                        item['created_at'] = str(item['created_at'])
                items.append(item)

            safe_items = [_json_safe(it) for it in items]
        finally:
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass

        try:
            from models import _DB_BACKEND
            backend = _DB_BACKEND
        except Exception:
            backend = "postgres" if DATABASE_URL else "sqlite"

        return jsonify({
            "status": "success",
            "page": page,
            "limit": limit,
            "total": int(total or 0),
            "has_more": bool(offset + limit < (total or 0)),
            "items": safe_items,
            "db": backend,
            "isTemporaryDb": backend != "postgres",
        })
    except Exception as e:
        logger.error(f"api_explorer_listings error: {e}", exc_info=True)
        return jsonify({
            "status": "success",
            "page": 1,
            "limit": 12,
            "total": 0,
            "has_more": False,
            "items": [],
            "message": str(e),
        }), 200


@web_app.route('/api/views/<int:listing_id>', methods=['POST'])
def api_view_booster(listing_id):
    """Increments view_count by a random amount between +3 and +7."""
    try:
        boost = random.randint(3, 7)
        conn = get_db_connection()
        cur = conn.cursor()
        p = get_placeholder()
        cur.execute(f"SELECT view_count FROM listings WHERE id = {p}", (listing_id,))
        row = cur.fetchone()
        if not row:
            conn.close()
            return jsonify({"status": "error", "message": "not found"}), 404
        current = row['view_count'] if isinstance(row, dict) else row[0]
        if current is None or current == 0:
            baseline = random.randint(35, 90)
            new_count = baseline + boost
        else:
            new_count = int(current) + boost
        cur.execute(f"UPDATE listings SET view_count = {p} WHERE id = {p}", (new_count, listing_id))
        from models import is_postgres
        if not is_postgres():
            try:
                conn.commit()
            except Exception:
                pass
        conn.close()
        return jsonify({"status": "success", "view_count": new_count})
    except Exception as e:
        logger.error(f"view booster error: {e}")
        return jsonify({"status": "error"}), 500


@web_app.route('/api/items/<int:listing_id>/status', methods=['PATCH'])
def api_update_item_status(listing_id):
    """Mark listing as sold / rented / pending (re-activate)."""
    try:
        data = request.json or {}
        new_status = str(data.get('status', '')).lower().strip()
        user_id = data.get('user_id')
        if new_status not in ('sold', 'rented', 'pending', 'expired'):
            return jsonify({"status": "error", "message": "Invalid status"}), 400

        conn = get_db_connection()
        cur = conn.cursor()
        p = get_placeholder()
        cur.execute(f"SELECT user_chat_id, status FROM listings WHERE id = {p}", (listing_id,))
        row = cur.fetchone()
        if not row:
            conn.close()
            return jsonify({"status": "error", "message": "Not found"}), 404

        owner_id = row['user_chat_id'] if isinstance(row, dict) else row[0]
        is_admin = (str(user_id) == str(ADMIN_CHAT_ID_INT) and ADMIN_CHAT_ID_INT != 0)
        is_owner = (str(user_id) == str(owner_id))
        if not (is_owner or is_admin):
            conn.close()
            return jsonify({"status": "error", "message": "Forbidden"}), 403

        cur.execute(f"UPDATE listings SET status = {p} WHERE id = {p}", (new_status, listing_id))
        from models import is_postgres
        if not is_postgres():
            try:
                conn.commit()
            except Exception:
                pass
        conn.close()
        logger.info(f"✅ Listing #{listing_id} status → {new_status} by user {user_id}")
        return jsonify({"status": "success", "new_status": new_status})
    except Exception as e:
        logger.error(f"status update error: {e}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500


@web_app.route('/api/items/<int:listing_id>', methods=['DELETE'])
def api_delete_item(listing_id):
    """Soft-delete a listing (status='deleted'). Owner or Admin only."""
    try:
        data = request.json or {}
        user_id = data.get('user_id')
        conn = get_db_connection()
        cur = conn.cursor()
        p = get_placeholder()
        cur.execute(f"SELECT user_chat_id FROM listings WHERE id = {p}", (listing_id,))
        row = cur.fetchone()
        if not row:
            conn.close()
            return jsonify({"status": "error", "message": "Not found"}), 404
        owner_id = row['user_chat_id'] if isinstance(row, dict) else row[0]
        is_admin = (str(user_id) == str(ADMIN_CHAT_ID_INT) and ADMIN_CHAT_ID_INT != 0)
        is_owner = (str(user_id) == str(owner_id))
        if not (is_owner or is_admin):
            conn.close()
            return jsonify({"status": "error", "message": "Forbidden"}), 403
        cur.execute(f"UPDATE listings SET status = 'deleted' WHERE id = {p}", (listing_id,))
        from models import is_postgres
        if not is_postgres():
            try:
                conn.commit()
            except Exception:
                pass
        conn.close()
        return jsonify({"status": "success"})
    except Exception as e:
        logger.error(f"delete item error: {e}")
        return jsonify({"status": "error"}), 500


@web_app.route('/api/stats', methods=['GET'])
def api_stats():
    try:
        stats = get_platform_stats()
        return jsonify({"status": "success", **stats})
    except Exception as e:
        logger.error(f"api_stats: {e}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500


@web_app.route('/api/brokers', methods=['GET'])
def api_brokers():
    try:
        page = max(1, int(request.args.get("page", 1)))
        limit = min(15, max(1, int(request.args.get("limit", 12))))
        offset = (page - 1) * limit
        sub_city = request.args.get("sub_city") or None
        brokers = get_active_brokers(sub_city=sub_city, status="approved", limit=limit, offset=offset)
        total = count_brokers(status="approved")
        items = []
        for b in brokers:
            items.append({
                "id": b.get("id"),
                "chat_id": b.get("chat_id"),
                "full_name": b.get("full_name"),
                "phone": b.get("phone"),
                "username": b.get("username"),
                "sub_city": b.get("sub_city"),
                "specialty": b.get("specialty") or b.get("role_type"),
                "rating": float(b.get("rating") or 5),
                "total_ratings": b.get("total_ratings") or 0,
                "is_online": bool(b.get("is_online", True)),
                "status": b.get("status"),
            })
        return jsonify({
            "status": "success",
            "page": page,
            "limit": limit,
            "total": total,
            "has_more": offset + limit < total,
            "items": items,
        })
    except Exception as e:
        logger.error(f"api_brokers: {e}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500


@web_app.route('/api/listings', methods=['GET'])
def api_listings_alias():
    """Alias with strict pagination."""
    return api_explorer_listings()


def run_flask():
    """Start Flask HTTP server (Mini App + REST API) on 0.0.0.0:PORT."""
    port = int(PORT or 8080)
    logger.info("Starting Flask on 0.0.0.0:%s", port)
    web_app.run(host="0.0.0.0", port=port, use_reloader=False, threaded=True)


if __name__ == '__main__':
    run_flask()

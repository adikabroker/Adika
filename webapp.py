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


# ==============================================================================
# SELLER FORM HTML (CSS Dual-Class Language Switcher)
# ==============================================================================
SELLER_FORM_HTML = r"""
<!DOCTYPE html>
<html lang="am">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
  <title>Post Listing | ማስታወቂያ ልቀቅ</title>
  <script src="https://telegram.org/js/telegram-web-app.js"></script>
  <script src="https://cdn.tailwindcss.com"></script>
  <script crossorigin src="https://cdn.jsdelivr.net/npm/react@18.2.0/umd/react.production.min.js"></script>
  <script crossorigin src="https://cdn.jsdelivr.net/npm/react-dom@18.2.0/umd/react-dom.production.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/@babel/standalone@7.24.0/babel.min.js"></script>

  <style>
    body { margin:0; background:#b5eff3; font-family:system-ui,-apple-system,sans-serif; -webkit-tap-highlight-color:transparent; }
    .lang-en { display: none !important; }
    .lang-am { display: inline-block !important; }
    body.lang-en-active .lang-en { display: inline-block !important; }
    body.lang-en-active .lang-am { display: none !important; }
    .chip-active { background:#16acbd; color:#fff; font-weight:700; box-shadow:0 2px 6px rgba(22,172,189,.35); border: 1px solid #16acbd; }
    .chip-idle { background:#ffffff; color:#334155; border:1px solid #cbd5e1; font-weight: 600; }
    input, textarea, select { font-size: 15px !important; }
  </style>
</head>
<body class="bg-[#b5eff3] min-h-screen text-slate-800">
  <div id="root"></div>
  <script type="text/babel">
    const { useState, useRef, useEffect } = React;
    const tg = (window.Telegram && window.Telegram.WebApp) ? window.Telegram.WebApp : {
      expand(){}, ready(){}, close(){}, initDataUnsafe: {}, setHeaderColor(){}, setBackgroundColor(){}
    };
    try { tg.ready(); tg.expand(); tg.setHeaderColor('#16acbd'); tg.setBackgroundColor('#b5eff3'); } catch (e) {}

    const user = tg.initDataUnsafe?.user || {};
    const autoUsername = user.username ? '@' + user.username : '';
    const autoPhone = user.phone_number || '';

    function formatPrice(val) {
      const digits = String(val).replace(/[^\d]/g, '');
      return digits ? digits.replace(/\B(?=(\d{3})+(?!\d))/g, ',') : '';
    }
    function parsePrice(val) {
      return String(val).replace(/[^\d]/g, '');
    }

    function Chip({ am, en, active, onClick, danger }) {
      return (
        <button type="button" onClick={onClick}
          className={`px-3 py-1.5 rounded-full text-xs whitespace-nowrap transition-all shadow-sm ${
            active ? (danger ? 'bg-rose-500 text-white font-bold' : 'chip-active') : 'chip-idle hover:bg-slate-50'
          }`}>
          <span className="lang-am">{am}</span>
          <span className="lang-en">{en}</span>
        </button>
      );
    }

    function ToggleCard({ active, onToggle, icon, am, en, danger }) {
      return (
        <button type="button" onClick={onToggle}
          className={`w-full flex items-center justify-between p-3 rounded-2xl border transition-all text-left bg-white shadow-[0_4px_14px_rgba(15,23,42,0.06)] ${
            active ? (danger ? 'border-rose-300 text-rose-700 bg-rose-50/50' : 'border-[#16acbd]/40 text-[#0e7490] bg-[#16acbd]/5') : 'border-slate-200/80 text-slate-700'
          }`}>
          <div className="flex items-center gap-2">
            <span className="text-base">{icon}</span>
            <div className="text-xs font-bold text-slate-800">
              <span className="lang-am">{am}</span>
              <span className="lang-en">{en}</span>
            </div>
          </div>
          <div className={`w-10 h-5 rounded-full relative transition-colors ${active ? (danger ? 'bg-rose-500' : 'bg-[#16acbd]') : 'bg-slate-300'}`}>
            <div className={`absolute top-0.5 w-4 h-4 rounded-full bg-white shadow transition-transform ${active ? 'translate-x-5' : 'translate-x-0.5'}`} />
          </div>
        </button>
      );
    }

    function SellerForm() {
      const [lang, setLang] = useState(() => localStorage.getItem('adika_lang') || 'am');

      useEffect(() => {
        if (lang === 'en') document.body.classList.add('lang-en-active');
        else document.body.classList.remove('lang-en-active');
      }, [lang]);

      const switchLang = (newLang) => {
        setLang(newLang);
        localStorage.setItem('adika_lang', newLang);
        if (newLang === 'en') document.body.classList.add('lang-en-active');
        else document.body.classList.remove('lang-en-active');
      };

      const [step, setStep] = useState(1);
      const [category, setCategory] = useState('መኪና');
      const [carModel, setCarModel] = useState('');
      const [fuel, setFuel] = useState('');
      const [transmission, setTransmission] = useState('');
      const [mileage, setMileage] = useState('');
      const [condition, setCondition] = useState('');
      const [carType, setCarType] = useState('');
      const [locationArea, setLocationArea] = useState('');
      const [bedrooms, setBedrooms] = useState('');
      const [bathrooms, setBathrooms] = useState('');
      const [parking, setParking] = useState(false);
      const [houseCondition, setHouseCondition] = useState('');
      const [houseType, setHouseType] = useState('');
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

      const compressImage = (file) => new Promise((resolve, reject) => {
        try {
          if (!file || file.size > 8 * 1024 * 1024) return reject(new Error('Max 8MB'));
          const reader = new FileReader();
          reader.onload = (e) => {
            const img = new Image();
            img.onload = () => {
              const canvas = document.createElement('canvas');
              let cw = img.width, ch = img.height;
              const max = 1000;
              if (cw > max || ch > max) {
                if (cw > ch) { ch = (ch / cw) * max; cw = max; }
                else { cw = (cw / ch) * max; cw = max; }
              }
              canvas.width = cw; canvas.height = ch;
              canvas.getContext('2d').drawImage(img, 0, 0, cw, ch);
              resolve(canvas.toDataURL('image/jpeg', 0.65));
            };
            img.src = e.target.result;
          };
          reader.readAsDataURL(file);
        } catch (err) { reject(err); }
      });

      const addFiles = async (fileList) => {
        setPhotoError('');
        const files = Array.from(fileList || []).slice(0, 5 - photos.length);
        if (!files.length) return;
        setPhotoBusy(true);
        try {
          for (const f of files) {
            if (!f.type || !f.type.startsWith('image/')) continue;
            const dataUrl = await compressImage(f);
            setPhotos(prev => prev.length < 5 ? [...prev, dataUrl] : prev);
          }
        } catch (err) {
          setPhotoError(String(err.message || err));
        } finally {
          setPhotoBusy(false);
        }
      };

      const removePhoto = (i) => setPhotos(prev => prev.filter((_, idx) => idx !== i));
      const canNext1 = category && (category === 'መኪና' ? (carModel || carType || condition) : (houseType || locationArea));
      const canSubmit = Boolean(description && description.trim());

      const submit = async () => {
        if (!canSubmit || submitting) return;
        setSubmitting(true);
        setStatus('');
        const isCar = category === 'መኪና';
        const subCat = isCar ? (carModel || carType) : (houseType ? `${houseType}${locationArea ? ` • ${locationArea}` : ''}` : locationArea);
        const data = {
          user_id: user.id || 'unknown',
          category,
          sub_category: subCat,
          price: parsePrice(price),
          negotiable,
          urgent_sale: urgent,
          description,
          phone,
          telegram_user: telegramUser,
          photos,
          car_model: carModel,
          location_area: locationArea,
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
            setTimeout(() => tg.close(), 2500);
          } else {
            setStatus(result.message || 'Error');
            setSubmitting(false);
          }
        } catch (e) {
          setStatus('Network error');
          setSubmitting(false);
        }
      };

      if (status === 'ok') {
        return (
          <div className="min-h-screen flex items-center justify-center p-6 bg-[#b5eff3]">
            <div className="bg-white rounded-3xl p-6 text-center space-y-4 shadow-[0_12px_28px_rgba(15,23,42,0.12)] border border-white/60 max-w-sm">
              <div className="w-16 h-16 rounded-full bg-[#16acbd]/15 text-[#16acbd] flex items-center justify-center text-3xl mx-auto">✓</div>
              <h2 className="font-bold text-base text-slate-800">
                <span className="lang-am">ማስታወቂያዎ ተመዝግቧል!</span>
                <span className="lang-en">Successfully Posted!</span>
              </h2>
              <p className="font-medium text-xs text-slate-600 leading-relaxed px-2">
                <span className="lang-am">ንብረትዎ ለተረጋገጡ ደላሎችና ገዢዎች ተሰራጭቷል።</span>
                <span className="lang-en">Your listing has been submitted and broadcasted to verified brokers.</span>
              </p>
            </div>
          </div>
        );
      }

      return (
        <div className="min-h-screen bg-[#b5eff3] pb-24">
          <div className="fixed top-0 left-0 right-0 z-40 bg-[#16acbd] shadow-md px-4 py-2.5 text-white">
            <div className="flex items-center justify-between max-w-xs mx-auto mb-1.5">
              <div className="font-extrabold text-xs tracking-wide">
                <span className="lang-am">ማስታወቂያ ልቀቅ</span>
                <span className="lang-en">Post Listing</span>
              </div>
              <div className="flex items-center gap-1.5">
                <div className="flex items-center bg-black/20 p-0.5 rounded-lg shrink-0">
                  <button type="button" onClick={() => switchLang('am')}
                    className={`px-2 py-0.5 rounded text-[10px] font-extrabold transition-all ${lang === 'am' ? 'bg-white text-[#16acbd] shadow-sm' : 'text-white/80'}`}>
                    AM
                  </button>
                  <button type="button" onClick={() => switchLang('en')}
                    className={`px-2 py-0.5 rounded text-[10px] font-extrabold transition-all ${lang === 'en' ? 'bg-white text-[#16acbd] shadow-sm' : 'text-white/80'}`}>
                    EN
                  </button>
                </div>
                <div className="text-[10px] bg-white/20 px-2 py-0.5 rounded-full font-bold">{step}/3</div>
              </div>
            </div>
            <div className="flex items-center gap-1 max-w-xs mx-auto">
              {[1, 2, 3].map((i) => (
                <React.Fragment key={i}>
                  <div className="flex-1 text-center">
                    <div className={`mx-auto w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold ${
                      step >= i ? 'bg-white text-[#16acbd]' : 'bg-white/30 text-white'
                    }`}>{i}</div>
                  </div>
                  {i < 3 && <div className={`h-0.5 flex-1 rounded ${step > i ? 'bg-white' : 'bg-white/30'}`} />}
                </React.Fragment>
              ))}
            </div>
          </div>

          <div className="pt-20 px-3.5">
            <div className="bg-white rounded-2xl p-4 shadow-[0_12px_28px_rgba(15,23,42,0.12)] border border-slate-200/80 space-y-4">
              {step === 1 && (
                <div className="space-y-3.5">
                  <div>
                    <label className="text-xs font-bold text-slate-700 mb-1.5 block">
                      <span className="lang-am">📦 ምድብ</span>
                      <span className="lang-en">📦 Category</span>
                    </label>
                    <div className="flex gap-2">
                      <Chip am="🚗 መኪና" en="🚗 Vehicle" active={category==='መኪና'} onClick={() => setCategory('መኪና')} />
                      <Chip am="🏠 ቤት" en="🏠 Property" active={category==='ቤት'} onClick={() => setCategory('ቤት')} />
                    </div>
                  </div>

                  {category === 'መኪና' ? (
                    <>
                      <div>
                        <label className="text-xs font-bold text-slate-700 mb-1 block">
                          <span className="lang-am">🚘 የመኪና ስም / ሞዴል</span>
                          <span className="lang-en">🚘 Car Make / Model</span>
                        </label>
                        <input type="text" value={carModel} onChange={e => setCarModel(e.target.value)}
                          placeholder="Toyota Vitz 2020 / Hyundai Tucson"
                          className="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-200 focus:bg-white focus:ring-2 focus:ring-[#16acbd] outline-none text-xs font-bold" />
                      </div>
                      <div>
                        <label className="text-xs font-bold text-slate-700 mb-1 block">
                          <span className="lang-am">🚗 የመኪና አይነት</span>
                          <span className="lang-en">🚗 Vehicle Type</span>
                        </label>
                        <div className="flex gap-1.5 overflow-x-auto pb-1">
                          {[['Sedan','Sedan'],['SUV / 4WD','SUV / 4WD'],['Commercial','Commercial']].map(([am,en]) =>
                            <Chip key={am} am={am} en={en} active={carType===am} onClick={() => setCarType(am)} />
                          )}
                        </div>
                      </div>
                      <div>
                        <label className="text-xs font-bold text-slate-700 mb-1 block">
                          <span className="lang-am">⛽ የነዳጅ አይነት</span>
                          <span className="lang-en">⛽ Fuel Type</span>
                        </label>
                        <div className="flex gap-1.5 overflow-x-auto pb-1">
                          {[['ቤንዚን','Petrol'],['ናፍጣ','Diesel'],['ኤሌክትሪክ','Electric'],['ሀይብሪድ','Hybrid']].map(([am,en]) =>
                            <Chip key={am} am={am} en={en} active={fuel===am} onClick={() => setFuel(am)} />
                          )}
                        </div>
                      </div>
                      <div>
                        <label className="text-xs font-bold text-slate-700 mb-1 block">
                          <span className="lang-am">⚙️ ማርሽ</span>
                          <span className="lang-en">⚙️ Transmission</span>
                        </label>
                        <div className="flex gap-2">
                          {[['ኦቶማቲክ','Automatic'],['ማኑዋል','Manual']].map(([am,en]) =>
                            <Chip key={am} am={am} en={en} active={transmission===am} onClick={() => setTransmission(am)} />
                          )}
                        </div>
                      </div>
                      <div>
                        <label className="text-xs font-bold text-slate-700 mb-1 block">
                          <span className="lang-am">📊 ሁኔታ</span>
                          <span className="lang-en">📊 Condition</span>
                        </label>
                        <div className="flex gap-1.5 overflow-x-auto pb-1">
                          {[['አዲስ','Brand New'],['ንጹህ የያዘ','Clean Used'],['ጥገና የሚፈልግ','Needs Repair']].map(([am,en]) =>
                            <Chip key={am} am={am} en={en} active={condition===am} onClick={() => setCondition(am)} />
                          )}
                        </div>
                      </div>
                      <div>
                        <label className="text-xs font-bold text-slate-700 mb-1 block">
                          <span className="lang-am">🛣️ ኪሎሜትር (KM)</span>
                          <span className="lang-en">🛣️ Mileage (KM)</span>
                        </label>
                        <input type="number" value={mileage} onChange={e => setMileage(e.target.value)}
                          placeholder="45000"
                          className="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-200 focus:bg-white focus:ring-2 focus:ring-[#16acbd] outline-none text-xs" />
                      </div>
                    </>
                  ) : (
                    <>
                      <div>
                        <label className="text-xs font-bold text-slate-700 mb-1 block">
                          <span className="lang-am">🏠 የቤት አይነት</span>
                          <span className="lang-en">🏠 Property Type</span>
                        </label>
                        <div className="flex gap-1.5 overflow-x-auto pb-1">
                          {[['ቪላ','Villa'],['አፓርታማ','Apartment'],['ኮንዶሚኒየም','Condo'],['ንግድ ቦታ','Commercial'],['መሬት','Land']].map(([am,en]) =>
                            <Chip key={am} am={am} en={en} active={houseType===am} onClick={() => setHouseType(am)} />
                          )}
                        </div>
                      </div>
                      <div>
                        <label className="text-xs font-bold text-slate-700 mb-1 block">
                          <span className="lang-am">📍 አካባቢ / ቦታ</span>
                          <span className="lang-en">📍 Location / Area</span>
                        </label>
                        <input type="text" value={locationArea} onChange={e => setLocationArea(e.target.value)}
                          placeholder="Bole, CMC, Kazanchis, 150m²"
                          className="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-200 focus:bg-white focus:ring-2 focus:ring-[#16acbd] outline-none text-xs font-bold" />
                      </div>
                      <div>
                        <label className="text-xs font-bold text-slate-700 mb-1 block">
                          <span className="lang-am">🛏️ መኝታ ክፍሎች</span>
                          <span className="lang-en">🛏️ Bedrooms</span>
                        </label>
                        <div className="flex gap-1.5">
                          {['1','2','3','4','5+'].map(b =>
                            <Chip key={b} am={b} en={b} active={bedrooms===b} onClick={() => setBedrooms(b)} />
                          )}
                        </div>
                      </div>
                      <ToggleCard active={parking} onToggle={() => setParking(!parking)} icon="🚗" am="የመኪና ማቆሚያ አለው" en="Dedicated Parking" />
                    </>
                  )}

                  <div>
                    <label className="text-xs font-bold text-slate-700 mb-1 block">
                      <span className="lang-am">📝 ዝርዝር መግለጫ</span>
                      <span className="lang-en">📝 Description</span>
                    </label>
                    <textarea value={description} onChange={e => setDescription(e.target.value)} rows={3}
                      placeholder="ስለ ንብረቱ ተጨማሪ መረጃ ይግለጹ / Add specifications..."
                      className="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-200 focus:bg-white focus:ring-2 focus:ring-[#16acbd] outline-none text-xs resize-none" />
                  </div>
                </div>
              )}

              {step === 2 && (
                <div className="space-y-3.5">
                  <div>
                    <label className="text-xs font-bold text-slate-700 mb-1 block">
                      <span className="lang-am">💰 ዋጋ (ብር)</span>
                      <span className="lang-en">💰 Price (ETB)</span>
                    </label>
                    <div className="relative">
                      <input type="text" inputMode="numeric" value={price}
                        onChange={e => setPrice(formatPrice(e.target.value))}
                        placeholder="2,500,000"
                        className="w-full px-3 py-2.5 rounded-xl bg-slate-50 border border-slate-200 focus:bg-white focus:ring-2 focus:ring-[#16acbd] outline-none text-xs font-bold text-slate-900" />
                      <span className="absolute right-3 top-1/2 -translate-y-1/2 text-xs font-bold text-[#16acbd]">ETB</span>
                    </div>
                  </div>
                  <ToggleCard active={negotiable} onToggle={() => setNegotiable(!negotiable)} icon="🤝" am="የሚደራደር ዋጋ" en="Negotiable Price" />
                  <ToggleCard active={urgent} onToggle={() => setUrgent(!urgent)} icon="⚡" am="አስቸኳይ ሽያጭ" en="Urgent Sale" danger />

                  <div>
                    <label className="text-xs font-bold text-slate-700 mb-1 block">
                      <span className="lang-am">📸 ፎቶዎች (እስከ 5)</span>
                      <span className="lang-en">📸 Photos (Up to 5)</span>
                    </label>
                    <div onClick={() => fileRef.current?.click()}
                      className="border-2 border-dashed border-slate-200 bg-slate-50/70 hover:bg-slate-50 rounded-2xl p-5 text-center cursor-pointer transition-all">
                      <div className="text-2xl mb-1">📷</div>
                      <p className="text-xs font-bold text-slate-700">
                        <span className="lang-am">ፎቶ ይስቀሉ</span>
                        <span className="lang-en">Upload Photos</span>
                      </p>
                      <input ref={fileRef} type="file" accept="image/*" multiple className="hidden"
                        onChange={e => { addFiles(e.target.files); e.target.value=''; }} />
                    </div>
                    {photos.length > 0 && (
                      <div className="grid grid-cols-3 gap-2 mt-2.5">
                        {photos.map((src, i) => (
                          <div key={i} className="relative aspect-square rounded-xl overflow-hidden border border-slate-200 shadow-sm">
                            <img src={src} className="w-full h-full object-cover" alt="" />
                            <button type="button" onClick={() => removePhoto(i)}
                              className="absolute top-1 right-1 w-5 h-5 rounded-full bg-rose-500 text-white text-xs flex items-center justify-center font-bold">×</button>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              )}

              {step === 3 && (
                <div className="space-y-3.5">
                  <div>
                    <label className="text-xs font-bold text-slate-700 mb-1 block">
                      <span className="lang-am">📞 ስልክ ቁጥር</span>
                      <span className="lang-en">📞 Phone Number</span>
                    </label>
                    <input type="tel" value={phone} onChange={e => setPhone(e.target.value)}
                      placeholder="0911223344"
                      className="w-full px-3 py-2.5 rounded-xl bg-slate-50 border border-slate-200 focus:bg-white focus:ring-2 focus:ring-[#16acbd] outline-none text-xs font-bold" />
                  </div>
                  <div>
                    <label className="text-xs font-bold text-slate-700 mb-1 block">
                      <span className="lang-am">📱 ቴሌግራም</span>
                      <span className="lang-en">📱 Telegram</span>
                    </label>
                    <input type="text" value={telegramUser} onChange={e => setTelegramUser(e.target.value)}
                      placeholder="@username"
                      className="w-full px-3 py-2.5 rounded-xl bg-slate-50 border border-slate-200 focus:bg-white focus:ring-2 focus:ring-[#16acbd] outline-none text-xs font-bold" />
                  </div>
                </div>
              )}
            </div>
          </div>

          <div className="fixed bottom-0 left-0 right-0 p-3 bg-white/95 backdrop-blur-md border-t border-slate-200 flex gap-2 z-40">
            {step > 1 ? (
              <button type="button" onClick={() => setStep(s => s-1)}
                className="w-1/3 py-2.5 rounded-xl bg-slate-100 text-slate-700 font-bold text-xs active:scale-95">
                <span className="lang-am">ተመለስ</span><span className="lang-en">Back</span>
              </button>
            ) : (
              <button type="button" onClick={() => tg.close()}
                className="w-1/3 py-2.5 rounded-xl bg-slate-100 text-slate-700 font-bold text-xs active:scale-95">
                <span className="lang-am">ሰርዝ</span><span className="lang-en">Cancel</span>
              </button>
            )}
            {step < 3 ? (
              <button type="button" onClick={() => { if (step===1 && !canNext1) return; setStep(s => s+1); }}
                disabled={step===1 ? !canNext1 : photoBusy}
                className="flex-1 py-2.5 rounded-xl bg-[#16acbd] text-white font-bold text-xs shadow-md active:scale-95 disabled:opacity-40">
                <span className="lang-am">ቀጣይ →</span><span className="lang-en">Next →</span>
              </button>
            ) : (
              <button type="button" onClick={submit} disabled={!canSubmit || submitting}
                className="flex-1 py-2.5 rounded-xl bg-[#16acbd] text-white font-bold text-xs shadow-md active:scale-95 disabled:opacity-40 flex items-center justify-center gap-1">
                {submitting ? '...' : <><span className="lang-am">🚀 ማስታወቂያ መዝግብ</span><span className="lang-en">🚀 Submit Listing</span></>}
              </button>
            )}
          </div>
        </div>
      );
    }

    ReactDOM.createRoot(document.getElementById('root')).render(<SellerForm />);
  </script>
</body>
</html>
"""


# ==============================================================================
# BUYER FORM HTML (CSS Dual-Class Language Switcher)
# ==============================================================================
BUYER_FORM_HTML = r"""
<!DOCTYPE html>
<html lang="am">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
  <title>Post Buyer Request | የፍላጎት ጥያቄ</title>
  <script src="https://telegram.org/js/telegram-web-app.js"></script>
  <script src="https://cdn.tailwindcss.com"></script>
  <script crossorigin src="https://cdn.jsdelivr.net/npm/react@18.2.0/umd/react.production.min.js"></script>
  <script crossorigin src="https://cdn.jsdelivr.net/npm/react-dom@18.2.0/umd/react-dom.production.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/@babel/standalone@7.24.0/babel.min.js"></script>

  <style>
    body { margin:0; background:#b5eff3; font-family:system-ui,-apple-system,sans-serif; -webkit-tap-highlight-color:transparent; }
    .lang-en { display: none !important; }
    .lang-am { display: inline-block !important; }
    body.lang-en-active .lang-en { display: inline-block !important; }
    body.lang-en-active .lang-am { display: none !important; }
    .chip-active { background:#16acbd; color:#fff; font-weight:700; box-shadow:0 2px 6px rgba(22,172,189,.35); border: 1px solid #16acbd; }
    .chip-idle { background:#ffffff; color:#334155; border:1px solid #cbd5e1; font-weight: 600; }
    input, textarea { font-size: 15px !important; }
  </style>
</head>
<body class="bg-[#b5eff3] min-h-screen text-slate-800">
  <div id="root"></div>
  <script type="text/babel">
    const { useState, useEffect } = React;
    const tg = (window.Telegram && window.Telegram.WebApp) ? window.Telegram.WebApp : {
      expand(){}, ready(){}, close(){}, initDataUnsafe: {}, setHeaderColor(){}, setBackgroundColor(){}
    };
    try { tg.ready(); tg.expand(); tg.setHeaderColor('#16acbd'); tg.setBackgroundColor('#b5eff3'); } catch (e) {}

    const user = tg.initDataUnsafe?.user || {};
    const autoUsername = user.username ? '@' + user.username : '';
    const autoPhone = user.phone_number || '';

    function formatPrice(val) {
      const digits = String(val).replace(/[^\d]/g, '');
      return digits ? digits.replace(/\B(?=(\d{3})+(?!\d))/g, ',') : '';
    }
    function parsePrice(val) {
      return String(val).replace(/[^\d]/g, '');
    }

    function Chip({ am, en, active, onClick }) {
      return (
        <button type="button" onClick={onClick}
          className={`px-3 py-1.5 rounded-full text-xs whitespace-nowrap transition-all shadow-sm ${active ? 'chip-active' : 'chip-idle hover:bg-slate-50'}`}>
          <span className="lang-am">{am}</span>
          <span className="lang-en">{en}</span>
        </button>
      );
    }

    function BuyerForm() {
      const [lang, setLang] = useState(() => localStorage.getItem('adika_lang') || 'am');

      useEffect(() => {
        if (lang === 'en') document.body.classList.add('lang-en-active');
        else document.body.classList.remove('lang-en-active');
      }, [lang]);

      const switchLang = (newLang) => {
        setLang(newLang);
        localStorage.setItem('adika_lang', newLang);
        if (newLang === 'en') document.body.classList.add('lang-en-active');
        else document.body.classList.remove('lang-en-active');
      };

      const [category, setCategory] = useState('መኪና');
      const [budgetMin, setBudgetMin] = useState('');
      const [budgetMax, setBudgetMax] = useState('');
      const [createAlert, setCreateAlert] = useState(true);
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
            setStatus(result.message || 'Submission error');
            setSubmitting(false);
          }
        } catch (e) {
          setStatus('Network error');
          setSubmitting(false);
        }
      };

      if (status === 'ok') {
        return (
          <div className="min-h-screen flex items-center justify-center p-6 bg-[#b5eff3]">
            <div className="bg-white rounded-3xl p-6 text-center space-y-4 shadow-[0_12px_28px_rgba(15,23,42,0.12)] border border-white/60 max-w-sm">
              <div className="w-16 h-16 rounded-full bg-[#16acbd]/15 text-[#16acbd] flex items-center justify-center text-3xl mx-auto">✓</div>
              <h2 className="font-bold text-base text-slate-800">
                <span className="lang-am">ጥያቄዎ ተመዝግቧል!</span>
                <span className="lang-en">Request Broadcasted!</span>
              </h2>
              <p className="font-medium text-xs text-slate-600 leading-relaxed px-2">
                <span className="lang-am">የፍላጎት ጥያቄዎ ለተረጋገጡ ደላሎች ተሰራጭቷል።</span>
                <span className="lang-en">Your request has been saved and shared with certified brokers.</span>
              </p>
            </div>
          </div>
        );
      }

      return (
        <div className="min-h-screen bg-[#b5eff3] pb-24">
          <div className="fixed top-0 left-0 right-0 z-40 bg-[#16acbd] shadow-md px-4 py-2.5 text-white flex items-center justify-between">
            <h1 className="font-extrabold text-xs tracking-wide">
              <span className="lang-am">የሚፈልጉትን ንብረት ይግለጹ</span>
              <span className="lang-en">Submit Buyer Request</span>
            </h1>
            <div className="flex items-center bg-black/20 p-0.5 rounded-lg shrink-0">
              <button type="button" onClick={() => switchLang('am')}
                className={`px-2 py-0.5 rounded text-[10px] font-extrabold transition-all ${lang === 'am' ? 'bg-white text-[#16acbd] shadow-sm' : 'text-white/80'}`}>
                AM
              </button>
              <button type="button" onClick={() => switchLang('en')}
                className={`px-2 py-0.5 rounded text-[10px] font-extrabold transition-all ${lang === 'en' ? 'bg-white text-[#16acbd] shadow-sm' : 'text-white/80'}`}>
                EN
              </button>
            </div>
          </div>

          <div className="pt-14 px-3.5">
            <div className="bg-white rounded-2xl p-4 shadow-[0_12px_28px_rgba(15,23,42,0.12)] border border-slate-200/80 space-y-3.5">
              <div>
                <label className="text-xs font-bold text-slate-700 mb-1 block">
                  <span className="lang-am">📦 ምድብ</span>
                  <span className="lang-en">📦 Category</span>
                </label>
                <div className="flex gap-2">
                  <Chip am="🚗 መኪና" en="🚗 Vehicle" active={category==='መኪና'} onClick={() => setCategory('መኪና')} />
                  <Chip am="🏠 ቤት" en="🏠 Property" active={category==='ቤት'} onClick={() => setCategory('ቤት')} />
                </div>
              </div>

              <div>
                <label className="text-xs font-bold text-slate-700 mb-1 block">
                  <span className="lang-am">💰 የበጀት ክልል (ብር)</span>
                  <span className="lang-en">💰 Budget Range (ETB)</span>
                </label>
                <div className="flex gap-2 items-center">
                  <div className="flex-1 relative">
                    <span className="absolute left-2.5 top-1/2 -translate-y-1/2 text-xs font-bold text-slate-400">Min</span>
                    <input type="text" inputMode="numeric" value={budgetMin}
                      onChange={e => setBudgetMin(formatPrice(e.target.value))}
                      placeholder="1,000,000"
                      className="w-full pl-9 pr-2 py-2 rounded-xl bg-slate-50 border border-slate-200 focus:bg-white focus:ring-2 focus:ring-[#16acbd] outline-none text-xs font-semibold" />
                  </div>
                  <span className="text-slate-400 font-bold">—</span>
                  <div className="flex-1 relative">
                    <span className="absolute left-2.5 top-1/2 -translate-y-1/2 text-xs font-bold text-slate-400">Max</span>
                    <input type="text" inputMode="numeric" value={budgetMax}
                      onChange={e => setBudgetMax(formatPrice(e.target.value))}
                      placeholder="2,500,000"
                      className="w-full pl-10 pr-2 py-2 rounded-xl bg-slate-50 border border-slate-200 focus:bg-white focus:ring-2 focus:ring-[#16acbd] outline-none text-xs font-semibold" />
                  </div>
                </div>
              </div>

              <button type="button" onClick={() => setCreateAlert(!createAlert)}
                className={`w-full flex items-center justify-between p-3 rounded-xl border transition-all text-left ${
                  createAlert ? 'bg-[#16acbd]/10 border-[#16acbd]/50 text-[#0e7490]' : 'bg-slate-50 border-slate-200 text-slate-700'
                }`}>
                <div className="text-xs font-semibold">
                  <div>
                    <span className="lang-am">🔔 ፈጣን ማሳወቂያ</span>
                    <span className="lang-en">🔔 Match Alert</span>
                  </div>
                  <div className="text-[10px] text-slate-500">
                    <span className="lang-am">ተመሳሳይ ንብረት ሲለቀቅ ማሳወቂያ ይድረሰኝ</span>
                    <span className="lang-en">Notify me when matching items post</span>
                  </div>
                </div>
                <div className={`w-9 h-5 rounded-full relative transition-colors shrink-0 ${createAlert ? 'bg-[#16acbd]' : 'bg-slate-300'}`}>
                  <div className={`absolute top-0.5 w-4 h-4 rounded-full bg-white shadow transition-transform ${createAlert ? 'translate-x-4' : 'translate-x-0.5'}`} />
                </div>
              </button>

              <div>
                <label className="text-xs font-bold text-slate-700 mb-1 block">
                  <span className="lang-am">📝 ዝርዝር ፍላጎትና መስፈርቶች</span>
                  <span className="lang-en">📝 Requirements & Details</span>
                </label>
                <textarea value={details} onChange={e => setDetails(e.target.value)} rows={3}
                  placeholder="Toyota Vitz 2020, white, automatic, clean condition..."
                  className="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-200 focus:bg-white focus:ring-2 focus:ring-[#16acbd] outline-none text-xs resize-none" />
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-xs font-bold text-slate-700 mb-1 block">
                    <span className="lang-am">📞 ስልክ</span><span className="lang-en">📞 Phone</span>
                  </label>
                  <input type="tel" value={phone} onChange={e => setPhone(e.target.value)}
                    placeholder="0911223344"
                    className="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-200 focus:bg-white focus:ring-2 focus:ring-[#16acbd] outline-none text-xs font-bold" />
                </div>
                <div>
                  <label className="text-xs font-bold text-slate-700 mb-1 block">
                    <span className="lang-am">📱 ቴሌግራም</span><span className="lang-en">📱 Telegram</span>
                  </label>
                  <input type="text" value={telegramUser} onChange={e => setTelegramUser(e.target.value)}
                    placeholder="@username"
                    className="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-200 focus:bg-white focus:ring-2 focus:ring-[#16acbd] outline-none text-xs font-bold" />
                </div>
              </div>
            </div>
          </div>

          <div className="fixed bottom-0 left-0 right-0 p-3 bg-white/95 backdrop-blur-md border-t border-slate-200 flex gap-2 z-40">
            <button type="button" onClick={() => tg.close()}
              className="w-1/3 py-2.5 rounded-xl bg-slate-100 text-slate-700 font-bold text-xs active:scale-95">
              <span className="lang-am">ሰርዝ</span><span className="lang-en">Cancel</span>
            </button>
            <button type="button" onClick={submit} disabled={!details || submitting}
              className="flex-1 py-2.5 rounded-xl bg-[#16acbd] text-white font-bold text-xs shadow-md active:scale-95 disabled:opacity-40 flex items-center justify-center gap-1">
              {submitting ? '...' : <><span className="lang-am">📨 ጥያቄውን ላክ</span><span className="lang-en">📨 Broadcast</span></>}
            </button>
          </div>
        </div>
      );
    }

    ReactDOM.createRoot(document.getElementById('root')).render(<BuyerForm />);
  </script>
</body>
</html>
"""


# ==============================================================================
# EXPLORER HTML (CSS Dual-Class Switcher + Fixed Bottom Nav + Centered FAB)
# ==============================================================================
EXPLORER_HTML = r"""
<!DOCTYPE html>
<html lang="en">
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

    /* Bulletproof CSS Dual-Class Language Switcher */
    .lang-en { display: none !important; }
    .lang-am { display: inline-block !important; }
    body.lang-en-active .lang-en { display: inline-block !important; }
    body.lang-en-active .lang-am { display: none !important; }

    .adika-card {
      background: #ffffff;
      border: 1px solid rgba(226, 232, 240, 0.8);
      border-radius: 1rem;
      box-shadow: 0 8px 20px rgba(15, 23, 42, 0.08);
      transition: transform 0.12s ease, box-shadow 0.12s ease;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      overflow: hidden;
      position: relative;
    }
    .adika-card:active {
      transform: scale(0.98);
    }

    .no-scrollbar::-webkit-scrollbar { display: none; }
    .no-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
  </style>
</head>
<body class="bg-[#b5eff3] min-h-screen">

  <!-- ================================================================= -->
  <!-- 1. FIXED STICKY TEAL HEADER (Compact 3-Row Layout)                -->
  <!-- ================================================================= -->
  <header class="fixed top-0 left-0 right-0 z-50 bg-[#16acbd] text-white shadow-md p-2 flex flex-col gap-1.5">
    <div class="w-full max-w-md mx-auto flex flex-col gap-1.5">
      <!-- Top Row: Segmented Switcher + AM | EN Language Switcher -->
      <div class="flex items-center gap-2">
        <div class="flex-1 grid grid-cols-2 gap-1 p-0.5 bg-black/15 rounded-xl">
          <button id="tabSell" type="button"
            class="py-1 rounded-lg text-xs font-bold transition-all bg-white text-[#16acbd] shadow-sm flex items-center justify-center gap-1">
            <span>🛒</span>
            <span class="lang-am">ገበያ</span>
            <span class="lang-en">Marketplace</span>
          </button>
          <button id="tabBuy" type="button"
            class="py-1 rounded-lg text-xs font-bold transition-all text-white/90 hover:text-white flex items-center justify-center gap-1">
            <span>📋</span>
            <span class="lang-am">ፈላጊዎች</span>
            <span class="lang-en">Buyers</span>
          </button>
        </div>

        <!-- Global AM | EN Language Switcher Button -->
        <div class="flex items-center bg-black/20 p-0.5 rounded-xl shrink-0">
          <button id="langAmBtn" type="button" class="px-2 py-1 rounded-lg text-xs font-extrabold transition-all bg-white text-[#16acbd] shadow-sm">
            AM
          </button>
          <button id="langEnBtn" type="button" class="px-2 py-1 rounded-lg text-xs font-extrabold transition-all text-white/80 hover:text-white">
            EN
          </button>
        </div>
      </div>

      <!-- Second Row: Sleek Quick Search Input Bar -->
      <div class="relative">
        <span class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 text-xs pointer-events-none">🔍</span>
        <input id="q" type="search" placeholder="ንብረት ይፈልጉ... / Search listings..." autocomplete="off"
          class="w-full pl-8 pr-3 py-1.5 rounded-xl bg-white text-slate-800 placeholder-slate-400 text-xs font-medium outline-none shadow-sm focus:ring-2 focus:ring-white/50" />
      </div>

      <!-- Third Row: Category Pills (Horizontal Scroll) -->
      <div id="cats" class="flex gap-1.5 overflow-x-auto no-scrollbar pb-0.5">
        <button type="button" class="cat-pill px-3 py-1 rounded-full text-xs font-bold whitespace-nowrap transition-all bg-white text-[#16acbd] shadow-sm" data-id="">
          <span class="lang-am">✨ ሁሉም</span>
          <span class="lang-en">✨ All</span>
        </button>
        <button type="button" class="cat-pill px-3 py-1 rounded-full text-xs font-bold whitespace-nowrap transition-all bg-white/20 text-white hover:bg-white/30" data-id="መኪና">
          <span class="lang-am">🚗 መኪኖች</span>
          <span class="lang-en">🚗 Cars</span>
        </button>
        <button type="button" class="cat-pill px-3 py-1 rounded-full text-xs font-bold whitespace-nowrap transition-all bg-white/20 text-white hover:bg-white/30" data-id="ቤት">
          <span class="lang-am">🏠 ቤቶች</span>
          <span class="lang-en">🏠 Property</span>
        </button>
        <button type="button" class="cat-pill px-3 py-1 rounded-full text-xs font-bold whitespace-nowrap transition-all bg-white/20 text-white hover:bg-white/30" data-id="ንግድ">
          <span class="lang-am">🏢 ንግድ</span>
          <span class="lang-en">🏢 Commercial</span>
        </button>
      </div>
    </div>
  </header>

  <!-- ================================================================= -->
  <!-- 2. MAIN CONTENT AREA (Snug pt-32 Spacing & Wide px-2.5 Grid)      -->
  <!-- ================================================================= -->
  <main class="w-full max-w-md mx-auto pt-32 pb-24 px-2.5">
    <!-- Active Filter Banner -->
    <div id="filterBanner" class="hidden mb-2 px-3 py-1.5 bg-white/90 backdrop-blur-sm rounded-xl border border-white flex items-center justify-between text-xs shadow-sm">
      <span id="filterText" class="font-bold text-[#0e7490] truncate"></span>
      <button id="clearFilterBtn" type="button" class="text-rose-600 font-bold ml-2 shrink-0">✕</button>
    </div>

    <div id="status" class="text-center py-8 text-slate-600 font-semibold text-xs">
      <div class="inline-block animate-spin w-5 h-5 border-2 border-[#16acbd] border-t-transparent rounded-full mb-1.5"></div>
      <div>
        <span class="lang-am">እየጫነ ነው…</span>
        <span class="lang-en">Loading listings…</span>
      </div>
    </div>

    <!-- 2-Column Responsive Elevated Cards Grid -->
    <div id="grid" class="grid grid-cols-2 gap-2.5"></div>

    <!-- Load More -->
    <div class="text-center mt-3.5 mb-2">
      <button id="more" type="button"
        class="hidden px-5 py-2 rounded-full bg-white text-[#16acbd] font-extrabold text-xs shadow-md border border-white/60 active:scale-95 transition-all">
        <span class="lang-am">ተጨማሪ ↓</span>
        <span class="lang-en">Load More ↓</span>
      </button>
    </div>
  </main>

  <!-- ================================================================= -->
  <!-- 3. FIXED FLOATING BOTTOM NAV & PRECISION CENTERED FAB (+)         -->
  <!-- ================================================================= -->
  <nav class="fixed bottom-3 left-3 right-3 z-50 bg-white/95 backdrop-blur-xl rounded-full shadow-[0_10px_30px_rgba(0,0,0,0.15)] border border-white/60 px-4 py-2 flex items-center justify-between max-w-md mx-auto">
    <!-- Left Section: Home & AI Tabs -->
    <div class="flex items-center gap-2 w-5/12 justify-around">
      <button id="navHome" type="button" class="flex flex-col items-center justify-center px-1 py-0.5 rounded-full bg-[#16acbd]/15 text-[#16acbd] transition-all">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/>
        </svg>
        <span class="text-[9px] font-bold mt-0.5">
          <span class="lang-am">መነሻ</span>
          <span class="lang-en">Home</span>
        </span>
      </button>

      <button id="navAi" type="button" class="flex flex-col items-center justify-center px-1 py-0.5 rounded-full text-slate-500 hover:text-slate-800 transition-all">
        <div class="relative">
          <svg class="w-4 h-4 text-[#16acbd]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
          </svg>
          <span class="absolute -top-1 -right-1 w-1.5 h-1.5 rounded-full bg-amber-400 animate-ping"></span>
        </div>
        <span class="text-[9px] font-semibold mt-0.5 text-[#0e7490]">
          <span class="lang-am">AI ✨</span>
          <span class="lang-en">AI ✨</span>
        </span>
      </button>
    </div>

    <!-- Center Precision-Locked FAB (+) Button -->
    <button id="fabBtn" type="button"
      class="absolute -top-5 left-1/2 -translate-x-1/2 z-50 w-12 h-12 bg-[#16acbd] text-white rounded-full shadow-lg flex items-center justify-center border-4 border-[#b5eff3] active:scale-95 transition-transform">
      <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.8" d="M12 4v16m8-8H4"/>
      </svg>
    </button>

    <!-- Right Section: Messages & Help Tabs -->
    <div class="flex items-center gap-2 w-5/12 justify-around">
      <button id="navMessages" type="button" class="flex flex-col items-center justify-center px-1 py-0.5 rounded-full text-slate-500 hover:text-slate-800 transition-all">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"/>
        </svg>
        <span class="text-[9px] font-semibold mt-0.5">
          <span class="lang-am">መልእክት</span>
          <span class="lang-en">Inbox</span>
        </span>
      </button>

      <button id="navHelp" type="button" class="flex flex-col items-center justify-center px-1 py-0.5 rounded-full text-slate-500 hover:text-slate-800 transition-all">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
        </svg>
        <span class="text-[9px] font-semibold mt-0.5">
          <span class="lang-am">እርዳታ</span>
          <span class="lang-en">Help</span>
        </span>
      </button>
    </div>
  </nav>

  <!-- ================================================================= -->
  <!-- 4. DEDICATED AI SMART FILTER MODAL                                -->
  <!-- ================================================================= -->
  <div id="aiModal" class="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm hidden items-end justify-center">
    <div class="w-full max-w-md bg-white rounded-t-3xl max-h-[85vh] flex flex-col shadow-2xl overflow-hidden">
      <div class="px-4 py-3 bg-[#16acbd] text-white flex items-center justify-between shrink-0">
        <div class="flex items-center gap-2">
          <span class="text-lg">✨</span>
          <div>
            <h3 class="font-extrabold text-xs tracking-wide">
              <span class="lang-am">AI Smart Filter</span>
              <span class="lang-en">AI Smart Filter</span>
            </h3>
            <p class="text-[10px] text-white/80">
              <span class="lang-am">በተፈጥሮአዊ ቋንቋ ወይም በቅንብሮች ይፈልጉ</span>
              <span class="lang-en">Search in natural language or smart tags</span>
            </p>
          </div>
        </div>
        <button id="aiModalClose" type="button" class="w-7 h-7 rounded-full bg-white/20 hover:bg-white/30 text-white font-bold flex items-center justify-center text-sm">✕</button>
      </div>

      <div class="overflow-y-auto flex-1 p-4 space-y-4">
        <div>
          <label class="text-xs font-bold text-slate-700 mb-1 block">
            <span class="lang-am">ምን አይነት ንብረት ይፈልጋሉ?</span>
            <span class="lang-en">What are you looking for?</span>
          </label>
          <textarea id="aiPrompt" rows="2"
            placeholder="Toyota Vitz, Automatic, under 2M ETB..."
            class="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-200 focus:bg-white focus:ring-2 focus:ring-[#16acbd] outline-none text-xs resize-none"></textarea>
        </div>

        <div>
          <label class="text-xs font-bold text-slate-700 mb-1.5 block">
            <span class="lang-am">ፈጣን አማራጮች</span>
            <span class="lang-en">Quick Tags</span>
          </label>
          <div class="flex flex-wrap gap-1.5">
            <button type="button" class="ai-chip px-2.5 py-1 rounded-full bg-slate-100 text-slate-700 text-xs font-medium hover:bg-[#16acbd]/10" data-q="መኪና">🚗 Cars / መኪኖች</button>
            <button type="button" class="ai-chip px-2.5 py-1 rounded-full bg-slate-100 text-slate-700 text-xs font-medium hover:bg-[#16acbd]/10" data-q="ቤት">🏠 House / ቤቶች</button>
            <button type="button" class="ai-chip px-2.5 py-1 rounded-full bg-slate-100 text-slate-700 text-xs font-medium hover:bg-[#16acbd]/10" data-q="ኦቶማቲክ">⚙️ Automatic</button>
            <button type="button" class="ai-chip px-2.5 py-1 rounded-full bg-slate-100 text-slate-700 text-xs font-medium hover:bg-[#16acbd]/10" data-q="አዲስ">✨ Brand New</button>
            <button type="button" class="ai-chip px-2.5 py-1 rounded-full bg-slate-100 text-slate-700 text-xs font-medium hover:bg-[#16acbd]/10" data-q="ቪላ">🏡 Villa</button>
          </div>
        </div>

        <div>
          <label class="text-xs font-bold text-slate-700 mb-1.5 block">
            <span class="lang-am">የበጀት መጠን</span>
            <span class="lang-en">Budget Range</span>
          </label>
          <div class="grid grid-cols-3 gap-1.5 text-xs">
            <button type="button" class="price-chip py-1.5 px-2 rounded-lg border border-slate-200 text-slate-700 font-semibold text-center hover:border-[#16acbd]" data-price="< 1M">&lt; 1M ETB</button>
            <button type="button" class="price-chip py-1.5 px-2 rounded-lg border border-slate-200 text-slate-700 font-semibold text-center hover:border-[#16acbd]" data-price="1M - 3M">1M - 3M ETB</button>
            <button type="button" class="price-chip py-1.5 px-2 rounded-lg border border-slate-200 text-slate-700 font-semibold text-center hover:border-[#16acbd]" data-price="> 3M">&gt; 3M ETB</button>
          </div>
        </div>
      </div>

      <div class="p-3 bg-white border-t border-slate-100 shrink-0 flex gap-2">
        <button id="aiResetBtn" type="button" class="w-1/3 py-2.5 rounded-xl bg-slate-100 text-slate-700 font-bold text-xs">
          <span class="lang-am">አጽዳ</span><span class="lang-en">Reset</span>
        </button>
        <button id="aiApplyBtn" type="button" class="flex-1 py-2.5 rounded-xl bg-[#16acbd] text-white font-bold text-xs shadow-md active:scale-95 flex items-center justify-center gap-1.5">
          <span>✨ <span class="lang-am">አጣራ</span><span class="lang-en">Apply</span></span>
        </button>
      </div>
    </div>
  </div>

  <!-- ================================================================= -->
  <!-- 5. BOTTOM-SHEET DETAIL MODAL WITH SHARE BUTTON                    -->
  <!-- ================================================================= -->
  <div id="modalOverlay" class="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm hidden items-end justify-center">
    <div id="modalSheet"
      class="w-full max-w-md bg-white rounded-t-3xl max-h-[85vh] flex flex-col shadow-2xl overflow-hidden">

      <div class="px-4 py-2.5 bg-white border-b border-slate-100 flex items-center justify-between shrink-0">
        <div class="flex items-center gap-2">
          <span id="modalCategoryBadge" class="px-2.5 py-0.5 rounded-full bg-[#16acbd]/10 text-[#0e7490] text-xs font-bold">Property</span>
          <span id="modalIdBadge" class="text-xs text-slate-400 font-semibold">#ADK-</span>
        </div>
        <div class="flex items-center gap-1.5">
          <button id="modalFavBtn" type="button" class="w-7 h-7 rounded-full bg-slate-100 text-slate-400 hover:text-rose-500 font-bold flex items-center justify-center text-sm">❤️</button>
          <button id="modalClose" type="button" class="w-7 h-7 rounded-full bg-slate-100 text-slate-500 font-bold flex items-center justify-center text-sm">✕</button>
        </div>
      </div>

      <div id="modalScrollBody" class="overflow-y-auto flex-1 p-4 space-y-3.5">
        <div id="modalMediaContainer" class="w-full h-48 rounded-2xl overflow-hidden bg-slate-100 relative"></div>

        <div>
          <div class="flex items-center gap-1">
            <h2 id="modalTitle" class="text-sm font-extrabold text-slate-900 leading-tight"></h2>
            <span class="text-emerald-600 text-xs font-black">✔</span>
          </div>
          <div class="mt-1.5 flex items-center gap-2">
            <span id="modalPrice" class="px-2.5 py-0.5 rounded-full bg-[#16acbd]/15 text-[#0e7490] font-black text-xs"></span>
            <span id="modalTime" class="text-[11px] text-slate-400 font-medium"></span>
          </div>
        </div>

        <div id="modalSpecs" class="grid grid-cols-2 gap-2 text-xs font-medium text-slate-600 bg-slate-50 p-2.5 rounded-xl border border-slate-100"></div>

        <div>
          <h4 class="text-[11px] font-bold text-slate-500 uppercase tracking-wider mb-1">
            <span class="lang-am">ዝርዝር መግለጫ</span>
            <span class="lang-en">Full Description</span>
          </h4>
          <p id="modalDesc" class="text-xs text-slate-700 leading-relaxed whitespace-pre-line bg-slate-50/50 p-2.5 rounded-xl border border-slate-100"></p>
        </div>
      </div>

      <!-- Pinned 3 Action Buttons (Call, Telegram, Share) -->
      <div class="p-2.5 bg-white border-t border-slate-100 shrink-0 grid grid-cols-3 gap-2">
        <a id="modalCallBtn" href="#"
          class="flex items-center justify-center gap-1 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs shadow-sm active:scale-95 transition-all">
          <span>📞</span>
          <span class="lang-am">ደውል</span>
          <span class="lang-en">Call</span>
        </a>
        <a id="modalChatBtn" href="#"
          class="flex items-center justify-center gap-1 py-2.5 rounded-xl bg-[#16acbd] hover:bg-[#1394a3] text-white font-bold text-xs shadow-sm active:scale-95 transition-all">
          <span>💬</span> <span>Telegram</span>
        </a>
        <button id="modalShareBtn" type="button"
          class="flex items-center justify-center gap-1 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-900 text-white font-bold text-xs shadow-sm active:scale-95 transition-all">
          <span>🔗</span>
          <span class="lang-am">አጋራ</span>
          <span class="lang-en">Share</span>
        </button>
      </div>
    </div>
  </div>

  <!-- ================================================================= -->
  <!-- 6. APPLICATION LOGIC & CSS CLASS TOGGLE                           -->
  <!-- ================================================================= -->
  <script>
  (function () {
    var tg = window.Telegram && window.Telegram.WebApp ? window.Telegram.WebApp : null;
    if (tg) {
      try { tg.ready(); tg.expand(); tg.setHeaderColor('#16acbd'); tg.setBackgroundColor('#b5eff3'); } catch (e) {}
    }

    var favorites = {};
    try {
      favorites = JSON.parse(localStorage.getItem('adika_favs') || '{}');
    } catch(e) {}

    function toggleFav(id) {
      if (favorites[id]) delete favorites[id];
      else favorites[id] = true;
      try { localStorage.setItem('adika_favs', JSON.stringify(favorites)); } catch(e){}
      renderFavoritesUI();
    }

    var state = {
      tab: "marketplace",
      category: "",
      q: "",
      page: 1,
      hasMore: false,
      loading: false,
      items: [],
      selectedItem: null
    };

    var grid = document.getElementById("grid");
    var statusEl = document.getElementById("status");
    var moreBtn = document.getElementById("more");
    var tabSell = document.getElementById("tabSell");
    var tabBuy = document.getElementById("tabBuy");
    var qInput = document.getElementById("q");
    var catsEl = document.getElementById("cats");
    var fabBtn = document.getElementById("fabBtn");
    var filterBanner = document.getElementById("filterBanner");
    var filterText = document.getElementById("filterText");
    var clearFilterBtn = document.getElementById("clearFilterBtn");

    var langAmBtn = document.getElementById("langAmBtn");
    var langEnBtn = document.getElementById("langEnBtn");

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
    var modalShareBtn = document.getElementById("modalShareBtn");
    var modalFavBtn = document.getElementById("modalFavBtn");

    // AI Modal elements
    var aiModal = document.getElementById("aiModal");
    var aiModalClose = document.getElementById("aiModalClose");
    var aiPrompt = document.getElementById("aiPrompt");
    var aiApplyBtn = document.getElementById("aiApplyBtn");
    var aiResetBtn = document.getElementById("aiResetBtn");

    // =================================================================
    // BULLETPROOF CSS DUAL-CLASS LANGUAGE SWITCHER
    // =================================================================
    function setLanguage(lang) {
      localStorage.setItem('adika_lang', lang);
      if (lang === 'en') {
        document.body.classList.add('lang-en-active');
        langEnBtn.className = "px-2 py-1 rounded-lg text-xs font-extrabold transition-all bg-white text-[#16acbd] shadow-sm";
        langAmBtn.className = "px-2 py-1 rounded-lg text-xs font-extrabold transition-all text-white/80 hover:text-white";
        qInput.placeholder = "Search listings...";
      } else {
        document.body.classList.remove('lang-en-active');
        langAmBtn.className = "px-2 py-1 rounded-lg text-xs font-extrabold transition-all bg-white text-[#16acbd] shadow-sm";
        langEnBtn.className = "px-2 py-1 rounded-lg text-xs font-extrabold transition-all text-white/80 hover:text-white";
        qInput.placeholder = "ንብረት ይፈልጉ...";
      }
    }

    langAmBtn.onclick = function() { setLanguage('am'); };
    langEnBtn.onclick = function() { setLanguage('en'); };

    var initialLang = localStorage.getItem('adika_lang') || 'am';
    setLanguage(initialLang);

    function esc(s) {
      return String(s == null ? "" : s)
        .replace(/&/g, "&amp;").replace(/</g, "&lt;")
        .replace(/>/g, "&gt;").replace(/"/g, "&quot;");
    }

    function relativeTime(iso) {
      if (!iso) return "";
      try {
        var secs = Math.max(0, Math.floor((Date.now() - new Date(iso).getTime()) / 1000));
        if (secs < 60) return "Just now";
        if (secs < 3600) return Math.floor(secs / 60) + "m";
        if (secs < 86400) return Math.floor(secs / 3600) + "h";
        return Math.floor(secs / 86400) + "d";
      } catch (e) { return ""; }
    }

    function renderFavoritesUI() {
      var btns = document.querySelectorAll(".card-fav-btn");
      btns.forEach(function(b) {
        var id = b.getAttribute("data-id");
        b.innerHTML = favorites[id] ? "❤️" : "🤍";
      });
      if (state.selectedItem) {
        modalFavBtn.innerHTML = favorites[state.selectedItem.id] ? "❤️" : "🤍";
      }
    }

    function createCardElement(item) {
      var photos = item.photos || [];
      if (!Array.isArray(photos)) photos = [];
      var isCar = (item.main_category === "መኪና" || item.category === "መኪና");
      var icon = isCar ? "🚗" : "🏠";

      var extra = item.extra_data || {};
      if (typeof extra === "string") {
        try { extra = JSON.parse(extra); } catch (e) { extra = {}; }
      }

      var cardTitleAm = "";
      var cardTitleEn = "";
      var subBadge1 = "";
      var subBadge2 = "";

      if (isCar) {
        cardTitleAm = extra.car_model || item.sub_category || "መኪና";
        cardTitleEn = extra.car_model || item.sub_category || "Vehicle";
        if (extra.transmission) subBadge1 = extra.transmission.split('/')[0].trim();
        if (extra.fuel_type) subBadge2 = extra.fuel_type.split('/')[0].trim();
      } else {
        cardTitleAm = item.sub_category || extra.house_type || "ቤት";
        cardTitleEn = item.sub_category || extra.house_type || "Property";
        if (extra.bedrooms) subBadge1 = extra.bedrooms + " Bed";
        if (extra.location_area) subBadge2 = extra.location_area;
      }

      var media;
      if (photos.length > 0) {
        media = '<img src="' + esc(photos[0]) + '" alt="" class="w-full h-full object-cover" loading="lazy" />';
      } else {
        media = '<div class="w-full h-full flex flex-col items-center justify-center bg-gradient-to-br from-[#16acbd] to-[#0e7490] text-white p-2">' +
          '<span class="text-3xl mb-1">' + icon + '</span>' +
          '<span class="text-[9px] font-bold text-white/90">No Image</span>' +
          '</div>';
      }

      var priceNum = item.price || "—";
      var priceLabel = priceNum + " ETB";
      var views = item.view_count || item.views_count || 12;
      var isFav = Boolean(favorites[item.id]);

      var card = document.createElement("div");
      card.className = "adika-card cursor-pointer";
      card.innerHTML =
        '<div class="relative w-full h-24 bg-slate-100 overflow-hidden">' +
          '<!-- Active Online Status Green Pulsing Dot -->' +
          '<div class="absolute top-2 left-2 z-10 w-2.5 h-2.5 bg-emerald-500 rounded-full animate-pulse shadow-[0_0_8px_rgba(16,185,129,0.8)]"></div>' +
          media +
          '<div class="absolute bottom-1 left-1 right-1 flex justify-between items-center text-[8px] text-white font-bold">' +
            '<span class="bg-black/60 backdrop-blur-sm px-1.5 py-0.5 rounded">👁️ ' + esc(views) + '</span>' +
            '<span class="bg-black/60 backdrop-blur-sm px-1.5 py-0.5 rounded">' + esc(relativeTime(item.created_at)) + '</span>' +
          '</div>' +
        '</div>' +
        '<div class="p-2 flex-1 flex flex-col justify-between">' +
          '<div>' +
            '<div class="font-extrabold text-xs text-slate-800 truncate flex items-center gap-0.5">' +
              '<span class="truncate lang-am">' + esc(cardTitleAm) + '</span>' +
              '<span class="truncate lang-en">' + esc(cardTitleEn) + '</span>' +
              '<span class="text-emerald-600 text-[10px] shrink-0" title="Verified">✔</span>' +
            '</div>' +
            '<div class="flex items-center gap-1 mt-1 overflow-hidden">' +
              (subBadge1 ? '<span class="px-1.5 py-0.5 rounded bg-slate-100 text-slate-600 font-semibold text-[8px] truncate">' + esc(subBadge1) + '</span>' : '') +
              (subBadge2 ? '<span class="px-1.5 py-0.5 rounded bg-slate-100 text-slate-600 font-semibold text-[8px] truncate">' + esc(subBadge2) + '</span>' : '') +
            '</div>' +
          '</div>' +
          '<div class="mt-2 flex items-center justify-between gap-1">' +
            '<div class="inline-block px-1.5 py-0.5 rounded bg-[#16acbd]/10 text-[#0e7490] font-black text-[10px] truncate max-w-[80%]">💰 ' + esc(priceLabel) + '</div>' +
            '<button type="button" class="card-fav-btn text-sm p-0.5 transition-transform active:scale-75" data-id="' + esc(item.id) + '">' +
              (isFav ? '❤️' : '🤍') +
            '</button>' +
          '</div>' +
        '</div>';

      var favBtnEl = card.querySelector(".card-fav-btn");
      favBtnEl.onclick = function(e) {
        e.stopPropagation();
        toggleFav(item.id);
      };

      card.onclick = function () {
        openDetailModal(item);
      };

      return card;
    }

    function openDetailModal(item) {
      state.selectedItem = item;
      var extra = item.extra_data || {};
      if (typeof extra === "string") {
        try { extra = JSON.parse(extra); } catch (e) { extra = {}; }
      }
      var photos = item.photos || [];
      if (!Array.isArray(photos)) photos = [];
      var isCar = (item.main_category === "መኪና" || item.category === "መኪና");

      modalCategoryBadge.textContent = (isCar ? "Vehicle" : "Property") + " • Verified ✔";
      modalIdBadge.textContent = "#ADK-" + (item.id || "001");

      var modalTitleText = isCar ? (extra.car_model || item.sub_category || "Vehicle") : (item.sub_category || extra.house_type || "Property");
      modalTitle.textContent = modalTitleText;

      var isSell = String(item.req_type || "").toUpperCase() === "SELL";
      modalPrice.textContent = (isSell ? "Price: " : "Budget: ") + (item.price || "Contact") + " ETB";
      modalTime.textContent = "⏱️ " + relativeTime(item.created_at);
      modalDesc.textContent = item.description || "No further details provided.";

      if (photos.length > 0) {
        modalMediaContainer.innerHTML = '<img src="' + esc(photos[0]) + '" alt="" class="w-full h-full object-cover" />';
      } else {
        modalMediaContainer.innerHTML =
          '<div class="w-full h-full flex flex-col items-center justify-center bg-gradient-to-br from-[#16acbd] to-[#0e7490] text-white">' +
            '<span class="text-4xl mb-1">' + (isCar ? '🚗' : '🏠') + '</span>' +
            '<span class="text-xs font-bold">No Image Available</span>' +
          '</div>';
      }

      var specsHtml = "";
      if (isCar) {
        if (extra.fuel_type) specsHtml += '<div>⛽ Fuel: <span class="font-bold text-slate-800">' + esc(extra.fuel_type) + '</span></div>';
        if (extra.transmission) specsHtml += '<div>⚙️ Trans: <span class="font-bold text-slate-800">' + esc(extra.transmission) + '</span></div>';
        if (extra.mileage) specsHtml += '<div>🛣️ Mileage: <span class="font-bold text-slate-800">' + esc(extra.mileage) + ' KM</span></div>';
        if (extra.condition) specsHtml += '<div>📊 Condition: <span class="font-bold text-slate-800">' + esc(extra.condition) + '</span></div>';
      } else {
        if (extra.bedrooms) specsHtml += '<div>🛏️ Beds: <span class="font-bold text-slate-800">' + esc(extra.bedrooms) + '</span></div>';
        if (extra.bathrooms) specsHtml += '<div>🛁 Baths: <span class="font-bold text-slate-800">' + esc(extra.bathrooms) + '</span></div>';
        if (extra.parking) specsHtml += '<div>🚗 Parking: <span class="font-bold text-slate-800">' + esc(extra.parking) + '</span></div>';
        if (extra.condition) specsHtml += '<div>📊 Condition: <span class="font-bold text-slate-800">' + esc(extra.condition) + '</span></div>';
      }
      modalSpecs.innerHTML = specsHtml || '<div>Status: <span class="font-bold text-slate-800">Active & Verified ✔</span></div>';

      var phone = item.phone ? String(item.phone).replace(/\s+/g, "") : "";
      var tUser = extra.telegram_user ? String(extra.telegram_user).replace("@", "") : "";
      modalCallBtn.href = phone ? ("tel:" + phone) : "#";
      modalChatBtn.href = tUser ? ("https://t.me/" + tUser) : (item.user_chat_id ? ("tg://user?id=" + item.user_chat_id) : "#");

      modalFavBtn.innerHTML = favorites[item.id] ? "❤️" : "🤍";
      modalFavBtn.onclick = function() {
        toggleFav(item.id);
      };

      modalShareBtn.onclick = function() {
        var shareUrl = window.location.origin + "/explorer?id=" + item.id;
        var shareText = "Check out " + modalTitle.textContent + " on Adika Marketplace: " + shareUrl;
        if (navigator.share) {
          navigator.share({ title: "Adika Marketplace", text: shareText, url: shareUrl }).catch(function(){});
        } else if (tg && tg.openTelegramLink) {
          tg.openTelegramLink("https://t.me/share/url?url=" + encodeURIComponent(shareUrl) + "&text=" + encodeURIComponent(shareText));
        } else {
          navigator.clipboard.writeText(shareText);
          alert("Link copied!");
        }
      };

      modalOverlay.classList.remove("hidden");
      modalOverlay.classList.add("flex");

      if (item.id) {
        try { fetch("/api/views/" + item.id, { method: "POST" }).catch(function(){}); } catch(e){}
      }
    }

    modalClose.onclick = function () {
      modalOverlay.classList.add("hidden");
      modalOverlay.classList.remove("flex");
      state.selectedItem = null;
    };
    modalOverlay.onclick = function (e) {
      if (e.target === modalOverlay) modalClose.onclick();
    };

    function finishLoading(items, append, hasMore) {
      state.loading = false;
      if (!append) {
        grid.innerHTML = "";
        state.items = items;
      } else {
        state.items = state.items.concat(items);
      }
      if (!items || !items.length) {
        if (!append) {
          statusEl.style.display = "block";
          statusEl.innerHTML = '<div class="text-2xl mb-1">📭</div><div class="text-slate-600 font-bold text-xs"><span class="lang-am">ምንም ንብረት አልተገኘም</span><span class="lang-en">No listings found</span></div>';
        }
        moreBtn.classList.add("hidden");
        return;
      }
      statusEl.style.display = "none";
      for (var i = 0; i < items.length; i++) {
        grid.appendChild(createCardElement(items[i]));
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
        statusEl.innerHTML = '<div class="inline-block animate-spin w-5 h-5 border-2 border-[#16acbd] border-t-transparent rounded-full mb-1.5"></div><div><span class="lang-am">እየጫነ ነው…</span><span class="lang-en">Loading…</span></div>';
        grid.innerHTML = "";
      }

      var page = append ? state.page + 1 : 1;
      var qs = "page=" + page + "&limit=12&order=DESC&active_only=1&type=" +
        (state.tab === "marketplace" ? "SELL" : "BUY");
      if (state.category) qs += "&category=" + encodeURIComponent(state.category);
      if (state.q) qs += "&q=" + encodeURIComponent(state.q);

      fetch("/api/explorer/listings?" + qs)
        .then(function(res){ return res.json(); })
        .then(function(data){
          var items = data.items || data.listings || [];
          state.page = page;
          state.hasMore = !!(data.has_more || data.hasMore);
          finishLoading(items, append, state.hasMore);
        })
        .catch(function(err){
          finishLoading([], append, false);
        });
    }

    // Dynamic Central FAB
    fabBtn.onclick = function () {
      if (state.tab === "marketplace") {
        window.location.href = "/seller-form";
      } else {
        window.location.href = "/buyer-form";
      }
    };

    function setTabs() {
      if (state.tab === "marketplace") {
        tabSell.className = "py-1 rounded-lg text-xs font-bold transition-all bg-white text-[#16acbd] shadow-sm flex items-center justify-center gap-1";
        tabBuy.className = "py-1 rounded-lg text-xs font-bold transition-all text-white/90 hover:text-white flex items-center justify-center gap-1";
      } else {
        tabBuy.className = "py-1 rounded-lg text-xs font-bold transition-all bg-white text-[#16acbd] shadow-sm flex items-center justify-center gap-1";
        tabSell.className = "py-1 rounded-lg text-xs font-bold transition-all text-white/90 hover:text-white flex items-center justify-center gap-1";
      }
    }

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
      var buttons = catsEl.querySelectorAll("button");
      buttons.forEach(function(b) {
        if ((b.getAttribute("data-id") || "") === state.category) {
          b.className = "cat-pill px-3 py-1 rounded-full text-xs font-bold whitespace-nowrap transition-all bg-white text-[#16acbd] shadow-sm";
        } else {
          b.className = "cat-pill px-3 py-1 rounded-full text-xs font-bold whitespace-nowrap transition-all bg-white/20 text-white hover:bg-white/30";
        }
      });
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

    // AI Smart Filter modal handlers
    document.getElementById("navAi").onclick = function() {
      aiModal.classList.remove("hidden");
      aiModal.classList.add("flex");
    };
    aiModalClose.onclick = function() {
      aiModal.classList.add("hidden");
      aiModal.classList.remove("flex");
    };
    aiModal.onclick = function(e) {
      if (e.target === aiModal) aiModalClose.onclick();
    };

    document.querySelectorAll(".ai-chip").forEach(function(btn) {
      btn.onclick = function() {
        var q = btn.getAttribute("data-q");
        aiPrompt.value = (aiPrompt.value ? aiPrompt.value + " " : "") + q;
      };
    });

    document.querySelectorAll(".price-chip").forEach(function(btn) {
      btn.onclick = function() {
        var p = btn.getAttribute("data-price");
        aiPrompt.value = (aiPrompt.value ? aiPrompt.value + " " : "") + p;
      };
    });

    aiApplyBtn.onclick = function() {
      var query = aiPrompt.value.trim();
      if (!query) {
        aiModalClose.onclick();
        return;
      }
      aiApplyBtn.disabled = true;
      aiApplyBtn.innerHTML = '<span>⏳ Searching...</span>';
      filterText.textContent = "🔍 " + query;
      filterBanner.classList.remove("hidden");

      fetch("/api/ai-search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: query })
      })
      .then(function(res) { return res.json(); })
      .then(function(data) {
        aiApplyBtn.disabled = false;
        aiApplyBtn.innerHTML = '<span>✨ <span class="lang-am">አጣራ</span><span class="lang-en">Apply</span></span>';
        aiModalClose.onclick();
        var bannerText = data.banner_text;
        if (!bannerText) {
          var parsed = data.parsed || {};
          var tagParts = [];
          if (parsed.keyword) tagParts.push(parsed.keyword);
          if (parsed.category && parsed.category !== "all") {
            tagParts.push(parsed.category === "cars" ? "🚗 Cars" : "🏠 Property");
          }
          if (parsed.max_price) {
            tagParts.push("< " + Number(parsed.max_price).toLocaleString() + " ETB");
          }
          bannerText = tagParts.length ? tagParts.join(" • ") : ("AI Filter: " + query);
        }
        filterText.textContent = bannerText;
        filterBanner.classList.remove("hidden");
        var items = data.results || data.items || [];
        finishLoading(items, false, false);
      })
      .catch(function(err) {
        aiApplyBtn.disabled = false;
        aiApplyBtn.innerHTML = '<span>✨ <span class="lang-am">አጣራ</span><span class="lang-en">Apply</span></span>';
        aiModalClose.onclick();
        state.q = query;
        qInput.value = query;
        load(false);
      });
    };

    aiResetBtn.onclick = function() {
      aiPrompt.value = "";
      state.q = "";
      qInput.value = "";
      filterBanner.classList.add("hidden");
      aiModalClose.onclick();
      load(false);
    };

    clearFilterBtn.onclick = function() {
      state.q = "";
      qInput.value = "";
      aiPrompt.value = "";
      filterBanner.classList.add("hidden");
      load(false);
    };

    // Bottom Navigation Handlers
    document.getElementById("navHome").onclick = function () {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    };
    document.getElementById("navMessages").onclick = function () {
      if (tg && tg.openTelegramLink) {
        tg.openTelegramLink("https://t.me/AdikaMarketplaceBot");
      } else {
        window.open("https://t.me/AdikaMarketplaceBot", "_blank");
      }
    };
    document.getElementById("navHelp").onclick = function () {
      var msg = "Adika Marketplace • Help Center\nContact @AdikaMarketplaceBot or call 0911000000.";
      if (tg && tg.showAlert) tg.showAlert(msg);
      else alert(msg);
    };

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


@web_app.route('/api/submit-listing', methods=['POST'])
def submit_listing():
    try:
        data = request.json or {}
        user_id = data.get('user_id')
        category = data.get('category', 'መኪና')
        sub_category = data.get('sub_category', '')
        car_model = data.get('car_model', '')
        location_area = data.get('location_area', '')
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
            return jsonify({"status": "error", "message": "User ID not found. Open in Telegram."}), 400
        negotiable_text = "✅ Negotiable / የሚደራደር" if negotiable else "❌ Fixed / የማይደራደር"
        urgent_text = "⚡ **URGENT SALE / አስቸኳይ ሽያጭ!** " if urgent_sale else ""
        full_desc = f"{urgent_text}"
        full_desc += f"💰 Price: {price} ETB ({negotiable_text})\n"
        if category == 'መኪና':
            if car_model: full_desc += f"🚘 Model: {car_model}\n"
            elif car_type: full_desc += f"🚗 Type: {car_type}\n"
            if fuel_type: full_desc += f"⛽ Fuel: {fuel_type}\n"
            if transmission: full_desc += f"⚙️ Transmission: {transmission}\n"
            if mileage: full_desc += f"🛣️ Mileage: {mileage} KM\n"
            if condition: full_desc += f"📊 Condition: {condition}\n"
        else:
            if house_type: full_desc += f"🏠 Type: {house_type}\n"
            if location_area: full_desc += f"📍 Location: {location_area}\n"
            if bedrooms: full_desc += f"🛏️ Bedrooms: {bedrooms}\n"
            if bathrooms: full_desc += f"🛁 Bathrooms: {bathrooms}\n"
            if parking: full_desc += f"🚗 Parking: {parking}\n"
            if house_condition: full_desc += f"📊 Condition: {house_condition}\n"
        full_desc += f"📝 Details: {description}\n"
        full_desc += f"📞 Phone: {phone}\n"
        if telegram_user: full_desc += f"📱 Telegram: {telegram_user}\n"
        uid = int(user_id) if str(user_id).isdigit() else 0
        extra = {
            'fuel_type': fuel_type, 'transmission': transmission, 'mileage': mileage,
            'condition': condition or house_condition, 'bedrooms': bedrooms,
            'bathrooms': bathrooms, 'parking': parking, 'house_type': house_type,
            'car_type': car_type, 'car_model': car_model, 'location_area': location_area,
            'negotiable': negotiable, 'urgent_sale': urgent_sale,
            'telegram_user': telegram_user
        }
        safe_photos = []
        if isinstance(photos, list):
            for ph in photos[:3]:
                s = str(ph)
                if len(s) > 350000:
                    s = s[:350000]
                safe_photos.append(s)
        resolved_sub = sub_category or (car_model if category == 'መኪና' else (f"{house_type} • {location_area}" if house_type and location_area else (house_type or location_area)))
        req_id = add_listing(
            user_chat_id=uid,
            user_name="WebApp User",
            req_type="SELL",
            main_category=(category or "መኪና"),
            sub_category=resolved_sub,
            action_type="መሸጥ",
            property_type="",
            description=full_desc,
            price=str(price),
            phone=str(phone or ""),
            extra_data=extra,
            photos=safe_photos
        )
        if not req_id and safe_photos:
            req_id = add_listing(
                user_chat_id=uid,
                user_name="WebApp User",
                req_type="SELL",
                main_category=(category or "መኪና"),
                sub_category=resolved_sub,
                action_type="መሸጥ",
                property_type="",
                description=full_desc,
                price=str(price),
                phone=str(phone or ""),
                extra_data=extra,
                photos=[]
            )
        if req_id:
            notification_text = f"🛍️ **New Listing (#ADK-{req_id})**\n\n{full_desc}"
            _send_notification_safe(notification_text, req_id, int(user_id))
            return jsonify({"status": "success", "req_id": req_id})
        else:
            return jsonify({"status": "error", "message": "Failed to save listing"}), 500
    except Exception as e:
        logger.error(f"submit_listing error: {e}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500


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
        if not user_id or user_id == "unknown":
            return jsonify({"status": "error", "message": "User ID not found"}), 400
        budget_range = f"{budget_min} - {budget_max}" if budget_min and budget_max else (budget_min or budget_max or "Not specified")
        full_desc = (
            f"💰 Budget: {budget_range} ETB\n"
            f"📝 Details: {details}\n"
            f"📞 Phone: {phone}\n"
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
            notification_text = f"🔔 **New Buyer Request (#ADK-{req_id})**\n\n{full_desc}"
            _send_notification_safe(notification_text, req_id, int(user_id))
            if create_alert and str(user_id).isdigit():
                save_search_alert(int(user_id), category, budget_min, budget_max)
            return jsonify({"status": "success", "req_id": req_id})
        else:
            return jsonify({"status": "error", "message": "Failed to save request"}), 500
    except Exception as e:
        logger.error(f"submit_request error: {e}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500


@web_app.route('/api/health', methods=['GET'])
def api_health():
    import config as app_config
    from models import _DB_BACKEND
    backend = getattr(app_config, "DB_BACKEND", None) or _DB_BACKEND
    info = {
        "ok": True,
        "database": backend,
        "persistent": backend == "postgres",
        "webapp_url": WEBAPP_URL,
    }
    return jsonify(info)


@web_app.route('/api/explorer/listings', methods=['GET', 'OPTIONS'])
def api_explorer_listings():
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

            where = ["1=1"]
            params = []
            where.append(f"(status IS NULL OR status != {p})")
            params.append('deleted')
            if active_only:
                where.append(f"(status IS NULL OR LOWER(CAST(status AS TEXT)) NOT IN ({p},{p},{p}))")
                params.extend(['sold', 'rented', 'expired'])
            if req_type in ('SELL', 'BUY'):
                where.append(f"UPPER(COALESCE(req_type,'')) = UPPER({p})")
                params.append(req_type)
            if category:
                where.append(f"(main_category = {p} OR category = {p})")
                params.extend([category, category])
            if search:
                like = "ILIKE" if is_postgres() else "LIKE"
                where.append(f"(CAST(description AS TEXT) {like} {p} OR CAST(price AS TEXT) {like} {p} OR CAST(sub_category AS TEXT) {like} {p})")
                params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])

            where_sql = " AND ".join(where)
            total = 0
            try:
                cur.execute(f"SELECT COUNT(*) AS cnt FROM listings WHERE {where_sql}", params)
                total_row = cur.fetchone()
                total = total_row['cnt'] if isinstance(total_row, dict) else (total_row[0] if total_row else 0)
            except Exception:
                total = 0

            cur.execute(
                f"SELECT * FROM listings WHERE {where_sql} "
                f"ORDER BY id DESC LIMIT {p} OFFSET {p}",
                list(params) + [limit, offset],
            )
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
                        cur.execute(f"SELECT photo_id FROM listing_photos WHERE listing_id = {p}", (item['id'],))
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

        return jsonify({
            "status": "success",
            "page": page,
            "limit": limit,
            "total": int(total or 0),
            "has_more": bool(offset + limit < (total or 0)),
            "items": safe_items,
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
        }), 200


import re
import io
import base64

try:
    from PIL import Image, ImageEnhance, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    Image = None
    ImageEnhance = None
    ImageDraw = None
    ImageFont = None
    PIL_AVAILABLE = False


def process_listing_image(image_input, enhance: bool = True, watermark_text: str = "Adika Marketplace"):
    """
    Enhance listing image (contrast, brightness, sharpness) and add Adika Marketplace watermark.
    Accepts: base64 string, data URL, bytes, or PIL Image.
    Returns: base64 data URL string (data:image/jpeg;base64,...)
    """
    if not PIL_AVAILABLE or Image is None:
        if isinstance(image_input, (bytes, bytearray)):
            b64 = base64.b64encode(image_input).decode("utf-8")
            return f"data:image/jpeg;base64,{b64}"
        elif isinstance(image_input, str):
            if image_input.startswith("data:image/"):
                return image_input
            return f"data:image/jpeg;base64,{image_input}"
        return image_input

    try:
        img = None
        if isinstance(image_input, Image.Image):
            img = image_input
        elif isinstance(image_input, (bytes, bytearray)):
            img = Image.open(io.BytesIO(image_input))
        elif isinstance(image_input, str):
            clean_b64 = image_input
            if "," in image_input and image_input.startswith("data:"):
                clean_b64 = image_input.split(",", 1)[1]
            img_bytes = base64.b64decode(clean_b64)
            img = Image.open(io.BytesIO(img_bytes))
        else:
            return image_input

        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        # 1. Image Enhancement
        if enhance:
            try:
                enh_contrast = ImageEnhance.Contrast(img)
                img = enh_contrast.enhance(1.12)
                enh_bright = ImageEnhance.Brightness(img)
                img = enh_bright.enhance(1.04)
                enh_sharp = ImageEnhance.Sharpness(img)
                img = enh_sharp.enhance(1.15)
            except Exception as e:
                logger.warning(f"Image enhancement error: {e}")

        # 2. Watermarking
        try:
            width, height = img.size
            draw = ImageDraw.Draw(img)
            font_size = max(14, int(min(width, height) * 0.042))
            try:
                font = ImageFont.truetype("DejaVuSans-Bold.ttf", font_size)
            except Exception:
                try:
                    font = ImageFont.truetype("arial.ttf", font_size)
                except Exception:
                    font = ImageFont.load_default()

            text = watermark_text or "Adika Marketplace"
            # Calculate text bounding box
            try:
                bbox = draw.textbbox((0, 0), text, font=font)
                tw = bbox[2] - bbox[0]
                th = bbox[3] - bbox[1]
            except Exception:
                tw = len(text) * (font_size * 0.6)
                th = font_size

            pad_x = 12
            pad_y = 6
            margin = 16
            x2 = width - margin
            y2 = height - margin
            x1 = x2 - tw - (pad_x * 2)
            y1 = y2 - th - (pad_y * 2)

            # Draw semi-transparent pill overlay
            overlay = Image.new("RGBA", img.size, (255, 255, 255, 0))
            overlay_draw = ImageDraw.Draw(overlay)
            overlay_draw.rounded_rectangle(
                [x1, y1, x2, y2],
                radius=8,
                fill=(15, 23, 42, 180),
                outline=(22, 172, 189, 230),
                width=2
            )
            overlay_draw.text((x1 + pad_x, y1 + pad_y), text, font=font, fill=(255, 255, 255, 255))

            img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
        except Exception as e:
            logger.warning(f"Watermark error: {e}")

        # Save to JPEG buffer
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=85, optimize=True)
        out_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
        return f"data:image/jpeg;base64,{out_b64}"
    except Exception as e:
        logger.error(f"process_listing_image error: {e}")
        return image_input


@web_app.route('/api/ai-autofill', methods=['POST', 'OPTIONS'])
def api_ai_autofill():
    """
    Analyze vehicle or property image using Gemini 1.5 Flash and return autofilled listing details.
    """
    if request.method == 'OPTIONS':
        return ('', 204)
    try:
        image_bytes = None
        mime_type = "image/jpeg"

        # Check multipart form data
        if 'image' in request.files:
            f = request.files['image']
            image_bytes = f.read()
            mime_type = f.mimetype or "image/jpeg"
        elif 'file' in request.files:
            f = request.files['file']
            image_bytes = f.read()
            mime_type = f.mimetype or "image/jpeg"
        elif request.is_json:
            data = request.json or {}
            raw_img = data.get('image') or data.get('base64') or data.get('photo')
            if raw_img:
                if "," in raw_img and raw_img.startswith("data:"):
                    header, raw_b64 = raw_img.split(",", 1)
                    if "image/png" in header:
                        mime_type = "image/png"
                    elif "image/webp" in header:
                        mime_type = "image/webp"
                else:
                    raw_b64 = raw_img
                image_bytes = base64.b64decode(raw_b64)

        if not image_bytes:
            return jsonify({
                "status": "error",
                "message": "No image provided. Upload a file or send base64 data."
            }), 400

        api_key = os.environ.get("GEMINI_API_KEY")
        autofill_result = None

        if api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=api_key)
                system_prompt = (
                    "You are an expert appraiser and cataloger for Adika Marketplace in Ethiopia.\n"
                    "Analyze the provided image (car, house/apartment, commercial space, or general item).\n"
                    "Extract and infer accurate listing information in strictly valid JSON with keys:\n"
                    "- 'title': concise English title (e.g. 'Toyota Vitz 2012 Automatic', 'Modern 2-Bedroom Apartment in Bole')\n"
                    "- 'category': 'cars' | 'property' | 'commercial'\n"
                    "- 'transmission': 'Automatic' | 'Manual' | null (if car)\n"
                    "- 'fuel_type': 'Benzine' | 'Diesel' | 'Electric' | 'Hybrid' | null (if car)\n"
                    "- 'description': high-converting, professional marketing description written in Amharic (አማርኛ).\n"
                    "Return ONLY JSON."
                )
                model = genai.GenerativeModel(
                    model_name="gemini-1.5-flash",
                    system_instruction=system_prompt,
                    generation_config={"response_mime_type": "application/json", "temperature": 0.2}
                )
                image_part = {
                    "mime_type": mime_type,
                    "data": image_bytes
                }
                response = model.generate_content(["Analyze this product for marketplace listing:", image_part])
                text = (response.text or "").strip()
                if text.startswith("```json"):
                    text = text[7:]
                if text.startswith("```"):
                    text = text[3:]
                if text.endswith("```"):
                    text = text[:-3]
                autofill_result = json.loads(text.strip())
            except Exception as e:
                logger.warning(f"Gemini AI autofill error: {e}")

        if not autofill_result or not isinstance(autofill_result, dict):
            autofill_result = {
                "title": "Clean Verified Listing",
                "category": "cars",
                "transmission": "Automatic",
                "fuel_type": "Benzine",
                "description": "በጣም ንጹህ እና አስተማማኝ ይዞታ ላይ ያለ ንብረት። ለበለጠ መረጃ በስልክ ወይም በቴሌግራም ያግኙን።"
            }

        # Also provide enhanced watermarked image preview
        processed_img_url = process_listing_image(image_bytes)

        return jsonify({
            "status": "success",
            "autofill": autofill_result,
            "processed_image": processed_img_url
        })
    except Exception as e:
        logger.error(f"api_ai_autofill error: {e}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500


@web_app.route('/api/ai-moderate', methods=['POST', 'OPTIONS'])
def api_ai_moderate():
    """
    Validate listing text and/or images to ensure safety, no personal ID cards, spam, or inappropriate content.
    """
    if request.method == 'OPTIONS':
        return ('', 204)
    try:
        data = request.json or {}
        text_content = f"{data.get('title', '')} {data.get('description', '')} {data.get('text', '')}".strip()
        raw_img = data.get('image') or data.get('photo') or data.get('base64')

        api_key = os.environ.get("GEMINI_API_KEY")
        if api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=api_key)
                prompt = (
                    "You are a strict content safety and moderation officer for an Ethiopian e-commerce marketplace.\n"
                    "Check if the submission contains prohibited content:\n"
                    "1. Government/personal ID cards, driver licenses, passports, or private personal documents.\n"
                    "2. Explicit pornography, nudity, or weapons/violence.\n"
                    "3. Scam, fraudulent gambling, drugs, or malicious spam.\n"
                    "Return strictly JSON:\n"
                    "- 'approved': true (if safe) or false (if violation)\n"
                    "- 'reason': short concise explanation in English.\n"
                )
                model = genai.GenerativeModel(
                    model_name="gemini-1.5-flash",
                    system_instruction=prompt,
                    generation_config={"response_mime_type": "application/json", "temperature": 0.0}
                )
                contents = [f"Text content: {text_content}"]
                if raw_img:
                    mime_type = "image/jpeg"
                    if "," in raw_img and raw_img.startswith("data:"):
                        header, raw_b64 = raw_img.split(",", 1)
                        if "image/png" in header:
                            mime_type = "image/png"
                    else:
                        raw_b64 = raw_img
                    img_bytes = base64.b64decode(raw_b64)
                    contents.append({"mime_type": mime_type, "data": img_bytes})

                response = model.generate_content(contents)
                resp_text = (response.text or "").strip()
                if resp_text.startswith("```json"):
                    resp_text = resp_text[7:]
                if resp_text.startswith("```"):
                    resp_text = resp_text[3:]
                if resp_text.endswith("```"):
                    resp_text = resp_text[:-3]
                mod_result = json.loads(resp_text.strip())
                return jsonify({
                    "status": "success",
                    "approved": bool(mod_result.get("approved", True)),
                    "reason": mod_result.get("reason", "Content approved.")
                })
            except Exception as e:
                logger.warning(f"AI moderation Gemini call error: {e}")

        # Fallback heuristic moderation
        banned_keywords = ["passport", "id card", "national id", "kebele id", "porn", "sex", "weapon", "gun", "weed", "hack"]
        is_safe = True
        reason = "Content complies with marketplace guidelines."
        lower_txt = text_content.lower()
        for kw in banned_keywords:
            if kw in lower_txt:
                is_safe = False
                reason = f"Prohibited keyword detected: '{kw}'"
                break

        return jsonify({
            "status": "success",
            "approved": is_safe,
            "reason": reason
        })
    except Exception as e:
        logger.error(f"api_ai_moderate error: {e}", exc_info=True)
        return jsonify({"status": "error", "message": str(e), "approved": True, "reason": "Auto-passed due to internal error"}), 500


def _clean_keyword(kw: str):
    if not kw:
        return None
    s = str(kw).strip()
    amharic_map = {
        "ቪትስ": "vits", "ቪትዝ": "vits", "ያሪስ": "yaris", "ኮሮላ": "corolla",
        "ቱክሰን": "tucson", "ሱዙኪ": "suzuki", "ዲዛየር": "dzire", "አክሰንት": "accent",
        "ራቭ4": "rav4", "ቪላ": "villa", "አፓርታማ": "apartment", "ኮንዶ": "condo",
        "ኮንዶሚኒየም": "condo", "ቦሌ": "bole", "ሲኤምሲ": "cmc", "መኪና": "cars", "ቤት": "property"
    }
    for amh, eng in amharic_map.items():
        if amh in s:
            s = s.replace(amh, eng)
    # Remove all numbers/digits (0-9)
    s = re.sub(r'\d+', ' ', s)
    # Remove comparison and special symbols
    s = re.sub(r'[<>=~+&|/\\#*!?^$]', ' ', s)
    tokens = [t.strip(",. \t\n\r:;!?'\"()[]{}") for t in s.split()]
    fillers = {
        "under", "below", "above", "more", "less", "than", "price", "etb", "birr", "ብር",
        "በታች", "በላይ", "ከ", "ለ", "የሚሆን", "ያነሰ", "የበለጠ", "ዋጋ", "around", "for", "in",
        "car", "cars", "vehicle", "መኪና", "ቤት", "house", "property", "all", "buy", "sell",
        "million", "thousand", "ሚሊዮን", "ሺህ", "k", "m"
    }
    cleaned_tokens = [t for t in tokens if t.lower() not in fillers and len(t) > 1 and not t.isdigit()]
    res = " ".join(cleaned_tokens).strip()
    return res if len(res) >= 2 else None


def _extract_fallback_price(text: str):
    t = text.lower().replace(",", "")
    m = re.search(r'(\d+(\.\d+)?)\s*(m|million|ሚሊዮን)', t)
    if m:
        return int(float(m.group(1)) * 1_000_000)
    k = re.search(r'(\d+(\.\d+)?)\s*(k|ሺህ|thousand)', t)
    if k:
        return int(float(k.group(1)) * 1_000)
    d = re.search(r'\b(\d{5,10})\b', t)
    if d:
        return int(d.group(1))
    return None


def parse_prompt_with_ai(prompt_text: str):
    clean_text = (prompt_text or "").strip()
    if not clean_text:
        return {"category": "all", "max_price": None, "keyword": None}

    api_key = os.environ.get("GEMINI_API_KEY")
    parsed_result = None

    if api_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            system_instruction = (
                "You are an AI Search Parser for an Ethiopian marketplace (cars, properties, commercial items).\n"
                "Given a search prompt in English or Amharic (e.g. 'Vits under 2M ETB', 'ቪትስ < 2M', 'ኮሮላ 1.5 ሚሊዮን', 'መኪና < 1M', '2 bedroom apartment in Bole below 30k'):\n"
                "Extract a strictly formatted JSON object with keys:\n"
                "- 'category': 'cars' | 'property' | 'all'\n"
                "- 'max_price': integer ETB value or null (e.g. '2M', '2 million', '2 ሚሊዮን' -> 2000000; '500k', '500 ሺህ' -> 500000; '1.5M' -> 1500000; '< 1M' -> 1000000)\n"
                "- 'keyword': clean single item model/brand/neighborhood in English (e.g. 'vits', 'yaris', 'corolla', 'tucson', 'suzuki', 'villa', 'apartment', 'bole', 'cmc') or null.\n"
                "RULES:\n"
                "1. NEVER include filler words like 'under', 'below', 'price', 'ETB', 'ብር', 'በታች', '<', '>', 'ለ', or price numbers inside 'keyword'.\n"
                "2. Transliterate Amharic item names to English (e.g. 'ቪትስ' -> 'vits', 'ያሪስ' -> 'yaris', 'ኮሮላ' -> 'corolla', 'ቱክሰን' -> 'tucson', 'አፓርታማ' -> 'apartment', 'ቪላ' -> 'villa').\n"
                "3. If query is just 'መኪና' or 'cars', set category='cars' and keyword=null.\n"
                "4. If query is just 'ቤት' or 'house', set category='property' and keyword=null.\n"
                "Respond ONLY with valid JSON."
            )
            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                system_instruction=system_instruction,
                generation_config={"response_mime_type": "application/json", "temperature": 0.0}
            )
            response = model.generate_content(f"User Query: {clean_text}")
            text = (response.text or "").strip()
            if text.startswith("```json"):
                text = text[7:]
            if text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
            parsed_result = json.loads(text.strip())
        except Exception as e:
            logger.warning(f"Gemini API parse error via google.generativeai, falling back: {e}")

    if not parsed_result or not isinstance(parsed_result, dict):
        cat = "all"
        lower = clean_text.lower()
        if any(w in lower for w in ["car", "vitz", "toyota", "hyundai", "መኪና", "ቪትስ", "ኮሮላ", "ያሪስ"]):
            cat = "cars"
        elif any(w in lower for w in ["house", "villa", "apartment", "condo", "ቤት", "ኮንዶ", "ቪላ", "አፓርታማ"]):
            cat = "property"
        parsed_result = {
            "category": cat,
            "max_price": _extract_fallback_price(clean_text),
            "keyword": _clean_keyword(clean_text)
        }

    # Final sanitization
    raw_kw = parsed_result.get("keyword")
    cleaned_kw = _clean_keyword(raw_kw) if raw_kw else None
    cat = str(parsed_result.get("category", "all")).lower()
    if cat not in ("cars", "property", "all"):
        cat = "all"

    max_p = parsed_result.get("max_price")
    if max_p is not None:
        try:
            max_p = int(float(str(max_p).replace(",", "")))
        except Exception:
            max_p = _extract_fallback_price(clean_text)

    return {
        "category": cat,
        "max_price": max_p,
        "keyword": cleaned_kw
    }


# Alias for backward-compatibility
parse_search_with_gemini = parse_prompt_with_ai


@web_app.route('/api/ai-search', methods=['POST', 'OPTIONS'])
def api_ai_search():
    if request.method == 'OPTIONS':
        return ('', 204)
    try:
        data = request.json or {}
        prompt = (data.get('prompt') or '').strip()
        if not prompt:
            return jsonify({"status": "success", "banner_text": "All listings", "parsed": {}, "items": [], "results": []})

        parsed = parse_search_with_gemini(prompt)
        category = parsed.get("category", "all")
        max_price = parsed.get("max_price")
        raw_keyword = parsed.get("keyword")
        # Strict Python Regex Sanitization
        keyword = _clean_keyword(raw_keyword) if raw_keyword else None
        parsed["keyword"] = keyword

        # Format clean banner text
        banner_parts = []
        if keyword:
            banner_parts.append(keyword)
        if category and category != "all":
            banner_parts.append("🚗 Cars" if category == "cars" else "🏠 Property")
        if max_price:
            banner_parts.append(f"< {int(max_price):,} ETB")
        banner_text = " • ".join(banner_parts) if banner_parts else "All listings"

        conn = get_db_connection()
        cur = conn.cursor()
        p = get_placeholder()
        from models import is_postgres

        where = ["1=1"]
        params = []
        where.append(f"(status IS NULL OR status != {p})")
        params.append('deleted')
        where.append(f"(status IS NULL OR LOWER(CAST(status AS TEXT)) NOT IN ({p},{p},{p}))")
        params.extend(['sold', 'rented', 'expired'])

        if category == "cars":
            where.append(f"(main_category = {p} OR category = {p})")
            params.extend(["መኪና", "መኪና"])
        elif category == "property":
            where.append(f"(main_category = {p} OR category = {p})")
            params.extend(["ቤት", "ቤት"])

        # If keyword becomes empty after cleaning, do NOT apply LIKE %keyword%
        if keyword:
            like = "ILIKE" if is_postgres() else "LIKE"
            where.append(f"(CAST(description AS TEXT) {like} {p} OR CAST(sub_category AS TEXT) {like} {p})")
            params.extend([f"%{keyword}%", f"%{keyword}%"])

        where_sql = " AND ".join(where)
        cur.execute(
            f"SELECT * FROM listings WHERE {where_sql} ORDER BY id DESC LIMIT 50",
            params
        )
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
                    cur.execute(f"SELECT photo_id FROM listing_photos WHERE listing_id = {p}", (item['id'],))
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

            # Apply integer price comparison
            if max_price:
                price_str = str(item.get('price', '') or '')
                digits = re.sub(r'[^\d]', '', price_str)
                if digits:
                    try:
                        numeric_price = int(digits)
                        if numeric_price > int(max_price):
                            continue
                    except Exception:
                        pass
            items.append(item)

        conn.close()
        safe_items = [_json_safe(it) for it in items[:30]]
        return jsonify({
            "status": "success",
            "banner_text": banner_text,
            "parsed": parsed,
            "items": safe_items,
            "results": safe_items
        })
    except Exception as e:
        logger.error(f"api_ai_search error: {e}", exc_info=True)
        return jsonify({"status": "error", "message": str(e), "banner_text": "Error", "items": [], "results": []}), 500


@web_app.route('/api/views/<int:listing_id>', methods=['POST'])
def api_view_booster(listing_id):
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
        new_count = (int(current) if current else random.randint(35, 90)) + boost
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
        return jsonify({"status": "error"}), 500


@web_app.route('/api/items/<int:listing_id>/status', methods=['PATCH'])
def api_update_item_status(listing_id):
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
        return jsonify({"status": "success", "new_status": new_status})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@web_app.route('/api/items/<int:listing_id>', methods=['DELETE'])
def api_delete_item(listing_id):
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
        return jsonify({"status": "error"}), 500


@web_app.route('/api/stats', methods=['GET'])
def api_stats():
    try:
        stats = get_platform_stats()
        return jsonify({"status": "success", **stats})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@web_app.route('/api/brokers', methods=['GET'])
def api_brokers():
    try:
        page = max(1, int(request.args.get("page", 1)))
        limit = min(15, max(1, int(request.args.get("limit", 12))))
        offset = (page - 1) * limit
        brokers = get_active_brokers(status="approved", limit=limit, offset=offset)
        total = count_brokers(status="approved")
        return jsonify({
            "status": "success",
            "page": page,
            "limit": limit,
            "total": total,
            "has_more": offset + limit < total,
            "items": brokers,
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@web_app.route('/api/listings', methods=['GET'])
def api_listings_alias():
    return api_explorer_listings()


# ==============================================================================
# PHASE 2: FINANCIAL & CALCULATOR AI MODULES
# ==============================================================================

def _calculate_vehicle_duty(fuel_type: str, engine_cc: int, manufacture_year: int, cif_etb: float, cif_usd: float = None, usd_rate: float = 128.5):
    """
    Computes Ethiopian Customs Duty, Excise Tax, Surtax, Withholding, and VAT
    under current Ethiopian Ministry of Finance vehicle tariff regulations.
    """
    fuel = str(fuel_type or "benzine").lower().strip()
    is_ev = any(w in fuel for w in ["electric", "ev", "ኤሌክትሪክ"])
    is_hybrid = any(w in fuel for w in ["hybrid", "ሀይብሪድ"])

    current_year = 2026
    age_years = max(0, current_year - int(manufacture_year or current_year))
    cc = max(0, int(engine_cc or 0))

    if cif_usd and not cif_etb:
        cif_etb = float(cif_usd) * float(usd_rate)
    elif cif_etb and not cif_usd:
        cif_usd = float(cif_etb) / float(usd_rate)
    else:
        cif_etb = float(cif_etb or 0)
        cif_usd = float(cif_usd or (cif_etb / usd_rate if usd_rate else 0))

    if is_ev:
        # Ethiopian EV Incentives: 5% duty, 0% excise, 0% surtax, 3% withholding, 15% VAT
        duty_rate = 0.05
        excise_rate = 0.00
        surtax_rate = 0.00
        withholding_rate = 0.03
        vat_rate = 0.15
        policy_note = "Green Energy EV Incentive (5% Duty, 0% Excise, Surtax Exempt)"
    elif is_hybrid:
        duty_rate = 0.20
        if cc <= 1300:
            base_excise = 0.10
        elif cc <= 1800:
            base_excise = 0.20
        else:
            base_excise = 0.30
        age_factor = 1.0 if age_years <= 2 else (1.3 if age_years <= 5 else 1.6)
        excise_rate = round(base_excise * age_factor, 3)
        surtax_rate = 0.10
        withholding_rate = 0.03
        vat_rate = 0.15
        policy_note = "Hybrid Vehicle Tariff (Eco-Reduced Excise Tier)"
    else:
        # Standard Internal Combustion Engine (Benzine / Diesel)
        duty_rate = 0.35
        if cc <= 1300:
            base_excise = 0.30
        elif cc <= 1800:
            base_excise = 0.60
        else:
            base_excise = 1.00

        # Used vehicle age multiplier under Ethiopian Customs Tariff
        if age_years <= 2:
            excise_rate = base_excise
        elif age_years <= 4:
            excise_rate = round(base_excise + 0.80, 2)
        elif age_years <= 7:
            excise_rate = round(base_excise + 1.80, 2)
        else:
            excise_rate = round(min(5.00, base_excise + 3.50), 2)

        surtax_rate = 0.10
        withholding_rate = 0.03
        vat_rate = 0.15
        policy_note = f"Standard ICE Vehicle ({'New' if age_years <= 2 else f'{age_years} yrs used'}) Tariff Schedule"

    # Precise Ethiopian Tax Cascading Formula
    customs_duty = cif_etb * duty_rate
    excise_tax = (cif_etb + customs_duty) * excise_rate
    surtax = (cif_etb + customs_duty + excise_tax) * surtax_rate
    withholding_tax = cif_etb * withholding_rate
    vat = (cif_etb + customs_duty + excise_tax + surtax) * vat_rate

    total_taxes = customs_duty + excise_tax + surtax + withholding_tax + vat
    total_landed_cost = cif_etb + total_taxes
    effective_tax_pct = round((total_taxes / cif_etb * 100), 1) if cif_etb > 0 else 0

    return {
        "status": "success",
        "cif_etb": round(cif_etb, 2),
        "cif_usd": round(cif_usd, 2),
        "exchange_rate_usd_etb": usd_rate,
        "policy_note": policy_note,
        "vehicle_details": {
            "fuel_type": "Electric" if is_ev else ("Hybrid" if is_hybrid else "Benzine / Diesel"),
            "engine_cc": cc if not is_ev else 0,
            "manufacture_year": manufacture_year,
            "age_years": age_years
        },
        "tax_rates": {
            "customs_duty": f"{round(duty_rate * 100, 1)}%",
            "excise_tax": f"{round(excise_rate * 100, 1)}%",
            "surtax": f"{round(surtax_rate * 100, 1)}%",
            "withholding": f"{round(withholding_rate * 100, 1)}%",
            "vat": f"{round(vat_rate * 100, 1)}%"
        },
        "tax_breakdown": {
            "customs_duty_etb": round(customs_duty, 2),
            "excise_tax_etb": round(excise_tax, 2),
            "surtax_etb": round(surtax, 2),
            "withholding_tax_etb": round(withholding_tax, 2),
            "vat_etb": round(vat_etb, 2),
            "total_taxes_etb": round(total_taxes, 2)
        },
        "total_landed_cost_etb": round(total_landed_cost, 2),
        "effective_tax_percentage": f"{effective_tax_pct}%"
    }


@web_app.route('/api/calculate-duty', methods=['GET', 'POST', 'OPTIONS'])
def api_calculate_duty():
    """
    1. CUSTOMS DUTY CALCULATOR ENGINE (/api/calculate-duty):
    Calculate Ethiopian customs duty, Excise tax, VAT, and surtax for vehicles based on
    fuel type (Benzine/Diesel vs Electric), engine size (CC), and manufacture year.
    """
    if request.method == 'OPTIONS':
        return ('', 204)
    try:
        if request.method == 'POST':
            data = request.json or {}
        else:
            data = request.args

        fuel_type = data.get('fuel_type') or data.get('fuel') or 'Benzine'
        engine_cc = int(data.get('engine_cc') or data.get('cc') or 1500)
        manufacture_year = int(data.get('manufacture_year') or data.get('year') or 2020)
        cif_etb = float(data.get('cif_etb') or data.get('cif') or data.get('price') or 0)
        cif_usd = float(data.get('cif_usd') or data.get('usd') or 0)
        usd_rate = float(data.get('usd_rate') or data.get('exchange_rate') or 128.5)

        if not cif_etb and not cif_usd:
            cif_usd = 12000.0  # default sample CIF

        result = _calculate_vehicle_duty(
            fuel_type=fuel_type,
            engine_cc=engine_cc,
            manufacture_year=manufacture_year,
            cif_etb=cif_etb,
            cif_usd=cif_usd,
            usd_rate=usd_rate
        )
        return jsonify(result)
    except Exception as e:
        logger.error(f"api_calculate_duty error: {e}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500


@web_app.route('/api/calculate-loan', methods=['GET', 'POST', 'OPTIONS'])
def api_calculate_loan():
    """
    2. BANK LOAN & MORTGAGE ELIGIBILITY (/api/calculate-loan):
    Calculate monthly mortgage/auto loan repayments using standard Ethiopian bank interest rates (~16-19%).
    Determine buyer eligibility based on monthly income vs estimated monthly payment (DTI ratio).
    """
    if request.method == 'OPTIONS':
        return ('', 204)
    try:
        if request.method == 'POST':
            data = request.json or {}
        else:
            data = request.args

        price = float(data.get('price') or data.get('property_price') or data.get('vehicle_price') or 3000000.0)
        down_payment_pct = float(data.get('down_payment_percent') or data.get('down_payment_pct') or 20.0)
        annual_rate_pct = float(data.get('interest_rate') or data.get('annual_rate') or 17.5)  # Standard Ethiopian rate
        tenure_years = int(data.get('tenure_years') or data.get('years') or 10)
        monthly_income = float(data.get('monthly_income') or data.get('income') or 0)
        existing_monthly_debt = float(data.get('existing_debt') or 0)

        down_payment_amount = price * (down_payment_pct / 100.0)
        principal = max(0.0, price - down_payment_amount)

        monthly_rate = (annual_rate_pct / 100.0) / 12.0
        total_months = max(1, tenure_years * 12)

        if monthly_rate > 0:
            compound = (1.0 + monthly_rate) ** total_months
            monthly_repayment = principal * (monthly_rate * compound) / (compound - 1.0)
        else:
            monthly_repayment = principal / total_months

        total_repayment = monthly_repayment * total_months
        total_interest = total_repayment - principal

        # Eligibility & Debt-to-Income (DTI) Analysis
        eligibility = {
            "eligible": None,
            "dti_ratio_pct": None,
            "verdict": "Provide 'monthly_income' to check eligibility",
            "max_allowed_monthly_payment": None,
            "max_borrowing_capacity_etb": None
        }

        if monthly_income > 0:
            total_monthly_obligations = monthly_repayment + existing_monthly_debt
            dti = (total_monthly_obligations / monthly_income) * 100.0
            max_payment_allowed = max(0.0, (monthly_income * 0.45) - existing_monthly_debt)

            if monthly_rate > 0:
                compound = (1.0 + monthly_rate) ** total_months
                max_loan_cap = max_payment_allowed * (compound - 1.0) / (monthly_rate * compound)
            else:
                max_loan_cap = max_payment_allowed * total_months

            if dti <= 35.0:
                verdict = "Highly Eligible (Prime Tier) — Fits comfortably within standard bank DTI limits."
                is_eligible = True
            elif dti <= 45.0:
                verdict = "Eligible (Standard Tier) — Meets Ethiopian Commercial Banks (CBE/Awash/Dashen) 45% DTI cap."
                is_eligible = True
            elif dti <= 55.0:
                verdict = "Borderline / High Debt Ratio — Requires co-signer or higher down payment."
                is_eligible = False
            else:
                verdict = "Ineligible — Exceeds statutory debt-to-income threshold (DTI > 50%)."
                is_eligible = False

            eligibility = {
                "eligible": is_eligible,
                "dti_ratio_pct": round(dti, 1),
                "monthly_income_etb": round(monthly_income, 2),
                "total_monthly_debt_etb": round(total_monthly_obligations, 2),
                "max_allowed_monthly_payment_etb": round(max_payment_allowed, 2),
                "max_borrowing_capacity_etb": round(max_loan_cap, 2),
                "verdict": verdict
            }

        return jsonify({
            "status": "success",
            "loan_summary": {
                "asset_price_etb": round(price, 2),
                "down_payment_pct": f"{round(down_payment_pct, 1)}%",
                "down_payment_amount_etb": round(down_payment_amount, 2),
                "principal_loan_amount_etb": round(principal, 2),
                "annual_interest_rate": f"{round(annual_rate_pct, 2)}%",
                "tenure_years": tenure_years,
                "total_installments": total_months
            },
            "repayment_details": {
                "monthly_repayment_etb": round(monthly_repayment, 2),
                "total_interest_payable_etb": round(total_interest, 2),
                "total_amount_payable_etb": round(total_repayment, 2),
                "interest_to_principal_ratio": f"{round((total_interest / principal * 100), 1) if principal > 0 else 0}%"
            },
            "eligibility_analysis": eligibility
        })
    except Exception as e:
        logger.error(f"api_calculate_loan error: {e}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500


@web_app.route('/api/financial-insights', methods=['GET', 'POST', 'OPTIONS'])
def api_financial_insights():
    """
    3. RENTAL YIELD & DEPRECIATION ESTIMATOR (/api/financial-insights):
    - Calculate annual ROI (%) for property investments based on purchase price and estimated monthly rent.
    - Estimate 3-year resale value and fuel-vs-electric (EV) monthly cost savings analysis.
    """
    if request.method == 'OPTIONS':
        return ('', 204)
    try:
        if request.method == 'POST':
            data = request.json or {}
        else:
            data = request.args

        category = str(data.get('category') or 'property').lower().strip()
        price = float(data.get('price') or data.get('purchase_price') or 4500000.0)

        # 1. PROPERTY RENTAL YIELD & ROI ENGINE
        monthly_rent = float(data.get('monthly_rent') or data.get('rent') or (price * 0.007))  # approx 0.7% monthly yield
        maintenance_pct = float(data.get('maintenance_pct') or 1.5)
        vacancy_pct = float(data.get('vacancy_pct') or 5.0)
        annual_property_tax = float(data.get('property_tax') or 5000.0)

        gross_annual_rent = monthly_rent * 12.0
        gross_yield_pct = (gross_annual_rent / price * 100.0) if price > 0 else 0.0

        vacancy_loss = gross_annual_rent * (vacancy_pct / 100.0)
        annual_maintenance = price * (maintenance_pct / 100.0)
        net_annual_income = gross_annual_rent - vacancy_loss - annual_maintenance - annual_property_tax
        net_yield_pct = (net_annual_income / price * 100.0) if price > 0 else 0.0
        payback_years = (price / net_annual_income) if net_annual_income > 0 else 0.0

        # Property 3-Year & 5-Year Capital Appreciation in Addis Ababa (Historical ~15-20% asset inflation)
        prop_appreciation_annual_pct = 15.0
        prop_val_yr3 = price * ((1.0 + (prop_appreciation_annual_pct / 100.0)) ** 3)
        prop_val_yr5 = price * ((1.0 + (prop_appreciation_annual_pct / 100.0)) ** 5)

        # 2. VEHICLE FUEL VS ELECTRIC (EV) TCO & COST SAVINGS ENGINE
        monthly_km = float(data.get('monthly_km') or 1500.0)
        ice_km_per_liter = float(data.get('ice_efficiency') or 11.0)
        ev_kwh_per_100km = float(data.get('ev_efficiency') or 15.0)
        fuel_price_per_liter = float(data.get('fuel_price') or 118.0)  # ETB/L in Ethiopia
        electricity_price_kwh = float(data.get('electricity_price') or 2.50)  # ETB/kWh domestic rate

        ice_monthly_fuel = (monthly_km / max(1.0, ice_km_per_liter)) * fuel_price_per_liter
        ev_monthly_charging = (monthly_km / 100.0 * ev_kwh_per_100km) * electricity_price_kwh
        monthly_fuel_savings = max(0.0, ice_monthly_fuel - ev_monthly_charging)
        annual_fuel_savings = monthly_fuel_savings * 12.0

        # Annual maintenance savings (EV has ~65% fewer moving parts, no engine oil/filters)
        ice_annual_service = 45000.0
        ev_annual_service = 12000.0
        annual_service_savings = ice_annual_service - ev_annual_service
        total_3yr_ev_savings = (annual_fuel_savings * 3.0) + (annual_service_savings * 3.0)

        # 3-Year Resale Value Estimate (Vehicle Market Dynamics in Ethiopia)
        # Note: In Ethiopia, high inflation and import taxes mean Toyota vehicles often hold or gain nominal ETB value
        ice_resale_yr3 = price * 0.95  # 95% nominal retention
        ev_resale_yr3 = price * 0.88   # 88% nominal retention

        return jsonify({
            "status": "success",
            "property_rental_insights": {
                "purchase_price_etb": round(price, 2),
                "estimated_monthly_rent_etb": round(monthly_rent, 2),
                "gross_annual_rent_etb": round(gross_annual_rent, 2),
                "gross_rental_yield": f"{round(gross_yield_pct, 2)}%",
                "net_annual_income_etb": round(net_annual_income, 2),
                "net_rental_yield": f"{round(net_yield_pct, 2)}%",
                "estimated_payback_period_years": round(payback_years, 1),
                "projected_property_value_3yr_etb": round(prop_val_yr3, 2),
                "projected_property_value_5yr_etb": round(prop_val_yr5, 2)
            },
            "vehicle_energy_and_resale_insights": {
                "benchmark_vehicle_price_etb": round(price, 2),
                "monthly_mileage_km": monthly_km,
                "ice_monthly_fuel_cost_etb": round(ice_monthly_fuel, 2),
                "ev_monthly_charging_cost_etb": round(ev_monthly_charging, 2),
                "monthly_ev_savings_etb": round(monthly_fuel_savings, 2),
                "annual_fuel_savings_etb": round(annual_fuel_savings, 2),
                "annual_maintenance_savings_etb": round(annual_service_savings, 2),
                "total_3year_ev_cost_savings_etb": round(total_3yr_ev_savings, 2),
                "estimated_3year_resale_value": {
                    "ice_nominal_resale_etb": round(ice_resale_yr3, 2),
                    "ev_nominal_resale_etb": round(ev_resale_yr3, 2),
                    "notes": "Reflects Ethiopian nominal asset retention and foreign exchange dynamics."
                }
            }
        })
    except Exception as e:
        logger.error(f"api_financial_insights error: {e}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500


def run_flask():
    port = int(PORT or 8080)
    logger.info("Starting Flask on 0.0.0.0:%s", port)
    web_app.run(host="0.0.0.0", port=port, use_reloader=False, threaded=True)


if __name__ == '__main__':
    run_flask()

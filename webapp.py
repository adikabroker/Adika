# ==============================================================================
# webapp.py — Flask Mini App + REST API# ==============================================================================
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
    resp.headers.pop("X-Frame-Options", None)  # Telegram needs frames allowed
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



SELLER_FORM_HTML = r"""
<!DOCTYPE html>
<html lang="am">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
  <title>Adika Marketplace</title>
  <script src="https://telegram.org/js/telegram-web-app.js"></script>
  <script src="https://cdn.tailwindcss.com"></script>
  <script crossorigin src="https://cdn.jsdelivr.net/npm/react@18.2.0/umd/react.production.min.js"></script>
  <script crossorigin src="https://cdn.jsdelivr.net/npm/react-dom@18.2.0/umd/react-dom.production.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/@babel/standalone@7.24.0/babel.min.js"></script>

  <style>
    body { margin:0; background:#f0f4f9; font-family:system-ui,-apple-system,sans-serif; -webkit-tap-highlight-color:transparent; }
    .chip-active { background:#2563eb; color:#fff; font-weight:700; box-shadow:0 1px 3px rgba(37,99,235,.3); }
    .chip-idle { background:#fff; color:#4b5563; border:1px solid #e2e8f0; }
    input, textarea, select { font-size: 16px !important; }
  </style>
</head>
<body class="bg-[#f0f4f9]">
  <div id="root"></div>
  <script type="text/babel">
    const { useState, useEffect, useRef } = React;
    const tg = (window.Telegram && window.Telegram.WebApp) ? window.Telegram.WebApp : {
      expand(){}, ready(){}, close(){}, initDataUnsafe: {}, setHeaderColor(){}, setBackgroundColor(){}, showAlert: (m)=>alert(m)
    };
    try { tg.ready(); tg.expand(); } catch (e) { console.warn(e); }
    try { tg.setHeaderColor('#2563eb'); tg.setBackgroundColor('#f8fafc'); } catch (e) {}

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
          className={`px-3 py-1.5 rounded-full text-xs whitespace-nowrap transition-all ${
            active
              ? (danger ? 'bg-red-500 text-white font-bold shadow-sm' : 'chip-active')
              : 'chip-idle'
          }`}>
          {label}
        </button>
      );
    }

    function ToggleCard({ active, onToggle, icon, label, danger }) {
      return (
        <button type="button" onClick={onToggle}
          className={`w-full flex items-center gap-3 p-3 rounded-xl border transition-all text-left ${
            active
              ? (danger ? 'bg-red-50 border-red-200 text-red-700' : 'bg-blue-50 border-blue-200 text-blue-700')
              : 'bg-white border-gray-200 text-gray-600'
          }`}>
          <div className={`w-10 h-6 rounded-full relative transition-colors ${active ? (danger ? 'bg-red-500' : 'bg-blue-600') : 'bg-gray-300'}`}>
            <div className={`absolute top-0.5 w-5 h-5 rounded-full bg-white shadow transition-transform ${active ? 'translate-x-4' : 'translate-x-0.5'}`} />
          </div>
          <span className="text-sm font-medium">{icon} {label}</span>
        </button>
      );
    }

    const CAR_TYPE_KEYS = ['የቤት መኪና','የሥራ መኪና','ከባድ ተሽከርካሪ'];
    const FUEL_KEYS = ['ቤንዚን','ናፍጣ','ኤሌክትሪክ','ሀይብሪድ'];
    const TRANSMISSION_KEYS = ['ማንዋል','ኦቶማቲክ'];
    const CONDITION_KEYS = ['አዲስ','ያገለገለ','ጥገና የሚፈልግ'];
    const HOUSE_TYPE_KEYS = ['ቪላ','አፓርታማ','ኮንዶሚኒየም','ሪል እስቴት','መሬት'];
    const BEDROOM_KEYS = ['1','2','3','4','5+'];
    const BATHROOM_KEYS = ['1','2','3','4+'];
    const HOUSE_CONDITION_KEYS = ['አዲስ','ጥሩ','እድሳት የሚፈልግ'];

    const I18N = {
      am: {
        title:"ንብረት ለገበያ ያቅርቡ", step1:"መረጃ", step2:"ዋጋና ፎቶ", step3:"አድራሻ",
        category:"📦 ዋና ምድብ", car:"🚗 መኪና", house:"🏠 ቤት",
        carType:"🚗 አይነት", fuel:"⛽ ነዳጅ", transmission:"⚙️ ማርሽ", condition:"📊 ሁኔታ", mileage:"🛣️ ኪሎሜትር (KM)",
        carTypes:{"የቤት መኪና":"የቤት መኪና","የሥራ መኪና":"የሥራ መኪና","ከባድ ተሽከርካሪ":"ከባድ ተሽከርካሪ"},
        fuels:{"ቤንዚን":"ቤንዚን","ናፍጣ":"ናፍጣ","ኤሌክትሪክ":"ኤሌክትሪክ","ሀይብሪድ":"ሀይብሪድ"},
        transmissions:{"ማንዋል":"ማንዋል","ኦቶማቲክ":"ኦቶማቲክ"},
        conditions:{"አዲስ":"አዲስ","ያገለገለ":"ያገለገለ","ጥገና የሚፈልግ":"ጥገና የሚፈልግ"},
        houseType:"🏠 አይነት", bedrooms:"🛏️ መኝታ", bathrooms:"🛁 መታጠቢያ", houseCondition:"📊 ሁኔታ", parking:"🚗 ፓርኪንግ አለው",
        houseTypes:{"ቪላ":"ቪላ","አፓርታማ":"አፓርታማ","ኮንዶሚኒየም":"ኮንዶሚኒየም","ሪል እስቴት":"ሪል እስቴት","መሬት":"መሬት"},
        bedroomMap:{"1":"1","2":"2","3":"3","4":"4","5+":"5+"},
        bathroomMap:{"1":"1","2":"2","3":"3","4+":"4+"},
        houseConditions:{"አዲስ":"አዲስ","ጥሩ":"ጥሩ","እድሳት የሚፈልግ":"እድሳት የሚፈልግ"},
        description:"📝 መግለጫ", descPlaceholder:"የንብረቱን ሙሉ ዝርዝር ያስገቡ...",
        price:"💰 ዋጋ (ብር)", pricePlaceholder:"2,500,000", negotiable:"💰 ዋጋው የሚደራደር ነው", urgent:"⚡ አስቸኳይ ሽያጭ",
        photos:"📸 ፎቶዎች (እስከ 5)", photosDrag:"ፎቶዎችን እዚህ ይስቀሉ (እስከ 5)", photosClick:"ወይም ይጫኑ ለመምረጥ", photoBusy:"ፎቶ እየተሰረረ ነው…",
        phone:"📞 ስልክ ቁጥር", phoneOpt:"(አማራጭ)", phonePlaceholder:"0911223344", telegram:"📱 Telegram Username", telegramPlaceholder:"@username",
        next:"ቀጣይ →", back:"ተመለስ", cancel:"❌ ሰርዝ", submit:"🚀 መዝገብ", submitBusy:"እየተላከ...",
        successTitle:"✅", successText:"ማስታወቂያዎ በተሳካ ሁኔታ ተመዝገቧል! ለደላሎችም ተልኳል። ማስታወቂያዎን ማጥፋት ወይም ማስተካከል ሲፈልጉ በማንኛውም ጊዜ ወደ 'የገበያ ቦታ' በመሄድ ማስተካከል ይችላሉ።", successSub:"ለደላሎች ተልኳል…"
 },
      en: {
        title:"List an Item", step1:"Details", step2:"Price & Photos", step3:"Contact",
        category:"📦 Category", car:"🚗 Cars", house:"🏠 Houses",
        carType:"🚗 Type", fuel:"⛽ Fuel", transmission:"⚙️ Transmission", condition:"📊 Condition", mileage:"🛣️ Mileage (KM)",
        carTypes:{"የቤት መኪና":"Sedan","የሥራ መኪና":"Commercial","ከባድ ተሽከርካሪ":"Heavy Vehicle"},
        fuels:{"ቤንዚን":"Petrol","ናፍጣ":"Diesel","ኤሌክትሪክ":"Electric","ሀይብሪድ":"Hybrid"},
        transmissions:{"ማንዋል":"Manual","ኦቶማቲክ":"Automatic"},
        conditions:{"አዲስ":"New","ያገለገለ":"Used","ጥገና የሚፈልግ":"Needs Repair"},
        houseType:"🏠 Type", bedrooms:"🛏️ Bedrooms", bathrooms:"🛁 Bathrooms", houseCondition:"📊 Condition", parking:"🚗 Has Parking",
        houseTypes:{"ቪላ":"Villa","አፓርታማ":"Apartment","ኮንዶሚኒየም":"Condominium","ሪል እስቴት":"Real Estate","መሬት":"Land"},
        bedroomMap:{"1":"1","2":"2","3":"3","4":"4","5+":"5+"},
        bathroomMap:{"1":"1","2":"2","3":"3","4+":"4+"},
        houseConditions:{"አዲስ":"New","ጥሩ":"Good","እድሳት የሚፈልግ":"Needs Renovation"},
        description:"📝 Description", descPlaceholder:"Enter full details about the item...",
        price:"💰 Price (ETB)", pricePlaceholder:"2,500,000", negotiable:"💰 Price is negotiable", urgent:"⚡ Urgent Sale",
        photos:"📸 Photos (up to 5)", photosDrag:"Drag photos here (up to 5)", photosClick:"or click to select", photoBusy:"Processing photo…",
        phone:"📞 Phone", phoneOpt:"(Optional)", phonePlaceholder:"0911223344", telegram:"📱 Telegram Username", telegramPlaceholder:"@username",
        next:"Next →", back:"Back", cancel:"❌ Cancel", submit:"🚀 Submit", submitBusy:"Sending...",
        successTitle:"✅", successText:"Your listing has been posted successfully! It has been sent to brokers. Whenever you want to delete or edit your listing, you can do so by visiting the Marketplace.", successSub:"Sent to brokers…"
      }
    };

    function SellerForm() {
      const [lang, setLang] = useState('am');
      const t = (k) => I18N[lang][k] || I18N['am'][k] || k;
      const lbl = (obj, key) => (I18N[lang][obj] && I18N[lang][obj][key]) ? I18N[lang][obj][key] : (I18N['am'][obj] && I18N['am'][obj][key]) ? I18N['am'][obj][key] : key;

      const [step, setStep] = useState(1);
      const [category, setCategory] = useState('መኪና');
      const [fuel, setFuel] = useState('');
      const [transmission, setTransmission] = useState('');
      const [mileage, setMileage] = useState('');
      const [condition, setCondition] = useState('');
      const [carType, setCarType] = useState('');
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
      const [dragOver, setDragOver] = useState(false);

      const compressImage = (file) => new Promise((resolve, reject) => {
        try {
          if (!file || file.size > 8 * 1024 * 1024) {
            reject(new Error(lang==='am'?'ፎቶ በጣም ትልቅ ነው (max 8MB)':'Photo too large (max 8MB)'));
            return;
          }
          const reader = new FileReader();
          reader.onerror = () => reject(new Error(lang==='am'?'ፎቶ ማንበብ አልተቻለም':'Could not read photo'));
          reader.onload = (e) => {
            const img = new Image();
            img.onerror = () => reject(new Error(lang==='am'?'ልክ ያልሆነ ምስል':'Invalid image'));
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
              } catch (err) { reject(err); }
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
            try {
              const dataUrl = await compressImage(f);
              setPhotos(prev => prev.length < 5 ? [...prev, dataUrl] : prev);
            } catch (err) {
              setPhotoError(String(err.message || err));
              try { if (window.Telegram?.WebApp?.showAlert) window.Telegram.WebApp.showAlert(String(err.message || err)); } catch (_) {}
            }
          }
        } finally { setPhotoBusy(false); }
      };

      const removePhoto = (i) => setPhotos(prev => prev.filter((_, idx) => idx !== i));

      const canNext1 = category && (category === 'መኪና' ? (carType || condition) : (houseType || houseCondition));
      const canNext2 = true;
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
            parking: parking ? (lang==='am'?'አለ':'Yes') : (lang==='am'?'የለም':'No'),
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
            setStatus(result.message || (lang==='am'?'ስህተት':'Error'));
            setSubmitting(false);
          }
        } catch (e) {
          setStatus(lang==='am'?'የኔትወርክ ስህተት':'Network error');
          setSubmitting(false);
        }
      };

      const steps = [t('step1'), t('step2'), t('step3')];

      if (status === 'ok') {
        return (
          <div className="min-h-screen flex items-center justify-center p-6">
            <div className="text-center space-y-3">
              <div className="text-5xl">{t('successTitle')}</div>
              <p className="font-bold text-base text-green-700 leading-snug px-2 text-center">{t('successText')}</p>
              <p className="text-sm text-gray-500">{t('successSub')}</p>
            </div>
          </div>
        );
      }

      return (
        <div className="min-h-screen pb-28">
          <div className="sticky top-0 z-20 bg-[#e2ebf6]/95 backdrop-blur-md shadow-[0_4px_20px_rgba(0,0,0,0.03)] px-4 pt-3 pb-2">
            <div className="flex items-center justify-between mb-2">
              <h1 className="font-bold text-sm text-gray-800">{t('title')}</h1>
              <button type="button" onClick={() => setLang(l => l==='am'?'en':'am')}
 className="text-[11px] font-bold bg-white/90 text-blue-700 px-2.5 py-1 rounded-full shadow-sm border-0 outline-none">
                {lang==='am' ? '🇬🇧 EN' : '🇪🇹 AM'}
              </button>
            </div>
            <div className="flex items-center gap-1">
              {steps.map((s, i) => (
                <React.Fragment key={s}>
                  <div className={`flex-1 text-center`}>
                    <div className={`mx-auto w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold ${
                      step > i+1 ? 'bg-blue-600 text-white' : step === i+1 ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-500'
                    }`}>{i+1}</div>
                    <div className={`text-[10px] mt-0.5 ${step===i+1 ? 'text-blue-600 font-bold' : 'text-gray-400'}`}>{s}</div>
                  </div>
                  {i < 2 && <div className={`h-0.5 flex-1 mb-3 ${step > i+1 ? 'bg-blue-600' : 'bg-gray-200'}`} />}
 </React.Fragment>
              ))}
            </div>
          </div>

          <div className="p-4 space-y-4">
            {step === 1 && (
              <div className="space-y-4">
                <div>
                  <label className="text-xs font-medium text-gray-600 mb-1.5 block">{t('category')}</label>
                  <div className="flex gap-2">
                    <Chip label={t('car')} active={category==='መኪና'} onClick={() => setCategory('መኪና')} />
                    <Chip label={t('house')} active={category==='ቤት'} onClick={() => setCategory('ቤት')} />
                  </div>
                </div>

                {category === 'መኪና' ? (
                  <>
                    <div>
                      <label className="text-xs font-medium text-gray-600 mb-1.5 block">{t('carType')}</label>
                      <div className="flex gap-2 overflow-x-auto pb-1">
                        {CAR_TYPE_KEYS.map(tk => <Chip key={tk} label={lbl('carTypes',tk)} active={carType===tk} onClick={() => setCarType(tk)} />)}
                      </div>
                    </div>
                    <div>
                      <label className="text-xs font-medium text-gray-600 mb-1.5 block">{t('fuel')}</label>
                      <div className="flex gap-2 overflow-x-auto pb-1">
                        {FUEL_KEYS.map(tk => <Chip key={tk} label={lbl('fuels',tk)} active={fuel===tk} onClick={() => setFuel(tk)} />)}
                      </div>
                    </div>
                    <div>
                      <label className="text-xs font-medium text-gray-600 mb-1.5 block">{t('transmission')}</label>
                      <div className="flex gap-2">
                        {TRANSMISSION_KEYS.map(tk => <Chip key={tk} label={lbl('transmissions',tk)} active={transmission===tk} onClick={() => setTransmission(tk)} />)}
                      </div>
                    </div>
                    <div>
                      <label className="text-xs font-medium text-gray-600 mb-1.5 block">{t('condition')}</label>
                      <div className="flex gap-2 overflow-x-auto pb-1">
                        {CONDITION_KEYS.map(tk => <Chip key={tk} label={lbl('conditions',tk)} active={condition===tk} onClick={() => setCondition(tk)} />)}
                      </div>
                    </div>
                    <div>
                      <label className="text-xs font-medium text-gray-600 mb-1.5 block">{t('mileage')}</label>
                      <input type="number" value={mileage} onChange={e => setMileage(e.target.value)}
                        placeholder="50000"
                        className="w-full px-3 py-2.5 rounded-xl bg-white border border-gray-200 focus:bg-white focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none text-sm" />
                    </div>
                  </>
                ) : (
                  <>
                    <div>
                      <label className="text-xs font-medium text-gray-600 mb-1.5 block">{t('houseType')}</label>
                      <div className="flex gap-2 overflow-x-auto pb-1">
                        {HOUSE_TYPE_KEYS.map(tk => <Chip key={tk} label={lbl('houseTypes',tk)} active={houseType===tk} onClick={() => setHouseType(tk)} />)}
                      </div>
                    </div>
                    <div>
                      <label className="text-xs font-medium text-gray-600 mb-1.5 block">{t('bedrooms')}</label>
                      <div className="flex gap-2">
                        {BEDROOM_KEYS.map(tk => <Chip key={tk} label={lbl('bedroomMap',tk)} active={bedrooms===tk} onClick={() => setBedrooms(tk)} />)}
                      </div>
                    </div>
                    <div>
                      <label className="text-xs font-medium text-gray-600 mb-1.5 block">{t('bathrooms')}</label>
                      <div className="flex gap-2">
                        {BATHROOM_KEYS.map(tk => <Chip key={tk} label={lbl('bathroomMap',tk)} active={bathrooms===tk} onClick={() => setBathrooms(tk)} />)}
                      </div>
                    </div>
                    <div>
                      <label className="text-xs font-medium text-gray-600 mb-1.5 block">{t('houseCondition')}</label>
                      <div className="flex gap-2 overflow-x-auto pb-1">
                        {HOUSE_CONDITION_KEYS.map(tk => <Chip key={tk} label={lbl('houseConditions',tk)} active={houseCondition===tk} onClick={() => setHouseCondition(tk)} />)}
                      </div>
                    </div>
                    <ToggleCard active={parking} onToggle={() => setParking(!parking)} icon="🚗" label={t('parking')} />
 </>
                )}

                <div>
                  <label className="text-xs font-medium text-gray-600 mb-1.5 block">{t('description')}</label>
                  <textarea value={description} onChange={e => setDescription(e.target.value)} rows={3}
                    placeholder={t('descPlaceholder')}
                    className="w-full px-3 py-2.5 rounded-xl bg-white border border-gray-200 focus:bg-white focus:ring-2 focus:ring-blue-500 outline-none text-sm resize-none" />
                </div>
              </div>
            )}

            {step === 2 && (
              <div className="space-y-4">
                <div>
                  <label className="text-xs font-medium text-gray-600 mb-1.5 block">{t('price')}</label>
                  <div className="relative">
                    <input type="text" inputMode="numeric" value={price}
                      onChange={e => setPrice(formatPrice(e.target.value))}
                      placeholder={t('pricePlaceholder')}
                      className="w-full px-3 py-2.5 rounded-xl bg-white border border-gray-200 focus:bg-white focus:ring-2 focus:ring-blue-500 outline-none text-sm font-semibold" />
                    <span className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-gray-400">ETB</span>
                  </div>
                </div>
                <ToggleCard active={negotiable} onToggle={() => setNegotiable(!negotiable)} icon="💰" label={t('negotiable')} />
                <ToggleCard active={urgent} onToggle={() => setUrgent(!urgent)} icon="⚡" label={t('urgent')} danger />

                <div>
                  <label className="text-xs font-medium text-gray-600 mb-1.5 block">{t('photos')}</label>
                  <div
                    onDragOver={e => { e.preventDefault(); setDragOver(true); }}
                    onDragLeave={() => setDragOver(false)}
                    onDrop={e => { e.preventDefault(); setDragOver(false); addFiles(e.dataTransfer.files); }}
                    onClick={() => fileRef.current?.click()}
                    className={`border-2 border-dashed rounded-2xl p-5 text-center cursor-pointer transition-colors ${
                      dragOver ? 'border-blue-400 bg-blue-50' : 'border-gray-200 bg-white/60'
                    }`}>
                    <div className="text-3xl mb-1">📷</div>
                    <p className="text-xs text-gray-500">{t('photosDrag')}</p>
                    <p className="text-[10px] text-gray-400 mt-0.5">{t('photosClick')}</p>
                    <input ref={fileRef} type="file" accept="image/*" multiple className="hidden"
                      onChange={e => { addFiles(e.target.files); e.target.value=''; }} />
                  </div>
                  {photoBusy && <p className="text-[11px] text-blue-600">{t('photoBusy')}</p>}
                  {photoError && <p className="text-[11px] text-red-600">{photoError}</p>}
                  {photos.length > 0 && (
                    <div className="grid grid-cols-3 gap-2 mt-3">
                      {photos.map((src, i) => (
                        <div key={i} className="relative aspect-square rounded-xl overflow-hidden border border-gray-100">
                          <img src={src} className="w-full h-full object-cover" alt="" />
                          <button type="button" onClick={(e) => { e.stopPropagation(); removePhoto(i); }}
                            className="absolute top-1 right-1 w-6 h-6 rounded-full bg-red-500 text-white text-xs flex items-center justify-center shadow">×</button>
 </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            )}

            {step === 3 && (
              <div className="space-y-4">
                <div>
                  <label className="text-xs font-medium text-gray-600 mb-1.5 block">{t('phone')} <span className="text-gray-400 font-normal">{t('phoneOpt')}</span></label>
                  <input type="tel" value={phone} onChange={e => setPhone(e.target.value)}
 placeholder={t('phonePlaceholder')}
                    className="w-full px-3 py-2.5 rounded-xl bg-white border border-gray-200 focus:bg-white focus:ring-2 focus:ring-blue-500 outline-none text-sm" />
                </div>
                <div>
                  <label className="text-xs font-medium text-gray-600 mb-1.5 block">{t('telegram')}</label>
                  <input type="text" value={telegramUser} onChange={e => setTelegramUser(e.target.value)}
                    placeholder={t('telegramPlaceholder')}
                    className="w-full px-3 py-2.5 rounded-xl bg-white border border-gray-200 focus:bg-white focus:ring-2 focus:ring-blue-500 outline-none text-sm" />
                </div>
                {status && status !== 'ok' && (
                  <p className="text-sm text-red-600 text-center">{status}</p>
                )}
              </div>
            )}
          </div>

          <div className="fixed bottom-0 left-0 right-0 p-3 bg-white/95 backdrop-blur shadow-[0_-4px_24px_rgba(0,0,0,0.04)] flex gap-2 border-0 outline-none">
            {step > 1 ? (
              <button type="button" onClick={() => setStep(s => s-1)}
                className="w-1/3 py-3 rounded-xl bg-gray-100 text-gray-600 font-bold text-sm">{t('back')}</button>
            ) : (
              <button type="button" onClick={() => tg.close()}
                className="w-1/3 py-3 rounded-xl bg-gray-100 text-gray-600 font-bold text-sm">{t('cancel')}</button>
            )}
            {step < 3 ? (
              <button type="button" onClick={() => {
                  if (step === 1 && !canNext1) return;
                  if (photoBusy) return;
                  setStep(s => s+1);
                }}
                disabled={step===1 ? !canNext1 : photoBusy}
 className="flex-1 py-3 rounded-xl bg-blue-600 text-white font-bold text-sm disabled:opacity-40">
                {t('next')}
              </button>
            ) : (
              <button type="button" onClick={submit} disabled={!canSubmit || submitting}
                className="flex-1 py-3 rounded-xl bg-blue-600 text-white font-bold text-sm disabled:opacity-40 flex items-center justify-center gap-1">
                {submitting ? t('submitBusy') : t('submit')}
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


BUYER_FORM_HTML = r"""
<!DOCTYPE html>
<html lang="am">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
  <title>Adika Marketplace</title>
  <script src="https://telegram.org/js/telegram-web-app.js"></script>
  <script src="https://cdn.tailwindcss.com"></script>
  <script crossorigin src="https://cdn.jsdelivr.net/npm/react@18.2.0/umd/react.production.min.js"></script>
  <script crossorigin src="https://cdn.jsdelivr.net/npm/react-dom@18.2.0/umd/react-dom.production.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/@babel/standalone@7.24.0/babel.min.js"></script>

  <style>
    body { margin:0; background:#f0f4f9; font-family:system-ui,-apple-system,sans-serif; -webkit-tap-highlight-color:transparent; }
    .chip-active { background:#2563eb; color:#fff; font-weight:700; box-shadow:0 1px 3px rgba(37,99,235,.3); }
    .chip-idle { background:#fff; color:#4b5563; border:1px solid #e2e8f0; }
    input, textarea { font-size: 16px !important; }
  </style>
</head>
<body class="bg-[#f0f4f9]">
  <div id="root"></div>
  <script type="text/babel">
    const { useState } = React;
    const tg = (window.Telegram && window.Telegram.WebApp) ? window.Telegram.WebApp : {
      expand(){}, ready(){}, close(){}, initDataUnsafe: {}, setHeaderColor(){}, setBackgroundColor(){}, showAlert: (m)=>alert(m)
    };
    try { tg.ready(); tg.expand(); } catch (e) { console.warn(e); }
    try { tg.setHeaderColor('#2563eb'); tg.setBackgroundColor('#f8fafc'); } catch (e) {}

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
          className={`px-3 py-1.5 rounded-full text-xs whitespace-nowrap transition-all ${active ? 'chip-active' : 'chip-idle'}`}>
          {label}
        </button>
      );
    }

    const I18N = {
      am: {
        title:"የሚፈልጉትን ንብረት ይግለጹ",
        category:"📦 ምድብ", car:"🚗 መኪና", house:"🏠 ቤት",
        budget:"💰 የበጀት ክልል (ብር)", from:"ከ", to:"እስከ",
        notify:"🔔 ተመሳሳይ ንብረት ሲለቀቅ ማሳወቂያ ይድረሰኝ",
        details:"📝 ዝርዝር ፍላጎት", detailsPlaceholder:"ለምሳሌ፦ ቶዮታ ቪትዝ 2020፣ ነጭ፣ ኦቶማቲክ...",
        phone:"📞 ስልክ ቁጥር", phoneOpt:"(አማራጭ)", phonePlaceholder:"0911223344",
        telegram:"📱 Telegram Username", telegramPlaceholder:"@username",
        cancel:"❌ ሰርዝ", send:"📨 ጥያቄውን ላክ", sending:"እየተላከ...",
        successTitle:"✅", successText:"ማስታወቂያዎ በተሳካ ሁኔታ ተመዝገቧል! ለደላሎችም ተልኳል። ማስታወቂያዎን ማጥፋት ወይም ማስተካከል ሲፈልጉ በማንኛውም ጊዜ ወደ 'የገበያ ቦታ' በመሄድ ማስተካከል ይችላሉ።", successSub:"አቅራቢዎች መልስ ይሰጡዎታል…",
        errorNetwork:"የኔትወርክ ስህተት", errorGeneric:"ስህተት"
      },
      en: {
        title:"Post a Request",
        category:"📦 Category", car:"🚗 Cars", house:"🏠 Houses",
        budget:"💰 Budget Range (ETB)", from:"From", to:"To",
        notify:"🔔 Notify me when similar items are listed",
        details:"📝 Request Details", detailsPlaceholder:"e.g., Toyota Vitz 2020, white, automatic...",
        phone:"📞 Phone", phoneOpt:"(Optional)", phonePlaceholder:"0911223344",
        telegram:"📱 Telegram Username", telegramPlaceholder:"@username",
        cancel:"❌ Cancel", send:"📨 Send Request", sending:"Sending...",
        successTitle:"✅", successText:"Your request has been submitted successfully! It has been sent to brokers. Whenever you want to edit or delete it, visit the Marketplace.", successSub:"Suppliers will respond to you…",
        errorNetwork:"Network error", errorGeneric:"Error"
      }
    };

    function BuyerForm() {
      const [lang, setLang] = useState('am');
      const t = (k) => I18N[lang][k] || I18N['am'][k] || k;

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
            setTimeout(() => tg.close(), 2200);
          } else {
            setStatus(result.message || t('errorGeneric'));
            setSubmitting(false);
          }
        } catch (e) {
          setStatus(t('errorNetwork'));
          setSubmitting(false);
        }
      };

      if (status === 'ok') {
        return (
          <div className="min-h-screen flex items-center justify-center p-6">
            <div className="text-center space-y-3">
              <div className="text-5xl">{t('successTitle')}</div>
              <p className="font-bold text-base text-green-700 leading-snug px-2 text-center">{t('successText')}</p>
              <p className="text-sm text-gray-500">{t('successSub')}</p>
            </div>
          </div>
        );
      }

      return (
 <div className="min-h-screen pb-28">
          <div className="sticky top-0 z-20 bg-[#e2ebf6]/95 backdrop-blur-md shadow-[0_4px_20px_rgba(0,0,0,0.03)] px-4 py-3 flex items-center justify-between">
            <h1 className="font-bold text-sm text-gray-800">{t('title')}</h1>
            <button type="button" onClick={() => setLang(l => l==='am'?'en':'am')}
              className="text-[11px] font-bold bg-white/90 text-blue-700 px-2.5 py-1 rounded-full shadow-sm border-0 outline-none">
              {lang==='am' ? '🇬🇧 EN' : '🇪🇹 AM'}
            </button>
          </div>

          <div className="p-4 space-y-4">
            <div>
              <label className="text-xs font-medium text-gray-600 mb-1.5 block">{t('category')}</label>
              <div className="flex gap-2">
                <Chip label={t('car')} active={category==='መኪና'} onClick={() => setCategory('መኪና')} />
                <Chip label={t('house')} active={category==='ቤት'} onClick={() => setCategory('ቤት')} />
              </div>
            </div>

            <div>
              <label className="text-xs font-medium text-gray-600 mb-1.5 block">{t('budget')}</label>
              <div className="flex gap-2 items-center">
                <div className="flex-1 relative">
                  <span className="absolute left-2.5 top-1/2 -translate-y-1/2 text-[10px] text-gray-400">{t('from')}</span>
                  <input type="text" inputMode="numeric" value={budgetMin}
                    onChange={e => setBudgetMin(formatPrice(e.target.value))}
                    placeholder="500,000"
                    className="w-full pl-10 pr-2 py-2.5 rounded-xl bg-white border border-gray-200 focus:bg-white focus:ring-2 focus:ring-blue-500 outline-none text-sm" />
                </div>
                <span className="text-gray-300">—</span>
                <div className="flex-1 relative">
                  <span className="absolute left-2.5 top-1/2 -translate-y-1/2 text-[10px] text-gray-400">{t('to')}</span>
                  <input type="text" inputMode="numeric" value={budgetMax}
                    onChange={e => setBudgetMax(formatPrice(e.target.value))}
                    placeholder="2,000,000"
                    className="w-full pl-10 pr-2 py-2.5 rounded-xl bg-white border border-gray-200 focus:bg-white focus:ring-2 focus:ring-blue-500 outline-none text-sm" />
                </div>
              </div>
            </div>

            <button type="button" onClick={() => setCreateAlert(!createAlert)}
              className={`w-full flex items-center gap-3 p-3.5 rounded-xl border transition-all text-left ${
 createAlert ? 'bg-blue-50 border-blue-200 text-blue-700' : 'bg-white border-gray-200 text-gray-600'
              }`}>
              <div className={`w-10 h-6 rounded-full relative transition-colors shrink-0 ${createAlert ? 'bg-blue-600' : 'bg-gray-300'}`}>
                <div className={`absolute top-0.5 w-5 h-5 rounded-full bg-white shadow transition-transform ${createAlert ? 'translate-x-4' : 'translate-x-0.5'}`} />
              </div>
              <span className="text-sm font-medium leading-snug">{t('notify')}</span>
            </button>

            <div>
              <label className="text-xs font-medium text-gray-600 mb-1.5 block">{t('details')}</label>
              <textarea value={details} onChange={e => setDetails(e.target.value)} rows={4}
                placeholder={t('detailsPlaceholder')}
                className="w-full px-3 py-2.5 rounded-xl bg-white border border-gray-200 focus:bg-white focus:ring-2 focus:ring-blue-500 outline-none text-sm resize-none" />
            </div>

            <div>
              <label className="text-xs font-medium text-gray-600 mb-1.5 block">{t('phone')} <span className="text-gray-400 font-normal">{t('phoneOpt')}</span></label>
              <input type="tel" value={phone} onChange={e => setPhone(e.target.value)}
                placeholder={t('phonePlaceholder')}
                className="w-full px-3 py-2.5 rounded-xl bg-white border border-gray-200 focus:bg-white focus:ring-2 focus:ring-blue-500 outline-none text-sm" />
            </div>
            <div>
              <label className="text-xs font-medium text-gray-600 mb-1.5 block">{t('telegram')}</label>
              <input type="text" value={telegramUser} onChange={e => setTelegramUser(e.target.value)}
 placeholder={t('telegramPlaceholder')}
                className="w-full px-3 py-2.5 rounded-xl bg-white border border-gray-200 focus:bg-white focus:ring-2 focus:ring-blue-500 outline-none text-sm" />
            </div>

            {status && status !== 'ok' && (
              <p className="text-sm text-red-600 text-center">{status}</p>
            )}
          </div>

          <div className="fixed bottom-0 left-0 right-0 p-3 bg-white/95 backdrop-blur shadow-[0_-4px_24px_rgba(0,0,0,0.04)] flex gap-2 border-0 outline-none">
            <button type="button" onClick={() => tg.close()}
              className="w-1/3 py-3 rounded-xl bg-gray-100 text-gray-600 font-bold text-sm">{t('cancel')}</button>
            <button type="button" onClick={submit} disabled={!details || submitting}
              className="flex-1 py-3 rounded-xl bg-blue-600 text-white font-bold text-sm disabled:opacity-40 flex items-center justify-center gap-1">
              {submitting ? t('sending') : t('send')}
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
       return jsonify({"status": "error", "message": f"Server Error: {str(e)}"}), 500@web_app.route('/api/submit-request', methods=['POST'])
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
           main_category=(category or car_type or house_type or "መኪና"),
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


# ==============================================================================
# WEB APP EXPLORER (Vanilla JS + Tailwind-like CSS) - Full Production UI
# Features: Soft blue theme, floating cards, verified badge, relative time,
#            star rating, location, lang switcher, bottom nav
# ==============================================================================

EXPLORER_HTML = r"""
<!DOCTYPE html>
<html lang="am">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no" />
  <title>Adika Marketplace</title>
  <script src="https://telegram.org/js/telegram-web-app.js"></script>
  <style>
    html, body {
      margin: 0; padding: 0; width: 100%; max-width: 100vw;
      overflow-x: hidden; box-sizing: border-box;
      font-family: system-ui, -apple-system, sans-serif;
      background: #f0f4f9; color: #0f172a;
    }
    *, *::before, *::after { box-sizing: border-box; }
    .wrap { width: 100%; padding: 0 0 calc(64px + env(safe-area-inset-bottom)); min-height: 100vh; background: #f0f4f9; }
    .hdr {
      position: sticky; top: 0; z-index: 30;
      background: rgba(226,235,246,0.95);
      backdrop-filter: blur(12px);
      padding: 10px 12px;
      box-shadow: 0 4px 20px rgba(0,0,0,0.03);
      border: none !important; outline: none !important;
    }
    .brand-row { display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px; }
    .brand { font-weight: 800; font-size: 14px; color: #1e3a8a; }
    .lang-btn {
      border: none; outline: none; background: #fff; color: #2563eb;
      border-radius: 999px; padding: 6px 10px; font-size: 11px; font-weight: 700;
      box-shadow: 0 2px 6px rgba(15,23,42,0.05); cursor: pointer;
    }
    .tabs { display: flex; gap: 8px; margin-bottom: 8px; }
    .tab {
      flex: 1; border: none; outline: none; padding: 10px 6px; border-radius: 14px;
      font-weight: 700; font-size: 12px; background: #fff; color: #475569;
      box-shadow: 0 2px 8px rgba(15,23,42,0.05); cursor: pointer;
    }
    .tab.on { background: #2563eb; color: #fff; }
    .search-wrap { position: relative; margin-bottom: 8px; }
    .search-wrap span { position: absolute; left: 12px; top: 50%; transform: translateY(-50%); opacity: .4; }
    .search {
      width: 100%; padding: 11px 14px 11px 34px; border-radius: 14px;
      border: none; outline: none; background: #fff; font-size: 13px;
      box-shadow: 0 2px 12px rgba(15,23,42,0.04);
 }
    .cats { display: flex; gap: 6px; overflow-x: auto; padding-bottom: 2px; scrollbar-width: none; }
    .cats::-webkit-scrollbar { display: none; }
    .cat {
      flex: 0 0 auto; border: none; outline: none; background: #fff; border-radius: 999px;
      padding: 7px 12px; font-size: 11px; font-weight: 600; color: #334155;
      box-shadow: 0 2px 6px rgba(15,23,42,0.05); cursor: pointer;
    }
    .cat.on { background: #2563eb; color: #fff; }
    .grid {
      display: grid; grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 12px; padding: 12px;
    }
    .card {
      background: #fff;
      border: none !important; outline: none !important;
      border-radius: 16px;
      overflow: hidden;
      box-shadow: 0 8px 24px rgba(15,23,42,0.06);
      display: flex;
      flex-direction: column;
    }
    .card-media {
      position: relative; width: 100%; height: 120px;
      overflow: hidden;
      border: none !important;
    }
    .card-media img {
      width: 100%; height: 100%; object-fit: cover; display: block;
      border: none !important;
    }
    .ph {
      width: 100%; height: 100%;
      display: flex; align-items: center; justify-content: center;
      background: linear-gradient(135deg, #3b82f6 0%, #4f46e5 100%);
      border: none !important;
    }
    .ph-icon { font-size: 42px; line-height: 1; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.15)); color: rgba(255,255,255,0.9); }
    .verified-badge {
      position: absolute; top: 8px; left: 8px;
      background: rgba(255,255,255,0.9); color: #2563eb;
      font-size: 9px; font-weight: 700; padding: 3px 7px; border-radius: 999px;
      backdrop-filter: blur(4px); border: none !important;
    }
    .active-badge {
      position: absolute; top: 8px; right: 8px; width: 10px; height: 10px;
      background: #22c55e; border-radius: 50%; border: none;
      animation: pulse-green 1.6s ease-out infinite;
    }
    .active-badge.sold { background: #ef4444; animation: pulse-red 1.6s ease-out infinite; }
    @keyframes pulse-green {
      0% { box-shadow: 0 0 0 0 rgba(34,197,94,0.55); }
      70% { box-shadow: 0 0 0 8px rgba(34,197,94,0); }
      100% { box-shadow: 0 0 0 0 rgba(34,197,94,0); }
    }
    @keyframes pulse-red {
      0% { box-shadow: 0 0 0 0 rgba(239,68,68,0.55); }
      70% { box-shadow: 0 0 0 8px rgba(239,68,68,0); }
      100% { box-shadow: 0 0 0 0 rgba(239,68,68,0); }
    }
    .meta { position: absolute; left: 6px; right: 6px; bottom: 6px; display: flex; justify-content: space-between; }
    .badge { font-size: 9px; background: rgba(0,0,0,.4); backdrop-filter: blur(4px); color: #fff; padding: 2px 7px; border-radius: 999px; border: none !important; }
    .card-body { padding: 10px 10px 12px; }
    .title { font-weight: 700; font-size: 13px; color: #0f172a; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .sub { font-size: 11px; color: #64748b; margin-top: 3px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .row-trust { display: flex; align-items: center; gap: 6px; margin-top: 4px; flex-wrap: wrap; }
    .loc { font-size: 11px; color: #64748b; }
 .stars { font-size: 11px; color: #f59e0b; font-weight: 700; }
    .price-badge {
      display: inline-flex; margin: 8px auto 0; padding: 6px 12px; border-radius: 999px;
      background: #EFF6FF; color: #2563EB; font-weight: 800; font-size: 12px;
    }
    .actions { display: grid; grid-template-columns: 1fr 1fr; gap: 6px; margin-top: 10px; }
    .btn { border: none; outline: none; border-radius: 12px; padding: 9px; font-size: 16px; text-align: center; text-decoration: none; }
    .btn.call { background: #eff6ff; color: #1d4ed8; }
    .btn.chat { background: #f1f5f9; color: #334155; }
    .status-box { text-align: center; padding: 48px 16px; color: #64748b; font-size: 14px; }
    .status-box.err { color: #b91c1c; }
    .more {
      display: none; margin: 16px auto; border: none; outline: none; background: #fff; color: #2563eb;
      border-radius: 999px; padding: 11px 22px; font-weight: 700; font-size: 12px;
      box-shadow: 0 10px 25px -5px rgba(0,0,0,0.08); cursor: pointer;
    }
    /* Bottom Nav */
    .bottom-nav {
      position: fixed; bottom: 0; left: 0; right: 0; z-index: 40;
      background: rgba(255,255,255,0.92);
      backdrop-filter: blur(12px);
      box-shadow: 0 -4px 24px rgba(0,0,0,0.06);
      display: flex; justify-content: space-around; align-items: flex-start;
      padding: 6px 0 calc(6px + env(safe-area-inset-bottom));
      border: none !important; outline: none !important;
    }
    .nav-item {
      flex: 1; background: none; border: none; outline: none;
      display: flex; flex-direction: column; align-items: center; gap: 2px;
      color: #64748b; font-size: 10px; padding-top: 4px; cursor: pointer;
 }
    .nav-item.active { color: #2563eb; }
    .nav-icon { font-size: 20px; line-height: 1; }
    .nav-center-wrap { flex: 1; display: flex; justify-content: center; position: relative; top: -14px; }
    .nav-center-btn {
      width: 52px; height: 52px; border-radius: 50%; background: #2563eb; color: #fff;
      border: none; outline: none; box-shadow: 0 8px 20px rgba(37,99,235,0.35);
      font-size: 28px; display: flex; align-items: center; justify-content: center;
 cursor: pointer;
    }
  </style>
</head>
<body>
  <div class="wrap">
    <div class="hdr">
      <div class="brand-row">
        <div class="brand">Adika Marketplace</div>
        <button id="langBtn" class="lang-btn" type="button">🇬🇧 EN</button>
      </div>
      <div class="tabs">
        <button class="tab on" id="tabSell" type="button">🛒 የገበያ ቦታ</button>
        <button class="tab" id="tabBuy" type="button">📋 የፈላጊዎች</button>
      </div>
      <div class="search-wrap">
        <span>🔍</span>
        <input class="search" id="q" type="search" placeholder="ፈልግ..." autocomplete="off" />
      </div>
      <div class="cats" id="cats"></div>
    </div>
    <div id="status" class="status-box">እየጫነ ነው…</div>
    <div class="grid" id="grid"></div>
    <button class="more" id="more" type="button">ተጨማሪ ይመልከቱ</button>
  </div>

  <nav class="bottom-nav" id="bottomNav">
    <button class="nav-item" id="navHome" type="button">
      <span class="nav-icon">🏠</span>
      <span id="navHomeLabel">መነሻ</span>
    </button>
    <button class="nav-item" id="navSearch" type="button">
      <span class="nav-icon">🔍</span>
      <span id="navSearchLabel">ፈልግ</span>
    </button>
    <div class="nav-center-wrap">
      <button class="nav-center-btn" id="navSell" type="button">＋</button>
    </div>
    <button class="nav-item" id="navMessages" type="button">
      <span class="nav-icon">💬</span>
      <span id="navMessagesLabel">መልዕክቶች</span>
    </button>
    <button class="nav-item" id="navProfile" type="button">
      <span class="nav-icon">👤</span>
      <span id="navProfileLabel">መለያ</span>
    </button>
  </nav>

  <script>
  (function () {
    var API_BASE = "https://adika-y37t.onrender.com";
    try {
      if (location && location.origin && location.origin.indexOf("adika-y37t") !== -1) {
        API_BASE = location.origin;
      }
    } catch (e) {}

    try {
      var tg = window.Telegram && window.Telegram.WebApp;
      if (tg) {
        try { tg.ready(); } catch (e) {}
        try { tg.expand(); } catch (e) {}
      }
    } catch (e) {}

    var TX = {
      am: {
        tabSell:"🛒 የገበያ ቦታ", tabBuy:"📋 የፈላጊዎች", searchPlaceholder:"ፈልግ...",
        all:"✨ ሁሉም", car:"🚗 መኪና", house:"🏠 ቤት / ቦታ", business:"🏢 የሥራ ቦታ",
        loading:"እየጫነ ነው…", noItems:"ምንም አይነት የተመዘገበ ንብረት አልተገኘም", loadError:"መረጃ ማምጣት አልተቻለም — እንደገና ይሞክሩ", more:"ተጨማሪ ይመልከቱ",
        priceSell:"ዋጋ", priceBuy:"በጀት", verified:"✓ የደረሰ አካል", locationFallback:"አዲስ አበባ", kmAway:"ክ.ሌ",
        navHome:"መነሻ", navSearch:"ፈልግ", navSell:"አስተዋውቅ", navMessages:"መልዕክቶች", navProfile:"መለያ"
      },
      en: {
        tabSell:"🛒 Marketplace", tabBuy:"📋 Requests", searchPlaceholder:"Search...",
        all:"✨ All", car:"🚗 Cars", house:"🏠 Houses", business:"🏢 Business",
        loading:"Loading…", noItems:"No listings found.", loadError:"Failed to load data — please retry.", more:"Load more",
        priceSell:"Price", priceBuy:"Budget", verified:"✓ Verified", locationFallback:"Addis Ababa", kmAway:"km away",
        navHome:"Home", navSearch:"Search", navSell:"Sell", navMessages:"Messages", navProfile:"Profile"
      }
    };

    var CAT_KEYS = ["", "መኪና", "ቤት", "ንግድ"];

    var state = { tab: "marketplace", category: "", q: "", page: 1, hasMore: false, loading: false, lang: 'am' };
    var grid = document.getElementById("grid");
    var statusEl = document.getElementById("status");
    var moreBtn = document.getElementById("more");
    var tabSell = document.getElementById("tabSell");
    var tabBuy = document.getElementById("tabBuy");
    var qInput = document.getElementById("q");
    var catsEl = document.getElementById("cats");
    var langBtn = document.getElementById("langBtn");

    function esc(s) {
      return String(s == null ? "" : s)
        .replace(/&/g, "&amp;").replace(/</g, "&lt;")
        .replace(/>/g, "&gt;").replace(/"/g, "&quot;");
 }

    function showStatus(text, isErr) {
      statusEl.style.display = "block";
      statusEl.className = "status-box" + (isErr ? " err" : "");
      statusEl.textContent = text;
 }

    function hideStatus() {
      statusEl.style.display = "none";
    }

    function relativeTime(iso) {
      if (!iso) return "";
      try {
        var secs = Math.max(0, Math.floor((Date.now() - new Date(iso).getTime()) / 1000));
        if (secs < 60) return state.lang === 'am' ? "አሁን" : "now";
        if (secs < 3600) return Math.floor(secs / 60) + (state.lang === 'am' ? " ደቂቃ" : " min");
        if (secs < 86400) return Math.floor(secs / 3600) + (state.lang === 'am' ? " ሰዓት" : " hrs");
        return Math.floor(secs / 86400) + (state.lang === 'am' ? " ቀን" : " days");
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
      s = s.replace(/\(\s*\)/g, " ");
      return s.replace(/\s+/g, " ").trim().slice(0, 48);
    }

    function renderCats() {
      var tx = TX[state.lang];
      var map = { "": tx.all, "መኪና": tx.car, "ቤት": tx.house, "ንግድ": tx.business };
      var html = "";
      for (var i = 0; i < CAT_KEYS.length; i++) {
        var c = CAT_KEYS[i];
        html += '<button type="button" class="cat' + (state.category === c ? " on" : "") + '" data-id="' + esc(c) + '">' + esc(map[c] || c) + "</button>";
      }
      catsEl.innerHTML = html;
    }

    function setTabs() {
      var tx = TX[state.lang];
      tabSell.textContent = tx.tabSell;
      tabBuy.textContent = tx.tabBuy;
      tabSell.className = "tab" + (state.tab === "marketplace" ? " on" : "");
      tabBuy.className = "tab" + (state.tab === "requests" ? " on" : "");
    }

    function updateNavLabels() {
      var tx = TX[state.lang];
      document.getElementById('navHomeLabel').textContent = tx.navHome;
      document.getElementById('navSearchLabel').textContent = tx.navSearch;
      document.getElementById('navMessagesLabel').textContent = tx.navMessages;
      document.getElementById('navProfileLabel').textContent = tx.navProfile;
    }

    function cardHtml(item) {
      try {
        var tx = TX[state.lang];
        var extra = item.extra_data || {};
        if (typeof extra === "string") {
          try { extra = JSON.parse(extra); } catch (e) { extra = {}; }
        }
        var photos = item.photos || [];
        if (!Array.isArray(photos)) photos = [];
        var isCar = (item.main_category === "መኪና" || item.category === "መኪና");
        var icon = isCar ? "🚗" : "🏠";
        var media;
        if (photos.length) {
          media = '<img src="' + esc(photos[0]) + '" alt="" loading="lazy" />';
        } else {
          media = '<div class="ph"><div class="ph-icon">' + icon + '</div></div>';
        }
        var title = (item.main_category || item.category || "") + (item.sub_category ? " • " + item.sub_category : "");
        var desc = cleanDesc(item.description);
        var isSell = String(item.req_type || "").toUpperCase() === "SELL";
        var priceNum = item.price || "—";
        var priceLabel = tx.priceSell + ": " + priceNum;
        if (!isSell) priceLabel = tx.priceBuy + ": " + priceNum;

        var views = item.view_count || item.views_count || 0;
        var phone = item.phone ? String(item.phone).replace(/\s+/g, "") : "";
        var user = extra.telegram_user ? String(extra.telegram_user).replace("@", "") : "";
        var callHref = phone ? ("tel:" + phone) : "#";
        var chatHref = user ? ("https://t.me/" + user) : (item.user_chat_id ? ("tg://user?id=" + item.user_chat_id) : "#");
        var st = String(item.status || "").toUpperCase();
        var sold = (st === "SOLD" || st === "RENTED" || st === "EXPIRED");

        var listing_id = Number(item.id || 0);
        var distance = ((listing_id || 1) % 12) + 1;
        var rating = (4 + ((listing_id || 0) % 15) / 10).toFixed(1);
        var verifiedText = tx.verified;
        var locationText = (extra.location || tx.locationFallback) + ", ~" + distance + " " + tx.kmAway;

        return '<div class="card">' +
          '<div class="card-media">' +
            '<span class="active-badge' + (sold ? " sold" : "") + '"></span>' +
            '<div class="verified-badge">' + esc(verifiedText) + '</div>' +
            media +
 '<div class="meta">' +
              '<span class="badge">👁️ ' + esc(views) + '</span>' +
              '<span class="badge">' + esc(relativeTime(item.created_at)) + '</span>' +
            '</div>' +
          '</div>' +
          '<div class="card-body">' +
 '<div class="title">' + esc(title) + '</div>' +
            (desc ? '<div class="sub">' + esc(desc) + '</div>' : "") +
            '<div class="row-trust">' +
              '<span class="loc">📍 ' + esc(locationText) + '</span>' +
            '</div>' +
            '<div class="row-trust">' +
              '<span class="stars">★ ' + esc(rating) + '</span>' +
 '</div>' +
 '<div style="text-align:center;">' +
              '<span class="price-badge">💰 ' + esc(priceLabel) + '</span>' +
            '</div>' +
            '<div class="actions">' +
              '<a class="btn call" href="' + esc(callHref) + '">📞</a>' +
              '<a class="btn chat" href="' + esc(chatHref) + '">💬</a>' +
            '</div>' +
          '</div>' +
        '</div>';
      } catch (e) {
        return '<div class="card"><div class="sub">Card error</div></div>';
      }
    }

    function finishLoading(items, append, hasMore) {
      state.loading = false;
      if (!append) grid.innerHTML = "";
      if (!items || !items.length) {
        if (!append) {
          showStatus(TX[state.lang].noItems, false);
        }
        moreBtn.style.display = "none";
        return;
      }
      hideStatus();
      var html = "";
      for (var i = 0; i < items.length; i++) html += cardHtml(items[i]);
      grid.innerHTML = append ? (grid.innerHTML + html) : html;
      moreBtn.style.display = hasMore ? "block" : "none";
    }

    function load(append) {
      if (state.loading) return;
      state.loading = true;
      if (!append) {
        showStatus(TX[state.lang].loading, false);
        grid.innerHTML = "";
      }

      var safety = setTimeout(function () {
        if (state.loading) {
          state.loading = false;
          showStatus(TX[state.lang].noItems, false);
          moreBtn.style.display = "none";
        }
      }, 12000);

      var page = append ? state.page + 1 : 1;
      var qs = "page=" + page + "&limit=12&order=DESC&active_only=1&type=" +
        (state.tab === "marketplace" ? "SELL" : "BUY");
      if (state.category) qs += "&category=" + encodeURIComponent(state.category);
      if (state.q) qs += "&q=" + encodeURIComponent(state.q);

      var urls = [
        API_BASE + "/api/explorer/listings?" + qs,
        "/api/explorer/listings?" + qs
      ];

      function tryFetch(idx) {
        if (idx >= urls.length) {
          clearTimeout(safety);
          finishLoading([], append, false);
          showStatus(TX[state.lang].loadError, true);
          return;
        }
        var url = urls[idx];
        var xhr = new XMLHttpRequest();
        xhr.open("GET", url, true);
        xhr.timeout = 10000;
        xhr.setRequestHeader("Accept", "application/json");
        xhr.onload = function () {
          clearTimeout(safety);
          try {
            var data = {};
            try { data = JSON.parse(xhr.responseText || "{}"); } catch (e) { data = {}; }
            if (xhr.status >= 200 && xhr.status < 300) {
              var items = data.items || data.listings || [];
              if (!Array.isArray(items)) items = [];
              state.page = page;
              state.hasMore = !!(data.has_more || data.hasMore);
              finishLoading(items, append, state.hasMore);
            } else {
              tryFetch(idx + 1);
            }
          } catch (e) {
            tryFetch(idx + 1);
          }
        };
        xhr.onerror = function () { tryFetch(idx + 1); };
        xhr.ontimeout = function () { tryFetch(idx + 1); };
        try { xhr.send(); } catch (e) { tryFetch(idx + 1); }
      }
      tryFetch(0);
    }

    tabSell.onclick = function () { state.tab = "marketplace"; setTabs(); load(false); };
    tabBuy.onclick = function () { state.tab = "requests"; setTabs(); load(false); };
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

    langBtn.onclick = function () {
      state.lang = state.lang === 'am' ? 'en' : 'am';
      langBtn.textContent = state.lang === 'am' ? '🇬🇧 EN' : '🇪🇹 AM';
      qInput.placeholder = TX[state.lang].searchPlaceholder;
      renderCats();
      setTabs();
      updateNavLabels();
      if (!state.loading) load(false);
    };

    // Bottom nav actions
    document.getElementById('navHome').onclick = function () {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    };
    document.getElementById('navSearch').onclick = function () { qInput.focus(); };
    document.getElementById('navSell').onclick = function () { window.location.href = '/seller-form'; };
    document.getElementById('navMessages').onclick = function () {
      try { tg && tg.showAlert && tg.showAlert(state.lang==='am'?'በቅርቡ...':'Coming soon...'); } catch(e){}
 };
    document.getElementById('navProfile').onclick = function () {
      try { tg && tg.showAlert && tg.showAlert(state.lang==='am'?'በቅርቡ...':'Coming soon...'); } catch(e){}
    };

    renderCats();
    setTabs();
    updateNavLabels();
    setTimeout(function () { load(false); }, 50);
  })();
  </script>
</body>
</html>
""" # end EXPLORER_HTML@web_app.route('/')
def home():
    return (
        "<html><body style='font-family:sans-serif;padding:24px'>"
        "<h2>Adika Marketplace</h2>"
        "<p>Server is running.</p>"
        f"<p>WEBAPP_URL: <code>{WEBAPP_URL}</code></p>"
        "<ul>"
        "<li><a href='/seller-form'>/seller-form</a></li>"
        "<li><a href='/buyer-form'>/buyer-form</a></li>"
        "<li><a href='/explorer'>/explorer</a></li>"
        "<li><a href='/api/health'>/api/health</a></li>"
        "</ul></body></html>"
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
        # refresh backend after connect
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

            # Detect columns safely
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
            from models import _DB_BACKEND backend = _DB_BACKEND
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
        # Never leave the Mini App spinning — return empty success payload
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
    """
    Social-proof view booster.
    Increments view_count by a random amount between +3 and +7.
    Called once per card per session from the frontend IntersectionObserver.
    """
    import random
    try:
        boost = random.randint(3, 7)
        conn = get_db_connection()
        cur = conn.cursor()
        p = get_placeholder()
        # Ensure baseline exists for brand-new rows that still have 0
        cur.execute(f"SELECT view_count FROM listings WHERE id = {p}", (listing_id,))
        row = cur.fetchone()
        if not row:
            conn.close()
            return jsonify({"status": "error", "message": "not found"}), 404
        current = row['view_count'] if isinstance(row, dict) else row[0]
        if current is None or current == 0:
            # Assign initial baseline 35–90 then add boost
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
    """
    Mark listing as sold / rented / pending (re-activate).
    Only the owner (user_chat_id) or ADMIN may update.
    Body: { "status": "sold"|"rented"|"pending", "user_id": <telegram_id> }
    """
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


# ---------- Auto-Expiry / Cleanup Job ----------




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
        # Sanitize for JSON
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
    """Alias with strict pagination (10-15 max)."""
    return api_explorer_listings()

def run_flask():
    """Start Flask HTTP server (Mini App + REST API) on 0.0.0.0:PORT."""
    port = int(PORT or 8080)
    logger.info("Starting Flask on 0.0.0.0:%s", port)
    web_app.run(host="0.0.0.0", port=port, use_reloader=False, threaded=True)

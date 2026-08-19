# ==============================================================================
# webapp.py — Flask Mini App + REST API for Adika Marketplace
# Upgraded with:
# - Clean Single-Language UI with Dedicated AM | EN Language Switcher
# - Dynamic category-specific listing card specs (Cars: Model + Trans + Fuel; Property: Type + Location)
# - Favorite (❤️) Heart button in the Card Footer next to Price (NEVER over image)
# - Perfectly aligned 3-row compact Teal Header with pt-40 main padding
# - Telegram-native floating bottom navigation bar
# - AI Smart Filter Modal & Bottom-Sheet Detail Modal with Call, Telegram, & Share
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
# SELLER FORM HTML (Dynamic Single-Language with AM | EN Switcher)
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
    .chip-active { background:#16acbd; color:#fff; font-weight:700; box-shadow:0 2px 6px rgba(22,172,189,.35); border: 1px solid #16acbd; }
    .chip-idle { background:#ffffff; color:#334155; border:1px solid #cbd5e1; font-weight: 600; }
    input, textarea, select { font-size: 15px !important; }
  </style>
</head>
<body class="bg-[#b5eff3] min-h-screen text-slate-800">
  <div id="root"></div>
  <script type="text/babel">
    const { useState, useRef } = React;
    const tg = (window.Telegram && window.Telegram.WebApp) ? window.Telegram.WebApp : {
      expand(){}, ready(){}, close(){}, initDataUnsafe: {}, setHeaderColor(){}, setBackgroundColor(){}
    };
    try { tg.ready(); tg.expand(); } catch (e) {}
    try { tg.setHeaderColor('#16acbd'); tg.setBackgroundColor('#b5eff3'); } catch (e) {}

    const user = tg.initDataUnsafe?.user || {};
    const autoUsername = user.username ? '@' + user.username : '';
    const autoPhone = user.phone_number || '';

    const I18N = {
      am: {
        title: "ማስታወቂያ ልቀቅ",
        step: "ደረጃ",
        steps: ["መረጃ", "ዋጋና ፎቶ", "አድራሻ"],
        category: "ምድብ",
        car: "መኪና",
        property: "ቤት",
        carModel: "የመኪና ስም / ሞዴል (ለምሳሌ፦ Toyota Vitz 2020)",
        carType: "የመኪና አይነት",
        fuel: "የነዳጅ አይነት",
        transmission: "ማርሽ",
        condition: "ሁኔታ",
        mileage: "ኪሎሜትር (KM)",
        propertyType: "የቤት አይነት",
        locationArea: "አካባቢ / ቦታ (ለምሳሌ፦ ቦሌ፣ ሲኤምሲ)",
        bedrooms: "መኝታ ክፍሎች",
        bathrooms: "መታጠቢያ ክፍሎች",
        parking: "የመኪና ማቆሚያ አለው",
        desc: "ሙሉ ዝርዝር መግለጫ",
        descPh: "ስለ ንብረቱ ተጨማሪ መረጃ፣ ሞዴል፣ ገፅታዎች ይግለጹ...",
        price: "ዋጋ (ብር)",
        negotiable: "የሚደራደር ዋጋ",
        urgent: "አስቸኳይ ሽያጭ",
        photos: "ፎቶዎች (እስከ 5)",
        upload: "ፎቶ ይስቀሉ",
        phone: "ስልክ ቁጥር",
        telegram: "የቴሌግራም ስም",
        back: "ተመለስ",
        cancel: "ሰርዝ",
        next: "ቀጣይ",
        submit: "ማስታወቂያ መዝግብ",
        submitting: "በመመዝገብ ላይ...",
        successTitle: "ማስታወቂያዎ ተመዝግቧል!",
        successMsg: "ንብረትዎ ለተረጋገጡ ደላሎችና ገዢዎች ተሰራጭቷል።",
        closing: "ይዘጋል..."
      },
      en: {
        title: "Post Listing",
        step: "Step",
        steps: ["Details", "Price & Media", "Contact"],
        category: "Category",
        car: "Vehicle",
        property: "Property",
        carModel: "Car Make / Model (e.g. Toyota Vitz 2020)",
        carType: "Vehicle Type",
        fuel: "Fuel Type",
        transmission: "Transmission",
        condition: "Condition",
        mileage: "Mileage (KM)",
        propertyType: "Property Type",
        locationArea: "Location / Neighborhood (e.g. Bole, CMC)",
        bedrooms: "Bedrooms",
        bathrooms: "Bathrooms",
        parking: "Dedicated Parking",
        desc: "Full Description",
        descPh: "Describe the item, location, key features, specs...",
        price: "Price (ETB)",
        negotiable: "Negotiable Price",
        urgent: "Urgent Sale",
        photos: "Photos (Up to 5)",
        upload: "Upload Photos",
        phone: "Phone Number",
        telegram: "Telegram Username",
        back: "Back",
        cancel: "Cancel",
        next: "Next",
        submit: "Submit Listing",
        submitting: "Submitting...",
        successTitle: "Successfully Posted!",
        successMsg: "Your listing has been submitted and broadcasted to verified brokers.",
        closing: "Closing..."
      }
    };

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
          className={`px-3 py-1.5 rounded-full text-xs whitespace-nowrap transition-all shadow-sm ${
            active
              ? (danger ? 'bg-rose-500 text-white font-bold' : 'chip-active')
              : 'chip-idle hover:bg-slate-50'
          }`}>
          {label}
        </button>
      );
    }

    function ToggleCard({ active, onToggle, icon, label, danger }) {
      return (
        <button type="button" onClick={onToggle}
          className={`w-full flex items-center justify-between p-3 rounded-2xl border transition-all text-left bg-white shadow-[0_4px_14px_rgba(15,23,42,0.06)] ${
            active
              ? (danger ? 'border-rose-300 text-rose-700 bg-rose-50/50' : 'border-[#16acbd]/40 text-[#0e7490] bg-[#16acbd]/5')
              : 'border-slate-200/80 text-slate-700'
          }`}>
          <div className="flex items-center gap-2">
            <span className="text-base">{icon}</span>
            <div className="text-xs font-bold text-slate-800">{label}</div>
          </div>
          <div className={`w-10 h-5 rounded-full relative transition-colors ${active ? (danger ? 'bg-rose-500' : 'bg-[#16acbd]') : 'bg-slate-300'}`}>
            <div className={`absolute top-0.5 w-4 h-4 rounded-full bg-white shadow transition-transform ${active ? 'translate-x-5' : 'translate-x-0.5'}`} />
          </div>
        </button>
      );
    }

    function SellerForm() {
      const [lang, setLang] = useState('am');
      const t = I18N[lang];

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
          if (!file || file.size > 8 * 1024 * 1024) return reject(new Error('Image too large (max 8MB)'));
          const reader = new FileReader();
          reader.onerror = () => reject(new Error('Failed to read photo'));
          reader.onload = (e) => {
            const img = new Image();
            img.onerror = () => reject(new Error('Invalid image'));
            img.onload = () => {
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
            setStatus(result.message || 'Error occurred');
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
              <h2 className="font-bold text-base text-slate-800">{t.successTitle}</h2>
              <p className="font-medium text-xs text-slate-600 leading-relaxed px-2">
                {t.successMsg}
              </p>
              <p className="text-[11px] text-[#16acbd] font-semibold">{t.closing}</p>
            </div>
          </div>
        );
      }

      return (
        <div className="min-h-screen bg-[#b5eff3] pb-24">
          <div className="fixed top-0 left-0 right-0 z-40 bg-[#16acbd] shadow-md px-4 py-2.5 text-white">
            <div className="flex items-center justify-between max-w-xs mx-auto mb-1.5">
              <div className="font-extrabold text-xs tracking-wide">{t.title}</div>
              <div className="flex items-center gap-1.5">
                <button type="button" onClick={() => setLang(lang === 'am' ? 'en' : 'am')}
                  className="px-2 py-0.5 bg-white/20 hover:bg-white/30 rounded-full text-[10px] font-extrabold">
                  {lang === 'am' ? 'EN' : 'አማ'}
                </button>
                <div className="text-[10px] bg-white/20 px-2 py-0.5 rounded-full font-bold">{t.step} {step}/3</div>
              </div>
            </div>
            <div className="flex items-center gap-1 max-w-xs mx-auto">
              {t.steps.map((label, i) => (
                <React.Fragment key={label}>
                  <div className="flex-1 text-center">
                    <div className={`mx-auto w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold ${
                      step > i+1 ? 'bg-white text-[#16acbd]' : step === i+1 ? 'bg-white text-[#16acbd] ring-2 ring-white/50' : 'bg-white/30 text-white'
                    }`}>{i+1}</div>
                  </div>
                  {i < 2 && <div className={`h-0.5 flex-1 rounded ${step > i+1 ? 'bg-white' : 'bg-white/30'}`} />}
                </React.Fragment>
              ))}
            </div>
          </div>

          <div className="pt-20 px-3.5">
            <div className="bg-white rounded-2xl p-4 shadow-[0_12px_28px_rgba(15,23,42,0.12)] border border-slate-200/80 space-y-4">
              {step === 1 && (
                <div className="space-y-3.5">
                  <div>
                    <label className="text-xs font-bold text-slate-700 mb-1.5 block">📦 {t.category}</label>
                    <div className="flex gap-2">
                      <Chip label={`🚗 ${t.car}`} active={category==='መኪና'} onClick={() => setCategory('መኪና')} />
                      <Chip label={`🏠 ${t.property}`} active={category==='ቤት'} onClick={() => setCategory('ቤት')} />
                    </div>
                  </div>

                  {category === 'መኪና' ? (
                    <>
                      <div>
                        <label className="text-xs font-bold text-slate-700 mb-1 block">🚘 {t.carModel}</label>
                        <input type="text" value={carModel} onChange={e => setCarModel(e.target.value)}
                          placeholder="e.g. Toyota Vitz 2020 / Hyundai Tucson"
                          className="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-200 focus:bg-white focus:ring-2 focus:ring-[#16acbd] outline-none text-xs font-bold" />
                      </div>
                      <div>
                        <label className="text-xs font-bold text-slate-700 mb-1 block">🚗 {t.carType}</label>
                        <div className="flex gap-1.5 overflow-x-auto pb-1">
                          {['Sedan','SUV / 4WD','Commercial','Heavy Duty'].map(typeKey =>
                            <Chip key={typeKey} label={typeKey} active={carType===typeKey} onClick={() => setCarType(typeKey)} />
                          )}
                        </div>
                      </div>
                      <div>
                        <label className="text-xs font-bold text-slate-700 mb-1 block">⛽ {t.fuel}</label>
                        <div className="flex gap-1.5 overflow-x-auto pb-1">
                          {['Petrol / ቤንዚን','Diesel / ናፍጣ','Electric / ኤሌክትሪክ','Hybrid / ሀይብሪድ'].map(f =>
                            <Chip key={f} label={f} active={fuel===f} onClick={() => setFuel(f)} />
                          )}
                        </div>
                      </div>
                      <div>
                        <label className="text-xs font-bold text-slate-700 mb-1 block">⚙️ {t.transmission}</label>
                        <div className="flex gap-2">
                          {['Automatic','Manual'].map(tr =>
                            <Chip key={tr} label={tr} active={transmission===tr} onClick={() => setTransmission(tr)} />
                          )}
                        </div>
                      </div>
                      <div>
                        <label className="text-xs font-bold text-slate-700 mb-1 block">📊 {t.condition}</label>
                        <div className="flex gap-1.5 overflow-x-auto pb-1">
                          {['Brand New','Clean Used','Need Repair'].map(c =>
                            <Chip key={c} label={c} active={condition===c} onClick={() => setCondition(c)} />
                          )}
                        </div>
                      </div>
                      <div>
                        <label className="text-xs font-bold text-slate-700 mb-1 block">🛣️ {t.mileage}</label>
                        <input type="number" value={mileage} onChange={e => setMileage(e.target.value)}
                          placeholder="45000"
                          className="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-200 focus:bg-white focus:ring-2 focus:ring-[#16acbd] outline-none text-xs" />
                      </div>
                    </>
                  ) : (
                    <>
                      <div>
                        <label className="text-xs font-bold text-slate-700 mb-1 block">🏠 {t.propertyType}</label>
                        <div className="flex gap-1.5 overflow-x-auto pb-1">
                          {['Villa','Apartment','Condominium','Commercial','Land'].map(h =>
                            <Chip key={h} label={h} active={houseType===h} onClick={() => setHouseType(h)} />
                          )}
                        </div>
                      </div>
                      <div>
                        <label className="text-xs font-bold text-slate-700 mb-1 block">📍 {t.locationArea}</label>
                        <input type="text" value={locationArea} onChange={e => setLocationArea(e.target.value)}
                          placeholder="e.g. Bole Atlas, CMC, Kazanchis, 150m²"
                          className="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-200 focus:bg-white focus:ring-2 focus:ring-[#16acbd] outline-none text-xs font-bold" />
                      </div>
                      <div>
                        <label className="text-xs font-bold text-slate-700 mb-1 block">🛏️ {t.bedrooms}</label>
                        <div className="flex gap-1.5">
                          {['1','2','3','4','5+'].map(b =>
                            <Chip key={b} label={b} active={bedrooms===b} onClick={() => setBedrooms(b)} />
                          )}
                        </div>
                      </div>
                      <div>
                        <label className="text-xs font-bold text-slate-700 mb-1 block">🛁 {t.bathrooms}</label>
                        <div className="flex gap-1.5">
                          {['1','2','3','4+'].map(ba =>
                            <Chip key={ba} label={ba} active={bathrooms===ba} onClick={() => setBathrooms(ba)} />
                          )}
                        </div>
                      </div>
                      <ToggleCard active={parking} onToggle={() => setParking(!parking)} icon="🚗" label={t.parking} />
                    </>
                  )}

                  <div>
                    <label className="text-xs font-bold text-slate-700 mb-1 block">📝 {t.desc}</label>
                    <textarea value={description} onChange={e => setDescription(e.target.value)} rows={3}
                      placeholder={t.descPh}
                      className="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-200 focus:bg-white focus:ring-2 focus:ring-[#16acbd] outline-none text-xs resize-none" />
                  </div>
                </div>
              )}

              {step === 2 && (
                <div className="space-y-3.5">
                  <div>
                    <label className="text-xs font-bold text-slate-700 mb-1 block">💰 {t.price}</label>
                    <div className="relative">
                      <input type="text" inputMode="numeric" value={price}
                        onChange={e => setPrice(formatPrice(e.target.value))}
                        placeholder="2,500,000"
                        className="w-full px-3 py-2.5 rounded-xl bg-slate-50 border border-slate-200 focus:bg-white focus:ring-2 focus:ring-[#16acbd] outline-none text-xs font-bold text-slate-900" />
                      <span className="absolute right-3 top-1/2 -translate-y-1/2 text-xs font-bold text-[#16acbd]">ETB</span>
                    </div>
                  </div>
                  <ToggleCard active={negotiable} onToggle={() => setNegotiable(!negotiable)} icon="🤝" label={t.negotiable} />
                  <ToggleCard active={urgent} onToggle={() => setUrgent(!urgent)} icon="⚡" label={t.urgent} danger />

                  <div>
                    <label className="text-xs font-bold text-slate-700 mb-1 block">📸 {t.photos}</label>
                    <div onClick={() => fileRef.current?.click()}
                      className="border-2 border-dashed border-slate-200 bg-slate-50/70 hover:bg-slate-50 rounded-2xl p-5 text-center cursor-pointer transition-all">
                      <div className="text-2xl mb-1">📷</div>
                      <p className="text-xs font-bold text-slate-700">{t.upload}</p>
                      <input ref={fileRef} type="file" accept="image/*" multiple className="hidden"
                        onChange={e => { addFiles(e.target.files); e.target.value=''; }} />
                    </div>
                    {photoBusy && <p className="text-[11px] text-[#16acbd] font-semibold mt-1 text-center">Optimizing images…</p>}
                    {photoError && <p className="text-[11px] text-rose-600 font-semibold mt-1 text-center">{photoError}</p>}
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
                    <label className="text-xs font-bold text-slate-700 mb-1 block">📞 {t.phone}</label>
                    <input type="tel" value={phone} onChange={e => setPhone(e.target.value)}
                      placeholder="0911223344"
                      className="w-full px-3 py-2.5 rounded-xl bg-slate-50 border border-slate-200 focus:bg-white focus:ring-2 focus:ring-[#16acbd] outline-none text-xs font-bold" />
                  </div>
                  <div>
                    <label className="text-xs font-bold text-slate-700 mb-1 block">📱 {t.telegram}</label>
                    <input type="text" value={telegramUser} onChange={e => setTelegramUser(e.target.value)}
                      placeholder="@username"
                      className="w-full px-3 py-2.5 rounded-xl bg-slate-50 border border-slate-200 focus:bg-white focus:ring-2 focus:ring-[#16acbd] outline-none text-xs font-bold" />
                  </div>
                  {status && status !== 'ok' && (
                    <p className="text-xs text-rose-600 font-bold text-center">{status}</p>
                  )}
                </div>
              )}
            </div>
          </div>

          <div className="fixed bottom-0 left-0 right-0 p-3 bg-white/95 backdrop-blur-md border-t border-slate-200 flex gap-2 z-40">
            {step > 1 ? (
              <button type="button" onClick={() => setStep(s => s-1)}
                className="w-1/3 py-2.5 rounded-xl bg-slate-100 text-slate-700 font-bold text-xs active:scale-95">{t.back}</button>
            ) : (
              <button type="button" onClick={() => tg.close()}
                className="w-1/3 py-2.5 rounded-xl bg-slate-100 text-slate-700 font-bold text-xs active:scale-95">{t.cancel}</button>
            )}
            {step < 3 ? (
              <button type="button" onClick={() => { if (step===1 && !canNext1) return; setStep(s => s+1); }}
                disabled={step===1 ? !canNext1 : photoBusy}
                className="flex-1 py-2.5 rounded-xl bg-[#16acbd] text-white font-bold text-xs shadow-md active:scale-95 disabled:opacity-40">
                {t.next} →
              </button>
            ) : (
              <button type="button" onClick={submit} disabled={!canSubmit || submitting}
                className="flex-1 py-2.5 rounded-xl bg-[#16acbd] text-white font-bold text-xs shadow-md active:scale-95 disabled:opacity-40 flex items-center justify-center gap-1">
                {submitting ? t.submitting : `🚀 ${t.submit}`}
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
# BUYER FORM HTML (Dynamic Single-Language with AM | EN Switcher)
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
    .chip-active { background:#16acbd; color:#fff; font-weight:700; box-shadow:0 2px 6px rgba(22,172,189,.35); border: 1px solid #16acbd; }
    .chip-idle { background:#ffffff; color:#334155; border:1px solid #cbd5e1; font-weight: 600; }
    input, textarea { font-size: 15px !important; }
  </style>
</head>
<body class="bg-[#b5eff3] min-h-screen text-slate-800">
  <div id="root"></div>
  <script type="text/babel">
    const { useState } = React;
    const tg = (window.Telegram && window.Telegram.WebApp) ? window.Telegram.WebApp : {
      expand(){}, ready(){}, close(){}, initDataUnsafe: {}, setHeaderColor(){}, setBackgroundColor(){}
    };
    try { tg.ready(); tg.expand(); } catch (e) {}
    try { tg.setHeaderColor('#16acbd'); tg.setBackgroundColor('#b5eff3'); } catch (e) {}

    const user = tg.initDataUnsafe?.user || {};
    const autoUsername = user.username ? '@' + user.username : '';
    const autoPhone = user.phone_number || '';

    const I18N = {
      am: {
        title: "የሚፈልጉትን ንብረት ይግለጹ",
        category: "ምድብ",
        car: "መኪና",
        property: "ቤት",
        budget: "የበጀት ክልል (ብር)",
        alertTitle: "ፈጣን ማሳወቂያ",
        alertSub: "ተመሳሳይ ንብረት ሲለቀቅ ማሳወቂያ ይድረሰኝ",
        details: "ዝርዝር ፍላጎትና መስፈርቶች",
        detailsPh: "ለምሳሌ፦ ቶዮታ ቪትዝ 2020፣ ነጭ ቀለም፣ ኦቶማቲክ፣ ንጹህ...",
        phone: "ስልክ ቁጥር",
        telegram: "ቴሌግራም",
        cancel: "ሰርዝ",
        submit: "ጥያቄውን ላክ",
        submitting: "በመላክ ላይ...",
        successTitle: "ጥያቄዎ ተመዝግቧል!",
        successMsg: "የፍላጎት ጥያቄዎ ለተረጋገጡ ደላሎች ተሰራጭቷል።",
        closing: "ይዘጋል..."
      },
      en: {
        title: "Submit Buyer Request",
        category: "Category",
        car: "Vehicle",
        property: "Property",
        budget: "Budget Range (ETB)",
        alertTitle: "Instant Match Alert",
        alertSub: "Notify me when matching listings are posted",
        details: "Specifications & Details",
        detailsPh: "e.g. Looking for Toyota Vitz 2020, white, automatic, clean condition...",
        phone: "Phone Number",
        telegram: "Telegram",
        cancel: "Cancel",
        submit: "Broadcast Request",
        submitting: "Broadcasting...",
        successTitle: "Request Broadcasted!",
        successMsg: "Your request has been saved and shared with certified brokers.",
        closing: "Closing..."
      }
    };

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
          className={`px-3 py-1.5 rounded-full text-xs whitespace-nowrap transition-all shadow-sm ${active ? 'chip-active' : 'chip-idle hover:bg-slate-50'}`}>
          {label}
        </button>
      );
    }

    function BuyerForm() {
      const [lang, setLang] = useState('am');
      const t = I18N[lang];

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
              <h2 className="font-bold text-base text-slate-800">{t.successTitle}</h2>
              <p className="font-medium text-xs text-slate-600 leading-relaxed px-2">
                {t.successMsg}
              </p>
              <p className="text-[11px] text-[#16acbd] font-semibold">{t.closing}</p>
            </div>
          </div>
        );
      }

      return (
        <div className="min-h-screen bg-[#b5eff3] pb-24">
          <div className="fixed top-0 left-0 right-0 z-40 bg-[#16acbd] shadow-md px-4 py-2.5 text-white flex items-center justify-between">
            <h1 className="font-extrabold text-xs tracking-wide">{t.title}</h1>
            <button type="button" onClick={() => setLang(lang === 'am' ? 'en' : 'am')}
              className="px-2 py-0.5 bg-white/20 hover:bg-white/30 rounded-full text-[10px] font-extrabold">
              {lang === 'am' ? 'EN' : 'አማ'}
            </button>
          </div>

          <div className="pt-14 px-3.5">
            <div className="bg-white rounded-2xl p-4 shadow-[0_12px_28px_rgba(15,23,42,0.12)] border border-slate-200/80 space-y-3.5">
              <div>
                <label className="text-xs font-bold text-slate-700 mb-1 block">📦 {t.category}</label>
                <div className="flex gap-2">
                  <Chip label={`🚗 ${t.car}`} active={category==='መኪና'} onClick={() => setCategory('መኪና')} />
                  <Chip label={`🏠 ${t.property}`} active={category==='ቤት'} onClick={() => setCategory('ቤት')} />
                </div>
              </div>

              <div>
                <label className="text-xs font-bold text-slate-700 mb-1 block">💰 {t.budget}</label>
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
                  <div>🔔 {t.alertTitle}</div>
                  <div className="text-[10px] text-slate-500">{t.alertSub}</div>
                </div>
                <div className={`w-9 h-5 rounded-full relative transition-colors shrink-0 ${createAlert ? 'bg-[#16acbd]' : 'bg-slate-300'}`}>
                  <div className={`absolute top-0.5 w-4 h-4 rounded-full bg-white shadow transition-transform ${createAlert ? 'translate-x-4' : 'translate-x-0.5'}`} />
                </div>
              </button>

              <div>
                <label className="text-xs font-bold text-slate-700 mb-1 block">📝 {t.details}</label>
                <textarea value={details} onChange={e => setDetails(e.target.value)} rows={3}
                  placeholder={t.detailsPh}
                  className="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-200 focus:bg-white focus:ring-2 focus:ring-[#16acbd] outline-none text-xs resize-none" />
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-xs font-bold text-slate-700 mb-1 block">📞 {t.phone}</label>
                  <input type="tel" value={phone} onChange={e => setPhone(e.target.value)}
                    placeholder="0911223344"
                    className="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-200 focus:bg-white focus:ring-2 focus:ring-[#16acbd] outline-none text-xs font-bold" />
                </div>
                <div>
                  <label className="text-xs font-bold text-slate-700 mb-1 block">📱 {t.telegram}</label>
                  <input type="text" value={telegramUser} onChange={e => setTelegramUser(e.target.value)}
                    placeholder="@username"
                    className="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-200 focus:bg-white focus:ring-2 focus:ring-[#16acbd] outline-none text-xs font-bold" />
                </div>
              </div>

              {status && status !== 'ok' && (
                <p className="text-xs text-rose-600 font-bold text-center">{status}</p>
              )}
            </div>
          </div>

          <div className="fixed bottom-0 left-0 right-0 p-3 bg-white/95 backdrop-blur-md border-t border-slate-200 flex gap-2 z-40">
            <button type="button" onClick={() => tg.close()}
              className="w-1/3 py-2.5 rounded-xl bg-slate-100 text-slate-700 font-bold text-xs active:scale-95">{t.cancel}</button>
            <button type="button" onClick={submit} disabled={!details || submitting}
              className="flex-1 py-2.5 rounded-xl bg-[#16acbd] text-white font-bold text-xs shadow-md active:scale-95 disabled:opacity-40 flex items-center justify-center gap-1">
              {submitting ? t.submitting : `📨 ${t.submit}`}
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
# EXPLORER HTML (Marketplace + Pure Single-Language AM|EN + Dynamic Cards)
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

    .adika-card {
      background: #ffffff;
      border: 1px solid rgba(226, 232, 240, 0.85);
      border-radius: 1rem;
      box-shadow: 0 12px 28px rgba(15, 23, 42, 0.12);
      transition: transform 0.12s ease, box-shadow 0.12s ease;
      display: flex;
      flex-direction: column;
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
  <!-- 1. FIXED STICKY TEAL HEADER WITH AM | EN TOGGLE, SEARCH & PILLS   -->
  <!-- ================================================================= -->
  <header class="fixed top-0 left-0 right-0 z-50 bg-[#16acbd] text-white shadow-md p-2 flex flex-col gap-2">
    <div class="w-full max-w-md mx-auto flex flex-col gap-2">
      <!-- Top Row: Segmented Switcher + AM | EN Language Switcher -->
      <div class="flex items-center gap-2">
        <div class="flex-1 grid grid-cols-2 gap-1 p-1 bg-black/15 rounded-xl">
          <button id="tabSell" type="button"
            class="py-1.5 rounded-lg text-xs font-bold transition-all bg-white text-[#16acbd] shadow-sm flex items-center justify-center gap-1">
            <span>🛒</span> <span id="txtTabSell">ገበያ</span>
          </button>
          <button id="tabBuy" type="button"
            class="py-1.5 rounded-lg text-xs font-bold transition-all text-white/90 hover:text-white flex items-center justify-center gap-1">
            <span>📋</span> <span id="txtTabBuy">ፈላጊዎች</span>
          </button>
        </div>

        <!-- Language Toggle Switcher (AM | EN) -->
        <div class="flex items-center bg-black/20 p-1 rounded-xl shrink-0">
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
        <input id="q" type="search" placeholder="ንብረት ይፈልጉ..." autocomplete="off"
          class="w-full pl-8 pr-3 py-2 rounded-xl bg-white text-slate-800 placeholder-slate-400 text-xs font-medium outline-none shadow-sm focus:ring-2 focus:ring-white/50" />
      </div>

      <!-- Third Row: Category Pills (Horizontal Scroll) -->
      <div id="cats" class="flex gap-1.5 overflow-x-auto no-scrollbar pb-0.5"></div>
    </div>
  </header>

  <!-- ================================================================= -->
  <!-- 2. MAIN CONTENT AREA (pt-40 to prevent header clipping)           -->
  <!-- ================================================================= -->
  <main class="w-full max-w-md mx-auto pt-40 pb-28 px-2.5">
    <!-- Active Filter Banner -->
    <div id="filterBanner" class="hidden mb-2 px-3 py-1.5 bg-white/90 backdrop-blur-sm rounded-xl border border-white flex items-center justify-between text-xs shadow-sm">
      <span id="filterText" class="font-bold text-[#0e7490] truncate"></span>
      <button id="clearFilterBtn" type="button" class="text-rose-600 font-bold ml-2 shrink-0">✕</button>
    </div>

    <div id="status" class="text-center py-12 text-slate-600 font-semibold text-xs">
      <div class="inline-block animate-spin w-6 h-6 border-2 border-[#16acbd] border-t-transparent rounded-full mb-2"></div>
      <div id="txtLoading">እየጫነ ነው…</div>
    </div>

    <!-- 2-Column Responsive Elevated Cards Grid -->
    <div id="grid" class="grid grid-cols-2 gap-2"></div>

    <!-- Load More -->
    <div class="text-center mt-4 mb-2">
      <button id="more" type="button"
        class="hidden px-5 py-2 rounded-full bg-white text-[#16acbd] font-extrabold text-xs shadow-md border border-white/60 active:scale-95 transition-all">
        <span id="txtLoadMore">ተጨማሪ ↓</span>
      </button>
    </div>
  </main>

  <!-- ================================================================= -->
  <!-- 3. FLOATING TRANSLUCENT BOTTOM NAVIGATION WITH AI & DYNAMIC "+"   -->
  <!-- ================================================================= -->
  <nav class="fixed bottom-4 left-4 right-4 max-w-md mx-auto bg-white/95 backdrop-blur-xl rounded-full shadow-2xl border border-white/60 p-2 z-40 flex items-center justify-around">
    <!-- Home Tab -->
    <button id="navHome" type="button" class="nav-item flex flex-col items-center justify-center px-2 py-1 rounded-full bg-[#16acbd]/15 text-[#16acbd] transition-all">
      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/>
      </svg>
      <span id="txtNavHome" class="text-[9px] font-bold mt-0.5">መነሻ</span>
    </button>

    <!-- AI Smart Filter Tab -->
    <button id="navAi" type="button" class="nav-item flex flex-col items-center justify-center px-2 py-1 rounded-full text-slate-500 hover:text-slate-800 transition-all">
      <div class="relative">
        <svg class="w-4 h-4 text-[#16acbd]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
        </svg>
        <span class="absolute -top-1 -right-1 w-1.5 h-1.5 rounded-full bg-amber-400 animate-ping"></span>
      </div>
      <span id="txtNavAi" class="text-[9px] font-semibold mt-0.5 text-[#0e7490]">AI ፍለጋ ✨</span>
    </button>

    <!-- Central Dynamic "+" FAB -->
    <button id="fabBtn" type="button"
      class="w-11 h-11 -my-2 rounded-full bg-[#16acbd] text-white flex items-center justify-center shadow-[0_6px_18px_rgba(22,172,189,0.45)] active:scale-90 transition-all border-2 border-white">
      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.8" d="M12 4v16m8-8H4"/>
      </svg>
    </button>

    <!-- Messages Tab -->
    <button id="navMessages" type="button" class="nav-item flex flex-col items-center justify-center px-2 py-1 rounded-full text-slate-500 hover:text-slate-800 transition-all">
      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"/>
      </svg>
      <span id="txtNavMsg" class="text-[9px] font-semibold mt-0.5">መልእክት</span>
    </button>

    <!-- Help Tab -->
    <button id="navHelp" type="button" class="nav-item flex flex-col items-center justify-center px-2 py-1 rounded-full text-slate-500 hover:text-slate-800 transition-all">
      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
      </svg>
      <span id="txtNavHelp" class="text-[9px] font-semibold mt-0.5">እርዳታ</span>
    </button>
  </nav>

  <!-- ================================================================= -->
  <!-- 4. DEDICATED AI SMART FILTER MODAL                                -->
  <!-- ================================================================= -->
  <div id="aiModal" class="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm hidden items-end justify-center">
    <div class="w-full max-w-md bg-white rounded-t-3xl max-h-[85vh] flex flex-col shadow-2xl overflow-hidden animate-in slide-in-from-bottom duration-200">
      <div class="px-4 py-3 bg-[#16acbd] text-white flex items-center justify-between shrink-0">
        <div class="flex items-center gap-2">
          <span class="text-lg">✨</span>
          <div>
            <h3 id="txtAiTitle" class="font-extrabold text-xs tracking-wide">AI Smart Filter</h3>
            <p id="txtAiSubtitle" class="text-[10px] text-white/80">በተፈጥሮአዊ ቋንቋ ወይም በቅንብሮች ይፈልጉ</p>
          </div>
        </div>
        <button id="aiModalClose" type="button" class="w-7 h-7 rounded-full bg-white/20 hover:bg-white/30 text-white font-bold flex items-center justify-center text-sm">✕</button>
      </div>

      <div class="overflow-y-auto flex-1 p-4 space-y-4">
        <div>
          <label id="txtAiPromptLabel" class="text-xs font-bold text-slate-700 mb-1 block">ምን አይነት ንብረት ይፈልጋሉ?</label>
          <textarea id="aiPrompt" rows="2"
            placeholder="ለምሳሌ፦ ቶዮታ መኪና ከ1.5 ሚሊየን ብር በታች..."
            class="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-200 focus:bg-white focus:ring-2 focus:ring-[#16acbd] outline-none text-xs resize-none"></textarea>
        </div>

        <div>
          <label id="txtAiQuickLabel" class="text-xs font-bold text-slate-700 mb-1.5 block">ፈጣን አማራጮች</label>
          <div class="flex flex-wrap gap-1.5" id="aiQuickChips"></div>
        </div>

        <div>
          <label id="txtAiPriceLabel" class="text-xs font-bold text-slate-700 mb-1.5 block">የበጀት መጠን</label>
          <div class="grid grid-cols-3 gap-1.5 text-xs">
            <button type="button" class="price-chip py-1.5 px-2 rounded-lg border border-slate-200 text-slate-700 font-semibold text-center hover:border-[#16acbd]" data-price="< 1M">&lt; 1M ETB</button>
            <button type="button" class="price-chip py-1.5 px-2 rounded-lg border border-slate-200 text-slate-700 font-semibold text-center hover:border-[#16acbd]" data-price="1M - 3M">1M - 3M ETB</button>
            <button type="button" class="price-chip py-1.5 px-2 rounded-lg border border-slate-200 text-slate-700 font-semibold text-center hover:border-[#16acbd]" data-price="> 3M">&gt; 3M ETB</button>
          </div>
        </div>
      </div>

      <div class="p-3 bg-white border-t border-slate-100 shrink-0 flex gap-2">
        <button id="aiResetBtn" type="button" class="w-1/3 py-2.5 rounded-xl bg-slate-100 text-slate-700 font-bold text-xs">አጽዳ</button>
        <button id="aiApplyBtn" type="button" class="flex-1 py-2.5 rounded-xl bg-[#16acbd] text-white font-bold text-xs shadow-md active:scale-95 flex items-center justify-center gap-1.5">
          <span>✨ አጣራ</span>
        </button>
      </div>
    </div>
  </div>

  <!-- ================================================================= -->
  <!-- 5. BOTTOM-SHEET DETAIL MODAL WITH SHARE BUTTON                    -->
  <!-- ================================================================= -->
  <div id="modalOverlay" class="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm hidden items-end justify-center">
    <div id="modalSheet"
      class="w-full max-w-md bg-white rounded-t-3xl max-h-[85vh] flex flex-col shadow-2xl overflow-hidden animate-in slide-in-from-bottom duration-200">

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
          <h4 id="modalDescHeading" class="text-[11px] font-bold text-slate-500 uppercase tracking-wider mb-1">ዝርዝር መግለጫ</h4>
          <p id="modalDesc" class="text-xs text-slate-700 leading-relaxed whitespace-pre-line bg-slate-50/50 p-2.5 rounded-xl border border-slate-100"></p>
        </div>
      </div>

      <!-- Pinned 3 Action Buttons (Call, Telegram, Share) -->
      <div class="p-2.5 bg-white border-t border-slate-100 shrink-0 grid grid-cols-3 gap-2">
        <a id="modalCallBtn" href="#"
          class="flex items-center justify-center gap-1 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs shadow-sm active:scale-95 transition-all">
          <span>📞</span> <span id="txtModalCall">ደውል</span>
        </a>
        <a id="modalChatBtn" href="#"
          class="flex items-center justify-center gap-1 py-2.5 rounded-xl bg-[#16acbd] hover:bg-[#1394a3] text-white font-bold text-xs shadow-sm active:scale-95 transition-all">
          <span>💬</span> <span>Telegram</span>
        </a>
        <button id="modalShareBtn" type="button"
          class="flex items-center justify-center gap-1 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-900 text-white font-bold text-xs shadow-sm active:scale-95 transition-all">
          <span>🔗</span> <span id="txtModalShare">አጋራ</span>
        </button>
      </div>
    </div>
  </div>

  <!-- ================================================================= -->
  <!-- 6. JAVASCRIPT LOGIC WITH DYNAMIC SINGLE-LANGUAGE SWITCHER         -->
  <!-- ================================================================= -->
  <script>
  (function () {
    var tg = window.Telegram && window.Telegram.WebApp ? window.Telegram.WebApp : null;
    if (tg) {
      try { tg.ready(); tg.expand(); tg.setHeaderColor('#16acbd'); tg.setBackgroundColor('#b5eff3'); } catch (e) {}
    }

    var currentLang = localStorage.getItem('adika_lang') || 'am';

    var DICT = {
      am: {
        tabSell: "ገበያ",
        tabBuy: "ፈላጊዎች",
        searchPh: "ንብረት ይፈልጉ...",
        loading: "እየጫነ ነው…",
        noListings: "ምንም ንብረት አልተገኘም",
        loadMore: "ተጨማሪ ↓",
        navHome: "መነሻ",
        navAi: "AI ፍለጋ ✨",
        navMsg: "መልእክት",
        navHelp: "እርዳታ",
        aiTitle: "AI Smart Filter",
        aiSubtitle: "በተፈጥሮአዊ ቋንቋ ወይም በቅንብሮች ይፈልጉ",
        aiPromptLabel: "ምን አይነት ንብረት ይፈልጋሉ?",
        aiPromptPh: "ለምሳሌ፦ ቶዮታ መኪና ከ1.5 ሚሊየን ብር በታች...",
        aiQuickLabel: "ፈጣን አማራጮች",
        aiPriceLabel: "የበጀት መጠን",
        aiReset: "አጽዳ",
        aiApply: "✨ አጣራ",
        modalDescHeading: "ዝርዝር መግለጫ",
        modalCall: "ደውል",
        modalShare: "አጋራ",
        priceTag: "ዋጋ: ",
        budgetTag: "በጀት: ",
        forSale: "ሽያጭ",
        looking: "ፈላጊ",
        justNow: "አሁን",
        noDesc: "ምንም ዝርዝር መግለጫ አልተሰጠም።",
        copied: "ሊንኩ ተገልብጧል!",
        helpAlert: "አዲካ የገበያ መድረክ • የደንበኞች እርዳታ\nለእርዳታ በ @AdikaMarketplaceBot ያግኙን ወይም በ 0911000000 ይደውሉ።",
        cats: [
          { id: "", label: "✨ ሁሉም" },
          { id: "መኪና", label: "🚗 መኪኖች" },
          { id: "ቤት", label: "🏠 ቤቶች" },
          { id: "ንግድ", label: "🏢 ንግድ" }
        ],
        quickChips: [
          { label: "🚗 መኪኖች", q: "መኪና" },
          { label: "🏠 ቤቶች", q: "ቤት" },
          { label: "⚙️ ኦቶማቲክ", q: "ኦቶማቲክ" },
          { label: "✨ አዲስ", q: "አዲስ" },
          { label: "⚡ አስቸኳይ", q: "አስቸኳይ" },
          { label: "🏡 ቪላ", q: "ቪላ" },
          { label: "🚘 ቶዮታ", q: "ቶዮታ" }
        ]
      },
      en: {
        tabSell: "Marketplace",
        tabBuy: "Buyers",
        searchPh: "Search listings...",
        loading: "Loading listings…",
        noListings: "No listings found",
        loadMore: "Load More ↓",
        navHome: "Home",
        navAi: "AI Smart ✨",
        navMsg: "Inbox",
        navHelp: "Help",
        aiTitle: "AI Smart Filter",
        aiSubtitle: "Search in natural language or smart tags",
        aiPromptLabel: "What are you looking for?",
        aiPromptPh: "e.g. Toyota car in Addis under 1.5M ETB...",
        aiQuickLabel: "Quick Smart Tags",
        aiPriceLabel: "Budget Range",
        aiReset: "Reset",
        aiApply: "✨ Apply Filter",
        modalDescHeading: "Full Description",
        modalCall: "Call",
        modalShare: "Share",
        priceTag: "Price: ",
        budgetTag: "Budget: ",
        forSale: "For Sale",
        looking: "Looking",
        justNow: "Just now",
        noDesc: "No further description provided.",
        copied: "Link copied to clipboard!",
        helpAlert: "Adika Marketplace • Help Center\nFor support, contact @AdikaMarketplaceBot or call 0911000000.",
        cats: [
          { id: "", label: "✨ All" },
          { id: "መኪና", label: "🚗 Cars" },
          { id: "ቤት", label: "🏠 Property" },
          { id: "ንግድ", label: "🏢 Commercial" }
        ],
        quickChips: [
          { label: "🚗 Cars", q: "መኪና" },
          { label: "🏠 Property", q: "ቤት" },
          { label: "⚙️ Automatic", q: "Automatic" },
          { label: "✨ Brand New", q: "New" },
          { label: "⚡ Urgent", q: "Urgent" },
          { label: "🏡 Villa", q: "Villa" },
          { label: "🚘 Toyota", q: "Toyota" }
        ]
      }
    };

    var favorites = {};
    try {
      favorites = JSON.parse(localStorage.getItem('adika_favs') || '{}');
    } catch(e) {}

    function toggleFav(id) {
      if (favorites[id]) {
        delete favorites[id];
      } else {
        favorites[id] = true;
      }
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
    var aiQuickChipsEl = document.getElementById("aiQuickChips");

    function applyLanguage(l) {
      currentLang = l;
      localStorage.setItem('adika_lang', l);
      var t = DICT[l];

      document.getElementById("txtTabSell").textContent = t.tabSell;
      document.getElementById("txtTabBuy").textContent = t.tabBuy;
      qInput.placeholder = t.searchPh;
      document.getElementById("txtLoading").textContent = t.loading;
      document.getElementById("txtLoadMore").textContent = t.loadMore;
      document.getElementById("txtNavHome").textContent = t.navHome;
      document.getElementById("txtNavAi").textContent = t.navAi;
      document.getElementById("txtNavMsg").textContent = t.navMsg;
      document.getElementById("txtNavHelp").textContent = t.navHelp;

      document.getElementById("txtAiTitle").textContent = t.aiTitle;
      document.getElementById("txtAiSubtitle").textContent = t.aiSubtitle;
      document.getElementById("txtAiPromptLabel").textContent = t.aiPromptLabel;
      aiPrompt.placeholder = t.aiPromptPh;
      document.getElementById("txtAiQuickLabel").textContent = t.aiQuickLabel;
      document.getElementById("txtAiPriceLabel").textContent = t.aiPriceLabel;
      aiResetBtn.textContent = t.aiReset;
      aiApplyBtn.innerHTML = t.aiApply;

      document.getElementById("modalDescHeading").textContent = t.modalDescHeading;
      document.getElementById("txtModalCall").textContent = t.modalCall;
      document.getElementById("txtModalShare").textContent = t.modalShare;

      if (l === 'am') {
        langAmBtn.className = "px-2 py-1 rounded-lg text-xs font-extrabold transition-all bg-white text-[#16acbd] shadow-sm";
        langEnBtn.className = "px-2 py-1 rounded-lg text-xs font-extrabold transition-all text-white/80 hover:text-white";
      } else {
        langEnBtn.className = "px-2 py-1 rounded-lg text-xs font-extrabold transition-all bg-white text-[#16acbd] shadow-sm";
        langAmBtn.className = "px-2 py-1 rounded-lg text-xs font-extrabold transition-all text-white/80 hover:text-white";
      }

      renderCats();
      renderAiQuickChips();
      if (state.items && state.items.length) {
        finishLoading(state.items, false, state.hasMore);
      }
    }

    langAmBtn.onclick = function() { applyLanguage('am'); };
    langEnBtn.onclick = function() { applyLanguage('en'); };

    function esc(s) {
      return String(s == null ? "" : s)
        .replace(/&/g, "&amp;").replace(/</g, "&lt;")
        .replace(/>/g, "&gt;").replace(/"/g, "&quot;");
    }

    function relativeTime(iso) {
      if (!iso) return "";
      try {
        var secs = Math.max(0, Math.floor((Date.now() - new Date(iso).getTime()) / 1000));
        var t = DICT[currentLang];
        if (secs < 60) return t.justNow;
        if (secs < 3600) return Math.floor(secs / 60) + "m";
        if (secs < 86400) return Math.floor(secs / 3600) + "h";
        return Math.floor(secs / 86400) + "d";
      } catch (e) { return ""; }
    }

    function renderCats() {
      var catList = DICT[currentLang].cats;
      var html = "";
      for (var i = 0; i < catList.length; i++) {
        var c = catList[i];
        var on = (state.category === c.id);
        html += '<button type="button" class="cat-pill px-3 py-1 rounded-full text-xs font-bold whitespace-nowrap transition-all ' +
          (on ? 'bg-white text-[#16acbd] shadow-sm' : 'bg-white/20 text-white hover:bg-white/30') +
          '" data-id="' + esc(c.id) + '">' + esc(c.label) + '</button>';
      }
      catsEl.innerHTML = html;
    }

    function renderAiQuickChips() {
      var chips = DICT[currentLang].quickChips;
      var html = "";
      for (var i = 0; i < chips.length; i++) {
        var ch = chips[i];
        html += '<button type="button" class="ai-chip px-2.5 py-1 rounded-full bg-slate-100 text-slate-700 text-xs font-medium hover:bg-[#16acbd]/10 hover:text-[#0e7490]" data-q="' + esc(ch.q) + '">' + esc(ch.label) + '</button>';
      }
      aiQuickChipsEl.innerHTML = html;
      aiQuickChipsEl.querySelectorAll(".ai-chip").forEach(function(btn) {
        btn.onclick = function() {
          var query = btn.getAttribute("data-q");
          aiPrompt.value = (aiPrompt.value ? aiPrompt.value + " " : "") + query;
        };
      });
    }

    function setTabs() {
      if (state.tab === "marketplace") {
        tabSell.className = "py-1.5 rounded-lg text-xs font-bold transition-all bg-white text-[#16acbd] shadow-sm flex items-center justify-center gap-1";
        tabBuy.className = "py-1.5 rounded-lg text-xs font-bold transition-all text-white/90 hover:text-white flex items-center justify-center gap-1";
      } else {
        tabBuy.className = "py-1.5 rounded-lg text-xs font-bold transition-all bg-white text-[#16acbd] shadow-sm flex items-center justify-center gap-1";
        tabSell.className = "py-1.5 rounded-lg text-xs font-bold transition-all text-white/90 hover:text-white flex items-center justify-center gap-1";
      }
    }

    function renderFavoritesUI() {
      var btns = document.querySelectorAll(".card-fav-btn");
      btns.forEach(function(b) {
        var id = b.getAttribute("data-id");
        if (favorites[id]) {
          b.innerHTML = "❤️";
        } else {
          b.innerHTML = "🤍";
        }
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
      var t = DICT[currentLang];

      var extra = item.extra_data || {};
      if (typeof extra === "string") {
        try { extra = JSON.parse(extra); } catch (e) { extra = {}; }
      }

      // Dynamic Title & Specs based on Category
      var cardTitle = "";
      var subBadge1 = "";
      var subBadge2 = "";

      if (isCar) {
        cardTitle = extra.car_model || item.sub_category || (currentLang === 'am' ? 'መኪና' : 'Vehicle');
        if (extra.transmission) subBadge1 = extra.transmission.split('/')[0].trim();
        if (extra.fuel_type) subBadge2 = extra.fuel_type.split('/')[0].trim();
      } else {
        cardTitle = item.sub_category || extra.house_type || (currentLang === 'am' ? 'ቤት / ንብረት' : 'Property');
        if (extra.bedrooms) subBadge1 = extra.bedrooms + " " + (currentLang === 'am' ? 'መኝታ' : 'Beds');
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

      var isSell = String(item.req_type || "").toUpperCase() === "SELL";
      var priceNum = item.price || "—";
      var priceLabel = priceNum + " ETB";
      var views = item.view_count || item.views_count || 12;
      var isFav = Boolean(favorites[item.id]);

      var card = document.createElement("div");
      card.className = "adika-card cursor-pointer";
      card.innerHTML =
        '<div class="relative w-full h-24 bg-slate-100 overflow-hidden">' +
          media +
          '<div class="absolute bottom-1 left-1 right-1 flex justify-between items-center text-[8px] text-white font-bold">' +
            '<span class="bg-black/60 backdrop-blur-sm px-1.5 py-0.5 rounded">👁️ ' + esc(views) + '</span>' +
            '<span class="bg-black/60 backdrop-blur-sm px-1.5 py-0.5 rounded">' + esc(relativeTime(item.created_at)) + '</span>' +
          '</div>' +
        '</div>' +
        '<div class="p-2 flex-1 flex flex-col justify-between">' +
          '<div>' +
            '<div class="font-extrabold text-xs text-slate-800 truncate flex items-center gap-0.5">' +
              '<span class="truncate">' + esc(cardTitle) + '</span>' +
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
      var t = DICT[currentLang];

      var catBadge = isCar ? (currentLang === 'am' ? 'መኪና' : 'Vehicle') : (currentLang === 'am' ? 'ቤት / ንብረት' : 'Property');
      modalCategoryBadge.textContent = catBadge + " • Verified ✔";
      modalIdBadge.textContent = "#ADK-" + (item.id || "001");

      var modalTitleText = isCar ? (extra.car_model || item.sub_category || catBadge) : (item.sub_category || extra.house_type || catBadge);
      modalTitle.textContent = modalTitleText;

      var isSell = String(item.req_type || "").toUpperCase() === "SELL";
      modalPrice.textContent = (isSell ? t.priceTag : t.budgetTag) + (item.price || "Contact") + " ETB";
      modalTime.textContent = "⏱️ " + relativeTime(item.created_at);
      modalDesc.textContent = item.description || t.noDesc;

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
        var shareText = "Check out " + modalTitle.textContent + " on Adika Marketplace (" + modalPrice.textContent + "): " + shareUrl;
        if (navigator.share) {
          navigator.share({ title: "Adika Marketplace", text: shareText, url: shareUrl }).catch(function(){});
        } else if (tg && tg.openTelegramLink) {
          tg.openTelegramLink("https://t.me/share/url?url=" + encodeURIComponent(shareUrl) + "&text=" + encodeURIComponent(shareText));
        } else {
          navigator.clipboard.writeText(shareText);
          alert(t.copied);
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
          statusEl.innerHTML = '<div class="text-2xl mb-1">📭</div><div class="text-slate-600 font-bold text-xs">' + DICT[currentLang].noListings + '</div>';
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
        statusEl.innerHTML = '<div class="inline-block animate-spin w-5 h-5 border-2 border-[#16acbd] border-t-transparent rounded-full mb-1.5"></div><div>' + DICT[currentLang].loading + '</div>';
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

    document.querySelectorAll(".price-chip").forEach(function(btn) {
      btn.onclick = function() {
        var p = btn.getAttribute("data-price");
        aiPrompt.value = (aiPrompt.value ? aiPrompt.value + " " : "") + p;
      };
    });

    aiApplyBtn.onclick = function() {
      var query = aiPrompt.value.trim();
      if (query) {
        state.q = query;
        qInput.value = query;
        filterText.textContent = "AI Filter: " + query;
        filterBanner.classList.remove("hidden");
      }
      aiModalClose.onclick();
      load(false);
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
      var t = DICT[currentLang];
      if (tg && tg.showAlert) {
        tg.showAlert(t.helpAlert);
      } else {
        alert(t.helpAlert);
      }
    };

    applyLanguage(currentLang);
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
        "<p>Single-Language AI-powered Mini App with AM | EN Language Switcher.</p>"
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


def run_flask():
    port = int(PORT or 8080)
    logger.info("Starting Flask on 0.0.0.0:%s", port)
    web_app.run(host="0.0.0.0", port=port, use_reloader=False, threaded=True)


if __name__ == '__main__':
    run_flask()

# -*- coding: utf-8 -*-
"""Adika Mini App HTML templates (Telegram WebApp).

Self-contained: SELLER_FORM_HTML, BUYER_FORM_HTML, EXPLORER_HTML.
Optional sibling modules (ui_styles, ui_tools) are imported if present
and NEVER crash the page if missing.
"""
from __future__ import annotations

import logging
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE and _HERE not in sys.path:
    sys.path.insert(0, _HERE)

try:
    import ui_styles  # noqa: F401
except Exception as exc:
    logging.getLogger(__name__).warning("ui_styles optional import skipped: %s", exc)

try:
    import ui_tools  # noqa: F401
except Exception as exc:
    logging.getLogger(__name__).warning("ui_tools optional import skipped: %s", exc)


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
  
    
      100% { transform: translateX(120%); }
    }
    
      50% { filter: drop-shadow(0 0 10px rgba(99,102,241,0.55)); }
    }
    
    
    
    
    
    
    
    
    
    

    
      100% { transform: translateX(120%); }
    }
    
    
      50% { transform: scale(1.15); opacity: 0.85; }
    }
    
    .promo-slide {
      will-change: opacity, transform;
    }
    .promo-slide .promo-orb {
      transition: opacity 0.28s cubic-bezier(0.34, 1.56, 0.64, 1) 0ms,
                  transform 0.28s cubic-bezier(0.34, 1.56, 0.64, 1) 0ms;
    }
    .promo-slide .promo-icon {
      transition: opacity 0.32s cubic-bezier(0.34, 1.56, 0.64, 1) 80ms,
                  transform 0.32s cubic-bezier(0.34, 1.56, 0.64, 1) 80ms;
    }
    .promo-slide .promo-title,
    .promo-slide .promo-sub {
      transition: opacity 0.32s cubic-bezier(0.34, 1.56, 0.64, 1) 160ms,
                  transform 0.32s cubic-bezier(0.34, 1.56, 0.64, 1) 160ms;
    }
    .promo-slide .promo-cta {
      transition: opacity 0.32s cubic-bezier(0.34, 1.56, 0.64, 1) 240ms,
                  transform 0.32s cubic-bezier(0.34, 1.56, 0.64, 1) 240ms;
    }
    .promo-slide:not(.is-active) .promo-orb,
    .promo-slide:not(.is-active) .promo-icon,
    .promo-slide:not(.is-active) .promo-title,
    .promo-slide:not(.is-active) .promo-sub,
    .promo-slide:not(.is-active) .promo-cta {
      opacity: 0;
      transform: scale(0.85) translateY(12px);
    }
    .promo-slide.is-active .promo-orb {
      opacity: 1;
      transform: scale(1);
      animation: adikaGlowOrb 2s ease-in-out infinite;
    }
    .promo-slide.is-active .promo-icon {
      opacity: 1;
      transform: scale(1) rotateY(0deg);
    }
    .promo-slide.is-active .promo-title,
    .promo-slide.is-active .promo-sub {
      opacity: 1;
      transform: translateY(0) scale(1);
    }
    .promo-slide.is-active .promo-cta {
      opacity: 1;
      transform: translateY(0) scale(1);
    }
    .promo-slide.is-active {
      opacity: 1 !important;
      transform: scale(1) translateY(0) !important;
      pointer-events: auto !important;
      z-index: 2;
    }
    .promo-slide.is-exit {
      opacity: 0 !important;
      transform: scale(0.92) translateY(-22px) !important;
      pointer-events: none !important;
      z-index: 1;
    }

    @keyframes adikaShimmer {
      0% { transform: translateX(-120%); }
      100% { transform: translateX(120%); }
    }
    @keyframes adikaNeonPulse {
      0%, 100% { box-shadow: 0 0 10px rgba(34,211,238,0.35), 0 0 18px rgba(56,189,248,0.2), inset 0 1px 0 rgba(255,255,255,0.1); }
      50% { box-shadow: 0 0 16px rgba(45,212,191,0.45), 0 0 24px rgba(34,211,238,0.28), inset 0 1px 0 rgba(255,255,255,0.12); }
    }
    @keyframes adikaGlowOrb {
      0%, 100% { transform: scale(1); opacity: 0.5; }
      50% { transform: scale(1.18); opacity: 0.85; }
    }
    @keyframes adikaHeartbeat {
      0%, 100% { transform: scale(1); }
      50% { transform: scale(1.06); }
    }
    @keyframes adikaLetterIn {
      from { opacity: 0; transform: translateY(12px); }
      to { opacity: 1; transform: translateY(0); }
    }
    #adikaPromoBanner {
      animation: adikaNeonPulse 2.2s ease-in-out infinite;
    }
    .promo-slide { will-change: opacity, transform; }
    .promo-slide.is-active { opacity: 1 !important; transform: scale(1) translateY(0) !important; pointer-events: auto !important; z-index: 2; }
    .promo-slide.is-exit { opacity: 0 !important; transform: scale(0.92) translateY(-22px) !important; pointer-events: none !important; z-index: 1; }
    .promo-slide.is-active .promo-orb { opacity: 1; animation: adikaGlowOrb 2s ease-in-out infinite; }
    .promo-slide.is-active .promo-icon {
      animation: none;
      opacity: 1;
      transform: scale(1);
    }
    .promo-slide.is-active .promo-cta {
      animation: adikaHeartbeat 1.6s ease-in-out infinite;
      animation-delay: 0.4s;
    }
    .promo-slide:not(.is-active) .promo-orb,
    .promo-slide:not(.is-active) .promo-icon,
    .promo-slide:not(.is-active) .promo-title,
    .promo-slide:not(.is-active) .promo-sub,
    .promo-slide:not(.is-active) .promo-cta {
      opacity: 0;
    }
    .promo-slide.is-active .promo-letter {
      animation: adikaLetterIn 0.32s cubic-bezier(0.34, 1.56, 0.64, 1) both;
    }
</style>
</head>
<body class="bg-[#b5eff3] min-h-screen text-slate-800">
<script>

    /* SAFE STORAGE — Telegram WebView sandbox */
    var __mem = {};
    function _lsGet(k){ try { return localStorage.getItem(k); } catch(e) { return __mem[k] || null; } }
    function _lsSet(k,v){ try { localStorage.setItem(k,v); } catch(e) { __mem[k] = String(v); } }
    function _lsDel(k){ try { localStorage.removeItem(k); } catch(e) { delete __mem[k]; } }
window.openAiChat = window.openAiChat || function(prefillText){
  try {
    var tools = ["dutyModal","loanModal","compareModal","contractModal","poaModal","diagModal","chassisModal","landMapModal","aiModal","aiSearchView"];
    for (var i=0;i<tools.length;i++){
      var el = document.getElementById(tools[i]);
      if (!el) continue;
      el.classList.add("hidden");
      el.classList.remove("flex");
      el.style.setProperty("display","none","important");
    }
    var v = document.getElementById("analysisView");
    if (v){
      v.classList.remove("hidden");
      v.classList.add("flex");
      v.style.setProperty("display","flex","important");
      v.style.setProperty("z-index","260","important");
    }
    document.body.style.overflow = "hidden";
    var log = document.getElementById("advisorChatLog");
    if (log && !log.dataset.seeded){
      log.innerHTML = "";
      window.advisorChatHistory = [];
      var hello = "ሰላም! እኔ የ Adika Senior Financial Advisor ነኝ። እንዴት ልረዳዎት?";
      if (typeof appendAdvisorChat === "function") appendAdvisorChat("advisor", hello);
      log.dataset.seeded = "1";
    }
    var input = document.getElementById("advisorChatInput");
    if (prefillText && input){
      input.value = prefillText;
      setTimeout(function(){
        var sendBtn = document.getElementById("advisorChatSend");
        if (sendBtn) sendBtn.click();
      }, 30);
    }
  } catch (err) { console.error("openAiChat", err); }
};
window.handleStartAiChat = window.handleStartAiChat || function(opts){
  opts = opts || {};
  var budgetEl = document.getElementById("advisorBudget");
  var incomeEl = document.getElementById("advisorMonthlyIncome");
  var budget = Number(opts.budget || (budgetEl && budgetEl.value) || 0);
  var income = Number(opts.income || (incomeEl && incomeEl.value) || 0);
  var kind = opts.optionType || opts.context || "general";
  var b = (budget||0).toLocaleString();
  var inc = (income||0).toLocaleString();
  var title = kind;
  if (kind==="auto" || kind==="Automotive") title = "ተሽከርካሪ";
  else if (kind==="property" || kind==="Real Estate") title = "ሪል እስቴት";
  else if (kind==="roi" || kind==="Business") title = "ንግድ";
  else title = "ፋይናንስ";
  var prompt = "በ " + b + " ETB በጀት እና በ " + inc + " ETB ወርሃዊ ገቢ የተመረጡትን የ" + title + " የፋይናንስ አማራጮች ማብራሪያ እፈልጋለሁ።";
  window.openAiChat(prompt);
};

document.addEventListener("click", function(ev){
  var t = ev.target;
  if (!t || !t.closest) return;
  if (t.closest("#hubFinanceAdvisorBanner")) {
    ev.preventDefault(); ev.stopPropagation();
    if (window.handleStartAiChat) window.handleStartAiChat({optionType:"general"});
    return;
  }
  var cta = t.closest(".opp-chat-cta");
  if (cta) {
    ev.preventDefault(); ev.stopPropagation();
    if (window.handleStartAiChat) window.handleStartAiChat({context: cta.getAttribute("data-context")||"auto"});
  }
}, true);
</script>

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
      const [lang, setLang] = useState(() => _lsGet('adika_lang') || 'am');

      useEffect(() => {
        if (lang === 'en') document.body.classList.add('lang-en-active');
        else document.body.classList.remove('lang-en-active');
      }, [lang]);

      const switchLang = (newLang) => {
        setLang(newLang);
        _lsSet('adika_lang', newLang);
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
      const [chassisNumber, setChassisNumber] = useState('');
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

      const resetForm = () => {
        setStep(1);
        setCarModel('');
        setFuel('');
        setTransmission('');
        setMileage('');
        setCondition('');
        setCarType('');
        setChassisNumber('');
        setLocationArea('');
        setBedrooms('');
        setBathrooms('');
        setParking(false);
        setHouseCondition('');
        setHouseType('');
        setPrice('');
        setNegotiable(true);
        setUrgent(false);
        setDescription('');
        setPhotos([]);
      };

      const submitListing = async (event) => {
        if (event && event.preventDefault) event.preventDefault();
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
          chassis_number: chassisNumber,
          ...(isCar ? {
            fuel_type: fuel, transmission, mileage, condition, car_type: carType, chassis_number: chassisNumber
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
          const result = await res.json().catch(() => ({}));
          if (res.ok && (result.success === true || result.status === 'success' || result.req_id)) {
            setStatus('ok');
            resetForm();
            try { _lsDel('adika_draft_seller'); } catch (e) {}
            setTimeout(() => {
              if (window.Telegram && window.Telegram.WebApp && window.Telegram.WebApp.close) {
                try { window.location.href='/explorer'; } catch(e) {}
              } else {
                window.location.href = "/explorer";
              }
            }, 3000);
          } else {
            const msg = result.message || 'የማስታወቂያ ምዝገባው አልተሳካም። እባክዎ እንደገና ይሞክሩ።';
            setStatus(msg);
            alert(msg);
            setSubmitting(false);
          }
        } catch (e) {
          const errMsg = 'የኔትወርክ ስህተት አጋጥሟል። እባክዎ እንደገና ይሞክሩ።';
          setStatus(errMsg);
          alert(errMsg);
          setSubmitting(false);
        }
      };
      window.submitListing = submitListing;

      if (status === 'ok') {
        return (
          <div className="min-h-screen flex items-center justify-center p-6 bg-[#b5eff3]">
            <div className="bg-white rounded-3xl p-6 text-center space-y-4 shadow-[0_12px_28px_rgba(15,23,42,0.12)] border border-white/60 max-w-sm w-full">
              <div className="w-16 h-16 rounded-full bg-[#16acbd]/15 text-[#16acbd] flex items-center justify-center text-3xl mx-auto">✓</div>
              <h2 className="font-bold text-base text-slate-800">
                <span className="lang-am">ማስታወቂያዎ በተሳካ ሁኔታ ተመዝግቧል!</span>
                <span className="lang-en">Listing Successfully Posted!</span>
              </h2>
              <p className="font-medium text-xs text-slate-600 leading-relaxed px-2">
                <span className="lang-am">ንብረትዎ ለተረጋገጡ ደላሎችና ገዢዎች ተሰራጭቷል።</span>
                <span className="lang-en">Your listing has been submitted and broadcasted to verified buyers & brokers.</span>
              </p>
              <div className="flex flex-col gap-2 pt-2">
                <a href="/explorer"
                  className="w-full py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-teal-400 text-slate-950 font-bold hover:brightness-110 active:scale-95 text-xs shadow-md text-center block">
                  <span className="lang-am">ወደ ገበያ ሂድ</span>
                  <span className="lang-en">View Marketplace</span>
                </a>
                <button type="button" onClick={() => { setStatus(''); resetForm(); }}
                  className="w-full py-2 rounded-xl bg-slate-100 text-slate-700 font-bold text-xs">
                  <span className="lang-am">+ ሌላ ማስታወቂያ ልቀቅ</span>
                  <span className="lang-en">+ Post Another</span>
                </button>
              </div>
            </div>
          </div>
        );
      }

      return (
        <div className="min-h-screen bg-[#b5eff3] pb-24">
          <div className="fixed top-0 left-0 right-0 z-40 shadow-md px-3 py-2 text-white border-b border-white/20" style={{background:'rgba(15,23,42,0.82)',backdropFilter:'blur(16px)',WebkitBackdropFilter:'blur(16px)'}}>
            <div className="flex items-center justify-between max-w-md mx-auto mb-1.5 gap-2">
              <button type="button" onClick={() => { try { if (window.Telegram && window.Telegram.WebApp) window.location.href='/explorer'; else window.location.href='/explorer'; } catch(e) { window.location.href='/explorer'; } }}
                className="flex items-center gap-1 px-2.5 py-1.5 rounded-xl bg-white/10 hover:bg-white/20 border border-white/20 text-[11px] font-medium shrink-0">
                ← <span className="lang-am">ወደ ዋና ገፅ</span><span className="lang-en">Back</span>
              </button>
              <div className="font-extrabold text-xs tracking-wide truncate text-center flex-1">
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
            <div className="bg-white rounded-2xl p-4 shadow-[0_12px_28px_rgba(15,23,42,0.12)] border border-white/40 bg-white/40 backdrop-blur-md/80 space-y-4">
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
                          className="w-full px-3 py-2 rounded-xl bg-slate-50 border border-white/40 bg-white/40 backdrop-blur-md focus:bg-white focus:ring-2 focus:ring-[#16acbd] outline-none text-xs font-bold" />
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
                          className="w-full px-3 py-2 rounded-xl bg-slate-50 border border-white/40 bg-white/40 backdrop-blur-md focus:bg-white focus:ring-2 focus:ring-[#16acbd] outline-none text-xs" />
                      </div>
                      <div>
                        <label className="text-xs font-bold text-slate-700 mb-1 flex items-center justify-between">
                          <span>
                            <span className="lang-am">🛡️ የሻሲ ቁጥር (Chassis/VIN)</span>
                            <span className="lang-en">🛡️ Chassis / VIN</span>
                          </span>
                          <span className="text-[10px] text-[#0e7490] font-semibold bg-[#16acbd]/10 px-1.5 py-0.5 rounded">
                            <span className="lang-am">አማራጭ (ኦፊሴላዊ ባጅ ያገኛል)</span>
                            <span className="lang-en">Optional (Grants Verified Badge)</span>
                          </span>
                        </label>
                        <input type="text" value={chassisNumber} onChange={e => setChassisNumber(e.target.value.toUpperCase())}
                          placeholder="ለምሳሌ፡ JTDKN36U48... (17 Digits)"
                          className="w-full px-3 py-2 rounded-xl bg-slate-50 border border-white/40 bg-white/40 backdrop-blur-md focus:bg-white focus:ring-2 focus:ring-[#16acbd] outline-none text-xs font-mono uppercase font-bold text-slate-800" />
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
                          className="w-full px-3 py-2 rounded-xl bg-slate-50 border border-white/40 bg-white/40 backdrop-blur-md focus:bg-white focus:ring-2 focus:ring-[#16acbd] outline-none text-xs font-bold" />
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
                      className="w-full px-3 py-2 rounded-xl bg-slate-50 border border-white/40 bg-white/40 backdrop-blur-md focus:bg-white focus:ring-2 focus:ring-[#16acbd] outline-none text-xs resize-none" />
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
                        className="w-full px-3 py-2.5 rounded-xl bg-slate-50 border border-white/40 bg-white/40 backdrop-blur-md focus:bg-white focus:ring-2 focus:ring-[#16acbd] outline-none text-xs font-bold text-slate-900" />
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
                          <div key={i} className="relative aspect-square rounded-xl overflow-hidden border border-white/40 bg-white/40 backdrop-blur-md shadow-sm">
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
                      className="w-full px-3 py-2.5 rounded-xl bg-slate-50 border border-white/40 bg-white/40 backdrop-blur-md focus:bg-white focus:ring-2 focus:ring-[#16acbd] outline-none text-xs font-bold" />
                  </div>
                  <div>
                    <label className="text-xs font-bold text-slate-700 mb-1 block">
                      <span className="lang-am">📱 ቴሌግራም</span>
                      <span className="lang-en">📱 Telegram</span>
                    </label>
                    <input type="text" value={telegramUser} onChange={e => setTelegramUser(e.target.value)}
                      placeholder="@username"
                      className="w-full px-3 py-2.5 rounded-xl bg-slate-50 border border-white/40 bg-white/40 backdrop-blur-md focus:bg-white focus:ring-2 focus:ring-[#16acbd] outline-none text-xs font-bold" />
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
              <button type="button" onClick={() => {
                  try { resetForm(); } catch (e) {}
                  try {
                    if (window.Telegram && window.Telegram.WebApp && window.Telegram.WebApp.close) {
                      window.location.href='/explorer';
                    } else {
                      window.location.href = '/explorer';
                    }
                  } catch (e) { window.location.href = '/explorer'; }
                }}
                className="w-1/3 py-2.5 rounded-xl bg-slate-100 text-slate-700 font-bold text-xs active:scale-95">
                <span className="lang-am">ሰርዝ</span><span className="lang-en">Cancel</span>
              </button>
            )}
            {step < 3 ? (
              <button type="button" onClick={() => { if (step===1 && !canNext1) return; setStep(s => s+1); }}
                disabled={step===1 ? !canNext1 : photoBusy}
                className="flex-1 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-teal-400 text-slate-950 font-bold hover:brightness-110 active:scale-95 text-xs shadow-md active:scale-95 disabled:opacity-40">
                <span className="lang-am">ቀጣይ →</span><span className="lang-en">Next →</span>
              </button>
            ) : (
              <button id="submitBtn" type="button" onClick={(e) => submitListing(e)} disabled={!canSubmit || submitting}
                className="flex-1 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-teal-400 text-slate-950 font-bold hover:brightness-110 active:scale-95 text-xs shadow-md active:scale-95 disabled:opacity-40 flex items-center justify-center gap-1.5">
                {submitting ? (
                  <span className="flex items-center gap-1.5 font-bold">
                    <span className="lang-am">እየተመዘገበ ነው... ⏳</span>
                    <span className="lang-en">Posting... ⏳</span>
                  </span>
                ) : (
                  <>
                    <span className="lang-am">🚀 ማስታወቂያ መዝግብ</span>
                    <span className="lang-en">🚀 Submit Listing</span>
                  </>
                )}
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
      const [lang, setLang] = useState(() => _lsGet('adika_lang') || 'am');

      useEffect(() => {
        if (lang === 'en') document.body.classList.add('lang-en-active');
        else document.body.classList.remove('lang-en-active');
      }, [lang]);

      const switchLang = (newLang) => {
        setLang(newLang);
        _lsSet('adika_lang', newLang);
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

      const resetForm = () => {
        setBudgetMin('');
        setBudgetMax('');
        setCreateAlert(true);
        setDetails('');
      };

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
          if (res.ok && (result.success === true || result.status === 'success' || result.req_id)) {
            setStatus('ok');
            resetForm();
            try { _lsDel('adika_draft_buyer'); } catch (e) {}
            setTimeout(() => {
              if (window.Telegram && window.Telegram.WebApp && window.Telegram.WebApp.close) {
                try { window.location.href='/explorer'; } catch(e) {}
              }
            }, 3000);
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
            <div className="bg-white rounded-3xl p-6 text-center space-y-4 shadow-[0_12px_28px_rgba(15,23,42,0.12)] border border-white/60 max-w-sm w-full">
              <div className="w-16 h-16 rounded-full bg-[#16acbd]/15 text-[#16acbd] flex items-center justify-center text-3xl mx-auto">✓</div>
              <h2 className="font-bold text-base text-slate-800">
                <span className="lang-am">ጥያቄዎ በተሳካ ሁኔታ ተመዝግቧል!</span>
                <span className="lang-en">Request Broadcasted!</span>
              </h2>
              <p className="font-medium text-xs text-slate-600 leading-relaxed px-2">
                <span className="lang-am">የፍላጎት ጥያቄዎ ለተረጋገጡ ደላሎችና ሻጮች ተሰራጭቷል።</span>
                <span className="lang-en">Your request has been saved and shared with certified brokers and sellers.</span>
              </p>
              <div className="flex flex-col gap-2 pt-2">
                <a href="/explorer"
                  className="w-full py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-teal-400 text-slate-950 font-bold text-xs shadow-md text-center block">
                  <span className="lang-am">ወደ ገበያ ሂድ</span>
                  <span className="lang-en">View Marketplace</span>
                </a>
                <button type="button" onClick={() => { setStatus(''); resetForm(); }}
                  className="w-full py-2 rounded-xl bg-slate-100 text-slate-700 font-bold text-xs">
                  <span className="lang-am">+ ሌላ ጥያቄ ላክ</span>
                  <span className="lang-en">+ Submit Another</span>
                </button>
              </div>
            </div>
          </div>
        );
      }

      return (
        <div className="min-h-screen bg-[#b5eff3] pb-24">
          <div className="fixed top-0 left-0 right-0 z-40 shadow-md px-3 py-2 text-white flex items-center justify-between gap-2 border-b border-white/20" style={{background:'rgba(15,23,42,0.82)',backdropFilter:'blur(16px)',WebkitBackdropFilter:'blur(16px)'}}>
            <button type="button" onClick={() => { try { if (window.Telegram && window.Telegram.WebApp) window.location.href='/explorer'; else window.location.href='/explorer'; } catch(e) { window.location.href='/explorer'; } }}
              className="flex items-center gap-1 px-2.5 py-1.5 rounded-xl bg-white/10 hover:bg-white/20 border border-white/20 text-[11px] font-medium shrink-0">
              ← <span className="lang-am">ወደ ዋና ገፅ</span><span className="lang-en">Back</span>
            </button>
            <h1 className="font-extrabold text-xs tracking-wide truncate flex-1 text-center">
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
            <div className="rounded-2xl p-4 bg-white/70 backdrop-blur-2xl border border-white/30 shadow-2xl shadow-cyan-950/20 shadow-[0_12px_28px_rgba(15,23,42,0.12)] border border-white/40 bg-white/40 backdrop-blur-md/80 space-y-3.5">
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
                      className="w-full pl-9 pr-2 py-2 rounded-xl bg-slate-50 border border-white/40 bg-white/40 backdrop-blur-md focus:bg-white focus:ring-2 focus:ring-[#16acbd] outline-none text-xs font-semibold" />
                  </div>
                  <span className="text-slate-400 font-bold">—</span>
                  <div className="flex-1 relative">
                    <span className="absolute left-2.5 top-1/2 -translate-y-1/2 text-xs font-bold text-slate-400">Max</span>
                    <input type="text" inputMode="numeric" value={budgetMax}
                      onChange={e => setBudgetMax(formatPrice(e.target.value))}
                      placeholder="2,500,000"
                      className="w-full pl-10 pr-2 py-2 rounded-xl bg-slate-50 border border-white/40 bg-white/40 backdrop-blur-md focus:bg-white focus:ring-2 focus:ring-[#16acbd] outline-none text-xs font-semibold" />
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
                  className="w-full px-3 py-2 rounded-xl bg-slate-50 border border-white/40 bg-white/40 backdrop-blur-md focus:bg-white focus:ring-2 focus:ring-[#16acbd] outline-none text-xs resize-none" />
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-xs font-bold text-slate-700 mb-1 block">
                    <span className="lang-am">📞 ስልክ</span><span className="lang-en">📞 Phone</span>
                  </label>
                  <input type="tel" value={phone} onChange={e => setPhone(e.target.value)}
                    placeholder="0911223344"
                    className="w-full px-3 py-2 rounded-xl bg-slate-50 border border-white/40 bg-white/40 backdrop-blur-md focus:bg-white focus:ring-2 focus:ring-[#16acbd] outline-none text-xs font-bold" />
                </div>
                <div>
                  <label className="text-xs font-bold text-slate-700 mb-1 block">
                    <span className="lang-am">📱 ቴሌግራም</span><span className="lang-en">📱 Telegram</span>
                  </label>
                  <input type="text" value={telegramUser} onChange={e => setTelegramUser(e.target.value)}
                    placeholder="@username"
                    className="w-full px-3 py-2 rounded-xl bg-slate-50 border border-white/40 bg-white/40 backdrop-blur-md focus:bg-white focus:ring-2 focus:ring-[#16acbd] outline-none text-xs font-bold" />
                </div>
              </div>
            </div>
          </div>

          <div className="fixed bottom-0 left-0 right-0 p-3 bg-white/95 backdrop-blur-md border-t border-slate-200 flex gap-2 z-40">
            <button type="button" onClick={() => {
                  try { if (typeof resetForm === 'function') resetForm(); } catch(e) {}
                  try {
                    if (window.Telegram && window.Telegram.WebApp && window.Telegram.WebApp.close) window.location.href='/explorer';
                    else window.location.href = '/explorer';
                  } catch (e) { window.location.href = '/explorer'; }
                }}
              className="w-1/3 py-2.5 rounded-xl bg-slate-100 text-slate-700 font-bold text-xs active:scale-95">
              <span className="lang-am">ሰርዝ</span><span className="lang-en">Cancel</span>
            </button>
            <button type="button" onClick={submit} disabled={!details || submitting}
              className="flex-1 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-teal-400 text-slate-950 font-bold text-xs shadow-md active:scale-95 disabled:opacity-40 flex items-center justify-center gap-1.5">
              {submitting ? (
                <span className="flex items-center gap-1.5 font-bold">
                  <span className="lang-am">እየተመዘገበ ነው... ⏳</span>
                  <span className="lang-en">Broadcasting... ⏳</span>
                </span>
              ) : (
                <>
                  <span className="lang-am">📨 ጥያቄውን ላክ</span>
                  <span className="lang-en">📨 Broadcast Request</span>
                </>
              )}
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
    :root { --teal:#16acbd; --teal-d:#0e7490; --mint:#b5eff3; }
    html,body{margin:0;background:var(--mint);font-family:system-ui,-apple-system,sans-serif;-webkit-tap-highlight-color:transparent;}
    #grid{display:grid;grid-template-columns:1fr 1fr;gap:10px;}
    .card{position:relative;border-radius:16px;overflow:hidden;background:#d7f6f8;min-height:168px;box-shadow:0 8px 18px rgba(15,23,42,.12);text-align:left;border:0;}
    .card .ph{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font-size:42px;opacity:.35;}
    .card img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;}
    .card img.broken{display:none;}
    .card .meta{position:absolute;left:0;right:0;bottom:0;padding:28px 10px 10px;background:linear-gradient(to top,rgba(15,23,42,.82),transparent);color:#fff;}
    .sheet{display:none;}
    .sheet.open{display:flex!important;}
    .pill-on{background:#fff;color:var(--teal-d);}
    .pill-off{background:rgba(255,255,255,.2);color:#fff;}
  </style>
</head>
<body>
<header class="fixed top-0 left-0 right-0 z-40 text-white" style="background:rgba(0,131,143,.92);backdrop-filter:blur(16px);">
  <div class="max-w-md mx-auto px-2.5 pt-2 pb-2 space-y-1.5">
    <div class="flex gap-2 items-center">
      <div class="flex-1 grid grid-cols-2 gap-1 p-0.5 bg-black/15 rounded-xl">
        <button type="button" id="tabSell" class="py-1.5 rounded-lg text-xs font-bold bg-white text-[#16acbd]">ገበያ</button>
        <button type="button" id="tabBuy" class="py-1.5 rounded-lg text-xs font-bold text-white/90">ፈላጊዎች</button>
      </div>
      <button type="button" id="btnBroker" class="px-2.5 py-1.5 rounded-xl bg-white/20 text-[11px] font-bold">ደላላ?</button>
    </div>
    <input id="search" class="w-full rounded-xl px-3 py-2 text-xs text-slate-800 outline-none" placeholder="ፈልግ... ሞዴል፣ ቦታ፣ ዋጋ" />
    <div id="cats" class="flex gap-1.5 overflow-x-auto"></div>
  </div>
</header>

<main class="max-w-md mx-auto px-2.5" style="padding-top:148px;padding-bottom:118px;">
  <div id="promo" class="mb-2.5 rounded-2xl px-3 py-2.5 text-white flex items-center justify-between"
       style="background:linear-gradient(90deg,#0f172a,#0e7490);">
    <div>
      <div class="text-[9px] tracking-widest text-cyan-300 font-bold">ADIKA DIGITAL SYSTEM</div>
      <div class="text-xs font-black">ዲጂታል መሣሪያዎች</div>
    </div>
    <button type="button" id="promoGo" class="text-[11px] font-bold bg-cyan-400 text-slate-950 px-3 py-1.5 rounded-full">ክፈት →</button>
  </div>
  <div id="status" class="text-center text-xs text-slate-600 pb-2"></div>
  <div id="grid"></div>
</main>

<nav class="fixed bottom-3 left-3 right-3 z-40 max-w-md mx-auto rounded-full px-1 py-1.5 flex items-center justify-between shadow-xl"
     style="background:rgba(255,255,255,.94);">
  <button type="button" id="navHome" class="flex-1 py-1 text-[10px] font-black text-[#0e7490]">መነሻ</button>
  <button type="button" id="navAi" class="flex-1 py-1 text-[10px] font-bold text-slate-500">አማካሪ</button>
  <button type="button" id="fabBtn" class="w-12 h-12 -mt-6 rounded-full text-white text-2xl font-black shadow-lg shrink-0" style="background:#16acbd;">+</button>
  <button type="button" id="navChat" class="flex-1 py-1 text-[10px] font-bold text-slate-500">መልእክት</button>
  <button type="button" id="navHelp" class="flex-1 py-1 text-[10px] font-bold text-slate-500">እርዳታ</button>
</nav>

<div id="chatSheet" class="sheet fixed inset-0 z-50 bg-[#b5eff3] flex-col max-w-md mx-auto">
  <div class="p-3 text-white flex justify-between items-center" style="background:#16acbd;">
    <button type="button" class="js-close px-3 py-1 rounded-lg bg-white/20 text-xs">← ተመለስ</button>
    <b>አዲካ ዲጂታል አማካሪ</b>
    <button type="button" class="js-close">✕</button>
  </div>
  <div id="chatLog" class="flex-1 overflow-y-auto p-3 text-sm space-y-2"></div>
  <div class="p-2 bg-white flex gap-2">
    <input id="chatInput" class="flex-1 rounded-full px-3 py-2 text-sm bg-slate-100 outline-none" placeholder="መልእክትዎን ይጻፉ..." />
    <button type="button" id="chatSend" class="px-4 rounded-full text-white text-xs font-bold" style="background:#16acbd;">ላክ</button>
  </div>
</div>

<div id="toolsSheet" class="sheet fixed inset-0 z-50 flex-col max-w-md mx-auto text-white" style="background:#020617;">
  <div class="p-3 flex justify-between items-center">
    <button type="button" class="js-close px-3 py-1.5 rounded-xl bg-white/10 text-xs">← ዋና ገፅ</button>
    <b>Adika Digital Hub</b>
    <button type="button" class="js-close">✕</button>
  </div>
  <div class="px-3 grid grid-cols-2 gap-2 text-xs">
    <button type="button" class="js-tool p-3 rounded-2xl bg-white/10 text-left border border-white/10" data-tool="ውክልና">📜 የውክልና ማጣሪያ</button>
    <button type="button" class="js-tool p-3 rounded-2xl bg-white/10 text-left border border-white/10" data-tool="ሻሲ">🔍 የሻንሲ ማጣሪያ</button>
    <button type="button" class="js-tool p-3 rounded-2xl bg-white/10 text-left border border-white/10" data-tool="ቀረጥ">🧮 የቀረጥ ስሌት</button>
    <button type="button" class="js-tool p-3 rounded-2xl bg-white/10 text-left border border-white/10" data-tool="ብድር">🏦 የባንክ ብድር</button>
    <button type="button" class="js-tool p-3 rounded-2xl bg-white/10 text-left border border-white/10" data-tool="ንፅፅር">⚖️ የመኪና ንፅፅር</button>
    <button type="button" class="js-tool p-3 rounded-2xl bg-white/10 text-left border border-white/10" data-tool="ውል">📄 የሽያጭ ውል</button>
  </div>
  <button type="button" id="openChatFromTools" class="m-3 mt-auto p-3 rounded-2xl font-black text-slate-950" style="background:#22d3ee;">አሁኑኑ አማክር →</button>
</div>

<div id="detailSheet" class="sheet fixed inset-0 z-50 bg-white flex-col max-w-md mx-auto">
  <div class="p-3 text-white flex justify-between items-center" style="background:#16acbd;">
    <button type="button" class="js-close px-3 py-1 rounded-lg bg-white/20 text-xs">← ተመለስ</button>
    <b id="detailTitle" class="truncate px-2">ዝርዝር</b>
    <button type="button" class="js-close">✕</button>
  </div>
  <div id="detailMedia" class="w-full aspect-video bg-slate-200 overflow-hidden"></div>
  <div id="detailBody" class="flex-1 overflow-y-auto p-3 text-sm"></div>
  <div class="p-3 grid grid-cols-2 gap-2" style="padding-bottom:calc(12px + env(safe-area-inset-bottom));">
    <a id="detailCall" class="text-center py-3 rounded-xl bg-emerald-600 text-white font-bold" href="tel:">📞 ደውል</a>
    <button type="button" id="detailChat" class="py-3 rounded-xl text-white font-bold" style="background:#16acbd;">💬 አማክር</button>
  </div>
</div>

<div id="brokerSheet" class="sheet fixed inset-0 z-50 items-end justify-center bg-black/45">
  <div class="w-full max-w-md rounded-t-3xl p-4 text-white" style="background:rgba(15,23,42,.92);backdrop-filter:blur(16px);">
    <div class="flex justify-between mb-3"><b>ደላላ ምዝገባ</b><button type="button" class="js-close">✕</button></div>
    <input id="brName" class="w-full mb-2 px-3 py-2.5 rounded-xl bg-white/10 outline-none" placeholder="ሙሉ ስም" />
    <input id="brPhone" class="w-full mb-3 px-3 py-2.5 rounded-xl bg-white/10 outline-none" placeholder="ስልክ" />
    <button type="button" id="brSubmit" class="w-full py-3 rounded-xl font-black text-slate-950" style="background:#22d3ee;">መመዝገብ</button>
  </div>
</div>

<script>
(function () {
  var tg = window.Telegram && Telegram.WebApp;
  try { if (tg) { tg.ready(); tg.expand(); tg.setHeaderColor("#16acbd"); } } catch (e) {}

  var state = { tab: "SELL", cat: "", q: "", items: [] };
  var CATS = [
    { id: "", label: "ሁሉም" },
    { id: "መኪና", label: "መኪና" },
    { id: "ቤት", label: "ቤት" },
    { id: "ንግድ", label: "ንግድ" }
  ];

  function $(id) { return document.getElementById(id); }
  function openSheet(id) {
    ["chatSheet","toolsSheet","detailSheet","brokerSheet"].forEach(function (x) { $(x).classList.remove("open"); });
    if (id) $(id).classList.add("open");
  }
  function money(v) {
    var n = Number(String(v || "").replace(/[^\d.]/g, ""));
    if (!n || n <= 0 || n > 300000000) return "ለዋጋ ደውሉ";
    return Math.round(n).toLocaleString("en-US") + " ETB";
  }
  function isHouse(it) {
    var c = String(it.main_category || it.category || it.sub_category || "");
    return c.indexOf("ቤት") >= 0 || /house|property|real|land/i.test(c);
  }
  function titleOf(it) {
    var t = [it.brand, it.model].filter(Boolean).join(" ").trim();
    if (t) return t;
    var s = (it.sub_category || it.title || "").trim();
    if (s && s !== "መኪና" && s !== "ቤት") return s;
    return it.category || it.main_category || "ማስታወቂያ";
  }
  function photoOf(it) {
    var keys = ["photo_urls","photos","listing_photos","image_url","image","photo","thumbnail"];
    var p = "";
    for (var i = 0; i < keys.length; i++) {
      if (it[keys[i]]) { p = it[keys[i]]; break; }
    }
    if (Array.isArray(p)) p = p[0] || "";
    if (p && typeof p === "object") p = p.url || p.src || "";
    if (typeof p === "string" && p.charAt(0) === "[") {
      try { var arr = JSON.parse(p); p = arr[0] || ""; } catch (e) {}
    }
    p = String(p || "").trim();
    if (!p || p === "null" || p === "undefined") return "";
    return p;
  }

  function paintCats() {
    $("cats").innerHTML = CATS.map(function (c) {
      var on = state.cat === c.id;
      return '<button type="button" data-cat="' + c.id + '" class="shrink-0 px-3 py-1 rounded-full text-xs font-bold ' + (on ? "pill-on" : "pill-off") + '">' + c.label + "</button>";
    }).join("");
  }

  function paintGrid(items) {
    state.items = items || [];
    if (!state.items.length) {
      $("grid").innerHTML = '<p class="col-span-2 text-center text-sm py-10 text-slate-600">ምንም አልተገኘም</p>';
      return;
    }
    $("grid").innerHTML = state.items.map(function (it, i) {
      var src = photoOf(it);
      var icon = isHouse(it) ? "🏠" : "🚗";
      var img = src ? '<img src="' + String(src).replace(/"/g,"") + '" alt="" onerror="this.classList.add(\'broken\')" />' : "";
      return '<button type="button" class="card" data-i="' + i + '">' +
        '<div class="ph">' + icon + "</div>" + img +
        '<div class="meta">' +
          '<div class="text-[12px] font-extrabold truncate">' + titleOf(it) + "</div>" +
          '<div class="text-[12px] font-black text-cyan-200">💰 ' + money(it.price) + "</div>" +
        "</div></button>";
    }).join("");
  }

  function load() {
    $("status").textContent = "እየጫነ ነው...";
    var qs = "page=1&limit=40&order=DESC&active_only=1&type=" + state.tab;
    if (state.cat) qs += "&category=" + encodeURIComponent(state.cat);
    if (state.q) qs += "&q=" + encodeURIComponent(state.q);
    var urls = ["/api/listings?" + qs, "/api/explorer/listings?" + qs];
    function next(i) {
      if (i >= urls.length) { $("status").textContent = ""; paintGrid([]); return; }
      fetch(urls[i], { credentials: "same-origin" })
        .then(function (r) { return r.json(); })
        .then(function (d) {
          var items = (d && (d.items || d.listings || d.results || d.data)) || [];
          if (!Array.isArray(items) || !items.length) return next(i + 1);
          $("status").textContent = "";
          paintGrid(items);
        })
        .catch(function () { next(i + 1); });
    }
    next(0);
  }

  $("tabSell").onclick = function () {
    state.tab = "SELL";
    this.className = "py-1.5 rounded-lg text-xs font-bold bg-white text-[#16acbd]";
    $("tabBuy").className = "py-1.5 rounded-lg text-xs font-bold text-white/90";
    load();
  };
  $("tabBuy").onclick = function () {
    state.tab = "BUY";
    this.className = "py-1.5 rounded-lg text-xs font-bold bg-white text-[#16acbd]";
    $("tabSell").className = "py-1.5 rounded-lg text-xs font-bold text-white/90";
    load();
  };
  $("search").onkeydown = function (e) { if (e.key === "Enter") { state.q = this.value.trim(); load(); } };
  $("cats").onclick = function (e) {
    var b = e.target.closest("[data-cat]"); if (!b) return;
    state.cat = b.getAttribute("data-cat") || ""; paintCats(); load();
  };
  $("grid").onclick = function (e) {
    var b = e.target.closest("[data-i]"); if (!b) return;
    var it = state.items[Number(b.getAttribute("data-i"))]; if (!it) return;
    $("detailTitle").textContent = titleOf(it);
    var src = photoOf(it);
    $("detailMedia").innerHTML = src
      ? '<img src="' + String(src).replace(/"/g,"") + '" style="width:100%;height:100%;object-fit:cover" />'
      : '<div style="height:100%;display:flex;align-items:center;justify-content:center;font-size:48px">' + (isHouse(it)?"🏠":"🚗") + "</div>";
    $("detailBody").innerHTML = '<p class="font-black text-lg text-[#0e7490] mb-2">' + money(it.price) + "</p><p class=\"whitespace-pre-wrap text-slate-700\">" + (it.description || "") + "</p>";
    $("detailCall").href = "tel:" + (it.phone || it.phone_number || "");
    openSheet("detailSheet");
  };
  $("navHome").onclick = function () { openSheet(null); window.scrollTo({ top: 0, behavior: "smooth" }); };
  $("navAi").onclick = function () { openSheet("toolsSheet"); };
  $("navChat").onclick = function () { openSheet("chatSheet"); };
  $("navHelp").onclick = function () { alert("Adika Marketplace\n@AdikaMarketplaceBot"); };
  $("fabBtn").onclick = function () { location.href = state.tab === "BUY" ? "/buyer-form" : "/seller-form"; };
  $("btnBroker").onclick = function () { openSheet("brokerSheet"); };
  $("promoGo").onclick = function () { openSheet("toolsSheet"); };
  $("openChatFromTools").onclick = function () { openSheet("chatSheet"); };
  $("detailChat").onclick = function () { openSheet("chatSheet"); };
  document.querySelectorAll(".js-close").forEach(function (b) { b.onclick = function () { openSheet(null); }; });
  document.querySelectorAll(".js-tool").forEach(function (b) {
    b.onclick = function () { openSheet("chatSheet"); $("chatInput").value = "የ" + b.getAttribute("data-tool") + " አገልግሎት እፈልጋለሁ"; };
  });
  $("brSubmit").onclick = function () {
    var name = $("brName").value.trim(), phone = $("brPhone").value.trim();
    if (!name || !phone) { alert("ስም እና ስልክ ያስፈልጋሉ"); return; }
    fetch("/api/brokers/register", { method:"POST", headers:{ "Content-Type":"application/json" }, body: JSON.stringify({ name:name, phone:phone }) })
      .then(function (r) { return r.json(); })
      .then(function (d) { alert(d.success ? "ተመዝግቧል" : (d.message || "አልተሳካም")); if (d.success) openSheet(null); })
      .catch(function () { alert("ኔትወርክ ስህተት"); });
  };
  $("chatSend").onclick = function () {
    var msg = $("chatInput").value.trim(); if (!msg) return;
    $("chatLog").innerHTML += '<div class="text-right"><span class="inline-block bg-teal-600 text-white p-2 rounded-2xl">' + msg + "</span></div>";
    $("chatInput").value = "";
    fetch("/api/advisor/chat", { method:"POST", headers:{ "Content-Type":"application/json" }, body: JSON.stringify({ message: msg }) })
      .then(function (r) { return r.json(); })
      .then(function (d) { $("chatLog").innerHTML += '<div class="bg-white p-2 rounded-2xl">' + (d.reply || d.message || d.text || "ተቀብያለሁ") + "</div>"; })
      .catch(function () { $("chatLog").innerHTML += "<div>አልተሳካም</div>"; });
  };

  paintCats();
  load();
})();
</script>
</body>
</html>

"""

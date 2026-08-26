# ui_components.py — HTML/CSS templates for Adika Telegram Mini App
# Seller form, Buyer form, and Explorer (Marketplace) pages.
"""UI template constants. No Flask dependency."""

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
          if (res.ok && (result.status === 'success' || !result.status)) {
            setStatus('ok');
            resetForm();
            try { localStorage.removeItem('adika_draft_seller'); } catch (e) {}
            setTimeout(() => {
              if (window.Telegram && window.Telegram.WebApp && window.Telegram.WebApp.close) {
                try { window.Telegram.WebApp.close(); } catch(e) {}
              } else {
                window.location.href = "/";
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
                  className="w-full py-2.5 rounded-xl bg-[#16acbd] text-white font-bold text-xs shadow-md text-center block">
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
                          className="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-200 focus:bg-white focus:ring-2 focus:ring-[#16acbd] outline-none text-xs font-mono uppercase font-bold text-slate-800" />
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
              <button id="submitBtn" type="button" onClick={(e) => submitListing(e)} disabled={!canSubmit || submitting}
                className="flex-1 py-2.5 rounded-xl bg-[#16acbd] text-white font-bold text-xs shadow-md active:scale-95 disabled:opacity-40 flex items-center justify-center gap-1.5">
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
          if (result.status === 'success' || res.ok) {
            setStatus('ok');
            resetForm();
            try { localStorage.removeItem('adika_draft_buyer'); } catch (e) {}
            setTimeout(() => {
              if (window.Telegram && window.Telegram.WebApp && window.Telegram.WebApp.close) {
                try { window.Telegram.WebApp.close(); } catch(e) {}
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
                  className="w-full py-2.5 rounded-xl bg-[#16acbd] text-white font-bold text-xs shadow-md text-center block">
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
              className="flex-1 py-2.5 rounded-xl bg-[#16acbd] text-white font-bold text-xs shadow-md active:scale-95 disabled:opacity-40 flex items-center justify-center gap-1.5">
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
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no, viewport-fit=cover" />
  <title>Adika Marketplace</title>
  <script src="https://telegram.org/js/telegram-web-app.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/jsqr@1.4.0/dist/jsQR.js"></script>
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

    /* Executive hero carousel — compact max 110px */
    .hero-carousel {
      display: flex; gap: 0.4rem; overflow-x: auto; scroll-snap-type: x mandatory;
      -webkit-overflow-scrolling: touch; padding-bottom: 0;
      max-height: 110px;
    }
    .hero-carousel::-webkit-scrollbar { display: none; }
    .hero-slide {
      scroll-snap-align: start; flex: 0 0 72%; min-width: 72%;
      max-height: 96px; border-radius: 0.7rem; border: 1px solid rgb(30 41 59);
      background: linear-gradient(90deg, #020617 0%, #0f172a 50%, #020617 100%);
      padding: 0.4rem 0.65rem; color: #f8fafc;
      box-shadow: 0 4px 12px rgba(2, 6, 23, 0.28);
      transition: transform 0.12s ease;
      display: flex; flex-direction: column; justify-content: center;
    }
    .hero-slide:active { transform: scale(0.985); }
    .hero-slide .accent { color: #fbbf24; font-size: 9px; }
    .hero-slide .hero-title { font-size: 11px; font-weight: 900; line-height: 1.2; }
    .hero-slide .hero-sub { font-size: 8px; color: #94a3b8; line-height: 1.25; margin-top: 2px; }
    .hero-slide .hero-cta-line { font-size: 8px; font-weight: 700; margin-top: 4px; }
    .hero-dots { display: flex; justify-content: center; gap: 4px; margin-top: 4px; }
    .hero-dot { width: 4px; height: 4px; border-radius: 999px; background: rgba(15,23,42,0.25); }
    .hero-dot.active { background: #0e7490; width: 12px; }

    /* Instagram-style listing photo auto-enhancement (zero-cost CSS) */
    .listing-photo-frame {
      position: relative;
      width: 100%;
      aspect-ratio: 4 / 3;
      overflow: hidden;
      border-radius: 0.75rem;
      background: #e2e8f0;
    }
    .listing-photo-frame::before {
      content: "";
      position: absolute;
      inset: 0;
      z-index: 0;
      background: linear-gradient(145deg, #cbd5e1, #94a3b8);
      filter: blur(12px);
      transform: scale(1.08);
    }
    .listing-photo-enhance {
      position: relative;
      z-index: 1;
      width: 100%;
      height: 100%;
      object-fit: cover;
      object-position: center;
      border-radius: 0.75rem;
      filter: contrast(108%) brightness(102%) saturate(110%);
      -webkit-filter: contrast(108%) brightness(102%) saturate(110%);
      transition: filter 0.2s ease, transform 0.2s ease;
    }
    .adika-card:active .listing-photo-enhance {
      transform: scale(1.02);
    }


    /* Glass chat bubbles */
    .chat-bubble-user {
      margin-left: 1.5rem; padding: 0.7rem 0.85rem; border-radius: 1rem;
      background: linear-gradient(135deg, #0d9488, #059669);
      color: #fff; box-shadow: 0 8px 24px rgba(13, 148, 136, 0.25);
      border: 1px solid rgba(255,255,255,0.15);
      backdrop-filter: blur(8px); -webkit-backdrop-filter: blur(8px);
    }
    .chat-bubble-ai {
      margin-right: 1.5rem; padding: 0.7rem 0.85rem; border-radius: 1rem;
      background: rgba(255,255,255,0.55);
      border: 1px solid rgba(255,255,255,0.45);
      box-shadow: 0 8px 24px rgba(15, 23, 42, 0.08);
      backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
      color: #0f172a;
    }
    .chat-input-bar {
      display: flex; align-items: flex-end; gap: 0.4rem;
      padding: 0.55rem; border-top: 1px solid rgba(226,232,240,0.9);
      background: rgba(255,255,255,0.85);
      backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px);
    }
    .chat-input-bar textarea {
      flex: 1; min-height: 38px; max-height: 110px; resize: none;
      border-radius: 0.85rem; padding: 0.55rem 0.75rem;
      font-size: 12px; line-height: 1.4; border: 1px solid #e2e8f0;
      background: #f8fafc; outline: none;
    }
    .chat-input-bar textarea:focus { border-color: #14b8a6; box-shadow: 0 0 0 2px rgba(20,184,166,0.2); }
    .chat-send-btn {
      width: 38px; height: 38px; border-radius: 999px; flex-shrink: 0;
      display: flex; align-items: center; justify-content: center;
      background: linear-gradient(135deg, #0d9488, #059669); color: #fff;
      border: none; box-shadow: 0 4px 12px rgba(13,148,136,0.35);
    }
    .chat-send-btn:active { transform: scale(0.94); }

    /* Corporate tool cards */
    .tool-card-pro {
      padding: 0.5rem 0.55rem; border-radius: 0.7rem; text-align: left;
      background: rgba(15, 23, 42, 0.6); border: 1px solid rgb(30 41 59);
      color: #e2e8f0; transition: background 0.15s ease, transform 0.1s ease;
      display: flex; flex-direction: column; gap: 0.2rem;
      box-shadow: 0 3px 10px rgba(2, 6, 23, 0.15);
      min-height: 0;
    }
    .tool-card-pro:hover, .tool-card-pro:active {
      background: rgba(30, 41, 59, 0.85); transform: scale(0.98);
    }
    .tool-card-pro .tool-title { font-weight: 800; font-size: 10px; color: #f1f5f9; line-height: 1.2; }
    .tool-card-pro .tool-sub { font-size: 8px; color: #94a3b8; line-height: 1.2; }
    .tool-icon-wrap {
      width: 22px; height: 22px; border-radius: 0.4rem;
      display: flex; align-items: center; justify-content: center;
      background: rgba(251, 191, 36, 0.12); border: 1px solid rgba(251, 191, 36, 0.25);
      color: #fbbf24;
    }
    .tool-icon-wrap svg { width: 12px; height: 12px; }

    .land-scan-laser {
      background: linear-gradient(180deg, transparent 0%, rgba(34,211,238,0.15) 48%, rgba(34,211,238,0.55) 50%, rgba(34,211,238,0.15) 52%, transparent 100%);
      background-size: 100% 200%;
      animation: landScan 1.4s linear infinite;
    }
    @keyframes landScan {
      0% { background-position: 0% 0%; }
      100% { background-position: 0% 100%; }
    }

    .tools-grid-compact {
      display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.4rem;
    }
    @media (max-width: 340px) {
      .tools-grid-compact { grid-template-columns: repeat(2, 1fr); }
    }
    .opp-card {
      border-radius: 0.65rem; padding: 0.45rem 0.55rem;
      background: linear-gradient(145deg, #0f172a 0%, #1e293b 100%);
      border: 1px solid #334155; color: #e2e8f0;
      box-shadow: 0 4px 12px rgba(2,6,23,0.2);
    }
    .opp-card .opp-label { font-size: 8px; font-weight: 700; letter-spacing: 0.04em; text-transform: uppercase; }
    .opp-card .opp-title { font-size: 11px; font-weight: 900; color: #fff; margin-top: 1px; line-height: 1.2; }
    .opp-card .opp-body { font-size: 9px; color: #94a3b8; margin-top: 3px; line-height: 1.35; }
    .opp-card .opp-cta {
      margin-top: 0.35rem; width: 100%; padding: 0.35rem 0.4rem;
      border-radius: 0.45rem; font-size: 8px; font-weight: 800; line-height: 1.25;
      background: linear-gradient(90deg, #0d9488, #0891b2); color: #fff;
      border: none; text-align: center;
    }
    /* Sticky chat input at absolute bottom of analysis view */
    #analysisView { display: none; flex-direction: column; }
    #analysisView.flex { display: flex !important; }
    #analysisView .chat-shell {
      flex: 1; display: flex; flex-direction: column; min-height: 0;
      position: relative; padding-bottom: 0;
    }
    #analysisView .chat-input-sticky {
      position: fixed; bottom: 0; left: 0; right: 0;
      max-width: 28rem; margin: 0 auto;
      z-index: 70;
      background: rgba(255,255,255,0.95);
      backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
      border-top: 1px solid rgba(226,232,240,0.95);
      padding: 0.5rem 0.65rem calc(0.5rem + env(safe-area-inset-bottom, 0px));
      box-shadow: 0 -4px 16px rgba(15,23,42,0.08);
    }
    #analysisView #advisorChatLog {
      padding-bottom: 5.5rem !important;
    }
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
        <button id="filterChassisChip" type="button" class="cat-pill px-3 py-1 rounded-full text-xs font-bold whitespace-nowrap transition-all bg-emerald-500/25 text-white hover:bg-emerald-500/35 border border-emerald-300/40" data-filter="chassis">
          <span>🔍 <span class="lang-am">ሻሲ ያላቸው ብቻ</span><span class="lang-en">VIN Verified</span></span>
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

    <!-- HOME HERO: Ultra-compact horizontal carousel (max 110px) -->
    <div id="homeHero" class="mb-1.5">
      <div id="heroCarousel" class="hero-carousel">
        <button id="heroAdvisorBtn" type="button" class="hero-slide text-left">
          <div class="flex items-center justify-between gap-1.5">
            <div class="min-w-0">
              <div class="text-[7px] font-bold tracking-wide uppercase text-slate-500">Adika Intelligence</div>
              <div class="hero-title">ዲጂታል የፋይናንስ አማካሪ</div>
              <div class="hero-sub">በጀት · ብድር · የገበያ ዋጋ</div>
            </div>
            <span class="accent font-black shrink-0">AI</span>
          </div>
          <div class="hero-cta-line text-teal-300 inline-flex items-center gap-0.5">ትንተና ጀምር →</div>
        </button>
        <button id="heroPoaBtn" type="button" class="hero-slide text-left">
          <div class="flex items-center justify-between gap-1.5">
            <div class="min-w-0">
              <div class="text-[7px] font-bold tracking-wide uppercase text-slate-500">Legal Desk</div>
              <div class="hero-title">የሰነድ ማረጋገጫ</div>
              <div class="hero-sub">ውክልና (POA) ዲጂታል ማጣሪያ</div>
            </div>
            <span class="accent font-black shrink-0">ID</span>
          </div>
          <div class="hero-cta-line text-amber-300 inline-flex items-center gap-0.5">አሁን ያረጋግጡ →</div>
        </button>
        <button id="heroToolsBtn" type="button" class="hero-slide text-left">
          <div class="flex items-center justify-between gap-1.5">
            <div class="min-w-0">
              <div class="text-[7px] font-bold tracking-wide uppercase text-slate-500">Tools Suite</div>
              <div class="hero-title">ፋይናንስና ህግ መሳሪያዎች</div>
              <div class="hero-sub">ቀረጥ · ብድር · ውል · ንጽጽር</div>
            </div>
            <span class="accent font-black shrink-0">PRO</span>
          </div>
          <div class="hero-cta-line text-sky-300 inline-flex items-center gap-0.5">መሳሪያዎች ክፈት →</div>
        </button>
      </div>
      <div class="hero-dots" id="heroDots">
        <span class="hero-dot active"></span><span class="hero-dot"></span><span class="hero-dot"></span>
      </div>
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


  <!-- DEDICATED LIVE ADVISOR CHAT (full-screen view state) -->
  <div id="analysisView" class="fixed inset-0 z-[60] bg-[#b5eff3] hidden flex-col max-w-md mx-auto w-full">
    <div class="shrink-0 px-3 py-2 bg-[#16acbd] text-white flex items-center justify-between shadow-md">
      <div class="flex items-center gap-2 min-w-0">
        <button id="analysisBackBtn" type="button" class="btn-back flex items-center gap-1 px-2.5 py-1.5 rounded-lg bg-white/20 hover:bg-white/30 text-[11px] font-bold">← ተመለስ</button>
        <div class="min-w-0 flex-1">
          <div class="font-black text-xs truncate">Adika Senior Financial Advisor</div>
          <div class="text-[10px] text-white/85 truncate">Live Advisor Chat</div>
        </div>
      </div>
      <div class="flex items-center gap-1.5 shrink-0">
        <span class="text-[9px] font-extrabold text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200/60">ዝግጁ</span>
        <button type="button" onclick="navigateBack('analysisView')" class="btn-close w-8 h-8 rounded-full bg-slate-900/80 hover:bg-slate-900 text-white flex items-center justify-center font-bold text-sm" aria-label="Close">✕</button>
      </div>
    </div>
    <div class="chat-shell flex-1 flex flex-col min-h-0 bg-slate-50/70">
      <div class="px-3 pt-2 pb-1 shrink-0">
        <div class="rounded-xl px-3 py-1.5 bg-slate-900/80 text-white flex items-center justify-between">
          <div class="text-[11px] font-black flex items-center gap-1.5">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#fbbf24" stroke-width="2"><path d="M21 15a4 4 0 0 1-4 4H7l-4 4V7a4 4 0 0 1 4-4h10a4 4 0 0 1 4 4z"/></svg>
            <span>የቀጥታ ውይይት</span>
          </div>
          <span class="text-[9px] font-bold text-emerald-300">ፈጣን ምላሽ</span>
        </div>
      </div>
      <div id="advisorChatLog" class="flex-1 overflow-y-auto px-3 pt-2 space-y-2.5 text-xs scroll-smooth"></div>
      <div class="chat-input-sticky chat-input-bar">
        <textarea id="advisorChatInput" rows="1" placeholder="ስለ መኪና፣ ቤት፣ ቀረጥ ወይም የባንክ ብድር ይጠይቁ..."></textarea>
        <button id="advisorChatSend" type="button" class="chat-send-btn" aria-label="Send">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 2L11 13"/><path d="M22 2l-7 20-4-9-9-4 20-7z"/></svg>
        </button>
      </div>
    </div>
  </div>

  <!-- ================================================================= -->
  <!-- 4. DEDICATED AI HUB & SMART FILTER MODAL                          -->
  <!-- ================================================================= -->
  <div id="aiModal" class="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm hidden items-end justify-center">
    <div class="w-full max-w-md bg-white rounded-t-3xl max-h-[90vh] flex flex-col shadow-2xl overflow-hidden">
      <!-- Header with Tabs -->
      <div class="px-4 py-2.5 bg-[#16acbd] text-white flex flex-col gap-2 shrink-0">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-2">
            <span class="text-lg">✨</span>
            <h3 class="font-extrabold text-xs tracking-wide">
              <span class="lang-am">አዲካ ዲጂታል አማካሪ & መሳሪያዎች</span>
              <span class="lang-en">Adika Digital Advisor & Tools Hub</span>
            </h3>
          </div>
          <div class="flex items-center gap-1.5 shrink-0">
            <button type="button" onclick="navigateBack('aiModal')" class="btn-back flex items-center gap-1 text-white bg-white/20 hover:bg-white/30 px-2.5 py-1.5 rounded-lg text-[11px] font-bold">
              ← ተመለስ
            </button>
            <button id="aiModalClose" type="button" class="btn-close w-8 h-8 rounded-full bg-slate-900/80 hover:bg-slate-900 text-white flex items-center justify-center font-bold text-sm">✕</button>
          </div>
        </div>
        <!-- Sub-tabs for AI Hub -->
        <div class="grid grid-cols-2 gap-1 bg-black/20 p-0.5 rounded-xl text-xs font-bold">
          <button id="aiTabTools" type="button" class="py-1 rounded-lg bg-white text-[#16acbd] shadow-sm transition-all text-center">
            <span class="lang-am">🛠️ መሳሪያዎች</span>
            <span class="lang-en">🛠️ Tools Hub</span>
          </button>
          <button id="aiTabSearch" type="button" class="py-1 rounded-lg text-white/80 hover:text-white transition-all text-center">
            <span class="lang-am">🔍 ፈጣን ፍለጋ</span>
            <span class="lang-en">🔍 Smart Search</span>
          </button>
        </div>
      </div>

      <!-- Tab 1: AI Tools Hub -->
      <div id="aiToolsView" class="overflow-y-auto flex-1 p-4 space-y-4">
        <!-- Smart Budget & Purchase Advisor -->
        <div class="bg-gradient-to-br from-[#16acbd]/10 to-[#b5eff3]/40 p-3.5 rounded-2xl border border-[#16acbd]/30 space-y-2.5">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-1.5 text-[#0e7490] font-extrabold text-xs">
              <span>💡</span>
              <span class="lang-am">የግዢና የበጀት አማካሪ</span>
              <span class="lang-en">Purchase & Budget Advisor</span>
            </div>
            <span class="text-[9px] font-black uppercase px-2 py-0.5 rounded-full bg-[#16acbd]/20 text-[#0e7490] whitespace-nowrap shrink-0">Adika Advisor</span>
          </div>

          <!-- 1. Budget + Monthly Income inputs -->
          <div class="grid grid-cols-2 gap-2">
            <div>
              <div class="flex items-center justify-between mb-1">
                <label class="text-[10px] font-bold text-slate-700">ጠቅላላ በጀት (ETB)</label>
              </div>
              <input id="advisorBudget" type="number" value="2000000" placeholder="2,000,000" class="w-full px-2.5 py-1.5 rounded-xl bg-white border border-slate-200 text-[11px] font-bold text-slate-800 outline-none focus:ring-2 focus:ring-[#16acbd]" />
              <div id="advisorBudgetFormatted" class="text-[9px] font-extrabold text-[#0e7490] mt-0.5">2,000,000 ETB</div>
            </div>
            <div>
              <div class="flex items-center justify-between mb-1">
                <label class="text-[10px] font-bold text-slate-700">ወርሃዊ ገቢ (ETB)</label>
              </div>
              <input id="advisorMonthlyIncome" type="number" value="25000" placeholder="25,000" class="w-full px-2.5 py-1.5 rounded-xl bg-white border border-slate-200 text-[11px] font-bold text-slate-800 outline-none focus:ring-2 focus:ring-[#16acbd]" />
              <div id="advisorIncomeFormatted" class="text-[9px] font-extrabold text-slate-500 mt-0.5">25,000 / ወር</div>
            </div>
          </div>
          <div class="flex gap-1 overflow-x-auto no-scrollbar">
            <button type="button" class="advisor-preset-chip px-2 py-0.5 rounded-lg bg-white border border-slate-200 text-[10px] font-bold text-slate-700 whitespace-nowrap active:scale-95 transition-all" data-budget="70000">70k</button>
            <button type="button" class="advisor-preset-chip px-2 py-0.5 rounded-lg bg-white border border-slate-200 text-[10px] font-bold text-slate-700 whitespace-nowrap active:scale-95 transition-all" data-budget="500000">500k</button>
            <button type="button" class="advisor-preset-chip px-2 py-0.5 rounded-lg bg-white border border-slate-200 text-[10px] font-bold text-slate-700 whitespace-nowrap active:scale-95 transition-all" data-budget="1500000">1.5M</button>
            <button type="button" class="advisor-preset-chip px-2 py-0.5 rounded-lg bg-white border border-slate-200 text-[10px] font-bold text-slate-700 whitespace-nowrap active:scale-95 transition-all" data-budget="3000000">3M</button>
            <button type="button" class="advisor-preset-chip px-2 py-0.5 rounded-lg bg-white border border-slate-200 text-[10px] font-bold text-slate-700 whitespace-nowrap active:scale-95 transition-all" data-budget="6000000">6M</button>
          </div>

          <!-- Generate opportunity cards (does NOT jump to chat) -->
          <button id="advisorBtn" type="button" class="w-full py-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-white font-black text-xs shadow-md active:scale-95 transition-all flex items-center justify-center gap-1.5 border border-slate-700">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#fbbf24" stroke-width="2"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>
            <span>የኢንቨስትመንት አማራጮች አሳይ</span>
          </button>

          <!-- 3 Investment Opportunity Cards -->
          <div id="opportunityCards" class="hidden space-y-1.5">
            <div class="opp-card" data-opp="auto">
              <div class="opp-label text-amber-400">A · Automotive</div>
              <div class="opp-title">ተሽከርካሪ + የባንክ ብድር</div>
              <div id="oppAutoBody" class="opp-body">ከቀጥታ ገበያ እየተጫነ…</div>
              <button type="button" class="opp-cta opp-chat-cta" data-context="auto">ጥልቅ የፋይናንስ ትንተና ከ Adika Digital Advisor Live Chat ያድርጉ →</button>
            </div>
            <div class="opp-card" data-opp="property">
              <div class="opp-label text-sky-400">B · Real Estate</div>
              <div class="opp-title">ሪል እስቴት · ቅድመ ክፍያ</div>
              <div id="oppPropBody" class="opp-body">ከቀጥታ ገበያ እየተጫነ…</div>
              <button type="button" class="opp-cta opp-chat-cta" data-context="property">ጥልቅ የፋይናንስ ትንተና ከ Adika Digital Advisor Live Chat ያድርጉ →</button>
            </div>
            <div class="opp-card" data-opp="roi">
              <div class="opp-label text-emerald-400">C · Business ROI</div>
              <div class="opp-title">ንግድ / Startup · ዓመታዊ ROI</div>
              <div id="oppRoiBody" class="opp-body">ከበጀት ቀመር እየተሰላ…</div>
              <button type="button" class="opp-cta opp-chat-cta" data-context="roi">ጥልቅ የፋይናንስ ትንተና ከ Adika Digital Advisor Live Chat ያድርጉ →</button>
            </div>
          </div>

          <!-- Result Container -->
          <div id="advisorResult" class="hidden p-3 bg-white rounded-2xl border border-slate-200 text-xs text-slate-700 leading-relaxed font-medium shadow-sm space-y-3"></div>

          <!-- Extra filters: shown only AFTER analysis -->
          <div id="advisorExtraFilters" class="hidden space-y-2.5 pt-1">
            <div>
              <label class="text-[10px] font-bold text-slate-700 block mb-1">የግዢ አላማ (Purchase Purpose)</label>
              <div class="grid grid-cols-2 gap-1 bg-white/80 p-1 rounded-xl border border-slate-200">
                <button id="advisorPurposeBiz" type="button" class="advisor-purpose-btn py-1.5 px-2 rounded-lg bg-[#16acbd] text-white font-bold text-[10px] text-center transition-all shadow-sm flex items-center justify-center gap-1" data-purpose="business">
                  <span>🚕</span>
                  <span>ለስራ / ንግድ (Ride/Cargo)</span>
                </button>
                <button id="advisorPurposeFam" type="button" class="advisor-purpose-btn py-1.5 px-2 rounded-lg text-slate-600 font-bold text-[10px] text-center hover:bg-slate-100 transition-all flex items-center justify-center gap-1" data-purpose="personal">
                  <span>🏠</span>
                  <span>ለግል / ቤተሰብ (Personal)</span>
                </button>
              </div>
            </div>
            <div>
              <label class="text-[10px] font-bold text-slate-700 block mb-1">የግዢ መንገድ (Payment Strategy)</label>
              <div class="grid grid-cols-2 gap-1 bg-white/80 p-1 rounded-xl border border-slate-200">
                <button id="advisorPayCash" type="button" class="advisor-pay-btn py-1.5 px-2 rounded-lg bg-[#16acbd] text-white font-bold text-[10px] text-center transition-all shadow-sm flex items-center justify-center gap-1" data-pay="cash">
                  <span>💵</span>
                  <span>ባለኝ በጀት (Cash Buy)</span>
                </button>
                <button id="advisorPayLoan" type="button" class="advisor-pay-btn py-1.5 px-2 rounded-lg text-slate-600 font-bold text-[10px] text-center hover:bg-slate-100 transition-all flex items-center justify-center gap-1" data-pay="loan">
                  <span>🏦</span>
                  <span>በባንክ ብድር (Down Payment)</span>
                </button>
              </div>
            </div>
            <div id="advisorIncomeRow" class="hidden">
              <label class="text-[10px] font-bold text-slate-700 block mb-1">ወርሃዊ የተጣራ ገቢ (Monthly Net Income in ETB)</label>
              <input id="advisorIncome" type="number" placeholder="80,000" value="80000" class="w-full px-3 py-1.5 rounded-xl bg-white border border-slate-200 text-xs font-bold text-slate-800 outline-none" />
            </div>
          </div>
        </div>

        <!-- Tools Grid -->
        <div>
          <h4 class="text-xs font-extrabold text-slate-700 mb-2">
            <span class="lang-am">ተጨማሪ የፋይናንስና የህግ መሳሪያዎች</span>
            <span class="lang-en">Financial, Legal & Diagnostic Tools</span>
          </h4>
          <div class="tools-grid-compact text-xs">
            <button id="toolDutyBtn" type="button" class="tool-card-pro">
              <span class="tool-icon-wrap"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="4" y="3" width="16" height="18" rx="2"/><path d="M8 7h8M8 11h8M8 15h5"/></svg></span>
              <span class="tool-title">የቀረጥ ስሌት</span>
              <span class="tool-sub">Customs Duty & Taxes</span>
            </button>
            <button id="toolLoanBtn" type="button" class="tool-card-pro">
              <span class="tool-icon-wrap"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 10h18M5 10V8a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2v2M5 10v8a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-8"/><circle cx="12" cy="14" r="1.5"/></svg></span>
              <span class="tool-title">የባንክ ብድር</span>
              <span class="tool-sub">Mortgage & Auto Loan</span>
            </button>
            <button id="toolCompareBtn" type="button" class="tool-card-pro">
              <span class="tool-icon-wrap"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M8 7h8M8 12h8M8 17h5"/><path d="M4 4v16M20 4v16"/></svg></span>
              <span class="tool-title">የመኪና ንጽጽር</span>
              <span class="tool-sub">Vehicle Comparison</span>
            </button>
            <button id="toolContractBtn" type="button" class="tool-card-pro">
              <span class="tool-icon-wrap"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6M9 15l2 2 4-4"/></svg></span>
              <span class="tool-title">የሽያጭ ውል</span>
              <span class="tool-sub">Legal Sales Contract</span>
            </button>
            <button id="toolPoaBtn" type="button" class="tool-card-pro">
              <span class="tool-icon-wrap"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="M9 12l2 2 4-4"/></svg></span>
              <span class="tool-title">ውክልና ማረጋገጫ</span>
              <span class="tool-sub">Verify Power of Attorney</span>
            </button>
            <button id="toolDiagBtn" type="button" class="tool-card-pro">
              <span class="tool-icon-wrap"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.8-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.1a1.7 1.7 0 0 0-1.1-1.5 1.7 1.7 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.8 1.7 1.7 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1a1.7 1.7 0 0 0 1.5-1.1 1.7 1.7 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.8.3H9a1.7 1.7 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.8V9c.3.6.9 1 1.5 1H21a2 2 0 1 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1z"/></svg></span>
              <span class="tool-title">የምርመራ ወረቀት</span>
              <span class="tool-sub">Garage Diagnostic Sheet</span>
            </button>
            <button id="toolChassisBtn" type="button" class="tool-card-pro">
              <span class="tool-icon-wrap"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><circle cx="12" cy="11" r="3"/><path d="M12 14v3"/></svg></span>
              <span class="tool-title">የሻሲ ማረጋገጫ</span>
              <span class="tool-sub">Chassis / VIN Specs</span>
            </button>
            <button id="toolLandMapBtn" type="button" class="tool-card-pro">
              <span class="tool-icon-wrap"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="M9 12l2 2 4-4"/><circle cx="12" cy="10" r="2"/></svg></span>
              <span class="tool-title">የዲጂታል ካርታ ማጣሪያ</span>
              <span class="tool-sub">Cadastral Map Verification</span>
            </button>
          </div>
        </div>
      </div>

      <!-- Tab 2: AI Smart Search View -->
      <div id="aiSearchView" class="hidden overflow-y-auto flex-1 p-4 space-y-4">
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

        <div class="pt-2 flex gap-2">
          <button id="aiResetBtn" type="button" class="w-1/3 py-2.5 rounded-xl bg-slate-100 text-slate-700 font-bold text-xs">
            <span class="lang-am">አጽዳ</span><span class="lang-en">Reset</span>
          </button>
          <button id="aiApplyBtn" type="button" class="flex-1 py-2.5 rounded-xl bg-[#16acbd] text-white font-bold text-xs shadow-md active:scale-95 flex items-center justify-center gap-1.5">
            <span>✨ <span class="lang-am">አጣራ</span><span class="lang-en">Apply</span></span>
          </button>
        </div>
      </div>
    </div>
  </div>

  <!-- ================================================================= -->
  <!-- 5. BOTTOM-SHEET DETAIL MODAL WITH DYNAMIC ACTION BUTTONS          -->
  <!-- ================================================================= -->
  <div id="modalOverlay" class="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm hidden items-end justify-center">
    <div id="modalSheet"
      class="w-full max-w-md bg-white rounded-t-3xl max-h-[88vh] flex flex-col shadow-2xl overflow-hidden">

      <div class="px-3 py-2 bg-white border-b border-slate-100 flex items-center justify-between shrink-0 gap-2">
        <div class="flex items-center gap-1.5 min-w-0">
          <button id="modalBackBtn" type="button" class="btn-back flex items-center gap-1 px-2.5 py-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-[11px] shrink-0">← ተመለስ</button>
          <span id="modalCategoryBadge" class="px-2 py-0.5 rounded-full bg-[#16acbd]/10 text-[#0e7490] text-[10px] font-bold truncate">Property</span>
          <span id="modalIdBadge" class="text-[10px] text-slate-400 font-semibold shrink-0">#ADK-</span>
        </div>
        <div class="flex items-center gap-1.5 shrink-0">
          <button id="modalFavBtn" type="button" class="w-7 h-7 rounded-full bg-slate-100 text-slate-400 hover:text-rose-500 font-bold flex items-center justify-center text-sm">❤️</button>
          <button id="modalClose" type="button" class="w-7 h-7 rounded-full bg-slate-800 text-white font-bold flex items-center justify-center text-sm shadow-sm" aria-label="Close">✕</button>
        </div>
      </div>

      <div id="modalScrollBody" class="overflow-y-auto flex-1 p-4 space-y-3.5 pb-2">
        <div id="modalMediaContainer" class="w-full aspect-[4/3] rounded-2xl overflow-hidden bg-slate-100 relative"></div>

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

        <!-- Category-Specific Dynamic Action Buttons Bar -->
        <div id="modalDynamicActions" class="p-2.5 bg-[#b5eff3]/30 rounded-2xl border border-[#16acbd]/30 space-y-1.5">
          <div class="text-[10px] font-extrabold text-[#0e7490] uppercase tracking-wider flex items-center gap-1">
            <span>✨</span>
            <span class="lang-am">ተዛማጅ የAI እና የፋይናንስ አገልግሎቶች</span>
            <span class="lang-en">Smart AI & Financial Utilities</span>
          </div>
          <div id="modalActionButtonsRow" class="flex gap-1.5 overflow-x-auto no-scrollbar"></div>
        </div>

        <div id="modalSpecs" class="grid grid-cols-2 gap-2 text-xs font-medium text-slate-600 bg-slate-50 p-2.5 rounded-xl border border-slate-100"></div>

        <div>
          <h4 class="text-[11px] font-bold text-slate-500 uppercase tracking-wider mb-1">
            <span class="lang-am">ዝርዝር መግለጫ</span>
            <span class="lang-en">Full Description</span>
          </h4>
          <p id="modalDesc" class="text-xs text-slate-700 leading-relaxed whitespace-pre-line bg-slate-50/50 p-2.5 rounded-xl border border-slate-100"></p>
        </div>

        <!-- Behavioral recommendations + Smart Alert -->
        <div id="modalRecoSection" class="space-y-2.5 pt-1">
          <div class="flex items-center justify-between gap-2">
            <div id="modalRecoTitle" class="text-[11px] font-extrabold text-slate-800">🤖 ለእርስዎ የተመረጡ ተቀራራቢ መኪኖች</div>
            <div id="modalRecoIntent" class="text-[9px] font-bold text-[#0e7490] bg-[#16acbd]/10 px-2 py-0.5 rounded-full truncate max-w-[45%]"></div>
          </div>
          <div id="modalRecoScroll" class="flex gap-2.5 overflow-x-auto no-scrollbar pb-1 -mx-0.5 px-0.5"></div>
          <div id="modalAlertCard" class="hidden p-3 rounded-2xl border border-amber-200 bg-gradient-to-r from-amber-50 via-orange-50 to-amber-50 space-y-2 shadow-sm">
            <p id="modalAlertText" class="text-[11px] text-slate-700 font-medium leading-relaxed"></p>
            <button type="button" id="modalAlertBtn" class="w-full py-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-white font-bold text-[11px] active:scale-[0.98]">
              🔔 አዎ! በቴሌግራም አሳውቀኝ (Subscribe to Alerts)
            </button>
            <div id="modalAlertStatus" class="text-[10px] font-bold text-emerald-700 hidden"></div>
          </div>
        </div>
      </div>

      <!-- Sticky bottom action bar -->
      <div class="p-2.5 bg-white/95 backdrop-blur-md border-t border-slate-100 shrink-0 grid grid-cols-3 gap-2 sticky bottom-0 z-10 shadow-[0_-4px_12px_rgba(0,0,0,0.06)]">
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
  <!-- 6. STANDALONE INTERACTIVE MODALS FOR AI TOOLS                     -->
  <!-- ================================================================= -->

  <!-- Modal: Customs Duty Calculator -->
  <div id="dutyModal" class="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm hidden items-end justify-center">
    <div class="w-full max-w-md bg-white rounded-t-3xl max-h-[88vh] flex flex-col shadow-2xl overflow-hidden">
      <div class="px-4 py-3 bg-[#16acbd] text-white flex items-center justify-between shrink-0">
        <h3 class="font-extrabold text-xs tracking-wide">🧮 የኢትዮጵያ ጉምሩክ የቀረጥ ስሌት (Duty Calculator)</h3>
        <div class="flex items-center gap-1.5 shrink-0">
          <button type="button" onclick="navigateBack('dutyModal')" class="btn-back flex items-center gap-1 text-white bg-white/20 hover:bg-white/30 px-2.5 py-1.5 rounded-lg text-[11px] font-bold">
            ← ተመለስ
          </button>
          <button type="button" onclick="closeModal('dutyModal')" class="btn-close w-8 h-8 rounded-full bg-slate-900/80 hover:bg-slate-900 text-white flex items-center justify-center font-bold text-sm" aria-label="Close">
            ✕
          </button>
        </div>
      </div>
      <div class="p-4 overflow-y-auto space-y-3 flex-1 text-xs">
        <div>
          <label class="font-bold text-slate-700 block mb-1">የመኪናው CIF ዋጋ (USD / ዶላር)</label>
          <input id="dutyCif" type="number" value="12000" class="w-full p-2 rounded-xl bg-slate-50 border text-xs font-bold" />
        </div>
        <div class="grid grid-cols-2 gap-2">
          <div>
            <label class="font-bold text-slate-700 block mb-1">የነዳጅ ዓይነት</label>
            <select id="dutyFuel" class="w-full p-2 rounded-xl bg-slate-50 border text-xs font-bold">
              <option value="Benzine">Benzine (ቤንዚን)</option>
              <option value="Diesel">Diesel (ናፍጣ)</option>
              <option value="Electric">Electric (ኤሌክትሪክ EV - 5% ቀረጥ)</option>
            </select>
          </div>
          <div>
            <label class="font-bold text-slate-700 block mb-1">የሞተር መጠን (CC)</label>
            <input id="dutyCc" type="number" value="1300" class="w-full p-2 rounded-xl bg-slate-50 border text-xs font-bold" />
          </div>
        </div>
        <button id="dutyCalculateBtn" class="w-full py-2.5 bg-[#16acbd] text-white font-bold rounded-xl shadow active:scale-95">ቀረጥ አስላ (Calculate)</button>
        <div id="dutyResult" class="hidden p-3 bg-slate-50 rounded-xl border space-y-1.5 font-medium"></div>
      </div>
    </div>
  </div>

  <!-- Modal: Bank Loan & Mortgage -->
  <div id="loanModal" class="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm hidden items-end justify-center">
    <div class="w-full max-w-md bg-white rounded-t-3xl max-h-[88vh] flex flex-col shadow-2xl overflow-hidden">
      <div class="px-4 py-3 bg-[#16acbd] text-white flex items-center justify-between shrink-0">
        <h3 class="font-extrabold text-xs tracking-wide">🏦 የባንክ ብድርና ወርሃዊ ክፍያ (Bank Loan)</h3>
        <div class="flex items-center gap-1.5 shrink-0">
          <button type="button" onclick="navigateBack('loanModal')" class="btn-back flex items-center gap-1 text-white bg-white/20 hover:bg-white/30 px-2.5 py-1.5 rounded-lg text-[11px] font-bold">
            ← ተመለስ
          </button>
          <button type="button" onclick="closeModal('loanModal')" class="btn-close w-8 h-8 rounded-full bg-slate-900/80 hover:bg-slate-900 text-white flex items-center justify-center font-bold text-sm" aria-label="Close">
            ✕
          </button>
        </div>
      </div>
      <div class="p-4 overflow-y-auto space-y-3 flex-1 text-xs">
        <div>
          <label class="font-bold text-slate-700 block mb-1">የንብረቱ ዋጋ (ብር)</label>
          <input id="loanPrice" type="number" value="3000000" class="w-full p-2 rounded-xl bg-slate-50 border text-xs font-bold" />
        </div>
        <div class="grid grid-cols-2 gap-2">
          <div>
            <label class="font-bold text-slate-700 block mb-1">ቅድመ ክፍያ (%)</label>
            <input id="loanDown" type="number" value="30" class="w-full p-2 rounded-xl bg-slate-50 border text-xs font-bold" />
          </div>
          <div>
            <label class="font-bold text-slate-700 block mb-1">የመክፈያ ዓመታት</label>
            <input id="loanYears" type="number" value="10" class="w-full p-2 rounded-xl bg-slate-50 border text-xs font-bold" />
          </div>
        </div>
        <button id="loanCalculateBtn" class="w-full py-2.5 bg-[#16acbd] text-white font-bold rounded-xl shadow active:scale-95">ብድር አስላ (Calculate)</button>
        <div id="loanResult" class="hidden p-3 bg-slate-50 rounded-xl border space-y-1.5 font-medium"></div>
      </div>
    </div>
  </div>

  <!-- Modal: Executive Institutional Comparison Dashboard -->
  <div id="compareModal" class="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm hidden items-end justify-center">
    <div class="w-full max-w-md bg-slate-950 rounded-t-3xl max-h-[92vh] flex flex-col shadow-2xl overflow-hidden border border-slate-800">
      <div class="px-3 py-2.5 bg-gradient-to-r from-slate-950 via-slate-900 to-slate-950 text-white flex items-center justify-between shrink-0 border-b border-slate-800">
        <div class="min-w-0">
          <div class="text-[9px] font-bold tracking-wide uppercase text-amber-400/90">Adika Institutional Analytics</div>
          <h3 class="font-black text-xs tracking-wide truncate">Comparison Engine</h3>
        </div>
        <div class="flex items-center gap-1.5 shrink-0">
          <button type="button" onclick="navigateBack('compareModal')" class="btn-back flex items-center gap-1 text-white bg-white/20 hover:bg-white/30 px-2.5 py-1.5 rounded-lg text-[11px] font-bold">
            ← ተመለስ
          </button>
          <button type="button" onclick="closeModal('compareModal')" class="btn-close w-8 h-8 rounded-full bg-slate-900/80 hover:bg-slate-900 text-white flex items-center justify-center font-bold text-sm" aria-label="Close">
            ✕
          </button>
        </div>
      </div>

      <div class="px-3 pt-2.5 shrink-0">
        <div class="flex p-0.5 rounded-full bg-slate-900 border border-slate-800 gap-0.5" id="compareTabs">
          <button type="button" data-ctab="vehicles" class="compare-tab flex-1 py-1.5 rounded-full text-[10px] font-extrabold transition-all bg-teal-600 text-white shadow">🚗 ተሽከርካሪ</button>
          <button type="button" data-ctab="property" class="compare-tab flex-1 py-1.5 rounded-full text-[10px] font-extrabold transition-all text-slate-400 hover:text-white">🏠 ሪል ስቴት</button>
          <button type="button" data-ctab="business" class="compare-tab flex-1 py-1.5 rounded-full text-[10px] font-extrabold transition-all text-slate-400 hover:text-white">💼 ቢዝነስ ROI</button>
        </div>
      </div>

      <div class="p-3 overflow-y-auto space-y-2.5 flex-1 text-xs">
        <!-- VEHICLES: hybrid autocomplete + free text -->
        <div id="comparePanelVehicles" class="space-y-2">
          <div class="grid grid-cols-2 gap-2">
            <div class="relative space-y-1">
              <label class="text-[9px] font-bold text-slate-400 block">መኪና A (ሞዴል)</label>
              <input id="compareCar1" type="text" list="vehicleSuggestions" autocomplete="off" placeholder="e.g. Toyota Belta" value="Toyota Vitz" class="w-full p-2 rounded-xl bg-slate-900 border border-slate-700 text-[11px] font-bold text-white outline-none focus:ring-1 focus:ring-teal-500" />
              <label class="text-[8px] font-bold text-slate-500">የምርት ዘመን (Year)</label>
              <input id="compareYear1" type="number" min="1990" max="2026" placeholder="2018" value="2018" class="w-full p-1.5 rounded-lg bg-slate-900 border border-slate-700 text-[11px] font-bold text-white outline-none focus:ring-1 focus:ring-teal-500" />
            </div>
            <div class="relative space-y-1">
              <label class="text-[9px] font-bold text-slate-400 block">መኪና B (ሞዴል)</label>
              <input id="compareCar2" type="text" list="vehicleSuggestions" autocomplete="off" placeholder="e.g. BYD Dolphin" value="BYD Dolphin" class="w-full p-2 rounded-xl bg-slate-900 border border-slate-700 text-[11px] font-bold text-white outline-none focus:ring-1 focus:ring-teal-500" />
              <label class="text-[8px] font-bold text-slate-500">የምርት ዘመን (Year)</label>
              <input id="compareYear2" type="number" min="1990" max="2026" placeholder="2023" value="2023" class="w-full p-1.5 rounded-lg bg-slate-900 border border-slate-700 text-[11px] font-bold text-white outline-none focus:ring-1 focus:ring-teal-500" />
            </div>
          </div>
          <datalist id="vehicleSuggestions">
            <option value="Toyota Vitz"><option value="Toyota Yaris"><option value="Toyota Corolla">
            <option value="Toyota Belta"><option value="Toyota RAV4"><option value="Toyota Fortuner">
            <option value="Toyota Hilux"><option value="Toyota Land Cruiser Prado"><option value="Toyota Land Cruiser 70">
            <option value="Toyota Hiace"><option value="BYD Seagull"><option value="BYD Dolphin"><option value="BYD Song Plus">
            <option value="Suzuki Dzire"><option value="Suzuki Swift"><option value="Hyundai Accent"><option value="Hyundai Tucson">
          </datalist>
          <p class="text-[9px] text-slate-500">በvehicles_db ከሌለ AI የጉምሩክ/ነዳጅ/ዋጋ ግምት ያሰላል (እንደ estimate ምልክት ይደረጋል)።</p>
        </div>

        <!-- PROPERTY: asset class selectors -->
        <div id="comparePanelProperty" class="hidden space-y-2">
          <div class="grid grid-cols-2 gap-2">
            <div>
              <label class="text-[9px] font-bold text-slate-400 block mb-1">Asset A</label>
              <select id="compareAsset1" class="w-full p-2 rounded-xl bg-slate-900 border border-slate-700 text-[11px] font-bold text-white">
                <option value="apartment">አፓርትመንት</option>
                <option value="condo">ኮንዶሚኒየም</option>
                <option value="residential_villa">ቪላ / የመኖሪያ ቤት</option>
                <option value="vacant_land">ባዶ መሬት</option>
                <option value="commercial_shop">የንግድ ሱቅ</option>
                <option value="warehouse">ዌርሃውስ</option>
              </select>
            </div>
            <div>
              <label class="text-[9px] font-bold text-slate-400 block mb-1">Asset B</label>
              <select id="compareAsset2" class="w-full p-2 rounded-xl bg-slate-900 border border-slate-700 text-[11px] font-bold text-white">
                <option value="vacant_land">ባዶ መሬት</option>
                <option value="apartment">አፓርትመንት</option>
                <option value="condo">ኮንዶሚኒየም</option>
                <option value="residential_villa">ቪላ / የመኖሪያ ቤት</option>
                <option value="commercial_shop">የንግድ ሱቅ</option>
                <option value="warehouse">ዌርሃውስ</option>
              </select>
            </div>
          </div>
          <div>
            <label class="text-[9px] font-bold text-slate-400 block mb-1">ማጣቀሻ በጀት (ETB)</label>
            <input id="comparePropBudget" type="number" value="3000000" class="w-full p-2 rounded-xl bg-slate-900 border border-slate-700 text-[11px] font-bold text-white" />
          </div>
          <p class="text-[9px] text-slate-500">Inflation hedge · Rental yield · 3/5yr appreciation · Development score</p>
        </div>

        <!-- BUSINESS: custom names -->
        <div id="comparePanelBusiness" class="hidden space-y-2">
          <div class="grid grid-cols-2 gap-2">
            <div>
              <label class="text-[9px] font-bold text-slate-400 block mb-1">ንግድ A</label>
              <input id="compareBiz1" type="text" value="Café & Restaurant" placeholder="e.g. Café & Restaurant" class="w-full p-2 rounded-xl bg-slate-900 border border-slate-700 text-[11px] font-bold text-white" />
            </div>
            <div>
              <label class="text-[9px] font-bold text-slate-400 block mb-1">ንግድ B</label>
              <input id="compareBiz2" type="text" value="Cosmetics Import" placeholder="e.g. Cosmetics Import" class="w-full p-2 rounded-xl bg-slate-900 border border-slate-700 text-[11px] font-bold text-white" />
            </div>
          </div>
          <p class="text-[9px] text-slate-500">Capital · Space · Labor · Demand · Risk · Breakeven · ROI</p>
        </div>

        <button id="compareBtn" type="button" class="w-full py-2.5 rounded-xl bg-gradient-to-r from-teal-600 to-emerald-600 text-white font-black text-xs shadow-lg active:scale-[0.98]">ውጤቱን ይመልከቱ →</button>
        <div id="compareResult" class="hidden space-y-2.5"></div>
      </div>
    </div>
  </div>

  <!-- Modal: Legal Contract Generator -->
  <div id="contractModal" class="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm hidden items-end justify-center">
    <div class="w-full max-w-md bg-white rounded-t-3xl max-h-[92vh] flex flex-col shadow-2xl overflow-hidden">
      <div class="px-4 py-3 bg-[#16acbd] text-white flex items-center justify-between shrink-0">
        <h3 class="font-extrabold text-xs tracking-wide">📜 ህጋዊ ውል ማዘጋጃ (Contract Wizard)</h3>
        <div class="flex items-center gap-1.5 shrink-0">
          <button type="button" onclick="navigateBack('contractModal')" class="btn-back flex items-center gap-1 text-white bg-white/20 hover:bg-white/30 px-2.5 py-1.5 rounded-lg text-[11px] font-bold">← ተመለስ</button>
          <button type="button" onclick="closeModal('contractModal')" class="btn-close w-8 h-8 rounded-full bg-slate-900/80 hover:bg-slate-900 text-white flex items-center justify-center font-bold text-sm" aria-label="Close">✕</button>
        </div>
      </div>

      <div class="px-3 pt-2 pb-1 bg-slate-50 border-b border-slate-100 shrink-0">
        <div class="grid grid-cols-4 gap-1 p-0.5 bg-slate-200/60 rounded-xl">
          <button type="button" class="contract-step-tab py-1.5 rounded-lg text-[9px] font-extrabold transition-all bg-white text-[#0e7490] shadow-sm" data-step="0">ዓይነት</button>
          <button type="button" class="contract-step-tab py-1.5 rounded-lg text-[9px] font-extrabold transition-all text-slate-500" data-step="1">ተዋዋዮች</button>
          <button type="button" class="contract-step-tab py-1.5 rounded-lg text-[9px] font-extrabold transition-all text-slate-500" data-step="2">ንብረት</button>
          <button type="button" class="contract-step-tab py-1.5 rounded-lg text-[9px] font-extrabold transition-all text-slate-500" data-step="3">ገንዘብ</button>
        </div>
      </div>

      <div class="p-3.5 overflow-y-auto space-y-3 flex-1 text-xs">
        <!-- STEP 0: Type -->
        <div id="contractStep0" class="contract-step space-y-2">
          <div class="text-[11px] font-black text-slate-800">የውል ዓይነት ይምረጡ</div>
          <div class="grid grid-cols-1 gap-2">
            <label class="c-type-opt flex items-center gap-2 p-3 rounded-xl border-2 border-[#16acbd] bg-[#16acbd]/5 cursor-pointer">
              <input type="radio" name="cContractType" value="vehicle_sale" checked class="accent-[#16acbd]" />
              <span class="font-bold text-slate-800">🚗 የመኪና ሽያጭ ውል (Vehicle Sale)</span>
            </label>
            <label class="c-type-opt flex items-center gap-2 p-3 rounded-xl border border-slate-200 bg-white cursor-pointer">
              <input type="radio" name="cContractType" value="vehicle_rental" class="accent-[#16acbd]" />
              <span class="font-bold text-slate-800">🔑 የመኪና ኪራይ ውል (Vehicle Rental)</span>
            </label>
            <label class="c-type-opt flex items-center gap-2 p-3 rounded-xl border border-slate-200 bg-white cursor-pointer">
              <input type="radio" name="cContractType" value="house_sale" class="accent-[#16acbd]" />
              <span class="font-bold text-slate-800">🏠 የቤት ሽያጭ ውል (House Sale)</span>
            </label>
            <label class="c-type-opt flex items-center gap-2 p-3 rounded-xl border border-slate-200 bg-white cursor-pointer">
              <input type="radio" name="cContractType" value="house_rental" class="accent-[#16acbd]" />
              <span class="font-bold text-slate-800">🏢 የቤት ኪራይ ውል (House Rental)</span>
            </label>
          </div>
        </div>

        <!-- STEP 1: Parties -->
        <div id="contractStep1" class="contract-step space-y-2.5 hidden">
          <div class="text-[11px] font-black text-slate-800">የተዋዋዮች መረጃ</div>
          <div class="p-2 rounded-xl bg-slate-50 border space-y-2">
            <div class="text-[10px] font-extrabold text-[#0e7490]" id="cPartyALabel">ውል ሰጪ / ሻጭ / አከራይ</div>
            <input id="cSellerName" type="text" placeholder="ሙሉ ስም *" class="w-full p-2 rounded-xl bg-white border text-xs font-bold" />
            <div class="grid grid-cols-2 gap-2">
              <input id="cSellerNationality" type="text" value="ኢትዮጵያዊ" class="w-full p-2 rounded-xl bg-white border text-xs font-bold" />
              <input id="cSellerPhone" type="tel" placeholder="ስልክ *" class="w-full p-2 rounded-xl bg-white border text-xs font-bold" />
            </div>
            <div class="grid grid-cols-2 gap-2">
              <select id="cSellerSubCity" class="w-full p-2 rounded-xl bg-white border text-xs font-bold">                <option value="">— ይምረጡ —</option>
                <option>አዲስ ከተማ</option>
                <option>አቃቂ ቃሊቲ</option>
                <option>አራዳ</option>
                <option>ቦሌ</option>
                <option>ጉለሌ</option>
                <option>ቂርቆስ</option>
                <option>ኮልፌ ቀራንዮ</option>
                <option>ልደታ</option>
                <option>ንፋስ ስልክ ላፍቶ</option>
                <option>የካ</option>
                <option>ሌሚ ኩራ</option>
              </select>
              <input id="cSellerWoreda" type="text" placeholder="ወረዳ" class="w-full p-2 rounded-xl bg-white border text-xs font-bold" />
            </div>
            <input id="cSellerHouseNo" type="text" placeholder="የቤት ቁጥር" class="w-full p-2 rounded-xl bg-white border text-xs font-bold" />
          </div>
          <div class="p-2 rounded-xl bg-slate-50 border space-y-2">
            <div class="text-[10px] font-extrabold text-[#0e7490]" id="cPartyBLabel">ውል ተቀባይ / ገዢ / ተከራይ</div>
            <input id="cBuyerName" type="text" placeholder="ሙሉ ስም *" class="w-full p-2 rounded-xl bg-white border text-xs font-bold" />
            <div class="grid grid-cols-2 gap-2">
              <input id="cBuyerNationality" type="text" value="ኢትዮጵያዊ" class="w-full p-2 rounded-xl bg-white border text-xs font-bold" />
              <input id="cBuyerPhone" type="tel" placeholder="ስልክ *" class="w-full p-2 rounded-xl bg-white border text-xs font-bold" />
            </div>
            <div class="grid grid-cols-2 gap-2">
              <select id="cBuyerSubCity" class="w-full p-2 rounded-xl bg-white border text-xs font-bold">                <option value="">— ይምረጡ —</option>
                <option>አዲስ ከተማ</option>
                <option>አቃቂ ቃሊቲ</option>
                <option>አራዳ</option>
                <option>ቦሌ</option>
                <option>ጉለሌ</option>
                <option>ቂርቆስ</option>
                <option>ኮልፌ ቀራንዮ</option>
                <option>ልደታ</option>
                <option>ንፋስ ስልክ ላፍቶ</option>
                <option>የካ</option>
                <option>ሌሚ ኩራ</option>
              </select>
              <input id="cBuyerWoreda" type="text" placeholder="ወረዳ" class="w-full p-2 rounded-xl bg-white border text-xs font-bold" />
            </div>
            <input id="cBuyerHouseNo" type="text" placeholder="የቤት ቁጥር" class="w-full p-2 rounded-xl bg-white border text-xs font-bold" />
          </div>
        </div>

        <!-- STEP 2: Asset fields (dynamic by type) -->
        <div id="contractStep2" class="contract-step space-y-2.5 hidden">
          <div class="text-[11px] font-black text-slate-800">የንብረት / መኪና መረጃ</div>
          <!-- Vehicle fields -->
          <div id="cFieldsVehicle" class="space-y-2">
            <div class="flex items-center justify-between">
              <span class="text-[10px] font-bold text-slate-500">መኪና</span>
              <label class="inline-flex items-center gap-1 px-2 py-1 rounded-lg bg-slate-900 text-white text-[10px] font-bold cursor-pointer">
                📷 ሊብሬ
                <input id="cLibreFile" type="file" accept="image/*" class="hidden" />
              </label>
            </div>
            <div id="cLibreStatus" class="hidden text-[10px] font-bold text-[#0e7490]"></div>
            <input id="cPlate" type="text" placeholder="ሰሌዳ ቁጥር *" class="w-full p-2 rounded-xl bg-slate-50 border text-xs font-bold" />
            <input id="cChassis" type="text" placeholder="ቻሲ / Chassis *" class="w-full p-2 rounded-xl bg-slate-50 border text-xs font-bold font-mono" />
            <input id="cEngine" type="text" placeholder="የሞተር ቁጥር" class="w-full p-2 rounded-xl bg-slate-50 border text-xs font-bold font-mono" />
            <input id="cCarModel" type="text" placeholder="የመኪና ዓይነት / ሞዴል *" class="w-full p-2 rounded-xl bg-slate-50 border text-xs font-bold" />
          </div>
          <!-- House fields -->
          <div id="cFieldsHouse" class="space-y-2 hidden">
            <div class="grid grid-cols-2 gap-2">
              <select id="cHouseSubCity" class="w-full p-2 rounded-xl bg-slate-50 border text-xs font-bold">                <option value="">— ይምረጡ —</option>
                <option>አዲስ ከተማ</option>
                <option>አቃቂ ቃሊቲ</option>
                <option>አራዳ</option>
                <option>ቦሌ</option>
                <option>ጉለሌ</option>
                <option>ቂርቆስ</option>
                <option>ኮልፌ ቀራንዮ</option>
                <option>ልደታ</option>
                <option>ንፋስ ስልክ ላፍቶ</option>
                <option>የካ</option>
                <option>ሌሚ ኩራ</option>
              </select>
              <input id="cHouseWoreda" type="text" placeholder="የቤት ወረዳ" class="w-full p-2 rounded-xl bg-slate-50 border text-xs font-bold" />
            </div>
            <input id="cHouseNo" type="text" placeholder="የቤት ቁጥር" class="w-full p-2 rounded-xl bg-slate-50 border text-xs font-bold" />
            <input id="cTitleDeed" type="text" placeholder="የካርታ / ደብተር ቁጥር" class="w-full p-2 rounded-xl bg-slate-50 border text-xs font-bold" />
            <input id="cAreaSqm" type="text" placeholder="ስፋት (ካ.ሜ)" class="w-full p-2 rounded-xl bg-slate-50 border text-xs font-bold" />
            <select id="cHouseUse" class="w-full p-2 rounded-xl bg-slate-50 border text-xs font-bold">
              <option value="የመኖሪያ">የመኖሪያ ቤት</option>
              <option value="የንግድ">የንግድ ቤት</option>
            </select>
          </div>
        </div>

        <!-- STEP 3: Money + Witnesses -->
        <div id="contractStep3" class="contract-step space-y-2.5 hidden">
          <div class="text-[11px] font-black text-slate-800">የገንዘብና ምስክሮች</div>
          <!-- Sale financials -->
          <div id="cFinSale" class="space-y-2">
            <div class="grid grid-cols-2 gap-2">
              <div>
                <label class="font-bold text-slate-600 block mb-1">ጠቅላላ ዋጋ (ብር) *</label>
                <input id="cTotalPrice" type="text" placeholder="2,200,000" class="w-full p-2 rounded-xl bg-slate-50 border text-xs font-bold" />
              </div>
              <div>
                <label class="font-bold text-slate-600 block mb-1">ቅድመ ክፍያ (ብር)</label>
                <input id="cAdvance" type="text" placeholder="500,000" class="w-full p-2 rounded-xl bg-slate-50 border text-xs font-bold" />
              </div>
            </div>
            <div class="p-2.5 rounded-xl bg-emerald-50 border border-emerald-200 flex justify-between items-center">
              <span class="font-bold text-emerald-800 text-[10px]">ቀሪ ክፍያ</span>
              <span id="cBalance" class="font-black text-emerald-900 text-sm">0 ብር</span>
            </div>
            <input id="cDeadline" type="text" placeholder="ማለቂያ ቀን (ምሳ. ጥቅምት 30 ቀን 2018 ዓ.ም)" class="w-full p-2 rounded-xl bg-slate-50 border text-xs font-bold" />
          </div>
          <!-- Rental financials -->
          <div id="cFinRental" class="space-y-2 hidden">
            <div class="grid grid-cols-2 gap-2">
              <input id="cRentRate" type="text" placeholder="የኪራይ ዋጋ (ብር) *" class="w-full p-2 rounded-xl bg-slate-50 border text-xs font-bold" />
              <select id="cRentPeriod" class="w-full p-2 rounded-xl bg-slate-50 border text-xs font-bold">
                <option value="በወር">በወር</option>
                <option value="በቀን">በቀን</option>
              </select>
            </div>
            <input id="cRentStart" type="text" placeholder="መጀመሪያ ቀን (አማርኛ ጽሁፍ)" class="w-full p-2 rounded-xl bg-slate-50 border text-xs font-bold" />
            <input id="cRentEnd" type="text" placeholder="ማለቂያ ቀን / የኪራይ ዘመን" class="w-full p-2 rounded-xl bg-slate-50 border text-xs font-bold" />
            <input id="cRentAdvanceMonths" type="text" placeholder="የተከፈለ ቅድመ ወራት ብዛት (ለቤት ኪራይ)" class="w-full p-2 rounded-xl bg-slate-50 border text-xs font-bold" />
            <input id="cRentAdvanceTotal" type="text" placeholder="ጠቅላላ የተከፈለ ቅድመ ኪራይ (ብር)" class="w-full p-2 rounded-xl bg-slate-50 border text-xs font-bold" />
          </div>
          <label class="font-bold text-slate-600 block mb-1">የውል ማፍረሻ ካሳ (በብር)</label>
          <input id="cPenalty" type="text" value="50000" placeholder="50000" class="w-full p-2 rounded-xl bg-slate-50 border text-xs font-bold" />
          <input id="cContractDate" type="text" placeholder="የውል ቀን (ምሳ. መስከረም 15 ቀን 2018 ዓ.ም)" class="w-full p-2 rounded-xl bg-slate-50 border text-xs font-bold" />

          <details class="rounded-xl border border-slate-200 bg-white" open>
            <summary class="cursor-pointer px-3 py-2 font-bold text-slate-700 text-[11px]">👥 3 ምስክሮች</summary>
            <div class="p-3 pt-1 space-y-3 border-t border-slate-100">
              <div class="space-y-1.5 p-2 bg-slate-50 rounded-xl">
                <div class="text-[10px] font-extrabold text-slate-500">ምስክር 1</div>
                <input id="cWit1Name" type="text" placeholder="ሙሉ ስም" class="w-full p-2 rounded-lg bg-white border text-xs font-bold" />
                <div class="grid grid-cols-2 gap-1.5">
                  <input id="cWit1Nat" type="text" value="ኢትዮጵያዊ" class="w-full p-2 rounded-lg bg-white border text-xs font-bold" />
                  <input id="cWit1Phone" type="tel" placeholder="ስልክ" class="w-full p-2 rounded-lg bg-white border text-xs font-bold" />
                </div>
                <input id="cWit1Addr" type="text" placeholder="ክ/ከተማ · ወረዳ · ቤት ቁ" class="w-full p-2 rounded-lg bg-white border text-xs font-bold" />
              </div>
              <div class="space-y-1.5 p-2 bg-slate-50 rounded-xl">
                <div class="text-[10px] font-extrabold text-slate-500">ምስክር 2</div>
                <input id="cWit2Name" type="text" placeholder="ሙሉ ስም" class="w-full p-2 rounded-lg bg-white border text-xs font-bold" />
                <div class="grid grid-cols-2 gap-1.5">
                  <input id="cWit2Nat" type="text" value="ኢትዮጵያዊ" class="w-full p-2 rounded-lg bg-white border text-xs font-bold" />
                  <input id="cWit2Phone" type="tel" placeholder="ስልክ" class="w-full p-2 rounded-lg bg-white border text-xs font-bold" />
                </div>
                <input id="cWit2Addr" type="text" placeholder="ክ/ከተማ · ወረዳ · ቤት ቁ" class="w-full p-2 rounded-lg bg-white border text-xs font-bold" />
              </div>
              <div class="space-y-1.5 p-2 bg-slate-50 rounded-xl">
                <div class="text-[10px] font-extrabold text-slate-500">ምስክር 3</div>
                <input id="cWit3Name" type="text" placeholder="ሙሉ ስም" class="w-full p-2 rounded-lg bg-white border text-xs font-bold" />
                <div class="grid grid-cols-2 gap-1.5">
                  <input id="cWit3Nat" type="text" value="ኢትዮጵያዊ" class="w-full p-2 rounded-lg bg-white border text-xs font-bold" />
                  <input id="cWit3Phone" type="tel" placeholder="ስልክ" class="w-full p-2 rounded-lg bg-white border text-xs font-bold" />
                </div>
                <input id="cWit3Addr" type="text" placeholder="ክ/ከተማ · ወረዳ · ቤት ቁ" class="w-full p-2 rounded-lg bg-white border text-xs font-bold" />
              </div>
            </div>
          </details>
        </div>

        <div id="contractResult" class="hidden p-3 bg-slate-50 rounded-xl border space-y-2 font-medium text-xs"></div>
      </div>

      <div class="p-2.5 border-t border-slate-100 bg-white shrink-0 space-y-2">
        <div class="flex gap-2">
          <button type="button" id="cStepPrev" class="flex-1 py-2 rounded-xl bg-slate-100 text-slate-700 font-bold text-[11px] hidden">← ቀድሞ</button>
          <button type="button" id="cStepNext" class="flex-1 py-2 rounded-xl bg-slate-800 text-white font-bold text-[11px]">ቀጣይ →</button>
        </div>
        <div class="grid grid-cols-2 gap-2">
          <button type="button" id="cSaveDraftBtn" class="py-2.5 rounded-xl bg-white border border-slate-200 text-slate-800 font-bold text-[11px]">💾 ረቂቅ አስቀምጥ</button>
          <button type="button" id="cFinalizeBtn" class="py-2.5 rounded-xl bg-[#16acbd] text-white font-bold text-[11px] shadow">📄 ውል አጠናቅቅ</button>
        </div>
      </div>
    </div>
  </div>

  <!-- Modal: Power of Attorney Verification (Adika Digital) -->
  <!-- Modal: Power of Attorney Verification (Adika Digital) -->
  <!-- Modal: Power of Attorney Verification (Adika Digital) -->
  <div id="poaModal" class="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm hidden items-end justify-center">
    <div class="w-full max-w-md bg-white rounded-t-3xl max-h-[90vh] flex flex-col shadow-2xl overflow-hidden">
      <div class="px-4 py-3.5 bg-gradient-to-r from-slate-900 via-[#0e7490] to-[#16acbd] text-white flex items-center justify-between shrink-0 shadow-sm">
        <div class="flex items-center gap-2 min-w-0">
          <div class="w-8 h-8 rounded-full bg-white/15 border border-white/30 flex items-center justify-center text-base shadow-inner shrink-0">📄</div>
          <div class="min-w-0">
            <div class="font-black text-xs tracking-tight flex items-center gap-1.5 flex-wrap">
              <span>የውክልና ሰነድ ማረጋገጫ (POA Digital Verification)</span>
              <span class="px-1.5 py-0.5 bg-cyan-400/25 border border-cyan-200/50 text-[9px] text-cyan-50 rounded-full font-bold uppercase shrink-0">ADIKA</span>
            </div>
            <div class="text-[10px] text-[#b5eff3] font-medium truncate">በአዲካ ዲጂታል ሲስተም የቀረበ የውክልና ሰነድ ማጣሪያ</div>
          </div>
        </div>
        <div class="flex items-center gap-1.5 shrink-0">
          <button type="button" onclick="navigateBack('poaModal')" class="btn-back flex items-center gap-1 text-white bg-white/20 hover:bg-white/30 px-2.5 py-1.5 rounded-lg text-[11px] font-bold">
            ← ተመለስ
          </button>
          <button type="button" onclick="closeModal('poaModal')" class="btn-close w-8 h-8 rounded-full bg-slate-900/80 hover:bg-slate-900 text-white flex items-center justify-center font-bold text-sm" aria-label="Close">
            ✕
          </button>
        </div>
      </div>

      <div class="p-4 overflow-y-auto space-y-3.5 flex-1 text-xs bg-[#f8fafc]">
        <div class="p-2.5 rounded-2xl bg-white border border-[#16acbd]/25 shadow-xs flex items-start gap-2.5 text-[11px] text-slate-600">
          <span class="text-base shrink-0 mt-0.5">📱</span>
          <div class="leading-snug">የውክልና ሰነዱን ፎቶ ይጭኑ። በአዲካ ዲጂታል ሲስተም ይመረመራል። ዲጂታል ምዝገባ የሌለው የቆየ ሰነድ በአካል ቢሮ ማረጋገጥ ያስፈልጋል።</div>
        </div>

        <div class="p-3 bg-white rounded-2xl border border-slate-200 shadow-xs space-y-2">
          <label class="font-extrabold text-slate-800 text-xs flex items-center gap-1.5">
            <span>📷</span>
            <span>የውክልና ሰነዱን ፎቶ ይጭኑ</span>
          </label>
          <input id="poaImageFile" type="file" accept="image/*" capture="environment"
            class="w-full text-xs text-slate-500 file:mr-2.5 file:py-1.5 file:px-3 file:rounded-xl file:border-0 file:text-[11px] file:font-bold file:bg-[#16acbd] file:text-white hover:file:bg-[#1394a3] cursor-pointer bg-slate-50 p-1.5 rounded-xl border border-slate-200 transition-all" />
          <p class="text-[10px] text-slate-400 leading-snug">የሰነዱን ሙሉ ገጽ ወይም የማህተም ክፍል ግልጽ አድርገው ይጭኑ።</p>
        </div>

        <div id="poaScanBusy" class="hidden p-3 text-center text-[11px] text-slate-500 bg-white rounded-xl border border-slate-100">
          ⏳ በአዲካ ዲጂታል ሲስተም እየተመረመረ ነው…
        </div>
        <div id="poaResult" class="hidden font-medium"></div>
      </div>
    </div>
  </div>

  <!-- Modal: Diagnostic Sheet Analyzer -->

  <!-- Modal: Digital Cadastral Map Verifier (Adika Digital System) -->
  <div id="landMapModal" class="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm hidden items-end justify-center">
    <div class="w-full max-w-md bg-white rounded-t-3xl max-h-[92vh] flex flex-col shadow-2xl overflow-hidden">
      <div class="px-4 py-3 bg-gradient-to-r from-slate-900 via-[#0e7490] to-[#16acbd] text-white flex items-center justify-between shrink-0">
        <div class="min-w-0">
          <div class="font-black text-xs tracking-tight">🛡️ የዲጂታል ካርታ ማጣሪያ</div>
          <div class="text-[10px] text-cyan-100/90 font-medium">Adika Digital System - Cadastral Verification</div>
        </div>
        <div class="flex items-center gap-1.5 shrink-0">
          <button type="button" onclick="navigateBack('landMapModal')" class="btn-back flex items-center gap-1 text-white bg-white/20 hover:bg-white/30 px-2.5 py-1.5 rounded-lg text-[11px] font-bold">← ተመለስ</button>
          <button type="button" onclick="closeModal('landMapModal')" class="btn-close w-8 h-8 rounded-full bg-slate-900/80 hover:bg-slate-900 text-white flex items-center justify-center font-bold text-sm">✕</button>
        </div>
      </div>

      <div class="p-4 overflow-y-auto flex-1 space-y-3 text-xs">
        <div id="landMapUploadPanel" class="space-y-3">
          <label class="block cursor-pointer">
            <div class="rounded-2xl border-2 border-dashed border-[#1e73be]/50 bg-gradient-to-br from-slate-50 to-blue-50/50 p-6 text-center active:scale-[0.99] transition">
              <div class="text-3xl mb-2">📷</div>
              <div class="font-black text-slate-800 text-sm">የካርታውን ፎቶ ያስገቡ</div>
              <div class="text-[10px] text-slate-500 mt-1.5 leading-relaxed">በ Adika Digital System ይመረመራል — ወደ ኦፊሴላዊ ካዳስተር ገጽ ይወሰዳሉ</div>
            </div>
            <input id="landMapFile" type="file" accept="image/*" capture="environment" class="hidden" />
          </label>
          <div id="landMapRetryBox" class="hidden">
            <button type="button" id="landMapRetryBtn" class="w-full py-3 rounded-xl bg-[#1e73be] text-white font-bold text-xs shadow">
              📷 እባክዎን የካርታውን ፎቶ ግልጽ አድርገው እንደገና ያንሱ
            </button>
            <p class="text-[10px] text-slate-500 text-center mt-2 leading-relaxed">በ Adika Digital System ማረጋገጫ ላይ ይገኛል</p>
          </div>
        </div>

        <div id="landMapScanPanel" class="hidden space-y-3">
          <div class="relative rounded-2xl overflow-hidden bg-slate-900 aspect-[4/3]">
            <img id="landMapPreview" alt="" class="w-full h-full object-contain opacity-90" />
            <div class="absolute inset-0 pointer-events-none land-scan-laser"></div>
            <div class="absolute bottom-0 inset-x-0 bg-gradient-to-t from-slate-950/90 to-transparent p-3">
              <div class="text-[10px] text-cyan-100 font-bold leading-relaxed">⚡ Adika Digital System የሰነዱን ምስል በማንበብ እና ከማዕከላዊ ዳታቤዝ ጋር በማገናኘት ላይ ይገኛል...</div>
            </div>
          </div>
        </div>

        <div id="landMapResultPanel" class="hidden space-y-0 -mx-4 -mt-1">
          <!-- DARA-style blue agency banner -->
          <div class="bg-[#1e73be] text-white px-3 py-3 text-center">
            <div class="font-black text-[11px] leading-snug tracking-tight">አዲስ አበባ ከተማ አስተዳደር</div>
            <div class="font-bold text-[10px] leading-snug mt-0.5">የመሬት ይዞታ ምዝገባና መረጃ ኤጀንሲ</div>
            <div class="text-[9px] text-blue-100 mt-1 font-medium">Adika Digital Verification Portal</div>
          </div>

          <!-- Success badge -->
          <div class="mx-3 mt-3 mb-2 flex items-center gap-2.5 rounded-lg border border-green-200 bg-green-50 px-3 py-2.5">
            <span class="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-green-600 text-white text-sm font-black">✔</span>
            <span class="font-black text-[12px] text-[#155724]">ይህ መረጃ የተረጋገጠ ነው</span>
          </div>

          <!-- Dynamic DARA cards injected here -->
          <div id="landMapResultGrid" class="px-3 pb-3 space-y-2.5 text-[11px]"></div>

          <div class="px-3 pb-3 space-y-2">
            <p class="text-[9px] text-slate-500 leading-relaxed">ይህ መረጃ በአዲስ አበባ ከተማ አስተዳደር የመሬት ይዞታ ምዝገባና መረጃ ኤጀንሲ ማዕከላዊ ካዳስተር ዳታቤዝ መሠረት በ Adika Digital System በጥንቃቄ የተረጋገጠ ነው።</p>
            <div class="grid grid-cols-2 gap-2">
              <button type="button" id="landMapToContractBtn" class="py-2.5 rounded-lg bg-[#1e73be] text-white font-bold text-[10px] shadow-sm">📄 መረጃውን ወደ ውል አዛውር</button>
              <button type="button" id="landMapShareBtn" class="py-2.5 rounded-lg bg-slate-800 text-white font-bold text-[10px]">📤 ማረጋገጫውን አጋራ</button>
            </div>
            <button type="button" id="landMapResetBtn" class="w-full py-2 rounded-lg bg-slate-100 text-slate-700 font-bold text-[10px]">← አዲስ ማጣሪያ</button>
          </div>
        </div>
      </div>
    </div>
  </div>

  <div id="diagModal" class="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm hidden items-end justify-center">
    <div class="w-full max-w-md bg-white rounded-t-3xl max-h-[88vh] flex flex-col shadow-2xl overflow-hidden">
      <div class="px-4 py-3 bg-[#16acbd] text-white flex items-center justify-between shrink-0">
        <h3 class="font-extrabold text-xs tracking-wide">🛠️ የምርመራ ወረቀት ተንታኝ (Diagnostic Analyzer)</h3>
        <div class="flex items-center gap-1.5 shrink-0">
          <button type="button" onclick="navigateBack('diagModal')" class="btn-back flex items-center gap-1 text-white bg-white/20 hover:bg-white/30 px-2.5 py-1.5 rounded-lg text-[11px] font-bold">
            ← ተመለስ
          </button>
          <button type="button" onclick="closeModal('diagModal')" class="btn-close w-8 h-8 rounded-full bg-slate-900/80 hover:bg-slate-900 text-white flex items-center justify-center font-bold text-sm" aria-label="Close">
            ✕
          </button>
        </div>
      </div>
      <div class="p-4 overflow-y-auto space-y-3 flex-1 text-xs">
        <div>
          <label class="font-bold text-slate-700 block mb-1">የመኪናው ሞዴል</label>
          <input id="diagCarModel" type="text" value="Toyota Vitz 2018" class="w-full p-2 rounded-xl bg-slate-50 border text-xs font-bold mb-2" />
          
          <label class="font-bold text-slate-700 block mb-1">1. የምርመራ ወረቀት ፎቶ ጫን (Upload Sheet)</label>
          <input id="diagImageFile" type="file" accept="image/*" class="w-full text-xs text-slate-500 file:mr-2 file:py-1.5 file:px-3 file:rounded-xl file:border-0 file:text-xs file:font-semibold file:bg-[#16acbd] file:text-white hover:file:bg-[#1394a3] cursor-pointer mb-2 bg-slate-50 p-1.5 rounded-xl border" />
          
          <label class="font-bold text-slate-700 block mb-1">2. ወይም የጋራዥ ምርመራ ጽሑፍ አስገባ (Type Text)</label>
          <textarea id="diagInput" rows="3" placeholder="Compression 160psi, Brake pads 40%, Valve gasket leak, AC low..." class="w-full p-2.5 rounded-xl bg-slate-50 border text-xs resize-none"></textarea>
        </div>
        <button id="diagAnalyzeBtn" class="w-full py-2.5 bg-[#16acbd] text-white font-bold rounded-xl shadow active:scale-95">🔍 ተንትንና ዋጋ አስላ (Analyze Report)</button>
        <div id="diagResult" class="hidden p-3 bg-slate-50 rounded-xl border space-y-1.5 font-medium"></div>
      </div>
    </div>
  </div>

  <!-- Modal: Chassis & VIN Verification Tool -->
  <div id="chassisModal" class="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm hidden items-end justify-center">
    <div class="w-full max-w-md bg-white rounded-t-3xl max-h-[88vh] flex flex-col shadow-2xl overflow-hidden">
      <div class="px-4 py-3 bg-[#16acbd] text-white flex items-center justify-between shrink-0">
        <div class="flex items-center gap-1.5">
          <span class="text-base">🛡️</span>
          <h3 class="font-extrabold text-xs tracking-wide">
            <span class="lang-am">የሻሲ ቁጥር ማረጋገጫ (Chassis / VIN Decoder)</span>
            <span class="lang-en">Chassis & VIN Verification</span>
          </h3>
        </div>
        <div class="flex items-center gap-1.5 shrink-0">
          <button type="button" onclick="navigateBack('chassisModal')" class="btn-back flex items-center gap-1 text-white bg-white/20 hover:bg-white/30 px-2.5 py-1.5 rounded-lg text-[11px] font-bold">
            ← ተመለስ
          </button>
          <button type="button" onclick="closeModal('chassisModal')" class="btn-close w-8 h-8 rounded-full bg-slate-900/80 hover:bg-slate-900 text-white flex items-center justify-center font-bold text-sm" aria-label="Close">
            ✕
          </button>
        </div>
      </div>
      <div class="p-4 overflow-y-auto space-y-3.5 flex-1 text-xs">
        <div>
          <label class="font-bold text-slate-700 block mb-1">
            <span class="lang-am">የመኪናው 17-ዲጂት ሻሲ / VIN ቁጥር ያስገቡ</span>
            <span class="lang-en">Enter 17-Digit Chassis / VIN Number</span>
          </label>
          <div class="relative">
            <input id="chassisInput" type="text" placeholder="ለምሳሌ፡ JTDKB20U... (17 Digits)" class="w-full px-3 py-2.5 rounded-xl bg-slate-50 border border-slate-200 focus:bg-white focus:ring-2 focus:ring-[#16acbd] outline-none text-xs font-mono uppercase font-black tracking-wider text-slate-800" />
          </div>
          
          <!-- Sample Test Chips -->
          <div class="mt-2.5">
            <span class="text-[10px] font-bold text-slate-400 block mb-1">
              <span class="lang-am">ፈጣን የሙከራ ሻሲዎች (Quick Test):</span>
              <span class="lang-en">Sample VINs:</span>
            </span>
            <div class="flex gap-1.5 overflow-x-auto no-scrollbar pb-1">
              <button type="button" class="vin-sample-chip px-2.5 py-1 rounded-lg bg-slate-100 hover:bg-[#16acbd]/10 hover:text-[#0e7490] text-[10px] font-bold text-slate-600 border border-slate-200 transition-all shrink-0" data-vin="JTDKB20U00189342">Toyota Vitz (Japan)</button>
              <button type="button" class="vin-sample-chip px-2.5 py-1 rounded-lg bg-slate-100 hover:bg-[#16acbd]/10 hover:text-[#0e7490] text-[10px] font-bold text-slate-600 border border-slate-200 transition-all shrink-0" data-vin="KMHD381CBKU782910">Hyundai Tucson (Korea)</button>
              <button type="button" class="vin-sample-chip px-2.5 py-1 rounded-lg bg-slate-100 hover:bg-[#16acbd]/10 hover:text-[#0e7490] text-[10px] font-bold text-slate-600 border border-slate-200 transition-all shrink-0" data-vin="LGXC12480PA093821">BYD Song Plus (EV)</button>
              <button type="button" class="vin-sample-chip px-2.5 py-1 rounded-lg bg-slate-100 hover:bg-[#16acbd]/10 hover:text-[#0e7490] text-[10px] font-bold text-slate-600 border border-slate-200 transition-all shrink-0" data-vin="MA3FBE41S00123984">Suzuki Dzire (Auto)</button>
            </div>
          </div>
        </div>

        <button id="chassisVerifyBtn" type="button" class="w-full py-2.5 bg-[#16acbd] text-white font-bold rounded-xl shadow-md active:scale-95 flex items-center justify-center gap-1.5">
          <span>🔍 <span class="lang-am">ሻሲ አረጋግጥና ዝርዝር አውጣ</span><span class="lang-en">Verify Chassis Specs</span></span>
        </button>

        <div id="chassisResult" class="hidden font-medium"></div>
      </div>
      <div class="p-2.5 border-t border-slate-100 bg-white shrink-0">
        <button type="button" onclick="navigateBack('chassisModal')" class="w-full py-2.5 rounded-xl bg-slate-800 text-white font-bold text-xs active:scale-[0.98]">
          ← ተመለስ
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
      var wasFav = Boolean(favorites[id]);
      if (favorites[id]) delete favorites[id];
      else favorites[id] = true;
      try { localStorage.setItem('adika_favs', JSON.stringify(favorites)); } catch(e){}
      renderFavoritesUI();
      // Persist bookmark for price-drop alerts (Telegram chat_id)
      try {
        var uid = (tg && tg.initDataUnsafe && tg.initDataUnsafe.user && tg.initDataUnsafe.user.id) || 0;
        if (uid && id) {
          fetch("/api/favorites/toggle", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              user_id: uid,
              chat_id: uid,
              listing_id: id,
              action: wasFav ? "remove" : "add"
            })
          }).catch(function(){});
        }
      } catch (e) {}
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


    // ---- Feed scroll + view history (recommendations) ----
    var savedFeedScrollY = 0;
    function pushViewHistory(item) {
      try {
        var extra = item.extra_data || {};
        if (typeof extra === "string") { try { extra = JSON.parse(extra); } catch (e) { extra = {}; } }
        var bm = {};
        try { bm = extractBrandModel(item, extra) || {}; } catch (e) {}
        var priceNum = 0;
        try {
          priceNum = Number(String(item.price || "").replace(/[^0-9.]/g, "")) || 0;
        } catch (e) {}
        var entry = {
          id: item.id,
          category: item.main_category || item.category || "",
          price: priceNum,
          fuel_type: extra.fuel_type || "",
          model: bm.display || item.sub_category || extra.car_model || "",
          brand: bm.brand || ""
        };
        var hist = [];
        try { hist = JSON.parse(localStorage.getItem("viewHistory") || "[]"); } catch (e) { hist = []; }
        if (!Array.isArray(hist)) hist = [];
        hist = hist.filter(function(h) { return String(h.id) !== String(entry.id); });
        hist.unshift(entry);
        hist = hist.slice(0, 3);
        localStorage.setItem("viewHistory", JSON.stringify(hist));
        // Zero-cost intent key (last 3 categories + prices)
        try {
          var intent = hist.map(function(h) {
            return { category: h.category || "", price: h.price || 0, model: h.model || "", brand: h.brand || "" };
          });
          localStorage.setItem("adik_user_intent", JSON.stringify(intent));
        } catch (e2) {}
      } catch (e) {}
    }
    function getViewHistory() {
      try {
        var hist = JSON.parse(localStorage.getItem("viewHistory") || "[]");
        if (!Array.isArray(hist) || !hist.length) {
          hist = JSON.parse(localStorage.getItem("adik_user_intent") || "[]");
        }
        return Array.isArray(hist) ? hist : [];
      } catch (e) { return []; }
    }

    function renderRecoCards(items, intentLabel) {
      var sc = document.getElementById("modalRecoScroll");
      var title = document.getElementById("modalRecoTitle");
      var intentEl = document.getElementById("modalRecoIntent");
      if (!sc) return;
      if (intentEl) intentEl.textContent = intentLabel || "";
      if (title) {
        var isCar = true;
        try {
          isCar = !(state.selectedItem && (state.selectedItem.main_category === "ቤት" || state.selectedItem.category === "ቤት"));
        } catch (e) {}
        title.textContent = isCar ? "🤖 ለእርስዎ የተመረጡ ተቀራራቢ መኪኖች" : "🤖 ለእርስዎ የተመረጡ ተቀራራቢ ንብረቶች";
      }
      if (!items || !items.length) {
        sc.innerHTML = '<div class="text-[10px] text-slate-400 font-medium py-2">ተቀራራቢ ዝርዝር በቅርቡ...</div>';
        return;
      }
      sc.innerHTML = items.map(function(it) {
        var extra = it.extra_data || {};
        if (typeof extra === "string") { try { extra = JSON.parse(extra); } catch (e) { extra = {}; } }
        var photos = [];
        try { photos = parsePhotosList(it); } catch (e) {}
        var img = getImageUrl(photos[0] || it.photo_urls || it.listing_photos || "") || "";
        var price = formatListingPrice(it.price);
        var name = it.title || it.sub_category || it.main_category || "ንብረት";
        return (
          '<button type="button" class="reco-card shrink-0 w-[138px] text-left rounded-xl border border-slate-200 bg-white shadow-sm overflow-hidden active:scale-[0.98]" data-id="' + esc(String(it.id || "")) + '">' +
            '<div class="aspect-[4/3] bg-slate-100">' +
              (img ? '<img src="' + esc(img) + '" class="listing-photo-enhance" loading="lazy" />' : '<div class="w-full h-full flex items-center justify-center text-2xl">🚗</div>') +
            '</div>' +
            '<div class="p-1.5 space-y-0.5">' +
              '<div class="text-[10px] font-extrabold text-slate-800 truncate">' + esc(name) + '</div>' +
              '<div class="text-[9px] font-black text-[#0e7490]">💰 ' + esc(price) + '</div>' +
            '</div>' +
          '</button>'
        );
      }).join("");
      sc.querySelectorAll(".reco-card").forEach(function(btn) {
        btn.onclick = function() {
          var id = btn.getAttribute("data-id");
          var found = (items || []).find(function(x) { return String(x.id) === String(id); });
          if (found) openDetailModal(found);
          else {
            // try from current feed state.items
            var f2 = (state.items || []).find(function(x) { return String(x.id) === String(id); });
            if (f2) openDetailModal(f2);
          }
        };
      });
    }

    function loadRecommendations(item) {
      var hist = getViewHistory();
      var sc = document.getElementById("modalRecoScroll");
      var alertCard = document.getElementById("modalAlertCard");
      var alertText = document.getElementById("modalAlertText");
      if (sc) sc.innerHTML = '<div class="text-[10px] text-slate-400 py-2">⏳ በመፈለግ ላይ...</div>';
      fetch("/api/recommendations", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ viewHistory: hist, exclude_id: item && item.id })
      })
      .then(function(r) { return r.json(); })
      .then(function(data) {
        renderRecoCards(data.items || [], data.intent_label || "");
        // Smart alert card
        if (alertCard && alertText && item) {
          var extra = item.extra_data || {};
          if (typeof extra === "string") { try { extra = JSON.parse(extra); } catch (e) { extra = {}; } }
          var bm = {};
          try { bm = extractBrandModel(item, extra) || {}; } catch (e) {}
          var priceNum = Number(String(item.price || "").replace(/[^0-9.]/g, "")) || 0;
          var lo = priceNum ? Math.round(priceNum * 0.85) : 0;
          var hi = priceNum ? Math.round(priceNum * 1.15) : 0;
          var modelName = bm.display || item.sub_category || "ንብረት";
          var rangeTxt = (lo && hi) ? (lo.toLocaleString() + " – " + hi.toLocaleString() + " ETB") : modelName;
          alertText.textContent = "💡 ከ " + rangeTxt + " / " + modelName + " ጋር ተመሳሳይ አዳዲስ ንብረቶች ሲለቀቁ በቴሌግራም እንዲደርስዎ ይፈልጋሉ?";
          alertCard.classList.remove("hidden");
          alertCard.dataset.minPrice = String(lo || 0);
          alertCard.dataset.maxPrice = String(hi || 999999999);
          alertCard.dataset.model = modelName;
          alertCard.dataset.category = item.main_category || item.category || "መኪና";
        }
      })
      .catch(function() {
        renderRecoCards([], "");
      });
    }

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
        if (secs < 3600) return Math.floor(secs / 60) + "m ago";
        if (secs < 86400) return Math.floor(secs / 3600) + "h ago";
        if (secs < 86400 * 30) return Math.floor(secs / 86400) + "d ago";
        if (secs < 86400 * 365) return Math.floor(secs / (86400 * 7)) + "w ago";
        return Math.floor(secs / (86400 * 365)) + "y ago";
      } catch (e) { return ""; }
    }

    function formatListingPrice(raw) {
      if (raw == null || raw === "" || raw === "—" || raw === "Contact") return "ለዋጋ ደውሉ";
      var cleaned = String(raw).replace(/ETB/gi, "").replace(/ብር/g, "").replace(/,/g, "").trim();
      var digits = cleaned.replace(/[^\d.]/g, "");
      var n = Number(digits);
      if (!isFinite(n) || n <= 0 || n > 300000000) return "ለዋጋ ደውሉ";
      return Math.round(n).toLocaleString() + " ETB";
    }

    function extractBrandModel(item, extra) {
      extra = extra || {};
      var raw = (extra.car_model || extra.brand_model || item.sub_category || item.title || "").toString().trim();
      var brands = ["Toyota","BYD","Hyundai","Suzuki","Chery","Jetour","Nissan","Honda","Mercedes","BMW","Audi","Lexus","Kia","Mitsubishi","Isuzu","Ford","Volkswagen","VW","Mazda","Subaru","Geely","Haval","Changan"];
      var brand = extra.brand || "";
      var model = raw;
      if (!brand && raw) {
        for (var i = 0; i < brands.length; i++) {
          var b = brands[i];
          var re = new RegExp("^" + b + "\\b", "i");
          if (re.test(raw)) {
            brand = b;
            model = raw.replace(re, "").trim() || raw;
            break;
          }
        }
      }
      if (brand && model && model.toLowerCase().indexOf(brand.toLowerCase()) === 0) {
        model = model.slice(brand.length).trim();
      }
      var display = brand ? (brand + (model ? " " + model : "")) : (raw || "መኪና");
      return { brand: brand, model: model || raw, display: display };
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

    function getImageUrl(photoUrls) {
      if (!photoUrls) return "";
      if (Array.isArray(photoUrls)) {
        var first = photoUrls[0];
        if (!first) return "";
        if (typeof first === "string") return first;
        if (first && typeof first === "object") {
          return first.url || first.src || first.photo_url || first.photo_id || "";
        }
        return String(first);
      }
      if (typeof photoUrls === "string") {
        var s = photoUrls.trim();
        if (!s) return "";
        if (s.charAt(0) === "[") {
          try {
            var parsed = JSON.parse(s);
            return getImageUrl(parsed);
          } catch (e) {
            return s;
          }
        }
        return s;
      }
      if (typeof photoUrls === "object") {
        return photoUrls.url || photoUrls.src || photoUrls.photo_url || photoUrls.photo_id || "";
      }
      return "";
    }

    function parsePhotosList(item) {
      if (!item) return [];
      var candidates = [
        item.photos,
        item.photo_urls,
        item.listing_photos,
        item.photo_url,
        item.image_url,
        item.photo_id
      ];
      var out = [];
      for (var i = 0; i < candidates.length; i++) {
        var raw = candidates[i];
        if (raw == null || raw === "") continue;
        if (Array.isArray(raw)) {
          for (var j = 0; j < raw.length; j++) {
            var u = getImageUrl(raw[j]);
            if (u) out.push(u);
          }
        } else if (typeof raw === "string") {
          var s = raw.trim();
          if (s.charAt(0) === "[") {
            try {
              var arr = JSON.parse(s);
              if (Array.isArray(arr)) {
                for (var k = 0; k < arr.length; k++) {
                  var u2 = getImageUrl(arr[k]);
                  if (u2) out.push(u2);
                }
              }
            } catch (e) {
              if (s) out.push(s);
            }
          } else if (s) {
            out.push(s);
          }
        } else {
          var u3 = getImageUrl(raw);
          if (u3) out.push(u3);
        }
      }
      var seen = {};
      var uniq = [];
      for (var x = 0; x < out.length; x++) {
        if (!seen[out[x]]) { seen[out[x]] = 1; uniq.push(out[x]); }
      }
      return uniq;
    }

    function createCardElement(item) {
      var photos = parsePhotosList(item);
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
        var bm = extractBrandModel(item, extra);
        cardTitleAm = bm.display || "መኪና";
        cardTitleEn = bm.display || "Vehicle";
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
        media = '<div class="listing-photo-frame">' +
          '<img src="' + esc(getImageUrl(photos[0]) || photos[0] || "") + '" alt="" class="listing-photo-enhance" loading="lazy" onerror="this.style.display=\'none\'" />' +
          '</div>';
      } else {
        media = '<div class="listing-photo-frame flex flex-col items-center justify-center bg-gradient-to-br from-[#16acbd] to-[#0e7490] text-white p-2">' +
          '<span class="text-3xl mb-1 relative z-10">' + icon + '</span>' +
          '<span class="text-[9px] font-bold text-white/90 relative z-10">No Image</span>' +
          '</div>';
      }

      var priceLabel = formatListingPrice(item.price);
      var views = item.view_count || item.views_count || 0;
      var isFav = Boolean(favorites[item.id]);
      var timeLabel = relativeTime(item.created_at);
      var hasChassis = Boolean(extra.chassis_number || item.chassis_number || extra.has_chassis || (item.description && (item.description.indexOf("Chassis") >= 0 || item.description.indexOf("ሻሲ") >= 0)));

      var card = document.createElement("div");
      card.className = "adika-card cursor-pointer";
      card.innerHTML =
        '<div class="relative w-full aspect-[4/3] bg-slate-100 overflow-hidden">' +
          '<div class="absolute top-2 left-2 z-10 w-2.5 h-2.5 bg-emerald-500 rounded-full animate-pulse shadow-[0_0_8px_rgba(16,185,129,0.8)]"></div>' +
          (hasChassis ? '<span class="absolute top-2 right-2 z-10 bg-emerald-700/90 text-white backdrop-blur-sm px-1.5 py-0.5 rounded text-[8px] font-black flex items-center gap-0.5 shadow-sm"><span>🛡️</span><span>ሻሲ ✓</span></span>' : '') +
          media +
          (views ? '<span class="absolute bottom-1.5 left-1.5 z-10 bg-black/60 backdrop-blur-sm px-1.5 py-0.5 rounded text-[8px] text-white font-bold">👁️ ' + esc(views) + '</span>' : '') +
        '</div>' +
        '<div class="px-2 py-1.5 flex flex-col gap-1">' +
          /* Top row: Brand-Model left | time right */
          '<div class="flex items-center justify-between gap-1.5 min-w-0">' +
            '<div class="font-extrabold text-[11px] text-slate-800 truncate min-w-0 flex items-center gap-0.5">' +
              '<span class="truncate lang-am">' + esc(cardTitleAm) + '</span>' +
              '<span class="truncate lang-en">' + esc(cardTitleEn) + '</span>' +
              '<span class="text-emerald-600 text-[10px] shrink-0">✓</span>' +
            '</div>' +
            (timeLabel ? '<span class="text-[9px] text-slate-400 font-medium whitespace-nowrap shrink-0">' + esc(timeLabel) + '</span>' : '') +
          '</div>' +
          /* Bottom row: Price left | heart right */
          '<div class="flex items-center justify-between gap-1.5 min-w-0">' +
            '<div class="inline-block px-1.5 py-0.5 rounded bg-[#16acbd]/10 text-[#0e7490] font-black text-[10px] truncate max-w-[85%]">💰 ' + esc(priceLabel) + '</div>' +
            '<button type="button" class="card-fav-btn text-sm p-0.5 transition-transform active:scale-75 shrink-0 leading-none" data-id="' + esc(item.id) + '">' +
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
      try { savedFeedScrollY = window.scrollY || window.pageYOffset || 0; } catch (e) { savedFeedScrollY = 0; }
      state.selectedItem = item;
      pushViewHistory(item);
      var extra = item.extra_data || {};
      if (typeof extra === "string") {
        try { extra = JSON.parse(extra); } catch (e) { extra = {}; }
      }
      var photos = parsePhotosList(item);
      var isCar = (item.main_category === "መኪና" || item.category === "መኪና");

      var modalTitleText = "";
      if (isCar) {
        var bm = extractBrandModel(item, extra);
        modalTitleText = bm.display || "መኪና";
        modalCategoryBadge.textContent = bm.brand || "መኪና";
      } else {
        modalTitleText = item.sub_category || extra.house_type || "ቤት";
        modalCategoryBadge.textContent = "ቤት";
      }
      modalIdBadge.textContent = "#ADK-" + (item.id || "001");
      modalTitle.textContent = modalTitleText;

      var isSell = String(item.req_type || item.action_type || "").toUpperCase().indexOf("SELL") >= 0 || String(item.action_type || "") === "መሸጥ";
      var priceTxt = formatListingPrice(item.price);
      modalPrice.textContent = priceTxt;
      modalTime.textContent = relativeTime(item.created_at) ? ("⏱️ " + relativeTime(item.created_at)) : "";
      modalDesc.textContent = item.description || "No further details provided.";

      // Image gallery carousel
      if (photos.length > 0) {
        var slides = photos.map(function(u, i) {
          return '<div class="modal-slide shrink-0 w-full h-full snap-center"><img src="' + esc(getImageUrl(u) || u || "") + '" alt="" class="listing-photo-enhance" loading="' + (i === 0 ? "eager" : "lazy") + '" /></div>';
        }).join("");
        var dots = photos.length > 1 ? ('<div class="absolute bottom-2 left-0 right-0 flex justify-center gap-1.5 z-10">' +
          photos.map(function(_, i) {
            return '<button type="button" class="modal-dot w-1.5 h-1.5 rounded-full ' + (i === 0 ? "bg-white" : "bg-white/50") + '" data-idx="' + i + '"></button>';
          }).join("") + '</div>') : "";
        modalMediaContainer.innerHTML =
          '<div id="modalGalleryTrack" class="flex w-full h-full overflow-x-auto snap-x snap-mandatory no-scrollbar">' + slides + '</div>' + dots;
        var track = document.getElementById("modalGalleryTrack");
        if (track && photos.length > 1) {
          track.onscroll = function() {
            var idx = Math.round(track.scrollLeft / Math.max(track.clientWidth, 1));
            var ds = modalMediaContainer.querySelectorAll(".modal-dot");
            ds.forEach(function(d, i) {
              d.className = "modal-dot w-1.5 h-1.5 rounded-full " + (i === idx ? "bg-white" : "bg-white/50");
            });
          };
          modalMediaContainer.querySelectorAll(".modal-dot").forEach(function(d) {
            d.onclick = function(e) {
              e.stopPropagation();
              var i = Number(d.getAttribute("data-idx") || 0);
              track.scrollTo({ left: i * track.clientWidth, behavior: "smooth" });
            };
          });
        }
      } else {
        modalMediaContainer.innerHTML =
          '<div class="w-full h-full flex flex-col items-center justify-center bg-gradient-to-br from-[#16acbd] to-[#0e7490] text-white">' +
            '<span class="text-4xl mb-1">' + (isCar ? '🚗' : '🏠') + '</span>' +
            '<span class="text-xs font-bold">No Image Available</span>' +
          '</div>';
      }

      var specsHtml = "";
      if (isCar) {
        if (extra.chassis_number) specsHtml += '<div class="col-span-2">🛡️ VIN: <span class="font-mono font-bold text-emerald-700">' + esc(extra.chassis_number) + ' (Verified ✓)</span></div>';
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

      // Populate dynamic category action buttons
      var actionsRow = document.getElementById("modalActionButtonsRow");
      if (actionsRow) {
        actionsRow.className = "flex gap-1.5 overflow-x-auto no-scrollbar pb-0.5";
        var chip = function(id, icon, label) {
          return '<button id="' + id + '" type="button" class="shrink-0 px-2.5 py-1.5 rounded-full bg-slate-50 border border-slate-200 text-[#0e7490] font-bold text-[10px] flex items-center gap-1 active:scale-95 whitespace-nowrap">' +
            '<span>' + icon + '</span><span>' + label + '</span></button>';
        };
        if (isCar) {
          actionsRow.innerHTML = chip("actCarDuty","🧮","የቀረጥ ስሌት") + chip("actCarCompare","⚖️","ንጽጽር") + chip("actCarDiag","🛠️","ምርመራ");
          document.getElementById("actCarDuty").onclick = function() {
            openToolModal('dutyModal');
            if (extra.cif_price) document.getElementById("dutyCif").value = extra.cif_price;
          };
          document.getElementById("actCarCompare").onclick = function() {
            openToolModal('compareModal');
            var c1 = document.getElementById("compareCar1");
            if (c1) c1.value = modalTitleText;
          };
          document.getElementById("actCarDiag").onclick = function() { openToolModal('diagModal'); };
        } else {
          actionsRow.innerHTML = chip("actPropLoan","🏦","የባንክ ብድር") + chip("actPropPoa","🔍","ውክልና") + chip("actPropContract","📜","ውል");
          document.getElementById("actPropLoan").onclick = function() { openToolModal('loanModal'); };
          document.getElementById("actPropPoa").onclick = function() { openToolModal('poaModal'); };
          document.getElementById("actPropContract").onclick = function() {
            openToolModal('contractModal');
            var rawPrice = parseInt(String(item.price || "").replace(/[^0-9]/g, "")) || "";
            var cp = document.getElementById("contractPrice");
            if (cp) cp.value = rawPrice;
          };
        }
      }

      if (item.id) {
        try { fetch("/api/views/" + item.id, { method: "POST" }).catch(function(){}); } catch(e){}
      }
      loadRecommendations(item);
    }

    function closeDetailModalPreserve() {
      modalOverlay.classList.add("hidden");
      modalOverlay.classList.remove("flex");
      state.selectedItem = null;
      try {
        window.scrollTo({ top: savedFeedScrollY || 0, behavior: "instant" in window ? "instant" : "auto" });
      } catch (e) {
        try { window.scrollTo(0, savedFeedScrollY || 0); } catch (e2) {}
      }
    }
    modalClose.onclick = closeDetailModalPreserve;
    var modalBackBtn = document.getElementById("modalBackBtn");
    if (modalBackBtn) {
      modalBackBtn.onclick = function() { closeDetailModalPreserve(); };
    };

    (function bindSmartAlert() {
      var btn = document.getElementById("modalAlertBtn");
      if (!btn) return;
      btn.onclick = function() {
        var card = document.getElementById("modalAlertCard");
        var status = document.getElementById("modalAlertStatus");
        var userId = (tg && tg.initDataUnsafe && tg.initDataUnsafe.user && tg.initDataUnsafe.user.id) || 0;
        var payload = {
          user_id: userId,
          chat_id: userId,
          target_category: (card && card.dataset.category) || "መኪና",
          min_price: (card && card.dataset.minPrice) || "0",
          max_price: (card && card.dataset.maxPrice) || "999999999",
          model: (card && card.dataset.model) || "",
          telegram_user: (tg && tg.initDataUnsafe && tg.initDataUnsafe.user) || {}
        };
        btn.disabled = true;
        btn.textContent = "⏳ በመመዝገብ ላይ...";
        fetch("/api/save-alert", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        })
        .then(function(r) { return r.json(); })
        .then(function(res) {
          btn.disabled = false;
          btn.textContent = "🔔 አዎ! በቴሌግራም አሳውቀኝ (Subscribe to Alerts)";
          if (status) {
            status.classList.remove("hidden");
            status.textContent = res.message || (res.success ? "✅ ተመዝግቧል!" : "❌ አልተሳካም");
            status.className = "text-[10px] font-bold " + (res.success ? "text-emerald-700" : "text-rose-600");
          }
          if (res.success && tg && tg.showAlert) {
            try { tg.showAlert(res.message || "ተመዝግቧል!"); } catch (e) {}
          }
        })
        .catch(function() {
          btn.disabled = false;
          btn.textContent = "🔔 አዎ! በቴሌግራም አሳውቀኝ (Subscribe to Alerts)";
          if (status) {
            status.classList.remove("hidden");
            status.textContent = "የኔትወርክ ስህተት";
            status.className = "text-[10px] font-bold text-rose-600";
          }
        });
      };
    })();
    modalOverlay.onclick = function (e) {
      if (e.target === modalOverlay) closeDetailModalPreserve();
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
          statusEl.innerHTML =
            '<div class="py-12 px-4 text-center">' +
              '<div class="text-4xl mb-2">📭</div>' +
              '<div class="text-slate-700 font-bold text-sm mb-1">' +
                '<span class="lang-am">ምንም አይነት ማስታወቂያ አልተገኘም</span>' +
                '<span class="lang-en">No listings found</span>' +
              '</div>' +
              '<p class="text-slate-500 text-xs">' +
                '<span class="lang-am">እባክዎ ሌላ ምድብ ወይም የፍለጋ ቃል ይሞክሩ</span>' +
                '<span class="lang-en">Please try a different category or search term</span>' +
              '</p>' +
            '</div>';
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
        statusEl.style.display = "none";
        var sk = "";
        for (var si = 0; si < 6; si++) {
          sk += '<div class="adika-card animate-pulse">' +
            '<div class="w-full aspect-[4/3] bg-slate-200"></div>' +
            '<div class="p-2 space-y-2">' +
              '<div class="h-3 bg-slate-200 rounded w-4/5"></div>' +
              '<div class="h-3 bg-slate-200 rounded w-2/5"></div>' +
              '<div class="h-2 bg-slate-100 rounded w-3/5"></div>' +
            '</div></div>';
        }
        grid.innerHTML = sk;
      }

      var page = append ? state.page + 1 : 1;
      var qs = "page=" + page + "&limit=12&order=DESC&active_only=1&type=" +
        (state.tab === "marketplace" ? "SELL" : "BUY");
      if (state.category) qs += "&category=" + encodeURIComponent(state.category);
      if (state.q) qs += "&q=" + encodeURIComponent(state.q);
      if (state.chassisOnly) qs += "&chassis_only=1";

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

    function selectCategory(catId) {
      state.category = (!catId || catId === "all" || catId === "null" || catId === "undefined" || catId === "✨ ሁሉም" || catId === "✨ All" || catId === "ሁሉም") ? "" : catId;
      var buttons = catsEl.querySelectorAll("button");
      buttons.forEach(function(b) {
        var bId = b.getAttribute("data-id") || "";
        if ((!state.category && (!bId || bId === "all")) || (state.category && bId === state.category)) {
          b.className = "cat-pill px-3 py-1 rounded-full text-xs font-bold whitespace-nowrap transition-all bg-white text-[#16acbd] shadow-sm";
        } else {
          b.className = "cat-pill px-3 py-1 rounded-full text-xs font-bold whitespace-nowrap transition-all bg-white/20 text-white hover:bg-white/30";
        }
      });
      load(false);
    }

    catsEl.onclick = function (ev) {
      var btn = ev.target.closest("button");
      if (!btn || !catsEl.contains(btn)) return;
      if (btn.id === "filterChassisChip") {
        state.chassisOnly = !state.chassisOnly;
        if (state.chassisOnly) {
          btn.className = "cat-pill px-3 py-1 rounded-full text-xs font-bold whitespace-nowrap transition-all bg-emerald-400 text-slate-900 shadow-md ring-2 ring-emerald-200";
          filterText.textContent = "🛡️ ሻሲ ያላቸው ብቻ (VIN Verified Only)";
          filterBanner.classList.remove("hidden");
        } else {
          btn.className = "cat-pill px-3 py-1 rounded-full text-xs font-bold whitespace-nowrap transition-all bg-emerald-500/25 text-white hover:bg-emerald-500/35 border border-emerald-300/40";
          filterBanner.classList.add("hidden");
        }
        load(false);
        return;
      }
      var catId = btn.getAttribute("data-id") || "";
      selectCategory(catId);
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

    // AI Smart Filter & AI Tools Hub Handlers
    var aiToolsView = document.getElementById("aiToolsView");
    var aiSearchView = document.getElementById("aiSearchView");
    var aiTabTools = document.getElementById("aiTabTools");
    var aiTabSearch = document.getElementById("aiTabSearch");

    aiTabTools.onclick = function() {
      aiToolsView.classList.remove("hidden");
      aiSearchView.classList.add("hidden");
      aiTabTools.className = "py-1 rounded-lg bg-white text-[#16acbd] shadow-sm transition-all text-center";
      aiTabSearch.className = "py-1 rounded-lg text-white/80 hover:text-white transition-all text-center";
    };

    aiTabSearch.onclick = function() {
      aiSearchView.classList.remove("hidden");
      aiToolsView.classList.add("hidden");
      aiTabSearch.className = "py-1 rounded-lg bg-white text-[#16acbd] shadow-sm transition-all text-center";
      aiTabTools.className = "py-1 rounded-lg text-white/80 hover:text-white transition-all text-center";
    };


    function adikaAdvisorCtaHtml(carModel, summary) {
      var model = (carModel || "መኪናዎ").toString().trim() || "መኪናዎ";
      var sum = (summary || "").toString().trim();
      return (
        '<div class="mt-3 p-3 rounded-2xl border border-teal-200 bg-gradient-to-r from-teal-50 via-cyan-50 to-sky-50 shadow-sm space-y-2">' +
          '<div class="flex items-start gap-2">' +
            '<span class="text-lg shrink-0">🤖</span>' +
            '<p class="text-[11px] text-slate-700 leading-relaxed font-medium">' +
              'ስለ <span class="font-black text-[#0e7490]">' + esc(model) + '</span> ተጨማሪ መረጃ ወይም የባለሙያ ምክር ይፈልጋሉ? ' +
              '<span class="font-bold">Adika Digital Adviser</span>ን ያነጋግሩ!' +
            '</p>' +
          '</div>' +
          '<button type="button" class="adika-advisor-cta-btn w-full text-center py-2.5 rounded-xl bg-[#16acbd] hover:bg-[#1394a3] text-white font-bold text-[11px] shadow-md active:scale-[0.98]" ' +
            'data-car="' + esc(model).replace(/"/g, '&quot;') + '" data-summary="' + esc(sum).replace(/"/g, '&quot;') + '">' +
            '💬 አሁኑኑ አማክር (Chat Now)' +
          '</button>' +
        '</div>'
      );
    }

    window.openAdviserChat = function(carModelName, diagnosticSummary) {
      var model = (carModelName || "መኪና").toString().trim() || "መኪና";
      var summary = (diagnosticSummary || "").toString().trim();
      // Close any open tool modals first
      ["dutyModal","loanModal","compareModal","contractModal","poaModal","diagModal","chassisModal","landMapModal","aiModal"].forEach(function(mid) {
        try { closeToolModal(mid); } catch (e) {}
      });
      showAnalysisView(true);
      var prompt = "ሰላም፣ ስለ " + model + " የምርመራ ውጤት ምክር እፈልጋለሁ።";
      if (summary) prompt += "\n\nማጠቃለያ:\n" + summary;
      else prompt += " Hello, I need advice regarding the diagnostic results for " + model + ".";
      var input = document.getElementById("advisorChatInput");
      if (input) {
        input.value = prompt;
        try {
          input.style.height = "auto";
          input.style.height = Math.min(input.scrollHeight, 120) + "px";
        } catch (e) {}
        input.focus();
      }
      // Ensure chat log has a welcome if empty
      var log = document.getElementById("advisorChatLog");
      if (log && !log.children.length) {
        appendAdvisorChat("advisor", "ሰላም! እኔ Adika Senior Financial Advisor ነኝ። ስለ " + model + " ጥያቄዎን ይላኩ — ወይም ከታች ያለውን ቅድመ-ጥያቄ ይላኩ።");
      }
    };

    // Delegate clicks on Advisor CTA buttons (works for dynamically injected HTML)
    document.addEventListener("click", function(ev) {
      var btn = ev.target && ev.target.closest ? ev.target.closest(".adika-advisor-cta-btn") : null;
      if (!btn) return;
      ev.preventDefault();
      openAdviserChat(btn.getAttribute("data-car") || "", btn.getAttribute("data-summary") || "");
    });

    window.openToolModal = function(id) {
      var m = document.getElementById(id);
      if (m) {
        m.classList.remove("hidden");
        m.classList.add("flex");
      }
    };

    window.closeToolModal = function(id) {
      var m = document.getElementById(id);
      if (m) {
        m.classList.add("hidden");
        m.classList.remove("flex");
      }
      // restore main feed scroll when no tool modal is open
      var anyOpen = false;
      ["dutyModal","loanModal","compareModal","contractModal","poaModal","diagModal","chassisModal","landMapModal","aiModal"].forEach(function(mid) {
        var el = document.getElementById(mid);
        if (el && !el.classList.contains("hidden")) anyOpen = true;
      });
      var av = document.getElementById("analysisView");
      if (av && !av.classList.contains("hidden")) anyOpen = true;
      if (!anyOpen) document.body.style.overflow = "";
    };
    window.closeModal = function(id) {
      if (id) closeToolModal(id);
      else {
        ["dutyModal","loanModal","compareModal","contractModal","poaModal","diagModal","chassisModal","landMapModal","aiModal"].forEach(function(mid) {
          closeToolModal(mid);
        });
        showAnalysisView(false);
      }
    };
    window.navigateBack = function(id) {
      // Same as close — returns user to main listing feed
      if (id === "analysisView") showAnalysisView(false);
      else closeModal(id);
    };
    // Overlay click closes tool modals (no page refresh)
    ["dutyModal","loanModal","compareModal","contractModal","poaModal","diagModal","chassisModal","landMapModal"].forEach(function(mid) {
      var el = document.getElementById(mid);
      if (!el) return;
      el.addEventListener("click", function(e) {
        if (e.target === el) closeToolModal(mid);
      });
    });

    // Tool Launchers
    document.getElementById("toolDutyBtn").onclick = function() { aiModalClose.onclick(); openToolModal("dutyModal"); };
    document.getElementById("toolLoanBtn").onclick = function() { aiModalClose.onclick(); openToolModal("loanModal"); };
    document.getElementById("toolCompareBtn").onclick = function() { aiModalClose.onclick(); openToolModal("compareModal"); };
    document.getElementById("toolContractBtn").onclick = function() { aiModalClose.onclick(); openToolModal("contractModal"); };
    document.getElementById("toolPoaBtn").onclick = function() { aiModalClose.onclick(); openToolModal("poaModal"); };
    document.getElementById("toolDiagBtn").onclick = function() { aiModalClose.onclick(); openToolModal("diagModal"); };
    if (document.getElementById("toolChassisBtn")) {
      document.getElementById("toolChassisBtn").onclick = function() { aiModalClose.onclick(); openToolModal("chassisModal"); };
      var _lmBtn = document.getElementById("toolLandMapBtn");
      if (_lmBtn) _lmBtn.onclick = function() { try { aiModalClose.onclick(); } catch(e){} openToolModal("landMapModal"); };
    }

    // AI Smart Financial Advisor Interactive Controls
    var selectedPurpose = "business";
    var selectedPay = "cash";

    var budgetInputEl = document.getElementById("advisorBudget");
    var budgetFormattedEl = document.getElementById("advisorBudgetFormatted");

    if (budgetInputEl && budgetFormattedEl) {
      budgetInputEl.oninput = function() {
        var v = Number(budgetInputEl.value) || 0;
        budgetFormattedEl.textContent = v > 0 ? (v.toLocaleString() + " ETB") : "0 ETB";
      };
    }
    var incomeInputEl = document.getElementById("advisorMonthlyIncome");
    var incomeFormattedEl = document.getElementById("advisorIncomeFormatted");
    if (incomeInputEl && incomeFormattedEl) {
      incomeInputEl.oninput = function() {
        var v = Number(incomeInputEl.value) || 0;
        incomeFormattedEl.textContent = v > 0 ? (v.toLocaleString() + " / ወር") : "0 / ወር";
      };
    }

    document.querySelectorAll(".advisor-preset-chip").forEach(function(btn) {
      btn.onclick = function() {
        var b = btn.getAttribute("data-budget");
        if (budgetInputEl) {
          budgetInputEl.value = b;
          if (budgetFormattedEl) budgetFormattedEl.textContent = Number(b).toLocaleString() + " ETB";
        }
      };
    });

    var purposeBizBtn = document.getElementById("advisorPurposeBiz");
    var purposeFamBtn = document.getElementById("advisorPurposeFam");
    if (purposeBizBtn && purposeFamBtn) {
      purposeBizBtn.onclick = function() {
        selectedPurpose = "business";
        purposeBizBtn.className = "advisor-purpose-btn py-1.5 px-2 rounded-lg bg-[#16acbd] text-white font-bold text-[10px] text-center transition-all shadow-sm flex items-center justify-center gap-1";
        purposeFamBtn.className = "advisor-purpose-btn py-1.5 px-2 rounded-lg text-slate-600 font-bold text-[10px] text-center hover:bg-slate-100 transition-all flex items-center justify-center gap-1";
      };
      purposeFamBtn.onclick = function() {
        selectedPurpose = "personal";
        purposeFamBtn.className = "advisor-purpose-btn py-1.5 px-2 rounded-lg bg-[#16acbd] text-white font-bold text-[10px] text-center transition-all shadow-sm flex items-center justify-center gap-1";
        purposeBizBtn.className = "advisor-purpose-btn py-1.5 px-2 rounded-lg text-slate-600 font-bold text-[10px] text-center hover:bg-slate-100 transition-all flex items-center justify-center gap-1";
      };
    }

    var payCashBtn = document.getElementById("advisorPayCash");
    var payLoanBtn = document.getElementById("advisorPayLoan");
    var incomeRow = document.getElementById("advisorIncomeRow");
    if (payCashBtn && payLoanBtn) {
      payCashBtn.onclick = function() {
        selectedPay = "cash";
        payCashBtn.className = "advisor-pay-btn py-1.5 px-2 rounded-lg bg-[#16acbd] text-white font-bold text-[10px] text-center transition-all shadow-sm flex items-center justify-center gap-1";
        payLoanBtn.className = "advisor-pay-btn py-1.5 px-2 rounded-lg text-slate-600 font-bold text-[10px] text-center hover:bg-slate-100 transition-all flex items-center justify-center gap-1";
        if (incomeRow) incomeRow.classList.add("hidden");
      };
      payLoanBtn.onclick = function() {
        selectedPay = "loan";
        payLoanBtn.className = "advisor-pay-btn py-1.5 px-2 rounded-lg bg-[#16acbd] text-white font-bold text-[10px] text-center transition-all shadow-sm flex items-center justify-center gap-1";
        payCashBtn.className = "advisor-pay-btn py-1.5 px-2 rounded-lg text-slate-600 font-bold text-[10px] text-center hover:bg-slate-100 transition-all flex items-center justify-center gap-1";
        if (incomeRow) incomeRow.classList.remove("hidden");
      };
    }


    // Home hero CTAs
    (function(){
      var ha = document.getElementById("heroAdvisorBtn");
      var hp = document.getElementById("heroPoaBtn");
      var ht = document.getElementById("heroToolsBtn");
      if (ha) ha.onclick = function() {
        if (typeof openToolModal === "function") openToolModal("aiModal");
        else {
          var m = document.getElementById("aiModal");
          if (m) { m.classList.remove("hidden"); m.classList.add("flex"); }
        }
      };
      if (hp) hp.onclick = function() {
        if (typeof openToolModal === "function") openToolModal("poaModal");
        else {
          var m = document.getElementById("poaModal");
          if (m) { m.classList.remove("hidden"); m.classList.add("flex"); }
        }
      };
      if (ht) ht.onclick = function() {
        if (typeof openToolModal === "function") openToolModal("aiModal");
        else {
          var m = document.getElementById("aiModal");
          if (m) { m.classList.remove("hidden"); m.classList.add("flex"); }
        }
      };
      // Carousel dots sync
      var car = document.getElementById("heroCarousel");
      var dots = document.querySelectorAll("#heroDots .hero-dot");
      if (car && dots.length) {
        car.addEventListener("scroll", function() {
          var i = Math.round(car.scrollLeft / Math.max(car.clientWidth * 0.78, 1));
          dots.forEach(function(d, idx){ d.classList.toggle("active", idx === i); });
        }, { passive: true });
      }
    })();

    function showAnalysisView(show) {
      var v = document.getElementById("analysisView");
      if (!v) return;
      if (show) {
        v.classList.remove("hidden");
        v.classList.add("flex");
        document.body.style.overflow = "hidden";
      } else {
        v.classList.add("hidden");
        v.classList.remove("flex");
        document.body.style.overflow = "";
      }
    }
    var analysisBackBtn = document.getElementById("analysisBackBtn");
    if (analysisBackBtn) analysisBackBtn.onclick = function() { showAnalysisView(false); };

    var advisorChatHistory = [];

    function appendAdvisorChat(role, text) {
      var log = document.getElementById("advisorChatLog");
      if (!log) return;
      var row = document.createElement("div");
      if (role === "user") {
        row.className = "chat-bubble-user text-right";
        row.innerHTML = '<div class="text-[9px] font-bold text-white/80 mb-0.5">እርስዎ</div><div class="text-xs font-semibold whitespace-pre-wrap leading-relaxed text-left">' + esc(String(text || "")) + '</div>';
      } else {
        row.className = "chat-bubble-ai text-left";
        row.innerHTML = '<div class="text-[9px] font-black text-teal-700 mb-0.5 flex items-center gap-1"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2l2.4 7.2H22l-6 4.8 2.4 7.2L12 16.4 5.6 21.2 8 14 2 9.2h7.6z"/></svg><span>Adika Senior Financial Advisor</span></div><div class="text-xs text-slate-700 whitespace-pre-wrap leading-relaxed">' + esc(String(text || "")) + '</div>';
      }
      log.appendChild(row);
      setTimeout(function() { log.scrollTop = log.scrollHeight; }, 50);
    }

    function renderBudgetBar(budget) {
      var b = Math.max(0, Number(budget) || 0);
      var purchase = Math.round(b * 0.70);
      var fees = Math.round(b * 0.15);
      var reserve = Math.max(0, b - purchase - fees);
      var el = document.getElementById("analysisBudgetTotal");
      if (el) el.textContent = b.toLocaleString() + " ETB";
      var set = function(id, text) { var n = document.getElementById(id); if (n) n.textContent = text; };
      set("pctPurchase", "70% · " + purchase.toLocaleString() + " ብር");
      set("pctFees", "15% · " + fees.toLocaleString() + " ብር");
      set("pctReserve", "15% · " + reserve.toLocaleString() + " ብር");
      var bp = document.getElementById("barPurchase");
      var bf = document.getElementById("barFees");
      var br = document.getElementById("barReserve");
      if (bp) bp.style.width = "70%";
      if (bf) bf.style.width = "15%";
      if (br) br.style.width = "15%";
      return { budget: b, purchase: purchase, fees: fees, reserve: reserve };
    }

    function renderAnalysisDashboard(d, budget) {
      showAnalysisView(true);
      var log = document.getElementById("advisorChatLog");
      if (log && !log.dataset.seeded) {
        log.innerHTML = "";
        advisorChatHistory = [];
        var initMsg = "ሰላም! እኔ የ Adika Senior Financial Advisor ነኝ። ስለ መኪና ወይም የቤት ግዢ፣ የቀረጥ ስሌት፣ የባንክ ብድር ወይም ማንኛውም የፋይናንስ ምክር ምን ማወቅ ይፈልጋሉ? ጥያቄዎን እዚህ ይጠይቁኝ።";
        appendAdvisorChat("advisor", initMsg);
        advisorChatHistory.push({ role: "advisor", content: initMsg });
        log.dataset.seeded = "1";
      }
    }


    // Advisor Button Action — render 3 investment opportunity cards (no direct jump to chat)
    function formatEtb(n) {
      n = Math.max(0, Number(n) || 0);
      return n.toLocaleString() + " ብር";
    }
    function renderOpportunityCards() {
      var budgetEl = document.getElementById("advisorBudget");
      var incomeEl = document.getElementById("advisorMonthlyIncome");
      var budget = Math.max(0, Number(budgetEl && budgetEl.value) || 0);
      var income = Math.max(0, Number(incomeEl && incomeEl.value) || 0);
      var autoBody = document.getElementById("oppAutoBody");
      var propBody = document.getElementById("oppPropBody");
      var roiBody = document.getElementById("oppRoiBody");
      var box = document.getElementById("opportunityCards");
      if (box) box.classList.remove("hidden");
      if (autoBody) autoBody.innerHTML = "ከአዲካ ገበያ እየተጫነ…";
      if (propBody) propBody.innerHTML = "ከአዲካ ገበያ እየተጫነ…";
      if (roiBody) roiBody.innerHTML = "እየተሰላ…";

      // Ethiopian commercial bank defaults
      var DOWN_PCT = 0.30;
      var APR = 0.18;
      var AUTO_YEARS = 5;
      var MORTGAGE_YEARS = 15;

      function parsePrice(v) {
        if (v == null) return 0;
        var n = Number(String(v).replace(/[^\d.]/g, ""));
        return isFinite(n) ? n : 0;
      }
      function fmt(n) {
        n = Math.round(Number(n) || 0);
        return n.toLocaleString() + " ብር";
      }
      // Standard amortization: M = P * r(1+r)^n / ((1+r)^n - 1)
      function monthlyPayment(principal, annualRate, years) {
        if (principal <= 0) return 0;
        var r = annualRate / 12;
        var n = years * 12;
        if (r === 0) return principal / n;
        var factor = Math.pow(1 + r, n);
        return principal * (r * factor) / (factor - 1);
      }
      function titleOf(it) {
        var extra = it.extra_data || {};
        if (typeof extra === "string") {
          try { extra = JSON.parse(extra); } catch (e) { extra = {}; }
        }
        return extra.car_model || it.sub_category || extra.house_type || it.main_category || ("#ADK-" + (it.id || ""));
      }
      function isCar(it) {
        var c = String(it.main_category || it.category || "");
        return c === "መኪና" || /car|vehicle/i.test(c);
      }
      function isHouse(it) {
        var c = String(it.main_category || it.category || "");
        return c === "ቤት" || c === "house" || /ቤት|property|house|land|መሬት/i.test(c);
      }

      // Fetch live SELL listings (real Adika DB via existing API)
      fetch("/api/explorer/listings?page=1&limit=40&order=DESC&active_only=1&type=SELL")
        .then(function(r){ return r.json(); })
        .then(function(data){
          var items = data.items || data.listings || [];
          var cars = [];
          var props = [];
          for (var i = 0; i < items.length; i++) {
            var it = items[i];
            var price = parsePrice(it.price);
            if (price <= 0) continue;
            if (isCar(it) && price <= budget) cars.push(it);
            if (isHouse(it) && (price <= budget || price * DOWN_PCT <= budget)) props.push(it);
          }
          cars.sort(function(a,b){ return parsePrice(b.price) - parsePrice(a.price); });
          props.sort(function(a,b){ return parsePrice(b.price) - parsePrice(a.price); });

          // --- Option A: Automotive ---
          if (autoBody) {
            if (cars.length === 0) {
              autoBody.innerHTML = budget > 0
                ? "በ <b>" + fmt(budget) + "</b> በጀት ውስጥ በአሁኑ ገበያ ላይ ተሽከርካሪ አልተገኘም። Mini App ገበያውን ይመልከቱ።"
                : "በጀት ያስገቡ።";
            } else {
              var top = cars.slice(0, 3);
              var lines = top.map(function(it){
                var p = parsePrice(it.price);
                var down = p * DOWN_PCT;
                var loan = p - down;
                var mpay = monthlyPayment(loan, APR, AUTO_YEARS);
                return "• <b>" + titleOf(it) + "</b> — " + fmt(p) +
                  "<br><span style='opacity:.85'>ቅድመ 30%: " + fmt(down) + " · ብድር: " + fmt(loan) +
                  " · ወርሃዊ (~18%/5ዓመት): " + fmt(mpay) + "</span>";
              });
              autoBody.innerHTML = "ከአዲካ ገበያ (" + cars.length + " ተሽከርካሪ ≤ በጀት):<br>" + lines.join("<br>");
            }
          }

          // --- Option B: Real Estate ---
          if (propBody) {
            if (props.length === 0) {
              propBody.innerHTML = budget > 0
                ? "በ <b>" + fmt(budget) + "</b> (ዋጋ ወይም 30% ቅድመ ክፍያ) የሚገኝ ቤት/መሬት በአሁኑ ገበያ አልተገኘም።"
                : "በጀት ያስገቡ።";
            } else {
              var topP = props.slice(0, 3);
              var linesP = topP.map(function(it){
                var p = parsePrice(it.price);
                var down = p * DOWN_PCT;
                var loan = Math.max(0, p - down);
                var mpay = monthlyPayment(loan, APR, MORTGAGE_YEARS);
                return "• <b>" + titleOf(it) + "</b> — " + fmt(p) +
                  "<br><span style='opacity:.85'>ቅድመ 30%: " + fmt(down) + " · ብድር: " + fmt(loan) +
                  " · ወርሃዊ (~18%/15ዓመት): " + fmt(mpay) + "</span>";
              });
              propBody.innerHTML = "ከአዲካ ገበያ (" + props.length + " ንብረት):<br>" + linesP.join("<br>");
            }
          }

          // --- Option C: Business ROI (formula-based Ethiopian benchmarks 15–35%) ---
          if (roiBody) {
            if (budget <= 0) {
              roiBody.innerHTML = "በጀት ያስገቡ።";
            } else {
              // Tier by budget size using fixed benchmark bands (not random)
              var lowY = 0.15, midY = 0.22, highY = 0.30;
              if (budget < 200000) { lowY = 0.20; midY = 0.28; highY = 0.35; }
              else if (budget < 1000000) { lowY = 0.18; midY = 0.25; highY = 0.32; }
              else { lowY = 0.15; midY = 0.22; highY = 0.28; }
              var ideas = [];
              if (budget < 150000) {
                ideas = ["ትንሽ የቁሳቁስ/ሞባይል መለዋወጫ ንግድ", "የምግብ/ጭማቂ ማስረጃ ኪዮስክ", "የመላኪያ (delivery) አገልግሎት"];
              } else if (budget < 800000) {
                ideas = ["የመኪና ኪራይ (ride) አንድ ተሽከርካሪ", "ትንሽ ሱፐርማርኬት/ሱቅ", "የጋራዥ ቀላል ጥገና አገልግሎት"];
              } else {
                ideas = ["ባለብዙ መኪና የኪራይ መርሃግብር", "ትንሽ የማከማቻ/ዌርሃውስ ኪራይ", "የሪል እስቴት ኪራይ ፖርትፎሊዮ"];
              }
              var yLow = Math.round(budget * lowY);
              var yMid = Math.round(budget * midY);
              var yHigh = Math.round(budget * highY);
              roiBody.innerHTML =
                "በጀት <b>" + fmt(budget) + "</b> — የኢትዮጵያ ገበያ ባንድ (15–35% ዓመታዊ):<br>" +
                "• " + ideas[0] + " · ROI ~" + Math.round(lowY*100) + "% → <b>" + fmt(yLow) + "/ዓመት</b><br>" +
                "• " + ideas[1] + " · ROI ~" + Math.round(midY*100) + "% → <b>" + fmt(yMid) + "/ዓመት</b><br>" +
                "• " + ideas[2] + " · ROI ~" + Math.round(highY*100) + "% → <b>" + fmt(yHigh) + "/ዓመት</b>" +
                (income > 0 ? "<br><span style='opacity:.85'>የእርስዎ ወርሃዊ ገቢ: " + fmt(income) + " (DTI ≤35% ለብድር)</span>" : "");
            }
          }
        })
        .catch(function(){
          if (autoBody) autoBody.innerHTML = "ገበያውን ማግኘት አልተቻለም። እንደገና ይሞክሩ ወይም Mini App ገበያ ይመልከቱ።";
          if (propBody) propBody.innerHTML = "ገበያውን ማግኘት አልተቻለም።";
          if (roiBody && budget > 0) {
            var y = Math.round(budget * 0.22);
            roiBody.innerHTML = "ግምታዊ መካከለኛ ROI 22%: <b>" + Math.round(budget * 0.22).toLocaleString() + " ብር/ዓመት</b> (ከበጀት ቀመር)።";
          }
        });
    }

    var advBtnEl = document.getElementById("advisorBtn");
    if (advBtnEl) {
      advBtnEl.onclick = function() {
        renderOpportunityCards();
      };
    }
    // Opportunity CTA → open live chat with context prefilled
    document.querySelectorAll(".opp-chat-cta").forEach(function(btn) {
      btn.onclick = function() {
        var ctx = btn.getAttribute("data-context") || "auto";
        var budget = Number((document.getElementById("advisorBudget") || {}).value) || 0;
        var income = Number((document.getElementById("advisorMonthlyIncome") || {}).value) || 0;
        var prompts = {
          auto: "በጀቴ " + budget.toLocaleString() + " ብር ነው፣ ወርሃዊ ገቢዬ " + income.toLocaleString() + " ብር ነው። በዚህ በጀት የትኛውን ተሽከርካሪ መምረጥ እችላለሁ? የባንክ ብድር አማራጭም አብረው ያብራሩልኝ።",
          property: "በጀቴ " + budget.toLocaleString() + " ብር ነው፣ ወርሃዊ ገቢዬ " + income.toLocaleString() + " ብር ነው። ለቤት/መሬት የመግቢያ ቅድመ ክፍያ እና የብድር አሰራር ያብራሩልኝ።",
          roi: "በጀቴ " + budget.toLocaleString() + " ብር ነው። የሪል እስቴት ወይም የንግድ ኢንቨስትመንት ዓመታዊ ROI እና የኪራይ ገቢ ግምት ያሳዩኝ።"
        };
        try {
          var aiModal = document.getElementById("aiModal");
          if (aiModal) { aiModal.classList.add("hidden"); aiModal.classList.remove("flex"); }
        } catch (e) {}
        showAnalysisView(true);
        var log = document.getElementById("advisorChatLog");
        if (log && !log.dataset.seeded) {
          log.innerHTML = "";
          advisorChatHistory = [];
          var initMsg = "ሰላም! እኔ የ Adika Senior Financial Advisor ነኝ። ስለ መኪና ወይም የቤት ግዢ፣ የቀረጥ ስሌት፣ የባንክ ብድር ወይም ማንኛውም የፋይናንስ ምክር ምን ማወቅ ይፈልጋሉ?";
          appendAdvisorChat("advisor", initMsg);
          advisorChatHistory.push({ role: "advisor", content: initMsg });
          log.dataset.seeded = "1";
        }
        var input = document.getElementById("advisorChatInput");
        if (input) {
          input.value = prompts[ctx] || prompts.auto;
          if (input.tagName === "TEXTAREA") {
            input.style.height = "auto";
            input.style.height = Math.min(input.scrollHeight, 110) + "px";
          }
        }
      };
    });


    (function(){
      function bindAdvisorChat() {
        var sendBtn = document.getElementById("advisorChatSend");
        var input = document.getElementById("advisorChatInput");
        if (!sendBtn || !input || sendBtn.dataset.bound === "1") return;
        sendBtn.dataset.bound = "1";
        function removeTyping() {
          var log = document.getElementById("advisorChatLog");
          if (!log) return;
          var nodes = log.querySelectorAll("[data-typing='1']");
          for (var i = 0; i < nodes.length; i++) nodes[i].parentNode.removeChild(nodes[i]);
        }
        function showTyping() {
          var log = document.getElementById("advisorChatLog");
          if (!log) return;
          removeTyping();
          var row = document.createElement("div");
          row.setAttribute("data-typing", "1");
          row.className = "mr-6 p-3 rounded-2xl bg-white text-slate-600 border border-slate-200/90 shadow-sm text-xs font-bold flex items-center gap-2 animate-in fade-in";
          row.innerHTML = '<span class="inline-flex gap-1 items-center"><span class="w-2 h-2 rounded-full bg-[#16acbd] animate-pulse"></span><span class="w-2 h-2 rounded-full bg-[#16acbd] animate-pulse" style="animation-delay:200ms"></span><span class="w-2 h-2 rounded-full bg-[#16acbd] animate-pulse" style="animation-delay:400ms"></span></span><span>አማካሪው መልስ በመጻፍ ላይ ነው...</span>';
          log.appendChild(row);
          setTimeout(function() { log.scrollTop = log.scrollHeight; }, 30);
        }
        function sendChat() {
          var text = (input.value || "").trim();
          if (!text) return;
          if (typeof appendAdvisorChat === "function") appendAdvisorChat("user", text);
          advisorChatHistory.push({ role: "user", content: text });
          input.value = "";
          if (input.tagName === "TEXTAREA") { input.style.height = "38px"; }
          showTyping();
          
          fetch("/api/advisor/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              message: text,
              history: advisorChatHistory
            })
          })
          .then(function(r){ return r.json(); })
          .then(function(d){
            removeTyping();
            var msg = d.reply || d.response || d.message || "ጥያቄዎን ተረድቻለሁ፤ በደስታ እርሶን ለማገዝ ዝግጁ ነኝ።";
            msg = String(msg).replace(/\bAI\b/gi, "እኛ").replace(/language model/gi, "እኛ").replace(/\bbot\b/gi, "እኛ");
            if (typeof appendAdvisorChat === "function") appendAdvisorChat("advisor", msg);
            advisorChatHistory.push({ role: "advisor", content: msg });
          })
          .catch(function(){
            removeTyping();
            if (typeof appendAdvisorChat === "function") {
              appendAdvisorChat("advisor", "መልስ ማግኘት አልተቻለም። እባክዎን ትንሽ ቆይተው እንደገና ይሞክሩ።");
            }
          });
        }
        sendBtn.onclick = sendChat;
        input.addEventListener("keydown", function(ev){
          if (ev.key === "Enter" && !ev.shiftKey) { ev.preventDefault(); sendChat(); }
        });
        if (input.tagName === "TEXTAREA") {
          input.addEventListener("input", function() {
            input.style.height = "auto";
            input.style.height = Math.min(input.scrollHeight, 110) + "px";
          });
        }
      }
      bindAdvisorChat();
      setTimeout(bindAdvisorChat, 500);
    })();

    // Duty Calculator Action
    document.getElementById("dutyCalculateBtn").onclick = function() {
      var cif = document.getElementById("dutyCif").value || 12000;
      var fuel = document.getElementById("dutyFuel").value || "Benzine";
      var cc = document.getElementById("dutyCc").value || 1300;
      var resEl = document.getElementById("dutyResult");
      resEl.classList.remove("hidden");
      resEl.innerHTML = "⏳ የቀረጥ ስሌት እየተሰራ ነው...";

      fetch("/api/calculate-duty", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ cif_usd: Number(cif), fuel_type: fuel, engine_cc: Number(cc), year: 2018 })
      })
      .then(function(r){ return r.json(); })
      .then(function(d){
        var duty = d.tax_breakdown || {};
        var totalTaxes = d.total_taxes_etb || duty.total_taxes_etb || d.total_tax_payable_etb || d.total_duty_etb || 0;
        var landedCost = d.total_landed_cost_etb || d.landed_cost_etb || 0;
        var cifEtb = d.cif_etb || d.cif_landed_cost_etb || (d.cif_usd ? d.cif_usd * 128.5 : 0);
        
        resEl.innerHTML =
          '<div class="space-y-2 text-xs">' +
            '<div class="p-2.5 rounded-2xl bg-[#16acbd]/10 border border-[#16acbd]/20">' +
              '<div class="text-[10px] text-slate-500 font-bold uppercase">ጠቅላላ የሚከፈል ቀረጥና ታክስ (Total Duty & Tax)</div>' +
              '<div class="text-lg font-black text-[#0e7490]">' + Number(totalTaxes).toLocaleString() + ' ETB</div>' +
              '<div class="text-[11px] text-slate-600 mt-1 flex justify-between">' +
                '<span>• CIF ዋጋ (Landed Cost USD/ETB):</span>' +
                '<b class="text-slate-900">$' + Number(d.cif_usd || cif).toLocaleString() + ' (~' + Number(cifEtb).toLocaleString() + ' ETB)</b>' +
              '</div>' +
              '<div class="text-[11px] text-slate-600 mt-0.5 flex justify-between">' +
                '<span>• ጠቅላላ የወደብ ዋጋ (Total Landed Cost):</span>' +
                '<b class="text-emerald-700">' + Number(landedCost).toLocaleString() + ' ETB</b>' +
              '</div>' +
            '</div>' +
            '<div class="grid grid-cols-2 gap-1.5 text-[10px] bg-white p-2.5 rounded-xl border border-slate-100 shadow-sm">' +
              '<div>ጉምሩክ ቀረጥ (' + (d.tax_rates ? d.tax_rates.customs_duty : '35%') + '): <b>' + Number(duty.customs_duty_etb || d.customs_duty_etb || 0).toLocaleString() + ' ETB</b></div>' +
              '<div>ኤክሳይስ ታክስ (' + (d.tax_rates ? d.tax_rates.excise_tax : '30%') + '): <b>' + Number(duty.excise_tax_etb || d.excise_tax_etb || 0).toLocaleString() + ' ETB</b></div>' +
              '<div>ቫት (VAT 15%): <b>' + Number(duty.vat_etb || d.vat_etb || 0).toLocaleString() + ' ETB</b></div>' +
              '<div>ሱር ታክስ (10%): <b>' + Number(duty.surtax_etb || d.surtax_etb || 0).toLocaleString() + ' ETB</b></div>' +
              '<div class="col-span-2 text-slate-500">ዊዝሆልዲንግ (3%): <b>' + Number(duty.withholding_tax_etb || d.withholding_tax_etb || 0).toLocaleString() + ' ETB</b></div>' +
            '</div>' +
            (d.policy_note ? '<div class="text-[10px] text-slate-500 italic">📌 ' + esc(d.policy_note) + '</div>' : '') +
          '</div>';
      })
      .catch(function(){ resEl.innerHTML = '<div class="p-2 bg-rose-50 text-rose-700 rounded-xl text-xs">ስሌቱን ማጠናቀቅ አልተቻለም። እባክዎ እንደገና ይሞክሩ።</div>'; });
    };

    // Bank Loan Action
    document.getElementById("loanCalculateBtn").onclick = function() {
      var price = document.getElementById("loanPrice").value || 3000000;
      var down = document.getElementById("loanDown").value || 30;
      var years = document.getElementById("loanYears").value || 10;
      var resEl = document.getElementById("loanResult");
      resEl.classList.remove("hidden");
      resEl.innerHTML = "⏳ የብድር ስሌት እየተሰራ ነው...";

      fetch("/api/calculate-loan", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ property_price: Number(price), down_payment_percent: Number(down), tenure_years: Number(years), monthly_income: 100000 })
      })
      .then(function(r){ return r.json(); })
      .then(function(d){
        var rep = d.repayment_details || {};
        var summary = d.loan_summary || {};
        var elig = d.eligibility_analysis || {};
        var monthlyPayment = rep.monthly_repayment_etb || d.monthly_payment_etb || d.estimated_monthly_payment || 0;
        var loanAmt = summary.principal_loan_amount_etb || d.loan_amount_etb || 0;
        var downAmt = summary.down_payment_amount_etb || d.down_payment_etb || 0;
        var totalInterest = rep.total_interest_payable_etb || d.total_interest_amount_etb || d.total_interest_etb || 0;
        var totalRepayment = rep.total_amount_payable_etb || d.total_repayment_amount_etb || d.total_repayment_etb || 0;
        var interestRate = summary.annual_interest_rate || (d.applied_interest_rate_pct ? d.applied_interest_rate_pct + "%" : "17.5%");

        resEl.innerHTML =
          '<div class="space-y-2 text-xs">' +
            '<div class="p-2.5 rounded-2xl bg-emerald-50 border border-emerald-200 shadow-sm">' +
              '<div class="text-[10px] text-emerald-700 font-bold uppercase">ወርሃዊ የባንክ ክፍያ (Monthly Payment)</div>' +
              '<div class="text-lg font-black text-emerald-700">' + Number(monthlyPayment).toLocaleString() + ' ETB / ወር</div>' +
              '<div class="grid grid-cols-2 gap-1 text-[11px] text-slate-600 mt-2 pt-2 border-t border-emerald-200/60">' +
                '<div>• የብድር መጠን (Principal): <b class="text-slate-800">' + Number(loanAmt).toLocaleString() + ' ETB</b></div>' +
                '<div>• ቅድመ ክፍያ (Down Payment): <b class="text-slate-800">' + Number(downAmt).toLocaleString() + ' ETB</b></div>' +
                '<div>• ጠቅላላ ወለድ (Total Interest): <b class="text-amber-700">' + Number(totalInterest).toLocaleString() + ' ETB</b></div>' +
                '<div>• ጠቅላላ የሚከፈል (Total Repayment): <b class="text-emerald-800">' + Number(totalRepayment).toLocaleString() + ' ETB</b></div>' +
                '<div class="col-span-2 text-slate-500">• የተተገበረ የወለድ ምጣኔ (Applied Rate): <b class="text-slate-800">' + esc(interestRate) + '</b> (' + (summary.tenure_years || years) + ' ዓመታት)</div>' +
              '</div>' +
            '</div>' +
            (elig.verdict ? 
              '<div class="p-2.5 bg-slate-50 rounded-xl border border-slate-200 text-[11px] text-slate-700">' +
                '<div class="font-bold text-slate-900 mb-0.5 flex items-center gap-1"><span>🏦</span><span>የብድር ብቁነት ትንተና:</span></div>' +
                '<div>' + esc(elig.verdict) + '</div>' +
                (elig.dti_ratio_pct ? '<div class="text-[10px] text-slate-500 mt-1">• የገቢ ሬሾ (Debt-to-Income / DTI): <b>' + elig.dti_ratio_pct + '%</b></div>' : '') +
              '</div>' : '') +
          '</div>';
      })
      .catch(function(){ resEl.innerHTML = '<div class="p-2 bg-rose-50 text-rose-700 rounded-xl text-xs">ስሌቱን ማጠናቀቅ አልተቻለም። እባክዎ እንደገና ይሞክሩ።</div>'; });
    };

    // Compare Cars Action
    // ===== World-class Comparison & Feasibility Engine =====
    var compareActiveTab = "vehicles";
    var lastComparePayload = null;

    document.querySelectorAll(".compare-tab").forEach(function(tab) {
      tab.onclick = function() {
        compareActiveTab = tab.getAttribute("data-ctab") || "vehicles";
        document.querySelectorAll(".compare-tab").forEach(function(x) {
          x.className = "compare-tab flex-1 py-1.5 rounded-full text-[10px] font-extrabold transition-all text-slate-400 hover:text-white";
        });
        tab.className = "compare-tab flex-1 py-1.5 rounded-full text-[10px] font-extrabold transition-all bg-teal-600 text-white shadow";
        var pv = document.getElementById("comparePanelVehicles");
        var pp = document.getElementById("comparePanelProperty");
        var pb = document.getElementById("comparePanelBusiness");
        if (pv) pv.classList.toggle("hidden", compareActiveTab !== "vehicles");
        if (pp) pp.classList.toggle("hidden", compareActiveTab !== "property");
        if (pb) pb.classList.toggle("hidden", compareActiveTab !== "business");
        var res = document.getElementById("compareResult");
        if (res) { res.classList.add("hidden"); res.innerHTML = ""; }
      };
    });

    function fmtEtb(n) {
      return Math.round(Number(n) || 0).toLocaleString() + " ብር";
    }
    function shortName(n, maxLen) {
      n = String(n || "").trim();
      maxLen = maxLen || 14;
      if (n.length <= maxLen) return n;
      return n.slice(0, maxLen - 1) + "…";
    }
    function metricLabel(am, en) {
      return '<span class="text-slate-200">' + am + '</span> <span class="text-slate-500 font-medium">· ' + en + '</span>';
    }
    function metricBarRow(labelHtml, v1, v2, unit, winner, name1, name2) {
      var max = Math.max(Number(v1) || 0, Number(v2) || 0, 1);
      var p1 = Math.round((Number(v1) || 0) / max * 100);
      var p2 = Math.round((Number(v2) || 0) / max * 100);
      var b1 = winner === "item_1" ? '<span class="ml-1 inline-flex items-center px-1.5 py-0.5 rounded-full text-[8px] font-black bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">🏆</span>' : '';
      var b2 = winner === "item_2" ? '<span class="ml-1 inline-flex items-center px-1.5 py-0.5 rounded-full text-[8px] font-black bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">🏆</span>' : '';
      var s1 = shortName(name1, 12);
      var s2 = shortName(name2, 12);
      return (
        '<div class="space-y-1.5">' +
          '<div class="flex justify-between items-start gap-2 text-[9px] font-bold leading-snug"><div class="min-w-0">' + labelHtml + '</div><span class="text-slate-500 shrink-0">' + unit + '</span></div>' +
          '<div class="flex items-center gap-2">' +
            '<div class="w-[4.6rem] text-[8px] font-black text-teal-300 shrink-0 truncate" title="' + (name1||'') + '">' + s1 + '</div>' +
            '<div class="flex-1 h-2.5 rounded-full bg-slate-800 overflow-hidden"><div class="h-full rounded-full bg-emerald-500 transition-all duration-700" style="width:' + p1 + '%"></div></div>' +
            '<div class="text-[9px] font-bold text-white min-w-[3.5rem] text-right">' + (Number(v1)||0).toLocaleString() + b1 + '</div>' +
          '</div>' +
          '<div class="flex items-center gap-2">' +
            '<div class="w-[4.6rem] text-[8px] font-black text-amber-300 shrink-0 truncate" title="' + (name2||'') + '">' + s2 + '</div>' +
            '<div class="flex-1 h-2.5 rounded-full bg-slate-800 overflow-hidden"><div class="h-full rounded-full bg-amber-500 transition-all duration-700" style="width:' + p2 + '%"></div></div>' +
            '<div class="text-[9px] font-bold text-white min-w-[3.5rem] text-right">' + (Number(v2)||0).toLocaleString() + b2 + '</div>' +
          '</div>' +
        '</div>'
      );
    }
    function glassCard(titleAm, titleEn, value, sub) {
      return '<div class="rounded-xl bg-slate-900/60 border border-slate-800 p-2.5 backdrop-blur-md">' +
        '<div class="text-[8px] text-slate-400 font-bold leading-snug">' + titleAm + '</div>' +
        '<div class="text-[7px] text-slate-500">' + titleEn + '</div>' +
        '<div class="text-[12px] font-black text-white mt-0.5 leading-tight">' + value + '</div>' +
        (sub ? '<div class="text-[8px] text-slate-500 mt-0.5">' + sub + '</div>' : '') +
      '</div>';
    }
    function estimateBadge(it) {
      return it && it.is_estimate ? '<span class="ml-1 px-1.5 py-0.5 rounded-full text-[8px] font-black bg-amber-500/15 text-amber-400 border border-amber-500/20">ግምት</span>' : '';
    }
    function executiveBox(d) {
      return (
        '<div class="rounded-2xl bg-slate-950/80 border border-slate-800 p-3.5">' +
          '<div class="flex items-center justify-between mb-1.5 gap-2">' +
            '<div class="text-[9px] font-black uppercase tracking-wide text-amber-400">የባለሙያ ማጠቃለያ</div>' +
            '<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-[9px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 shrink-0">🏆 ' + (d.winner_name || "") + '</span>' +
          '</div>' +
          '<p class="text-[11px] text-slate-200 leading-relaxed font-medium">' + (d.executive_summary_amharic || "") + '</p>' +
        '</div>'
      );
    }
    function liveChatCta(winnerName) {
      var safeName = winnerName || "ንብረት";
      return (
        '<button type="button" id="compareLiveChatCta" class="w-full mt-1 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-bold py-3.5 px-4 rounded-2xl shadow-xl transition-all flex items-center justify-between gap-2 text-[11px] leading-snug">' +
          '<span class="text-left">💬 ስለ ተመራጩ <b>' + safeName + '</b> ከ Adika Digital Advisor ጋር Live Chat ያድርጉ →</span>' +
        '</button>'
      );
    }
    function bindLiveChatCta(d) {
      var btn = document.getElementById("compareLiveChatCta");
      if (!btn) return;
      btn.onclick = function() {
        lastComparePayload = d;
        try {
          var m = document.getElementById("compareModal");
          if (m) { m.classList.add("hidden"); m.classList.remove("flex"); }
        } catch (e) {}
        if (typeof showAnalysisView === "function") showAnalysisView(true);
        var log = document.getElementById("advisorChatLog");
        if (log && !log.dataset.seeded) {
          log.innerHTML = "";
          if (typeof advisorChatHistory !== "undefined") advisorChatHistory = [];
          var initMsg = "ሰላም! እኔ የ Adika Senior Financial Advisor ነኝ። የንጽጽር ውጤትዎን አይቻለሁ — ጥያቄዎን በደስታ እመልሳለሁ።";
          if (typeof appendAdvisorChat === "function") {
            appendAdvisorChat("advisor", initMsg);
            if (typeof advisorChatHistory !== "undefined") advisorChatHistory.push({ role: "advisor", content: initMsg });
          }
          log.dataset.seeded = "1";
        }
        var input = document.getElementById("advisorChatInput");
        if (input) {
          var n1 = (d.item_1 && d.item_1.name) || "";
          var n2 = (d.item_2 && d.item_2.name) || "";
          input.value = "የ " + n1 + " እና " + n2 + " ንጽጽር አድርጌአለሁ። አሸናፊው " + (d.winner_name || "") + " ነው። እባክዎ ጥልቅ የፋይናንስ ምክር ይስጡኝ።";
          if (input.tagName === "TEXTAREA") {
            input.style.height = "auto";
            input.style.height = Math.min(input.scrollHeight, 110) + "px";
          }
        }
      };
    }
    function skeletonLoader() {
      return (
        '<div class="animate-pulse bg-slate-900/80 border border-slate-800 rounded-3xl p-5 space-y-3">' +
          '<div id="compareSkeletonStatus" class="text-[11px] font-bold text-teal-300/90 text-center">🔍 የAdika ገበያ መረጃዎችን ከመረጃ ቋት በማውጣት ላይ...</div>' +
          '<div class="grid grid-cols-2 gap-2"><div class="h-16 rounded-xl bg-slate-800/80"></div><div class="h-16 rounded-xl bg-slate-800/80"></div></div>' +
          '<div class="h-3 rounded-full bg-slate-800/80"></div>' +
          '<div class="h-3 rounded-full bg-slate-800/80 w-5/6"></div>' +
          '<div class="h-20 rounded-2xl bg-slate-800/80"></div>' +
        '</div>'
      );
    }
    function startSkeletonTicker() {
      var msgs = [
        "🔍 የAdika ገበያ መረጃዎችን ከመረጃ ቋት በማውጣት ላይ...",
        "⛽ የ 5 ዓመት የTCO/የወጪ ስሌቶችን በማስላት ላይ...",
        "💡 የAI የፋይናንስ ማጠቃለያ በማዘጋጀት ላይ..."
      ];
      var i = 0;
      return setInterval(function() {
        i = (i + 1) % msgs.length;
        var n = document.getElementById("compareSkeletonStatus");
        if (n) n.textContent = msgs[i];
      }, 800);
    }
    function wrapDashboard(inner, d) {
      return (
        '<div class="bg-slate-900/90 backdrop-blur-xl border border-slate-800 rounded-3xl p-4 shadow-2xl space-y-2.5">' +
          inner + executiveBox(d) + liveChatCta(d.winner_name) +
        '</div>'
      );
    }

    function renderVehicleDashboard(d) {
      var a = d.item_1 || {}, b = d.item_2 || {}, m = d.metrics || {}, c = d.calculated_metrics || {};
      var n1 = a.name || "ንብረት 1", n2 = b.name || "ንብረት 2";
      var html = '<div class="grid grid-cols-2 gap-2">';
      html += '<div class="rounded-xl bg-slate-900/60 border border-slate-800 p-2.5"><div class="text-[8px] font-bold text-teal-400">ንብረት 1' + estimateBadge(a) + '</div><div class="text-[11px] font-black text-white leading-tight mt-0.5">' + n1 + '</div><div class="text-[10px] text-slate-400 mt-1">' + fmtEtb(a.price) + '</div></div>';
      html += '<div class="rounded-xl bg-slate-900/60 border border-slate-800 p-2.5"><div class="text-[8px] font-bold text-amber-400">ንብረት 2' + estimateBadge(b) + '</div><div class="text-[11px] font-black text-white leading-tight mt-0.5">' + n2 + '</div><div class="text-[10px] text-slate-400 mt-1">' + fmtEtb(b.price) + '</div></div>';
      html += '</div>';
      html += '<div class="rounded-xl bg-slate-900/60 border border-slate-800 p-2.5 space-y-3">';
      html += '<div class="text-[9px] font-black text-slate-300">የንጽጽር መለኪያዎች</div>';
      if (m.tco_5yr) html += metricBarRow(metricLabel("የ 5 ዓመት አጠቃላይ የባለቤትነት ወጪ", "5-Year TCO"), m.tco_5yr.item_1, m.tco_5yr.item_2, "ብር", m.tco_5yr.winner, n1, n2);
      if (m.depreciation_pct) html += metricBarRow(metricLabel("ዓመታዊ የዋጋ ቅናሽ", "Depreciation"), m.depreciation_pct.item_1, m.depreciation_pct.item_2, "%", m.depreciation_pct.winner, n1, n2);
      if (m.fuel_efficiency) html += metricBarRow(metricLabel("የነዳጅ/የኤሌክትሪክ ቁጠባ አቅም", "Energy Efficiency"), m.fuel_efficiency.item_1, m.fuel_efficiency.item_2, "KM/L", m.fuel_efficiency.winner, n1, n2);
      if (m.parts_score) html += metricBarRow(metricLabel("የመለዋወጫ ተደራሽነት", "Parts Score"), m.parts_score.item_1, m.parts_score.item_2, "/100", m.parts_score.winner, n1, n2);
      if (m.resale_index) html += metricBarRow(metricLabel("መልሶ የመሸጥ አቅም (የገበያ ተፈላጊነት)", "Resale Index"), m.resale_index.item_1, m.resale_index.item_2, "/100", m.resale_index.winner, n1, n2);
      html += '</div>';
      html += '<div class="grid grid-cols-2 gap-1.5">';
      html += glassCard("ዝቅተኛ የ 30% ቅድመ ክፍያ", "Minimum Downpayment", fmtEtb(c.loan_downpayment_min));
      html += glassCard("የ 5 ዓመት ወጪ ልዩነት", "TCO Delta", fmtEtb(c.tco_5yr_delta));
      html += glassCard("ወርሃዊ የባንክ ብድር · " + shortName(n1, 10), "Monthly Bank Loan", fmtEtb(c.monthly_loan_item_1), "18% · 5ዓመት");
      html += glassCard("ወርሃዊ የባንክ ብድር · " + shortName(n2, 10), "Monthly Bank Loan", fmtEtb(c.monthly_loan_item_2), "18% · 5ዓመት");
      html += '</div>';
      return wrapDashboard(html, d);
    }
    function renderPropertyDashboard(d) {
      var a = d.item_1 || {}, b = d.item_2 || {}, m = d.metrics || {};
      var n1 = a.name || a.name_am || "ንብረት 1", n2 = b.name || b.name_am || "ንብረት 2";
      var html = '<div class="grid grid-cols-2 gap-2">';
      html += '<div class="rounded-xl bg-slate-900/60 border border-slate-800 p-2.5"><div class="text-[8px] font-bold text-teal-400">ንብረት 1</div><div class="text-[11px] font-black text-white">' + n1 + '</div><div class="text-[9px] text-slate-400 mt-1">ኪራይ/ወር ' + fmtEtb(a.monthly_rent_etb) + '</div></div>';
      html += '<div class="rounded-xl bg-slate-900/60 border border-slate-800 p-2.5"><div class="text-[8px] font-bold text-amber-400">ንብረት 2</div><div class="text-[11px] font-black text-white">' + n2 + '</div><div class="text-[9px] text-slate-400 mt-1">ኪራይ/ወር ' + fmtEtb(b.monthly_rent_etb) + '</div></div>';
      html += '</div>';
      html += '<div class="rounded-xl bg-slate-900/60 border border-slate-800 p-2.5 space-y-3">';
      html += '<div class="text-[9px] font-black text-slate-300">የሪል እስቴት መለኪያዎች</div>';
      if (m.inflation_hedge) html += metricBarRow(metricLabel("የዋጋ ግሽበትን የመቋቋም አቅም", "Inflation Hedge"), m.inflation_hedge.item_1, m.inflation_hedge.item_2, "/100", m.inflation_hedge.winner, n1, n2);
      if (m.rental_yield) html += metricBarRow(metricLabel("ወርሃዊ የኪራይ ገቢ ማስገኘት አቅም", "Rental Yield / Cashflow"), m.rental_yield.item_1, m.rental_yield.item_2, "%/ዓመት", m.rental_yield.winner, n1, n2);
      if (m.appreciation_5yr) html += metricBarRow(metricLabel("የ 5 ዓመት የዋጋ ዕድገት ግምት", "Capital Appreciation"), m.appreciation_5yr.item_1, m.appreciation_5yr.item_2, "%", m.appreciation_5yr.winner, n1, n2);
      if (m.appreciation_3yr) html += metricBarRow(metricLabel("የ 3 ዓመት የዋጋ ዕድገት", "3-Year Growth"), m.appreciation_3yr.item_1, m.appreciation_3yr.item_2, "%", m.appreciation_3yr.winner, n1, n2);
      if (m.development_score) html += metricBarRow(metricLabel("የልማት/እድሳት አቅም", "Development Potential"), m.development_score.item_1, m.development_score.item_2, "/100", m.development_score.winner, n1, n2);
      html += '</div>';
      html += '<div class="grid grid-cols-2 gap-1.5">';
      html += glassCard("ከ 5 ዓመት በኋላ · " + shortName(n1, 10), "Value @ 5yr", fmtEtb(a.value_5yr_etb), "ትርፍ " + fmtEtb(a.gain_5yr_etb));
      html += glassCard("ከ 5 ዓመት በኋላ · " + shortName(n2, 10), "Value @ 5yr", fmtEtb(b.value_5yr_etb), "ትርፍ " + fmtEtb(b.gain_5yr_etb));
      html += '</div>';
      return wrapDashboard(html, d);
    }
    function renderBusinessDashboard(d) {
      var a = d.item_1 || {}, b = d.item_2 || {}, m = d.metrics || {};
      var n1 = a.name || "ንግድ 1", n2 = b.name || "ንግድ 2";
      var html = '<div class="grid grid-cols-2 gap-2">';
      html += '<div class="rounded-xl bg-slate-900/60 border border-slate-800 p-2.5"><div class="text-[8px] font-bold text-teal-400">ንግድ 1</div><div class="text-[11px] font-black text-white leading-tight">' + n1 + '</div><div class="text-[9px] text-slate-400 mt-1">መነሻ ' + fmtEtb(a.min_capital) + '</div></div>';
      html += '<div class="rounded-xl bg-slate-900/60 border border-slate-800 p-2.5"><div class="text-[8px] font-bold text-amber-400">ንግድ 2</div><div class="text-[11px] font-black text-white leading-tight">' + n2 + '</div><div class="text-[9px] text-slate-400 mt-1">መነሻ ' + fmtEtb(b.min_capital) + '</div></div>';
      html += '</div>';
      html += '<div class="rounded-xl bg-slate-900/60 border border-slate-800 p-2.5 space-y-3">';
      html += '<div class="text-[9px] font-black text-slate-300">የንግድ አዋጭነት ማትሪክስ</div>';
      if (m.min_capital) html += metricBarRow(metricLabel("ዝቅተኛ የመነሻ ካፒታል", "Min Capital"), m.min_capital.item_1, m.min_capital.item_2, "ብር", m.min_capital.winner, n1, n2);
      if (m.space_sqm) html += metricBarRow(metricLabel("የቦታ ፍላጎት", "Space Footprint"), m.space_sqm.item_1, m.space_sqm.item_2, "m²", m.space_sqm.winner, n1, n2);
      if (m.labor_monthly) html += metricBarRow(metricLabel("ወርሃዊ የሰው ኃይልና የኦፕሬሽን ወጪ", "Monthly OpEx"), m.labor_monthly.item_1, m.labor_monthly.item_2, "ብር", m.labor_monthly.winner, n1, n2);
      if (m.demand) html += metricBarRow(metricLabel("የገበያ ፍላጎት", "Market Demand"), m.demand.item_1, m.demand.item_2, "/100", m.demand.winner, n1, n2);
      if (m.risk) html += metricBarRow(metricLabel("የስጋት መጠን", "Risk Score"), m.risk.item_1, m.risk.item_2, "/100", m.risk.winner, n1, n2);
      if (m.roi_mid) html += metricBarRow(metricLabel("አመታዊ የትርፍ ግምት", "Est. Annual ROI"), m.roi_mid.item_1, m.roi_mid.item_2, "%", m.roi_mid.winner, n1, n2);
      if (m.breakeven_months) html += metricBarRow(metricLabel("መነሻ በጀት የሚመለስበት ጊዜ (ወራት)", "Payback Period"), m.breakeven_months.item_1, m.breakeven_months.item_2, "ወር", m.breakeven_months.winner, n1, n2);
      html += '</div>';
      html += '<div class="grid grid-cols-2 gap-1.5">';
      html += glassCard("ROI · " + shortName(n1, 12), "ROI Range", (a.roi_low||0) + "–" + (a.roi_high||0) + "%", a.incentive || "");
      html += glassCard("ROI · " + shortName(n2, 12), "ROI Range", (b.roi_low||0) + "–" + (b.roi_high||0) + "%", b.incentive || "");
      html += '</div>';
      return wrapDashboard(html, d);
    }

    document.getElementById("compareBtn").onclick = function() {
      var resEl = document.getElementById("compareResult");
      resEl.classList.remove("hidden");
      resEl.innerHTML = skeletonLoader();
      var ticker = startSkeletonTicker();

      var payload = { category: compareActiveTab };
      if (compareActiveTab === "vehicles") {
        payload.car_1 = (document.getElementById("compareCar1").value || "").trim();
        payload.car_2 = (document.getElementById("compareCar2").value || "").trim();
        var y1 = (document.getElementById("compareYear1") || {}).value || "";
        var y2 = (document.getElementById("compareYear2") || {}).value || "";
        payload.car1_year = String(y1).trim();
        payload.car2_year = String(y2).trim();
        if (payload.car1_year && payload.car_1.indexOf(payload.car1_year) < 0) payload.car_1 += " " + payload.car1_year;
        if (payload.car2_year && payload.car_2.indexOf(payload.car2_year) < 0) payload.car_2 += " " + payload.car2_year;
      } else if (compareActiveTab === "property") {
        payload.asset_1 = document.getElementById("compareAsset1").value;
        payload.asset_2 = document.getElementById("compareAsset2").value;
        payload.budget = Number(document.getElementById("comparePropBudget").value) || 3000000;
      } else {
        payload.business_1 = (document.getElementById("compareBiz1").value || "").trim();
        payload.business_2 = (document.getElementById("compareBiz2").value || "").trim();
      }

      fetch("/api/compare-cars", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      })
      .then(function(r){ return r.json().then(function(d){ return { ok: r.ok, d: d }; }); })
      .then(function(x){
        if (ticker) clearInterval(ticker);
        if (!x.ok || x.d.status === "error") {
          resEl.innerHTML = '<div class="p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-[11px]">' + (x.d.message || "ንጽጽር አልተሳካም — እንደገና ይሞክሩ") + '</div>';
          return;
        }
        if (x.d.category === "property") resEl.innerHTML = renderPropertyDashboard(x.d);
        else if (x.d.category === "business") resEl.innerHTML = renderBusinessDashboard(x.d);
        else resEl.innerHTML = renderVehicleDashboard(x.d);
        bindLiveChatCta(x.d);
      })
      .catch(function(){
        if (ticker) clearInterval(ticker);
        resEl.innerHTML = '<div class="p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-[11px]">ግንኙነት አልተሳካም። እንደገና ይሞክሩ።</div>';
      });
    };

    // Helper: Read file to Base64
    function readFileAsBase64(file, callback) {
      if (!file) { callback(null); return; }
      var reader = new FileReader();
      reader.onload = function(e) { callback(e.target.result); };
      reader.onerror = function() { callback(null); };
      reader.readAsDataURL(file);
    }

    // ===== POA Digital Verification (client-side decode, no backend) =====
    function openExternalLink(url) {
      try {
        if (window.Telegram && window.Telegram.WebApp && window.Telegram.WebApp.openLink) {
          window.Telegram.WebApp.openLink(url);
          return;
        }
      } catch (e) {}
      window.open(url, "_blank", "noopener,noreferrer");
    }

    function showPoaStateA(url, resEl) {
      resEl.classList.remove("hidden");
      resEl.innerHTML =
        '<div class="p-3.5 rounded-2xl bg-white border border-emerald-200 shadow-sm space-y-3 text-xs">' +
          '<div class="font-black text-emerald-800 leading-snug">✅ የውክልና ሰነዱ በአዲካ ዲጂታል ሲስተም በስኬት ተመርምሯል!</div>' +
          '<button type="button" id="poaOpenDigitalBtn" class="w-full py-3 rounded-xl bg-[#16acbd] hover:bg-[#1394a3] text-white font-bold text-[11px] shadow-sm active:scale-[0.98] transition-all">' +
            '🔗 በአዲካ ዲጂታል ሲስተም የውክልና መረጃውን ይክፈቱ' +
          '</button>' +
        '</div>';
      var btn = document.getElementById("poaOpenDigitalBtn");
      if (btn) btn.onclick = function() { openExternalLink(url); };
    }

    function showPoaStateB(resEl) {
      resEl.classList.remove("hidden");
      resEl.innerHTML =
        '<div class="p-3.5 rounded-2xl bg-amber-50 border border-amber-200 text-amber-950 text-xs leading-relaxed">' +
          '⚠️ ይህ ሰነድ በአዲካ ዲጂታል ሲስተም ሊጣራ የሚችል የዲጂታል ምዝገባ መረጃ አልተገኘበትም። የቆየ የውክልና ሰነድ በመሆኑ፣ እባክዎን በአካል በአቅራቢያዎ በሚገኝ የሰነዶች ማረጋገጫና ምዝገባ (ውልና ማስረጃ) ቢሮ በመሄድ ያጣሩ።' +
        '</div>';
    }

    function showPoaStateC(resEl) {
      resEl.classList.remove("hidden");
      resEl.innerHTML =
        '<div class="p-3.5 rounded-2xl bg-rose-50 border border-rose-200 text-rose-900 text-xs leading-relaxed">' +
          '❌ በተላከው ፎቶ ላይ የሰነዱን ማረጋገጫ ማግኘት አልተቻለም። እባክዎን የሰነዱን ጽሁፍ እና ማህተም በግልጽ አድርገው ደግመው ይጭኑ።' +
        '</div>';
    }

    function scanPoaQrFromFile(file) {
      var resEl = document.getElementById("poaResult");
      var busy = document.getElementById("poaScanBusy");
      if (!file) return;
      if (busy) busy.classList.remove("hidden");
      if (resEl) { resEl.classList.add("hidden"); resEl.innerHTML = ""; }

      if (typeof jsQR !== "function") {
        if (busy) busy.classList.add("hidden");
        if (resEl) showPoaStateC(resEl);
        return;
      }

      var reader = new FileReader();
      reader.onerror = function() {
        if (busy) busy.classList.add("hidden");
        if (resEl) showPoaStateC(resEl);
      };
      reader.onload = function(event) {
        var img = new Image();
        img.onerror = function() {
          if (busy) busy.classList.add("hidden");
          if (resEl) showPoaStateC(resEl);
        };
        img.onload = function() {
          try {
            var canvas = document.createElement("canvas");
            var context = canvas.getContext("2d");
            // Keep up to 2500px for small paper document codes
            var width = img.width;
            var height = img.height;
            var MAX_SIZE = 2500;
            if (width > MAX_SIZE || height > MAX_SIZE) {
              if (width > height) {
                height = Math.round((height * MAX_SIZE) / width);
                width = MAX_SIZE;
              } else {
                width = Math.round((width * MAX_SIZE) / height);
                height = MAX_SIZE;
              }
            }
            canvas.width = Math.max(1, width);
            canvas.height = Math.max(1, height);
            context.drawImage(img, 0, 0, width, height);
            var imageData = context.getImageData(0, 0, width, height);

            var code = jsQR(imageData.data, imageData.width, imageData.height, {
              inversionAttempts: "attemptBoth"
            });

            if (busy) busy.classList.add("hidden");

            if (code && code.data && String(code.data).indexOf("http") !== -1) {
              var targetUrl = String(code.data).trim();
              if (resEl) showPoaStateA(targetUrl, resEl);
            } else {
              if (resEl) showPoaStateB(resEl);
            }
          } catch (err) {
            if (busy) busy.classList.add("hidden");
            if (resEl) showPoaStateC(resEl);
          }
        };
        img.src = event.target.result;
      };
      reader.readAsDataURL(file);
    }

    var poaImageFileEl = document.getElementById("poaImageFile");
    if (poaImageFileEl) {
      poaImageFileEl.addEventListener("change", function(e) {
        var file = e.target.files && e.target.files[0] ? e.target.files[0] : null;
        if (!file) return;
        scanPoaQrFromFile(file);
      });
    }


    // Diagnostic Analyze Action
    document.getElementById("diagAnalyzeBtn").onclick = function() {
      var carModel = document.getElementById("diagCarModel") ? document.getElementById("diagCarModel").value : "Toyota Vitz 2018";
      var diagText = (document.getElementById("diagInput").value || "").trim();
      var fileInput = document.getElementById("diagImageFile");
      var file = fileInput && fileInput.files && fileInput.files[0] ? fileInput.files[0] : null;
      var resEl = document.getElementById("diagResult");
      resEl.classList.remove("hidden");
      resEl.innerHTML = "⏳ የጋራዥ ምርመራ ሪፖርት እየተተነተነ ነው...";

      readFileAsBase64(file, function(base64Img) {
        fetch("/api/analyze-diagnostic", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ car_model: carModel, diagnostic_text: diagText, image_data: base64Img })
        })
        .then(function(r){ return r.json(); })
        .then(function(d){
          var an = d.analysis || d;

          // Strict Validation Check
          if (an.is_valid_diagnostic === false || an.error_message_amharic || an.status === 'error') {
            var errMsg = an.error_message_amharic || an.message || "እባክዎ ትክክለኛ የምርመራ ወረቀት ያስገቡ።";
            resEl.innerHTML =
              '<div class="p-3 bg-rose-50 border border-rose-200 rounded-2xl text-rose-800 text-xs shadow-sm space-y-1">' +
                '<div class="font-black text-rose-900 text-xs flex items-center gap-1.5">' +
                  '<span>⚠️</span><span>ትክክለኛ ያልሆነ የምርመራ ወረቀት (Invalid Sheet)</span>' +
                '</div>' +
                '<p class="leading-relaxed">' + esc(errMsg) + '</p>' +
              '</div>';
            return;
          }

          var score = an.health_score_pct || 86;
          var faults = an.identified_faults || [];
          var repCost = an.total_estimated_repair_cost_etb || 0;
          var advice = an.buyer_negotiation_advice_amharic || "";

          resEl.innerHTML =
            '<div class="space-y-2.5 text-xs">' +
              '<div class="p-3 bg-slate-900 text-white rounded-2xl flex items-center justify-between">' +
                '<div>' +
                  '<div class="text-[10px] text-slate-400 font-bold uppercase">አጠቃላይ የጤንነት ውጤት (Health Score)</div>' +
                  '<div class="text-xl font-black text-emerald-400">' + score + '%</div>' +
                '</div>' +
                '<div class="text-right text-[11px] space-y-0.5">' +
                  '<div>ሞተር: <span class="px-1.5 py-0.5 rounded bg-emerald-600/30 text-emerald-300 font-bold text-[10px]">' + esc(an.engine_grade || "A") + '</span></div>' +
                  '<div>ትራንስሚሽን: <span class="px-1.5 py-0.5 rounded bg-emerald-600/30 text-emerald-300 font-bold text-[10px]">' + esc(an.transmission_grade || "A") + '</span></div>' +
                '</div>' +
              '</div>' +
              '<div class="p-2.5 rounded-2xl bg-amber-50 border border-amber-200">' +
                '<div class="text-[10px] font-bold text-amber-800 uppercase">የተገመተ የጥገና ወጪ (Estimated Repairs)</div>' +
                '<div class="text-base font-black text-amber-900">' + Number(repCost).toLocaleString() + ' ETB</div>' +
              '</div>' +
              (faults.length > 0 ? 
                '<div class="space-y-1">' +
                  '<div class="font-bold text-slate-800 text-[11px]">የተለዩ የጥገና ክፍሎች:</div>' +
                  faults.map(function(f){
                    var comp = typeof f === "object" ? (f.component || "የተለየ ክፍል") : String(f);
                    var sev = typeof f === "object" ? (f.severity || "Med") : "Med";
                    var descText = typeof f === "object" ? (f.description || "") : "";
                    var cost = typeof f === "object" && f.estimated_cost_etb ? Number(f.estimated_cost_etb).toLocaleString() + ' ETB' : '';
                    return '<div class="p-2 bg-white rounded-xl border border-slate-100 flex items-center justify-between text-[11px]">' +
                      '<div><span class="font-bold text-slate-800">' + esc(comp) + '</span> <span class="text-[9px] px-1 py-0.2 rounded ' + (sev === "High" ? "bg-rose-100 text-rose-700" : "bg-amber-100 text-amber-700") + '">' + esc(sev) + '</span>' + (descText ? '<div class="text-[10px] text-slate-500">' + esc(descText) + '</div>' : '') + '</div>' +
                      (cost ? '<div class="font-bold text-slate-700 shrink-0 text-right">' + cost + '</div>' : '') +
                    '</div>';
                  }).join('') +
                '</div>' : '') +
              (advice ? 
                '<div class="p-2.5 bg-emerald-50 rounded-2xl border border-emerald-200 text-slate-800 text-[11px] leading-relaxed">' +
                  '<div class="font-bold text-emerald-800 mb-0.5">💡 የዋጋ መደራደሪያ ምክር:</div>' +
                  '<div>' + esc(advice) + '</div>' +
                '</div>' : '') +
              adikaAdvisorCtaHtml(carModel, (advice ? advice : '') + (repCost ? (' | ጥገና ~' + Number(repCost).toLocaleString() + ' ETB') : '')) +
            '</div>';
        })
        .catch(function(){ resEl.innerHTML = '<div class="p-2 bg-rose-50 text-rose-700 rounded-xl text-xs">ትንተናውን ማጠናቀቅ አልተቻለም።</div>'; });
      });
    };

    // Chassis / VIN Verification Action Handlers
    document.querySelectorAll(".vin-sample-chip").forEach(function(btn) {
      btn.onclick = function() {
        var v = btn.getAttribute("data-vin");
        var inp = document.getElementById("chassisInput");
        if (inp) {
          inp.value = v;
          inp.focus();
        }
      };
    });

    if (document.getElementById("chassisVerifyBtn")) {
      document.getElementById("chassisVerifyBtn").onclick = function() {
        var inp = document.getElementById("chassisInput");
        var vin = (inp ? inp.value : "").trim().toUpperCase();
        var resEl = document.getElementById("chassisResult");
        if (!resEl) return;
        if (!vin || vin.length < 5) {
          resEl.classList.remove("hidden");
          resEl.innerHTML = '<div class="p-3 bg-rose-50 border border-rose-200 rounded-2xl text-rose-800 text-xs font-bold">⚠️ እባክዎን ትክክለኛ የሻሲ ቁጥር ያስገቡ (ቢያንስ 5 ፊደላት/ቁጥሮች)።</div>';
          return;
        }
        resEl.classList.remove("hidden");
        resEl.innerHTML = '<div class="p-4 bg-slate-50 border border-slate-200 rounded-2xl text-slate-600 text-xs text-center font-medium">⏳ የሻሲ ቁጥሩ በኦፊሴላዊ የፋብሪካ ዳታቤዝ እየተረጋገጠ ነው...</div>';

        fetch("/api/verify-chassis", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ vin: vin })
        })
        .then(function(r){ return r.json(); })
        .then(function(res){
          if (res.status !== "success" || !res.data) {
            resEl.innerHTML = '<div class="p-3 bg-rose-50 border border-rose-200 rounded-2xl text-rose-800 text-xs font-semibold">' + esc(res.message || "የሻሲ ቁጥሩን ማረጋገጥ አልተቻለም።") + '</div>';
            return;
          }
          var d = res.data;
          var sp = d.specs || {};
          resEl.innerHTML =
            '<div class="space-y-3 text-xs">' +
              '<div class="p-3 bg-slate-900 text-white rounded-2xl flex items-center justify-between shadow-md">' +
                '<div>' +
                  '<div class="text-[10px] text-emerald-400 font-extrabold uppercase tracking-wide flex items-center gap-1"><span>✓</span><span>' + esc(d.badge || "Official Specs Verified") + '</span></div>' +
                  '<div class="text-sm font-black text-white mt-0.5">' + esc((sp.make || "") + " " + (sp.model || "")) + '</div>' +
                  '<div class="text-[10px] text-slate-400 font-mono">' + esc(sp.vin || vin) + '</div>' +
                '</div>' +
                '<div class="text-right">' +
                  '<span class="px-2 py-1 rounded-xl bg-emerald-500/20 text-emerald-300 font-black text-[11px] border border-emerald-500/40">' + esc(sp.year || "2020") + '</span>' +
                '</div>' +
              '</div>' +
              '<div class="grid grid-cols-2 gap-2 bg-slate-50 p-3 rounded-2xl border border-slate-200 text-[11px]">' +
                '<div><span class="text-slate-400 text-[10px] block">አምራች / Make:</span><span class="font-bold text-slate-800">' + esc(sp.make || "Toyota") + '</span></div>' +
                '<div><span class="text-slate-400 text-[10px] block">ሞዴል / Model:</span><span class="font-bold text-slate-800">' + esc(sp.model || "Vitz") + '</span></div>' +
                '<div><span class="text-slate-400 text-[10px] block">የምርት ዘመን / Year:</span><span class="font-bold text-slate-800">' + esc(sp.year || "2018") + '</span></div>' +
                '<div><span class="text-slate-400 text-[10px] block">የትውልድ አገር / Country:</span><span class="font-bold text-slate-800">' + esc(sp.country || "Japan") + '</span></div>' +
                '<div><span class="text-slate-400 text-[10px] block">ሞተር / Engine:</span><span class="font-bold text-slate-800">' + esc(sp.engine || "1.3L VVT-i") + '</span></div>' +
                '<div><span class="text-slate-400 text-[10px] block">ነዳጅ / Fuel:</span><span class="font-bold text-slate-800">' + esc(sp.fuel_type || "Benzine") + '</span></div>' +
                '<div><span class="text-slate-400 text-[10px] block">ማርሽ / Transmission:</span><span class="font-bold text-slate-800">' + esc(sp.transmission || "Automatic") + '</span></div>' +
                '<div><span class="text-slate-400 text-[10px] block">ቦዲ / Body Style:</span><span class="font-bold text-slate-800">' + esc(sp.body_style || "Hatchback") + '</span></div>' +
                '<div class="col-span-2"><span class="text-slate-400 text-[10px] block">የመገጣጠሚያ ፋብሪካ / Assembly:</span><span class="font-bold text-slate-800">' + esc(sp.assembly || "Official Assembly Plant") + '</span></div>' +
                '<div class="col-span-2"><span class="text-slate-400 text-[10px] block">የህጋዊነት ደረጃ / Legal Status:</span><span class="font-bold text-emerald-700 flex items-center gap-1"><span>🛡️</span><span>' + esc(sp.legal_status || "Clean Title / Registered Libre Match") + '</span></span></div>' +
              '</div>' +
              (d.details_amharic ?
                '<div class="p-3 bg-emerald-50 rounded-2xl border border-emerald-200 text-slate-800 text-[11px] leading-relaxed">' +
                  '<div class="font-bold text-emerald-900 mb-0.5">ℹ️ የማረጋገጫ ማጠቃለያ:</div>' +
                  '<div>' + esc(d.details_amharic) + '</div>' +
                '</div>' : '') +
              adikaAdvisorCtaHtml(((sp.make || "") + " " + (sp.model || "")).trim() || vin) +
            '</div>';
        })
        .catch(function(){
          resEl.innerHTML = '<div class="p-3 bg-rose-50 border border-rose-200 rounded-2xl text-rose-800 text-xs">የኔትወርክ ስህተት አጋጥሟል። እባክዎ እንደገና ይሞክሩ።</div>';
        });
      };
    }

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
      state.chassisOnly = false;
      var fChip = document.getElementById("filterChassisChip");
      if (fChip) {
        fChip.className = "cat-pill px-3 py-1 rounded-full text-xs font-bold whitespace-nowrap transition-all bg-emerald-500/25 text-white hover:bg-emerald-500/35 border border-emerald-300/40";
      }
      filterBanner.classList.add("hidden");
      selectCategory("");
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



    // ========== Digital Cadastral Map Verifier — Photo-only multi-stage QR ==========
    (function initLandMapVerifier() {
      var CADASTRE_VERIFY = "https://land.addiscadaster.gov.et/verify";
      var CADASTRE_SEARCH = "https://land.addiscadaster.gov.et/search";
      var lastExtract = null;

      function showPanel(name) {
        ["landMapUploadPanel", "landMapScanPanel", "landMapResultPanel"].forEach(function(id) {
          var el = document.getElementById(id);
          if (el) el.classList.toggle("hidden", id !== name);
        });
        var retry = document.getElementById("landMapRetryBox");
        if (retry) retry.classList.add("hidden");
      }

      function showRetryOnly() {
        showPanel("landMapUploadPanel");
        var retry = document.getElementById("landMapRetryBox");
        if (retry) retry.classList.remove("hidden");
      }

      function saveForContract(extract) {
        lastExtract = extract || lastExtract;
        if (!lastExtract) return;
        try {
          localStorage.setItem("adika_land_map_last", JSON.stringify(lastExtract));
          var draft = {};
          try { draft = JSON.parse(localStorage.getItem("adika_contract_draft_v2") || "{}") || {}; } catch (e) {}
          draft.contract_type = (draft.contract_type && String(draft.contract_type).indexOf("house") >= 0)
            ? draft.contract_type : "house_sale";
          draft.property_info = draft.property_info || {};
          if (lastExtract.upin) draft.property_info.title_deed = lastExtract.upin;
          if (lastExtract.cert) draft.property_info.title_deed = lastExtract.cert || lastExtract.upin;
          if (lastExtract.area) draft.property_info.area_sqm = String(lastExtract.area).replace(/[^\d.]/g, "");
          if (lastExtract.sub_city) draft.property_info.sub_city = lastExtract.sub_city;
          if (lastExtract.name) {
            draft.seller_info = draft.seller_info || {};
            draft.seller_info.name = lastExtract.name;
          }
          localStorage.setItem("adika_contract_draft_v2", JSON.stringify(draft));
        } catch (e) {}
      }

      function openOfficialUrl(url) {
        if (!url) return false;
        url = String(url).trim();
        try {
          if (window.Telegram && Telegram.WebApp && typeof Telegram.WebApp.openLink === "function") {
            Telegram.WebApp.openLink(url);
            return true;
          }
        } catch (e0) {}
        try {
          if (typeof tg !== "undefined" && tg && typeof tg.openLink === "function") {
            tg.openLink(url);
            return true;
          }
        } catch (e1) {}
        try {
          window.open(url, "_blank", "noopener,noreferrer");
          return true;
        } catch (e2) {
          try { window.location.href = url; } catch (e3) {}
          return false;
        }
      }

      function redirectWithExtract(extract) {
        extract = extract || {};
        // Prefer raw / url / upin string through universal decoder
        var candidates = [
          extract.url,
          extract.raw,
          extract.upin,
          extract.cert,
          extract.plot
        ];
        for (var i = 0; i < candidates.length; i++) {
          if (candidates[i] && handleParsedLandPayload(candidates[i])) {
            try {
              showPanel("landMapUploadPanel");
              var retry = document.getElementById("landMapRetryBox");
              if (retry) retry.classList.add("hidden");
            } catch (e) {}
            return;
          }
        }
        // Compose from fields
        if (extract.upin) {
          if (handleParsedLandPayload(String(extract.upin))) return;
        }
        showRetryOnly();
      }


      function buildOfficialUrl(extract) {
        extract = extract || {};
        if (extract.url && /^https?:\/\//i.test(extract.url)) return extract.url;
        var upin = (extract.upin || "").trim();
        var cert = (extract.cert || "").trim();
        if (upin) return CADASTRE_VERIFY + "?upin=" + encodeURIComponent(upin);
        if (cert) return CADASTRE_SEARCH + "?q=" + encodeURIComponent(cert);
        return null;
      }

      function parseQrPayload(raw) {
        var out = { upin: "", cert: "", name: "", area: "", sub_city: "", url: "", raw: raw || "" };
        if (!raw) return out;
        var s = String(raw).trim();
        if (/^https?:\/\//i.test(s)) {
          out.url = s;
          try {
            var u = new URL(s);
            out.upin = u.searchParams.get("upin") || u.searchParams.get("UPIN") || u.searchParams.get("id") || "";
            out.cert = u.searchParams.get("cert") || u.searchParams.get("certificate") || "";
          } catch (e) {}
          // path segment fallback e.g. /verify/AA0009...
          if (!out.upin) {
            var m = s.match(/\b(AA\d{8,})\b/i);
            if (m) out.upin = m[1];
          }
          return out;
        }
        try {
          if (s.charAt(0) === "{") {
            var j = JSON.parse(s);
            out.upin = j.upin || j.UPIN || j.parcel_id || "";
            out.cert = j.certificate || j.cert_no || "";
            out.name = j.owner || j.name || "";
            out.url = j.url || j.verify_url || j.link || "";
            return out;
          }
        } catch (e2) {}
        try {
          var q = s.indexOf("?") >= 0 ? s.split("?")[1] : s;
          q.split("&").forEach(function(pair) {
            var kv = pair.split("=");
            if (kv.length < 2) return;
            var k = decodeURIComponent(kv[0] || "").toLowerCase();
            var v = decodeURIComponent((kv[1] || "").replace(/\+/g, " "));
            if (k.indexOf("upin") >= 0 || k === "id") out.upin = v;
            if (k.indexOf("cert") >= 0) out.cert = v;
            if (k.indexOf("url") >= 0 || k.indexOf("link") >= 0) out.url = v;
          });
        } catch (e3) {}
        var up = s.match(/\b(AA\d{8,})\b/i);
        if (up && !out.upin) out.upin = up[1];
        var cert = s.match(/\b(ETH[\d\-]{8,})\b/i);
        if (cert && !out.cert) out.cert = cert[1];
        // bare AA code as entire payload
        if (!out.upin && /^AA\d{8,}$/i.test(s)) out.upin = s;
        return out;
      }

      function tryJsQR(imageData) {
        if (typeof jsQR !== "function") return null;
        try {
          var code = jsQR(imageData.data, imageData.width, imageData.height, { inversionAttempts: "attemptBoth" });
          return code && code.data ? code.data : null;
        } catch (e) {
          return null;
        }
      }

      function getImageData(canvas) {
        return canvas.getContext("2d").getImageData(0, 0, canvas.width, canvas.height);
      }

      function toGrayscaleContrast(ctx, w, h, contrast) {
        var imgData = ctx.getImageData(0, 0, w, h);
        var d = imgData.data;
        var c = contrast || 1.35;
        var intercept = 128 * (1 - c);
        for (var i = 0; i < d.length; i += 4) {
          var g = 0.299 * d[i] + 0.587 * d[i + 1] + 0.114 * d[i + 2];
          g = g * c + intercept;
          if (g < 0) g = 0;
          if (g > 255) g = 255;
          // mild threshold boost for QR modules
          if (g > 160) g = 255;
          else if (g < 90) g = 0;
          d[i] = d[i + 1] = d[i + 2] = g;
        }
        ctx.putImageData(imgData, 0, 0);
        return imgData;
      }

      function sharpen(ctx, w, h) {
        var weights = [0, -1, 0, -1, 5, -1, 0, -1, 0];
        var src = ctx.getImageData(0, 0, w, h);
        var dst = ctx.createImageData(w, h);
        var s = src.data, d = dst.data;
        for (var y = 1; y < h - 1; y++) {
          for (var x = 1; x < w - 1; x++) {
            for (var ch = 0; ch < 3; ch++) {
              var sum = 0;
              var wi = 0;
              for (var ky = -1; ky <= 1; ky++) {
                for (var kx = -1; kx <= 1; kx++) {
                  var idx = ((y + ky) * w + (x + kx)) * 4 + ch;
                  sum += s[idx] * weights[wi++];
                }
              }
              d[(y * w + x) * 4 + ch] = Math.max(0, Math.min(255, sum));
            }
            d[(y * w + x) * 4 + 3] = 255;
          }
        }
        ctx.putImageData(dst, 0, 0);
        return dst;
      }

      function drawScaled(img, maxW) {
        var canvas = document.createElement("canvas");
        var scale = img.width > maxW ? maxW / img.width : 1;
        // also upscale tiny images
        if (img.width < 400) scale = 800 / Math.max(img.width, 1);
        canvas.width = Math.max(1, Math.floor(img.width * scale));
        canvas.height = Math.max(1, Math.floor(img.height * scale));
        var ctx = canvas.getContext("2d");
        ctx.imageSmoothingEnabled = true;
        ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
        return { canvas: canvas, ctx: ctx };
      }

      function cropRegion(srcCanvas, xRatio, yRatio, wRatio, hRatio, outMax) {
        var sx = Math.floor(srcCanvas.width * xRatio);
        var sy = Math.floor(srcCanvas.height * yRatio);
        var sw = Math.floor(srcCanvas.width * wRatio);
        var sh = Math.floor(srcCanvas.height * hRatio);
        var canvas = document.createElement("canvas");
        var scale = outMax / Math.max(sw, sh);
        if (scale < 1) scale = 1;
        if (scale > 3) scale = 3;
        canvas.width = Math.max(1, Math.floor(sw * scale));
        canvas.height = Math.max(1, Math.floor(sh * scale));
        var ctx = canvas.getContext("2d");
        ctx.imageSmoothingEnabled = false;
        ctx.drawImage(srcCanvas, sx, sy, sw, sh, 0, 0, canvas.width, canvas.height);
        return { canvas: canvas, ctx: ctx };
      }

      function extractUpinFromPixelsHeuristic(imageData) {
        // Extremely lightweight: not true OCR — rely on QR primarily.
        // Placeholder for pattern if we had OCR; returns null here.
        return null;
      }

      function hardBinarize(ctx, w, h, threshold) {
        var thr = threshold == null ? 128 : threshold;
        var imgData = ctx.getImageData(0, 0, w, h);
        var d = imgData.data;
        for (var i = 0; i < d.length; i += 4) {
          var g = 0.299 * d[i] + 0.587 * d[i + 1] + 0.114 * d[i + 2];
          var v = g >= thr ? 255 : 0;
          d[i] = d[i + 1] = d[i + 2] = v;
          d[i + 3] = 255;
        }
        ctx.putImageData(imgData, 0, 0);
        return imgData;
      }

      function handleParsedLandPayload(payload) {
        if (payload == null || payload === "") return false;
        var decodedText = String(payload).trim();
        try { console.log("[Adika Digital System] Raw QR Output:", decodedText); } catch (e0) {}

        // Case 1: Standard URL (female title deed style)
        if (/^https?:\/\//i.test(decodedText)) {
          openOfficialUrl(decodedText);
          try { saveForContract({ url: decodedText, raw: decodedText }); } catch (e) {}
          return true;
        }

        // Case 1b: URL embedded inside longer text / JSON string
        var urlInText = decodedText.match(/https?:\/\/[^\s\"'<>]+/i);
        if (urlInText) {
          openOfficialUrl(urlInText[0]);
          try { saveForContract({ url: urlInText[0], raw: decodedText }); } catch (e) {}
          return true;
        }

        // Case 2: JSON object payload
        try {
          if (decodedText.charAt(0) === "{" || decodedText.charAt(0) === "[") {
            var j = JSON.parse(decodedText);
            if (Array.isArray(j)) j = j[0] || {};
            var jUrl = j.url || j.verify_url || j.link || j.href || "";
            var jUpin = j.upin || j.UPIN || j.parcel_id || j.plot || j.code || j.id || "";
            if (jUrl && /^https?:\/\//i.test(String(jUrl))) {
              openOfficialUrl(String(jUrl));
              try { saveForContract({ url: jUrl, upin: jUpin, raw: decodedText }); } catch (e) {}
              return true;
            }
            if (jUpin) {
              openOfficialUrl(CADASTRE_VERIFY + "?upin=" + encodeURIComponent(String(jUpin).trim()));
              try { saveForContract({ upin: String(jUpin).trim(), raw: decodedText }); } catch (e) {}
              return true;
            }
          }
        } catch (eJson) {}

        // Case 3: Raw UPIN / plot code (male cadastral style e.g. AA00091305321)
        var upinMatch =
          decodedText.match(/\b(AA\d{8,})\b/i) ||
          decodedText.match(/\b(KK\d{8,})\b/i) ||
          decodedText.match(/\b(LTP[-_]?[A-Z0-9\-]+)\b/i) ||
          decodedText.match(/\b([A-Z]{1,4}\d{8,15})\b/i) ||
          decodedText.match(/([A-Z0-9]{8,20})/i);
        if (upinMatch) {
          var extractedUpin = upinMatch[1] || upinMatch[0];
          extractedUpin = String(extractedUpin).trim();
          var cadastralUrl = CADASTRE_VERIFY + "?upin=" + encodeURIComponent(extractedUpin);
          openOfficialUrl(cadastralUrl);
          try { saveForContract({ upin: extractedUpin, raw: decodedText }); } catch (e) {}
          return true;
        }

        // Case 4: query-string style without host (upin=AA...&...)
        var qs = decodedText.match(/(?:upin|plot|id|code)\s*[=:]\s*([A-Z0-9\-]+)/i);
        if (qs) {
          openOfficialUrl(CADASTRE_VERIFY + "?upin=" + encodeURIComponent(qs[1]));
          try { saveForContract({ upin: qs[1], raw: decodedText }); } catch (e) {}
          return true;
        }

        // Last resort: open default plot lookup with whole payload (no alert)
        if (decodedText.length >= 6) {
          openOfficialUrl("https://e-services.addisababa.gov.et/land/verify?plot=" + encodeURIComponent(decodedText));
          try { saveForContract({ raw: decodedText }); } catch (e) {}
          return true;
        }
        return false;
      }


      function multiStageScan(img, cb) {
        var found = null;
        var t0 = (typeof performance !== "undefined" && performance.now) ? performance.now() : Date.now();
        try {
          var srcW = img.naturalWidth || img.width;
          var srcH = img.naturalHeight || img.height;
          if (!srcW || !srcH) { cb(null); return; }

          // Zone 1 Top-Right | Zone 2 Mid-Right | Zone 3 Top-Left | Zone 4 handled as full downscale
          var zones = [
            [0.50, 0.00, 0.50, 0.35],
            [0.50, 0.25, 0.50, 0.35],
            [0.00, 0.00, 0.50, 0.35]
          ];
          var thresholds = [128, 110, 145];

          function scanZone(sx, sy, sw, sh, scaleUp) {
            if (found) return;
            sw = Math.max(1, sw); sh = Math.max(1, sh);
            var crop = document.createElement("canvas");
            crop.width = sw; crop.height = sh;
            var cctx = crop.getContext("2d", { willReadFrequently: true });
            cctx.imageSmoothingEnabled = false;
            cctx.drawImage(img, sx, sy, sw, sh, 0, 0, sw, sh);

            var up = document.createElement("canvas");
            var sc = scaleUp || 2;
            up.width = Math.max(1, Math.floor(sw * sc));
            up.height = Math.max(1, Math.floor(sh * sc));
            var uctx = up.getContext("2d", { willReadFrequently: true });
            uctx.imageSmoothingEnabled = false;
            uctx.drawImage(crop, 0, 0, up.width, up.height);

            for (var ti = 0; ti < thresholds.length && !found; ti++) {
              var trial = document.createElement("canvas");
              trial.width = up.width; trial.height = up.height;
              var tctx = trial.getContext("2d", { willReadFrequently: true });
              tctx.imageSmoothingEnabled = false;
              tctx.drawImage(up, 0, 0);
              var id = tctx.getImageData(0, 0, trial.width, trial.height);
              var d = id.data;
              var contrast = 1.65;
              var intercept = 128 * (1 - contrast);
              var thr = thresholds[ti];
              for (var i = 0; i < d.length; i += 4) {
                // suppress blue/purple stamp bias (lower blue channel weight)
                var g = 0.35 * d[i] + 0.50 * d[i + 1] + 0.15 * d[i + 2];
                g = g * contrast + intercept;
                var v = g >= thr ? 255 : 0;
                d[i] = d[i + 1] = d[i + 2] = v;
                d[i + 3] = 255;
              }
              tctx.putImageData(id, 0, 0);
              found = tryJsQR(id);
            }
          }

          for (var zi = 0; zi < zones.length && !found; zi++) {
            var z = zones[zi];
            var sx = Math.floor(srcW * z[0]);
            var sy = Math.floor(srcH * z[1]);
            var sw = Math.floor(srcW * z[2]);
            var sh = Math.floor(srcH * z[3]);
            scanZone(sx, sy, sw, sh, 2);
          }

          // Zone 4: full image downscaled fallback
          if (!found) {
            var maxW = 900;
            var scale = srcW > maxW ? maxW / srcW : 1;
            var fw = Math.max(1, Math.floor(srcW * scale));
            var fh = Math.max(1, Math.floor(srcH * scale));
            var full = document.createElement("canvas");
            full.width = fw; full.height = fh;
            var fctx = full.getContext("2d", { willReadFrequently: true });
            fctx.imageSmoothingEnabled = true;
            fctx.drawImage(img, 0, 0, fw, fh);
            var fid = fctx.getImageData(0, 0, fw, fh);
            var fd = fid.data;
            for (var j = 0; j < fd.length; j += 4) {
              var g2 = 0.35 * fd[j] + 0.50 * fd[j + 1] + 0.15 * fd[j + 2];
              var v2 = g2 >= 128 ? 255 : 0;
              fd[j] = fd[j + 1] = fd[j + 2] = v2;
            }
            fctx.putImageData(fid, 0, 0);
            found = tryJsQR(fid);
          }
        } catch (e) {
          found = null;
        }
        var t1 = (typeof performance !== "undefined" && performance.now) ? performance.now() : Date.now();
        try { console.log("[Adika Digital System] 4-zone ms:", Math.round(t1 - t0), found ? "ok" : "miss"); } catch (e2) {}
        cb(found);
      }

      function extractCodesFromText(txt) {
        var out = { upin: "", cert: "", name: "", area: "", sub_city: "", url: "" };
        if (!txt) return out;
        var s = String(txt);
        // UPIN / Plot codes used on AA certificates
        var up =
          s.match(/\b(AA\d{9,14})\b/i) ||
          s.match(/\b(KK\d{9,14})\b/i) ||
          s.match(/\b(LTP[-_]?KK[\d\-]+)\b/i) ||
          s.match(/\b(LTP[-_][A-Z]{0,4}\d[\d\-]+)\b/i);
        if (up) out.upin = up[1].toUpperCase();
        var cert = s.match(/\b(ETH[\d\-]{8,})\b/i);
        if (cert) out.cert = cert[1].toUpperCase();
        var area = s.match(/(\d{2,5}(?:[.,]\d{1,3})?)\s*(m²|m2|sq\.?\s*m)/i);
        if (area) out.area = area[1].replace(",", ".") + " m²";
        var nameM =
          s.match(/(?:Full\s*Name|Owner|የባለይዞታው\s*ሙሉ\s*ስም|ሙሉ\s*ስም)\s*[:：\-]?\s*([A-Za-z\u1200-\u137F\s]{5,50})/i);
        if (nameM) out.name = nameM[1].replace(/\s+/g, " ").trim();
        var cities = [
          ["Addis Ketema", "አዲስ ከተማ"], ["Kolfe", "ኮልፌ ቀራንዮ"], ["Bole", "ቦሌ"],
          ["Arada", "አራዳ"], ["Yeka", "የካ"], ["Lideta", "ልደታ"], ["Kirkos", "ቂርቆስ"],
          ["Gullele", "ጉለሌ"], ["Nifas", "ንፋስ ስልክ ላፍቶ"], ["Akaki", "አቃቂ ቃሊቲ"], ["Lemi", "ሌሚ ኩራ"]
        ];
        for (var i = 0; i < cities.length; i++) {
          if (s.toLowerCase().indexOf(cities[i][0].toLowerCase()) >= 0 || s.indexOf(cities[i][1]) >= 0) {
            out.sub_city = cities[i][1];
            break;
          }
        }
        var urlM = s.match(/https?:\/\/[^\s\"']+addiscadaster[^\s\"']+/i) ||
                   s.match(/https?:\/\/[^\s\"']+land\.[^\s\"']+/i);
        if (urlM) out.url = urlM[0];
        return out;
      }

      function runTesseractOCR(dataUrl, cb) {
        function go(Tesseract) {
          try {
            Tesseract.recognize(dataUrl, "eng", {
              logger: function() {}
            }).then(function(res) {
              var text = (res && res.data && res.data.text) || "";
              cb(extractCodesFromText(text));
            }).catch(function() { cb(null); });
          } catch (e) { cb(null); }
        }
        if (window.Tesseract) {
          go(window.Tesseract);
          return;
        }
        // Dynamic load — only on QR failure (cost/latency)
        var s = document.createElement("script");
        s.src = "https://cdn.jsdelivr.net/npm/tesseract.js@5/dist/tesseract.min.js";
        s.onload = function() { go(window.Tesseract); };
        s.onerror = function() { cb(null); };
        document.head.appendChild(s);
      }

      function runBackendOCR(dataUrl, cb) {
        fetch("/api/land-map/ocr", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ image_data: dataUrl })
        })
          .then(function(r) { return r.json(); })
          .then(function(res) {
            if (res && res.success && res.data) cb(res.data);
            else cb(null);
          })
          .catch(function() { cb(null); });
      }

      function processDataUrl(dataUrl) {
        showPanel("landMapScanPanel");
        var prev = document.getElementById("landMapPreview");
        if (prev) prev.src = dataUrl;
        var img = new Image();
        img.onload = function() {
          multiStageScan(img, function(qrRaw) {
            if (qrRaw) {
              var payload = String(qrRaw).trim();
              if (handleParsedLandPayload(payload)) {
                showPanel("landMapUploadPanel");
                return;
              }
              redirectWithExtract(parseQrPayload(payload));
              return;
            }
            // Lightweight miss path: backend OCR only (no slow client OCR by default)
            runBackendOCR(dataUrl, function(serverFields) {
              if (serverFields && (serverFields.upin || serverFields.cert || serverFields.url)) {
                redirectWithExtract(serverFields);
              } else {
                showRetryOnly();
              }
            });
          });
        };
        img.onerror = function() { showRetryOnly(); };
        img.src = dataUrl;
      }

      var fileInput = document.getElementById("landMapFile");
      if (fileInput) {
        fileInput.onchange = function() {
          var f = fileInput.files && fileInput.files[0];
          if (!f) return;
          var retry = document.getElementById("landMapRetryBox");
          if (retry) retry.classList.add("hidden");
          var reader = new FileReader();
          reader.onload = function() { processDataUrl(reader.result); };
          reader.readAsDataURL(f);
        };
      }

      var retryBtn = document.getElementById("landMapRetryBtn");
      if (retryBtn) {
        retryBtn.onclick = function() {
          if (fileInput) {
            fileInput.value = "";
            fileInput.click();
          }
        };
      }

      var resetBtn = document.getElementById("landMapResetBtn");
      if (resetBtn) {
        resetBtn.onclick = function() {
          lastExtract = null;
          if (fileInput) fileInput.value = "";
          showPanel("landMapUploadPanel");
        };
      }

      var toContract = document.getElementById("landMapToContractBtn");
      if (toContract) {
        toContract.onclick = function() {
          saveForContract(lastExtract);
          try { closeModal("landMapModal"); } catch (e) {}
          if (typeof openToolModal === "function") openToolModal("contractModal");
        };
      }

      var shareBtn = document.getElementById("landMapShareBtn");
      if (shareBtn) {
        shareBtn.onclick = function() {
          var url = buildOfficialUrl(lastExtract) || CADASTRE_VERIFY;
          if (navigator.share) {
            navigator.share({ title: "Cadastre Verification", url: url }).catch(function(){});
          } else if (navigator.clipboard) {
            navigator.clipboard.writeText(url);
          } else {
            openOfficialUrl(url);
          }
        };
      }
    })();

    // ========== Contract Wizard (4 types, continuous legal prose) ==========
    (function initContractWizard() {
      var step = 0;
      var draftId = null;
      var SUB_KEY = "adika_contract_draft_v2";

      function val(id) {
        var el = document.getElementById(id);
        return el ? String(el.value || "").trim() : "";
      }
      function setVal(id, v) {
        var el = document.getElementById(id);
        if (el && v != null) el.value = v;
      }
      function parseMoney(s) {
        return Number(String(s || "").replace(/[^0-9.]/g, "")) || 0;
      }
      function fmtMoney(n) {
        return Math.max(0, Math.round(n)).toLocaleString() + " ብር";
      }
      function getContractType() {
        var r = document.querySelector('input[name="cContractType"]:checked');
        return r ? r.value : "vehicle_sale";
      }
      function updateBalance() {
        var total = parseMoney(val("cTotalPrice"));
        var adv = parseMoney(val("cAdvance"));
        var el = document.getElementById("cBalance");
        if (el) el.textContent = fmtMoney(Math.max(0, total - adv));
      }
      function syncTypeUI() {
        var t = getContractType();
        var isVehicle = t.indexOf("vehicle") === 0;
        var isSale = t.indexOf("sale") >= 0;
        var fv = document.getElementById("cFieldsVehicle");
        var fh = document.getElementById("cFieldsHouse");
        var fs = document.getElementById("cFinSale");
        var fr = document.getElementById("cFinRental");
        if (fv) fv.classList.toggle("hidden", !isVehicle);
        if (fh) fh.classList.toggle("hidden", isVehicle);
        if (fs) fs.classList.toggle("hidden", !isSale);
        if (fr) fr.classList.toggle("hidden", isSale);
        var a = document.getElementById("cPartyALabel");
        var b = document.getElementById("cPartyBLabel");
        if (a) a.textContent = isSale ? "ውል ሰጪ (ሻጭ)" : "አከራይ";
        if (b) b.textContent = isSale ? "ውል ተቀባይ (ገዢ)" : "ተከራይ";
        document.querySelectorAll(".c-type-opt").forEach(function(lab) {
          var inp = lab.querySelector("input");
          if (!inp) return;
          if (inp.checked) {
            lab.className = "c-type-opt flex items-center gap-2 p-3 rounded-xl border-2 border-[#16acbd] bg-[#16acbd]/5 cursor-pointer";
          } else {
            lab.className = "c-type-opt flex items-center gap-2 p-3 rounded-xl border border-slate-200 bg-white cursor-pointer";
          }
        });
      }
      function collectPayload(status) {
        var userId = (tg && tg.initDataUnsafe && tg.initDataUnsafe.user && tg.initDataUnsafe.user.id) || 0;
        var ctype = getContractType();
        return {
          contract_id: draftId,
          user_id: userId,
          contract_type: ctype,
          contract_status: status || "Draft",
          seller_info: {
            name: val("cSellerName"),
            nationality: val("cSellerNationality") || "ኢትዮጵያዊ",
            phone: val("cSellerPhone"),
            sub_city: val("cSellerSubCity"),
            woreda: val("cSellerWoreda"),
            house_no: val("cSellerHouseNo")
          },
          buyer_info: {
            name: val("cBuyerName"),
            nationality: val("cBuyerNationality") || "ኢትዮጵያዊ",
            phone: val("cBuyerPhone"),
            sub_city: val("cBuyerSubCity"),
            woreda: val("cBuyerWoreda"),
            house_no: val("cBuyerHouseNo")
          },
          vehicle_info: {
            plate: val("cPlate"),
            chassis: val("cChassis"),
            engine: val("cEngine"),
            model: val("cCarModel")
          },
          property_info: {
            sub_city: val("cHouseSubCity"),
            woreda: val("cHouseWoreda"),
            house_no: val("cHouseNo"),
            title_deed: val("cTitleDeed"),
            area_sqm: val("cAreaSqm"),
            use_type: val("cHouseUse")
          },
          financial_info: {
            total_price: parseMoney(val("cTotalPrice")),
            advance: parseMoney(val("cAdvance")),
            balance: Math.max(0, parseMoney(val("cTotalPrice")) - parseMoney(val("cAdvance"))),
            deadline: val("cDeadline"),
            rent_rate: parseMoney(val("cRentRate")),
            rent_period: val("cRentPeriod") || "በወር",
            rent_start: val("cRentStart"),
            rent_end: val("cRentEnd"),
            rent_advance_months: val("cRentAdvanceMonths"),
            rent_advance_total: parseMoney(val("cRentAdvanceTotal")),
            penalty: parseMoney(val("cPenalty")),
            contract_date: val("cContractDate")
          },
          witnesses: [
            { name: val("cWit1Name"), nationality: val("cWit1Nat"), phone: val("cWit1Phone"), address: val("cWit1Addr") },
            { name: val("cWit2Name"), nationality: val("cWit2Nat"), phone: val("cWit2Phone"), address: val("cWit2Addr") },
            { name: val("cWit3Name"), nationality: val("cWit3Nat"), phone: val("cWit3Phone"), address: val("cWit3Addr") }
          ]
        };
      }
      function showStep(n) {
        step = n;
        [0,1,2,3].forEach(function(i) {
          var panel = document.getElementById("contractStep" + i);
          if (panel) panel.classList.toggle("hidden", i !== n);
        });
        document.querySelectorAll(".contract-step-tab").forEach(function(btn) {
          var s = Number(btn.getAttribute("data-step"));
          btn.className = s === n
            ? "contract-step-tab py-1.5 rounded-lg text-[9px] font-extrabold transition-all bg-white text-[#0e7490] shadow-sm"
            : "contract-step-tab py-1.5 rounded-lg text-[9px] font-extrabold transition-all text-slate-500";
        });
        var prev = document.getElementById("cStepPrev");
        var next = document.getElementById("cStepNext");
        if (prev) prev.classList.toggle("hidden", n <= 0);
        if (next) next.classList.toggle("hidden", n >= 3);
        syncTypeUI();
        try { localStorage.setItem(SUB_KEY, JSON.stringify(collectPayload("Draft"))); } catch (e) {}
      }
      function restoreDraft() {
        try {
          var raw = localStorage.getItem(SUB_KEY);
          if (!raw) return;
          var d = JSON.parse(raw);
          if (!d) return;
          draftId = d.contract_id || null;
          if (d.contract_type) {
            var r = document.querySelector('input[name="cContractType"][value="' + d.contract_type + '"]');
            if (r) r.checked = true;
          }
          var s = d.seller_info || {}, b = d.buyer_info || {}, v = d.vehicle_info || {}, p = d.property_info || {}, f = d.financial_info || {};
          setVal("cSellerName", s.name); setVal("cSellerNationality", s.nationality); setVal("cSellerPhone", s.phone);
          setVal("cSellerSubCity", s.sub_city); setVal("cSellerWoreda", s.woreda); setVal("cSellerHouseNo", s.house_no);
          setVal("cBuyerName", b.name); setVal("cBuyerNationality", b.nationality); setVal("cBuyerPhone", b.phone);
          setVal("cBuyerSubCity", b.sub_city); setVal("cBuyerWoreda", b.woreda); setVal("cBuyerHouseNo", b.house_no);
          setVal("cPlate", v.plate); setVal("cChassis", v.chassis); setVal("cEngine", v.engine); setVal("cCarModel", v.model);
          setVal("cHouseSubCity", p.sub_city); setVal("cHouseWoreda", p.woreda); setVal("cHouseNo", p.house_no);
          setVal("cTitleDeed", p.title_deed); setVal("cAreaSqm", p.area_sqm); setVal("cHouseUse", p.use_type);
          setVal("cTotalPrice", f.total_price); setVal("cAdvance", f.advance); setVal("cDeadline", f.deadline);
          setVal("cRentRate", f.rent_rate); setVal("cRentPeriod", f.rent_period); setVal("cRentStart", f.rent_start);
          setVal("cRentEnd", f.rent_end); setVal("cRentAdvanceMonths", f.rent_advance_months);
          setVal("cRentAdvanceTotal", f.rent_advance_total); setVal("cPenalty", f.penalty); setVal("cContractDate", f.contract_date);
          var w = d.witnesses || [];
          for (var i = 0; i < 3; i++) {
            var wi = w[i] || {};
            setVal("cWit" + (i+1) + "Name", wi.name);
            setVal("cWit" + (i+1) + "Nat", wi.nationality);
            setVal("cWit" + (i+1) + "Phone", wi.phone);
            setVal("cWit" + (i+1) + "Addr", wi.address);
          }
          updateBalance();
          syncTypeUI();
        } catch (e) {}
      }

      document.querySelectorAll(".contract-step-tab").forEach(function(btn) {
        btn.onclick = function() { showStep(Number(btn.getAttribute("data-step")) || 0); };
      });
      document.querySelectorAll('input[name="cContractType"]').forEach(function(r) {
        r.onchange = function() { syncTypeUI(); };
      });
      var prevBtn = document.getElementById("cStepPrev");
      var nextBtn = document.getElementById("cStepNext");
      if (prevBtn) prevBtn.onclick = function() { showStep(Math.max(0, step - 1)); };
      if (nextBtn) nextBtn.onclick = function() { showStep(Math.min(3, step + 1)); };
      ["cTotalPrice", "cAdvance"].forEach(function(id) {
        var el = document.getElementById(id);
        if (el) el.addEventListener("input", updateBalance);
      });

      var libreFile = document.getElementById("cLibreFile");
      if (libreFile) {
        libreFile.onchange = function() {
          var f = libreFile.files && libreFile.files[0];
          if (!f) return;
          var st = document.getElementById("cLibreStatus");
          if (st) { st.classList.remove("hidden"); st.textContent = "⏳ ሊብሬ እየተነበበ ነው..."; }
          var reader = new FileReader();
          reader.onload = function() {
            fetch("/api/contracts/scan-libre", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ image_data: reader.result })
            }).then(function(r) { return r.json(); }).then(function(res) {
              var d = (res && res.data) || {};
              if (d.chassis) setVal("cChassis", d.chassis);
              if (d.engine) setVal("cEngine", d.engine);
              if (d.plate) setVal("cPlate", d.plate);
              if (d.model) setVal("cCarModel", d.model);
              if (st) st.textContent = res.success === false ? ("⚠️ " + (res.message || "OCR")) : "✅ ተሞልቷል — ያረጋግጡ";
            }).catch(function() { if (st) st.textContent = "⚠️ OCR አልተሳካም"; });
          };
          reader.readAsDataURL(f);
        };
      }

      function saveContract(status) {
        return fetch("/api/contracts/save", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(collectPayload(status))
        }).then(function(r) { return r.json(); });
      }

      var saveBtn = document.getElementById("cSaveDraftBtn");
      if (saveBtn) {
        saveBtn.onclick = function() {
          saveBtn.disabled = true;
          saveContract("Draft").then(function(res) {
            if (res.contract_id) draftId = res.contract_id;
            try { localStorage.setItem(SUB_KEY, JSON.stringify(collectPayload("Draft"))); } catch (e) {}
            if (tg && tg.showAlert) tg.showAlert(res.message || "ረቂቅ ተቀምጧል");
            else alert(res.message || "ረቂቅ ተቀምጧል");
          }).catch(function() { alert("ማስቀመጥ አልተቻለም"); })
          .finally(function() { saveBtn.disabled = false; });
        };
      }

      var finBtn = document.getElementById("cFinalizeBtn");
      if (finBtn) {
        finBtn.onclick = function() {
          var p = collectPayload("Finalized");
          if (!p.seller_info.name || !p.buyer_info.name) {
            alert("እባክዎ የተዋዋዮች ስም ይሙሉ");
            showStep(1);
            return;
          }
          finBtn.disabled = true;
          finBtn.textContent = "⏳...";
          saveContract("Finalized").then(function(res) {
            if (res.contract_id) draftId = res.contract_id;
            var result = document.getElementById("contractResult");
            if (result) {
              result.classList.remove("hidden");
              var cid = res.contract_id || draftId || "";
              var pdfUrl = "/api/contracts/" + encodeURIComponent(cid) + "/export-pdf";
              result.innerHTML =
                '<div class="font-black text-slate-800 text-[11px]">✅ ውል ተጠናቋል</div>' +
                '<div class="text-[10px] text-slate-600">#' + esc(String(cid)) + '</div>' +
                '<div class="grid grid-cols-3 gap-1.5 pt-1">' +
                  '<a href="' + pdfUrl + '" target="_blank" class="text-center py-2 rounded-xl bg-slate-900 text-white font-bold text-[10px]">📥 PDF አውርድ</a>' +
                  '<button type="button" id="cPrintBtn" class="py-2 rounded-xl bg-[#16acbd] text-white font-bold text-[10px]">🖨️ ህትመት</button>' +
                  '<button type="button" id="cShareBtn" class="py-2 rounded-xl bg-emerald-600 text-white font-bold text-[10px]">📤 ውል አጋራ</button>' +
                '</div>' +
                '<pre class="mt-2 max-h-48 overflow-y-auto whitespace-pre-wrap text-[10px] bg-white p-2 rounded-lg border leading-relaxed">' + esc(res.contract_text || "") + '</pre>';
              var pb = document.getElementById("cPrintBtn");
              if (pb) pb.onclick = function() {
                window.open(pdfUrl + "?print=1", "_blank");
              };
              var sb = document.getElementById("cShareBtn");
              if (sb) sb.onclick = function() {
                var abs = (window.location.origin || "") + pdfUrl;
                if (navigator.share) {
                  navigator.share({ title: "Adika ውል #" + cid, text: "ህጋዊ ውል — Adika Marketplace", url: abs }).catch(function(){});
                } else if (navigator.clipboard && navigator.clipboard.writeText) {
                  navigator.clipboard.writeText(abs).then(function() {
                    if (tg && tg.showAlert) tg.showAlert("ሊንኩ ተቀድቷል");
                    else alert("ሊንኩ ተቀድቷል");
                  });
                } else {
                  window.open(pdfUrl, "_blank");
                }
              };
            }
            showStep(3);
          }).catch(function() { alert("ውል ማጠናቀቅ አልተቻለም"); })
          .finally(function() { finBtn.disabled = false; finBtn.textContent = "📄 ውል አጠናቅቅ"; });
        };
      }

      var origOpen = window.openToolModal;
      window.openToolModal = function(id) {
        if (typeof origOpen === "function") origOpen(id);
        else {
          var m = document.getElementById(id);
          if (m) { m.classList.remove("hidden"); m.classList.add("flex"); }
        }
        if (id === "contractModal") {
          restoreDraft();
          showStep(0);
          updateBalance();
          syncTypeUI();
        }
      };
      restoreDraft();
      showStep(0);
      updateBalance();
      syncTypeUI();
    })();


    setTabs();
    load(false);
  })();
  </script>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# Streamlit & Python Chat Interface Helper
# ---------------------------------------------------------------------------
try:
    import streamlit as st
except ImportError:
    st = None

try:
    from api_service import generate_advisor_response
except Exception:
    def generate_advisor_response(prompt, history=None, budget=None, system_prompt=None):
        full_prompt = f"System Context: {system_prompt}\nUser Budget: {budget} ETB\nUser Question: {prompt}"
        try:
            from api_service import _gemini_generate
            return _gemini_generate(prompt=full_prompt, api_key=None, system=system_prompt)
        except Exception:
            return "ይቅርታ፣ አሁን ላይ ከኦፕሬተራችን ጋር ማገናኘት አልተቻለም። እባክዎ ጥቂት ቆይተው እንደገና ይሞክሩ።"


def render_chat_interface(user_budget):
    if st is None:
        return
    st.markdown("### 💬 ከአዲካ የፋይናንስ ኦፕሬተር ጋር ይወያዩ")
    
    # 1. State ማስጀመሪያ
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": f"ሰላም! እኔ የ Adika Senior Financial Advisor ነኝ። በያዙት {user_budget:,.0f} ETB በጀት ዙሪያ የሚፈልጉትን ማንኛውንም ጥያቄ መጠየቅ ይችላሉ።"}
        ]

    # 2. የቻት ታሪክ ማሳያ (Scrollable Container)
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])

    # 3. ጥያቄ መቀበያ እና የኤፒአይ ጥሪ
    if prompt := st.chat_input("ጥያቄዎን እዚህ ያስገቡ..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.write(prompt)

        with st.chat_message("assistant"):
            with st.spinner("ኦፕሬተሩ መልስ በመጻፍ ላይ ነው..."):
                response = generate_advisor_response(
                    prompt=prompt, 
                    history=st.session_state.messages, 
                    budget=user_budget
                )
                st.write(response)
                
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()



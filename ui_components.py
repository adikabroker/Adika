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

    <!-- HOME HERO: Document Verify + Digital Advisor (compact dual cards) -->
    <div id="homeHero" class="grid grid-cols-2 gap-2 mb-2.5">
      <button id="heroAdvisorBtn" type="button"
        class="relative overflow-hidden rounded-2xl p-2.5 text-left border border-white/70 shadow-[0_8px_20px_rgba(15,23,42,0.10)] active:scale-[0.98] transition-all"
        style="background:linear-gradient(135deg,rgba(22,172,189,0.92),rgba(14,116,144,0.95));">
        <div class="text-white space-y-1.5">
          <div class="text-base leading-none">💡</div>
          <div class="font-black text-[11px] leading-tight">አዲካ ዲጂታል አማካሪ</div>
          <div class="text-[9px] text-white/85 leading-snug">በጀትዎን ትክክለኛ ግምት</div>
          <span class="inline-flex mt-0.5 px-2 py-0.5 rounded-full bg-white/20 text-[9px] font-bold">ነጻ የገበያ ትንተና →</span>
        </div>
      </button>
      <button id="heroPoaBtn" type="button"
        class="relative overflow-hidden rounded-2xl p-2.5 text-left border border-white/70 shadow-[0_8px_20px_rgba(15,23,42,0.10)] active:scale-[0.98] transition-all"
        style="background:linear-gradient(135deg,rgba(15,23,42,0.92),rgba(30,58,138,0.95));">
        <div class="text-white space-y-1.5">
          <div class="text-base leading-none">📄</div>
          <div class="font-black text-[11px] leading-tight">የሰነድ ማረጋገጫ</div>
          <div class="text-[9px] text-white/85 leading-snug">የውክልና ሰነድ ዲጂታል ማጣሪያ</div>
          <span class="inline-flex mt-0.5 px-2 py-0.5 rounded-full bg-white/20 text-[9px] font-bold">አሁን ያረጋግጡ →</span>
        </div>
      </button>
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


  <!-- DEDICATED ANALYSIS DASHBOARD (full-screen view state) -->
  <div id="analysisView" class="fixed inset-0 z-[60] bg-[#b5eff3] hidden flex-col max-w-md mx-auto">
    <div class="shrink-0 px-3 py-2.5 bg-[#16acbd] text-white flex items-center gap-2 shadow-md">
      <button id="analysisBackBtn" type="button" class="px-2 py-1 rounded-lg bg-white/20 hover:bg-white/30 text-[11px] font-bold">← ወደ ዋና ገጽ</button>
      <div class="min-w-0 flex-1">
        <div class="font-black text-xs truncate">Adika Senior Financial Advisor</div>
        <div class="text-[10px] text-white/85 truncate">የበጀት ትንተናና ምክር</div>
      </div>
    </div>
    <div class="flex-1 overflow-y-auto p-3 space-y-3 pb-28">
      <div id="analysisBudgetBar" class="bg-white rounded-2xl p-3 shadow-sm border border-white/80 space-y-2">
        <div class="flex justify-between items-center text-[11px] font-bold text-slate-700">
          <span>የበጀት ክፍፍል</span>
          <span id="analysisBudgetTotal" class="text-[#0e7490]">—</span>
        </div>
        <div class="h-2.5 rounded-full bg-slate-100 overflow-hidden flex">
          <div id="barPurchase" class="h-full bg-[#16acbd]" style="width:70%"></div>
          <div id="barFees" class="h-full bg-amber-400" style="width:15%"></div>
          <div id="barReserve" class="h-full bg-emerald-400" style="width:15%"></div>
        </div>
        <div class="grid grid-cols-3 gap-1 text-[9px] font-semibold text-slate-600">
          <div><span class="inline-block w-2 h-2 rounded-full bg-[#16acbd] mr-1"></span>ግዢ <b id="pctPurchase">70%</b></div>
          <div><span class="inline-block w-2 h-2 rounded-full bg-amber-400 mr-1"></span>ክፍያ/ታክስ <b id="pctFees">15%</b></div>
          <div><span class="inline-block w-2 h-2 rounded-full bg-emerald-400 mr-1"></span>ሪዘርቭ <b id="pctReserve">15%</b></div>
        </div>
      </div>
      <div id="analysisCards" class="space-y-2"></div>
      <div id="analysisAdvice" class="bg-white rounded-2xl p-3 shadow-sm text-[11px] text-slate-700 leading-relaxed"></div>
      <!-- Live advisor chat -->
      <div class="bg-white rounded-2xl shadow-sm border border-slate-200/90 overflow-hidden flex flex-col min-h-[280px] max-h-[460px]">
        <div class="px-3.5 py-2.5 bg-slate-50/90 border-b border-slate-100 flex items-center justify-between shrink-0">
          <div class="text-[11px] font-black text-slate-800 flex items-center gap-1.5">
            <span>💬</span>
            <span>ከአማካሪ ጋር የቀጥታ ውይይት (Live Advisor)</span>
          </div>
          <span class="text-[9px] font-extrabold text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200/60">ዝግጁ</span>
        </div>
        <div id="advisorChatLog" class="flex-1 overflow-y-auto p-3.5 space-y-3 max-h-[360px] text-xs scroll-smooth"></div>
        <div class="p-2.5 border-t border-slate-100 bg-white flex gap-1.5 shrink-0">
          <input id="advisorChatInput" type="text" placeholder="ስለ ቀረጥ፣ ንጽጽር ወይም የባንክ ብድር ይጠይቁ..." class="flex-1 px-3 py-2 rounded-xl bg-slate-50 border border-slate-200 text-xs outline-none focus:ring-2 focus:ring-[#16acbd]" />
          <button id="advisorChatSend" type="button" class="px-4 py-2 rounded-xl bg-[#16acbd] hover:bg-[#0e7490] text-white font-bold text-xs active:scale-95 transition-all shadow-sm">ላክ</button>
        </div>
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
          <button id="aiModalClose" type="button" class="w-7 h-7 rounded-full bg-white/20 hover:bg-white/30 text-white font-bold flex items-center justify-center text-sm">✕</button>
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

          <!-- 1. Budget Input & Quick Chips -->
          <div>
            <div class="flex items-center justify-between mb-1">
              <label class="text-[10px] font-bold text-slate-700 block">የእርስዎ በጀት (Total Budget in ETB)</label>
              <span id="advisorBudgetFormatted" class="text-[10px] font-extrabold text-[#0e7490]">2,000,000 ETB</span>
            </div>
            <input id="advisorBudget" type="number" value="2000000" placeholder="2,000,000" class="w-full px-3 py-1.5 rounded-xl bg-white border border-slate-200 text-xs font-bold text-slate-800 outline-none focus:ring-2 focus:ring-[#16acbd]" />
            <div class="flex gap-1 mt-1.5 overflow-x-auto no-scrollbar">
              <button type="button" class="advisor-preset-chip px-2 py-0.5 rounded-lg bg-white border border-slate-200 text-[10px] font-bold text-slate-700 whitespace-nowrap active:scale-95 transition-all" data-budget="70000">70k</button>
              <button type="button" class="advisor-preset-chip px-2 py-0.5 rounded-lg bg-white border border-slate-200 text-[10px] font-bold text-slate-700 whitespace-nowrap active:scale-95 transition-all" data-budget="500000">500k</button>
              <button type="button" class="advisor-preset-chip px-2 py-0.5 rounded-lg bg-white border border-slate-200 text-[10px] font-bold text-slate-700 whitespace-nowrap active:scale-95 transition-all" data-budget="1500000">1.5M</button>
              <button type="button" class="advisor-preset-chip px-2 py-0.5 rounded-lg bg-white border border-slate-200 text-[10px] font-bold text-slate-700 whitespace-nowrap active:scale-95 transition-all" data-budget="3000000">3M</button>
              <button type="button" class="advisor-preset-chip px-2 py-0.5 rounded-lg bg-white border border-slate-200 text-[10px] font-bold text-slate-700 whitespace-nowrap active:scale-95 transition-all" data-budget="6000000">6M</button>
            </div>
          </div>

          <!-- Action: Generate first (progressive disclosure) -->
          <button id="advisorBtn" type="button" class="w-full py-2.5 rounded-xl bg-[#16acbd] hover:bg-[#1394a3] text-white font-black text-xs shadow-md active:scale-95 transition-all flex items-center justify-center gap-1.5">
            <span>✨</span>
            <span>የአዲካ ዲጂታል ትንተና አፍልቅ (Generate Analysis)</span>
          </button>

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
          <div class="grid grid-cols-2 gap-2 text-xs">
            <!-- Tool 1: Customs Duty -->
            <button id="toolDutyBtn" type="button" class="p-3 rounded-2xl bg-slate-50 border border-slate-200 hover:border-[#16acbd] flex flex-col text-left transition-all active:scale-95 shadow-sm">
              <span class="text-xl mb-1">🧮</span>
              <span class="font-extrabold text-slate-800">የቀረጥ ስሌት</span>
              <span class="text-[10px] text-slate-500">Customs Duty & Taxes</span>
            </button>
            <!-- Tool 2: Bank Loan -->
            <button id="toolLoanBtn" type="button" class="p-3 rounded-2xl bg-slate-50 border border-slate-200 hover:border-[#16acbd] flex flex-col text-left transition-all active:scale-95 shadow-sm">
              <span class="text-xl mb-1">🏦</span>
              <span class="font-extrabold text-slate-800">የባንክ ብድር</span>
              <span class="text-[10px] text-slate-500">Mortgage & Auto Loan</span>
            </button>
            <!-- Tool 3: Car Compare -->
            <button id="toolCompareBtn" type="button" class="p-3 rounded-2xl bg-slate-50 border border-slate-200 hover:border-[#16acbd] flex flex-col text-left transition-all active:scale-95 shadow-sm">
              <span class="text-xl mb-1">⚖️</span>
              <span class="font-extrabold text-slate-800">የመኪና ንጽጽር</span>
              <span class="text-[10px] text-slate-500">Vehicle Comparison</span>
            </button>
            <!-- Tool 4: Legal Contract -->
            <button id="toolContractBtn" type="button" class="p-3 rounded-2xl bg-slate-50 border border-slate-200 hover:border-[#16acbd] flex flex-col text-left transition-all active:scale-95 shadow-sm">
              <span class="text-xl mb-1">📜</span>
              <span class="font-extrabold text-slate-800">የሽያጭ ውል</span>
              <span class="text-[10px] text-slate-500">Legal Sales Contract</span>
            </button>
            <!-- Tool 5: Verify POA -->
            <button id="toolPoaBtn" type="button" class="p-3 rounded-2xl bg-slate-50 border border-slate-200 hover:border-[#16acbd] flex flex-col text-left transition-all active:scale-95 shadow-sm">
              <span class="text-xl mb-1">🔍</span>
              <span class="font-extrabold text-slate-800">ውክልና ማረጋገጫ</span>
              <span class="text-[10px] text-slate-500">Verify Power of Attorney</span>
            </button>
            <!-- Tool 6: Diagnostic Sheet -->
            <button id="toolDiagBtn" type="button" class="p-3 rounded-2xl bg-slate-50 border border-slate-200 hover:border-[#16acbd] flex flex-col text-left transition-all active:scale-95 shadow-sm">
              <span class="text-xl mb-1">🛠️</span>
              <span class="font-extrabold text-slate-800">የምርመራ ወረቀት</span>
              <span class="text-[10px] text-slate-500">Garage Diagnostic Sheet</span>
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

        <!-- Category-Specific Dynamic Action Buttons Bar -->
        <div id="modalDynamicActions" class="p-2.5 bg-[#b5eff3]/30 rounded-2xl border border-[#16acbd]/30 space-y-1.5">
          <div class="text-[10px] font-extrabold text-[#0e7490] uppercase tracking-wider flex items-center gap-1">
            <span>✨</span>
            <span class="lang-am">ተዛማጅ የAI እና የፋይናንስ አገልግሎቶች</span>
            <span class="lang-en">Smart AI & Financial Utilities</span>
          </div>
          <div id="modalActionButtonsRow" class="grid grid-cols-3 gap-1.5"></div>
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
  <!-- 6. STANDALONE INTERACTIVE MODALS FOR AI TOOLS                     -->
  <!-- ================================================================= -->

  <!-- Modal: Customs Duty Calculator -->
  <div id="dutyModal" class="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm hidden items-end justify-center">
    <div class="w-full max-w-md bg-white rounded-t-3xl max-h-[88vh] flex flex-col shadow-2xl overflow-hidden">
      <div class="px-4 py-3 bg-[#16acbd] text-white flex items-center justify-between shrink-0">
        <h3 class="font-extrabold text-xs tracking-wide">🧮 የኢትዮጵያ ጉምሩክ የቀረጥ ስሌት (Duty Calculator)</h3>
        <button onclick="closeToolModal('dutyModal')" class="w-7 h-7 rounded-full bg-white/20 text-white font-bold text-sm">✕</button>
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
        <button onclick="closeToolModal('loanModal')" class="w-7 h-7 rounded-full bg-white/20 text-white font-bold text-sm">✕</button>
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

  <!-- Modal: Vehicle Comparison Engine -->
  <div id="compareModal" class="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm hidden items-end justify-center">
    <div class="w-full max-w-md bg-white rounded-t-3xl max-h-[90vh] flex flex-col shadow-2xl overflow-hidden">
      <div class="px-4 py-3 bg-[#16acbd] text-white flex items-center justify-between shrink-0">
        <h3 class="font-extrabold text-xs tracking-wide">⚖️ የመኪኖች ንጽጽር (Car Comparison)</h3>
        <button onclick="closeToolModal('compareModal')" class="w-7 h-7 rounded-full bg-white/20 text-white font-bold text-sm">✕</button>
      </div>
      <div class="p-4 overflow-y-auto space-y-3 flex-1 text-xs">
        <div class="grid grid-cols-2 gap-2">
          <div>
            <label class="font-bold text-slate-700 block mb-1">መኪና 1</label>
            <input id="compareCar1" type="text" value="Toyota Vitz 2018" class="w-full p-2 rounded-xl bg-slate-50 border text-xs font-bold" />
          </div>
          <div>
            <label class="font-bold text-slate-700 block mb-1">መኪና 2</label>
            <input id="compareCar2" type="text" value="Suzuki Dzire 2020" class="w-full p-2 rounded-xl bg-slate-50 border text-xs font-bold" />
          </div>
        </div>
        <button id="compareBtn" class="w-full py-2.5 bg-[#16acbd] text-white font-bold rounded-xl shadow active:scale-95">ንጽጽር አፍልቅ (Compare)</button>
        <div id="compareResult" class="hidden p-3 bg-slate-50 rounded-xl border space-y-2 font-medium"></div>
      </div>
    </div>
  </div>

  <!-- Modal: Legal Contract Generator -->
  <div id="contractModal" class="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm hidden items-end justify-center">
    <div class="w-full max-w-md bg-white rounded-t-3xl max-h-[90vh] flex flex-col shadow-2xl overflow-hidden">
      <div class="px-4 py-3 bg-[#16acbd] text-white flex items-center justify-between shrink-0">
        <h3 class="font-extrabold text-xs tracking-wide">📜 ህጋዊ የሽያጭ ውል ማዘጋጃ (Contract Generator)</h3>
        <button onclick="closeToolModal('contractModal')" class="w-7 h-7 rounded-full bg-white/20 text-white font-bold text-sm">✕</button>
      </div>
      <div class="p-4 overflow-y-auto space-y-2.5 flex-1 text-xs">
        <div>
          <label class="font-bold text-slate-700 block mb-1">የውል ዓይነት</label>
          <select id="contractType" class="w-full p-2 rounded-xl bg-slate-50 border text-xs font-bold">
            <option value="vehicle">የመኪና ሽያጭ ውል (Vehicle Sale)</option>
            <option value="property">የቤትና ይዞታ ሽያጭ ውል (Property Sale)</option>
          </select>
        </div>
        <div class="grid grid-cols-2 gap-2">
          <div>
            <label class="font-bold text-slate-700 block mb-1">የሻጭ ሙሉ ስም</label>
            <input id="contractSeller" type="text" placeholder="አቶ ተስፋዬ በቀለ" class="w-full p-2 rounded-xl bg-slate-50 border text-xs font-bold" />
          </div>
          <div>
            <label class="font-bold text-slate-700 block mb-1">የገዢ ሙሉ ስም</label>
            <input id="contractBuyer" type="text" placeholder="ወ/ሮ ማርታ ደሳለኝ" class="w-full p-2 rounded-xl bg-slate-50 border text-xs font-bold" />
          </div>
        </div>
        <div class="grid grid-cols-2 gap-2">
          <div>
            <label class="font-bold text-slate-700 block mb-1">ጠቅላላ ዋጋ (ብር)</label>
            <input id="contractPrice" type="text" placeholder="2,200,000" class="w-full p-2 rounded-xl bg-slate-50 border text-xs font-bold" />
          </div>
          <div>
            <label class="font-bold text-slate-700 block mb-1">ቅድመ ክፍያ (ብር)</label>
            <input id="contractAdvance" type="text" placeholder="500,000" class="w-full p-2 rounded-xl bg-slate-50 border text-xs font-bold" />
          </div>
        </div>
        <div class="grid grid-cols-2 gap-2">
          <div>
            <label class="font-bold text-slate-700 block mb-1">የሰሌዳ / ሰነድ ቁጥር</label>
            <input id="contractDocId" type="text" placeholder="ኮድ 3 - A12345" class="w-full p-2 rounded-xl bg-slate-50 border text-xs font-bold" />
          </div>
          <div>
            <label class="font-bold text-slate-700 block mb-1">ሻንሲ ቁጥር (Chassis)</label>
            <input id="contractChassis" type="text" placeholder="JTDKN36U48..." class="w-full p-2 rounded-xl bg-slate-50 border text-xs font-bold" />
          </div>
        </div>
        <div class="grid grid-cols-2 gap-2">
          <div>
            <label class="font-bold text-slate-700 block mb-1">የሞተር ቁጥር (Engine)</label>
            <input id="contractEngine" type="text" placeholder="1NZ-FE-88992" class="w-full p-2 rounded-xl bg-slate-50 border text-xs font-bold" />
          </div>
          <div>
            <label class="font-bold text-slate-700 block mb-1">የሊብሬ / የካርታ ቁጥር</label>
            <input id="contractLibre" type="text" placeholder="LIB-AA-998822" class="w-full p-2 rounded-xl bg-slate-50 border text-xs font-bold" />
          </div>
        </div>
        <button id="contractGenerateBtn" class="w-full py-2.5 bg-[#16acbd] text-white font-bold rounded-xl shadow active:scale-95">📄 ውል አዘጋጅ (Generate Contract)</button>
        <div id="contractResult" class="hidden p-3 bg-slate-50 rounded-xl border space-y-2 font-medium"></div>
      </div>
    </div>
  </div>

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
        <button type="button" onclick="closeToolModal('poaModal')" class="w-7 h-7 rounded-full bg-white/20 hover:bg-white/30 text-white font-bold text-sm transition-all flex items-center justify-center shrink-0">✕</button>
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
  <div id="diagModal" class="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm hidden items-end justify-center">
    <div class="w-full max-w-md bg-white rounded-t-3xl max-h-[88vh] flex flex-col shadow-2xl overflow-hidden">
      <div class="px-4 py-3 bg-[#16acbd] text-white flex items-center justify-between shrink-0">
        <h3 class="font-extrabold text-xs tracking-wide">🛠️ የምርመራ ወረቀት ተንታኝ (Diagnostic Analyzer)</h3>
        <button onclick="closeToolModal('diagModal')" class="w-7 h-7 rounded-full bg-white/20 text-white font-bold text-sm">✕</button>
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

      // Populate dynamic category action buttons
      var actionsRow = document.getElementById("modalActionButtonsRow");
      if (actionsRow) {
        if (isCar) {
          actionsRow.innerHTML =
            '<button id="actCarDuty" type="button" class="p-2 rounded-xl bg-white border border-[#16acbd]/40 text-[#0e7490] font-bold text-[10px] flex flex-col items-center justify-center gap-0.5 active:scale-95 shadow-sm">' +
              '<span class="text-sm">🧮</span><span>የቀረጥ ስሌት</span>' +
            '</button>' +
            '<button id="actCarCompare" type="button" class="p-2 rounded-xl bg-white border border-[#16acbd]/40 text-[#0e7490] font-bold text-[10px] flex flex-col items-center justify-center gap-0.5 active:scale-95 shadow-sm">' +
              '<span class="text-sm">⚖️</span><span>ንጽጽር</span>' +
            '</button>' +
            '<button id="actCarDiag" type="button" class="p-2 rounded-xl bg-white border border-[#16acbd]/40 text-[#0e7490] font-bold text-[10px] flex flex-col items-center justify-center gap-0.5 active:scale-95 shadow-sm">' +
              '<span class="text-sm">🛠️</span><span>ምርመራ</span>' +
            '</button>';
          document.getElementById("actCarDuty").onclick = function() {
            openToolModal('dutyModal');
            if (extra.cif_price) document.getElementById("dutyCif").value = extra.cif_price;
          };
          document.getElementById("actCarCompare").onclick = function() {
            openToolModal('compareModal');
            document.getElementById("compareCar1").value = modalTitleText;
          };
          document.getElementById("actCarDiag").onclick = function() {
            openToolModal('diagModal');
          };
        } else {
          actionsRow.innerHTML =
            '<button id="actPropLoan" type="button" class="p-2 rounded-xl bg-white border border-[#16acbd]/40 text-[#0e7490] font-bold text-[10px] flex flex-col items-center justify-center gap-0.5 active:scale-95 shadow-sm">' +
              '<span class="text-sm">🏦</span><span>የባንክ ብድር</span>' +
            '</button>' +
            '<button id="actPropPoa" type="button" class="p-2 rounded-xl bg-white border border-[#16acbd]/40 text-[#0e7490] font-bold text-[10px] flex flex-col items-center justify-center gap-0.5 active:scale-95 shadow-sm">' +
              '<span class="text-sm">🔍</span><span>ውክልና ማጣሪያ</span>' +
            '</button>' +
            '<button id="actPropContract" type="button" class="p-2 rounded-xl bg-white border border-[#16acbd]/40 text-[#0e7490] font-bold text-[10px] flex flex-col items-center justify-center gap-0.5 active:scale-95 shadow-sm">' +
              '<span class="text-sm">📜</span><span>የሽያጭ ውል</span>' +
            '</button>';
          document.getElementById("actPropLoan").onclick = function() {
            openToolModal('loanModal');
            var rawPrice = parseInt(String(item.price || "").replace(/[^0-9]/g, "")) || 3000000;
            document.getElementById("loanPrice").value = rawPrice;
          };
          document.getElementById("actPropPoa").onclick = function() {
            openToolModal('poaModal');
          };
          document.getElementById("actPropContract").onclick = function() {
            openToolModal('contractModal');
            var rawPrice = parseInt(String(item.price || "").replace(/[^0-9]/g, "")) || "";
            document.getElementById("contractPrice").value = rawPrice;
          };
        }
      }

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
    };

    // Tool Launchers
    document.getElementById("toolDutyBtn").onclick = function() { aiModalClose.onclick(); openToolModal("dutyModal"); };
    document.getElementById("toolLoanBtn").onclick = function() { aiModalClose.onclick(); openToolModal("loanModal"); };
    document.getElementById("toolCompareBtn").onclick = function() { aiModalClose.onclick(); openToolModal("compareModal"); };
    document.getElementById("toolContractBtn").onclick = function() { aiModalClose.onclick(); openToolModal("contractModal"); };
    document.getElementById("toolPoaBtn").onclick = function() { aiModalClose.onclick(); openToolModal("poaModal"); };
    document.getElementById("toolDiagBtn").onclick = function() { aiModalClose.onclick(); openToolModal("diagModal"); };

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
        row.className = "ml-6 p-3 rounded-2xl bg-[#16acbd] text-white shadow-sm text-right animate-in fade-in duration-150";
        row.innerHTML = '<div class="text-[9px] font-bold text-white/80 mb-0.5">እርስዎ</div><div class="text-xs font-semibold whitespace-pre-wrap leading-relaxed text-left">' + esc(String(text || "")) + '</div>';
      } else {
        row.className = "mr-6 p-3 rounded-2xl bg-white text-slate-800 border border-slate-200/90 shadow-sm leading-relaxed text-left animate-in fade-in duration-150";
        row.innerHTML = '<div class="text-[9px] font-black text-[#0e7490] mb-0.5 flex items-center gap-1"><span>💼</span><span>Adika Senior Financial Advisor</span></div><div class="text-xs text-slate-700 whitespace-pre-wrap leading-relaxed">' + esc(String(text || "")) + '</div>';
      }
      log.appendChild(row);
      setTimeout(function() {
        log.scrollTop = log.scrollHeight;
      }, 50);
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
      var advice = d.advice || d;
      var body = advice.advice_amharic || advice.advice_am || advice.message || advice.summary || "";
      body = String(body).replace(/\bAI\b/gi, "እኛ").replace(/language model/gi, "እኛ").replace(/\bbot\b/gi, "እኛ");
      var title = advice.title || advice.summary_title || "የበጀት ትንተና";
      var options = advice.options || advice.recommendations || [];
      var steps = advice.next_steps || advice.steps || [];
      var budgetNum = Number(budget) || 0;

      renderBudgetBar(budgetNum);

      var cardsEl = document.getElementById("analysisCards");
      if (cardsEl) {
        var purchaseCap = Math.round(budgetNum * 0.70);
        var filtered = (options || []).filter(function(o) {
          var p = o.estimated_price_etb || o.max_price || o.price_etb;
          if (p == null && o.estimated_price_range_etb) {
            var m = String(o.estimated_price_range_etb).replace(/,/g, "").match(/(\d+)/g);
            if (m && m.length) p = Number(m[m.length - 1]);
          }
          if (p == null || isNaN(Number(p))) return true;
          return Number(p) <= purchaseCap * 1.05;
        }).slice(0, 6);
        if (!filtered.length && options && options.length) filtered = options.slice(0, 3);
        cardsEl.innerHTML = filtered.map(function(o) {
          var name = o.name || o.title || o.asset || "አማራጭ";
          var price = o.estimated_price_range_etb || o.price || o.range || "";
          var fuel = o.fuel_or_maintenance || o.maintenance || "";
          return '<div class="bg-white rounded-2xl p-3 shadow-sm border border-white/80">' +
            '<div class="font-black text-slate-900 text-[12px]">' + esc(String(name)) + '</div>' +
            (price ? '<div class="text-[#0e7490] font-bold text-[11px] mt-1">💰 ' + esc(String(price)) + '</div>' : '') +
            (fuel ? '<div class="text-[10px] text-slate-500 mt-0.5">' + esc(String(fuel)) + '</div>' : '') +
            '<div class="text-[9px] text-emerald-700 font-bold mt-1">✓ በ70% የግዢ በጀት ወሰን ውስጥ</div>' +
          '</div>';
        }).join("") || '<div class="text-[11px] text-slate-500 p-2">በበጀትዎ የሚገጥሙ አማራጮች እየተዘጋጁ ነው…</div>';
      }

      var advEl = document.getElementById("analysisAdvice");
      if (advEl) {
        advEl.innerHTML =
          '<div class="text-[9px] font-extrabold text-[#0e7490] uppercase tracking-wide mb-1">ከአማካሪ</div>' +
          '<div class="font-black text-slate-900 text-[12px] mb-1">' + esc(String(title)) + '</div>' +
          '<div class="whitespace-pre-wrap leading-relaxed">' + esc(String(body)) + '</div>' +
          (steps && steps.length
            ? '<div class="mt-2 space-y-1">' + steps.map(function(s){
                return '<div class="flex gap-1"><span class="text-[#16acbd]">✓</span><span>' + esc(String(s)) + '</span></div>';
              }).join("") + '</div>'
            : '');
      }

      var log = document.getElementById("advisorChatLog");
      if (log && !log.dataset.seeded) {
        log.innerHTML = "";
        advisorChatHistory = [];
        var initMsg = "ሰላም፣ እኔ የ Adika Senior Financial Advisor ነኝ። በበጀትዎ (" + Number(budgetNum).toLocaleString() + " ብር) ላይ የ70% ግዢ፣ 15% ክፍያ/ታክስ እና 15% ሪዘርቭ ክፍፍል ትንተና አዘጋጅተናል። ጥያቄ ካለዎት እዚህ ይጻፉልን።";
        appendAdvisorChat("advisor", initMsg);
        advisorChatHistory.push({ role: "advisor", content: initMsg });
        log.dataset.seeded = "1";
      }
    }


        // Advisor Button Action (/api/ai-advisor) — progressive disclosure
    document.getElementById("advisorBtn").onclick = function() {
      var budget = document.getElementById("advisorBudget").value || 2000000;
      var purpose = "personal";
      document.querySelectorAll(".advisor-purpose-btn").forEach(function(b) {
        if (b.className.indexOf("bg-[#16acbd]") >= 0) purpose = b.getAttribute("data-purpose") || purpose;
      });
      var pay = "cash";
      document.querySelectorAll(".advisor-pay-btn").forEach(function(b) {
        if (b.className.indexOf("bg-[#16acbd]") >= 0) pay = b.getAttribute("data-pay") || pay;
      });
      var incomeEl = document.getElementById("advisorIncome");
      var income = incomeEl ? incomeEl.value : "";

      // Close input modal → open dedicated analysis page
      try {
        var aiModal = document.getElementById("aiModal");
        if (aiModal) { aiModal.classList.add("hidden"); aiModal.classList.remove("flex"); }
      } catch (e) {}
      showAnalysisView(true);
      var cardsEl = document.getElementById("analysisCards");
      var advEl = document.getElementById("analysisAdvice");
      var log = document.getElementById("advisorChatLog");
      if (log) { log.innerHTML = ""; log.dataset.seeded = ""; }
      advisorChatHistory = [];
      renderBudgetBar(budget);
      if (advEl) {
        advEl.innerHTML =
          '<div class="flex items-center gap-2 text-slate-600 p-2 bg-white rounded-xl border border-slate-100">' +
            '<span class="inline-flex gap-1 items-center">' +
              '<span class="w-2 h-2 rounded-full bg-[#16acbd] animate-pulse"></span>' +
              '<span class="w-2 h-2 rounded-full bg-[#16acbd] animate-pulse" style="animation-delay:200ms"></span>' +
              '<span class="w-2 h-2 rounded-full bg-[#16acbd] animate-pulse" style="animation-delay:400ms"></span>' +
            '</span>' +
            '<span class="font-bold text-xs">ኦፕሬተሩ መልስ በመጻፍ ላይ ነው...</span>' +
          '</div>';
      }
      if (cardsEl) cardsEl.innerHTML = "";

      fetch("/api/ai-advisor", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          budget: Number(budget),
          purpose: purpose,
          payment_strategy: pay,
          monthly_income: income ? Number(income) : undefined,
          strict_budget_cap: true
        })
      })
      .then(function(r){ return r.json(); })
      .then(function(d){
        renderAnalysisDashboard(d, budget);
        var extra = document.getElementById("advisorExtraFilters");
        if (extra) extra.classList.remove("hidden");
      })
      .catch(function(){
        if (advEl) advEl.innerHTML = '<div class="text-rose-700 font-bold text-xs p-2">ትንተና ማግኘት አልተቻለም። እንደገና ይሞክሩ።</div>';
      });
    };


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
          row.innerHTML = '<span class="inline-flex gap-1 items-center"><span class="w-2 h-2 rounded-full bg-[#16acbd] animate-pulse"></span><span class="w-2 h-2 rounded-full bg-[#16acbd] animate-pulse" style="animation-delay:200ms"></span><span class="w-2 h-2 rounded-full bg-[#16acbd] animate-pulse" style="animation-delay:400ms"></span></span><span>ኦፕሬተሩ መልስ በመጻፍ ላይ ነው...</span>';
          log.appendChild(row);
          setTimeout(function() { log.scrollTop = log.scrollHeight; }, 30);
        }
        function sendChat() {
          var text = (input.value || "").trim();
          if (!text) return;
          if (typeof appendAdvisorChat === "function") appendAdvisorChat("user", text);
          advisorChatHistory.push({ role: "user", content: text });
          input.value = "";
          showTyping();
          var budgetEl = document.getElementById("advisorBudget");
          var budget = budgetEl && budgetEl.value ? Number(budgetEl.value) : 2000000;
          var purchaseCap = Math.round(budget * 0.70);
          fetch("/api/ai-advisor", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              budget: budget,
              chat_message: text,
              history: advisorChatHistory,
              strict_budget_cap: true,
              purchase_allocation_etb: purchaseCap
            })
          })
          .then(function(r){ return r.json(); })
          .then(function(d){
            removeTyping();
            var advice = (d && d.advice) ? d.advice : (d || {});
            var msg = d.reply || advice.chat_reply || advice.advice_amharic || advice.advice_am || advice.message || advice.reply ||
              ("ጥያቄዎን ተረድተናል። እኛ በ " + purchaseCap.toLocaleString() + " ብር (70% የግዢ ድርሻ) ወሰን ውስጥ እንመክራለን።");
            msg = String(msg).replace(/\bAI\b/gi, "እኛ").replace(/language model/gi, "እኛ").replace(/\bbot\b/gi, "እኛ");
            if (typeof appendAdvisorChat === "function") appendAdvisorChat("advisor", msg);
            advisorChatHistory.push({ role: "advisor", content: msg });
          })
          .catch(function(){
            removeTyping();
            if (typeof appendAdvisorChat === "function") {
              appendAdvisorChat("advisor", "አሁን መልስ ማግኘት አልተቻለም። ትንሽ ቆይተው ይሞክሩ።");
            }
          });
        }
        sendBtn.onclick = sendChat;
        input.addEventListener("keydown", function(ev){ if (ev.key === "Enter") { ev.preventDefault(); sendChat(); } });
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
    document.getElementById("compareBtn").onclick = function() {
      var c1 = document.getElementById("compareCar1").value || "Toyota Vitz 2018";
      var c2 = document.getElementById("compareCar2").value || "Suzuki Dzire 2020";
      var resEl = document.getElementById("compareResult");
      resEl.classList.remove("hidden");
      resEl.innerHTML = "⏳ AI ንጽጽሩን እያዘጋጀ ነው...";

      fetch("/api/compare-cars", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ car1: c1, car2: c2 })
      })
      .then(function(r){ return r.json(); })
      .then(function(d){
        var cmp = d.comparison || d;
        var car1 = cmp.car_1 || {};
        var car2 = cmp.car_2 || {};
        var winner = cmp.verdict_winner || "";
        var verdictAm = cmp.verdict_summary_amharic || "";

        resEl.innerHTML =
          '<div class="space-y-3">' +
            '<div class="grid grid-cols-2 gap-2">' +
              // Car 1 Card
              '<div class="p-2.5 rounded-2xl bg-white border border-[#16acbd]/30 shadow-sm flex flex-col justify-between space-y-2">' +
                '<div>' +
                  '<div class="font-extrabold text-xs text-slate-900 truncate flex items-center gap-1">' +
                    '<span>🚗</span>' +
                    '<span class="truncate">' + esc(car1.name || c1) + '</span>' +
                  '</div>' +
                  (winner && car1.name && winner.toLowerCase().indexOf(car1.name.toLowerCase().split(" ")[0]) !== -1 ? '<span class="inline-block mt-1 px-1.5 py-0.5 rounded-full bg-emerald-50 text-emerald-700 font-extrabold text-[8px] border border-emerald-200">🏆 ተመራጭ</span>' : '') +
                  '<div class="mt-2 space-y-1 text-[10px] text-slate-600">' +
                    '<div>⚙️ <b>ሞተር:</b> ' + esc(car1.engine || "1.3L Petrol") + '</div>' +
                    '<div>⛽ <b>ፍጆታ:</b> <span class="text-emerald-600 font-bold">' + esc(car1.fuel_consumption_kml || "16 KM/L") + '</span></div>' +
                    '<div>💵 <b>ወርሃዊ ነዳጅ:</b> ' + esc(car1.monthly_fuel_cost_etb || "5,000 ETB") + '</div>' +
                    '<div>🛠️ <b>መለዋወጫ:</b> ' + esc(car1.parts_availability_rating || "5/5") + '</div>' +
                    '<div>📈 <b>የመሸጫ እሴት:</b> ' + esc(car1.resale_retention_pct || "92%") + '</div>' +
                  '</div>' +
                '</div>' +
                '<div class="pt-1.5 border-t border-slate-100 text-[9px] space-y-1">' +
                  '<div class="font-bold text-emerald-700">ጥንካሬዎች (Pros):</div>' +
                  ((car1.pros || []).map(function(p){ return '<div class="text-slate-600 flex items-start gap-0.5 leading-tight"><span class="text-emerald-500">✔</span><span>' + esc(p) + '</span></div>'; }).join('')) +
                  '<div class="font-bold text-rose-600 mt-1">ጉድለቶች (Cons):</div>' +
                  ((car1.cons || []).map(function(c){ return '<div class="text-slate-600 flex items-start gap-0.5 leading-tight"><span class="text-rose-500">•</span><span>' + esc(c) + '</span></div>'; }).join('')) +
                '</div>' +
              '</div>' +
              // Car 2 Card
              '<div class="p-2.5 rounded-2xl bg-white border border-[#16acbd]/30 shadow-sm flex flex-col justify-between space-y-2">' +
                '<div>' +
                  '<div class="font-extrabold text-xs text-slate-900 truncate flex items-center gap-1">' +
                    '<span>🚗</span>' +
                    '<span class="truncate">' + esc(car2.name || c2) + '</span>' +
                  '</div>' +
                  (winner && car2.name && winner.toLowerCase().indexOf(car2.name.toLowerCase().split(" ")[0]) !== -1 ? '<span class="inline-block mt-1 px-1.5 py-0.5 rounded-full bg-emerald-50 text-emerald-700 font-extrabold text-[8px] border border-emerald-200">🏆 ተመራጭ</span>' : '') +
                  '<div class="mt-2 space-y-1 text-[10px] text-slate-600">' +
                    '<div>⚙️ <b>ሞተር:</b> ' + esc(car2.engine || "1.2L Petrol") + '</div>' +
                    '<div>⛽ <b>ፍጆታ:</b> <span class="text-emerald-600 font-bold">' + esc(car2.fuel_consumption_kml || "20 KM/L") + '</span></div>' +
                    '<div>💵 <b>ወርሃዊ ነዳጅ:</b> ' + esc(car2.monthly_fuel_cost_etb || "4,200 ETB") + '</div>' +
                    '<div>🛠️ <b>መለዋወጫ:</b> ' + esc(car2.parts_availability_rating || "4.2/5") + '</div>' +
                    '<div>📈 <b>የመሸጫ እሴት:</b> ' + esc(car2.resale_retention_pct || "88%") + '</div>' +
                  '</div>' +
                '</div>' +
                '<div class="pt-1.5 border-t border-slate-100 text-[9px] space-y-1">' +
                  '<div class="font-bold text-emerald-700">ጥንካሬዎች (Pros):</div>' +
                  ((car2.pros || []).map(function(p){ return '<div class="text-slate-600 flex items-start gap-0.5 leading-tight"><span class="text-emerald-500">✔</span><span>' + esc(p) + '</span></div>'; }).join('')) +
                  '<div class="font-bold text-rose-600 mt-1">ጉድለቶች (Cons):</div>' +
                  ((car2.cons || []).map(function(c){ return '<div class="text-slate-600 flex items-start gap-0.5 leading-tight"><span class="text-rose-500">•</span><span>' + esc(c) + '</span></div>'; }).join('')) +
                '</div>' +
              '</div>' +
            '</div>' +
            // Amharic Summary Card
            (verdictAm ? 
              '<div class="p-3 bg-[#b5eff3]/40 rounded-2xl border border-[#16acbd]/40 text-slate-800 text-[11px] leading-relaxed">' +
                '<div class="font-extrabold text-[#0e7490] text-xs mb-1 flex items-center gap-1"><span>💡</span><span>የባለሙያ ውሳኔና ምክረ-ሀሳብ:</span></div>' +
                '<p class="whitespace-pre-line">' + esc(verdictAm) + '</p>' +
              '</div>' : '') +
          '</div>';
      })
      .catch(function(){ resEl.innerHTML = '<div class="p-2 bg-rose-50 text-rose-700 rounded-xl text-xs">ንጽጽሩን ማመንጨት አልተቻለም። እባክዎ እንደገና ይሞክሩ።</div>'; });
    };

    // Contract Generate Action
    document.getElementById("contractGenerateBtn").onclick = function() {
      var contractType = document.getElementById("contractType") ? document.getElementById("contractType").value : "vehicle";
      var seller = document.getElementById("contractSeller").value || "አቶ ዮሐንስ ታደሰ";
      var buyer = document.getElementById("contractBuyer").value || "ወ/ሮ ሰላም አየለ";
      var price = document.getElementById("contractPrice").value || "2,000,000";
      var advance = document.getElementById("contractAdvance").value || "500,000";
      var docId = document.getElementById("contractDocId").value || "ኮድ 3 - A54321";
      var chassis = document.getElementById("contractChassis") ? document.getElementById("contractChassis").value : "";
      var engine = document.getElementById("contractEngine") ? document.getElementById("contractEngine").value : "";
      var libre = document.getElementById("contractLibre") ? document.getElementById("contractLibre").value : "";

      var resEl = document.getElementById("contractResult");
      resEl.classList.remove("hidden");
      resEl.innerHTML = "⏳ ህጋዊ ውል እየተዘጋጀ ነው...";

      fetch("/api/generate-contract", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          contract_type: contractType,
          seller_name: seller,
          buyer_name: buyer,
          agreed_price: price,
          total_price: price,
          advance_payment: advance,
          item_identifier: docId,
          plate_number: docId,
          chassis_number: chassis,
          engine_number: engine,
          libre_number: libre
        })
      })
      .then(function(r){ return r.json(); })
      .then(function(d){
        var contractObj = d.contract || {};
        var contractText = contractObj.contract_text_amharic || contractObj.print_ready_text || d.contract_text || (typeof d.contract === "string" ? d.contract : "ውል ተዘጋጅቷል");
        var contractTitle = contractObj.contract_title || "ህጋዊ የሽያጭ ውል ስምምነት";
        var clauses = contractObj.key_clauses_summary || [];

        resEl.innerHTML =
          '<div class="space-y-2.5 text-xs">' +
            '<div class="font-extrabold text-slate-800 flex items-center justify-between pb-1 border-b border-slate-100">' +
              '<span class="flex items-center gap-1"><span>📜</span><span>' + esc(contractTitle) + '</span></span>' +
              '<span class="text-[10px] text-emerald-600 font-bold bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200">✔ ዝግጁ ነው</span>' +
            '</div>' +
            (clauses.length > 0 ?
              '<div class="flex flex-wrap gap-1">' +
                clauses.map(function(c){ return '<span class="px-2 py-0.5 bg-[#16acbd]/10 text-[#0e7490] rounded-full text-[9px] font-bold">✔ ' + esc(c) + '</span>'; }).join('') +
              '</div>' : '') +
            '<div id="contractGeneratedText" class="p-3.5 bg-slate-50 border border-slate-200 rounded-2xl text-[11px] font-mono whitespace-pre-wrap leading-relaxed max-h-72 overflow-y-auto text-slate-800 shadow-inner select-all">' + esc(contractText) + '</div>' +
            '<div class="grid grid-cols-2 gap-2">' +
              '<button id="copyContractBtn" type="button" class="py-2.5 bg-[#16acbd] hover:bg-[#1394a3] text-white font-bold rounded-xl text-xs active:scale-95 shadow transition-all flex items-center justify-center gap-1.5">' +
                '<span>📋</span><span>ኮፒ አድርግ (Copy)</span>' +
              '</button>' +
              '<button id="printContractBtn" type="button" class="py-2.5 bg-slate-800 hover:bg-slate-900 text-white font-bold rounded-xl text-xs active:scale-95 shadow transition-all flex items-center justify-center gap-1.5">' +
                '<span>🖨️</span><span>ፕሪንት / አጋራ (Print)</span>' +
              '</button>' +
            '</div>' +
            '<div id="copyToast" class="hidden text-center py-1.5 px-3 bg-emerald-100 border border-emerald-300 text-emerald-800 text-[11px] font-bold rounded-xl transition-all">✔ የሽያጭ ውሉ በተሳካ ሁኔታ ኮፒ ተደርጓል!</div>' +
          '</div>';

        document.getElementById("copyContractBtn").onclick = function() {
          var t = document.getElementById("contractGeneratedText").innerText;
          var toast = document.getElementById("copyToast");
          if (navigator.clipboard) {
            navigator.clipboard.writeText(t).then(function(){
              if (toast) {
                toast.classList.remove("hidden");
                setTimeout(function(){ toast.classList.add("hidden"); }, 3000);
              }
            }).catch(function(){
              alert("ውሉ ኮፒ ተደርጓል!");
            });
          } else {
            alert("ጽሑፉን ይምረጡና ኮፒ ያድርጉ።");
          }
        };

        var printBtn = document.getElementById("printContractBtn");
        if (printBtn) {
          printBtn.onclick = function() {
            var t = document.getElementById("contractGeneratedText").innerText;
            var w = window.open('', '_blank');
            if (w) {
              w.document.write('<html><head><title>' + esc(contractTitle) + '</title><style>body{font-family:sans-serif;padding:30px;line-height:1.6;font-size:13px;white-space:pre-wrap;}</style></head><body>' + esc(t) + '</body></html>');
              w.document.close();
              w.focus();
              setTimeout(function(){ w.print(); }, 250);
            } else {
              window.print();
            }
          };
        }
      })
      .catch(function(){ resEl.innerHTML = '<div class="p-2 bg-rose-50 text-rose-700 rounded-xl text-xs">ውሉን ማዘጋጀት አልተቻለም። እባክዎ እንደገና ይሞክሩ።</div>'; });
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
            '</div>';
        })
        .catch(function(){ resEl.innerHTML = '<div class="p-2 bg-rose-50 text-rose-700 rounded-xl text-xs">ትንተናውን ማጠናቀቅ አልተቻለም።</div>'; });
      });
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
    
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": f"ሰላም! እኔ የ Adika Senior Financial Advisor ነኝ። በያዙት {user_budget:,.0f} ETB በጀት ዙሪያ የሚፈልጉትን ማንኛውንም የፋይናንስ እና የገበያ ጥያቄ መጠየቅ ይችላሉ።"}
        ]

    # የቀደሙ መልእክቶችን ማሳየት
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # የተጠቃሚ አዲስ ጥያቄ
    if prompt := st.chat_input("ጥያቄዎን እዚህ ያስገቡ..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        # Typing Indicator & Real API Call
        with st.chat_message("assistant"):
            with st.spinner("ኦፕሬተሩ መልስ በመጻፍ ላይ ነው..."):
                system_instruction = (
                    "You are a human Senior Financial Advisor at Adika Digital. "
                    "Speak politely and naturally in Amharic like an expert advisor. "
                    "NEVER mention you are an AI, bot, or language model. "
                    "Always refer to Adika as 'እኛ' or 'እኔ'. Strictly respect the user's budget context."
                )
                
                # api_service.py ላይ ያለውን ጥሪ ማገናኘት
                response = generate_advisor_response(
                    prompt=prompt, 
                    history=st.session_state.messages, 
                    budget=user_budget
                )
                st.write(response)
                
        st.session_state.messages.append({"role": "assistant", "content": response})


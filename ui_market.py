# -*- coding: utf-8 -*-
"""Adika Marketplace cards & hero feed (Module 4 of 5).

Contains:
  - Main feed HTML (promo hero + 2-column listing grid)
  - Image URL parser (string / JSON array / JS array)
  - Card renderer (brand-model, price guard, relative time, favorite)
  - Fallback demo cards so the grid is never blank

Detail modal / tools / chat live in other modules.
"""

from __future__ import annotations

LISTINGS_ENDPOINT = "/api/explorer/listings"
PRICE_CALL_FOR_PRICE_MAX = 300_000_000


def format_listing_price(raw) -> str:
    """Mirror of JS formatListingPrice. Missing/0/>300M -> ለዋጋ ደውሉ."""
    if raw is None or raw == "" or raw in ("—", "Contact"):
        return "ለዋጋ ደውሉ"
    cleaned = str(raw).replace("ETB", "").replace("etb", "").replace("ብር", "").replace(",", "").strip()
    digits = "".join(ch for ch in cleaned if ch.isdigit() or ch == ".")
    try:
        n = float(digits) if digits else 0.0
    except ValueError:
        return "ለዋጋ ደውሉ"
    if n <= 0 or n > PRICE_CALL_FOR_PRICE_MAX:
        return "ለዋጋ ደውሉ"
    return f"{int(round(n)):,} ETB"


def first_photo_url(photo_urls) -> str:
    """Safe first-image extractor for string / list / JSON-encoded list."""
    if not photo_urls:
        return ""
    if isinstance(photo_urls, (list, tuple)):
        first = photo_urls[0] if photo_urls else ""
        if isinstance(first, dict):
            return str(first.get("url") or first.get("src") or first.get("photo_url") or "")
        return str(first or "")
    if isinstance(photo_urls, dict):
        return str(photo_urls.get("url") or photo_urls.get("src") or photo_urls.get("photo_url") or "")
    if isinstance(photo_urls, str):
        s = photo_urls.strip()
        if s.startswith("["):
            import json
            try:
                parsed = json.loads(s)
                return first_photo_url(parsed)
            except Exception:
                return s
        return s
    return ""

MARKET_FEED_HTML = r"""
  <main id="adikaMainFeed" class="w-full max-w-md mx-auto px-2.5 pb-32" style="padding-top: 118px; padding-bottom: 140px;">
    <!-- Active Filter Banner -->
    <div id="filterBanner" class="hidden mb-1 px-3 py-1 bg-white/90 backdrop-blur-sm rounded-xl border border-white flex items-center justify-between text-xs shadow-sm">
      <span id="filterText" class="font-bold text-[#0e7490] truncate"></span>
      <button id="clearFilterBtn" type="button" class="text-rose-600 font-bold ml-2 shrink-0">✕</button>
    </div>

    <!-- Adika Digital System — Auto-Play Slim Promo Banner (h-14, infinite loop) -->
    <div id="homeHero" class="-mt-2 pt-0 mb-1 px-0">
      <div id="adikaPromoBanner" class="relative w-full h-11 rounded-xl overflow-hidden cursor-pointer active:scale-[0.99] transition-transform"
           style="margin-top:0; background: rgba(15,23,42,0.90); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
                  border: 1.5px solid transparent;
                  background-image: linear-gradient(rgba(15,23,42,0.90), rgba(15,23,42,0.90)), linear-gradient(90deg, #22d3ee, #7dd3fc, #2dd4bf, #22d3ee);
                  background-size: 100% 100%, 200% 100%;
                  background-origin: border-box; background-clip: padding-box, border-box;">
        <div class="absolute inset-0 pointer-events-none opacity-40 overflow-hidden">
          <div style="position:absolute;inset:0;background:linear-gradient(90deg,transparent,rgba(34,211,238,0.2),rgba(125,211,252,0.15),transparent);animation:adikaShimmer 2.2s linear infinite;"></div>
        </div>
        <div id="promoSlides" class="relative h-full w-full">
          <div class="promo-slide absolute inset-0 flex items-center gap-2 py-1 px-3 is-active" data-tool="poa" data-idx="0">
            <span class="promo-orb absolute left-1 w-8 h-8 rounded-full pointer-events-none" style="background:radial-gradient(circle,rgba(34,211,238,0.45),transparent 70%);"></span>
            <span class="promo-icon relative text-base shrink-0 z-[1]">📜</span>
            <div class="flex-1 min-w-0 relative z-[1]">
              <p class="promo-title text-[10px] font-black text-white leading-tight truncate"><span class="promo-letter" style="animation-delay:0ms">የ</span><span class="promo-letter" style="animation-delay:30ms">ው</span><span class="promo-letter" style="animation-delay:60ms">ክ</span><span class="promo-letter" style="animation-delay:90ms">ል</span><span class="promo-letter" style="animation-delay:120ms">ና</span> <span class="promo-letter" style="animation-delay:180ms">ማ</span><span class="promo-letter" style="animation-delay:210ms">ጣ</span><span class="promo-letter" style="animation-delay:240ms">ሪ</span><span class="promo-letter" style="animation-delay:270ms">ያ</span></p>
              <p class="promo-sub text-[8px] text-sky-100/85 font-medium truncate">የውክልና ሰነዶችን ህጋዊነት በስካን ያረጋገጡ</p>
            </div>
            <span class="promo-cta relative z-[1] text-[8px] font-black text-slate-950 shrink-0 px-2 py-0.5 rounded-full" style="background:#0ea5e9;box-shadow:0 2px 8px rgba(14,165,233,0.45);">አስጀምር ➔</span>
          </div>
          <div class="promo-slide absolute inset-0 flex items-center gap-2 py-1 px-3" data-tool="chassis" data-idx="1" style="opacity:0;pointer-events:none">
            <span class="promo-orb absolute left-1 w-8 h-8 rounded-full pointer-events-none" style="background:radial-gradient(circle,rgba(56,189,248,0.45),transparent 70%);"></span>
            <span class="promo-icon relative text-base shrink-0 z-[1]">🔍</span>
            <div class="flex-1 min-w-0 relative z-[1]">
              <p class="promo-title text-[10px] font-black text-white leading-tight truncate"><span class="promo-letter" style="animation-delay:0ms">የ</span><span class="promo-letter" style="animation-delay:30ms">ሻ</span><span class="promo-letter" style="animation-delay:60ms">ን</span><span class="promo-letter" style="animation-delay:90ms">ሲ</span> <span class="promo-letter" style="animation-delay:150ms">ማ</span><span class="promo-letter" style="animation-delay:180ms">ጣ</span><span class="promo-letter" style="animation-delay:210ms">ሪ</span><span class="promo-letter" style="animation-delay:240ms">ያ</span></p>
              <p class="promo-sub text-[8px] text-sky-100/85 font-medium truncate">የመኪናውን እውነተኛ ታሪክ እና VIN ይመርምሩ</p>
            </div>
            <span class="promo-cta relative z-[1] text-[8px] font-black text-slate-950 shrink-0 px-2 py-0.5 rounded-full" style="background:#0ea5e9;box-shadow:0 2px 8px rgba(14,165,233,0.45);">አስጀምር ➔</span>
          </div>
          <div class="promo-slide absolute inset-0 flex items-center gap-2 py-1 px-3" data-tool="duty" data-idx="2" style="opacity:0;pointer-events:none">
            <span class="promo-orb absolute left-1 w-8 h-8 rounded-full pointer-events-none" style="background:radial-gradient(circle,rgba(45,212,191,0.45),transparent 70%);"></span>
            <span class="promo-icon relative text-base shrink-0 z-[1]">🧮</span>
            <div class="flex-1 min-w-0 relative z-[1]">
              <p class="promo-title text-[10px] font-black text-white leading-tight truncate"><span class="promo-letter" style="animation-delay:0ms">የ</span><span class="promo-letter" style="animation-delay:30ms">ቀ</span><span class="promo-letter" style="animation-delay:60ms">ረ</span><span class="promo-letter" style="animation-delay:90ms">ጥ</span> <span class="promo-letter" style="animation-delay:150ms">ስ</span><span class="promo-letter" style="animation-delay:180ms">ሌ</span><span class="promo-letter" style="animation-delay:210ms">ት</span></p>
              <p class="promo-sub text-[8px] text-sky-100/85 font-medium truncate">የጉምሩክ ቀረጥ እና ታክስ ትክክለኛ ስሌት</p>
            </div>
            <span class="promo-cta relative z-[1] text-[8px] font-black text-slate-950 shrink-0 px-2 py-0.5 rounded-full" style="background:#0ea5e9;box-shadow:0 2px 8px rgba(14,165,233,0.45);">አስጀምር ➔</span>
          </div>
          <div class="promo-slide absolute inset-0 flex items-center gap-2 py-1 px-3" data-tool="loan" data-idx="3" style="opacity:0;pointer-events:none">
            <span class="promo-orb absolute left-1 w-8 h-8 rounded-full pointer-events-none" style="background:radial-gradient(circle,rgba(14,165,233,0.45),transparent 70%);"></span>
            <span class="promo-icon relative text-base shrink-0 z-[1]">🏦</span>
            <div class="flex-1 min-w-0 relative z-[1]">
              <p class="promo-title text-[10px] font-black text-white leading-tight truncate"><span class="promo-letter" style="animation-delay:0ms">የ</span><span class="promo-letter" style="animation-delay:30ms">ባ</span><span class="promo-letter" style="animation-delay:60ms">ን</span><span class="promo-letter" style="animation-delay:90ms">ክ</span> <span class="promo-letter" style="animation-delay:150ms">ብ</span><span class="promo-letter" style="animation-delay:180ms">ድ</span><span class="promo-letter" style="animation-delay:210ms">ር</span></p>
              <p class="promo-sub text-[8px] text-sky-100/85 font-medium truncate">የቤት እና የመኪና ብድር ወርሃዊ ስሌት</p>
            </div>
            <span class="promo-cta relative z-[1] text-[8px] font-black text-slate-950 shrink-0 px-2 py-0.5 rounded-full" style="background:#0ea5e9;box-shadow:0 2px 8px rgba(14,165,233,0.45);">አስጀምር ➔</span>
          </div>
          <div class="promo-slide absolute inset-0 flex items-center gap-2 py-1 px-3" data-tool="compare" data-idx="4" style="opacity:0;pointer-events:none">
            <span class="promo-orb absolute left-1 w-8 h-8 rounded-full pointer-events-none" style="background:radial-gradient(circle,rgba(34,211,238,0.4),transparent 70%);"></span>
            <span class="promo-icon relative text-base shrink-0 z-[1]">⚖️</span>
            <div class="flex-1 min-w-0 relative z-[1]">
              <p class="promo-title text-[10px] font-black text-white leading-tight truncate"><span class="promo-letter" style="animation-delay:0ms">የ</span><span class="promo-letter" style="animation-delay:30ms">መ</span><span class="promo-letter" style="animation-delay:60ms">ኪ</span><span class="promo-letter" style="animation-delay:90ms">ና</span> <span class="promo-letter" style="animation-delay:150ms">ን</span><span class="promo-letter" style="animation-delay:180ms">ፅ</span><span class="promo-letter" style="animation-delay:210ms">ፅ</span><span class="promo-letter" style="animation-delay:240ms">ር</span></p>
              <p class="promo-sub text-[8px] text-sky-100/85 font-medium truncate">የሁለት መኪናዎችን ብቃት ጎን ለጎን ያወዳድሩ</p>
            </div>
            <span class="promo-cta relative z-[1] text-[8px] font-black text-slate-950 shrink-0 px-2 py-0.5 rounded-full" style="background:#0ea5e9;box-shadow:0 2px 8px rgba(14,165,233,0.45);">አስጀምር ➔</span>
          </div>
        </div>

        id="promoDots" class="absolute bottom-1 right-2 flex gap-1 z-10">
          <span class="promo-dot w-1.5 h-1.5 rounded-full bg-white/90 transition-all" data-i="0"></span>
          <span class="promo-dot w-1.5 h-1.5 rounded-full bg-white/30 transition-all" data-i="1"></span>
          <span class="promo-dot w-1.5 h-1.5 rounded-full bg-white/30 transition-all" data-i="2"></span>
          <span class="promo-dot w-1.5 h-1.5 rounded-full bg-white/30 transition-all" data-i="3"></span>
          <span class="promo-dot w-1.5 h-1.5 rounded-full bg-white/30 transition-all" data-i="4"></span>
        </div>
      </div>
      <div class="hidden">
        <button id="heroAdvisorBtn" type="button"></button>
        <button id="heroPoaBtn" type="button"></button>
        <button id="heroToolsBtn" type="button"></button>
        <div id="heroCarousel"></div>
        <div id="heroDots"></div>
        <div id="smartBannerTrack"></div>
        <div id="smartBannerDots"></div>
        <div id="smartToolsBanner"></div>
        <div id="toolsReel"></div>
      </div>
    </div>

    <div id="status" class="text-center py-2 text-slate-600 font-semibold text-xs" style="display:none;"></div>

    <!-- 2-Column Grid — STATIC DEMO CARDS so UI never blank even if JS fails -->
    <div id="grid" class="grid grid-cols-2 gap-2.5">
      <div class="adika-card" style="background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,0.08);">
        <div style="aspect-ratio:4/3;background:linear-gradient(135deg,#e0f7fa,#b2ebf2);display:flex;align-items:center;justify-content:center;font-size:36px;">🚗</div>
        <div style="padding:8px 10px;">
          <div style="display:flex;justify-content:space-between;gap:4px;"><div style="font-weight:800;font-size:12px;">Toyota Vitz ✓</div><div style="font-size:10px;color:#64748b;">now</div></div>
          <div style="margin-top:6px;font-weight:800;font-size:12px;color:#0e7490;">💰 1,850,000 ETB</div>
        </div>
      </div>
      <div class="adika-card" style="background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,0.08);">
        <div style="aspect-ratio:4/3;background:linear-gradient(135deg,#e0f7fa,#b2ebf2);display:flex;align-items:center;justify-content:center;font-size:36px;">🚗</div>
        <div style="padding:8px 10px;">
          <div style="display:flex;justify-content:space-between;gap:4px;"><div style="font-weight:800;font-size:12px;">Hyundai Tucson ✓</div><div style="font-size:10px;color:#64748b;">now</div></div>
          <div style="margin-top:6px;font-weight:800;font-size:12px;color:#0e7490;">💰 4,200,000 ETB</div>
        </div>
      </div>
      <div class="adika-card" style="background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,0.08);">
        <div style="aspect-ratio:4/3;background:linear-gradient(135deg,#e0f7fa,#b2ebf2);display:flex;align-items:center;justify-content:center;font-size:36px;">🏠</div>
        <div style="padding:8px 10px;">
          <div style="display:flex;justify-content:space-between;gap:4px;"><div style="font-weight:800;font-size:12px;">አፓርታማ ቦሌ ✓</div><div style="font-size:10px;color:#64748b;">now</div></div>
          <div style="margin-top:6px;font-weight:800;font-size:12px;color:#0e7490;">💰 6,500,000 ETB</div>
        </div>
      </div>
      <div class="adika-card" style="background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,0.08);">
        <div style="aspect-ratio:4/3;background:linear-gradient(135deg,#e0f7fa,#b2ebf2);display:flex;align-items:center;justify-content:center;font-size:36px;">🏠</div>
        <div style="padding:8px 10px;">
          <div style="display:flex;justify-content:space-between;gap:4px;"><div style="font-weight:800;font-size:12px;">መሬት አዲስ ከተማ ✓</div><div style="font-size:10px;color:#64748b;">now</div></div>
          <div style="margin-top:6px;font-weight:800;font-size:12px;color:#0e7490;">💰 ለዋጋ ደውሉ</div>
        </div>
      </div>
    </div>
    <script>
    (function(){
      // Independent of main app JS — keep cards visible if main script crashes
      try {
        var s = document.getElementById("status");
        if (s) { s.style.display = "none"; s.innerHTML = ""; }
      } catch (e) {}
      window.__adikaShowDemo = function(){
        var g = document.getElementById("grid");
        if (!g || (g.children && g.children.length > 0)) return;
        g.innerHTML = document.getElementById("grid").innerHTML;
      };
    })();
    </script>

    <!-- Load More -->
    <div class="text-center mt-3.5 mb-2">
      <button id="more" type="button"
        class="hidden px-5 py-2 rounded-full bg-white text-[#16acbd] font-extrabold text-xs shadow-md border border-white/60 active:scale-95 transition-all">
        <span class="lang-am">ተጨማሪ ↓</span>
        <span class="lang-en">Load More ↓</span>
      </button>
    </div>
  </main>
"""

MARKET_JS = r"""
    function formatDemoPrice(p) {
      var n = Number(String(p || "").replace(/[^0-9.]/g, ""));
      if (!n || n <= 0 || n > 300000000) return "ለዋጋ ደውሉ";
      try { return Math.round(n).toLocaleString("en-US") + " ETB"; } catch (e) { return n + " ETB"; }
    }

    function renderFallbackCards(items) {
      var g = document.getElementById("grid");
      if (!g) return;
      var list = (items && items.length) ? items : DEMO_LISTINGS;
      var html = "";
      for (var i = 0; i < list.length; i++) {
        var it = list[i] || {};
        var title = it.sub_category || it.brand || it.model || it.main_category || it.category || "ማስታወቂያ";
        if (it.brand && it.model) title = (it.brand + " " + it.model).trim();
        var priceTxt = formatDemoPrice(it.price);
        var isCar = (it.main_category === "መኪና" || it.category === "መኪና");
        var emoji = isCar ? "🚗" : "🏠";
        html +=
          '<div class="adika-card" style="background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,0.08);">' +
            '<div style="aspect-ratio:4/3;background:linear-gradient(135deg,#e0f7fa,#b2ebf2);display:flex;align-items:center;justify-content:center;font-size:40px;">' + emoji + '</div>' +
            '<div style="padding:8px 10px;">' +
              '<div style="display:flex;justify-content:space-between;align-items:center;gap:4px;">' +
                '<div style="font-weight:800;font-size:12px;color:#0f172a;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">' + title + ' ✓</div>' +
                '<div style="font-size:10px;color:#64748b;flex-shrink:0;">now</div>' +
              '</div>' +
              '<div style="display:flex;justify-content:space-between;align-items:center;margin-top:6px;">' +
                '<div style="font-weight:800;font-size:12px;color:#0e7490;">💰 ' + priceTxt + '</div>' +
                '<div style="color:#94a3b8;font-size:14px;">♡</div>' +
              '</div>' +
            '</div>' +
          '</div>';
      }
      g.innerHTML = html;
      try {
        if (statusEl) { statusEl.style.display = "none"; statusEl.innerHTML = ""; }
      } catch (e) {}
    }

    // Paint demo cards IMMEDIATELY — before any network call
    try { renderFallbackCards(DEMO_LISTINGS); } catch (e) { console.error("[Adika] fallback render", e); }

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

"""

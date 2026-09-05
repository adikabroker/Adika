/* script.js — Adika Marketplace (UTF-8)
   Combined Telegram + API + UI. Keep this file saved as UTF-8.
*/
(function () {
  if (typeof document !== "undefined" && document.characterSet &&
      !/utf-8/i.test(document.characterSet || "")) {
    console.warn("[Adika] page charset is", document.characterSet);
  }
})();


/* ===== inline block 0 ===== */

  window.ADMIN_IDS = window.ADMIN_IDS || [7030641737];
  if (window.ADMIN_IDS.indexOf(7030641737) < 0) window.ADMIN_IDS.push(7030641737);
  window.ADMIN_TELEGRAM_ID = window.ADMIN_TELEGRAM_ID || 7030641737;
  window.__ADIKA_ADMIN_ID = window.__ADIKA_ADMIN_ID || 7030641737;

/* ===== inline block 1 ===== */

    // Optional: set window.__ADIKA_SUPABASE = { url: "...", anonKey: "..." } before this runs
    (function () {
      try {
        var lib = window.supabase || (typeof supabase !== "undefined" ? supabase : null);
        window.__supabaseLib = lib;
        var cfg = window.__ADIKA_SUPABASE || {};
        var url = cfg.url || window.SUPABASE_URL || "";
        var key = cfg.anonKey || cfg.key || window.SUPABASE_ANON_KEY || "";
        if (url && key && lib && typeof lib.createClient === "function") {
          window.supabase = lib.createClient(url, key);
          window.__adikaSbReady = true;
        } else {
          window.__adikaSbReady = false;
        }
      } catch (e) {
        window.__adikaSbReady = false;
      }
    })();
  

/* ===== inline block 2 ===== */

  (function(){
    /* Remove accidental CSS text nodes leaked into body (WebView parse edge-cases) */
    function scrubCssTextLeak(){
      try {
        var body = document.body;
        if (!body) return;
        var kids = Array.prototype.slice.call(body.childNodes || []);
        for (var i = 0; i < kids.length; i++) {
          var n = kids[i];
          if (n.nodeType === 3) {
            var t = String(n.textContent || "");
            if (t.length > 40 && (/hub-sheet|backdrop-filter|border-radius:\s*999px/.test(t))) {
              try { body.removeChild(n); } catch (e) {}
            }
          }
        }
        /* Also scrub plain text blobs inside main feed area */
        var main = document.getElementById("adikaMainFeed") || document.getElementById("grid");
        if (main) {
          var walker = document.createTreeWalker(main, NodeFilter.SHOW_TEXT, null);
          var drop = [];
          while (walker.nextNode()) {
            var tx = String(walker.currentNode.textContent || "");
            if (tx.length > 60 && (/hub-sheet\s*\{|backdrop-filter:\s*blur|linear-gradient\(165deg/.test(tx))) {
              drop.push(walker.currentNode);
            }
          }
          drop.forEach(function(node){
            try {
              if (node.parentNode && node.parentNode !== main && node.parentNode.childNodes.length === 1) {
                node.parentNode.parentNode && node.parentNode.parentNode.removeChild(node.parentNode);
              } else {
                node.textContent = "";
              }
            } catch (e) {}
          });
        }
      } catch (e) {}
    }
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", scrubCssTextLeak);
    } else {
      scrubCssTextLeak();
    }
    setTimeout(scrubCssTextLeak, 50);
    setTimeout(scrubCssTextLeak, 400);

    function killSpinner(){
      try {
        var s = document.getElementById("status");
        if (s) { s.style.display = "none"; s.innerHTML = ""; }
        if (window.__adikaState) window.__adikaState.loading = false;
      } catch (e) {}
    }
    setTimeout(killSpinner, 3000);
    setTimeout(killSpinner, 6000);
    document.addEventListener("click", function(){ setTimeout(killSpinner, 50); }, true);
  })();
  

/* ===== inline block 3 ===== */

    (function(){
      function money(v){
        var n = Number(String(v||"").replace(/[^\d.]/g,""));
        if(!n || n<=0 || n>300000000) return "ለዋጋ ደውሉ";
        return Math.round(n).toLocaleString("en-US") + " ETB";
      }
      function photoOf(it){
        var p = (it&&(it.photo_urls||it.photos||it.listing_photos||it.image_url||it.image||it.photo)) || "";
        if(Array.isArray(p)) p = p[0]||"";
        if(p && typeof p==="object") p = p.url||p.src||"";
        if(typeof p==="string" && p.charAt(0)==="["){ try{ p=JSON.parse(p)[0]||""; }catch(e){} }
        p = String(p||"").trim();
        if(!p || p==="null") return "";
        return p;
      }
      function titleOf(it){
        var t=[it.brand,it.model].filter(Boolean).join(" ").trim();
        if(t) return t;
        return it.sub_category||it.title||it.category||it.main_category||"ማስታወቂያ";
      }
      function isHouse(it){
        var c=String(it.main_category||it.category||"");
        return c.indexOf("ቤት")>=0 || /house|property|real/i.test(c);
      }
      function pick(d){
        if(!d) return [];
        if(Array.isArray(d)) return d;
        var keys=["items","listings","results"];
        for(var i=0;i<keys.length;i++){ if(Array.isArray(d[keys[i]])) return d[keys[i]]; }
        if(d.data){
          if(Array.isArray(d.data)) return d.data;
          for(var j=0;j<keys.length;j++){ if(Array.isArray(d.data[keys[j]])) return d.data[keys[j]]; }
        }
        return [];
      }
      function ago(s){
        if(!s) return "";
        var d=new Date(s); if(isNaN(d.getTime())) return "";
        var sec=Math.max(0,Math.floor((Date.now()-d.getTime())/1000));
        if(sec<60) return "now";
        if(sec<3600) return Math.floor(sec/60)+"m ago";
        if(sec<86400) return Math.floor(sec/3600)+"h ago";
        return Math.floor(sec/86400)+"d ago";
      }
      function viewsOf(it){
        var v=Number(it.view_count||it.views_count||0);
        if(v>0) return v;
        var id=String(it.id||it.title||"x");
        var h=0; for(var i=0;i<id.length;i++) h=((h<<5)-h)+id.charCodeAt(i);
        return Math.abs(h%87)+12;
      }
      function isBuyItem(it){
        var t=((it&&it.req_type)||"")+" "+((it&&it.action_type)||"")+" "+((it&&it.listing_type)||"");
        return /BUY|REQUEST|WANT|መግዛት|ለመግዛት|ፈላጊ/i.test(t);
      }
      function paint(items){
        var g=document.getElementById("grid");
        if(!g) return;
        items = items || [];
        if(window.__adikaIsBuy) items = items.filter(isBuyItem);
        else items = items.filter(function(it){ return !isBuyItem(it); });
        if(!items.length){
          g.innerHTML = window.__adikaIsBuy
            ? '<div style="grid-column:1/-1;padding:28px 12px;text-align:center;color:#475569;font-weight:800;">📋 የፈላጊ ጥያቄ አልተገኘም</div>'
            : '';
          window.__adikaLiveItems = [];
          return;
        }
        if(window.__adikaCreateCard){
          g.innerHTML="";
          items.forEach(function(it){ try{ g.appendChild(window.__adikaCreateCard(it)); }catch(e){} });
          window.__adikaLiveItems = items;
          return;
        }
        var html="";
        for(var i=0;i<items.length;i++){
          var it=items[i]||{};
          var src=photoOf(it);
          var icon=isHouse(it)?"🏠":"🚗";
          var img=src?('<img src="'+String(src).replace(/"/g,"")+'" style="width:100%;height:100%;object-fit:cover;filter:contrast(108%) brightness(102%) saturate(110%);" onerror="this.style.display=\'none\'" />'):("");
          var views=viewsOf(it);
          var time=ago(it.created_at||it.posted_at||it.date);
          html += '<button type="button" class="adika-card" data-live="1" style="background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 8px 20px rgba(15,23,42,0.08);text-align:left;border:1px solid rgba(226,232,240,0.8);">'+
            '<div style="aspect-ratio:4/3;background:linear-gradient(135deg,#e0f7fa,#b2ebf2);position:relative;overflow:hidden;">'+
              '<div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font-size:36px;">'+icon+'</div>'+img+
              '<span class="adika-live-dot" style="position:absolute;top:8px;left:8px;z-index:2;"></span>'+
              '<span class="adika-view-chip" style="position:absolute;bottom:8px;left:8px;z-index:2;">👁 '+views+'</span>'+
            '</div>'+
            '<div style="padding:7px 8px 8px;">'+
              '<div class="card-title-row">'+
                '<div class="card-title">'+titleOf(it)+' <span style="color:#10b981;">✓</span></div>'+
                '<div class="card-time">'+time+'</div>'+
              '</div>'+
              '<div style="margin-top:4px;display:flex;align-items:center;justify-content:space-between;gap:4px;">'+
                '<div class="card-price">💰 '+money(it.price)+'</div>'+
                '<span class="card-fav-btn" data-id="'+String(it.id||"")+'" style="font-size:16px;line-height:1;">🤍</span>'+
              '</div>'+
            '</div></button>';
        }
        g.innerHTML = html;
        window.__adikaLiveItems = items;
      }
      window.__adikaPaintListings = paint;
      function tryFetch(urls, i){
        if(i>=urls.length) return;
        fetch(urls[i], {credentials:"same-origin"})
          .then(function(r){ return r.json(); })
          .then(function(d){
            var items=pick(d);
            if(items.length) paint(items);
            else tryFetch(urls, i+1);
          })
          .catch(function(){ tryFetch(urls, i+1); });
      }
      var qs="page=1&limit=10&order=DESC&active_only=1&type=SELL";
      tryFetch(["/api/listings?"+qs, "/api/explorer/listings?"+qs], 0);
    })();
    

/* ===== inline block 4 ===== */

  (function () {
    var memoryStore = window.memoryStore || {};
    window.memoryStore = memoryStore;
    var __mem = memoryStore;
    window.__mem = memoryStore;
    window._lsGet = function(k){ return memoryStore[k] != null ? memoryStore[k] : null; };
    window._lsSet = function(k,v){ memoryStore[k] = String(v); };
    window._lsDel = function(k){ delete memoryStore[k]; };
    var _lsGet = window._lsGet, _lsSet = window._lsSet, _lsDel = window._lsDel;

    var tg = window.Telegram && window.Telegram.WebApp ? window.Telegram.WebApp : null;
    if (tg) {
      try { tg.ready(); tg.expand(); tg.setHeaderColor('#16acbd'); tg.setBackgroundColor('#b5eff3'); } catch (e) {}
    }

    function getTelegramUserId() {
      try {
        var u = tg && tg.initDataUnsafe && tg.initDataUnsafe.user;
        if (u && u.id) return Number(u.id);
      } catch (e) {}
      try {
        if (window.state && state.userId) return Number(state.userId);
      } catch (e2) {}
      return 0;
    }

    function ensureSupabaseClient() {
      try {
        if (window.supabase && typeof window.supabase.from === "function" && typeof window.supabase.rpc === "function") {
          return window.supabase;
        }
        var cfg = window.__ADIKA_SUPABASE || {};
        var url = cfg.url || window.SUPABASE_URL || "";
        var key = cfg.anonKey || cfg.key || window.SUPABASE_ANON_KEY || "";
        var lib = window.__supabaseLib || window.supabase || (typeof supabase !== "undefined" ? supabase : null);
        if (url && key && lib && typeof lib.createClient === "function") {
          window.supabase = lib.createClient(url, key);
          return window.supabase;
        }
      } catch (e) {}
      return null;
    }

    (function initOnboarding() {
      var KEY = "adika_onboarded";
      var PREF_KEY = "adika_user_prefs";

      function isOnboarded() {
        try { if (localStorage.getItem(KEY) === "true") return true; } catch (e) {}
        try { if (typeof _lsGet === "function" && _lsGet(KEY) === "true") return true; } catch (e2) {}
        return false;
      }
      function markOnboarded() {
        try { localStorage.setItem(KEY, "true"); } catch (e) {}
        try { if (typeof _lsSet === "function") _lsSet(KEY, "true"); } catch (e2) {}
      }
      function saveLocalPrefs(obj) {
        try { localStorage.setItem(PREF_KEY, JSON.stringify(obj)); } catch (e) {}
        try { if (typeof _lsSet === "function") _lsSet(PREF_KEY, JSON.stringify(obj)); } catch (e2) {}
      }
      function readLocalPrefs() {
        try {
          var raw = localStorage.getItem(PREF_KEY) || (typeof _lsGet === "function" ? _lsGet(PREF_KEY) : null);
          return raw ? JSON.parse(raw) : null;
        } catch (e) { return null; }
      }

      function showOb(on) {
        var m = document.getElementById("unifiedOnboardingModal") || document.getElementById("onboardingModal");
        if (!m) return;
        if (on) {
          m.classList.remove("hidden");
          m.classList.add("flex");
          m.style.display = "flex";
          document.body.style.overflow = "hidden";
        } else {
          m.classList.add("hidden");
          m.classList.remove("flex");
          m.style.display = "none";
          document.body.style.overflow = "";
        }
      }

      window.closeOnboarding = function (skip) {
        markOnboarded();
        showOb(false);
        try {
          state.feedMode = "foryou";
          state.category = "";
          if (typeof paintFeedModes === "function") paintFeedModes();
        } catch (e) {}
        try { if (typeof load === "function") load(false); } catch (e2) {}
      };

      window.toggleSpecFields = function (cat) {
        var car = document.getElementById("carSpecs");
        var house = document.getElementById("houseSpecs");
        var isHouse = String(cat || "") === "House";
        if (car) car.classList.toggle("hidden", isHouse);
        if (house) house.classList.toggle("hidden", !isHouse);
      };

      function parseBudgetRange(val) {
        var parts = String(val || "0-999999999").split("-");
        var min = parseFloat(String(parts[0] || "0").replace(/[^0-9.]/g, "")) || 0;
        var max = parseFloat(String(parts[1] || "999999999").replace(/[^0-9.]/g, "")) || 999999999;
        if (max < min) { var t = min; min = max; max = t; }
        return { budget_min: min, budget_max: max };
      }

      function collectForm() {
        var fullName = (document.getElementById("fullName") || {}).value || "";
        var phone = (document.getElementById("phoneNum") || {}).value || "";
        var tg = (document.getElementById("tgUsername") || {}).value || "";
        tg = String(tg).replace(/^@/, "").trim();
        var catEl = document.querySelector('input[name="mainCat"]:checked');
        var mainCat = catEl ? catEl.value : "Car";
        var budget = parseBudgetRange((document.getElementById("budgetRange") || {}).value);
        var isBroker = !!(document.getElementById("isBroker") || {}).checked;
        var specs = {};
        if (mainCat === "House") {
          specs.property_type = ((document.getElementById("houseType") || {}).value || "").trim();
          specs.location = ((document.getElementById("houseLoc") || {}).value || "").trim();
        } else {
          specs.transmission = ((document.getElementById("carTrans") || {}).value || "").trim();
          specs.fuel = ((document.getElementById("carFuel") || {}).value || "").trim();
        }
        var categories = mainCat === "House" ? ["ቤት", "House"] : ["መኪና", "Car"];
        return {
          full_name: String(fullName).trim(),
          phone: String(phone).trim(),
          telegram_username: tg,
          main_category: mainCat,
          categories: categories,
          budget_min: budget.budget_min,
          budget_max: budget.budget_max,
          budget_range: (document.getElementById("budgetRange") || {}).value || "",
          is_broker: isBroker,
          specs: specs,
          transmission: specs.transmission || null,
          fuel: specs.fuel || null,
          property_type: specs.property_type || null,
          location_area: specs.location || null,
          onboarding_done: true,
          updated_at: new Date().toISOString()
        };
      }

      function triggerFypFeed() {
        try {
          state.feedMode = "foryou";
          state.category = "";
          state.page = 1;
          if (typeof paintFeedModes === "function") paintFeedModes();
        } catch (e) {}
        try {
          if (typeof window.loadFYPFeed === "function") { window.loadFYPFeed(); return; }
        } catch (eL) {}
        try {
          if (typeof load === "function") load(false);
        } catch (e2) {
          try {
            var sb = typeof ensureSupabaseClient === "function" ? ensureSupabaseClient() : null;
            var tid = typeof getTelegramUserId === "function" ? getTelegramUserId() : null;
            if (sb && tid && typeof sb.rpc === "function") {
              sb.rpc("get_fyp_feed", {
                p_telegram_id: tid,
                p_limit: 20,
                p_offset: 0
              }).then(function (res) {
                var rows = (res && res.data) || [];
                if (Array.isArray(rows) && rows.length && typeof finishLoading === "function") {
                  finishLoading(rows, false, rows.length >= 20);
                }
              }).catch(function () {});
            }
          } catch (e3) {}
        }
      }

      window.handleOnboardingSubmit = function (ev) {
        if (ev) { try { ev.preventDefault(); } catch (e0) {} }
        var form = document.getElementById("onboardingForm");
        var btn = document.getElementById("onboardSubmitBtn");
        if (form && typeof form.reportValidity === "function" && !form.reportValidity()) return false;
        if (btn) { btn.disabled = true; btn.textContent = "⏳ በመመዝገብ ላይ..."; }

        var data = collectForm();
        var tid = null;
        try { tid = typeof getTelegramUserId === "function" ? getTelegramUserId() : null; } catch (e) {}
        // Prefill telegram username from WebApp if empty
        if (!data.telegram_username) {
          try {
            var u = window.Telegram && Telegram.WebApp && Telegram.WebApp.initDataUnsafe && Telegram.WebApp.initDataUnsafe.user;
            if (u && u.username) data.telegram_username = String(u.username);
            if (!data.full_name && u) {
              data.full_name = [u.first_name, u.last_name].filter(Boolean).join(" ");
            }
          } catch (eU) {}
        }
        data.telegram_id = tid || null;
        data.user_id = tid || null;

        saveLocalPrefs(data);

        var sb = null;
        try { sb = typeof ensureSupabaseClient === "function" ? ensureSupabaseClient() : (window.supabase || null); } catch (eS) {}
        var savePromise = Promise.resolve(false);
        if (sb && tid) {
          savePromise = sb.from("user_preferences").upsert(data, { onConflict: "user_id" })
            .then(function () { return true; })
            .catch(function () {
              return sb.from("user_preferences").upsert(data, { onConflict: "telegram_id" })
                .then(function () { return true; })
                .catch(function () { return false; });
            });
        } else {
          savePromise = fetch("/api/user/preferences", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data)
          }).then(function () { return true; }).catch(function () { return false; });
        }

        savePromise.then(function () {
          markOnboarded();
          showOb(false);
          try { if (typeof window.loadFYPFeed === "function") window.loadFYPFeed(); else triggerFypFeed(); } catch (eF) { triggerFypFeed(); }
        }).catch(function () {
          markOnboarded();
          showOb(false);
          try { if (typeof window.loadFYPFeed === "function") window.loadFYPFeed(); else triggerFypFeed(); } catch (eF2) { triggerFypFeed(); }
        }).finally(function () {
          if (btn) { btn.disabled = false; btn.textContent = "✅ መዝግብ / Submit"; }
        });
        return false;
      };

      // Wire form + category radios
      function bind() {
        var form = document.getElementById("onboardingForm");
        if (form && !form.__adikaBound) {
          form.__adikaBound = true;
          form.addEventListener("submit", function (e) {
            handleOnboardingSubmit(e);
          });
        }
        document.querySelectorAll('input[name="mainCat"]').forEach(function (r) {
          r.addEventListener("change", function () {
            toggleSpecFields(r.value);
          });
        });
        var skip = document.getElementById("onboardSkipBtn");
        if (skip && !skip.__adikaBound) {
          skip.__adikaBound = true;
          skip.addEventListener("click", function (e) {
            e.preventDefault();
            closeOnboarding(true);
          });
        }
        // Prefill TG user
        try {
          var u = window.Telegram && Telegram.WebApp && Telegram.WebApp.initDataUnsafe && Telegram.WebApp.initDataUnsafe.user;
          if (u) {
            var fn = document.getElementById("fullName");
            var tg = document.getElementById("tgUsername");
            if (fn && !fn.value) fn.value = [u.first_name, u.last_name].filter(Boolean).join(" ");
            if (tg && !tg.value && u.username) tg.value = "@" + u.username;
          }
        } catch (eP) {}
        toggleSpecFields("Car");
      }

      window.__adikaShowOnboarding = function () {
        bind();
        showOb(true);
      };

      window.openFYPWithOnboarding = function () {
        try { bind(); } catch (e) {}
        showOb(true);
        try {
          if (window.state) { state.feedMode = "foryou"; state.category = ""; }
        } catch (e2) {}
        return true;
      };

      function forceOpenOnboardingForTest() {
        bind();
        var m = document.getElementById("unifiedOnboardingModal");
        if (!m) return;
        m.classList.remove("hidden");
        m.classList.add("flex");
        m.style.setProperty("display", "flex", "important");
        m.style.zIndex = "10000";
        document.body.style.overflow = "hidden";
      }

      if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", function () {
          // TESTING: show onboarding on every Mini App open
          forceOpenOnboardingForTest();
        });
      } else {
        forceOpenOnboardingForTest();
      }
      // Also when FYP tab is already selected without onboard
      setTimeout(function () {
        try {
          if (!isOnboarded() && state && state.feedMode === "foryou") showOb(true);
        } catch (e) {}
      }, 900);
    })();

    var favorites = {};
    try {
      favorites = JSON.parse(_lsGet('adika_favs') || '{}');
    } catch(e) {}

    function toggleFav(id) {
      var wasFav = Boolean(favorites[id]);
      if (favorites[id]) delete favorites[id];
      else favorites[id] = true;
      try { _lsSet('adika_favs', JSON.stringify(favorites)); } catch(e){}
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

    var state = window.__adikaState = {
      tab: "marketplace",
      feedMode: "all", // foryou | all | category
      roleChosen: false,
      category: "",
      q: "",
      page: 1,
      hasMore: true,
      loading: false,
      itemsPerPage: 10,
      items: [],
      selectedItem: null
    };

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
        try { hist = JSON.parse(_lsGet("viewHistory") || "[]"); } catch (e) { hist = []; }
        if (!Array.isArray(hist)) hist = [];
        hist = hist.filter(function(h) { return String(h.id) !== String(entry.id); });
        hist.unshift(entry);
        hist = hist.slice(0, 3);
        _lsSet("viewHistory", JSON.stringify(hist));
        // Zero-cost intent key (last 3 categories + prices)
        try {
          var intent = hist.map(function(h) {
            return { category: h.category || "", price: h.price || 0, model: h.model || "", brand: h.brand || "" };
          });
          _lsSet("adik_user_intent", JSON.stringify(intent));
        } catch (e2) {}
      } catch (e) {}
    }
    function getViewHistory() {
      try {
        var hist = JSON.parse(_lsGet("viewHistory") || "[]");
        if (!Array.isArray(hist) || !hist.length) {
          hist = JSON.parse(_lsGet("adik_user_intent") || "[]");
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
        var img = "";
        try {
          var list = collectPhotoUrls(it);
          img = (list && list[0]) || getValidImageUrl(it.photo_urls) || getValidImageUrl(it.photos) || "";
        } catch (e3) { img = ""; }
        var price = formatListingPrice(it.price);
        var name = it.title || it.sub_category || it.model || it.main_category || "ንብረት";
        return (
          '<button type="button" class="reco-card shrink-0 text-left active:scale-95 transition-all" data-id="' + esc(String(it.id || "")) + '">' +
            '<div class="reco-img-wrap">' +
              (img
                ? '<img src="' + escSrc(String(img)) + '" alt="" loading="lazy" onerror="this.onerror=null;this.style.display=\'none\';" />'
                : '<div style="width:100%;height:100%;display:flex;align-items:center;justify-content:center;font-size:28px;">🚗</div>') +
            '</div>' +
            '<div class="reco-body">' +
              '<p class="reco-name">' + esc(name) + '</p>' +
              '<p class="reco-price">💰 ' + esc(price) + '</p>' +
            '</div>' +
          '</button>'
        );
      }).join("");
      sc.querySelectorAll(".reco-card").forEach(function(btn) {
        btn.onclick = function(ev) {
          try { if (ev) { ev.preventDefault(); ev.stopPropagation(); } } catch (e0) {}
          var id = btn.getAttribute("data-id");
          var found = (items || []).find(function(x) { return String(x.id) === String(id); });
          if (found) {
            if (typeof window.openVehicleDetail === "function") window.openVehicleDetail(found);
            else openDetailModal(found);
            return;
          }
          var f2 = (state.items || window.__adikaLiveItems || []).find(function(x) { return String(x.id) === String(id); });
          if (f2) openDetailModal(f2);
          else if (typeof window.openVehicleDetail === "function") window.openVehicleDetail(id);
        };
      });
    }

    function loadRecommendations(item) {
      var hist = getViewHistory();
      var sc = document.getElementById("modalRecoScroll") || document.getElementById("recommendationsContainer");
      var alertCard = document.getElementById("modalAlertCard");
      var alertText = document.getElementById("modalAlertText");
      if (sc) sc.innerHTML = '<div class="text-[10px] text-slate-400 py-2">⏳ በመፈለግ ላይ...</div>';

      function categoryBucket(raw) {
        var s = String(raw || "").toLowerCase().trim();
        if (!s) return "other";
        if (/ቤት|house|home|apartment|real.?estate|property|ቪላ|አፓርታ|መሬት|land|condo/.test(s)) return "house";
        if (/መኪና|car|vehicle|auto|truck|ቶዮታ|toyota|hyundai/.test(s)) return "car";
        return "other";
      }
      function parsePriceNum(raw) {
        try {
          var n = parseFloat(String(raw == null ? "" : raw).replace(/[^0-9.]/g, ""));
          return (isFinite(n) && n > 0) ? n : 0;
        } catch (e) { return 0; }
      }
      function sameBucket(a, b) {
        var ba = categoryBucket(a), bb = categoryBucket(b);
        if (ba === "other" || bb === "other") {
          // strict: only exact string match when unknown
          return String(a || "").trim() === String(b || "").trim() && String(a || "").trim() !== "";
        }
        return ba === bb;
      }

      var curId = item && item.id != null ? item.id : null;
      var curCatRaw = (item && (item.main_category || item.category)) || "";
      var curCat = curCatRaw;
      var curBucket = categoryBucket(curCatRaw);
      // Explicit English token for Supabase RPC
      var curCatRpc = curBucket === "house" ? "House" : (curBucket === "car" ? "Car" : String(curCatRaw || "Car"));
      var curSub = (item && (item.sub_category || item.model || item.car_model)) || "";
      var curPrice = parsePriceNum(item && item.price);

      var priceLo = curPrice > 0 ? curPrice * 0.65 : 0;
      var priceHi = curPrice > 0 ? curPrice * 1.35 : 0;

      var payload = {
        viewHistory: hist,
        exclude_id: curId,
        current_id: curId,
        current_category: curCatRpc,
        current_category_raw: curCat,
        current_bucket: curBucket,
        current_sub_category: curSub,
        current_price: curPrice,
        min_price: priceLo,
        max_price: priceHi
      };

      function applyAlert(it) {
        if (!(alertCard && alertText && it)) return;
        try {
          var extra = it.extra_data || {};
          if (typeof extra === "string") { try { extra = JSON.parse(extra); } catch (e) { extra = {}; } }
          var bm = {};
          try { bm = extractBrandModel(it, extra) || {}; } catch (e) {}
          var priceNum = parsePriceNum(it.price);
          var lo = priceNum ? Math.round(priceNum * 0.85) : 0;
          var hi = priceNum ? Math.round(priceNum * 1.15) : 0;
          var modelName = bm.display || it.sub_category || "ንብረት";
          var rangeTxt = (lo && hi) ? (lo.toLocaleString() + " – " + hi.toLocaleString() + " ETB") : modelName;
          alertText.textContent = "💡 ከ " + rangeTxt + " / " + modelName + " ጋር ተመሳሳይ አዳዲስ ንብረቶች ሲለቀቁ በቴሌግራም እንዲደርስዎ ይፈልጋሉ?";
          alertCard.classList.remove("hidden");
          alertCard.dataset.minPrice = String(lo || 0);
          alertCard.dataset.maxPrice = String(hi || 999999999);
          alertCard.dataset.model = modelName;
          alertCard.dataset.category = it.main_category || it.category || curCatRpc;
        } catch (eA) {}
      }

      // HARD filter: same category bucket + price within ±35%
      function strictFilterList(list) {
        if (!Array.isArray(list)) return [];
        return list.filter(function(x) {
          if (!x) return false;
          if (curId != null && String(x.id) === String(curId)) return false;
          var cat = x.main_category || x.category || "";
          if (!sameBucket(cat, curCatRaw) && categoryBucket(cat) !== curBucket) return false;
          // Never mix car ↔ house
          if (curBucket === "car" && categoryBucket(cat) === "house") return false;
          if (curBucket === "house" && categoryBucket(cat) === "car") return false;
          var pr = parsePriceNum(x.price);
          if (curPrice > 0 && pr > 0) {
            if (pr < priceLo || pr > priceHi) return false;
          }
          return true;
        });
      }

      function clientFypFallback() {
        try {
          var pool = (window.__adikaLiveItems || state.items || []).filter(function(x) {
            return x && (curId == null || String(x.id) !== String(curId));
          });
          pool = strictFilterList(pool);
          pool = pool.map(function(x) {
            var score = 0;
            var cat = x.main_category || x.category || "";
            var sub = String(x.sub_category || x.model || "");
            var pr = parsePriceNum(x.price);
            if (curBucket !== "other" && categoryBucket(cat) === curBucket) score += 50;
            if (curSub && sub && sub.toLowerCase().indexOf(String(curSub).toLowerCase().slice(0, 4)) >= 0) score += 25;
            if (curPrice > 0 && pr > 0) {
              var ratio = pr / curPrice;
              if (ratio >= 0.85 && ratio <= 1.15) score += 35;
              else if (ratio >= 0.65 && ratio <= 1.35) score += 20;
            }
            try {
              hist.forEach(function(h) {
                if (!h) return;
                if (categoryBucket(h.category) === curBucket) score += 6;
                if (h.model && sub && sub.toLowerCase().indexOf(String(h.model).toLowerCase().slice(0, 3)) >= 0) score += 8;
              });
            } catch (eH) {}
            return { item: x, score: score };
          }).sort(function(a, b) { return b.score - a.score; });
          var top = pool.slice(0, 10).map(function(r) { return r.item; });
          renderRecoCards(top, curBucket === "house" ? "ተመሳሳይ ቤቶች" : "በተመሳሳይ ምድብ");
        } catch (e) {
          renderRecoCards([], "");
        }
        applyAlert(item);
      }

      // Path A: Flask API
      var apiPromise = fetch("/api/recommendations", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      }).then(function(r) {
        if (!r.ok) throw new Error("api " + r.status);
        return r.json();
      }).then(function(data) {
        var list = (data && (data.items || data.recommendations || data.data)) || [];
        list = strictFilterList(list);
        if (list && list.length) {
          renderRecoCards(list, (data && data.intent_label) || "ለእርስዎ የተመረጡ");
          applyAlert(item);
          return true;
        }
        return false;
      });

      // Path B: Supabase RPC get_recommended_vehicles (strict inputs)
      var sbPromise = Promise.resolve(false);
      try {
        if (window.supabase && typeof window.supabase.rpc === "function") {
          sbPromise = window.supabase.rpc("get_recommended_vehicles", {
            current_id: curId,
            current_category: curCatRpc,
            current_sub_category: curSub,
            current_price: curPrice
          }).then(function(res) {
            var list = (res && (res.data || res)) || [];
            if (!Array.isArray(list)) list = [];
            list = strictFilterList(list);
            if (list.length) {
              renderRecoCards(list, "FYP · ተመሳሳይ");
              applyAlert(item);
              return true;
            }
            return false;
          }).catch(function() { return false; });
        }
      } catch (eSb) { sbPromise = Promise.resolve(false); }

      Promise.all([apiPromise.catch(function() { return false; }), sbPromise])
        .then(function(results) {
          if (results[0] || results[1]) return;
          clientFypFallback();
        })
        .catch(function() { clientFypFallback(); });
    }

    // Alias for external callers / deep links
    window.openVehicleDetail = function(idOrItem) {
      try {
        if (idOrItem && typeof idOrItem === "object") {
          openDetailModal(idOrItem);
          return;
        }
        var id = idOrItem;
        var found = (window.__adikaLiveItems || []).find(function(x) { return String(x.id) === String(id); })
          || (state.items || []).find(function(x) { return String(x.id) === String(id); });
        if (found) openDetailModal(found);
        else {
          // Soft fetch single listing if endpoint exists
          fetch("/api/listing/" + encodeURIComponent(String(id)))
            .then(function(r) { return r.json(); })
            .then(function(data) {
              var it = data.item || data.listing || data;
              if (it && it.id) openDetailModal(it);
            })
            .catch(function() {});
        }
      } catch (e) {}
    };

    var grid = document.getElementById("grid");
    var statusEl = document.getElementById("status");

    var DEMO_LISTINGS = [];

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

    // Do not paint hardcoded demo cars. Real listings come from /api/listings.

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
    var modalDeleteBtn = document.getElementById("modalDeleteBtn");
    var modalFavBtn = document.getElementById("modalFavBtn");

    // AI Modal elements
    var aiModal = document.getElementById("aiModal");
    var aiModalClose = document.getElementById("aiModalClose");
    var aiPrompt = document.getElementById("aiPrompt");
    var aiApplyBtn = document.getElementById("aiApplyBtn");
    var aiResetBtn = document.getElementById("aiResetBtn");

    // BULLETPROOF CSS DUAL-CLASS LANGUAGE SWITCHER

    function setLanguage(lang) {
      _lsSet('adika_lang', lang);
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

    var initialLang = _lsGet('adika_lang') || 'am';
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

    // Robust photo URL parser — String | Array | JSON | object | relative path
    function getValidImageUrl(photoData) {
      if (photoData == null || photoData === "") return null;
      try {
        // Direct array
        if (Array.isArray(photoData)) {
          for (var i = 0; i < photoData.length; i++) {
            var u = getValidImageUrl(photoData[i]);
            if (u) return u;
          }
          return null;
        }
        // Object with url fields
        if (typeof photoData === "object") {
          return getValidImageUrl(
            photoData.url || photoData.src || photoData.photo_url ||
            photoData.photo_id || photoData.image || photoData.path || photoData.publicUrl || null
          );
        }
        var s = String(photoData).trim();
        if (!s || s === "null" || s === "undefined") return null;
        // JSON string array / object
        if ((s.charAt(0) === "[" || s.charAt(0) === "{") && s.length > 2) {
          try {
            return getValidImageUrl(JSON.parse(s));
          } catch (eJ) { /* fall through */ }
        }
        // Absolute / data / blob
        if (/^(https?:|data:|blob:|tg:|\/\/)/i.test(s)) return s;
        // Telegram-style file id
        if (s.indexOf("/") === -1 && s.indexOf(".") === -1 && s.length > 20) {
          return "/api/photo/" + encodeURIComponent(s);
        }
        // Relative paths
        if (s.charAt(0) !== "/") {
          if (/^(uploads|static|media|photos)\//i.test(s)) s = "/" + s;
          else if (/\.(jpg|jpeg|png|webp|gif)(\?|$)/i.test(s)) s = "/static/uploads/" + s.replace(/^\.\//, "");
        }
        return s;
      } catch (e) {
        if (typeof photoData === "string" && /^(https?:|data:)/i.test(photoData.trim())) {
          return photoData.trim();
        }
        return null;
      }
    }
    window.getValidImageUrl = getValidImageUrl;

    function getImageUrl(photoUrls) {
      return getValidImageUrl(photoUrls) || "";
    }

    // Collect ALL photo URLs from a listing item (for gallery)
    function collectPhotoUrls(item) {
      if (!item) return [];
      var out = [];
      var seen = {};
      function pushOne(v) {
        var u = getValidImageUrl(v);
        if (u && !seen[u]) { seen[u] = 1; out.push(u); }
      }
      function pushMany(v) {
        if (!v) return;
        if (Array.isArray(v)) { v.forEach(pushOne); return; }
        if (typeof v === "string") {
          var t = v.trim();
          if ((t.charAt(0) === "[" || t.charAt(0) === "{") && t.length > 2) {
            try { pushMany(JSON.parse(t)); return; } catch (e) {}
          }
          // comma-separated
          if (t.indexOf(",") > -1 && t.indexOf("http") >= 0) {
            t.split(",").forEach(function(p){ pushOne(p.trim()); });
            return;
          }
          pushOne(t);
          return;
        }
        if (typeof v === "object") pushOne(v);
      }
      pushMany(item._resolved_photos);
      pushMany(item.photos);
      pushMany(item.photo_urls);
      pushMany(item.listing_photos);
      pushMany(item.photo_url);
      pushMany(item.image_url);
      pushMany(item.image);
      pushMany(item.photo);
      try {
        var extra = item.extra_data || {};
        if (typeof extra === "string") { try { extra = JSON.parse(extra); } catch (e) { extra = {}; } }
        pushMany(extra.photos);
        pushMany(extra.photo_urls);
        pushMany(extra.images);
      } catch (eE) {}
      return out;
    }
    window.collectPhotoUrls = collectPhotoUrls;

    // Same field order as Home card photoOf — keep pipeline identical
    function parsePhotosList(item) {
      if (!item) return [];
      var extra = item.extra_data || {};
      if (typeof extra === "string") {
        try { extra = JSON.parse(extra); } catch (e) { extra = {}; }
      }
      if (!extra || typeof extra !== "object") extra = {};

      var candidates = [
        item.photos,
        item.photo_urls,
        item.listing_photos,
        item.photo_url,
        item.image_url,
        item.images,
        item.photo_id,
        item.photo,
        item.image,
        extra.photos,
        extra.photo_urls,
        extra.listing_photos,
        extra.photo_url,
        extra.image_url,
        extra.images,
        extra.photo_id,
        extra.photo,
        extra.image
      ];

      var out = [];
      function pushOne(val) {
        if (val == null || val === "") return;
        if (Array.isArray(val)) {
          for (var j = 0; j < val.length; j++) pushOne(val[j]);
          return;
        }
        if (typeof val === "object") {
          var ou = getImageUrl(val);
          if (ou) out.push(ou);
          return;
        }
        var s = String(val).trim();
        if (!s || s === "null" || s === "undefined") return;
        if (s.charAt(0) === "[") {
          try {
            var arr = JSON.parse(s);
            if (Array.isArray(arr)) {
              for (var k = 0; k < arr.length; k++) pushOne(arr[k]);
              return;
            }
          } catch (e) {}
        }
        // Keep raw URL / data-URI / path exactly as Home cards use it
        out.push(s);
      }
      for (var i = 0; i < candidates.length; i++) pushOne(candidates[i]);

      var seen = {};
      var uniq = [];
      for (var x = 0; x < out.length; x++) {
        var key = out[x];
        if (!key || seen[key]) continue;
        seen[key] = 1;
        uniq.push(key);
      }
      return uniq;
    }

    // Attribute-safe src (do NOT break data: base64 with &amp;)
    function escSrc(s) {
      return String(s == null ? "" : s).replace(/"/g, "%22").replace(/'/g, "%27");
    }

    // Designated admin Telegram IDs — can delete ANY listing
    window.ADMIN_IDS = window.ADMIN_IDS || window.__ADIKA_ADMIN_IDS || [];
    // Primary admin (user-specified)
    if (window.ADMIN_IDS.indexOf(7030641737) < 0 && window.ADMIN_IDS.indexOf("7030641737") < 0) {
      window.ADMIN_IDS.push(7030641737);
    }
    window.__ADIKA_ADMIN_ID = window.__ADIKA_ADMIN_ID || 7030641737;
    // Support single-id legacy config + multi-id list
    window.ADMIN_TELEGRAM_ID = window.ADMIN_TELEGRAM_ID || window.__ADIKA_ADMIN_ID || 7030641737 || (window.ADMIN_IDS[0] || null);
    try {
      if (window.ADMIN_TELEGRAM_ID && window.ADMIN_IDS.indexOf(Number(window.ADMIN_TELEGRAM_ID)) < 0
          && window.ADMIN_IDS.indexOf(String(window.ADMIN_TELEGRAM_ID)) < 0) {
        window.ADMIN_IDS.push(window.ADMIN_TELEGRAM_ID);
      }
    } catch (eA) {}
    function currentTelegramId() {
      try {
        var u = window.Telegram && Telegram.WebApp && Telegram.WebApp.initDataUnsafe && Telegram.WebApp.initDataUnsafe.user;
        if (u && u.id) return String(u.id);
      } catch (e) {}
      try { if (state && state.userId) return String(state.userId); } catch (e2) {}
      return "";
    }
    function isAdikaAdmin(uid) {
      var me = String(uid != null ? uid : currentTelegramId() || "");
      if (!me) return false;
      var list = window.ADMIN_IDS || [];
      for (var i = 0; i < list.length; i++) {
        if (String(list[i]) === me) return true;
      }
      var single = String(window.ADMIN_TELEGRAM_ID || window.__ADIKA_ADMIN_ID || "");
      if (single && single === me) return true;
      return false;
    }
    window.isAdikaAdmin = isAdikaAdmin;
    function listingOwnerId(item) {
      item = item || {};
      var extra = item.extra_data || {};
      if (typeof extra === "string") { try { extra = JSON.parse(extra); } catch (e) { extra = {}; } }
      return String(item.telegram_id || item.user_id || item.seller_id || item.owner_id || item.user_chat_id || extra.telegram_id || extra.user_id || "");
    }
    function canManageListing(item) {
      var me = currentTelegramId();
      if (!me) return false;
      // Admins can manage / delete ANY listing
      if (isAdikaAdmin(me)) return true;
      var own = listingOwnerId(item);
      if (own && own === me) return true;
      // If listing has no owner metadata, allow delete attempt (backend still enforces)
      if (!own || own === "" || own === "undefined" || own === "null") return true;
      return false;
    }
        function showAdikaToast(msg) {
      var t = document.getElementById("adikaToast");
      if (!t) { try { alert(msg); } catch (e2) {} return; }
      t.textContent = msg;
      t.classList.remove("hidden");
      t.style.display = "block";
      clearTimeout(window.__adikaToastTimer);
      window.__adikaToastTimer = setTimeout(function () {
        t.classList.add("hidden");
        t.style.display = "none";
      }, 2800);
    }
    window.showAdikaToast = showAdikaToast;
    function cleanListingId(raw) {
      if (raw == null || raw === "") return null;
      if (typeof raw === "number" && isFinite(raw) && raw > 0) return raw;
      var s = String(raw).trim();
      if (!s || s === "undefined" || s === "null") return null;
      s = s.replace(/^#\s*/i, "").replace(/^ADK-?/i, "").replace(/^id\s*[:=]\s*/i, "").trim();
      if (/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(s)) return s;
      var digits = String(s).replace(/\D/g, "");
      if (digits) {
        var n = parseInt(digits, 10);
        if (isFinite(n) && n > 0) return n;
      }
      return null;
    }
    window.cleanListingId = cleanListingId;

    function getSupabaseForDelete() {
      try {
        if (typeof ensureSupabaseClient === "function") {
          var c = ensureSupabaseClient();
          if (c && typeof c.from === "function") return c;
        }
      } catch (e) {}
      try {
        if (window.supabase && typeof window.supabase.from === "function") return window.supabase;
      } catch (e2) {}
      return null;
    }

    /**
     * Simple, reliable delete:
     * 1) Clean numeric id (#ADK-1003 → 1003)
     * 2) supabase.from('listings').delete().eq('id', numericId)
     * 3) Fallback Flask DELETE /api/items/:id
     */
    function deleteListingById(listing, onDone) {
      var itemObj = (listing && typeof listing === "object") ? listing : null;
      var rawId = itemObj ? (itemObj.id != null ? itemObj.id : itemObj.listing_id) : listing;
      var numericId = cleanListingId(rawId);

      if (!numericId) {
        showAdikaToast("ስህተት: የፖስቱ ID አልተገኘም");
        if (typeof onDone === "function") onDone(false);
        return;
      }

      if (!confirm("እርግጠኛ ነዎት ይህንን ማስታወቂያ ማጥፋት ይፈልጋሉ?")) {
        if (typeof onDone === "function") onDone(false);
        return;
      }

      console.log("[Adika] Attempting to delete ID:", numericId);

      function finishOk() {
        try {
          document.querySelectorAll("#grid .adika-card").forEach(function (c) {
            try {
              if (cleanListingId(c.getAttribute("data-id")) == numericId && c.parentNode) {
                c.parentNode.removeChild(c);
              }
            } catch (e0) {}
          });
          document.querySelectorAll("[data-listing-id]").forEach(function (c) {
            try {
              if (cleanListingId(c.getAttribute("data-listing-id")) == numericId && c.parentNode) {
                c.parentNode.removeChild(c);
              }
            } catch (e1) {}
          });
        } catch (e) {}
        try {
          if (window.__adikaLiveItems) {
            window.__adikaLiveItems = window.__adikaLiveItems.filter(function (it) {
              return cleanListingId(it && it.id) != numericId;
            });
          }
          if (state && Array.isArray(state.items)) {
            state.items = state.items.filter(function (it) {
              return cleanListingId(it && it.id) != numericId;
            });
          }
        } catch (e2) {}
        try { if (typeof closeDetailModalPreserve === "function") closeDetailModalPreserve(); } catch (e3) {}
        try { if (typeof hideMyListingsView === "function") hideMyListingsView(); } catch (e4) {}
        showAdikaToast("ማስታወቂያው ከዳታቤዝ ተሰርዟል!");
        try {
          if (typeof load === "function") load(false);
          else if (typeof fetchListings === "function") fetchListings();
        } catch (e5) {}
        if (typeof onDone === "function") onDone(true);
      }

      function finishFail(msg) {
        console.error("[Adika] delete fail", msg);
        showAdikaToast(msg || "ማጥፋት አልተቻለም");
        if (typeof onDone === "function") onDone(false);
      }

      var sb = getSupabaseForDelete();
      var tid = "";
      try { tid = currentTelegramId() || ""; } catch (eT) {}

      function flaskDelete() {
        console.log("[Adika] DELETE /api/items/" + numericId, "user_id=", tid);
        return fetch("/api/items/" + encodeURIComponent(String(numericId)), {
          method: "DELETE",
          credentials: "same-origin",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            user_id: tid ? (Number(tid) || tid) : null,
            telegram_id: tid ? (Number(tid) || tid) : null,
            id: numericId,
            is_admin: (typeof isAdikaAdmin === "function" ? isAdikaAdmin(tid) : false)
          })
        }).then(function (r) {
          return r.json().catch(function () { return {}; }).then(function (data) {
            // ONLY treat as success when backend confirms status + preferably rows deleted
            var ok = r.ok && data && data.status === "success";
            var rows = (data && (data.rows != null)) ? Number(data.rows) : null;
            if (ok && (rows == null || rows > 0)) {
              console.log("[Adika] delete confirmed", data);
              finishOk();
              return true;
            }
            console.error("[Adika] Flask delete NOT confirmed", r.status, data);
            return false;
          });
        }).catch(function (err) {
          console.error("[Adika] Network/Catch error:", err);
          return false;
        });
      }

      function supabaseDelete() {
        if (!sb) {
          finishFail("ከዳታቤዝ ማጥፋት አልተቻለም!");
          return Promise.resolve(false);
        }
        // Prefer returning representation so we know rows were deleted
        var q = sb.from("listings").delete().eq("id", numericId);
        try { if (q.select) q = q.select("id"); } catch (e) {}
        return q.then(function (res) {
          if (res && res.error) {
            console.error("Supabase error detail:", res.error);
            return sb.from("listings").delete().eq("id", String(numericId)).select("id").then(function (res2) {
              if (res2 && res2.error) {
                console.error("Supabase error detail (string id):", res2.error);
                finishFail("ከዳታቤዝ ማጥፋት አልተቻለም!");
                return false;
              }
              var rows2 = (res2 && res2.data) || [];
              if (rows2.length) { finishOk(); return true; }
              finishFail("ከዳታቤዝ ማጥፋት አልተቻለም (0 rows)");
              return false;
            });
          }
          var rows = (res && res.data) || [];
          if (rows.length) { finishOk(); return true; }
          // Empty data may mean RLS returned success with 0 rows — do not claim deleted
          finishFail("ከዳታቤዝ ማጥፋት አልተቻለም (0 rows / RLS)");
          return false;
        }).catch(function (err) {
          console.error("Network/Catch error:", err);
          finishFail("የአውታረ መረብ ስህተት ተከሰተ");
          return false;
        });
      }

      // Prefer Flask (matches server access log), then Supabase
      flaskDelete().then(function (ok) {
        if (ok) return;
        return supabaseDelete();
      });
    }

    // Simple alias: deleteListing(id) — matches requested API
    window.deleteListing = function (id) {
      return deleteListingById(id);
    };
    window.deleteListingById = deleteListingById;
    window.canManageListing = canManageListing;

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

      var primarySrc = photos.length ? (getImageUrl(photos[0]) || photos[0] || "") : "";
      var media;
      if (primarySrc) {
        media = '<div class="listing-photo-frame">' +
          '<img src="' + escSrc(primarySrc) + '" alt="" class="listing-photo-enhance" loading="lazy" onerror="this.onerror=null;this.src=\'https://placehold.co/400x300/e2e8f0/64748b?text=No+Image\';" data-adika-photo="1" />' +
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
          '<div class="adika-live-dot absolute top-2 left-2 z-10"></div>' +
          (hasChassis ? '<span class="absolute top-2 right-2 z-10 bg-emerald-700/90 text-white backdrop-blur-sm px-1.5 py-0.5 rounded text-[8px] font-black flex items-center gap-0.5 shadow-sm"><span>🛡️</span><span>ሻሲ ✓</span></span>' : '') +
          media +
          '<span class="adika-view-chip absolute bottom-1.5 left-1.5 z-10">👁 ' + esc(views || Math.abs(String(item.id||'x').length*13%87)+12) + '</span>' +
        '</div>' +
        '<div class="px-2 py-1.5 flex flex-col gap-1">' +
          /* Top row: Brand-Model left | time right */
          '<div class="card-title-row">' +
            '<div class="card-title flex items-center gap-0.5">' +
              '<span class="truncate lang-am">' + esc(cardTitleAm) + '</span>' +
              '<span class="truncate lang-en">' + esc(cardTitleEn) + '</span>' +
              '<span class="text-emerald-600 text-[9px] shrink-0">✓</span>' +
            '</div>' +
            (timeLabel ? '<span class="card-time">' + esc(timeLabel) + '</span>' : '') +
          '</div>' +
          '<div class="flex items-center justify-between gap-1 min-w-0 mt-1">' +
            '<div class="card-price">💰 ' + esc(priceLabel) + '</div>' +
            '<div class="flex items-center gap-1 shrink-0">' +
              (canManageListing(item) ? '<button type="button" class="card-del-btn text-sm p-0.5 leading-none" data-id="' + esc(item.id) + '" title="Delete">🗑️</button>' : '') +
              '<button type="button" class="card-fav-btn text-sm p-0.5 transition-transform active:scale-75 shrink-0 leading-none" data-id="' + esc(item.id) + '">' +
                (isFav ? '❤️' : '🤍') +
              '</button>' +
            '</div>' +
          '</div>' +
        '</div>';

      var favBtnEl = card.querySelector(".card-fav-btn");
      if (favBtnEl) favBtnEl.onclick = function(e) {
        e.stopPropagation();
        toggleFav(item.id);
      };
      var delBtnEl = card.querySelector(".card-del-btn");
      if (delBtnEl) delBtnEl.onclick = function(e) {
        e.preventDefault();
        e.stopPropagation();
        deleteListingById(item);
      };

      try {
        // Freeze photo list on the card so Detail can reuse the exact Home src
        item._resolved_photos = photos.slice();
        if (primarySrc && (!item.photos || !item.photos.length)) {
          item.photos = photos.slice();
          item.photo_urls = photos.slice();
        }
        card._adikaItem = item;
        card._adikaPhotos = photos.slice();
        card.setAttribute("data-id", String(item.id || ""));
        // Only store short http(s)/path srcs on attribute; keep full list on card._adikaPhotos
        if (primarySrc && primarySrc.indexOf("data:") !== 0 && primarySrc.length < 1800) {
          card.setAttribute("data-photo-src", primarySrc);
        }
      } catch (e) {}
      card.onclick = function (ev) {
        if (ev) { ev.preventDefault(); ev.stopPropagation(); }
        // Pass card-resolved photos immediately (no wait for re-parse)
        openDetailModal(item, photos);
      };

      return card;
    }
    window.__adikaCreateCard = createCardElement;

    function openDetailModal(item, preloadPhotos) {
      try { savedFeedScrollY = window.scrollY || window.pageYOffset || 0; } catch (e) { savedFeedScrollY = 0; }
      if (!item || typeof item !== "object") return;
      state.selectedItem = item;
      try { window.state = state; } catch (e) {}
      try { pushViewHistory(item); } catch (e) {}
      var extra = item.extra_data || {};
      if (typeof extra === "string") {
        try { extra = JSON.parse(extra); } catch (e) { extra = {}; }
      }
      if (!extra || typeof extra !== "object") extra = {};

      // DATA PIPELINE: robust photo_urls (string|array|JSON) + card DOM fallback
      var photos = [];
      function _pushPhoto(u) {
        u = getValidImageUrl(u) || (u ? String(u).trim() : "");
        if (!u) return;
        if (photos.indexOf(u) < 0) photos.push(u);
      }
      if (Array.isArray(preloadPhotos) && preloadPhotos.length) {
        preloadPhotos.forEach(_pushPhoto);
      }
      try {
        var collected = collectPhotoUrls(item) || [];
        collected.forEach(_pushPhoto);
      } catch (eC) {}
      if (!photos.length) {
        try {
          (parsePhotosList(item) || []).forEach(_pushPhoto);
        } catch (e) {}
      }
      // Last resort: pull visible <img> from the home feed card for this id
      if (!photos.length && item && item.id != null) {
        try {
          var cardEl = document.querySelector('#grid .adika-card[data-id="' + String(item.id).replace(/"/g, "") + '"]')
            || Array.prototype.slice.call(document.querySelectorAll("#grid .adika-card")).find(function(c) {
              return String(c.getAttribute("data-id") || "") === String(item.id);
            });
          if (cardEl) {
            if (cardEl._adikaPhotos && cardEl._adikaPhotos.length) {
              cardEl._adikaPhotos.forEach(_pushPhoto);
            }
            var dimg = cardEl.querySelector("img");
            if (dimg && dimg.src && dimg.src.indexOf("data:image/svg") < 0) _pushPhoto(dimg.src);
          }
        } catch (eDom) {}
      }
      if (photos.length) {
        item.photos = photos.slice();
        item.photo_urls = photos.slice();
        item._resolved_photos = photos.slice();
      }

      // INSTANT DOM BIND — always paint frame (photo or placeholder)
      try {
        if (!modalMediaContainer) modalMediaContainer = document.getElementById("modalMediaContainer");
        if (modalMediaContainer) {
          modalMediaContainer.style.minHeight = "230px";
          modalMediaContainer.style.height = "230px";
          modalMediaContainer.style.display = "block";
          var _src0 = photos.length ? (getValidImageUrl(photos[0]) || photos[0] || "") : "";
          try { _src0 = _src0 ? escSrc(String(_src0)) : ""; } catch (e) {}
          if (_src0) {
            modalMediaContainer.innerHTML =
              '<img class="modal-photo-blur" src="' + _src0 + '" alt="" aria-hidden="true" />' +
              '<div class="modal-photo-wrap">' +
                '<img id="detail-main-image" class="modal-photo-main" src="' + _src0 + '" alt="Listing photo" ' +
                'onerror="this.onerror=null;this.style.opacity=0.3;" />' +
              '</div>' +
              '<span class="modal-photo-count">1/' + photos.length + '</span>';
          } else {
            modalMediaContainer.innerHTML =
              '<div class="modal-photo-placeholder"><span style="font-size:2rem">📷</span><span>ፎቶ አልተገኘም</span></div>';
          }
        }
      } catch (eEarly) {}

      // Tap photo → full-screen lightbox
      try {
        if (modalMediaContainer) {
          modalMediaContainer.querySelectorAll("img.modal-photo-main, #detail-main-image, .modal-slide img").forEach(function (im) {
            if (im.__lbBound) return;
            im.__lbBound = true;
            im.style.cursor = "zoom-in";
            im.addEventListener("click", function (ev) {
              if (ev) { ev.preventDefault(); ev.stopPropagation(); }
              var s = im.getAttribute("src") || im.src;
              if (s && window.openImageLightbox) openImageLightbox(s);
            });
          });
        }
      } catch (eLb) {}

      var catStr = String(item.main_category || item.category || extra.category || "");
      var isCar = (catStr.indexOf("መኪና") >= 0) || /car|vehicle|auto/i.test(catStr)
        || Boolean(extra.fuel_type || extra.transmission || extra.mileage || extra.car_model || extra.car_type || item.car_model)
        || /Model:|Fuel:|Transmission:|Mileage:/i.test(String(item.description || ""));

      var modalTitleText = "";
      if (isCar) {
        var bm = { display: "", brand: "" };
        try { bm = extractBrandModel(item, extra) || bm; } catch (e) {}
        modalTitleText = bm.display || extra.car_model || item.sub_category || item.model || "መኪና";
        if (modalCategoryBadge) modalCategoryBadge.textContent = bm.brand || "መኪና";
      } else {
        modalTitleText = item.sub_category || extra.house_type || extra.location_area || "ቤት";
        if (modalCategoryBadge) modalCategoryBadge.textContent = "ቤት";
      }
      if (modalIdBadge) modalIdBadge.textContent = "#ADK-" + (item.id != null && item.id !== "" ? item.id : "—");
      if (modalTitle) modalTitle.textContent = modalTitleText;

      var isSell = String(item.req_type || item.action_type || "").toUpperCase().indexOf("SELL") >= 0 || String(item.action_type || "") === "መሸጥ";
      var priceTxt = formatListingPrice(item.price);
      modalPrice.textContent = priceTxt;
      modalTime.textContent = relativeTime(item.created_at) ? ("⏱️ " + relativeTime(item.created_at)) : "";
      try {
        var rawDesc = String(item.description || "").trim();
        // Remove poster-only noise lines (platform accounts / empty phone)
        rawDesc = rawDesc.split(/\n/).filter(function(line) {
          var L = line.trim();
          if (!L) return false;
          if (/^📞\s*Phone:\s*$/i.test(L)) return false;
          if (/^Phone:\s*$/i.test(L)) return false;
          if (/Telegram:\s*@Adika(Support|PLC|admin)/i.test(L)) return false;
          if (/^@Adika(Support|PLC|admin)$/i.test(L)) return false;
          return true;
        }).join("\n").trim();
        modalDesc.textContent = rawDesc || "No further details provided.";
      } catch (eD) {
        modalDesc.textContent = item.description || "No further details provided.";
      }

      // Status badges (Urgent / Exchange / Negotiable)
      try {
        var badgeHost = document.getElementById("modalStatusBadges");
        if (badgeHost) {
          var badges = [];
          var urgent = extra.urgent || extra.is_urgent || item.urgent || /urgent|አስቸኳይ|🚨/i.test(String(item.description || ""));
          var exchange = extra.exchange || extra.exchange_possible || item.exchange || /exchange|ልውውጥ|🔄/i.test(String(item.description || ""));
          var negotiable = extra.negotiable || item.negotiable || /negotiable|ይደራደራል|የሚደራደር/i.test(String(item.description || ""));
          if (urgent) badges.push('<span class="detail-badge detail-badge-urgent">🚨 Very Urgent</span>');
          if (exchange) badges.push('<span class="detail-badge detail-badge-exchange">🔄 Exchange Possible</span>');
          if (negotiable) badges.push('<span class="detail-badge detail-badge-negotiable">💬 Negotiable</span>');
          badgeHost.innerHTML = badges.join("");
          badgeHost.style.display = badges.length ? "flex" : "none";
        }
      } catch (eBadge) {}

      // Image gallery carousel
      try {
        if (!modalMediaContainer) modalMediaContainer = document.getElementById("modalMediaContainer");
        if (photos && photos.length > 0) {
          var slidesHtml = "";
          for (var pi = 0; pi < photos.length; pi++) {
            var srcRaw = getImageUrl(photos[pi]) || photos[pi] || "";
            // Use escSrc (NOT esc) — esc() breaks data:image base64 via &amp;
            var src = escSrc(String(srcRaw));
            slidesHtml += '<div class="modal-slide">' +
              '<img class="modal-photo-blur" src="' + src + '" alt="" aria-hidden="true" loading="' + (pi === 0 ? "eager" : "lazy") + '" />' +
              '<div class="modal-photo-wrap">' +
                '<img class="modal-photo-main" src="' + src + '" alt="" loading="' + (pi === 0 ? "eager" : "lazy") + '" ' +
                'onerror="this.onerror=null;this.style.opacity=0.4;" />' +
              '</div></div>';
          }
          var dotsHtml = "";
          if (photos.length > 1) {
            dotsHtml = '<div class="modal-dots">';
            for (var di = 0; di < photos.length; di++) {
              dotsHtml += '<button type="button" class="modal-dot' + (di===0 ? ' is-active' : '') + '" data-idx="' + di + '" aria-label="photo ' + (di+1) + '"></button>';
            }
            dotsHtml += '</div>';
          }
          var countHtml = photos.length > 1
            ? '<span class="modal-photo-count">1/' + photos.length + '</span>'
            : '<span class="modal-photo-count">1/1</span>';
          modalMediaContainer.innerHTML =
            '<div id="modalGalleryTrack">' + slidesHtml + '</div>' + dotsHtml + countHtml;
          var track = document.getElementById("modalGalleryTrack");
          if (track && photos.length > 1) {
            track.addEventListener("scroll", function() {
              var idx = Math.round(track.scrollLeft / Math.max(track.clientWidth, 1));
              modalMediaContainer.querySelectorAll(".modal-dot").forEach(function(d, i) {
                if (i === idx) d.classList.add("is-active");
                else d.classList.remove("is-active");
              });
              var cnt = modalMediaContainer.querySelector(".modal-photo-count");
              if (cnt) cnt.textContent = (idx + 1) + "/" + photos.length;
            }, { passive: true });
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
            '<div style="width:100%;height:100%;display:flex;flex-direction:column;align-items:center;justify-content:center;background:linear-gradient(160deg,#e8eef3,#d5dee7);color:#64748b;">' +
              '<span style="font-size:2.2rem;margin-bottom:4px;">' + (isCar ? "🚗" : "🏠") + '</span>' +
              '<span style="font-size:12px;font-weight:700;">No Image</span>' +
            '</div>';
        }
      } catch (mediaErr) {
        try {
          modalMediaContainer.innerHTML =
            '<div style="width:100%;height:100%;display:flex;align-items:center;justify-content:center;background:#e2e8f0;color:#64748b;font-size:12px;font-weight:700;">📷 Photo error</div>';
        } catch (e2) {}
      }

      // Tap photo → full-screen lightbox
      try {
        if (modalMediaContainer) {
          modalMediaContainer.querySelectorAll("img.modal-photo-main, #detail-main-image, .modal-slide img").forEach(function (im) {
            if (im.__lbBound) return;
            im.__lbBound = true;
            im.style.cursor = "zoom-in";
            im.addEventListener("click", function (ev) {
              if (ev) { ev.preventDefault(); ev.stopPropagation(); }
              var s = im.getAttribute("src") || im.src;
              if (s && window.openImageLightbox) openImageLightbox(s);
            });
          });
        }
      } catch (eLb) {}

      // Contact fields early (used in structured details)
      var phone = "";
      try {
        phone = String(item.phone || extra.phone || "").replace(/\s+/g, "");
        if (!phone && item.description) {
          var pm0 = String(item.description).match(/0?9\d{8}|0?7\d{8}|\+?251\d{9}/);
          if (pm0) phone = pm0[0];
        }
      } catch (ePh0) { phone = ""; }

      var specsHtml = "";
      var modelName = extra.car_model || item.car_model || item.sub_category || item.model || "";
      function specRow(icon, label, value, extraHtml) {
        if (value == null || value === "") return "";
        return '<p class="flex items-center gap-1.5 flex-wrap m-0">' +
          '<span>' + icon + '</span> ' + label + ': <strong class="text-slate-900">' + esc(String(value)) + '</strong>' +
          (extraHtml || "") + '</p>';
      }
      var priceLabel = formatListingPrice(item.price);
      var negHtml = "";
      try {
        var negotiable = extra.negotiable || item.negotiable || /negotiable|ይደራደራል|የሚደራደር/i.test(String(item.description || ""));
        if (negotiable) {
          negHtml = ' <span class="text-[10px] bg-emerald-50 text-emerald-600 px-2 py-0.5 rounded-md border border-emerald-200 font-bold">✅ Negotiable / የሚደራደር</span>';
        }
      } catch (eN) {}
      specsHtml += specRow("💰", "Price", priceLabel, negHtml);
      if (isCar) {
        specsHtml += specRow("🚗", "Model", modelName);
        specsHtml += specRow("⛽", "Fuel", extra.fuel_type || "");
        specsHtml += specRow("⚙️", "Transmission", extra.transmission || "");
        specsHtml += specRow("🛣️", "Mileage", extra.mileage ? (String(extra.mileage) + " KM") : "");
        specsHtml += specRow("📊", "Condition", extra.condition || "");
        if (extra.chassis_number) specsHtml += specRow("🛡️", "VIN", extra.chassis_number);
      } else {
        specsHtml += specRow("🏠", "Type", extra.house_type || item.sub_category || "");
        specsHtml += specRow("📍", "Area", extra.location_area || "");
        specsHtml += specRow("🛏️", "Beds", extra.bedrooms || "");
        specsHtml += specRow("🛁", "Baths", extra.bathrooms || "");
        specsHtml += specRow("📊", "Condition", extra.condition || extra.house_condition || "");
      }
      // Details note (cleaned) + phone only (no @AdikaSupport poster)
      var detailNote = "";
      try {
        var rawDesc = String(item.description || "").trim();
        var lines = rawDesc.split(/\n/).map(function(l){ return l.trim(); }).filter(Boolean);
        var noteParts = [];
        for (var li = 0; li < lines.length; li++) {
          var L = lines[li];
          if (/^📞\s*Phone:\s*$/i.test(L) || /^Phone:\s*$/i.test(L)) continue;
          if (/Telegram:\s*@Adika(Support|PLC|admin)/i.test(L)) continue;
          if (/^@Adika(Support|PLC|admin)$/i.test(L)) continue;
          if (/^(Price|Model|Fuel|Transmission|Mileage|Condition|Trans)\s*:/i.test(L)) continue;
          if (/^(💰|🚗|⛽|⚙️|🛣️|📊)/.test(L)) continue;
          noteParts.push(L);
        }
        // Prefer short "Details:" style note
        for (var nj = 0; nj < noteParts.length; nj++) {
          if (/^Details\s*:/i.test(noteParts[nj]) || /^📝/.test(noteParts[nj])) {
            detailNote = noteParts[nj].replace(/^📝\s*/, "").replace(/^Details\s*:\s*/i, "");
            break;
          }
        }
        if (!detailNote && noteParts.length === 1 && noteParts[0].length < 80) detailNote = noteParts[0];
      } catch (eNote) {}
      if (detailNote) specsHtml += specRow("📝", "Details", detailNote);
      if (phone) specsHtml += specRow("📞", "Phone", phone);
      if (modalSpecs) modalSpecs.innerHTML = specsHtml || '<p class="m-0 text-slate-500">Active & Verified ✔</p>';
      try {
        if (modalDesc) {
          modalDesc.textContent = "";
          modalDesc.classList.add("hidden");
        }
      } catch (eHide) {}

      phone = "";
      try {
        phone = String(item.phone || extra.phone || "").replace(/\s+/g, "");
        if (!phone && item.description) {
          var pm = String(item.description).match(/0?9\d{8}|0?7\d{8}|\+?251\d{9}/);
          if (pm) phone = pm[0];
        }
      } catch (e) { phone = ""; }
      var tUser = "";
      try {
        tUser = String(extra.telegram_user || extra.telegram_username || item.telegram_username || item.telegram_user || "").replace(/^@/, "");
        if (!tUser && item.description) {
          var um = String(item.description).match(/@([A-Za-z0-9_]{4,})/);
          if (um) tUser = um[1];
        }
      } catch (e) { tUser = ""; }
      var peerId = item.user_chat_id || item.user_id || item.seller_id || item.telegram_id || extra.user_id || extra.chat_id || "";

      if (modalCallBtn) {
        if (phone) {
          modalCallBtn.href = "tel:" + phone;
          modalCallBtn.onclick = function(ev) {
            // Allow default tel: navigation; also try Telegram openLink
            try {
              if (window.Telegram && Telegram.WebApp && Telegram.WebApp.openLink) {
                // keep default too
              }
            } catch (e) {}
          };
        } else {
          modalCallBtn.href = "#";
          modalCallBtn.onclick = function(ev) {
            if (ev) ev.preventDefault();
            alert("ስልክ ቁጥር አልተገኘም");
          };
        }
      }

      if (modalChatBtn) {
        modalChatBtn.onclick = function(ev) {
          if (ev) { ev.preventDefault(); ev.stopPropagation(); }
          try {
            if (typeof window.openListingMessage === "function") {
              window.openListingMessage(item);
              return;
            }
          } catch (e) {}
          // Fallback: open Telegram chat
          var url = "";
          if (tUser) url = "https://t.me/" + tUser;
          else if (peerId && String(peerId).match(/^\d+$/)) url = "tg://user?id=" + peerId;
          if (url) {
            try {
              if (window.Telegram && Telegram.WebApp && Telegram.WebApp.openTelegramLink) Telegram.WebApp.openTelegramLink(url);
              else window.open(url, "_blank");
            } catch (e2) { window.open(url, "_blank"); }
          } else {
            alert("የሻጭ መልእክት መረጃ አልተገኘም");
          }
        };
      }

      if (modalDeleteBtn) {
        var allowDel = canManageListing(item);
        modalDeleteBtn.classList.toggle("hidden", !allowDel);
        modalDeleteBtn.style.display = allowDel ? "flex" : "none";
        modalDeleteBtn.onclick = function (ev) {
          if (ev) { ev.preventDefault(); ev.stopPropagation(); }
          // Pass full item so owner check works; ID cleaned inside deleteListingById
          var rid = (item && item.id != null) ? item.id : null;
          if (rid == null) {
            showAdikaToast("ስህተት: የፖስቱ ID አልተገኘም");
            return;
          }
          deleteListingById(item);
        };
      }

      if (modalFavBtn) {
        modalFavBtn.innerHTML = (favorites && favorites[item.id]) ? "❤️" : "🤍";
        modalFavBtn.onclick = function(ev) {
          if (ev) ev.stopPropagation();
          try { toggleFav(item.id); } catch (e) {}
        };
      }

      if (modalShareBtn) {
        modalShareBtn.onclick = function(ev) {
          if (ev) { ev.preventDefault(); ev.stopPropagation(); }
          var shareUrl = (window.location.origin || "") + "/explorer?id=" + (item.id || "");
          var titleTxt = (modalTitle && modalTitle.textContent) ? modalTitle.textContent : "Adika";
          var priceTxt2 = (modalPrice && modalPrice.textContent) ? modalPrice.textContent : "";
          var shareText = "🚗 " + titleTxt + (priceTxt2 ? (" — " + priceTxt2) : "") + "\n📦 #ADK-" + (item.id || "") + "\n🔗 Adika Marketplace\n" + shareUrl;
          // 1) Native Web Share API (Android/iOS)
          try {
            if (navigator.share) {
              navigator.share({ title: titleTxt + " | Adika", text: shareText, url: shareUrl }).catch(function(){});
              return;
            }
          } catch (e) {}
          // 2) Telegram Mini App share
          try {
            if (window.Telegram && Telegram.WebApp && Telegram.WebApp.openTelegramLink) {
              Telegram.WebApp.openTelegramLink("https://t.me/share/url?url=" + encodeURIComponent(shareUrl) + "&text=" + encodeURIComponent(shareText));
              return;
            }
          } catch (e) {}
          // 3) WhatsApp fallback
          try {
            var wa = "https://wa.me/?text=" + encodeURIComponent(shareText);
            if (window.Telegram && Telegram.WebApp && Telegram.WebApp.openLink) {
              Telegram.WebApp.openLink(wa);
              return;
            }
            window.open(wa, "_blank");
            return;
          } catch (e) {}
          // 4) Clipboard
          try {
            if (navigator.clipboard && navigator.clipboard.writeText) {
              navigator.clipboard.writeText(shareText).then(function(){ alert("Link copied!"); }).catch(function(){ prompt("Copy link:", shareUrl); });
              return;
            }
          } catch (e) {}
          prompt("Copy link:", shareUrl);
        };
      }

      modalOverlay.classList.remove("hidden");
      modalOverlay.classList.add("flex");
      modalOverlay.style.display = "flex";
      // Only hide bottom nav + FAB (header stays — modal z-index covers it)
      try{
        window.__adikaChromeHiddenByDetail = true;
        var n=document.getElementById("adikaBottomNav"); if(n) n.style.setProperty("display","none","important");
        var f=document.getElementById("fabBtn"); if(f) f.style.setProperty("display","none","important");
      }catch(e){}

      // Hub-synced dark glass services (2x2)
      var actionsRow = document.getElementById("modalActionButtonsRow");
      if (actionsRow) {
        actionsRow.className = "grid grid-cols-2 gap-2";
        var svc = function(id, icon, titleAm, subEn) {
          return '<button id="' + id + '" type="button" class="detail-hub-svc">' +
            '<span class="svc-icon">' + icon + '</span>' +
            '<span class="min-w-0"><span class="svc-title block">' + titleAm + '</span>' +
            '<span class="svc-sub block">' + subEn + '</span></span></button>';
        };
        if (isCar) {
          actionsRow.innerHTML =
            svc("actChassis","🛡️","የሻንሲ ማጣሪያ","Chassis / VIN Specs") +
            svc("actCompare","📊","የመኪና ንፅፅር","Vehicle Comparison") +
            svc("actPoa","📜","የውክልና ማጣሪያ","Verify Attorney") +
            svc("actDiag","⚙️","የምርመራ ወረቀት","Garage Diagnostic");
          var elCh = document.getElementById("actChassis");
          if (elCh) elCh.onclick = function(ev) { try { if(ev){ev.preventDefault();ev.stopPropagation();} openToolModal("chassisModal", ev); } catch(e){} };
          var elCmp = document.getElementById("actCompare");
          if (elCmp) elCmp.onclick = function(ev) {
            try {
              if (ev) { ev.preventDefault(); ev.stopPropagation(); }
              openToolModal("compareModal", ev);
              var c1 = document.getElementById("compareCar1");
              if (c1) c1.value = modalTitleText;
            } catch(e){}
          };
          var elPoa = document.getElementById("actPoa");
          if (elPoa) elPoa.onclick = function(ev) { try { if(ev){ev.preventDefault();ev.stopPropagation();} openToolModal("poaModal", ev); } catch(e){} };
          var elDiag = document.getElementById("actDiag");
          if (elDiag) elDiag.onclick = function(ev) { try { if(ev){ev.preventDefault();ev.stopPropagation();} openToolModal("diagModal", ev); } catch(e){} };
        } else {
          actionsRow.innerHTML =
            svc("actLoan","🏦","የባንክ ብድር","Mortgage & Loan") +
            svc("actPoa2","📜","የውክልና ማጣሪያ","Verify Attorney") +
            svc("actContract","📄","የሽያጭ ውል","Legal Sales Contract") +
            svc("actLand","🗺️","የካርታ ማጣሪያ","Cadastral Map");
          var elL = document.getElementById("actLoan");
          if (elL) elL.onclick = function(ev) { try { if(ev){ev.preventDefault();ev.stopPropagation();} openToolModal("loanModal", ev); } catch(e){} };
          var elP2 = document.getElementById("actPoa2");
          if (elP2) elP2.onclick = function(ev) { try { if(ev){ev.preventDefault();ev.stopPropagation();} openToolModal("poaModal", ev); } catch(e){} };
          var elCt = document.getElementById("actContract");
          if (elCt) elCt.onclick = function(ev) {
            try {
              if (ev) { ev.preventDefault(); ev.stopPropagation(); }
              openToolModal("contractModal", ev);
              var rawPrice = parseInt(String(item.price || "").replace(/[^0-9]/g, "")) || "";
              var cp = document.getElementById("contractPrice");
              if (cp) cp.value = rawPrice;
            } catch(e){}
          };
          var elLand = document.getElementById("actLand");
          if (elLand) elLand.onclick = function(ev) { try { if(ev){ev.preventDefault();ev.stopPropagation();} openToolModal("landMapModal", ev); } catch(e){} };
        }
      }

      if (item.id) {
        try {
          var _vid = (item && item.id != null) ? String(item.id).replace(/\D/g, "") || item.id : "";
          if (_vid) fetch("/api/views/" + encodeURIComponent(_vid), { method: "POST", credentials: "same-origin" }).catch(function(){});
        } catch(e){}
      }
      loadRecommendations(item);
    }

    window.openDetailModal = openDetailModal;

    function forceShowBottomNav() {
      try {
        var n = document.getElementById("adikaBottomNav");
        if (!n) return;
        n.classList.remove("hidden");
        // Clear any inline hide
        try { n.style.removeProperty("display"); } catch (e0) {}
        try { n.style.removeProperty("visibility"); } catch (e1) {}
        try { n.style.removeProperty("opacity"); } catch (e2) {}
        n.style.setProperty("display", "flex", "important");
        n.style.setProperty("visibility", "visible", "important");
        n.style.setProperty("opacity", "1", "important");
        n.style.setProperty("pointer-events", "auto", "important");
        n.style.setProperty("z-index", "100", "important");
      } catch (e) {}
    }
    window.forceShowBottomNav = forceShowBottomNav;

    function forceShowFab() {
      try {
        var f = document.getElementById("fabBtn") || document.getElementById("fab-add-btn") || document.querySelector(".floating-btn");
        if (!f) return;
        f.classList.remove("hidden");
        try { f.style.removeProperty("display"); } catch (e0) {}
        f.style.setProperty("display", "flex", "important");
        f.style.setProperty("visibility", "visible", "important");
        f.style.setProperty("opacity", "1", "important");
        f.style.setProperty("pointer-events", "auto", "important");
        f.style.setProperty("z-index", "90", "important");
      } catch (e) {}
    }
    window.forceShowFab = forceShowFab;

    function openImageLightbox(src) {
      if (!src) return;
      try {
        var box = document.getElementById("adikaImageLightbox");
        var img = document.getElementById("adikaLightboxImg");
        if (!box || !img) return;
        img.src = src;
        box.classList.add("is-open");
        box.style.display = "flex";
        try { document.body.style.overflow = "hidden"; } catch (e) {}
      } catch (e) {}
    }
    function closeImageLightbox() {
      try {
        var box = document.getElementById("adikaImageLightbox");
        var img = document.getElementById("adikaLightboxImg");
        if (box) {
          box.classList.remove("is-open");
          box.style.display = "none";
        }
        if (img) img.src = "";
        try { document.body.style.overflow = ""; } catch (e) {}
      } catch (e) {}
    }
    window.openImageLightbox = openImageLightbox;
    window.closeImageLightbox = closeImageLightbox;
    (function bindLightboxOnce() {
      function bind() {
        var closeBtn = document.getElementById("adikaLightboxClose");
        var box = document.getElementById("adikaImageLightbox");
        if (closeBtn && !closeBtn.__lb) {
          closeBtn.__lb = true;
          closeBtn.onclick = function (e) {
            if (e) { e.preventDefault(); e.stopPropagation(); }
            closeImageLightbox();
          };
        }
        if (box && !box.__lb) {
          box.__lb = true;
          box.addEventListener("click", function (e) {
            if (e.target === box) closeImageLightbox();
          });
        }
        document.addEventListener("keydown", function (e) {
          if (e.key === "Escape") closeImageLightbox();
        });
      }
      if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", bind);
      else bind();
    })();

    function restoreHomeChrome() {
      try {
        forceShowBottomNav();
        forceShowFab();
        var f = document.getElementById("fabBtn");
        var h = document.getElementById("adikaFixedHeader");
        var hero = document.getElementById("homeHero");
        if (f) {
          f.classList.remove("hidden");
          try { f.style.removeProperty("display"); } catch (e) {}
          f.style.setProperty("display", "flex", "important");
          f.style.setProperty("visibility", "visible", "important");
        }
        if (h) {
          h.classList.remove("hidden");
          try { h.style.removeProperty("visibility"); h.style.removeProperty("display"); } catch (e) {}
          h.style.visibility = "visible";
          h.style.display = "";
        }
        if (hero) {
          try { hero.style.removeProperty("display"); } catch (e) {}
          hero.style.display = "";
          hero.classList.remove("hidden");
        }
        document.body.style.overflow = "";
        // Instant only (match Advisor tab speed) — one rAF safety re-assert
        try {
          if (window.instantShowHomeChrome) instantShowHomeChrome();
        } catch (eI) {}
        try {
          requestAnimationFrame(function () {
            forceShowBottomNav();
            forceShowFab();
          });
        } catch (eR) {
          forceShowBottomNav();
          forceShowFab();
        }
      } catch (e) {}
    }
    window.restoreHomeChrome = restoreHomeChrome;

    function instantShowHomeChrome() {
      // Synchronous — no animation delay
      try {
        var bottomNav = document.getElementById("adikaBottomNav") || document.getElementById("bottom-nav") || document.querySelector(".bottom-nav");
        if (bottomNav) {
          bottomNav.classList.remove("hidden");
          bottomNav.style.setProperty("display", "flex", "important");
          bottomNav.style.setProperty("visibility", "visible", "important");
          bottomNav.style.setProperty("opacity", "1", "important");
          bottomNav.style.setProperty("pointer-events", "auto", "important");
          bottomNav.style.setProperty("z-index", "100", "important");
        }
      } catch (e1) {}
      try {
        var fabBtn = document.getElementById("fabBtn") || document.getElementById("fab-add-btn") || document.querySelector(".floating-btn");
        if (fabBtn) {
          fabBtn.classList.remove("hidden");
          fabBtn.style.setProperty("display", "flex", "important");
          fabBtn.style.setProperty("visibility", "visible", "important");
          fabBtn.style.setProperty("opacity", "1", "important");
          fabBtn.style.setProperty("pointer-events", "auto", "important");
          fabBtn.style.setProperty("z-index", "90", "important");
        }
      } catch (e2) {}
      try {
        var h = document.getElementById("adikaFixedHeader");
        if (h) {
          h.classList.remove("hidden");
          h.style.setProperty("display", "", "important");
          h.style.setProperty("visibility", "visible", "important");
        }
      } catch (e3) {}
      try {
        var hero = document.getElementById("homeHero");
        if (hero) {
          hero.classList.remove("hidden");
          hero.style.removeProperty("display");
        }
      } catch (e4) {}
      try { document.body.style.overflow = ""; } catch (e5) {}
    }
    window.instantShowHomeChrome = instantShowHomeChrome;

    function closeDetailModalPreserve() {
      try {
        if (modalOverlay) {
          modalOverlay.classList.add("hidden");
          modalOverlay.classList.remove("flex");
          modalOverlay.style.display = "none";
        }
      } catch (e) {}
      // INSTANT restore (primary path — no lag)
      instantShowHomeChrome();
      try { forceShowBottomNav(); } catch (eN) {}
      try { forceShowFab(); } catch (eF) {}
      try { restoreHomeChrome(); } catch (eR) {}
      try { window.__adikaChromeHiddenByDetail = false; } catch (eF2) {}
      try { state.selectedItem = null; } catch (e) {}
      try {
        window.scrollTo({ top: savedFeedScrollY || 0, behavior: "instant" in window ? "instant" : "auto" });
      } catch (e) {
        try { window.scrollTo(0, savedFeedScrollY || 0); } catch (e2) {}
      }
      try {
        var hdr = document.getElementById("adikaFixedHeader");
        var main = document.getElementById("adikaMainFeed");
        if (hdr && main) {
          var hh = Math.ceil(hdr.getBoundingClientRect().height || 0);
          if (hh > 40) main.style.paddingTop = (hh + 6) + "px";
        }
      } catch (e3) {}
      // Instant re-assert (no timeout / no animation lag)
      instantShowHomeChrome();
      forceShowBottomNav();
      forceShowFab();
    }
    window.closeDetailModalPreserve = closeDetailModalPreserve;
    window.closeModal = closeDetailModalPreserve;

    // Recover bottom nav if stuck hidden after detail / tool sheets
    (function adikaNavWatchdog() {
      function recover() {
        try {
          var overlay = document.getElementById("modalOverlay");
          var detailOpen = overlay && !overlay.classList.contains("hidden") && overlay.style.display !== "none";
          if (detailOpen) return;
          var toolsOpen = false;
          ["aiModal","analysisView","dutyModal","loanModal","compareModal","contractModal","poaModal","diagModal","chassisModal","landMapModal","inboxView","myListingsView"].forEach(function(id) {
            var el = document.getElementById(id);
            if (el && !el.classList.contains("hidden") && el.style.display !== "none" && (el.classList.contains("flex") || el.style.display === "flex")) toolsOpen = true;
          });
          if (toolsOpen) return;
          if (typeof forceShowBottomNav === "function") forceShowBottomNav();
        } catch (e) {}
      }
      document.addEventListener("visibilitychange", function() { if (!document.hidden) setTimeout(recover, 100); });
      setInterval(recover, 1200);
      try {
        if (window.Telegram && Telegram.WebApp && Telegram.WebApp.onEvent) {
          Telegram.WebApp.onEvent("backButtonClicked", function() {
            try {
              if (window.closeDetailModalPreserve) window.closeDetailModalPreserve();
              else if (typeof restoreHomeChrome === "function") restoreHomeChrome();
              setTimeout(recover, 50);
            } catch (e) {}
          });
        }
      } catch (eTg) {}
    })();

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
      // ALWAYS unlock UI — finally semantics
      try { state.loading = false; } catch (e) {}
      try { showLoadMoreSpinner(false); } catch (e) {}
      try { if (grid) grid.style.opacity = "1"; } catch (e) {}
      try {
        if (statusEl) {
          statusEl.style.display = "none";
          statusEl.innerHTML = "";
        }
      } catch (e) {}
      items = items || [];
      try {
        var buyTab = (state.tab && state.tab !== "marketplace") || !!window.__adikaIsBuy;
        function isBuyItem(it){
          if (!it) return false;
          if (it._source === "buyer_requests" || it.is_buyer_request) return true;
          var t = ((it.req_type)||"")+" "+((it.action_type)||"")+" "+((it.listing_type)||"")+" "+((it.post_type)||"")+" "+((it.status)||"");
          if (/BUY|REQUEST|WANT|መግዛት|ለመግዛት|ፈላጊ/i.test(t)) return true;
          if ((it.budget_min != null || it.budget_max != null) && !it.price) return true;
          return false;
        }
        if (buyTab) {
          var anyBuySignal = items.some(isBuyItem);
          if (anyBuySignal) items = items.filter(isBuyItem);
        } else {
          items = items.filter(function(it){ return !isBuyItem(it); });
        }
        if (!append) {
          if (grid) grid.innerHTML = "";
          state.items = items;
        } else {
          state.items = (state.items || []).concat(items);
        }
        if (!items.length) {
          if (!append) {
            if (buyTab) {
              try {
                if (statusEl) {
                  statusEl.style.display = "block";
                  statusEl.innerHTML =
                    '<div class="py-8 px-4 text-center text-slate-600 text-sm font-bold">' +
                      '<div class="text-2xl mb-2">📋</div>' +
                      '<span class="lang-am">የፈላጊ ጥያቄ አልተገኘም</span>' +
                      '<div class="text-[11px] font-medium text-slate-400 mt-1">አዲስ ፍላጎት ለመለጠፍ + ይጫኑ</div>' +
                    '</div>';
                }
              } catch (e) {}
            } else {
              try {
                if (grid) grid.innerHTML = "";
                if (statusEl) {
                  statusEl.style.display = "block";
                  statusEl.innerHTML =
                    '<div class="py-8 px-4 text-center text-slate-600 text-sm font-bold">ምንም ማስታወቂያ አልተገኘም</div>';
                }
              } catch (e) {}
            }
          }
          try { if (moreBtn) moreBtn.classList.add("hidden"); } catch (e) {}
          return;
        }
        var painted = 0;
        for (var i = 0; i < items.length; i++) {
          try {
            if (grid) {
              grid.appendChild(createCardElement(items[i]));
              painted++;
            }
          } catch (cardErr) {
            console.error("[Adika] card render", cardErr);
          }
        }
        if (painted === 0 && items.length) {
          try { renderFallbackCards(items); } catch (e) {}
        }
        try {
          if (moreBtn) {
            if (hasMore) moreBtn.classList.remove("hidden");
            else moreBtn.classList.add("hidden");
          }
        } catch (e) {}
      } catch (err) {
        console.error("[Adika] finishLoading", err);
        try { state.loading = false; } catch (e) {}
        try { if (statusEl) { statusEl.style.display = "none"; } } catch (e) {}
      }
    }

    window.__adikaForceExplorer = function () {
      try {
        state.feedMode = "all";
        state.category = "";
        state.tab = "marketplace";
        state.loading = false;
        load(false);
      } catch (e) { console.error(e); }
    };

    var itemsPerPage = 10;
    function showLoadMoreSpinner(on) {
      try {
        var spin = document.getElementById("btnSpinner");
        var txt = document.getElementById("btnText");
        var txtEn = document.getElementById("btnTextEn");
        if (spin) spin.classList.toggle("hidden", !on);
        if (txt) txt.style.opacity = on ? "0.55" : "1";
        if (txtEn) txtEn.style.opacity = on ? "0.55" : "1";
        if (moreBtn) moreBtn.disabled = !!on;
      } catch (e) {}
    }
    function loadMoreVehicles() {
      if (state.loading || state.hasMore === false) return;
      load(true);
    }
    window.loadMoreVehicles = loadMoreVehicles;

    function load(append) {
      // Simple, reliable loader — never discard successful API data
      if (append && (state.loading || state.hasMore === false)) return;
      try { state.loading = true; } catch (e) {}
      try { if (append) showLoadMoreSpinner(true); } catch (e) {}
      try { if (grid && !append) grid.style.opacity = "0.7"; } catch (e) {}

      var page = append ? (state.page + 1) : 1;
      var isBuy = state.tab !== "marketplace";
      // Prefer explorer (known-good) unless user explicitly chose For You
      var useForYou = (!isBuy && state.feedMode === "foryou" && !state.q);
      var qs = "page=" + page + "&limit=" + itemsPerPage + "&order=DESC&active_only=1&type=" + (isBuy ? "BUY" : "SELL");
      var cat = (state.category || "").trim();
      if (!useForYou && cat && !/^(all|ሁሉም|✨|foryou)/i.test(cat)) {
        qs += "&category=" + encodeURIComponent(cat);
      }
      if (state.q) qs += "&q=" + encodeURIComponent(state.q);
      if (state.chassisOnly) qs += "&chassis_only=1";

      var urls = [];
      if (isBuy) {
        urls.push("/api/buyer-requests?page=" + page + "&limit=" + itemsPerPage + "&order=DESC&active_only=1");
        urls.push("/api/requests?page=" + page + "&limit=" + itemsPerPage + "&order=DESC");
        urls.push("/api/listings?" + qs);
        urls.push("/api/explorer/listings?" + qs);
      } else if (!useForYou) {
        urls.push("/api/listings?" + qs);
        urls.push("/api/explorer/listings?" + qs);
      }
      if (useForYou) {
        urls.push("/api/feed/for-you?page=" + page + "&limit=" + itemsPerPage + "&user_id=" + encodeURIComponent(state.userId || getTelegramUserId() || "0"));
        urls.push("/api/listings?" + qs);
      }

      var done = false;
      function applyItems(items, hasMore) {
        if (done && !(items && items.length)) return;
        done = true;
        try { state.loading = false; } catch (e) {}
        try { showLoadMoreSpinner(false); } catch (e) {}
        try { state.page = page; state.hasMore = !!hasMore; } catch (e) {}
        try { finishLoading(items || [], append, !!hasMore); } catch (e) {
          console.error("[Adika] applyItems", e);
          try { if (items && items.length) renderFallbackCards(items); } catch (e2) {}
        }
      }

      // FYP path: Supabase RPC get_fyp_feed first
      if (useForYou) {
        var sb = ensureSupabaseClient();
        var tid = getTelegramUserId() || Number(state.userId || 0);
        var offset = Math.max(0, (page - 1) * itemsPerPage);
        if (sb && typeof sb.rpc === "function" && tid) {
          sb.rpc("get_fyp_feed", {
            p_telegram_id: tid,
            p_limit: itemsPerPage,
            p_offset: offset
          }).then(function (res) {
            var rows = (res && res.data) || [];
            if (!Array.isArray(rows)) rows = [];
            if (rows.length > 0) {
              applyItems(rows, rows.length >= itemsPerPage);
              return;
            }
            tryUrl(0);
          }).catch(function () {
            tryUrl(0);
          });
        } else {
          tryUrl(0);
        }
      } else {
        tryUrl(0);
      }

      function tryUrl(i) {
        if (i >= urls.length) {
          applyItems([], false);
          return;
        }
        var url = urls[i];
        var timer = setTimeout(function () {
          // soft timeout: try next URL, do NOT lock out later success
          tryUrl(i + 1);
        }, 8000);

        fetch(url, { method: "GET", credentials: "same-origin" })
          .then(function (res) {
            return res.json().then(function (data) {
              return { ok: res.ok, data: data || {} };
            });
          })
          .then(function (r) {
            clearTimeout(timer);
            var items = (r.data.items || r.data.listings || r.data.results || (r.data.data && (r.data.data.items || r.data.data.listings)) || r.data.data || []);
            if (!Array.isArray(items)) items = [];
            if (items.length > 0) {
              var moreFlag = (r.data.has_more != null || r.data.hasMore != null)
                ? !!(r.data.has_more || r.data.hasMore)
                : items.length >= itemsPerPage;
              applyItems(items, moreFlag);
            } else {
              tryUrl(i + 1);
            }
          })
          .catch(function (err) {
            clearTimeout(timer);
            console.warn("[Adika] fetch fail", url, err);
            tryUrl(i + 1);
          });
      }
    }

    // Dynamic Central FAB → intent picker (2-step listing / request)
    fabBtn.onclick = function (ev) {
      try { if (ev) { ev.preventDefault(); ev.stopPropagation(); } } catch (e) {}
      if (typeof window.openIntentModal === "function") {
        window.openIntentModal();
        return;
      }
      if (state.tab === "marketplace") {
        window.location.href = "/seller-form";
      } else {
        window.location.href = "/buyer-form";
      }
    };

    function setTabs() {
      var buy = state.tab !== "marketplace";
      window.__adikaIsBuy = !!buy;
      if (!buy) {
        tabSell.className = "py-1 rounded-lg text-xs font-bold transition-all bg-white text-[#16acbd] shadow-sm flex items-center justify-center gap-1";
        tabBuy.className = "py-1 rounded-lg text-xs font-bold transition-all text-white/90 hover:text-white flex items-center justify-center gap-1";
      } else {
        tabBuy.className = "py-1 rounded-lg text-xs font-bold transition-all bg-white text-[#16acbd] shadow-sm flex items-center justify-center gap-1";
        tabSell.className = "py-1 rounded-lg text-xs font-bold transition-all text-white/90 hover:text-white flex items-center justify-center gap-1";
      }
    }

    function switchTab(mode) {
      state.tab = mode === "requests" ? "requests" : "marketplace";
      window.__adikaIsBuy = state.tab !== "marketplace";
      setTabs();
      try {
        if (grid) grid.innerHTML = "";
        state.items = [];
        state.page = 0;
        state.hasMore = true;
        if (statusEl) { statusEl.style.display = "none"; statusEl.innerHTML = ""; }
      } catch (e) {}
      load(false);
    }

    tabSell.onclick = function (ev) {
      try { if (ev) { ev.preventDefault(); ev.stopPropagation(); } } catch (e) {}
      switchTab("marketplace");
    };

    tabBuy.onclick = function (ev) {
      try { if (ev) { ev.preventDefault(); ev.stopPropagation(); } } catch (e) {}
      switchTab("requests");
    };

    // FYP tab gate: force onboarding if not completed
    function isAdikaOnboarded() {
      try { if (localStorage.getItem("adika_onboarded") === "true") return true; } catch (e) {}
      try { if (typeof _lsGet === "function" && _lsGet("adika_onboarded") === "true") return true; } catch (e2) {}
      return false;
    }
    function requireOnboardingForFyp() {
      if (isAdikaOnboarded()) return false;
      try {
        if (typeof window.__adikaShowOnboarding === "function") {
          window.__adikaShowOnboarding();
          return true;
        }
      } catch (e) {}
      try {
        var m = document.getElementById("unifiedOnboardingModal");
        if (m) {
          m.classList.remove("hidden");
          m.classList.add("flex");
          m.style.setProperty("display", "flex", "important");
          m.style.zIndex = "10000";
          document.body.style.overflow = "hidden";
          return true;
        }
      } catch (e2) {}
      return false;
    }
    window.requireOnboardingForFyp = requireOnboardingForFyp;
    window.isAdikaOnboarded = isAdikaOnboarded;

    window.openFYPWithOnboarding = window.openFYPWithOnboarding || function () {
      try {
        if (typeof window.__adikaShowOnboarding === "function") window.__adikaShowOnboarding();
        else requireOnboardingForFyp();
      } catch (e) {
        requireOnboardingForFyp();
      }
      try { state.feedMode = "foryou"; state.category = ""; } catch (e2) {}
      return true;
    };

    window.loadFYPFeed = function () {
      try {
        state.feedMode = "foryou";
        state.category = "";
        state.page = 1;
        state.hasMore = true;
        state.loading = false;
      } catch (e) {}
      try { if (typeof paintFeedModes === "function") paintFeedModes(); } catch (e2) {}
      try {
        if (typeof load === "function") {
          load(false);
          return;
        }
      } catch (e3) {}
      try {
        var sb = typeof ensureSupabaseClient === "function" ? ensureSupabaseClient() : (window.supabase || null);
        var tid = typeof getTelegramUserId === "function" ? getTelegramUserId() : 0;
        if (sb && tid && typeof sb.rpc === "function") {
          sb.rpc("get_fyp_feed", { p_telegram_id: tid, p_limit: 10, p_offset: 0 }).then(function (res) {
            var rows = (res && res.data) || [];
            if (Array.isArray(rows) && rows.length) {
              if (typeof finishLoading === "function") finishLoading(rows, false, rows.length >= 10);
              else if (window.__adikaPaintListings) window.__adikaPaintListings(rows);
            }
          }).catch(function () {});
        }
      } catch (e4) {}
    };

    function selectCategory(catId) {
      // Always unlock UI when user taps a category
      try { state.loading = false; } catch (e) {}

      catId = (catId || "").trim();
      if (catId === "foryou" || catId === "ለእርስዎ" || catId === "✨ ለእርስዎ") {
        try { if (typeof window.openFYPWithOnboarding === "function") window.openFYPWithOnboarding(); } catch (eOb) {}
        if (typeof requireOnboardingForFyp === "function" && requireOnboardingForFyp()) {
          // Show onboarding; still mark tab active but block personalized load until done
          state.feedMode = "foryou";
          state.category = "";
          // Update pills without loading FYP yet
          try {
            var buttons = catsEl.querySelectorAll("button");
            buttons.forEach(function(b) {
              if (b.getAttribute("data-filter") === "chassis") return;
              var bId = b.getAttribute("data-id") || "";
              var on = (bId === "foryou");
              b.className = on
                ? "cat-pill px-3 py-1 rounded-full text-xs font-bold whitespace-nowrap transition-all bg-white text-[#16acbd] shadow-sm"
                : "cat-pill px-3 py-1 rounded-full text-xs font-bold whitespace-nowrap transition-all bg-white/20 text-white hover:bg-white/30";
            });
          } catch (eP) {}
          return;
        }
        state.feedMode = "foryou";
        state.category = "";
      } else if (!catId || catId === "all" || catId === "null" || catId === "undefined" || catId === "✨ ሁሉም" || catId === "✨ All" || catId === "ሁሉም" || catId === "🌐 ሁሉም") {
        state.feedMode = "all";
        state.category = "";
      } else {
        state.feedMode = "cat";
        state.category = catId;
      }
      var buttons = catsEl.querySelectorAll("button");
      buttons.forEach(function(b) {
        if (b.getAttribute("data-filter") === "chassis") return;
        var bId = b.getAttribute("data-id") || "";
        var on = (state.feedMode === "foryou" && bId === "foryou")
          || (state.feedMode === "all" && (bId === "all" || bId === ""))
          || (state.feedMode === "cat" && bId === state.category);
        if (on) {
          b.className = "cat-pill px-3 py-1 rounded-full text-xs font-bold whitespace-nowrap transition-all bg-white text-[#16acbd] shadow-sm";
        } else if (b.getAttribute("data-filter") !== "chassis") {
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

    moreBtn.onclick = function () { loadMoreVehicles(); };

    (function bindInfiniteScroll() {
      var ticking = false;
      function nearBottom() {
        var el = document.documentElement;
        return (el.scrollTop + el.clientHeight >= el.scrollHeight - 100);
      }
      window.addEventListener("scroll", function () {
        if (ticking) return;
        ticking = true;
        requestAnimationFrame(function () {
          ticking = false;
          if (nearBottom()) loadMoreVehicles();
        });
      }, { passive: true });
      var wrap = document.getElementById("loadMoreWrap");
      if (wrap && "IntersectionObserver" in window) {
        try {
          var io = new IntersectionObserver(function (entries) {
            if (entries[0] && entries[0].isIntersecting) loadMoreVehicles();
          }, { rootMargin: "120px 0px" });
          io.observe(wrap);
        } catch (e) {}
      }
    })();

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

    function closeSmartSearchPanel() {
      if (aiSearchView) {
        aiSearchView.classList.add("hidden");
        aiSearchView.classList.remove("flex");
        aiSearchView.style.setProperty("display","none","important");
        aiSearchView.style.setProperty("pointer-events","none","important");
      }
      if (aiToolsView) aiToolsView.classList.remove("hidden");
      if (aiTabTools) aiTabTools.className = "py-1.5 rounded-lg bg-cyan-400/25 text-cyan-100 border border-cyan-400/30 shadow-sm transition-all text-center font-semibold";
      if (aiTabSearch) aiTabSearch.className = "py-1.5 rounded-lg text-white/80 hover:text-white hover:bg-white/10 transition-all text-center";
    }
    window.closeSmartSearchPanel = closeSmartSearchPanel;

    aiTabTools.onclick = function() {
      closeSmartSearchPanel();
    };

    aiTabSearch.onclick = function() {
      if (aiToolsView) aiToolsView.classList.remove("hidden");
      if (aiSearchView) {
        aiSearchView.classList.remove("hidden");
        aiSearchView.classList.add("flex");
        aiSearchView.style.setProperty("display","flex","important");
        aiSearchView.style.setProperty("pointer-events","auto","important");
      }
      if (aiTabSearch) aiTabSearch.className = "py-1.5 rounded-lg bg-cyan-400/25 text-cyan-100 border border-cyan-400/30 shadow-sm transition-all text-center font-semibold";
      if (aiTabTools) aiTabTools.className = "py-1.5 rounded-lg text-white/80 hover:text-white hover:bg-white/10 transition-all text-center";
    };

    var aiSearchBackBtn = document.getElementById("aiSearchBackBtn");
    var aiSearchCloseBtn = document.getElementById("aiSearchCloseBtn");
    if (aiSearchBackBtn) aiSearchBackBtn.onclick = closeSmartSearchPanel;
    if (aiSearchCloseBtn) aiSearchCloseBtn.onclick = closeSmartSearchPanel;

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

    window.__adikaOpenToolFromHub = function(modalId) {
      var ai = document.getElementById("aiModal");
      if (ai) {
        ai.classList.add("hidden");
        ai.classList.remove("flex");
        try { ai.style.display = "none"; } catch (e) {}
      }
      /* keep chrome hidden — openToolModal will hide nav again */
      openToolModal(modalId);
    };

    window.openToolModal = function(id, ev) {
      try { if (ev) { ev.preventDefault(); ev.stopPropagation(); } } catch (e0) {}
      var m = document.getElementById(id);
      if (m) {
        m.classList.remove("hidden");
        m.classList.add("flex");
        try {
          m.style.display = "flex";
          m.style.zIndex = "9999";
        } catch (e) {}
      }
      if (id === "aiModal") {
        try {
          var nav = document.getElementById("adikaBottomNav");
          var fab = document.getElementById("fabBtn");
          var hdr = document.getElementById("adikaFixedHeader");
          var hero = document.getElementById("homeHero");
          if (nav) nav.style.display = "none";
          if (fab) fab.style.display = "none";
          if (hdr) hdr.style.display = "none";
          if (hero) hero.style.display = "none";
          document.body.style.overflow = "hidden";
        } catch (e2) {}
      }
    };

    window.closeToolModal = function(id) {
      var m = document.getElementById(id);
      if (m) {
        m.classList.add("hidden");
        m.classList.remove("flex");
        try { m.style.display = "none"; } catch (e) {}
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
    window.returnToToolsHub = function() {
      var ai = document.getElementById("aiModal");
      if (ai) {
        ai.classList.remove("hidden");
        ai.classList.add("flex");
        try { ai.style.display = "flex"; } catch (e) {}
      }
      try {
        var nav = document.getElementById("adikaBottomNav");
        var fab = document.getElementById("fabBtn");
        var hdr = document.getElementById("adikaFixedHeader");
        var hero = document.getElementById("homeHero");
        if (nav) nav.style.display = "none";
        if (fab) fab.style.display = "none";
        if (hdr) hdr.style.display = "none";
        if (hero) hero.style.display = "none";
        document.body.style.overflow = "hidden";
      } catch (e2) {}
    };
    window.goHomeFromTool = function(id) {
      if (id) closeToolModal(id);
      var ai = document.getElementById("aiModal");
      if (ai) {
        ai.classList.add("hidden");
        ai.classList.remove("flex");
        try { ai.style.display = "none"; } catch (e) {}
      }
      try { if (typeof showAnalysisView === "function") showAnalysisView(false); } catch (e3) {}
      try {
        var nav = document.getElementById("adikaBottomNav");
        var fab = document.getElementById("fabBtn");
        var hdr = document.getElementById("adikaFixedHeader");
        var hero = document.getElementById("homeHero");
        if (nav) nav.style.display = "";
        if (fab) fab.style.display = "";
        if (hdr) hdr.style.display = "";
        if (hero) hero.style.display = "";
        document.body.style.overflow = "";
      } catch (e4) {}
    };
    window.closeModal = function(id) {
      var tools = ["dutyModal","loanModal","compareModal","contractModal","poaModal","diagModal","chassisModal","landMapModal"];
      if (id && tools.indexOf(id) !== -1) {
        closeToolModal(id);
        returnToToolsHub();
        return;
      }
      if (id) closeToolModal(id);
      else {
        tools.concat(["aiModal"]).forEach(function(mid) { closeToolModal(mid); });
        showAnalysisView(false);
      }
    };
    window.navigateBack = function(id) {
      if (id === "analysisView") { showAnalysisView(false); returnToToolsHub(); return; }
      if (id) { closeModal(id); return; }
      goHomeFromTool(null);
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
    document.getElementById("toolDutyBtn").onclick = function() { __adikaOpenToolFromHub("dutyModal"); };
    document.getElementById("toolLoanBtn").onclick = function() { __adikaOpenToolFromHub("loanModal"); };
    document.getElementById("toolCompareBtn").onclick = function() { __adikaOpenToolFromHub("compareModal"); };
    document.getElementById("toolContractBtn").onclick = function() { __adikaOpenToolFromHub("contractModal"); };
    document.getElementById("toolPoaBtn").onclick = function() { __adikaOpenToolFromHub("poaModal"); };
    document.getElementById("toolDiagBtn").onclick = function() { __adikaOpenToolFromHub("diagModal"); };
    if (document.getElementById("toolChassisBtn")) {
      document.getElementById("toolChassisBtn").onclick = function() { __adikaOpenToolFromHub("chassisModal"); };
      var _lmBtn = document.getElementById("toolLandMapBtn");
      if (_lmBtn) _lmBtn.onclick = function() { __adikaOpenToolFromHub("landMapModal"); };
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
        /* ALWAYS Tools Hub dashboard — never POA sub-view */
        if (typeof openToolModal === "function") openToolModal("aiModal");
        else {
          var m = document.getElementById("aiModal");
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

    window.setActiveTab = function(tab){
      if(tab === "chat" || tab === "advisor"){
        if(typeof showAnalysisView === "function") showAnalysisView(true);
        else if(typeof window.openAiChat === "function") window.openAiChat();
      } else if(tab === "tools"){
        if(typeof window.openTools === "function") window.openTools();
      } else if(tab === "home" || tab === "marketplace"){
        if(typeof window.openHome === "function") window.openHome();
      }
    };
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
    if (analysisBackBtn) analysisBackBtn.onclick = function(e) { if(e){e.preventDefault();e.stopPropagation();} showAnalysisView(false); if(window.openTools) openTools(); };
    var analysisCloseBtn = document.getElementById("analysisCloseBtn");
    if (analysisCloseBtn) analysisCloseBtn.onclick = function(e) { if(e){e.preventDefault();e.stopPropagation();} showAnalysisView(false); if(window.openTools) openTools(); };

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
      document.body.classList.add("hub-results-open");
      var dock0=document.getElementById("hubToolsDock"); if(dock0) dock0.style.display="none";
      var rnav0=document.getElementById("hubResultsNav"); if(rnav0){ rnav0.classList.remove("hidden"); rnav0.style.display="flex"; }
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
    window.openAiChat = function(prefillText) {
      try {
        ["aiModal","dutyModal","loanModal","compareModal","contractModal","poaModal","diagModal","chassisModal","landMapModal"].forEach(function(id){
          var m = document.getElementById(id);
          if (!m) return;
          m.classList.add("hidden");
          m.classList.remove("flex");
          m.style.setProperty("display","none","important");
        });
      } catch (e0) {}
      var v = document.getElementById("analysisView");
      if (v) {
        v.classList.remove("hidden");
        v.classList.add("flex");
        v.style.setProperty("display","flex","important");
        v.style.setProperty("z-index","260","important");
      }
      try { document.body.style.overflow = "hidden"; } catch (e1) {}
      var log = document.getElementById("advisorChatLog");
      if (log && !log.dataset.seeded) {
        log.innerHTML = "";
        try { advisorChatHistory = []; } catch (e2) {}
        var initMsg = "ሰላም! እኔ የ Adika Senior Financial Advisor ነኝ። ስለ መኪና ወይም የቤት ግዢ፣ የቀረጥ ስሌት፣ የባንክ ብድር ወይም ማንኛውም የፋይናንስ ምክር ምን ማወቅ ይፈልጋሉ?";
        if (typeof appendAdvisorChat === "function") appendAdvisorChat("advisor", initMsg);
        try { advisorChatHistory.push({ role: "advisor", content: initMsg }); } catch (e3) {}
        log.dataset.seeded = "1";
      }
      var input = document.getElementById("advisorChatInput");
      if (prefillText && input) {
        input.value = prefillText;
        try { input.focus(); } catch (e4) {}
        setTimeout(function() {
          var sendBtn = document.getElementById("advisorChatSend");
          if (sendBtn) sendBtn.click();
        }, 40);
      }
    };
    window.handleStartAiChat = function(opts) {
      opts = opts || {};
      var budget = Number(opts.budget);
      if (!budget) budget = Number((document.getElementById("advisorBudget") || {}).value) || 0;
      var income = Number(opts.income);
      if (!income) income = Number((document.getElementById("advisorMonthlyIncome") || {}).value) || 0;
      var kind = opts.optionType || opts.context || "general";
      var b = (budget || 0).toLocaleString();
      var inc = (income || 0).toLocaleString();
      var prompt = "በ " + b + " ETB በጀት የተመረጡትን የፋይናንስ አማራጮች ማብራሪያ እፈልጋለሁ።";
      if (kind === "auto" || kind === "Automotive") {
        prompt = "በጀቴ " + b + " ብር ነው፣ ወርሃዊ ገቢዬ " + inc + " ብር ነው። በዚህ በጀት የትኛውን ተሽከርካሪ መምረጥ እችላለሁ? የባንክ ብድር አማራጭም አብረው ያብራሩልኝ።";
      } else if (kind === "property" || kind === "Real Estate") {
        prompt = "በጀቴ " + b + " ብር ነው፣ ወርሃዊ ገቢዬ " + inc + " ብር ነው። ለቤት/መሬት የመግቢያ ቅድመ ክፍያ እና የብድር አሰራር ያብራሩልኝ።";
      } else if (kind === "roi" || kind === "Business") {
        prompt = "በጀቴ " + b + " ብር ነው። የንግድ/ሪል እስቴት ኢንቨስትመንት ዓመታዊ ROI እና የኪራይ ገቢ ግምት ያሳዩኝ።";
      }
      openAiChat(prompt);
    };
    var hubFinBanner = document.getElementById("hubFinanceAdvisorBanner");
    if (hubFinBanner) {
      hubFinBanner.onclick = function(ev) {
        if (ev) { ev.preventDefault(); ev.stopPropagation(); }
        handleStartAiChat({ optionType: "general" });
      };
    }
    document.addEventListener("click", function(ev) {
      var btn = ev.target && ev.target.closest ? ev.target.closest(".opp-chat-cta") : null;
      if (!btn) return;
      ev.preventDefault();
      ev.stopPropagation();
      handleStartAiChat({ context: btn.getAttribute("data-context") || "auto" });
    }, true);

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
          '<span class="text-left">💬 ስለ ተመራጩ <b>' + safeName + '</b> ከ Adika ዲጂታል አማካሪ ጋር Live Chat ያድርጉ →</span>' +
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
        "💡 የፋይናንስ ማጠቃለያ በማዘጋጀት ላይ..."
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
      /* Open Tools Hub (aiModal) full-screen — hide marketplace chrome */
      try {
        var m = document.getElementById("aiModal");
        if (m) {
          m.classList.remove("hidden");
          m.classList.add("flex");
          m.style.display = "flex";
        }
        try {
          var nav = document.getElementById("adikaBottomNav");
          var fab = document.getElementById("fabBtn");
          var hdr = document.getElementById("adikaFixedHeader");
          var hero = document.getElementById("homeHero");
          if (nav) nav.style.display = "none";
          if (fab) fab.style.display = "none";
          if (hdr) hdr.style.display = "none";
          if (hero) hero.style.display = "none";
          document.body.style.overflow = "hidden";
        } catch (e3) {}
        // ensure Tools tab is active
        try {
          var tabT = document.getElementById("aiTabTools");
          var tabS = document.getElementById("aiTabSearch");
          var vT = document.getElementById("aiToolsView");
          var vS = document.getElementById("aiSearchView");
          if (tabT) { tabT.className = "py-1 rounded-lg bg-white text-[#16acbd] shadow-sm transition-all text-center"; }
          if (tabS) { tabS.className = "py-1 rounded-lg text-white/80 hover:text-white transition-all text-center"; }
          if (vT) { vT.classList.remove("hidden"); }
          if (vS) { vS.classList.add("hidden"); }
        } catch (e4) {}
      } catch (e) {
        console.error("navAi", e);
      }
    };
    aiModalClose.onclick = function() {
      aiModal.classList.add("hidden");
      aiModal.classList.remove("flex");
      try { aiModal.style.display = "none"; } catch (e) {}
      try {
        var nav = document.getElementById("adikaBottomNav");
        var fab = document.getElementById("fabBtn");
        var hdr = document.getElementById("adikaFixedHeader");
        var hero = document.getElementById("homeHero");
        if (nav) nav.style.display = "";
        if (fab) fab.style.display = "";
        if (hdr) hdr.style.display = "";
        if (hero) hero.style.display = "";
        document.body.style.overflow = "";
      } catch (e2) {}
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
          bannerText = tagParts.length ? tagParts.join(" • ") : ("ዲጂታል ፍልተር: " + query);
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
      try { if (window.closeMyListings) window.closeMyListings(); } catch (e) {}
      try { if (window.closeInbox) window.closeInbox(); } catch (e2) {}
      try { if (window.restoreHomeChrome) window.restoreHomeChrome(); } catch (e3) {}
      try { if (window.forceShowBottomNav) window.forceShowBottomNav(); } catch (e4) {}
      window.scrollTo({ top: 0, behavior: 'smooth' });
    };
    document.getElementById("navMyListings").onclick = function () {
      if (window.openMyListings) window.openMyListings();
      else if (typeof openMyListings === "function") openMyListings();
    };
    document.getElementById("navHelp").onclick = function () {
      var msg = "Adika Marketplace • Help Center\nContact @AdikaMarketplaceBot or call 0911000000.";
      if (tg && tg.showAlert) tg.showAlert(msg);
      else alert(msg);
    };

    (function initLandMapVerifier() {
      var CADASTRE_VERIFY = "https://addislandfarm.gov.et/verify";
      // STRICT: only addislandfarm.gov.et (never dead DNS domains)
      var lastExtract = null;
      var isScanning = false;
      var pendingFinalUrl = "";

      function showPanel(name) {
        ["landMapUploadPanel", "landMapScanPanel", "landMapResultPanel"].forEach(function(id) {
          var el = document.getElementById(id);
          if (el) el.classList.toggle("hidden", id !== name);
        });
      }

      function showErrorToast(msg) {
        isScanning = false;
        showPanel("landMapUploadPanel");
        var toast = document.getElementById("landMapToast");
        if (toast) {
          toast.textContent = msg || "እባክዎን የካርታውን ፎቶ ግልጽ አድርገው እንደገና ያስገቡ።";
          toast.classList.remove("hidden");
          setTimeout(function() { try { toast.classList.add("hidden"); } catch (e) {} }, 5000);
        }
        var retry = document.getElementById("landMapRetryBox");
        if (retry) retry.classList.remove("hidden");
        var fi = document.getElementById("landMapFile");
        if (fi) try { fi.value = ""; } catch (e) {}
      }

      function saveForContract(extract) {
        lastExtract = extract || lastExtract;
        if (!lastExtract) return;
        try {
          _lsSet("adika_land_map_last", JSON.stringify(lastExtract));
          var draft = {};
          try { draft = JSON.parse(_lsGet("adika_contract_draft_v2") || "{}") || {}; } catch (e) {}
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
          _lsSet("adika_contract_draft_v2", JSON.stringify(draft));
        } catch (e) {}
      }

      function extractCertificateId(scannedText) {
        if (!scannedText) return null;
        var s = String(scannedText).trim();
        // 1. 36-char UUID (active digital certificates)
        var uuidMatch = s.match(/[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}/);
        if (uuidMatch) return uuidMatch[0];
        // 2. Reject old deed numbers AD… (not on digital portal)
        if (/^AD\d+/i.test(s) || /\bAD\d{10,}\b/i.test(s)) return null;
        // 3. Plot / Property codes (LTP-KK…, KK…, AA…) — not AD
        var codeMatch = s.match(/\b((?:LTP-)?(?:KK|AA)\d+)\b/i);
        if (codeMatch) return codeMatch[1] || codeMatch[0];
        // 4. Broader AA/KK UPIN only
        var upin = s.match(/\b(AA\d{6,}|KK\d{6,})\b/i);
        if (upin) return upin[1];
        // 5. DO NOT return static fallback like "addisland"
        return null;
      }

      function processScannedQrPayload(scannedText) {
        if (!scannedText) return null;
        var s = String(scannedText).trim();
        var uuidMatch = s.match(/[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}/);
        if (uuidMatch) {
          return "https://addislandfarm.gov.et/verify/" + uuidMatch[0];
        }
        // Reject old deed AD… prefixes
        if (/^AD/i.test(s) || /\bAD\d{8,}\b/i.test(s) || /addisland(?!farm)/i.test(s)) {
          try {
            var toast = document.getElementById("landMapToast");
            if (toast) {
              toast.textContent = "ይህ የቆየ የካርታ ቁጥር በመሆኑ በመንግስት ዲጂታል ፖርታል ላይ አልተመዘገበም። እባክዎን የቅርብ ጊዜውን ዲጂታል የካርታ ፎቶ ያስገቡ።";
              toast.classList.remove("hidden");
            } else {
              alert("ይህ የቆየ የካርታ ቁጥር በመሆኑ በመንግስት ዲጂታል ፖርታል ላይ አልተመዘገበም። እባክዎን የቅርብ ጊዜውን ዲጂታል የካርታ ፎቶ ያስገቡ።");
            }
          } catch (e) {}
          return null;
        }
        if (/addislandfarm\.gov\.et/i.test(s)) {
          var m = s.match(/https?:\/\/[^\s"'<>]*addislandfarm\.gov\.et[^\s"'<>]*/i);
          return m ? m[0] : s;
        }
        var id = extractCertificateId(s);
        if (id && /^[0-9a-fA-F-]{36}$/.test(id)) {
          return "https://addislandfarm.gov.et/verify/" + id;
        }
        if (id) {
          return "https://addislandfarm.gov.et/verify?upin=" + encodeURIComponent(id);
        }
        return "https://addislandfarm.gov.et/";
      }

      function sanitizeAndEnforceActiveDomain(scannedInput) {
        var cleanInput = scannedInput ? String(scannedInput).trim() : "";
        var BASE = "https://addislandfarm.gov.et";
        var VERIFY = BASE + "/verify";
        if (!cleanInput) return BASE + "/";

        // Block dead domains — extract real id only
        if (/land\.addiscadaster\.gov\.et|addiscadaster\.gov\.et|addisland\.gov\.et/i.test(cleanInput)) {
          try { console.warn("[Adika] Blocked dead domain. Remapping."); } catch (e) {}
          var idDead = extractCertificateId(cleanInput);
          if (idDead) {
            if (/^[0-9a-fA-F-]{36}$/.test(idDead)) return VERIFY + "/" + idDead;
            return VERIFY + "?upin=" + encodeURIComponent(idDead);
          }
          return BASE + "/";
        }

        // Full URL on active portal — keep
        if (/^https?:\/\//i.test(cleanInput) && /addislandfarm\.gov\.et/i.test(cleanInput)) {
          // Reject nonsense paths like /verify/addisland
          var bad = cleanInput.match(/\/verify\/(addisland|verify|home|index|null|undefined)\/?$/i);
          if (bad) return BASE + "/";
          return cleanInput;
        }

        // Other http(s) URLs — extract certificate id then map
        if (/^https?:\/\//i.test(cleanInput) || /https?:\/\//i.test(cleanInput)) {
          var idFromUrl = extractCertificateId(cleanInput);
          if (idFromUrl) {
            if (/^[0-9a-fA-F]{8}-[0-9a-fA-F-]{27}$/.test(idFromUrl)) return VERIFY + "/" + idFromUrl;
            return VERIFY + "?upin=" + encodeURIComponent(idFromUrl);
          }
          return BASE + "/";
        }

        // JSON
        try {
          if (cleanInput.charAt(0) === "{" || cleanInput.charAt(0) === "[") {
            var j = JSON.parse(cleanInput);
            if (Array.isArray(j)) j = j[0] || {};
            if (j.url) return sanitizeAndEnforceActiveDomain(String(j.url));
            var jid = j.upin || j.UPIN || j.parcel_id || j.plot || j.code || j.id || j.token || "";
            if (jid) return sanitizeAndEnforceActiveDomain(String(jid));
          }
        } catch (e) {}

        // Extract structured id from raw text
        var id = extractCertificateId(cleanInput);
        if (id) {
          if (/^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$/.test(id)) {
            return VERIFY + "/" + id;
          }
          return VERIFY + "?upin=" + encodeURIComponent(id);
        }

        // Last resort: only if input looks like a real token (not dictionary words)
        if (/^[A-Za-z0-9_\-]{8,64}$/.test(cleanInput) &&
            !/^(addisland|verify|null|undefined|http|https|www)$/i.test(cleanInput)) {
          return VERIFY + "?upin=" + encodeURIComponent(cleanInput);
        }
        return BASE + "/";
      }

      function buildFinalUrl(scannedPayload) {
        var processed = processScannedQrPayload(scannedPayload);
        if (processed === null) return ""; // rejected (e.g. AD old deed)
        return sanitizeAndEnforceActiveDomain(processed || scannedPayload);
      }

      function handleVerificationSuccess(scannedData) {
        var finalUrl = buildFinalUrl(scannedData);
        if (!finalUrl) {
          showErrorToast("እባክዎን የካርታውን ፎቶ ግልጽ አድርገው እንደገና ያስገቡ።");
          return;
        }
        // Pass correctly formatted URL to Adika modal (no auto-redirect)
        if (typeof triggerAdikaSuccessModal === "function") {
          // Store pre-built URL path: pass object so modal uses exact finalUrl
          triggerAdikaSuccessModal(scannedData, finalUrl);
        }
      }

      function extractUpinHint(payload, finalUrl) {
        var s = String(payload || "");
        var m = s.match(/\b(AA\d{8,16}|KK\d{8,16}|LTP[-_]?[A-Z0-9\-]+)\b/i);
        if (m) return m[1] || m[0];
        try {
          var u = new URL(finalUrl);
          return u.searchParams.get("upin") || u.searchParams.get("plot") || "";
        } catch (e) {
          return "";
        }
      }

      function openOfficialUrl(url) {
        if (!url) return false;
        url = sanitizeAndEnforceActiveDomain(String(url).trim());
        // Final hard gate — never open dead DNS hosts
        if (/addiscadaster|addisland\.gov\.et/i.test(url) && !/addislandfarm\.gov\.et/i.test(url)) {
          url = "https://addislandfarm.gov.et/";
        }
        try {
          if (window.Telegram && Telegram.WebApp && typeof Telegram.WebApp.openLink === "function") {
            try { Telegram.WebApp.openLink(url, { try_instant_view: false }); }
            catch (e0) { Telegram.WebApp.openLink(url); }
            return true;
          }
        } catch (e1) {}
        try {
          if (typeof tg !== "undefined" && tg && typeof tg.openLink === "function") {
            tg.openLink(url);
            return true;
          }
        } catch (e2) {}
        try { window.open(url, "_blank"); return true; } catch (e3) {}
        try { window.location.href = url; return true; } catch (e4) {}
        return false;
      }

      /** Show professional Adika success modal — NO auto-redirect */
      function triggerAdikaSuccessModal(scannedPayload, prebuiltUrl) {
        isScanning = false;
        var finalUrl = prebuiltUrl || buildFinalUrl(scannedPayload);
        if (!finalUrl) {
          showErrorToast("እባክዎን የካርታውን ፎቶ ግልጽ አድርገው እንደገና ያስገቡ።");
          return;
        }
        pendingFinalUrl = finalUrl;
        var upin = extractUpinHint(scannedPayload, finalUrl);
        saveForContract({
          raw: String(scannedPayload || ""),
          url: finalUrl,
          upin: upin || ""
        });

        var hint = document.getElementById("adikaPayloadHint");
        if (hint) {
          // Show safe label — never show wrong host confusion
          var label = upin || "";
          if (!label && /addislandfarm\.gov\.et/i.test(finalUrl)) {
            try { label = finalUrl.split("/verify/")[1] || ""; } catch (e) {}
          }
          if (label) {
            hint.textContent = "መለያ: " + label;
            hint.classList.remove("hidden");
          } else if (/^https?:\/\//i.test(String(scannedPayload || ""))) {
            hint.textContent = "ኦፊሴላዊ ማረጋገጫ ሊንክ ተገኝቷል";
            hint.classList.remove("hidden");
          } else {
            hint.classList.add("hidden");
          }
        }

        var viewBtn = document.getElementById("adikaViewResultBtn");
        if (viewBtn) {
          viewBtn.onclick = function() {
            openOfficialUrl(pendingFinalUrl || finalUrl);
          };
        }

        showPanel("landMapResultPanel");
        var fi = document.getElementById("landMapFile");
        if (fi) try { fi.value = ""; } catch (e) {}
      }

      function tryJsQROnImageData(imageData) {
        if (typeof jsQR !== "function" || !imageData) return null;
        try {
          var code = jsQR(imageData.data, imageData.width, imageData.height, { inversionAttempts: "attemptBoth" });
          return code && code.data ? String(code.data) : null;
        } catch (e) {
          return null;
        }
      }

      function enhanceAndScanCanvas(srcCanvas) {
        // Binarize copy for stamp resistance
        var c = document.createElement("canvas");
        c.width = srcCanvas.width;
        c.height = srcCanvas.height;
        var ctx = c.getContext("2d", { willReadFrequently: true });
        ctx.drawImage(srcCanvas, 0, 0);
        var id = ctx.getImageData(0, 0, c.width, c.height);
        var d = id.data;
        for (var i = 0; i < d.length; i += 4) {
          var g = 0.40 * d[i] + 0.50 * d[i + 1] + 0.10 * d[i + 2];
          var v = g >= 120 ? 255 : 0;
          d[i] = d[i + 1] = d[i + 2] = v;
          d[i + 3] = 255;
        }
        ctx.putImageData(id, 0, 0);
        return tryJsQROnImageData(id) || tryJsQROnImageData(ctx.getImageData(0, 0, c.width, c.height));
      }

      function scanRegionFromImage(img, rx, ry, rw, rh) {
        var srcW = img.naturalWidth || img.width;
        var srcH = img.naturalHeight || img.height;
        var x = Math.max(0, Math.floor(srcW * rx));
        var y = Math.max(0, Math.floor(srcH * ry));
        var w = Math.max(16, Math.floor(srcW * rw));
        var h = Math.max(16, Math.floor(srcH * rh));
        if (x + w > srcW) w = srcW - x;
        if (y + h > srcH) h = srcH - y;
        if (w < 16 || h < 16) return null;

        // native crop
        var crop = document.createElement("canvas");
        crop.width = w; crop.height = h;
        var cctx = crop.getContext("2d", { willReadFrequently: true });
        cctx.imageSmoothingEnabled = false;
        cctx.drawImage(img, x, y, w, h, 0, 0, w, h);
        var hit = enhanceAndScanCanvas(crop);
        if (hit) return hit;

        // 2x upscale + enhance
        var up = document.createElement("canvas");
        up.width = w * 2; up.height = h * 2;
        var uctx = up.getContext("2d", { willReadFrequently: true });
        uctx.imageSmoothingEnabled = false;
        uctx.drawImage(crop, 0, 0, up.width, up.height);
        hit = enhanceAndScanCanvas(up);
        if (hit) return hit;

        // multi-threshold on upscaled
        var thresholds = [100, 128, 150, 85];
        for (var ti = 0; ti < thresholds.length; ti++) {
          var trial = document.createElement("canvas");
          trial.width = up.width; trial.height = up.height;
          var tctx = trial.getContext("2d", { willReadFrequently: true });
          tctx.drawImage(up, 0, 0);
          var id = tctx.getImageData(0, 0, trial.width, trial.height);
          var d = id.data;
          var thr = thresholds[ti];
          for (var i = 0; i < d.length; i += 4) {
            var g = 0.40 * d[i] + 0.50 * d[i + 1] + 0.10 * d[i + 2];
            var v = g >= thr ? 255 : 0;
            d[i] = d[i + 1] = d[i + 2] = v;
            d[i + 3] = 255;
          }
          hit = tryJsQROnImageData(id);
          if (hit) return hit;
        }
        return null;
      }

      function processUploadedCertificate(imageElement) {
        var t0 = (typeof performance !== "undefined" && performance.now) ? performance.now() : Date.now();
        var qrData = null;

        // Pass 1: Top-Right (Title Deed / female format)
        qrData = scanRegionFromImage(imageElement, 0.55, 0.00, 0.45, 0.35);

        // Pass 2: Mid-Right beside photo (Cadastral / male format)
        if (!qrData) {
          qrData = scanRegionFromImage(imageElement, 0.55, 0.15, 0.45, 0.40);
        }
        // Pass 2b: slightly lower mid-right
        if (!qrData) {
          qrData = scanRegionFromImage(imageElement, 0.50, 0.18, 0.50, 0.42);
        }

        // Pass 3: Full canvas (downscaled for speed)
        if (!qrData) {
          var srcW = imageElement.naturalWidth || imageElement.width;
          var srcH = imageElement.naturalHeight || imageElement.height;
          var maxW = 1100;
          var scale = srcW > maxW ? maxW / srcW : 1;
          var canvas = document.createElement("canvas");
          canvas.width = Math.max(1, Math.floor(srcW * scale));
          canvas.height = Math.max(1, Math.floor(srcH * scale));
          var ctx = canvas.getContext("2d", { willReadFrequently: true });
          ctx.drawImage(imageElement, 0, 0, canvas.width, canvas.height);
          qrData = enhanceAndScanCanvas(canvas);
          if (!qrData) {
            var fullData = ctx.getImageData(0, 0, canvas.width, canvas.height);
            qrData = tryJsQROnImageData(fullData);
          }
        }

        var t1 = (typeof performance !== "undefined" && performance.now) ? performance.now() : Date.now();
        try { console.log("[Adika Digital System] scan ms:", Math.round(t1 - t0), qrData ? "OK" : "MISS"); } catch (e) {}

        if (qrData) {
          handleVerificationSuccess(qrData);
        } else {
          // Backend OCR last resort
          runBackendOCRLast(imageElement);
        }
      }

      function runBackendOCRLast(imgEl) {
        try {
          var c = document.createElement("canvas");
          var maxW = 1400;
          var w = imgEl.naturalWidth || imgEl.width;
          var h = imgEl.naturalHeight || imgEl.height;
          var sc = w > maxW ? maxW / w : 1;
          c.width = Math.floor(w * sc);
          c.height = Math.floor(h * sc);
          c.getContext("2d").drawImage(imgEl, 0, 0, c.width, c.height);
          var dataUrl = c.toDataURL("image/jpeg", 0.9);

          // 1) Backend pyzbar/OpenCV scan-qr
          fetch("/api/scan-qr", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ image_data: dataUrl })
          })
            .then(function(r) { return r.json().then(function(j) { return { ok: r.ok, j: j }; }); })
            .then(function(res) {
              if (res.j && res.j.success && (res.j.target_url || res.j.payload)) {
                if (res.j.target_url) {
                  triggerAdikaSuccessModal(res.j.payload || res.j.target_url, res.j.target_url);
                  return;
                }
                handleVerificationSuccess(res.j.payload);
                return;
              }
              // 2) Fallback OCR field extract
              return fetch("/api/land-map/ocr", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ image_data: dataUrl })
              }).then(function(r2) { return r2.json(); });
            })
            .then(function(res2) {
              if (!res2) return;
              if (res2.success && res2.data) {
                var cand = res2.data.url || res2.data.upin || res2.data.cert || "";
                if (cand) { handleVerificationSuccess(cand); return; }
              }
              showErrorToast("እባክዎን የካርታውን ፎቶ ግልጽ አድርገው እንደገና ያስገቡ።");
            })
            .catch(function() {
              showErrorToast("እባክዎን የካርታውን ፎቶ ግልጽ አድርገው እንደገና ያስገቡ።");
            });
        } catch (e) {
          showErrorToast("እባክዎን የካርታውን ፎቶ ግልጽ አድርገው እንደገና ያስገቡ።");
        }
      }

      function processDataUrl(dataUrl) {
        if (isScanning) return;
        isScanning = true;
        var toast = document.getElementById("landMapToast");
        if (toast) toast.classList.add("hidden");
        var retry = document.getElementById("landMapRetryBox");
        if (retry) retry.classList.add("hidden");
        showPanel("landMapScanPanel");
        var prev = document.getElementById("landMapPreview");
        if (prev) prev.src = dataUrl;

        var img = new Image();
        img.onload = function() {
          try {
            processUploadedCertificate(img);
          } catch (e) {
            showErrorToast("እባክዎን የካርታውን ፎቶ ግልጽ አድርገው እንደገና ያስገቡ።");
          }
        };
        img.onerror = function() {
          showErrorToast("እባክዎን የካርታውን ፎቶ ግልጽ አድርገው እንደገና ያስገቡ።");
        };
        img.src = dataUrl;
      }

      var fileInput = document.getElementById("landMapFile");
      if (fileInput) {
        fileInput.onchange = function() {
          var f = fileInput.files && fileInput.files[0];
          if (!f) return;
          isScanning = false;
          var reader = new FileReader();
          reader.onload = function() { processDataUrl(reader.result); };
          reader.onerror = function() {
            showErrorToast("እባክዎን የካርታውን ፎቶ ግልጽ አድርገው እንደገና ያስገቡ።");
          };
          reader.readAsDataURL(f);
        };
      }

      var retryBtn = document.getElementById("landMapRetryBtn");
      if (retryBtn) {
        retryBtn.onclick = function() {
          isScanning = false;
          if (fileInput) {
            try { fileInput.value = ""; } catch (e) {}
            fileInput.click();
          }
        };
      }

      var resetBtn = document.getElementById("landMapResetBtn");
      if (resetBtn) {
        resetBtn.onclick = function() {
          lastExtract = null;
          pendingFinalUrl = "";
          isScanning = false;
          if (fileInput) try { fileInput.value = ""; } catch (e) {}
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
          var u = pendingFinalUrl || (lastExtract && lastExtract.url) || CADASTRE_VERIFY;
          if (navigator.share) {
            navigator.share({ title: "Adika Digital Verification", url: u }).catch(function(){});
          } else {
            openOfficialUrl(u);
          }
        };
      }

      // Wire view button if present at init
      var viewBtn0 = document.getElementById("adikaViewResultBtn");
      if (viewBtn0) {
        viewBtn0.onclick = function() {
          if (pendingFinalUrl) openOfficialUrl(pendingFinalUrl);
        };
      }
    })();

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
        try { _lsSet(SUB_KEY, JSON.stringify(collectPayload("Draft"))); } catch (e) {}
      }
      function restoreDraft() {
        try {
          var raw = _lsGet(SUB_KEY);
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
            try { _lsSet(SUB_KEY, JSON.stringify(collectPayload("Draft"))); } catch (e) {}
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

    (function initParityFeatures() {
      try {
        state.userId = (window.Telegram && Telegram.WebApp && Telegram.WebApp.initDataUnsafe && Telegram.WebApp.initDataUnsafe.user && Telegram.WebApp.initDataUnsafe.user.id) || 0;
      } catch (e) { state.userId = 0; }

      function openM(id) {
        var m = document.getElementById(id);
        if (m) { m.classList.remove("hidden"); m.classList.add("flex"); m.style.display = "flex"; }
      }
      function closeM(id) {
        var m = document.getElementById(id);
        if (m) { m.classList.add("hidden"); m.classList.remove("flex"); m.style.display = "none"; }
      }

      // Prefill category strip: For You first
      function paintFeedModes() {
        if (!catsEl) return;
        var modes = [
          { id: "foryou", label: "✨ ለእርስዎ" },
          { id: "all", label: "🌐 ሁሉም" },
          { id: "መኪና", label: "🚗 መኪና" },
          { id: "ቤት", label: "🏠 ቤት" },
          { id: "ንግድ", label: "🏢 ንግድ" }
        ];
        catsEl.innerHTML = "";
        modes.forEach(function(m) {
          var b = document.createElement("button");
          b.type = "button";
          b.setAttribute("data-id", m.id);
          var on = (state.feedMode === "foryou" && m.id === "foryou")
            || (state.feedMode === "all" && m.id === "all")
            || (state.feedMode === "cat" && state.category === m.id);
          b.className = on
            ? "cat-pill px-3 py-1 rounded-full text-xs font-bold whitespace-nowrap transition-all bg-white text-[#16acbd] shadow-sm"
            : "cat-pill px-3 py-1 rounded-full text-xs font-bold whitespace-nowrap transition-all bg-white/20 text-white hover:bg-white/30";
          b.textContent = m.label;
          b.onclick = function() {
            if (m.id === "foryou") {
              state.feedMode = "foryou";
              state.category = "";
              paintFeedModes();
              if (typeof requireOnboardingForFyp === "function" && requireOnboardingForFyp()) return;
              load(false);
              return;
            }
            if (m.id === "all") { state.feedMode = "all"; state.category = ""; }
            else { state.feedMode = "cat"; state.category = m.id; }
            paintFeedModes();
            load(false);
          };
          catsEl.appendChild(b);
        });
      }
      paintFeedModes();

      // Role gate
      var roleKey = "adika_role_v1";
      var hasRole = false;
      try { hasRole = !!_lsGet(roleKey); } catch (e) {}
      // Do not block the marketplace behind role modal — optional entry only
      // if (!hasRole) openM("roleSelectModal");
      try { if (!hasRole) _lsSet(roleKey, "user"); } catch (e) {}

      var roleUser = document.getElementById("roleUserBtn");
      var roleBroker = document.getElementById("roleBrokerBtn");
      if (roleUser) roleUser.onclick = function() {
        try { _lsSet(roleKey, "user"); } catch (e) {}
        closeM("roleSelectModal");
        state.feedMode = "all";
        paintFeedModes();
        load(false);
      };
      if (roleBroker) roleBroker.onclick = function() {
        try { _lsSet(roleKey, "broker"); } catch (e) {}
        closeM("roleSelectModal");
        openM("brokerRegModal");
      };

      var brIdPhoto = document.getElementById("brIdPhoto");
      var brIdPreview = document.getElementById("brIdPreview");
      var brIdDataUrl = "";
      if (brIdPhoto) {
        brIdPhoto.onchange = function() {
          var f = brIdPhoto.files && brIdPhoto.files[0];
          if (!f) return;
          var reader = new FileReader();
          reader.onload = function(ev) {
            brIdDataUrl = ev.target.result || "";
            if (brIdPreview && brIdDataUrl) {
              brIdPreview.src = brIdDataUrl;
              brIdPreview.classList.remove("hidden");
            }
          };
          reader.readAsDataURL(f);
        };
      }

      var brSubmit = document.getElementById("brSubmitBtn");
      if (brSubmit) brSubmit.onclick = function() {
        var name = (document.getElementById("brName") || {}).value || "";
        var phone = (document.getElementById("brPhone") || {}).value || "";
        var user = (document.getElementById("brUser") || {}).value || "";
        var cats = [];
        document.querySelectorAll(".brCat:checked").forEach(function(c) { cats.push(c.value); });
        var tid = state.userId || 0;
        try {
          if ((!tid || tid === 0) && window.Telegram && Telegram.WebApp && Telegram.WebApp.initDataUnsafe && Telegram.WebApp.initDataUnsafe.user) {
            tid = Telegram.WebApp.initDataUnsafe.user.id || 0;
          }
        } catch (e) {}
        if (!name || !phone) { alert("ስም እና ስልክ ያስፈልጋሉ"); return; }
        brSubmit.disabled = true;
        brSubmit.textContent = "እየተመዘገበ ነው…";
        fetch("/api/brokers/register", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            telegram_id: tid,
            name: name,
            phone: phone,
            username: user,
            categories: cats,
            id_photo: brIdDataUrl || null
          })
        }).then(function(r){ return r.json(); }).then(function(d){
          if (d.success) {
            alert("✅ ምዝገባዎ ተልኳል! አድሚን ካረጋገጠ በኋላ ደላላ ይሆናሉ።");
            closeM("brokerRegModal");
            brIdDataUrl = "";
            try { if (brIdPreview) { brIdPreview.classList.add("hidden"); brIdPreview.src = ""; } } catch (e) {}
          } else {
            alert(d.message || "ምዝገባ አልተሳካም");
          }
        }).catch(function(){ alert("ኔትወርክ ስህተት"); })
        .finally(function(){
          brSubmit.disabled = false;
          brSubmit.textContent = "✅ መመዝገብ / Submit";
        });
      };

      // Floating entry for brokers
      try { /* broker float card handles entry */ } catch (e) {}
    })();

    (function initPromoBanner() {
      var INTERVAL_MS = 3000;
      var slides = [];
      var dots = [];
      var idx = 0;
      var timer = null;
      var banner = null;

      var btnMap = {
        poa: "toolPoaBtn",
        chassis: "toolChassisBtn",
        duty: "toolDutyBtn",
        loan: "toolLoanBtn",
        compare: "toolCompareBtn",
        contract: "toolContractBtn",
        diag: "toolDiagBtn"
      };

      function setHomeChrome(visible) {
        try {
          var nav = document.getElementById("adikaBottomNav");
          var fab = document.getElementById("fabBtn");
          var hero = document.getElementById("homeHero");
          if (nav) { if (visible) { nav.classList.remove("hidden"); nav.style.setProperty("display","flex","important"); } else { nav.style.display = "none"; } }
          if (fab) fab.style.display = visible ? "" : "none";
          if (hero) hero.style.display = visible ? "" : "none";
        } catch (e) {}
      }

      function showSlide(next) {
        if (!slides.length) return;
        var prev = idx;
        idx = ((next % slides.length) + slides.length) % slides.length;
        slides.forEach(function (el, i) {
          el.classList.remove("is-active", "is-exit", "is-enter");
          if (i === idx) {
            // ENTER from below + bounce ease cubic-bezier(0.34, 1.56, 0.64, 1)
            el.style.transition = "none";
            el.style.opacity = "0";
            el.style.transform = "scale(0.88) translateY(18px)";
            el.style.pointerEvents = "none";
            void el.offsetWidth;
            el.style.transition = "opacity 0.4s cubic-bezier(0.34, 1.56, 0.64, 1), transform 0.4s cubic-bezier(0.34, 1.56, 0.64, 1)";
            el.classList.add("is-active");
            el.style.opacity = "1";
            el.style.transform = "scale(1) translateY(0)";
            el.style.pointerEvents = "auto";
            // re-trigger letter kinetic + icon spring
            try {
              var letters = el.querySelectorAll(".promo-letter");
              letters.forEach(function(L, li) {
                L.style.animation = "none";
                void L.offsetWidth;
                L.style.animation = "adikaLetterIn 0.32s cubic-bezier(0.34, 1.56, 0.64, 1) both";
                L.style.animationDelay = (li * 30) + "ms";
              });
              var ic = el.querySelector(".promo-icon");
              if (ic) {
                ic.style.transition = "none";
                ic.style.transform = "scale(0)";
                void ic.offsetWidth;
                ic.style.transition = "transform 0.45s cubic-bezier(0.34, 1.56, 0.64, 1)";
                ic.style.transform = "scale(1.1)";
                setTimeout(function(){ ic.style.transform = "scale(1)"; }, 180);
              }
              var sub = el.querySelector(".promo-sub");
              if (sub) {
                sub.style.transition = "none";
                sub.style.opacity = "0";
                sub.style.transform = "translateX(-20px)";
                void sub.offsetWidth;
                sub.style.transition = "opacity 0.35s ease 0.12s, transform 0.35s cubic-bezier(0.16,1,0.3,1) 0.12s";
                sub.style.opacity = "1";
                sub.style.transform = "translateX(0)";
              }
            } catch (e) {}
          } else if (i === prev) {
            // EXIT: scale down + push UP rapidly
            el.classList.add("is-exit");
            el.style.transition = "opacity 0.28s cubic-bezier(0.4, 0, 1, 1), transform 0.28s cubic-bezier(0.4, 0, 1, 1)";
            el.style.opacity = "0";
            el.style.transform = "scale(0.92) translateY(-22px)";
            el.style.pointerEvents = "none";
          } else {
            el.style.opacity = "0";
            el.style.transform = "scale(0.9) translateY(16px)";
            el.style.pointerEvents = "none";
          }
        });
        dots.forEach(function (d, i) {
          d.style.background = i === idx ? "rgba(255,255,255,0.95)" : "rgba(255,255,255,0.28)";
          d.style.width = i === idx ? "10px" : "6px";
          d.style.borderRadius = i === idx ? "4px" : "999px";
        });
      }

      function openCurrentTool() {
        /* Banner → Tools Hub (aiModal), NEVER direct AI chat */
        try {
          if (typeof openToolModal === "function") openToolModal("aiModal");
          else {
            var m = document.getElementById("aiModal");
            if (m) {
              m.classList.remove("hidden");
              m.classList.add("flex");
              m.style.display = "flex";
            }
          }
          setHomeChrome(false);
          /* Stay on Tools Hub dashboard — do NOT auto-open POA/duty/compare forms */
          try { window.__adikaSelectedTool = null; } catch (e2) {}
        } catch (e) { console.error("openCurrentTool", e); }
      }

      window.__adikaOpenToolChat = function (toolKey) {
        try {
          setHomeChrome(false);
          if (typeof showAnalysisView === "function") showAnalysisView(true);
          var msg = toolKey === "loan"
            ? "ሰላም! የባንክ ብድር እና የፋይናንስ አማካሪ — ጠቅላላ ዋጋ ወይም ወርሃዊ ገቢዎን ይንገሩኝ።"
            : "ሰላም! በአዲካ ዲጂታል ሲስተም እንኳን ደህና መጡ። እንዴት ልረዳዎ?";
          setTimeout(function () {
            try {
              var log = document.getElementById("advisorChatLog");
              if (log) {
                var div = document.createElement("div");
                div.className = "mb-2 max-w-[90%]";
                div.innerHTML = '<div class="bg-cyan-50 border border-cyan-100 text-cyan-900 text-xs font-medium p-3 rounded-2xl">' + msg + "</div>";
                log.appendChild(div);
                log.scrollTop = log.scrollHeight;
              }
            } catch (e) {}
          }, 180);
        } catch (e) {}
      };

      try {
        if (typeof showAnalysisView === "function" && !window.__adikaNavWrapped) {
          window.__adikaNavWrapped = true;
          var _origShow = showAnalysisView;
          window.showAnalysisView = function (on) {
            try { _origShow(on); } catch (e) {}
            setHomeChrome(!on);
            if (on && timer) { clearInterval(timer); timer = null; }
            if (!on) startAuto();
          };
        }
      } catch (e) {}

      function startAuto() {
        if (timer) clearInterval(timer);
        timer = setInterval(function () {
          showSlide(idx + 1);
        }, INTERVAL_MS);
      }

      function boot() {
        banner = document.getElementById("adikaPromoBanner");
        slides = Array.prototype.slice.call(document.querySelectorAll(".promo-slide"));
        dots = Array.prototype.slice.call(document.querySelectorAll(".promo-dot"));
        if (!slides.length) return;
        showSlide(0);
        startAuto();
        if (banner) {
          banner.onclick = function () {
            openCurrentTool();
          };
          // pause briefly on touch then resume
          banner.addEventListener("touchstart", function () {
            if (timer) { clearInterval(timer); timer = null; }
          }, { passive: true });
          banner.addEventListener("touchend", function () {
            setTimeout(startAuto, 2500);
          }, { passive: true });
        }
        dots.forEach(function (d) {
          d.onclick = function (ev) {
            ev.stopPropagation();
            var i = parseInt(d.getAttribute("data-i") || "0", 10);
            showSlide(i);
            startAuto();
          };
        });
      }

      if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", boot);
      } else {
        boot();
      }

      var br = document.getElementById("brokerCtaHome");
      if (br) {
        br.onclick = function () {
          try {
            if (typeof openM === "function") openM("brokerRegModal");
            else {
              var m = document.getElementById("brokerRegModal");
              if (m) { m.classList.remove("hidden"); m.style.display = "flex"; }
            }
          } catch (e) {}
        };
      }
    })();

    setTabs();
    try { state.feedMode = "all"; state.category = ""; } catch (e) {}
    try { if (typeof paintFeedModes === "function") paintFeedModes(); } catch (e) {}

    try {
      state.loading = false;
      load(false);
    } catch (e) {
      console.error("[Adika] initial load", e);
      try { state.loading = false; } catch (e2) {}
      try { if(window.__adikaPaintListings) window.__adikaPaintListings([]); } catch (e3) {}
    }

    // If after 5s still only demos / empty, force explorer once more
    setTimeout(function () {
      try {
        var onlyDemo = state.items && state.items.length && String(state.items[0].id || "").indexOf("demo") === 0;
        var empty = !state.items || !state.items.length;
        if (onlyDemo || empty) {
          state.feedMode = "all";
          state.loading = false;
          load(false);
        }
      } catch (e) {}
      try { if (statusEl) statusEl.style.display = "none"; } catch (e) {}
    }, 5000);
  })();
  

/* ===== inline block 5 ===== */

(function(){
  function el(id){ return document.getElementById(id); }
  var TOOL_IDS = ["dutyModal","loanModal","compareModal","contractModal","poaModal","landMapModal","diagModal","chassisModal"];

  function show(id){
    var n = el(id); if(!n) return;
    n.classList.remove("hidden");
    n.classList.add("flex");
    n.style.display = "flex";
  }
  function hide(id){
    var n = el(id); if(!n) return;
    n.classList.add("hidden");
    n.classList.remove("flex");
    n.style.display = "none";
  }
  function closeAllTools(){ TOOL_IDS.forEach(hide); }
  function closeAll(){
    closeAllTools();
    ["aiModal","analysisView","modalOverlay","brokerRegModal","roleSelectModal"].forEach(hide);
    try { document.body.style.overflow = ""; } catch(e){}
  }
  function seedChat(){
    var log = el("advisorChatLog");
    if(!log) return;
    if(log.dataset.seeded === "1" && log.children.length) return;
    log.innerHTML = '<div class="chat-bubble-ai"><div class="text-[9px] font-bold text-cyan-300 mb-0.5">አዲካ ዲጂታል አማካሪ</div><div class="text-xs font-medium leading-relaxed">ሰላም። በአዲካ ዲጂታል ሲስተም የፋይናንስ አማካሪ ነኝ። ስለ መኪና፣ ቤት፣ ብድር ወይም ኢንቨስትመንት በአማርኛ ይጠይቁኝ — ዋጋ ከገበያ ዝርዝር ካለ ብቻ እጠቀማለሁ።</div></div>';
    log.dataset.seeded = "1";
  }
  function openChat(){
    window.__adikaChatFrom = "hub";
    var tools = el("aiModal");
    if(tools){ tools.classList.add("hidden"); tools.classList.remove("flex"); tools.style.display="none"; }
    closeAllTools();
    var n = el("analysisView");
    if(n){ n.classList.remove("hidden"); n.classList.add("flex"); n.style.display="flex"; n.style.zIndex="280"; }
    seedChat();
  }
  function openTools(){
    hide("analysisView");
    closeAllTools();
    var n = el("aiModal");
    if(n){ n.classList.remove("hidden"); n.classList.add("flex"); n.style.display="flex"; n.style.zIndex="260"; }
  }
  function openHome(){
    closeAll();
    try { if (window.restoreHomeChrome) window.restoreHomeChrome(); } catch(e){}
    try{ window.scrollTo({top:0,behavior:"smooth"}); }catch(e){ window.scrollTo(0,0); }
  }

  window.closeModal = function(id){
    if(id) hide(id);
    else closeAll();
    if(id && TOOL_IDS.indexOf(id) !== -1) openTools();
  };
  window.navigateBack = function(id){
    if(id === "analysisView"){ hide("analysisView"); openTools(); return; }
    if(id && TOOL_IDS.indexOf(id) !== -1){ hide(id); openTools(); return; }
    if(id) hide(id);
    else openHome();
  };
  window.goHomeFromTool = function(id){
    if(id) hide(id);
    openHome();
  };
  window.openAiChat = openChat;
  window.handleStartAiChat = window.handleStartAiChat || function(){ openChat(); };

  function setLang(en){
    document.body.classList.toggle("lang-en-active", !!en);
    document.documentElement.lang = en ? "en" : "am";
    var am = el("langAmBtn"), enBtn = el("langEnBtn");
    if(am) am.className = en ? "px-2 py-1 rounded-lg text-xs font-extrabold transition-all text-white/80" : "px-2 py-1 rounded-lg text-xs font-extrabold transition-all bg-white text-[#16acbd] shadow-sm";
    if(enBtn) enBtn.className = en ? "px-2 py-1 rounded-lg text-xs font-extrabold transition-all bg-white text-[#16acbd] shadow-sm" : "px-2 py-1 rounded-lg text-xs font-extrabold transition-all text-white/80";
  }
  function paintLive(items){
    if(window.__adikaPaintListings) window.__adikaPaintListings(items);
    window.__adikaLiveItems = items || [];
  }
  function loadListings(extra){
    var qs = "page=1&limit=40&order=DESC&active_only=1" + (extra||"");
    var buy = /type=BUY/i.test(extra||"") || !!window.__adikaIsBuy;
    fetch("/api/listings?"+qs,{credentials:"same-origin"}).then(function(r){return r.json();}).then(function(d){
      var items = (d && (d.items||d.listings||d.results||d.data)) || [];
      if(!Array.isArray(items) && items && items.items) items = items.items;
      function isBuyItem(it){
        var t=((it&&it.req_type)||"")+" "+((it&&it.action_type)||"")+" "+((it&&it.listing_type)||"");
        return /BUY|REQUEST|WANT|መግዛት|ለመግዛት|ፈላጊ/i.test(t);
      }
      if(Array.isArray(items)){
        items = buy ? items.filter(isBuyItem) : items.filter(function(it){ return !isBuyItem(it); });
        paintLive(items);
      }
    }).catch(function(){
      if(buy) paintLive([]);
    });
  }
  function markTabs(buy){
    var s = el("tabSell"), b = el("tabBuy");
    if(s) s.className = buy ? "py-1 rounded-lg text-xs font-bold transition-all text-white/90 hover:text-white flex items-center justify-center gap-1" : "py-1 rounded-lg text-xs font-bold transition-all bg-white text-[#16acbd] shadow-sm flex items-center justify-center gap-1";
    if(b) b.className = buy ? "py-1 rounded-lg text-xs font-bold transition-all bg-white text-[#16acbd] shadow-sm flex items-center justify-center gap-1" : "py-1 rounded-lg text-xs font-bold transition-all text-white/90 hover:text-white flex items-center justify-center gap-1";
    window.__adikaIsBuy = !!buy;
  }
  function markCats(id){
    document.querySelectorAll("#cats .cat-pill").forEach(function(b){
      if(b.getAttribute("data-filter")==="chassis") return;
      var on = (b.getAttribute("data-id")||"") === id;
      b.className = on
        ? "cat-pill px-3 py-1 rounded-full text-xs font-bold whitespace-nowrap transition-all bg-white text-[#16acbd] shadow-sm"
        : "cat-pill px-3 py-1 rounded-full text-xs font-bold whitespace-nowrap transition-all bg-white/20 text-white hover:bg-white/30";
    });
  }
  function parentModal(node){
    var n = node;
    while(n && n !== document.body){
      if(n.id && (TOOL_IDS.indexOf(n.id)>=0 || n.id==="analysisView" || n.id==="aiModal" || n.id==="modalOverlay")) return n.id;
      n = n.parentElement;
    }
    return "";
  }
  function fmt(n){ return Math.round(Number(n)||0).toLocaleString("en-US"); }
  function calcLoanLocal(){
    var price = Number((el("loanPrice")||{}).value||3000000);
    var downPct = Number((el("loanDown")||{}).value||30);
    var years = Number((el("loanYears")||{}).value||10);
    var down = price * downPct/100;
    var principal = Math.max(0, price-down);
    var months = years*12;
    var r = 0.18/12;
    var mo = principal * (r*Math.pow(1+r,months))/(Math.pow(1+r,months)-1);
    var box = el("loanResult");
    if(!box) return;
    box.classList.remove("hidden");
    box.innerHTML = '<div class="text-xs space-y-1"><div class="font-black text-emerald-700 text-lg">'+fmt(mo)+' ETB / ወር</div><div>ቅድመ ክፍያ: <b>'+fmt(down)+' ETB</b></div><div>የብድር መጠን: <b>'+fmt(principal)+' ETB</b></div><div>ወለድ: 18% · '+years+' ዓመት</div></div>';
  }
  function calcDutyLocal(){
    var cif = Number((el("dutyCif")||{}).value||12000);
    var fuel = ((el("dutyFuel")||{}).value||"Benzine");
    var cc = Number((el("dutyCc")||{}).value||1300);
    var rate = /electric/i.test(fuel) ? 0.05 : (cc>=1800?0.35:0.30);
    var etb = cif * 130;
    var duty = etb * rate;
    var excise = etb * 0.30;
    var vat = (etb+duty+excise)*0.15;
    var total = duty+excise+vat;
    var box = el("dutyResult");
    if(!box) return;
    box.classList.remove("hidden");
    box.innerHTML = '<div class="text-xs space-y-1"><div class="font-black text-[#0e7490] text-lg">'+fmt(total)+' ETB</div><div>ቀረጥ: <b>'+fmt(duty)+'</b></div><div>ኤክሳይስ: <b>'+fmt(excise)+'</b></div><div>ቫት: <b>'+fmt(vat)+'</b></div></div>';
  }

  window.__cStep = window.__cStep || 0;
  function localOpp(){
    var budget = Number((el("advisorBudget")||{}).value || 2000000);
    var income = Number((el("advisorMonthlyIncome")||{}).value || 25000);
    var down = Math.round(budget*0.3);
    var items = window.__adikaLiveItems || [];
    function price(it){ return Number(String(it.price||"").replace(/[^\d.]/g,""))||0; }
    function name(it){ return [it.brand,it.model].filter(Boolean).join(" ") || it.sub_category || it.title || "ማስታወቂያ"; }
    function isCar(it){ return /መኪና|car|vehicle|auto/i.test((it.main_category||"")+" "+(it.category||"")); }
    function isHouse(it){ return /ቤት|house|propert|land|apartment/i.test((it.main_category||"")+" "+(it.category||"")); }
    var cars = items.filter(function(it){ var p=price(it); return isCar(it)&&p>0&&p<=budget; }).slice(0,3);
    var homes = items.filter(function(it){ var p=price(it); return isHouse(it)&&p>0&&(p<=budget||p*0.3<=budget); }).slice(0,3);
    var autoTxt = cars.length ? cars.map(function(it){ var p=price(it); return "• "+name(it)+" — "+fmt(p)+" ብር"; }).join("<br>") : "ከአዲካ ገበያ በዚህ በጀት ተሽከርካሪ አልተገኘም። ቅድመ 30% "+fmt(down)+" ብር።";
    var homeTxt = homes.length ? homes.map(function(it){ return "• "+name(it)+" — "+fmt(price(it))+" ብር"; }).join("<br>") : "በ "+fmt(budget)+" ብር የሚገባ ቤት/መሬት አልተገኘም።";
    if(el("oppAutoBody")) el("oppAutoBody").innerHTML = "ተሽከርካሪ + የባንክ ብድር<br>"+autoTxt;
    if(el("oppPropBody")) el("oppPropBody").innerHTML = "ሪል እስቴት · ቅድመ ክፍያ<br>"+homeTxt;
    if(el("oppRoiBody")) el("oppRoiBody").innerHTML = "በጀት "+fmt(budget)+" ብር<br>• ROI 15% → "+fmt(budget*0.15)+" ብር/ዓመት<br>• ROI 22% → "+fmt(budget*0.22)+" ብር/ዓመት<br>• ROI 28% → "+fmt(budget*0.28)+" ብር/ዓመት<br>ወርሃዊ ገቢ: "+fmt(income)+" ብር";
    var cards = el("opportunityCards");
    if(cards){ cards.classList.remove("hidden"); cards.style.display="block"; }
    document.body.classList.add("hub-results-open");
    var dock = el("hubToolsDock"); if(dock) dock.style.display="none";
    var rnav = el("hubResultsNav"); if(rnav){ rnav.classList.remove("hidden"); rnav.style.display="flex"; }
    try{ var wrap=el("aiToolsView"); if(wrap){ wrap.scrollTop = 0; } }catch(e){}
  }
  function closeHubResults(){
    document.body.classList.remove("hub-results-open");
    var cards = el("opportunityCards");
    if(cards){ cards.classList.add("hidden"); cards.style.display="none"; }
    var dock = el("hubToolsDock"); if(dock) dock.style.display="";
    var rnav = el("hubResultsNav"); if(rnav){ rnav.classList.add("hidden"); rnav.style.display="none"; }
  }
  window.closeHubResults = closeHubResults;

  window.genBudget = localOpp;
  window.renderOpportunityCards = window.renderOpportunityCards || localOpp;

  function localCompare(){
    var a = ((el("compareCar1")||{}).value||"Toyota Vitz");
    var b = ((el("compareCar2")||{}).value||"BYD Dolphin");
    var y1 = ((el("compareYear1")||{}).value||"2018");
    var y2 = ((el("compareYear2")||{}).value||"2023");
    var box = el("compareResult");
    if(!box) return;
    box.classList.remove("hidden");
    box.innerHTML = '<div class="rounded-2xl border border-slate-700 bg-slate-900/80 p-3 text-white text-xs space-y-2">'+
      '<div class="font-black text-emerald-400">ውጤት</div>'+
      '<div><b>'+a+' ('+y1+')</b> vs <b>'+b+' ('+y2+')</b></div>'+
      '<div class="text-slate-300">አዲሱ ሞዴል በነዳጅ/ኤሌክትሪክ ወጪና ዋጋ ረጅም ጊዜ ሊበልጥ ይችላል። ትክክለኛ የገበያ ዋጋ ከአዲካ ዝርዝር ይመልከቱ።</div>'+
      '<button type="button" class="opp-chat-cta w-full py-2 rounded-xl bg-teal-600 font-bold">ጥልቅ ትንተና Live Chat ያድርጉ →</button>'+
      '</div>';
  }

  function localContractStep(delta){
    if(delta) window.__cStep = Math.max(0, Math.min(3, (window.__cStep||0)+delta));
    var n = window.__cStep||0;
    [0,1,2,3].forEach(function(i){
      var panel = el("contractStep"+i);
      if(panel) panel.classList.toggle("hidden", i!==n);
    });
    document.querySelectorAll(".contract-step-tab").forEach(function(btn){
      var s = Number(btn.getAttribute("data-step"));
      btn.className = s===n
        ? "contract-step-tab py-1.5 rounded-lg text-[9px] font-extrabold transition-all bg-white text-[#0e7490] shadow-sm"
        : "contract-step-tab py-1.5 rounded-lg text-[9px] font-extrabold transition-all text-slate-500";
    });
    var prev = el("cStepPrev"), next = el("cStepNext");
    if(prev) prev.classList.toggle("hidden", n<=0);
    if(next){ next.classList.toggle("hidden", n>=3); next.textContent = n>=3 ? "ጨርስ" : "ቀጣይ →"; }
  }
  function localContractFinish(finalized){
    var box = el("contractResult");
    if(!box) return;
    box.classList.remove("hidden");
    var seller = (el("cSellerName")||{}).value || "ሻጭ";
    var buyer = (el("cBuyerName")||{}).value || "ገዢ";
    var price = (el("cTotalPrice")||{}).value || "0";
    box.innerHTML = '<div class="text-xs space-y-1"><div class="font-black text-emerald-700">'+(finalized?"ውሉ ተጠናቅቋል":"ረቂቅ ተቀምጧል")+'</div><div>ሻጭ: <b>'+seller+'</b></div><div>ገዢ: <b>'+buyer+'</b></div><div>ዋጋ: <b>'+price+' ETB</b></div><div class="text-slate-500">PDF ለማውረድ ከሰርቨር ጋር ሲገናኝ ይቀጥላል።</div></div>';
    box.scrollIntoView({behavior:"smooth",block:"nearest"});
  }

  function localChassis(vin){
    vin = String(vin||"").trim().toUpperCase();
    var box = el("chassisResult");
    if(!box) return;
    box.classList.remove("hidden");
    if(vin.length<5){
      box.innerHTML = '<div class="p-3 bg-rose-50 border border-rose-200 rounded-2xl text-rose-800 text-xs font-bold">⚠️ እባክዎን የሻሲ ቁጥር ያስገቡ።</div>';
      return;
    }
    var map = {
      "JTDKB20U00189342": ["Toyota","Vitz","2012","Japan","1.3L Benzine"],
      "KMHD381CBKU782910": ["Hyundai","Tucson","2019","Korea","2.0L Diesel"],
      "LGXC12480PA093821": ["BYD","Song Plus","2023","China","Electric"],
      "MA3FBE41S00123984": ["Suzuki","Dzire","2018","India","1.2L Benzine"]
    };
    var d = map[vin] || ["—","ከ VIN ቅድመ-ፊደል","—","—","—"];
    if(!map[vin]){
      if(vin.indexOf("JTD")===0) d=["Toyota","(VIN ግምት)","—","Japan","Benzine"];
      else if(vin.indexOf("KMH")===0) d=["Hyundai","(VIN ግምት)","—","Korea","—"];
      else if(vin.indexOf("LGX")===0) d=["BYD","(VIN ግምት)","—","China","EV"];
      else if(vin.indexOf("MA3")===0) d=["Suzuki","(VIN ግምት)","—","India","—"];
    }
    box.innerHTML = '<div class="p-3 bg-slate-900 text-white rounded-2xl text-xs space-y-1">'+
      '<div class="text-emerald-400 font-black">✓ ሻሲ ተነቧል</div>'+
      '<div class="font-black text-sm">'+d[0]+' '+d[1]+'</div>'+
      '<div class="font-mono text-slate-400">'+vin+'</div>'+
      '<div>አመት: '+d[2]+' · አገር: '+d[3]+' · ሞተር: '+d[4]+'</div></div>';
    fetch("/api/verify-chassis",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({vin:vin})})
      .then(function(r){return r.json();})
      .then(function(res){
        if(res && res.data && res.data.specs){
          var sp=res.data.specs;
          box.innerHTML = '<div class="p-3 bg-slate-900 text-white rounded-2xl text-xs space-y-1">'+
            '<div class="text-emerald-400 font-black">✓ Official Specs</div>'+
            '<div class="font-black text-sm">'+(sp.make||"")+" "+(sp.model||"")+'</div>'+
            '<div class="font-mono text-slate-400">'+(sp.vin||vin)+'</div>'+
            '<div>አመት: '+(sp.year||"—")+' · '+(sp.country||"")+' · '+(sp.engine||sp.fuel_type||"")+'</div></div>';
        }
      }).catch(function(){});
  }

  function localDiag(){
    var model = ((el("diagCarModel")||{}).value||"መኪና");
    var txt = ((el("diagInput")||el("diagNotes")||{}).value||"");
    var box = el("diagResult") || el("diagAnalyzeBtn");
    var out = el("diagResult");
    if(!out){
      out = document.createElement("div");
      out.id="diagResult";
      var btn=el("diagAnalyzeBtn");
      if(btn&&btn.parentNode) btn.parentNode.appendChild(out);
    }
    out.classList.remove("hidden");
    out.innerHTML = '<div class="p-3 bg-slate-50 border rounded-xl text-xs">'+
      '<div class="font-black text-slate-800">የምርመራ ማጠቃለያ — '+model+'</div>'+
      '<div class="text-slate-600 mt-1">'+(txt||"ጽሁፍ ካልገባ የተጫነው ወረቀት ብቻ ይታያል። ግልጽ ያልሆነ ወጪ አንገምትም።")+'</div>'+
      '<button type="button" class="opp-chat-cta mt-2 w-full py-2 rounded-xl bg-[#16acbd] text-white font-bold">ስለ '+model+' አማክር →</button></div>';
  }

  document.addEventListener("click", function(e){

    var t = e.target.closest("button, a, .cat-pill, .opp-chat-cta, .compare-tab, .vin-sample-chip, [data-live], .adika-card, #adikaPromoBanner, #hubFinanceAdvisorBanner");
    if(!t) return;
    var id = t.id || "";
    var mid = parentModal(t);

    if(t.classList.contains("cat-pill") || (t.closest && t.closest("#cats"))){
      var pill = t.classList.contains("cat-pill") ? t : t.closest(".cat-pill");
      if(pill && pill.getAttribute("data-filter")==="chassis"){
        e.preventDefault(); e.stopPropagation();
        loadListings("&has_chassis=1");
        return;
      }
      if(pill){
        e.preventDefault(); e.stopPropagation();
        var cid = pill.getAttribute("data-id") || "all";
        markCats(cid);
        if(cid==="foryou"){
          if (typeof requireOnboardingForFyp === "function" && requireOnboardingForFyp()) return;
          if (typeof load === "function") { try { state.feedMode = "foryou"; state.category = ""; load(false); return; } catch (eL) {} }
          fetch("/api/feed/for-you",{credentials:"same-origin"}).then(function(r){return r.json();}).then(function(d){
            var items=(d&& (d.items||d.listings||d.results))||[];
            if(Array.isArray(items) && items.length) paintLive(items);
            else loadListings("");
          }).catch(function(){ loadListings(""); });
        } else if(cid==="all"){
          loadListings("");
        } else {
          loadListings("&category="+encodeURIComponent(cid));
        }
        return;
      }
    }

    if(id==="tabBuy"){
      e.preventDefault(); e.stopPropagation();
      try {
        if (typeof window.state !== "undefined") window.state.tab = "requests";
        window.__adikaIsBuy = true;
      } catch (e2) {}
      if (typeof markTabs === "function") markTabs(true);
      try {
        if (typeof load === "function" && window.state) { load(false); return; }
      } catch (e3) {}
      try {
        var g = document.getElementById("grid");
        if (g) g.innerHTML = "";
      } catch (e4) {}
      if (typeof window.fetchBuyerRequests === "function") {
        window.fetchBuyerRequests({ limit: 40 }).then(function(items){
          if (typeof paintLive === "function") paintLive(items || []);
          else if (window.__adikaPaintListings) window.__adikaPaintListings(items || []);
        }).catch(function(){ loadListings("&type=BUY"); });
      } else {
        loadListings("&type=BUY");
      }
      return;
    }
    if(id==="tabSell"){
      e.preventDefault(); e.stopPropagation();
      try {
        if (typeof window.state !== "undefined") window.state.tab = "marketplace";
        window.__adikaIsBuy = false;
      } catch (e2) {}
      if (typeof markTabs === "function") markTabs(false);
      try {
        if (typeof load === "function" && window.state) { load(false); return; }
      } catch (e3) {}
      try {
        var g2 = document.getElementById("grid");
        if (g2) g2.innerHTML = "";
      } catch (e4) {}
      loadListings("&type=SELL");
      return;
    }
    if(id==="langAmBtn"){ e.preventDefault(); e.stopPropagation(); setLang(false); return; }
    if(id==="langEnBtn"){ e.preventDefault(); e.stopPropagation(); setLang(true); return; }

    if(id==="adikaPromoBanner" || id==="heroToolsBtn" || id==="heroAdvisorBtn" || id==="navAi" || (t.closest && t.closest("#adikaPromoBanner"))){
      e.preventDefault(); e.stopPropagation(); openTools(); return;
    }
    if(id==="navHome"){ e.preventDefault(); e.stopPropagation(); openHome(); return; }
    if(id==="inboxBackBtn"){ e.preventDefault(); e.stopPropagation(); var pane=document.getElementById("inboxThreadPane"); if(pane && !pane.classList.contains("hidden")){ if(window.openInbox) openInbox(); return; } if(window.closeInbox) closeInbox(); return; }
    if(id==="inboxCloseBtn"){ e.preventDefault(); e.stopPropagation(); if(window.closeInbox) closeInbox(); return; }
    if(id==="myListingsBackBtn"||id==="myListingsCloseBtn"){ e.preventDefault(); e.stopPropagation(); if(window.goBack) goBack(); else if(window.hideMyListingsView) hideMyListingsView(); return; }
    if(id==="navMyListings"||id==="navMessages"){ e.preventDefault(); e.stopPropagation(); if(window.openMyListings) openMyListings(); else if(window.openInbox) openInbox(); return; }
    if(id==="navHelp"){ e.preventDefault(); e.stopPropagation(); alert("Adika Marketplace\n@AdikaMarketplaceBot"); return; }
    if(id==="fabBtn"){ e.preventDefault(); e.stopPropagation(); if(window.openIntentModal){ window.openIntentModal(); return; } location.href = window.__adikaIsBuy ? "/buyer-form" : "/seller-form"; return; }
    if(id==="brokerCtaHome"){ e.preventDefault(); e.stopPropagation(); show("brokerRegModal"); return; }

    if(id==="analysisHomeBtn"){ e.preventDefault(); e.stopPropagation(); hide("analysisView"); openHome(); return; }
    if(id==="analysisBackBtn" || id==="analysisCloseBtn"){ e.preventDefault(); e.stopPropagation(); hide("analysisView"); openTools(); return; }

    if(id==="aiHubBackBtn"){ e.preventDefault(); e.stopPropagation(); if(document.body.classList.contains("hub-results-open") && window.closeHubResults){ closeHubResults(); return; } openHome(); return; }
    if(id==="aiModalClose"){ e.preventDefault(); e.stopPropagation(); openHome(); return; }
    if(id==="aiTabTools"){ e.preventDefault(); e.stopPropagation(); if(el("aiToolsView")){ el("aiToolsView").classList.remove("hidden"); el("aiToolsView").style.display=""; } if(el("aiSearchView")){ el("aiSearchView").classList.add("hidden"); el("aiSearchView").style.display="none"; } return; }
    if(id==="aiTabSearch"){ e.preventDefault(); e.stopPropagation(); if(el("aiSearchView")){ el("aiSearchView").classList.remove("hidden"); el("aiSearchView").classList.add("flex"); el("aiSearchView").style.display="flex"; el("aiSearchView").style.pointerEvents="auto"; } return; }
    if(t.classList.contains("ai-chip")){
      e.preventDefault(); e.stopPropagation();
      var q = t.getAttribute("data-q")||t.textContent||"";
      if(el("aiPrompt")) el("aiPrompt").value = ((el("aiPrompt").value||"")+" "+q).trim();
      t.classList.toggle("ring-2"); t.classList.toggle("ring-cyan-300");
      return;
    }
    if(t.classList.contains("price-chip")){
      e.preventDefault(); e.stopPropagation();
      var pr = t.getAttribute("data-price")||"";
      if(el("aiPrompt")) el("aiPrompt").value = ((el("aiPrompt").value||"")+" "+pr).trim();
      document.querySelectorAll(".price-chip").forEach(function(c){ c.classList.remove("ring-2","ring-cyan-300"); });
      t.classList.add("ring-2","ring-cyan-300");
      return;
    }
    if(id==="aiResetBtn"){
      e.preventDefault(); e.stopPropagation();
      if(el("aiPrompt")) el("aiPrompt").value="";
      document.querySelectorAll(".ai-chip,.price-chip").forEach(function(c){ c.classList.remove("ring-2","ring-cyan-300"); });
      return;
    }
    if(id==="aiApplyBtn"){
      e.preventDefault(); e.stopPropagation();
      var q = ((el("aiPrompt")||{}).value||"").trim();
      if(el("q")) el("q").value = q;
      if(el("aiSearchView")){ el("aiSearchView").style.display="none"; el("aiSearchView").classList.add("hidden"); }
      openHome();
      if(q) loadListings("&q="+encodeURIComponent(q));
      else loadListings("");
      return;
    }

    if(t.classList.contains("advisor-preset-chip")){
      e.preventDefault(); e.stopPropagation();
      var b = t.getAttribute("data-budget");
      if(el("advisorBudget") && b) el("advisorBudget").value = b;
      return;
    }
    if(id==="advisorBtn"){ e.preventDefault(); e.stopPropagation(); if(typeof window.renderOpportunityCards==="function") window.renderOpportunityCards(); else if(window.genBudget) window.genBudget(); else localOpp(); return; }
    if(t.classList.contains("compare-tab") || t.getAttribute("data-ctab")){
      e.preventDefault(); e.stopPropagation();
      var tab = t.classList.contains("compare-tab") ? t : t.closest(".compare-tab");
      var mode = (tab && tab.getAttribute("data-ctab")) || "vehicles";
      document.querySelectorAll(".compare-tab").forEach(function(x){
        x.className = "compare-tab flex-1 py-1.5 rounded-full text-[10px] font-extrabold transition-all text-slate-300 hover:text-white bg-white/5";
      });
      if(tab) tab.className = "compare-tab flex-1 py-1.5 rounded-full text-[10px] font-extrabold transition-all bg-teal-600 text-white shadow";
      var pv=el("comparePanelVehicles"), pp=el("comparePanelProperty"), pb=el("comparePanelBusiness");
      if(pv){ pv.classList.toggle("hidden", mode!=="vehicles"); pv.style.display = mode==="vehicles" ? "block" : "none"; }
      if(pp){ pp.classList.toggle("hidden", mode!=="property"); pp.style.display = mode==="property" ? "block" : "none"; }
      if(pb){ pb.classList.toggle("hidden", mode!=="business"); pb.style.display = mode==="business" ? "block" : "none"; }
      return;
    }
    if(id==="compareBtn"){ e.preventDefault(); e.stopPropagation(); localCompare(); return; }
    if(id==="cStepNext"){ e.preventDefault(); e.stopPropagation(); localContractStep(1); return; }
    if(id==="cStepPrev"){ e.preventDefault(); e.stopPropagation(); localContractStep(-1); return; }
    if(t.classList.contains("contract-step-tab")){ e.preventDefault(); e.stopPropagation(); window.__cStep=Number(t.getAttribute("data-step")||0); localContractStep(0); return; }
    if(id==="cFinalizeBtn" || id==="cSaveDraftBtn"){ e.preventDefault(); e.stopPropagation(); localContractFinish(id==="cFinalizeBtn"); return; }
    if(t.classList.contains("vin-sample-chip")){ e.preventDefault(); e.stopPropagation(); var vin=t.getAttribute("data-vin")||""; if(el("chassisInput")) el("chassisInput").value=vin; localChassis(vin); return; }
    if(id==="chassisVerifyBtn"){ e.preventDefault(); e.stopPropagation(); localChassis((el("chassisInput")||{}).value||""); return; }
    if(id==="diagAnalyzeBtn"){ e.preventDefault(); e.stopPropagation(); localDiag(); return; }
    if(id==="hubFinanceAdvisorBanner" || id==="liveFromA" || id==="liveFromB" || id==="liveFromC" || t.classList.contains("opp-chat-cta")){
      e.preventDefault(); e.stopPropagation(); openChat(); return;
    }

    if(id==="toolDutyBtn"){ e.preventDefault(); e.stopPropagation(); show("dutyModal"); return; }
    if(id==="toolLoanBtn"){ e.preventDefault(); e.stopPropagation(); show("loanModal"); return; }
    if(id==="toolCompareBtn"){ e.preventDefault(); e.stopPropagation(); show("compareModal"); return; }
    if(id==="toolContractBtn"){ e.preventDefault(); e.stopPropagation(); show("contractModal"); return; }
    if(id==="toolPoaBtn"){ e.preventDefault(); e.stopPropagation(); show("poaModal"); return; }
    if(id==="toolDiagBtn"){ e.preventDefault(); e.stopPropagation(); show("diagModal"); return; }
    if(id==="toolChassisBtn"){ e.preventDefault(); e.stopPropagation(); show("chassisModal"); return; }
    if(id==="toolLandMapBtn"){ e.preventDefault(); e.stopPropagation(); show("landMapModal"); return; }

    if(id==="dutyCalculateBtn"){ e.preventDefault(); e.stopPropagation(); calcDutyLocal(); return; }
    if(id==="loanCalculateBtn"){ e.preventDefault(); e.stopPropagation(); calcLoanLocal(); return; }

    if(t.classList.contains("btn-back") || t.classList.contains("btn-close") || /ተመለስ|ዋና ገፅ|ሀብ/.test(t.textContent||"")){
      e.preventDefault(); e.stopPropagation();
      if(el("analysisView") && el("analysisView").style.display==="flex"){ hide("analysisView"); openTools(); return; }
      if(/ዋና ገፅ/.test(t.textContent||"") || /Home/i.test(t.textContent||"")){
        if(mid) hide(mid);
        openHome();
        return;
      }
      window.navigateBack(mid || "aiModal");
      return;
    }

    if(id==="modalClose" || id==="modalBackBtn" || id==="aiSearchBackBtn" || id==="aiSearchCloseBtn"){
      e.preventDefault(); e.stopPropagation();
      if(id.indexOf("Search")>=0){ if(el("aiSearchView")) { el("aiSearchView").classList.add("hidden"); el("aiSearchView").style.display="none"; } if(el("aiToolsView")) el("aiToolsView").classList.remove("hidden"); return; }
      // Must restore header/nav — do NOT use closeAll() alone
      if(window.closeDetailModalPreserve) window.closeDetailModalPreserve();
      else if(typeof closeDetailModalPreserve === "function") closeDetailModalPreserve();
      else {
        closeAll();
        try {
          var h=document.getElementById("adikaFixedHeader");
          if(h){ h.style.visibility="visible"; h.style.display=""; h.classList.remove("hidden"); }
          var n=document.getElementById("adikaBottomNav"); if(n){ n.classList.remove("hidden"); n.style.setProperty("display","flex","important"); }
          var f=document.getElementById("fabBtn"); if(f) f.style.display="";
        } catch(e2){}
      }
      return;
    }
    if(id==="modalChatBtn"){ e.preventDefault(); e.stopPropagation(); if(window.closeDetailModalPreserve) window.closeDetailModalPreserve(); else hide("modalOverlay"); if(window.openListingMessage) openListingMessage(); return; }

    if(t.getAttribute("data-live")==="1" || (t.classList && t.classList.contains("adika-card")) || (t.closest && t.closest(".adika-card"))){
      var card = (t.closest && t.closest(".adika-card")) || t;
      if(!card) return;
      var items = window.__adikaLiveItems || [];
      var it = card._adikaItem || null;
      if(!it){
        var cards = Array.prototype.slice.call(document.querySelectorAll("#grid .adika-card"));
        var idx = cards.indexOf(card);
        if(idx >= 0 && items[idx]) it = items[idx];
      }
      if(!it){
        var did = card.getAttribute("data-id");
        if(did && items.length){
          for(var ii=0;ii<items.length;ii++){ if(String(items[ii].id)===String(did)){ it=items[ii]; break; } }
        }
      }
      if(!it) return;
      e.preventDefault(); e.stopPropagation();
      var prePhotos = null;
      try {
        prePhotos = card._adikaPhotos || it._resolved_photos || null;
        if ((!prePhotos || !prePhotos.length) && card.getAttribute("data-photo-src")) {
          prePhotos = [card.getAttribute("data-photo-src")];
        }
        // If card DOM still has a visible img, use its current src (exact Home feed image)
        if ((!prePhotos || !prePhotos.length) && card.querySelector) {
          var imgEl = card.querySelector("img[data-adika-photo], .listing-photo-enhance, img");
          if (imgEl && imgEl.getAttribute("src")) prePhotos = [imgEl.getAttribute("src")];
        }
      } catch (e) { prePhotos = null; }
      if(window.openDetailModal){
        try { window.openDetailModal(it, prePhotos); } catch(err){ console.error("openDetailModal", err); }
      } else if(typeof openDetailModal === "function"){
        try { openDetailModal(it, prePhotos); } catch(err){ console.error("openDetailModal", err); }
      } else {
        // last-resort partial fill
        if(el("modalTitle")) el("modalTitle").textContent = (it.brand&&it.model)?(it.brand+" "+it.model):(it.sub_category||it.title||"ማስታወቂያ");
        if(el("modalPrice")){
          var n=Number(String(it.price||"").replace(/[^\d.]/g,""));
          el("modalPrice").textContent = (!n||n<=0||n>300000000)?"ለዋጋ ደውሉ":(Math.round(n).toLocaleString("en-US")+" ETB");
        }
        if(el("modalDesc")) el("modalDesc").textContent = it.description||"";
        show("modalOverlay");
      }
      return;
    }
  }, true);

  var send = el("advisorChatSend");
  if(send && !send.__bound2){
    send.__bound2 = true;
    send.addEventListener("click", function(){
      var inp = el("advisorChatInput");
      var log = el("advisorChatLog");
      var msg = inp ? String(inp.value||"").trim() : "";
      if(!msg) return;
      if(log) log.innerHTML += '<div class="text-right"><span class="inline-block bg-teal-600 text-white p-2 rounded-2xl">'+msg+"</span></div>";
      if(inp) inp.value="";
      fetch("/api/advisor/chat",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({message:msg})})
        .then(function(r){return r.json();})
        .then(function(d){ if(log) log.innerHTML += '<div class="bg-white p-2 rounded-2xl">'+(d.reply||d.message||d.text||"ተቀብያለሁ")+"</div>"; })
        .catch(function(){ if(log) log.innerHTML += '<div class="bg-white p-2 rounded-2xl">ተቀብያለሁ። በቅርቡ ዝርዝር መልስ ይደርሳል።</div>'; });
    });
  }
})();

/* ===== inline block 6 ===== */

(function(){
  function fitFeed(){
    var hdr = document.getElementById("adikaFixedHeader");
    var main = document.getElementById("adikaMainFeed");
    if(!hdr || !main) return;
    var h = Math.ceil(hdr.getBoundingClientRect().height || 0);
    main.style.paddingTop = (h + 6) + "px";
  }
  fitFeed();
  window.addEventListener("resize", fitFeed);
  setTimeout(fitFeed, 200);
  setTimeout(fitFeed, 800);
})();

/* ===== inline block 7 ===== */

(function(){
  function uid(){
    try{
      var u = window.Telegram && Telegram.WebApp && Telegram.WebApp.initDataUnsafe && Telegram.WebApp.initDataUnsafe.user;
      return String((u && u.id) || (window.state && state.userId) || "guest");
    }catch(e){ return "guest"; }
  }
  function uname(){
    try{
      var u = window.Telegram && Telegram.WebApp && Telegram.WebApp.initDataUnsafe && Telegram.WebApp.initDataUnsafe.user;
      if(!u) return "Adika User";
      return [u.first_name, u.last_name].filter(Boolean).join(" ") || u.username || "Adika User";
    }catch(e){ return "Adika User"; }
  }
  var ctx = { listing_id:"", peer_id:"", listing_title:"" };
  function showInbox(on){
    var v = document.getElementById("inboxView");
    if(!v) return;
    if(on){ v.classList.remove("hidden"); v.classList.add("flex"); v.style.display="flex"; }
    else { v.classList.add("hidden"); v.classList.remove("flex"); v.style.display="none"; }
  }
  function loadThreads(){
    var list = document.getElementById("inboxThreadList");
    var pane = document.getElementById("inboxThreadPane");
    if(list) list.classList.remove("hidden");
    if(pane) pane.classList.add("hidden");
    if(list) list.innerHTML = '<div class="text-center text-xs text-slate-500 py-6">እየጫነ ነው...</div>';
    fetch("/api/messages?user_id="+encodeURIComponent(uid()), {credentials:"same-origin"})
      .then(function(r){ return r.json(); })
      .then(function(d){
        var items = (d && d.items) || [];
        if(!list) return;
        if(!items.length){
          list.innerHTML = '<div class="text-center text-sm font-bold text-slate-500 py-10">መልእክት የለም<br><span class="text-[11px] font-medium">ከማስታወቂያ ላይ «መልእክት» ይጫኑ</span></div>';
          return;
        }
        list.innerHTML = items.map(function(it){
          return '<button type="button" class="w-full text-left bg-white rounded-2xl p-3 shadow-sm border border-slate-100 inbox-thread" data-lid="'+String(it.listing_id||"")+'" data-peer="'+String(it.peer_id||"")+'" data-title="'+(it.listing_title||"").replace(/"/g,"")+'">'+
            '<div class="font-black text-sm text-slate-800">'+(it.listing_title||"ማስታወቂያ")+'</div>'+
            '<div class="text-[11px] text-slate-500 mt-1 truncate">'+(it.last_message||"")+'</div></button>';
        }).join("");
      }).catch(function(){
        if(list) list.innerHTML = '<div class="text-center text-xs text-rose-500 py-6">መልእክት መጫን አልተሳካም</div>';
      });
  }
  function openThread(lid, peer, title){
    ctx.listing_id = String(lid||"");
    ctx.peer_id = String(peer||"");
    ctx.listing_title = title || "";
    var list = document.getElementById("inboxThreadList");
    var pane = document.getElementById("inboxThreadPane");
    var meta = document.getElementById("inboxThreadMeta");
    if(list) list.classList.add("hidden");
    if(pane) pane.classList.remove("hidden");
    if(meta) meta.textContent = ctx.listing_title || ("ውይይት #" + ctx.listing_id);
    loadThread();
  }
  function loadThread(){
    var log = document.getElementById("inboxThreadLog");
    if(!log) return;
    fetch("/api/messages?user_id="+encodeURIComponent(uid())+"&listing_id="+encodeURIComponent(ctx.listing_id)+"&peer_id="+encodeURIComponent(ctx.peer_id), {credentials:"same-origin"})
      .then(function(r){ return r.json(); })
      .then(function(d){
        var items = (d && d.items) || [];
        log.innerHTML = items.map(function(m){
          var mine = !!m.mine;
          return '<div class="'+(mine?"text-right":"text-left")+'"><div class="inline-block max-w-[80%] px-3 py-2 rounded-2xl text-[13px] '+(mine?"bg-[#16acbd] text-white":"bg-white border border-slate-200 text-slate-800")+'">'+(m.body||"")+'</div></div>';
        }).join("") || '<div class="text-center text-xs text-slate-400 py-6">መልእክት ይጀምሩ</div>';
        log.scrollTop = log.scrollHeight;
      }).catch(function(){});
  }
  function sendMsg(){
    var box = document.getElementById("inboxCompose");
    var text = box ? String(box.value||"").trim() : "";
    if(!text || !ctx.peer_id) return;
    fetch("/api/send_message", {
      method:"POST",
      headers:{"Content-Type":"application/json"},
      credentials:"same-origin",
      body: JSON.stringify({
        user_id: uid(),
        receiver_id: ctx.peer_id,
        listing_id: ctx.listing_id,
        listing_title: ctx.listing_title,
        sender_name: uname(),
        text: text
      })
    }).then(function(r){ return r.json(); }).then(function(d){
      if(box) box.value = "";
      loadThread();
    }).catch(function(){});
  }
  window.openInbox = function(){
    showInbox(true);
    try{
      var n=document.getElementById("adikaBottomNav"); if(n) n.style.display="none";
      var f=document.getElementById("fabBtn"); if(f) f.style.display="none";
    }catch(e){}
    loadThreads();
  };
  window.closeInbox = function(){
    showInbox(false);
    try{
      var n=document.getElementById("adikaBottomNav"); if(n){ n.classList.remove("hidden"); n.style.setProperty("display","flex","important"); }
      var f=document.getElementById("fabBtn"); if(f) f.style.display="";
    }catch(e){}
  };
  function sellerFromListing(listing){
    listing = listing || {};
    var extra = listing.extra_data || {};
    if(typeof extra === "string"){ try{ extra = JSON.parse(extra); }catch(e){ extra = {}; } }
    var peer = listing.user_chat_id || listing.user_id || listing.seller_id || listing.telegram_id || listing.owner_id || extra.user_id || extra.telegram_id || extra.chat_id || "";
    var uname = listing.telegram_username || listing.telegram_user || listing.user_name || extra.telegram_user || extra.telegram_username || extra.username || "";
    if(!uname){
      var m = String(listing.description||"").match(/@([A-Za-z0-9_]{4,})/);
      if(m) uname = m[1];
    }
    uname = String(uname||"").replace(/^@/,"");
    if(!peer && uname) peer = uname;
    return { peer: String(peer||""), uname: uname };
  }
  window.openListingMessage = function(listing){
    listing = listing || (window.state && state.selectedItem) || {};
    var s = sellerFromListing(listing);
    var peer = s.peer;
    if(!peer){
      var fallback = s.uname || "AkremFF";
      var url = "https://t.me/" + fallback;
      try{
        if(window.Telegram && Telegram.WebApp && Telegram.WebApp.openTelegramLink) Telegram.WebApp.openTelegramLink(url);
        else window.open(url, "_blank");
      }catch(e){ window.open(url, "_blank"); }
      return;
    }
    if(String(peer) === uid()){
      alert("የራስዎ ማስታወቂያ ነው");
      return;
    }
    showInbox(true);
    try{
      var n=document.getElementById("adikaBottomNav"); if(n) n.style.display="none";
      var f=document.getElementById("fabBtn"); if(f) f.style.display="none";
    }catch(e){}
    openThread(listing.id, peer, listing.sub_category || listing.title || listing.brand || "ማስታወቂያ");
  };
  document.addEventListener("click", function(e){
    var th = e.target.closest && e.target.closest(".inbox-thread");
    if(th){
      openThread(th.getAttribute("data-lid"), th.getAttribute("data-peer"), th.getAttribute("data-title"));
    }
  });
  var back = document.getElementById("inboxBackBtn");
  var close = document.getElementById("inboxCloseBtn");
  if(back) back.onclick = function(){
    var pane = document.getElementById("inboxThreadPane");
    if(pane && !pane.classList.contains("hidden")){ loadThreads(); return; }
    if(window.closeInbox) closeInbox(); else showInbox(false);
  };
  if(close) close.onclick = function(){ if(window.closeInbox) closeInbox(); else showInbox(false); };
  var send = document.getElementById("inboxSendBtn");
  if(send) send.onclick = sendMsg;
})();

/* ===== inline block 8 ===== */

(function(){
  function el(id){ return document.getElementById(id); }

  function tgId(){
    try{
      var u = window.Telegram && Telegram.WebApp && Telegram.WebApp.initDataUnsafe && Telegram.WebApp.initDataUnsafe.user;
      if(u && u.id != null) return String(u.id);
    }catch(e){}
    try{
      if(typeof getTelegramUserId === "function"){
        var id = getTelegramUserId();
        if(id != null && id !== "") return String(id);
      }
    }catch(e2){}
    try{ if(window.state && state.userId) return String(state.userId); }catch(e3){}
    return null;
  }

  function tgIdNum(){
    var s = tgId();
    var n = Number(s);
    return (isFinite(n) && n > 0) ? n : null;
  }

  function sb(){
    try{ if(typeof ensureSupabaseClient === "function") return ensureSupabaseClient(); }catch(e){}
    return window.supabase || null;
  }

  function hideMyListingsView(){
    var v = el("myListingsView");
    if(v){
      v.classList.add("hidden");
      v.classList.remove("flex");
      v.style.display = "none";
    }
    try{
      var main = el("adikaMainFeed") || el("mainFeed") || document.querySelector("main");
      if(main){
        main.style.removeProperty("display");
        main.classList.remove("hidden");
      }
    }catch(eM){}
    try{
      if(window.instantShowHomeChrome) instantShowHomeChrome();
      if(window.forceShowBottomNav) forceShowBottomNav();
      if(window.forceShowFab) forceShowFab();
      if(window.restoreHomeChrome) restoreHomeChrome();
    }catch(e2){}
    try{ document.body.style.overflow = ""; }catch(e3){}
  }
  window.hideMyListingsView = hideMyListingsView;
  window.goBack = function () {
    // Close detail / modals IMMEDIATELY
    try {
      var detail = document.getElementById("modalOverlay");
      if (detail) {
        detail.classList.add("hidden");
        detail.classList.remove("flex");
        detail.style.display = "none";
      }
    } catch (eD) {}
    try {
      if (window.closeDetailModalPreserve) closeDetailModalPreserve();
    } catch (eC) {}
    try {
      var mine = document.getElementById("myListingsView");
      if (mine && !mine.classList.contains("hidden") && mine.style.display !== "none") {
        hideMyListingsView();
      }
    } catch (e2) {}
    try {
      if (window.closeInbox) closeInbox();
    } catch (e3) {}
    // Instant chrome restore (same as Advisor speed)
    try {
      var bottomNav = document.getElementById("adikaBottomNav") || document.getElementById("bottom-nav") || document.querySelector(".bottom-nav");
      var fabBtn = document.getElementById("fabBtn") || document.getElementById("fab-add-btn") || document.querySelector(".floating-btn");
      if (bottomNav) {
        bottomNav.classList.remove("hidden");
        bottomNav.style.setProperty("display", "flex", "important");
        bottomNav.style.setProperty("visibility", "visible", "important");
        bottomNav.style.setProperty("opacity", "1", "important");
      }
      if (fabBtn) {
        fabBtn.classList.remove("hidden");
        fabBtn.style.setProperty("display", "flex", "important");
        fabBtn.style.setProperty("visibility", "visible", "important");
        fabBtn.style.setProperty("opacity", "1", "important");
      }
    } catch (eNav) {}
    try {
      if (window.instantShowHomeChrome) instantShowHomeChrome();
      if (window.forceShowBottomNav) forceShowBottomNav();
      if (window.forceShowFab) forceShowFab();
      if (window.restoreHomeChrome) restoreHomeChrome();
    } catch (e4) {}
  };
  window.closeModal = window.goBack;

  window.closeMyListings = hideMyListingsView;

  function showMyListingsView(){
    var v = el("myListingsView");
    if(!v) return;
    v.classList.remove("hidden");
    v.classList.add("flex");
    v.style.setProperty("display","flex","important");
    try{
      var n=el("adikaBottomNav"); if(n) n.style.setProperty("display","none","important");
      var f=el("fabBtn"); if(f) f.style.display="none";
    }catch(e){}
  }

  function esc(s){
    return String(s==null?"":s)
      .replace(/&/g,"&amp;").replace(/</g,"&lt;")
      .replace(/>/g,"&gt;").replace(/"/g,"&quot;");
  }
  function priceLabel(p){
    var n = Number(String(p||"").replace(/[^\d.]/g,""));
    if(!n || n<=0) return "ለዋጋ ደውሉ";
    try{ return Math.round(n).toLocaleString("en-US") + " ETB"; }catch(e){ return n + " ETB"; }
  }

  /** Resolve first photo from images / photo_urls / photos / image_url */
  function photoOf(item){
    if(!item) return "";
    var keys = ["images","photo_urls","photos","listing_photos","image_url","photo_url","image","photo"];
    for(var k=0;k<keys.length;k++){
      var p = item[keys[k]];
      if(p == null || p === "") continue;
      try{
        if(typeof getValidImageUrl === "function"){
          var gu = getValidImageUrl(p);
          if(gu) return gu;
        }
      }catch(e){}
      if(Array.isArray(p) && p.length){
        var first = p[0];
        if(typeof first === "string" && first) return first;
        if(first && typeof first === "object" && (first.url || first.src)) return first.url || first.src;
      }
      if(typeof p === "string"){
        var s = p.trim();
        if(!s) continue;
        if(s.charAt(0)==="["){
          try{
            var a = JSON.parse(s);
            if(Array.isArray(a) && a[0]){
              return typeof a[0]==="string" ? a[0] : (a[0].url || a[0].src || "");
            }
          }catch(e2){}
        }
        if(s.indexOf("http")===0 || s.indexOf("data:")===0 || s.indexOf("/")===0) return s;
      }
    }
    return "";
  }

  function renderCards(items){
    var grid = el("myListingsGrid") || el("myListingsContainer");
    var empty = el("myListingsEmpty");
    var status = el("myListingsStatus");
    if(status) status.classList.add("hidden");
    if(!items || !items.length){
      if(grid) grid.innerHTML = "";
      if(empty) empty.classList.remove("hidden");
      return;
    }
    if(empty) empty.classList.add("hidden");
    if(!grid) return;
    grid.innerHTML = items.map(function(it){
      var img = photoOf(it);
      var title = it.title || it.sub_category || it.brand || it.model || it.main_category || "ማስታወቂያ";
      var cat = it.main_category || it.category || "";
      var id = it.id;
      var ph = "https://images.unsplash.com/photo-1533473359331-0135ef1b58bf?auto=format&fit=crop&q=60&w=300";
      return (
        '<div class="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden" data-listing-id="'+esc(String(id))+'">'+
          '<div class="flex gap-0">'+
            '<div class="w-28 h-24 shrink-0 bg-slate-100 overflow-hidden">'+
              '<img src="'+esc(img || ph)+'" class="w-full h-full object-cover" alt="" onerror="this.onerror=null;this.src=\''+ph+'\';" />'+
            '</div>'+
            '<div class="flex-1 p-2.5 min-w-0 flex flex-col justify-between">'+
              '<div>'+
                '<div class="text-xs font-black text-slate-800 truncate">'+esc(title)+'</div>'+
                '<div class="text-[10px] text-slate-500 mt-0.5">'+esc(cat)+' · #'+esc(String(id))+'</div>'+
                '<div class="text-[11px] font-black text-[#0e7490] mt-1">💰 '+esc(priceLabel(it.price))+'</div>'+
              '</div>'+
            '</div>'+
          '</div>'+
          '<button type="button" class="my-listing-delete w-full py-2 bg-rose-50 hover:bg-rose-100 text-rose-600 text-[11px] font-black border-t border-rose-100 active:scale-[0.99]" data-id="'+esc(String(id))+'">'+
            '🗑️ ማስታወቂያውን ሰርዝ (Delete)'+
          '</button>'+
        '</div>'
      );
    }).join("");
    grid.querySelectorAll(".my-listing-delete").forEach(function(btn){
      btn.onclick = function(ev){
        if(ev){ ev.preventDefault(); ev.stopPropagation(); }
        var lid = btn.getAttribute("data-id");
        if(!lid) return;
        if(!confirm("ይህን ማስታወቂያ ሰርዘው? / Delete this listing permanently?")) return;
        // Prefer global deleteListingById (clean ID + Supabase strategies)
        if (typeof window.deleteListingById === "function") {
          window.deleteListingById({ id: lid }, function(ok){
            if(!ok && btn){ btn.disabled = false; btn.textContent = "🗑️ ማስታወቂያውን ሰርዝ (Delete)"; }
          });
          return;
        }
        deleteListing(lid, btn);
      };
    });
  }

  /**
   * REAL Supabase delete — DOM only after success.
   * Filters by id + telegram_id so RLS can allow owner delete.
   */
  function deleteListing(id, btn){
    // Delegate to the single production delete path
    if (typeof window.deleteListingById === "function") {
      window.deleteListingById({ id: id }, function(ok){
        if (!ok && btn) { btn.disabled = false; btn.textContent = "🗑️ ማስታወቂያውን ሰርዝ (Delete)"; }
        else if (typeof loadMyListings === "function") loadMyListings();
      });
      return;
    }
    if (typeof window.deleteListing === "function" && window.deleteListing !== deleteListing) {
      window.deleteListing(id);
    }
  }

  function loadMyListings(){
    var status = el("myListingsStatus");
    var empty = el("myListingsEmpty");
    var grid = el("myListingsGrid") || el("myListingsContainer");
    if(status){ status.classList.remove("hidden"); status.textContent = "እየጫነ ነው..."; }
    if(empty) empty.classList.add("hidden");
    if(grid) grid.innerHTML = "";

    // Always String — matches submitListing payload
    var currentUserId = "";
    try {
      var u = window.Telegram && Telegram.WebApp && Telegram.WebApp.initDataUnsafe && Telegram.WebApp.initDataUnsafe.user;
      if (u && u.id != null) currentUserId = String(u.id);
    } catch (e0) {}
    if (!currentUserId) {
      try { currentUserId = String(tgId() || ""); } catch (e1) {}
    }
    if (!currentUserId || currentUserId === "null" || currentUserId === "undefined") {
      if (status) status.textContent = "Telegram መለያ አልተገኘም — Mini App ከቴሌግራም ይክፈቱ";
      return;
    }
    var uid = String(currentUserId);
    var uidN = null;
    try {
      var n = Number(uid);
      if (isFinite(n) && n > 0) uidN = n;
    } catch (e2) {}

    function isMine(it) {
      if (!it) return false;
      function matchVal(v) {
        if (v == null || v === "") return false;
        var s = String(v);
        return s === uid || (uidN != null && s === String(uidN));
      }
      return matchVal(it.user_id) || matchVal(it.telegram_id) || matchVal(it.user_chat_id)
        || matchVal(it.owner_id) || matchVal(it.seller_id) || matchVal(it.telegram_id_str)
        || matchVal(it.chat_id);
    }

    function apply(rows) {
      rows = (rows || []).filter(isMine);
      // Merge localStorage stash (posts that may not be queryable yet)
      try {
        var key = "adika_my_posts_" + uid;
        var stash = JSON.parse(localStorage.getItem(key) || "[]");
        if (Array.isArray(stash) && stash.length) {
          var seen = {};
          rows.forEach(function (r) { if (r && r.id != null) seen[String(r.id)] = 1; });
          stash.forEach(function (r) {
            if (!r) return;
            if (r.id != null && seen[String(r.id)]) return;
            if (isMine(r) || true) {
              rows.unshift(r);
              if (r.id != null) seen[String(r.id)] = 1;
            }
          });
        }
      } catch (eS) {}
      // Merge in-memory feed items
      try {
        var live = window.__adikaLiveItems || (window.state && state.items) || [];
        if (Array.isArray(live)) {
          var seen2 = {};
          rows.forEach(function (r) { if (r && r.id != null) seen2[String(r.id)] = 1; });
          live.forEach(function (r) {
            if (!isMine(r)) return;
            if (r.id != null && seen2[String(r.id)]) return;
            rows.push(r);
            if (r.id != null) seen2[String(r.id)] = 1;
          });
        }
      } catch (eL) {}
      if (status) status.classList.add("hidden");
      renderCards(rows);
    }

    function fetchFromPublicListings() {
      return fetch("/api/listings?limit=100", { credentials: "same-origin" })
        .then(function (r) { return r.json(); })
        .then(function (d) {
          var list = (d && (d.items || d.listings || d.results || d.data)) || [];
          if (!Array.isArray(list)) list = [];
          apply(list);
        })
        .catch(function () {
          // last resort: memory only
          apply([]);
          if (status) {
            status.classList.remove("hidden");
            status.textContent = "መጫን አልተሳካም";
          }
        });
    }

    var client = sb();
    if (client && typeof client.from === "function") {
      var attempts = [];
      attempts.push(function () { return client.from("listings").select("*").eq("user_id", uid).order("created_at", { ascending: false }); });
      attempts.push(function () { return client.from("listings").select("*").eq("telegram_id", uid).order("created_at", { ascending: false }); });
      attempts.push(function () { return client.from("listings").select("*").eq("user_chat_id", uid).order("created_at", { ascending: false }); });
      if (uidN != null) {
        attempts.push(function () { return client.from("listings").select("*").eq("user_id", uidN).order("created_at", { ascending: false }); });
        attempts.push(function () { return client.from("listings").select("*").eq("telegram_id", uidN).order("created_at", { ascending: false }); });
        attempts.push(function () { return client.from("listings").select("*").eq("user_chat_id", uidN).order("created_at", { ascending: false }); });
      }
      attempts.push(function () { return client.from("listings").select("*").order("created_at", { ascending: false }).limit(100); });

      function run(i) {
        if (i >= attempts.length) return fetchFromPublicListings();
        return attempts[i]().then(function (res) {
          if (res && res.error) return run(i + 1);
          var rows = (res && res.data) || [];
          if (Array.isArray(rows) && rows.length) {
            var mine = rows.filter(isMine);
            if (mine.length) { apply(rows); return; }
            // got rows but none match — try next / public filter
            if (i === attempts.length - 1) { apply(rows); return; }
            return run(i + 1);
          }
          return run(i + 1);
        }).catch(function () { return run(i + 1); });
      }
      run(0);
    } else {
      fetchFromPublicListings();
    }
  }

  window.openMyListings = function(){
    showMyListingsView();
    loadMyListings();
  };
  window.loadMyListings = loadMyListings;

  function bind(){
    var b = el("myListingsBackBtn");
    var c = el("myListingsCloseBtn");
    var p = el("myListingsPostBtn");
    if(b && !b.__bound){ b.__bound = true; b.onclick = function(e){ if(e) e.preventDefault(); hideMyListingsView(); }; }
    if(c && !c.__bound){ c.__bound = true; c.onclick = function(e){ if(e) e.preventDefault(); hideMyListingsView(); }; }
    if(p && !p.__bound){
      p.__bound = true;
      p.onclick = function(){
        hideMyListingsView();
        try{
          if(window.openIntentModal) window.openIntentModal();
          else if(window.openAddListingModal) window.openAddListingModal();
        }catch(e){}
      };
    }
  }
  if(document.readyState === "loading") document.addEventListener("DOMContentLoaded", bind);
  else bind();
})();

/* ===== inline block 9 ===== */

(function(){
  function splitTitle(el){
    var title = el.querySelector(".promo-title");
    if(!title || title.dataset.split==="1") return;
    var raw = title.textContent || "";
    title.innerHTML = raw.split("").map(function(ch,i){
      if(ch===" ") return " ";
      return '<span class="promo-letter" style="animation-delay:'+(i*28)+'ms">'+ch+'</span>';
    }).join("");
    title.dataset.split = "1";
  }
  function run(){
    var slides = document.querySelectorAll("#promoSlides .promo-slide");
    var dots = document.querySelectorAll("#promoDots .promo-dot");
    if(!slides.length) return;
    slides.forEach(splitTitle);
    var i = 0;
    function paint(n){
      i = ((n % slides.length)+slides.length)%slides.length;
      slides.forEach(function(s,k){
        var on = k===i;
        s.style.opacity = on ? "1" : "0";
        s.style.pointerEvents = on ? "auto" : "none";
        s.style.transform = on ? "translateY(0) scale(1)" : "translateY(12px) scale(0.97)";
        s.style.transition = "opacity .4s ease, transform .45s cubic-bezier(.16,1,.3,1)";
        s.classList.toggle("is-active", on);
        if(on){
          s.querySelectorAll(".promo-letter").forEach(function(L){
            L.style.animation = "none";
            void L.offsetWidth;
            L.style.animation = "";
          });
        }
      });
      dots.forEach(function(d,k){
        d.style.background = k===i ? "rgba(255,255,255,.95)" : "rgba(255,255,255,.28)";
        d.style.width = k===i ? "10px" : "6px";
      });
    }
    paint(0);
    setInterval(function(){ paint(i+1); }, 3400);
  }
  if(document.readyState==="loading") document.addEventListener("DOMContentLoaded", run);
  else run();
})();

/* ===== inline block 10 ===== */

(function () {
  function el(id) { return document.getElementById(id); }
  function showM(id) {
    var n = el(id); if (!n) return;
    n.classList.remove("hidden");
    n.classList.add("flex");
    n.style.display = "flex";
  }
  function hideM(id) {
    var n = el(id); if (!n) return;
    n.classList.add("hidden");
    n.classList.remove("flex");
    n.style.display = "none";
  }
  function tgUser() {
    try {
      return (window.Telegram && Telegram.WebApp && Telegram.WebApp.initDataUnsafe && Telegram.WebApp.initDataUnsafe.user) || null;
    } catch (e) { return null; }
  }
  function tgId() {
    var u = tgUser();
    return (u && u.id) || (window.state && state.userId) || null;
  }
  function sbClient() {
    try {
      if (typeof ensureSupabaseClient === "function") return ensureSupabaseClient();
    } catch (e) {}
    return window.supabase || null;
  }

  window.openIntentModal = function () {
    hideM("addListingModal");
    hideM("addRequestModal");
    hideM("requestSuccessModal");
    showM("intentModal");
  };
  window.closeIntentModal = function () {
    hideM("intentModal");
    try { if (window.forceShowFab) forceShowFab(); } catch (e) {}
    try { if (window.restoreHomeChrome) restoreHomeChrome(); } catch (e2) {}
  };

  function setListingStep(n) {
    var s1 = el("listingStep1"), s2 = el("listingStep2");
    var c1 = el("listingStepChip1"), c2 = el("listingStepChip2");
    if (s1) s1.classList.toggle("hidden", n !== 1);
    if (s2) s2.classList.toggle("hidden", n !== 2);
    if (c1) c1.className = n === 1
      ? "flex-1 text-center text-[10px] font-black py-1.5 rounded-lg bg-cyan-400 text-slate-950"
      : "flex-1 text-center text-[10px] font-black py-1.5 rounded-lg text-slate-300";
    if (c2) c2.className = n === 2
      ? "flex-1 text-center text-[10px] font-black py-1.5 rounded-lg bg-cyan-400 text-slate-950"
      : "flex-1 text-center text-[10px] font-black py-1.5 rounded-lg text-slate-300";
  }

  window.openAddListingModal = function () {
    hideM("intentModal");
    setListingStep(1);
    showM("addListingModal");
  };
  window.openAddRequestModal = function () {
    hideM("intentModal");
    try {
      var u = tgUser();
      var tgInp = el("reqTg");
      if (tgInp && !tgInp.value && u && u.username) tgInp.value = "@" + u.username;
    } catch (e) {}
    showM("addRequestModal");
  };

  var photoDataUrls = [];

  function compressImageFile(file, maxW, quality) {
    maxW = maxW || 900;
    quality = quality || 0.72;
    return new Promise(function (resolve) {
      try {
        var reader = new FileReader();
        reader.onerror = function () { resolve(null); };
        reader.onload = function () {
          var dataUrl = reader.result;
          try {
            var img = new Image();
            img.onerror = function () { resolve(typeof dataUrl === "string" ? dataUrl : null); };
            img.onload = function () {
              try {
                var w = img.naturalWidth || img.width || 1;
                var h = img.naturalHeight || img.height || 1;
                var scale = w > maxW ? (maxW / w) : 1;
                var cw = Math.max(1, Math.round(w * scale));
                var ch = Math.max(1, Math.round(h * scale));
                var canvas = document.createElement("canvas");
                canvas.width = cw;
                canvas.height = ch;
                var ctx = canvas.getContext("2d");
                ctx.drawImage(img, 0, 0, cw, ch);
                var out = canvas.toDataURL("image/jpeg", quality);
                // Cap ~280KB string length roughly
                if (out && out.length > 400000) {
                  out = canvas.toDataURL("image/jpeg", 0.55);
                }
                resolve(out || dataUrl);
              } catch (e2) {
                resolve(typeof dataUrl === "string" ? dataUrl : null);
              }
            };
            img.src = dataUrl;
          } catch (e) {
            resolve(typeof dataUrl === "string" ? dataUrl : null);
          }
        };
        reader.readAsDataURL(file);
      } catch (e0) {
        resolve(null);
      }
    });
  }

  function renderPhotoPreview() {
    var prev = el("listPhotoPreview");
    if (!prev) return;
    prev.innerHTML = "";
    photoDataUrls.forEach(function (url, idx) {
      var wrap = document.createElement("div");
      wrap.className = "relative w-full aspect-square rounded-lg overflow-hidden bg-slate-800 border border-white/10";
      var img = document.createElement("img");
      img.src = url;
      img.className = "w-full h-full object-cover";
      img.alt = "photo " + (idx + 1);
      var btn = document.createElement("button");
      btn.type = "button";
      btn.setAttribute("aria-label", "Remove photo");
      btn.className = "absolute top-0.5 right-0.5 w-5 h-5 rounded-full bg-red-500 text-white text-[10px] font-black leading-none flex items-center justify-center shadow z-10";
      btn.textContent = "×";
      btn.onclick = function (e) {
        if (e) { e.preventDefault(); e.stopPropagation(); }
        photoDataUrls.splice(idx, 1);
        renderPhotoPreview();
        // clear file input so same file can be re-selected
        try {
          var inp = el("listPhotos");
          if (inp) inp.value = "";
        } catch (e2) {}
      };
      wrap.appendChild(img);
      wrap.appendChild(btn);
      prev.appendChild(wrap);
    });
  }

  function bindListingPhotos() {
    var inp = el("listPhotos");
    if (!inp || inp.__bound) return;
    inp.__bound = true;
    inp.addEventListener("change", function () {
      var files = Array.prototype.slice.call(inp.files || []).slice(0, 5);
      if (!files.length) return;
      var prev = el("listPhotoPreview");
      if (prev) prev.innerHTML = '<span class="text-[10px] text-slate-400 col-span-5">ፎቶ በመጫን ላይ...</span>';
      var chain = Promise.resolve();
      files.forEach(function (f) {
        chain = chain.then(function () {
          return compressImageFile(f, 900, 0.72).then(function (url) {
            if (url) {
              if (photoDataUrls.length < 5) photoDataUrls.push(url);
            }
          });
        });
      });
      chain.then(function () {
        renderPhotoPreview();
      }).catch(function () {
        renderPhotoPreview();
      });
    });
  }

  function bindCatToggle() {
    document.querySelectorAll('input[name="listCat"]').forEach(function (r) {
      if (r.__bound) return;
      r.__bound = true;
      r.addEventListener("change", function () {
        var house = r.value === "House";
        var cs = el("listCarSpecs"), hs = el("listHouseSpecs");
        if (cs) cs.classList.toggle("hidden", house);
        if (hs) hs.classList.toggle("hidden", !house);
      });
    });
  }

  function listingPayload() {
    var catEl = document.querySelector('input[name="listCat"]:checked');
    var cat = catEl ? catEl.value : "Car";
    var u = tgUser();
    var tid = tgId();
    var tidNum = Number(tid);
    var uploaded = (photoDataUrls || []).filter(function(x){ return !!x; });
    // Allow posting without photo — inject default placeholder
    var DEFAULT_LISTING_IMG = "https://images.unsplash.com/photo-1560518883-ce09059eeffa?w=500&auto=format&fit=crop&q=60";
    var imgs = uploaded.length > 0 ? uploaded : [DEFAULT_LISTING_IMG];
    return {
      title: (el("listTitle") || {}).value || "",
      main_category: cat === "House" ? "ቤት" : "መኪና",
      category: cat === "House" ? "ቤት" : "መኪና",
      sub_category: (el("listTitle") || {}).value || "",
      listing_type: "SELL",
      price: Number((el("listPrice") || {}).value || 0) || 0,
      negotiable: !!(el("listNeg") || {}).checked,
      urgent: !!(el("listUrgent") || {}).checked,
      phone: (el("listPhone") || {}).value || "",
      telegram_username: String((el("listTg") || {}).value || "").replace(/^@/, ""),
      // Always String so My Listings .eq() matches reliably
      telegram_id: tid != null ? String(tid) : "",
      user_id: tid != null ? String(tid) : "",
      user_chat_id: tid != null ? String(tid) : "",
      telegram_id_str: tid != null ? String(tid) : "",
      // Multi-column photo fields so feed + my-listings always find an image
      photos: imgs.slice(),
      photo_urls: imgs.slice(),
      images: imgs.slice(),
      image_url: imgs[0] || DEFAULT_LISTING_IMG,
      extra_data: {
        photos: imgs.slice(),
        photo_urls: imgs.slice(),
        images: imgs.slice(),
        image_url: imgs[0] || DEFAULT_LISTING_IMG,
        placeholder_photo: uploaded.length === 0
      },
      transmission: (el("listTrans") || {}).value || "",
      fuel: (el("listFuel") || {}).value || "",
      condition: (el("listCond") || {}).value || "",
      bedrooms: (el("listBeds") || {}).value || "",
      bathrooms: (el("listBaths") || {}).value || "",
      property_type: (el("listPType") || {}).value || "",
      seller_name: u ? [u.first_name, u.last_name].filter(Boolean).join(" ") : "",
      created_at: new Date().toISOString(),
      status: "active"
    };
  }

  function requestPayload() {
    var catEl = document.querySelector('input[name="reqCat"]:checked');
    var cat = catEl ? catEl.value : "Car";
    var u = tgUser();
    return {
      category: cat === "House" ? "ቤት" : "መኪና",
      main_category: cat === "House" ? "ቤት" : "መኪና",
      budget_min: Number((el("reqMin") || {}).value || 0) || 0,
      budget_max: Number((el("reqMax") || {}).value || 0) || 0,
      notes: (el("reqNotes") || {}).value || "",
      details: (el("reqNotes") || {}).value || "",
      phone: (el("reqPhone") || {}).value || "",
      telegram_id: tgId(),
      user_id: tgId(),
      telegram_username: String((el("reqTg") || {}).value || (u && u.username) || "").replace(/^@/, ""),
      buyer_name: u ? [u.first_name, u.last_name].filter(Boolean).join(" ") : "",
      notify_brokers: true,
      created_at: new Date().toISOString(),
      status: "open"
    };
  }

  function submitListing(ev) {
    if (ev) ev.preventDefault();
    var data = listingPayload();
    if (!data.title || !data.phone) {
      alert("ርዕስ እና ስልክ ያስፈልጋሉ");
      setListingStep(2);
      return;
    }
    var btn = el("listingSubmitBtn");
    if (btn) { btn.disabled = true; btn.textContent = "⏳..."; }

    // Ensure photos is a JSON-safe array of strings (compressed data-URLs or http)
    try {
      var arr = Array.isArray(data.photos) ? data.photos : [];
      arr = arr.filter(function (x) { return typeof x === "string" && x.length > 8; }).slice(0, 5);
      data.photos = arr;
      data.photo_urls = arr.slice();
      data.images = arr.slice();
      data.image_url = arr[0] || data.image_url || "";
      if (data.extra_data && typeof data.extra_data === "object") {
        data.extra_data.photos = arr.slice();
        data.extra_data.photo_urls = arr.slice();
        data.extra_data.images = arr.slice();
        data.extra_data.image_url = arr[0] || "";
      }
    } catch (eNorm) {}

    var hasRealPhotos = Array.isArray(data.photos) && data.photos.length && !(data.extra_data && data.extra_data.placeholder_photo);

    function finishOk() {
      hideM("addListingModal");
      if (btn) { btn.disabled = false; btn.textContent = "🚀 Submit Listing"; }
      // Stash for My Listings (survives ID type / RLS lag)
      try {
        var uid = String((data && (data.user_id || data.telegram_id)) || (tgId && tgId()) || "");
        if (uid) {
          var key = "adika_my_posts_" + uid;
          var stash = [];
          try { stash = JSON.parse(localStorage.getItem(key) || "[]"); } catch (e0) { stash = []; }
          if (!Array.isArray(stash)) stash = [];
          var row = Object.assign({}, data, {
            id: data.id || data.req_id || ("local-" + Date.now()),
            user_id: String(data.user_id || uid),
            telegram_id: String(data.telegram_id || uid),
            user_chat_id: String(data.user_chat_id || uid),
            created_at: data.created_at || new Date().toISOString()
          });
          stash.unshift(row);
          stash = stash.slice(0, 30);
          localStorage.setItem(key, JSON.stringify(stash));
        }
      } catch (eStash) {}
      photoDataUrls = [];
      try { var prev = el("listPhotoPreview"); if (prev) prev.innerHTML = ""; } catch (eP) {}
      try { if (typeof load === "function") load(false); } catch (e) {}
      try { showM("listingSuccessModal"); } catch (e2) {}
      try { if (window.instantShowHomeChrome) instantShowHomeChrome(); } catch (eI) {}
      try { if (window.forceShowFab) forceShowFab(); } catch (e3) {}
      try { if (window.restoreHomeChrome) restoreHomeChrome(); } catch (e4) {}
    }
    function finishFail(msg) {
      if (btn) { btn.disabled = false; btn.textContent = "🚀 Submit Listing"; }
      alert(msg || "ማስታወቂያ ማስገባት አልተሳካም");
    }

    function postApi() {
      return fetch("/api/submit-listing", {
        method: "POST",
        credentials: "same-origin",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
      }).then(function (r) {
        return r.json().catch(function () { return {}; }).then(function (j) {
          if (r.ok && (j.success || j.status === "success" || j.req_id)) {
            try {
              if (j.req_id) data.id = j.req_id;
              if (j.id) data.id = j.id;
            } catch (eId) {}
            finishOk();
            return true;
          }
          console.warn("[Adika] submit-listing fail", r.status, j);
          return false;
        });
      }).catch(function (err) {
        console.warn("[Adika] submit-listing network", err);
        return false;
      });
    }

    function postSupabase() {
      var sb = sbClient();
      if (!(sb && typeof sb.from === "function")) return Promise.resolve(false);
      // Strip huge base64 for Supabase column limits — keep short URLs only; API handles base64
      var slim = Object.assign({}, data);
      try {
        var keep = (slim.photos || []).filter(function (p) {
          return typeof p === "string" && (p.indexOf("http") === 0 || p.length < 50000);
        });
        if (!keep.length && (data.photos || []).length) {
          // photos are large data-URLs — let Flask handle them
          return Promise.resolve(false);
        }
        slim.photos = keep;
        slim.photo_urls = keep.slice();
        slim.images = keep.slice();
        slim.image_url = keep[0] || "";
      } catch (eS) {}
      return sb.from("listings").insert(slim).then(function (res) {
        if (res && res.error) {
          console.warn("[Adika] insert error", res.error);
          return false;
        }
        finishOk();
        return true;
      }).catch(function () { return false; });
    }

    // With photos → API first (handles base64). Without → either path.
    var chain = hasRealPhotos ? postApi().then(function (ok) { return ok ? true : postSupabase(); })
                              : postSupabase().then(function (ok) { return ok ? true : postApi(); });
    chain.then(function (ok) {
      if (!ok) finishFail("ማስታወቂያ ማስገባት አልተሳካም — እንደገና ይሞክሩ");
    });
  }

  function submitRequest(ev) {
    if (ev) ev.preventDefault();
    var data = requestPayload();
    if (!data.phone) { alert("ስልክ ያስፈልጋል"); return; }
    var btn = el("requestSubmitBtn");
    if (btn) { btn.disabled = true; btn.textContent = "⏳..."; }
    var sb = sbClient();
    var done = function () {
      hideM("addRequestModal");
      showM("requestSuccessModal");
      if (btn) { btn.disabled = false; btn.textContent = "ጥያቄ ላክ → ደላሎች"; }
      try {
        fetch("/api/notify-brokers", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(data) }).catch(function () {});
      } catch (e) {}
    };
    if (sb && typeof sb.from === "function") {
      sb.from("buyer_requests").insert(data).then(done).catch(function () {
        fetch("/api/submit-request", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(data) })
          .then(done).catch(done);
      });
    } else {
      fetch("/api/submit-request", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(data) })
        .then(done).catch(done);
    }
  }

  function bind() {
    bindListingPhotos();
    bindCatToggle();
    var sell = el("intentSellCard");
    var req = el("intentRequestCard");
    var ic = el("intentCloseBtn");
    if (sell && !sell.__bound) { sell.__bound = true; sell.onclick = function () { window.openAddListingModal(); }; }
    if (req && !req.__bound) { req.__bound = true; req.onclick = function () { window.openAddRequestModal(); }; }
    if (ic && !ic.__bound) { ic.__bound = true; ic.onclick = function () { hideM("intentModal"); }; }
    var ln = el("listingNextBtn"), lb = el("listingBackBtn"), lc = el("listingCloseBtn");
    if (ln && !ln.__bound) { ln.__bound = true; ln.onclick = function () { setListingStep(2); }; }
    if (lb && !lb.__bound) { lb.__bound = true; lb.onclick = function () { setListingStep(1); }; }
    if (lc && !lc.__bound) { lc.__bound = true; lc.onclick = function () { hideM("addListingModal"); }; }
    var rc = el("requestCloseBtn");
    if (rc && !rc.__bound) { rc.__bound = true; rc.onclick = function () { hideM("addRequestModal"); }; }
    var ok = el("requestSuccessOk");
    if (ok && !ok.__bound) { ok.__bound = true; ok.onclick = function () { hideM("requestSuccessModal"); }; }
    var lok = el("listingSuccessOk");
    if (lok && !lok.__bound) { lok.__bound = true; lok.onclick = function () { hideM("listingSuccessModal"); }; }
    var lf = el("addListingForm");
    if (lf && !lf.__bound) { lf.__bound = true; lf.addEventListener("submit", submitListing); }
    var rf = el("addRequestForm");
    if (rf && !rf.__bound) { rf.__bound = true; rf.addEventListener("submit", submitRequest); }
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", bind);
  else bind();
})();

/* ===== Buyers tab + single-banner + grid reset (overrides) ===== */
(function () {
  function el(id) { return document.getElementById(id); }

  window.fetchBuyers = window.fetchBuyers || async function fetchBuyers() {
    var rows = [];
    try {
      var res = await fetch("/api/listings?type=BUY&page=1&limit=40&order=DESC&active_only=1", { credentials: "same-origin" });
      if (res.ok) {
        var j = await res.json().catch(function () { return {}; });
        rows = j.data || j.listings || j.items || j.results || [];
      }
    } catch (e) {}
    if ((!rows || !rows.length) && window.supabase && typeof window.supabase.from === "function") {
      try {
        var r1 = await window.supabase.from("buyer_requests").select("*").order("created_at", { ascending: false }).limit(40);
        if (r1 && !r1.error) rows = r1.data || [];
      } catch (e2) {}
    }
    return Array.isArray(rows) ? rows : [];
  };

  function highlightBuyersTab(buy) {
    var s = el("tabSell"), b = el("tabBuy");
    if (s) {
      s.className = buy
        ? "tab-feed-btn py-1 rounded-lg text-xs font-bold transition-all text-white/90 hover:text-white flex items-center justify-center gap-1"
        : "tab-feed-btn is-active py-1 rounded-lg text-xs font-bold transition-all bg-white text-[#16acbd] shadow-sm flex items-center justify-center gap-1";
    }
    if (b) {
      b.className = buy
        ? "tab-feed-btn is-active py-1 rounded-lg text-xs font-bold transition-all bg-white text-[#16acbd] shadow-sm flex items-center justify-center gap-1"
        : "tab-feed-btn py-1 rounded-lg text-xs font-bold transition-all text-white/90 hover:text-white flex items-center justify-center gap-1";
    }
    window.__adikaIsBuy = !!buy;
    try { if (window.state) window.state.tab = buy ? "requests" : "marketplace"; } catch (e) {}
  }

  function clearGrid() {
    var g = el("grid");
    if (g) g.innerHTML = "";
  }

  function hideDuplicateBanners() {
    ["smartToolsBanner", "heroCarousel", "toolsReel", "smartBannerTrack"].forEach(function (id) {
      var n = el(id);
      if (n && n.closest && n.closest(".hidden")) return;
      /* keep promo once */
    });
  }

  function openBuyers() {
    highlightBuyersTab(true);
    clearGrid();
    hideDuplicateBanners();
    if (typeof load === "function") {
      try { if (window.state) window.state.tab = "requests"; load(false); return; } catch (e) {}
    }
    window.fetchBuyers().then(function (items) {
      if (typeof paintLive === "function") paintLive(items || []);
      else if (typeof finishLoading === "function") finishLoading(items || [], false, false);
    });
  }

  function openMarket() {
    highlightBuyersTab(false);
    clearGrid();
    if (typeof load === "function") {
      try { if (window.state) window.state.tab = "marketplace"; load(false); return; } catch (e) {}
    }
    if (typeof fetchListings === "function") {
      fetchListings({ limit: 20, offset: 0 }).then(function (items) {
        if (typeof paintLive === "function") paintLive(items || []);
      });
    }
  }

  function bindTabs() {
    var s = el("tabSell"), b = el("tabBuy");
    if (s) s.addEventListener("click", function (e) {
      e.preventDefault(); e.stopPropagation();
      openMarket();
    }, true);
    if (b) b.addEventListener("click", function (e) {
      e.preventDefault(); e.stopPropagation();
      openBuyers();
    }, true);
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", bindTabs);
  else bindTabs();
})();


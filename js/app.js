/* js/app.js — Init, Telegram, event listeners, forms, promo */
(function (w) {
  "use strict";

  function el(id) { return document.getElementById(id); }

  /* ----- Telegram ----- */
  function tgReady() {
    try {
      var tg = w.Telegram && w.Telegram.WebApp;
      if (!tg) return null;
      tg.ready();
      try { tg.expand(); } catch (e) {}
      return tg;
    } catch (e2) { return null; }
  }

  function tgUser() {
    try {
      var tg = w.Telegram && w.Telegram.WebApp;
      return (tg && tg.initDataUnsafe && tg.initDataUnsafe.user) || null;
    } catch (e) { return null; }
  }

  function tgId() {
    var u = tgUser();
    return u && u.id ? u.id : null;
  }

  function getTelegramUserId() {
    var id = tgId();
    return id != null ? String(id) : "";
  }

  function isAdikaAdmin() {
    var id = Number(tgId() || 0);
    var list = w.ADMIN_IDS || [];
    if (list.indexOf(id) >= 0) return true;
    if (Number(w.ADMIN_TELEGRAM_ID) === id) return true;
    if (Number(w.__ADIKA_ADMIN_ID) === id) return true;
    return false;
  }

  w.getTelegramUserId = getTelegramUserId;
  w.tgUser = tgUser;
  w.tgId = tgId;
  w.isAdikaAdmin = isAdikaAdmin;

  /* ----- Promo rotator ----- */
  function startPromo() {
    var slides = document.querySelectorAll("#promoSlides .promo-slide");
    if (!slides.length) return;
    var i = 0;
    function show(n) {
      slides.forEach(function (s, idx) {
        var on = idx === n;
        s.classList.toggle("is-active", on);
        s.style.opacity = on ? "1" : "0";
        s.style.pointerEvents = on ? "auto" : "none";
      });
    }
    show(0);
    setInterval(function () {
      i = (i + 1) % slides.length;
      show(i);
    }, 4200);

    var banner = el("adikaPromoBanner");
    if (banner && !banner.__bound) {
      banner.__bound = true;
      banner.onclick = function () {
        var active = document.querySelector("#promoSlides .promo-slide.is-active");
        var tool = active && active.getAttribute("data-tool");
        if (typeof w.openTools === "function") w.openTools();
        if (tool && typeof w.showM === "function") {
          // map tool name → modal if present
          var map = { duty: "dutyModal", loan: "loanModal", chassis: "chassisModal", contract: "contractModal", compare: "compareModal", poa: "poaModal" };
          if (map[tool]) {
            try { w.hideM("aiModal"); w.showM(map[tool]); } catch (e) {}
          }
        }
      };
    }
  }

  /* ----- Listing photos ----- */
  var photoDataUrls = [];
  w.photoDataUrls = photoDataUrls;

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
                var ww = img.naturalWidth || img.width || 1;
                var hh = img.naturalHeight || img.height || 1;
                var scale = ww > maxW ? (maxW / ww) : 1;
                var canvas = document.createElement("canvas");
                canvas.width = Math.max(1, Math.round(ww * scale));
                canvas.height = Math.max(1, Math.round(hh * scale));
                canvas.getContext("2d").drawImage(img, 0, 0, canvas.width, canvas.height);
                var out = canvas.toDataURL("image/jpeg", quality);
                if (out && out.length > 400000) out = canvas.toDataURL("image/jpeg", 0.55);
                resolve(out || dataUrl);
              } catch (e2) { resolve(typeof dataUrl === "string" ? dataUrl : null); }
            };
            img.src = dataUrl;
          } catch (e) { resolve(typeof dataUrl === "string" ? dataUrl : null); }
        };
        reader.readAsDataURL(file);
      } catch (e0) { resolve(null); }
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
      var btn = document.createElement("button");
      btn.type = "button";
      btn.className = "absolute top-0.5 right-0.5 w-5 h-5 rounded-full bg-red-500 text-white text-[10px] font-black leading-none flex items-center justify-center shadow z-10";
      btn.textContent = "×";
      btn.onclick = function (e) {
        if (e) { e.preventDefault(); e.stopPropagation(); }
        photoDataUrls.splice(idx, 1);
        renderPhotoPreview();
        try { var inp = el("listPhotos"); if (inp) inp.value = ""; } catch (e2) {}
      };
      wrap.appendChild(img);
      wrap.appendChild(btn);
      prev.appendChild(wrap);
    });
  }

  function setListingStep(n) {
    var s1 = el("listingStep1"), s2 = el("listingStep2");
    if (s1) s1.classList.toggle("hidden", n !== 1);
    if (s2) s2.classList.toggle("hidden", n !== 2);
  }

  function listingPayload() {
    var catEl = document.querySelector('input[name="listCat"]:checked');
    var cat = catEl ? catEl.value : "Car";
    var u = tgUser();
    var tid = tgId();
    var uploaded = (photoDataUrls || []).filter(Boolean);
    var DEFAULT_IMG = "https://images.unsplash.com/photo-1560518883-ce09059eeffa?w=500&auto=format&fit=crop&q=60";
    var imgs = uploaded.length ? uploaded : [DEFAULT_IMG];
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
      telegram_id: tid != null ? String(tid) : "",
      user_id: tid != null ? String(tid) : "",
      user_chat_id: tid != null ? String(tid) : "",
      photos: imgs.slice(),
      photo_urls: imgs.slice(),
      images: imgs.slice(),
      image_url: imgs[0] || DEFAULT_IMG,
      extra_data: { photos: imgs.slice(), placeholder_photo: uploaded.length === 0 },
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

  async function onSubmitListing(ev) {
    if (ev) ev.preventDefault();
    var data = listingPayload();
    if (!data.title || !data.phone) {
      alert("ርዕስ እና ስልክ ያስፈልጋሉ");
      setListingStep(2);
      return;
    }
    var btn = el("listingSubmitBtn");
    if (btn) { btn.disabled = true; btn.textContent = "⏳..."; }

    var result = typeof w.submitListing === "function" ? await w.submitListing(data) : { ok: false };
    if (btn) { btn.disabled = false; btn.textContent = "🚀 Submit Listing"; }

    if (result && result.ok) {
      try {
        var uid = String(data.user_id || getTelegramUserId() || "");
        if (uid) {
          var key = "adika_my_posts_" + uid;
          var stash = [];
          try { stash = JSON.parse(localStorage.getItem(key) || "[]"); } catch (e0) {}
          if (!Array.isArray(stash)) stash = [];
          stash.unshift(Object.assign({}, data, { id: data.id || ("local-" + Date.now()) }));
          localStorage.setItem(key, JSON.stringify(stash.slice(0, 30)));
        }
      } catch (eStash) {}
      photoDataUrls.length = 0;
      try { var prev = el("listPhotoPreview"); if (prev) prev.innerHTML = ""; } catch (eP) {}
      if (typeof w.hideM === "function") w.hideM("addListingModal");
      if (typeof w.showM === "function") w.showM("listingSuccessModal");
      if (typeof w.loadListings === "function") w.loadListings("&type=SELL");
      if (typeof w.restoreHomeChrome === "function") w.restoreHomeChrome();
    } else {
      alert("ማስታወቂያ ማስገባት አልተሳካም — እንደገና ይሞክሩ");
    }
  }

  async function onSubmitRequest(ev) {
    if (ev) ev.preventDefault();
    var data = requestPayload();
    if (!data.phone) { alert("ስልክ ያስፈልጋል"); return; }
    var btn = el("requestSubmitBtn");
    if (btn) { btn.disabled = true; btn.textContent = "⏳..."; }
    var result = typeof w.submitRequest === "function" ? await w.submitRequest(data) : { ok: false };
    if (btn) { btn.disabled = false; btn.textContent = "ጥያቄ ላክ → ደላሎች"; }
    if (typeof w.hideM === "function") w.hideM("addRequestModal");
    if (typeof w.showM === "function") w.showM("requestSuccessModal");
  }

  /* ----- My Listings ----- */
  async function openMyListings() {
    var view = el("myListingsView");
    if (!view) {
      // fallback: load and filter by uid
      if (typeof w.fetchMyListings === "function") {
        var items = await w.fetchMyListings();
        if (typeof w.paintLive === "function") {
          w.__adikaIsBuy = false;
          if (typeof w.markTabs === "function") w.markTabs(false);
          w.paintLive(items);
        }
        if (typeof w.toast === "function") w.toast("የእኔ ማስታወቂያዎች (" + (items.length || 0) + ")");
      }
      return;
    }
    if (typeof w.showM === "function") w.showM("myListingsView");
    var box = el("myListingsGrid") || el("myListingsList");
    if (box) box.innerHTML = '<div class="text-center text-xs text-slate-400 p-4">በመጫን ላይ...</div>';
    var items = typeof w.fetchMyListings === "function" ? await w.fetchMyListings() : [];
    if (!box) return;
    if (!items.length) {
      box.innerHTML = '<div class="text-center text-xs text-slate-500 p-6">ምንም ማስታወቂያ የለዎትም</div>';
      return;
    }
    var html = "";
    var admin = isAdikaAdmin();
    items.forEach(function (it) {
      var title = typeof w.titleOf === "function" ? w.titleOf(it) : (it.title || "ማስታወቂያ");
      var price = typeof w.money === "function" ? w.money(it.price) : (it.price || "");
      html +=
        '<div class="rounded-xl bg-white/10 border border-white/15 p-3 mb-2 flex items-center justify-between gap-2">' +
          '<div class="min-w-0"><div class="text-xs font-bold text-white truncate">' + title + '</div>' +
          '<div class="text-[10px] text-cyan-200">' + price + "</div></div>" +
          '<button type="button" class="my-del-btn shrink-0 px-2 py-1 rounded-lg bg-rose-500 text-white text-[10px] font-black" data-id="' + String(it.id || "") + '">ሰርዝ</button>' +
        "</div>";
    });
    box.innerHTML = html;
    box.querySelectorAll(".my-del-btn").forEach(function (btn) {
      btn.onclick = async function () {
        var id = btn.getAttribute("data-id");
        if (!id || !confirm("ማስታወቂያው ይሰረዝ?")) return;
        if (typeof w.deleteListing === "function") {
          var r = await w.deleteListing(id);
          if (r && r.ok) {
            btn.closest("div").remove();
            if (typeof w.toast === "function") w.toast("ተሰርዟል");
          } else {
            alert("መሰረዝ አልተሳካም");
          }
        }
      };
    });
  }

  /* ----- Bind UI ----- */
  function bindAll() {
    if (typeof w.bindLightbox === "function") w.bindLightbox();

    // Tabs
    var tabSell = el("tabSell"), tabBuy = el("tabBuy");
    if (tabSell && !tabSell.__bound) {
      tabSell.__bound = true;
      tabSell.onclick = function (ev) {
        if (ev) { ev.preventDefault(); ev.stopPropagation(); }
        if (typeof w.switchTab === "function") w.switchTab("marketplace");
      };
    }
    if (tabBuy && !tabBuy.__bound) {
      tabBuy.__bound = true;
      tabBuy.onclick = function (ev) {
        if (ev) { ev.preventDefault(); ev.stopPropagation(); }
        if (typeof w.switchTab === "function") w.switchTab("requests");
      };
    }

    // Nav
    var navHome = el("navHome");
    if (navHome && !navHome.__bound) {
      navHome.__bound = true;
      navHome.onclick = function (ev) {
        if (ev) { ev.preventDefault(); }
        if (typeof w.openHome === "function") w.openHome();
      };
    }
    var navAi = el("navAi");
    if (navAi && !navAi.__bound) {
      navAi.__bound = true;
      navAi.onclick = function (ev) {
        if (ev) { ev.preventDefault(); }
        if (typeof w.openTools === "function") w.openTools();
      };
    }
    var navMine = el("navMine") || el("navMyListings");
    if (navMine && !navMine.__bound) {
      navMine.__bound = true;
      navMine.onclick = function (ev) {
        if (ev) { ev.preventDefault(); }
        openMyListings();
      };
    }

    // FAB
    var fab = el("fabBtn");
    if (fab && !fab.__bound) {
      fab.__bound = true;
      fab.onclick = function (ev) {
        if (ev) { ev.preventDefault(); }
        if (typeof w.openIntentModal === "function") w.openIntentModal();
      };
    }

    // Lang
    var langAm = el("langAmBtn"), langEn = el("langEnBtn");
    if (langAm && !langAm.__bound) {
      langAm.__bound = true;
      langAm.onclick = function (ev) {
        if (ev) { ev.preventDefault(); }
        if (typeof w.setLang === "function") w.setLang(false);
      };
    }
    if (langEn && !langEn.__bound) {
      langEn.__bound = true;
      langEn.onclick = function (ev) {
        if (ev) { ev.preventDefault(); }
        if (typeof w.setLang === "function") w.setLang(true);
      };
    }

    // Intent / forms
    var sell = el("intentSellCard"), req = el("intentRequestCard"), ic = el("intentCloseBtn");
    if (sell && !sell.__bound) { sell.__bound = true; sell.onclick = function () { if (w.openAddListingModal) w.openAddListingModal(); }; }
    if (req && !req.__bound) { req.__bound = true; req.onclick = function () { if (w.openAddRequestModal) w.openAddRequestModal(); }; }
    if (ic && !ic.__bound) { ic.__bound = true; ic.onclick = function () { if (w.closeIntentModal) w.closeIntentModal(); }; }

    var ln = el("listingNextBtn"), lb = el("listingBackBtn"), lc = el("listingCloseBtn");
    if (ln && !ln.__bound) { ln.__bound = true; ln.onclick = function () { setListingStep(2); }; }
    if (lb && !lb.__bound) { lb.__bound = true; lb.onclick = function () { setListingStep(1); }; }
    if (lc && !lc.__bound) { lc.__bound = true; lc.onclick = function () { if (w.hideM) w.hideM("addListingModal"); if (w.restoreHomeChrome) w.restoreHomeChrome(); }; }

    var rc = el("requestCloseBtn");
    if (rc && !rc.__bound) { rc.__bound = true; rc.onclick = function () { if (w.hideM) w.hideM("addRequestModal"); if (w.restoreHomeChrome) w.restoreHomeChrome(); }; }

    var lok = el("listingSuccessOk"), rok = el("requestSuccessOk");
    if (lok && !lok.__bound) { lok.__bound = true; lok.onclick = function () { if (w.hideM) w.hideM("listingSuccessModal"); if (w.restoreHomeChrome) w.restoreHomeChrome(); }; }
    if (rok && !rok.__bound) { rok.__bound = true; rok.onclick = function () { if (w.hideM) w.hideM("requestSuccessModal"); if (w.restoreHomeChrome) w.restoreHomeChrome(); }; }

    var lf = el("addListingForm");
    if (lf && !lf.__bound) { lf.__bound = true; lf.addEventListener("submit", onSubmitListing); }
    var rf = el("addRequestForm");
    if (rf && !rf.__bound) { rf.__bound = true; rf.addEventListener("submit", onSubmitRequest); }

    // Photos
    var inp = el("listPhotos");
    if (inp && !inp.__bound) {
      inp.__bound = true;
      inp.addEventListener("change", function () {
        var files = Array.prototype.slice.call(inp.files || []).slice(0, 5);
        if (!files.length) return;
        var prev = el("listPhotoPreview");
        if (prev) prev.innerHTML = '<span class="text-[10px] text-slate-400 col-span-5">ፎቶ በመጫን ላይ...</span>';
        var chain = Promise.resolve();
        files.forEach(function (f) {
          chain = chain.then(function () {
            return compressImageFile(f).then(function (url) {
              if (url && photoDataUrls.length < 5) photoDataUrls.push(url);
            });
          });
        });
        chain.then(renderPhotoPreview).catch(renderPhotoPreview);
      });
    }

    // Category radio toggle car/house specs
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

    // Global click: cats, cards, back buttons
    document.addEventListener("click", function (e) {
      var t = e.target && e.target.closest ? e.target.closest("button, a, .cat-pill, .adika-card, [data-live]") : null;
      if (!t) return;
      var id = t.id || "";

      if (id === "aiModalClose" || id === "aiHubBackBtn") {
        e.preventDefault();
        if (w.openHome) w.openHome();
        return;
      }
      if (id === "analysisBackBtn" || id === "analysisCloseBtn") {
        e.preventDefault();
        if (w.hideM) w.hideM("analysisView");
        if (w.openTools) w.openTools();
        return;
      }
      if (id === "analysisHomeBtn") {
        e.preventDefault();
        if (w.hideM) w.hideM("analysisView");
        if (w.openHome) w.openHome();
        return;
      }
      if (id === "modalClose" || id === "modalBackBtn") {
        e.preventDefault();
        if (w.hideM) { w.hideM("modalOverlay"); w.hideM("detailModal"); }
        if (w.restoreHomeChrome) w.restoreHomeChrome();
        return;
      }

      // Category pills
      if (t.classList && t.classList.contains("cat-pill")) {
        var cid = t.getAttribute("data-id") || "all";
        var filter = t.getAttribute("data-filter");
        e.preventDefault();
        document.querySelectorAll("#cats .cat-pill").forEach(function (b) {
          if (b.getAttribute("data-filter") === "chassis") return;
          var on = (b.getAttribute("data-id") || "") === cid;
          b.className = on
            ? "cat-pill px-3 py-1 rounded-full text-xs font-bold whitespace-nowrap transition-all bg-white text-[#16acbd] shadow-sm"
            : "cat-pill px-3 py-1 rounded-full text-xs font-bold whitespace-nowrap transition-all bg-white/20 text-white hover:bg-white/30";
        });
        if (!w.loadListings) return;
        if (filter === "chassis") { w.loadListings("&has_chassis=1"); return; }
        if (cid === "foryou") {
          fetch("/api/feed/for-you", { credentials: "same-origin" })
            .then(function (r) { return r.json(); })
            .then(function (d) {
              var items = (d && (d.items || d.listings || d.results)) || [];
              if (Array.isArray(items) && items.length && w.paintLive) w.paintLive(items);
              else w.loadListings("&type=SELL");
            })
            .catch(function () { w.loadListings("&type=SELL"); });
        } else if (cid === "all") {
          w.loadListings(w.__adikaIsBuy ? "&type=BUY" : "&type=SELL");
        } else {
          w.loadListings((w.__adikaIsBuy ? "&type=BUY" : "&type=SELL") + "&category=" + encodeURIComponent(cid));
        }
        return;
      }

      // Card open
      if (t.getAttribute("data-live") === "1" || (t.classList && t.classList.contains("adika-card"))) {
        var card = (t.closest && t.closest(".adika-card")) || t;
        var items = w.__adikaLiveItems || [];
        var it = null;
        var did = card.getAttribute("data-id");
        if (did) {
          for (var i = 0; i < items.length; i++) {
            if (String(items[i].id) === String(did)) { it = items[i]; break; }
          }
        }
        if (!it) return;
        e.preventDefault();
        if (typeof w.openDetailModal === "function") {
          try { w.openDetailModal(it); } catch (err) {}
        } else {
          if (el("modalTitle")) el("modalTitle").textContent = w.titleOf ? w.titleOf(it) : (it.title || "");
          if (el("modalPrice")) el("modalPrice").textContent = w.money ? w.money(it.price) : "";
          if (el("modalDesc")) el("modalDesc").textContent = it.description || "";
          if (w.showM) w.showM("modalOverlay");
        }
      }
    }, true);

    // Image zoom → lightbox
    document.addEventListener("click", function (e) {
      var t = e.target;
      if (!t) return;
      if (t.id === "detail-main-image" || t.id === "mainDetailImage" || (t.classList && t.classList.contains("modal-photo-main"))) {
        var src = t.getAttribute("src");
        if (src && w.openLightbox) w.openLightbox(src);
      }
    });
  }

  function boot() {
    tgReady();
    try {
      w.currentUser = tgUser();
    } catch (e) {}

    bindAll();
    startPromo();

    if (typeof w.markTabs === "function") w.markTabs(false);
    if (typeof w.loadListings === "function") w.loadListings("&type=SELL");
    if (typeof w.restoreHomeChrome === "function") w.restoreHomeChrome();

    // Fit feed under fixed header
    try {
      var hdr = el("adikaFixedHeader");
      var main = el("adikaMainFeed");
      if (hdr && main) {
        var h = hdr.offsetHeight || 108;
        main.style.paddingTop = (h + 4) + "px";
      }
    } catch (e2) {}
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})(window);

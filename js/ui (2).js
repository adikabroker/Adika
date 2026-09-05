/* js/ui.js — Modals, navigation, lightbox, FAB, tabs, paint */
(function (w) {
  "use strict";

  function el(id) { return document.getElementById(id); }

  function showM(id) {
    var n = el(id);
    if (!n) return;
    n.classList.remove("hidden");
    n.style.display = (id.indexOf("Modal") >= 0 || id.indexOf("View") >= 0 || n.classList.contains("fixed")) ? "flex" : "block";
  }

  function hideM(id) {
    var n = el(id);
    if (!n) return;
    n.classList.add("hidden");
    n.style.display = "none";
  }

  function restoreHomeChrome() {
    var nav = el("adikaBottomNav");
    if (nav) {
      nav.style.display = "flex";
      nav.classList.remove("hidden");
    }
    var fab = el("fabBtn");
    if (fab) {
      fab.classList.remove("hidden");
      fab.style.setProperty("display", "flex", "important");
      fab.style.visibility = "visible";
      fab.style.opacity = "1";
      fab.style.pointerEvents = "auto";
      fab.style.zIndex = "90";
    }
    try { document.body.style.overflow = ""; } catch (e) {}
  }

  function forceShowFab() { restoreHomeChrome(); }

  var TOOL_IDS = [
    "dutyModal", "loanModal", "compareModal", "contractModal",
    "poaModal", "landMapModal", "diagModal", "chassisModal"
  ];

  function hideAllTools() { TOOL_IDS.forEach(hideM); }

  function goBack() {
    [
      "detailModal", "modalRoot", "modalSheet", "modalOverlay",
      "addListingModal", "addRequestModal", "intentModal",
      "aiModal", "analysisView", "contractModal", "inboxView",
      "myListingsView", "brokerRegModal", "roleSelectModal"
    ].concat(TOOL_IDS).forEach(function (id) {
      var n = el(id);
      if (n && !n.classList.contains("hidden") && n.style.display !== "none") {
        n.classList.add("hidden");
        n.style.display = "none";
      }
    });
    restoreHomeChrome();
  }

  function openLightbox(src) {
    var box = el("adikaImageLightbox");
    var img = el("adikaLightboxImg");
    if (!box || !img || !src) return;
    img.src = src;
    box.classList.add("is-open");
    box.classList.remove("hidden");
    box.style.display = "flex";
  }

  function closeLightbox() {
    var box = el("adikaImageLightbox");
    var img = el("adikaLightboxImg");
    if (img) img.src = "";
    if (box) {
      box.classList.remove("is-open");
      box.classList.add("hidden");
      box.style.display = "none";
    }
  }

  function bindLightbox() {
    var box = el("adikaImageLightbox");
    var closeBtn = el("adikaLightboxClose");
    if (closeBtn && !closeBtn.__bound) {
      closeBtn.__bound = true;
      closeBtn.onclick = function (e) {
        if (e) e.stopPropagation();
        closeLightbox();
      };
    }
    if (box && !box.__bound) {
      box.__bound = true;
      box.addEventListener("click", function (e) {
        if (e.target === box) closeLightbox();
      });
    }
  }

  /* ----- Tabs ----- */
  var state = w.state || { tab: "marketplace", items: [], page: 0, hasMore: true };
  w.state = state;

  function markTabs(buy) {
    var s = el("tabSell"), b = el("tabBuy");
    var active = "py-1 rounded-lg text-xs font-bold transition-all bg-white text-[#16acbd] shadow-sm flex items-center justify-center gap-1";
    var idle = "py-1 rounded-lg text-xs font-bold transition-all text-white/90 hover:text-white flex items-center justify-center gap-1";
    if (s) s.className = buy ? idle : active;
    if (b) b.className = buy ? active : idle;
    w.__adikaIsBuy = !!buy;
    state.tab = buy ? "requests" : "marketplace";
  }

  function isBuyItem(it) {
    if (!it) return false;
    if (it._source === "buyer_requests" || it.is_buyer_request) return true;
    var t = [it.req_type, it.action_type, it.listing_type, it.post_type, it.status].join(" ");
    if (/BUY|REQUEST|WANT|መግዛት|ለመግዛት|ፈላጊ/i.test(t)) return true;
    if ((it.budget_min != null || it.budget_max != null) && !it.price) return true;
    return false;
  }

  function clearGrid() {
    var g = el("grid");
    if (g) g.innerHTML = "";
    w.__adikaLiveItems = [];
    state.items = [];
  }

  function money(v) {
    var n = Number(String(v || "").replace(/[^\d.]/g, ""));
    if (!n || n <= 0 || n > 300000000) return "ለዋጋ ደውሉ";
    return Math.round(n).toLocaleString("en-US") + " ETB";
  }

  function titleOf(it) {
    var t = [it.brand, it.model].filter(Boolean).join(" ").trim();
    if (t) return t;
    return it.sub_category || it.title || it.category || it.main_category || "ማስታወቂያ";
  }

  function photoOf(it) {
    var p = (it && (it.photo_urls || it.photos || it.images || it.image_url || it.image || it.photo)) || "";
    if (Array.isArray(p)) p = p[0] || "";
    if (p && typeof p === "object") p = p.url || p.src || "";
    p = String(p || "").trim();
    return (!p || p === "null") ? "" : p;
  }

  function paintLive(items) {
    var g = el("grid");
    if (!g) return;
    items = items || [];
    var buy = !!w.__adikaIsBuy;
    if (buy) {
      var any = items.some(isBuyItem);
      if (any) items = items.filter(isBuyItem);
    } else {
      items = items.filter(function (it) { return !isBuyItem(it); });
    }
    w.__adikaLiveItems = items;
    state.items = items;

    if (!items.length) {
      g.innerHTML = buy
        ? '<div style="grid-column:1/-1;padding:28px 12px;text-align:center;color:#475569;font-weight:800;">📋 የፈላጊ ጥያቄ አልተገኘም</div>'
        : '<div style="grid-column:1/-1;padding:28px 12px;text-align:center;color:#475569;font-weight:800;">ምንም ማስታወቂያ አልተገኘም</div>';
      return;
    }

    if (typeof w.__adikaCreateCard === "function") {
      g.innerHTML = "";
      items.forEach(function (it) {
        try { g.appendChild(w.__adikaCreateCard(it)); } catch (e) {}
      });
      return;
    }

    var html = "";
    for (var i = 0; i < items.length; i++) {
      var it = items[i] || {};
      var src = photoOf(it);
      var icon = /ቤት|house|propert/i.test(String(it.main_category || it.category || "")) ? "🏠" : "🚗";
      var img = src
        ? '<img class="listing-photo-enhance" src="' + String(src).replace(/"/g, "") + '" style="width:100%;height:100%;object-fit:cover;" onerror="this.style.display=\'none\'" />'
        : "";
      html +=
        '<button type="button" class="adika-card" data-live="1" data-id="' + String(it.id || "") + '">' +
          '<div class="listing-photo-frame">' +
            '<div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font-size:36px;z-index:0;">' + icon + "</div>" + img +
          "</div>" +
          '<div style="padding:7px 8px 8px;">' +
            '<div class="card-title-row"><div class="card-title">' + titleOf(it) + "</div></div>" +
            '<div style="margin-top:4px;"><div class="card-price">💰 ' + money(it.price || it.budget_max || it.budget_min) + "</div></div>" +
          "</div>" +
        "</button>";
    }
    g.innerHTML = html;
  }

  function loadListings(extra) {
    clearGrid();
    var buy = /type=BUY/i.test(extra || "") || !!w.__adikaIsBuy;
    var status = el("status");
    if (status) { status.style.display = "block"; status.textContent = "በመጫን ላይ..."; }

    function done(items) {
      if (status) status.style.display = "none";
      paintLive(items || []);
    }

    if (buy && typeof w.fetchBuyerRequests === "function") {
      w.fetchBuyerRequests({ limit: 40 }).then(function (items) {
        if (items && items.length) { done(items); return; }
        return w.fetchListings({ type: "BUY", limit: 40 }).then(done);
      }).catch(function () { done([]); });
      return;
    }

    var opts = { limit: 40 };
    if (/type=SELL/i.test(extra || "")) opts.type = "SELL";
    if (/has_chassis/i.test(extra || "")) opts.has_chassis = true;
    var catM = /category=([^&]+)/.exec(extra || "");
    if (catM) opts.category = decodeURIComponent(catM[1]);

    if (typeof w.fetchListings === "function") {
      w.fetchListings(opts).then(done).catch(function () { done([]); });
    } else {
      done([]);
    }
  }

  function switchTab(mode) {
    var buy = mode === "requests";
    markTabs(buy);
    clearGrid();
    state.page = 0;
    state.hasMore = true;
    loadListings(buy ? "&type=BUY" : "&type=SELL");
  }

  function setLang(en) {
    document.body.classList.toggle("lang-en-active", !!en);
    document.documentElement.lang = en ? "en" : "am";
    var am = el("langAmBtn"), enBtn = el("langEnBtn");
    var on = "px-2 py-1 rounded-lg text-xs font-extrabold transition-all bg-white text-[#16acbd] shadow-sm";
    var off = "px-2 py-1 rounded-lg text-xs font-extrabold transition-all text-white/80 hover:text-white";
    if (am) am.className = en ? off : on;
    if (enBtn) enBtn.className = en ? on : off;
  }

  function openTools() {
    hideM("analysisView");
    hideAllTools();
    showM("aiModal");
    var n = el("aiModal");
    if (n) { n.style.display = "flex"; n.style.zIndex = "260"; }
  }

  function openHome() {
    goBack();
    restoreHomeChrome();
    try { w.scrollTo({ top: 0, behavior: "smooth" }); } catch (e) { w.scrollTo(0, 0); }
  }

  function openChat() {
    hideM("aiModal");
    hideAllTools();
    showM("analysisView");
    var n = el("analysisView");
    if (n) { n.style.display = "flex"; n.style.zIndex = "280"; }
  }

  function openIntentModal() { showM("intentModal"); }
  function closeIntentModal() { hideM("intentModal"); restoreHomeChrome(); }
  function openAddListingModal() { hideM("intentModal"); showM("addListingModal"); }
  function openAddRequestModal() { hideM("intentModal"); showM("addRequestModal"); }

  function toast(msg) {
    var t = el("adikaToast");
    if (!t) return;
    t.textContent = msg;
    t.classList.remove("hidden");
    t.style.display = "block";
    clearTimeout(t.__tid);
    t.__tid = setTimeout(function () {
      t.classList.add("hidden");
      t.style.display = "none";
    }, 2500);
  }

  /* exports */
  w.el = el;
  w.showM = showM;
  w.hideM = hideM;
  w.goBack = goBack;
  w.restoreHomeChrome = restoreHomeChrome;
  w.forceShowFab = forceShowFab;
  w.instantShowHomeChrome = restoreHomeChrome;
  w.openLightbox = openLightbox;
  w.closeLightbox = closeLightbox;
  w.bindLightbox = bindLightbox;
  w.markTabs = markTabs;
  w.switchTab = switchTab;
  w.paintLive = paintLive;
  w.loadListings = loadListings;
  w.clearGrid = clearGrid;
  w.setLang = setLang;
  w.openTools = openTools;
  w.openHome = openHome;
  w.openChat = openChat;
  w.openAiChat = openChat;
  w.handleStartAiChat = openChat;
  w.openIntentModal = openIntentModal;
  w.closeIntentModal = closeIntentModal;
  w.openAddListingModal = openAddListingModal;
  w.openAddRequestModal = openAddRequestModal;
  w.toast = toast;
  w.money = money;
  w.titleOf = titleOf;
  w.photoOf = photoOf;
  w.isBuyItem = isBuyItem;
  w.TOOL_IDS = TOOL_IDS;

  w.closeModal = function (id) {
    if (id) hideM(id);
    else goBack();
    if (id && TOOL_IDS.indexOf(id) !== -1) openTools();
    else restoreHomeChrome();
  };
  w.navigateBack = function (id) {
    if (id === "analysisView") { hideM("analysisView"); openTools(); return; }
    if (id && TOOL_IDS.indexOf(id) !== -1) { hideM(id); openTools(); return; }
    if (id) hideM(id);
    else openHome();
  };
  w.goHomeFromTool = function (id) {
    if (id) hideM(id);
    openHome();
  };
})(window);

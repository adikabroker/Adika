/* ui.js — clean UTF-8 UI layer for Adika Marketplace
   Modals, navigation, lightbox, FAB restore, tab toggles.
   Does NOT duplicate api.js or telegram.js. */
(function (w) {
  "use strict";

  function el(id) {
    return document.getElementById(id);
  }

  function showM(id) {
    var n = el(id);
    if (!n) return;
    n.classList.remove("hidden");
    n.style.display = (id.indexOf("Modal") >= 0 || n.classList.contains("fixed")) ? "flex" : "block";
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
      fab.style.display = "flex";
      fab.classList.remove("hidden");
      fab.style.visibility = "visible";
      fab.style.opacity = "1";
      fab.style.pointerEvents = "auto";
    }
    try { document.body.style.overflow = ""; } catch (e) {}
  }

  function forceShowFab() {
    restoreHomeChrome();
  }

  var TOOL_IDS = [
    "dutyModal", "loanModal", "compareModal", "contractModal",
    "poaModal", "landMapModal", "diagModal", "chassisModal"
  ];

  function hideAllTools() {
    TOOL_IDS.forEach(hideM);
  }

  function goBack() {
    [
      "detailModal", "modalRoot", "modalSheet", "modalOverlay",
      "addListingModal", "addRequestModal", "intentModal",
      "aiModal", "analysisView", "contractModal", "inboxView",
      "myListingsView", "brokerRegModal", "roleSelectModal"
    ].concat(TOOL_IDS).forEach(function (id) {
      var n = el(id);
      if (n && n.style.display !== "none" && !n.classList.contains("hidden")) {
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
    box.style.display = "flex";
  }

  function closeLightbox() {
    var box = el("adikaImageLightbox");
    var img = el("adikaLightboxImg");
    if (img) img.src = "";
    if (box) {
      box.classList.remove("is-open");
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
    document.addEventListener("click", function (e) {
      var t = e.target;
      if (!t) return;
      if (
        t.id === "detail-main-image" ||
        t.id === "mainDetailImage" ||
        (t.classList && t.classList.contains("modal-photo-main"))
      ) {
        var src = t.getAttribute("src");
        if (src) openLightbox(src);
      }
    });
  }

  /* ---------- Tabs: Marketplace / Buyers ---------- */
  var state = w.state || { tab: "marketplace", items: [], page: 0, hasMore: true, loading: false };
  w.state = state;

  function markTabs(buy) {
    var s = el("tabSell");
    var b = el("tabBuy");
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
    var t =
      (it.req_type || "") + " " +
      (it.action_type || "") + " " +
      (it.listing_type || "") + " " +
      (it.post_type || "") + " " +
      (it.status || "");
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
    var p = (it && (it.photo_urls || it.photos || it.listing_photos || it.image_url || it.image || it.photo)) || "";
    if (Array.isArray(p)) p = p[0] || "";
    if (p && typeof p === "object") p = p.url || p.src || "";
    p = String(p || "").trim();
    if (!p || p === "null") return "";
    return p;
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
        ? '<img src="' + String(src).replace(/"/g, "") + '" style="width:100%;height:100%;object-fit:cover;" onerror="this.style.display=\'none\'" />'
        : "";
      html +=
        '<button type="button" class="adika-card" data-live="1" data-id="' + String(it.id || "") + '" style="background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 8px 20px rgba(15,23,42,0.08);text-align:left;border:1px solid rgba(226,232,240,0.8);">' +
          '<div style="aspect-ratio:4/3;background:linear-gradient(135deg,#e0f7fa,#b2ebf2);position:relative;overflow:hidden;">' +
            '<div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font-size:36px;">' + icon + "</div>" + img +
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
    var qs = "page=1&limit=40&order=DESC&active_only=1" + (extra || "");

    function done(items) {
      paintLive(items || []);
    }

    if (buy && typeof w.fetchBuyerRequests === "function") {
      w.fetchBuyerRequests({ limit: 40 })
        .then(function (items) {
          if (items && items.length) { done(items); return; }
          return fetch("/api/listings?" + qs, { credentials: "same-origin" })
            .then(function (r) { return r.json(); })
            .then(function (d) {
              var rows = (d && (d.items || d.listings || d.results || d.data)) || [];
              if (!Array.isArray(rows) && rows && rows.items) rows = rows.items;
              done(rows);
            });
        })
        .catch(function () { done([]); });
      return;
    }

    fetch("/api/listings?" + qs, { credentials: "same-origin" })
      .then(function (r) { return r.json(); })
      .then(function (d) {
        var rows = (d && (d.items || d.listings || d.results || d.data)) || [];
        if (!Array.isArray(rows) && rows && rows.items) rows = rows.items;
        done(rows);
      })
      .catch(function () { done([]); });
  }

  function switchTab(mode) {
    var buy = mode === "requests";
    markTabs(buy);
    clearGrid();
    state.page = 0;
    state.hasMore = true;
    if (buy) loadListings("&type=BUY");
    else loadListings("&type=SELL");
  }

  function setLang(en) {
    document.body.classList.toggle("lang-en-active", !!en);
    document.documentElement.lang = en ? "en" : "am";
    var am = el("langAmBtn");
    var enBtn = el("langEnBtn");
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

  /* ---------- Intent / listing helpers (thin) ---------- */
  function openIntentModal() {
    showM("intentModal");
  }
  function closeIntentModal() {
    hideM("intentModal");
    restoreHomeChrome();
  }
  function openAddListingModal() {
    hideM("intentModal");
    showM("addListingModal");
  }
  function openAddRequestModal() {
    hideM("intentModal");
    showM("addRequestModal");
  }

  /* ---------- Bind once ---------- */
  function bindTabs() {
    var tabSell = el("tabSell");
    var tabBuy = el("tabBuy");
    if (tabSell && !tabSell.__bound) {
      tabSell.__bound = true;
      tabSell.onclick = function (ev) {
        if (ev) { ev.preventDefault(); ev.stopPropagation(); }
        switchTab("marketplace");
      };
    }
    if (tabBuy && !tabBuy.__bound) {
      tabBuy.__bound = true;
      tabBuy.onclick = function (ev) {
        if (ev) { ev.preventDefault(); ev.stopPropagation(); }
        switchTab("requests");
      };
    }
  }

  function bindNav() {
    var navHome = el("navHome");
    if (navHome && !navHome.__bound) {
      navHome.__bound = true;
      navHome.onclick = function (ev) {
        if (ev) { ev.preventDefault(); ev.stopPropagation(); }
        openHome();
      };
    }
    var navAi = el("navAi");
    if (navAi && !navAi.__bound) {
      navAi.__bound = true;
      navAi.onclick = function (ev) {
        if (ev) { ev.preventDefault(); ev.stopPropagation(); }
        openTools();
      };
    }
    var fab = el("fabBtn");
    if (fab && !fab.__bound) {
      fab.__bound = true;
      fab.onclick = function (ev) {
        if (ev) { ev.preventDefault(); ev.stopPropagation(); }
        openIntentModal();
      };
    }
    var langAm = el("langAmBtn");
    var langEn = el("langEnBtn");
    if (langAm && !langAm.__bound) {
      langAm.__bound = true;
      langAm.onclick = function (ev) {
        if (ev) { ev.preventDefault(); ev.stopPropagation(); }
        setLang(false);
      };
    }
    if (langEn && !langEn.__bound) {
      langEn.__bound = true;
      langEn.onclick = function (ev) {
        if (ev) { ev.preventDefault(); ev.stopPropagation(); }
        setLang(true);
      };
    }
  }

  function bindIntent() {
    var sell = el("intentSellCard");
    var req = el("intentRequestCard");
    var ic = el("intentCloseBtn");
    if (sell && !sell.__bound) {
      sell.__bound = true;
      sell.onclick = function () { openAddListingModal(); };
    }
    if (req && !req.__bound) {
      req.__bound = true;
      req.onclick = function () { openAddRequestModal(); };
    }
    if (ic && !ic.__bound) {
      ic.__bound = true;
      ic.onclick = function () { closeIntentModal(); };
    }
    var lc = el("listingCloseBtn");
    if (lc && !lc.__bound) {
      lc.__bound = true;
      lc.onclick = function () { hideM("addListingModal"); restoreHomeChrome(); };
    }
    var rc = el("requestCloseBtn");
    if (rc && !rc.__bound) {
      rc.__bound = true;
      rc.onclick = function () { hideM("addRequestModal"); restoreHomeChrome(); };
    }
    var lok = el("listingSuccessOk");
    if (lok && !lok.__bound) {
      lok.__bound = true;
      lok.onclick = function () { hideM("listingSuccessModal"); restoreHomeChrome(); };
    }
    var rok = el("requestSuccessOk");
    if (rok && !rok.__bound) {
      rok.__bound = true;
      rok.onclick = function () { hideM("requestSuccessModal"); restoreHomeChrome(); };
    }
  }

  function bindPromo() {
    var banner = el("adikaPromoBanner");
    if (banner && !banner.__bound) {
      banner.__bound = true;
      banner.onclick = function () { openTools(); };
    }
  }

  function bindGlobalClicks() {
    document.addEventListener("click", function (e) {
      var t = e.target && e.target.closest
        ? e.target.closest("button, a, .cat-pill, .adika-card, [data-live]")
        : null;
      if (!t) return;
      var id = t.id || "";

      if (id === "tabBuy") {
        e.preventDefault();
        e.stopPropagation();
        switchTab("requests");
        return;
      }
      if (id === "tabSell") {
        e.preventDefault();
        e.stopPropagation();
        switchTab("marketplace");
        return;
      }
      if (id === "aiModalClose" || id === "aiHubBackBtn") {
        e.preventDefault();
        e.stopPropagation();
        openHome();
        return;
      }
      if (id === "analysisBackBtn" || id === "analysisCloseBtn") {
        e.preventDefault();
        e.stopPropagation();
        hideM("analysisView");
        openTools();
        return;
      }
      if (id === "analysisHomeBtn") {
        e.preventDefault();
        e.stopPropagation();
        hideM("analysisView");
        openHome();
        return;
      }
      if (id === "modalClose" || id === "modalBackBtn") {
        e.preventDefault();
        e.stopPropagation();
        hideM("modalOverlay");
        hideM("detailModal");
        restoreHomeChrome();
        return;
      }
      if (t.classList && t.classList.contains("cat-pill")) {
        var cid = t.getAttribute("data-id") || "all";
        var filter = t.getAttribute("data-filter");
        e.preventDefault();
        e.stopPropagation();
        document.querySelectorAll("#cats .cat-pill").forEach(function (b) {
          if (b.getAttribute("data-filter") === "chassis") return;
          var on = (b.getAttribute("data-id") || "") === cid;
          b.className = on
            ? "cat-pill px-3 py-1 rounded-full text-xs font-bold whitespace-nowrap transition-all bg-white text-[#16acbd] shadow-sm"
            : "cat-pill px-3 py-1 rounded-full text-xs font-bold whitespace-nowrap transition-all bg-white/20 text-white hover:bg-white/30";
        });
        if (filter === "chassis") {
          loadListings("&has_chassis=1");
          return;
        }
        if (cid === "foryou") {
          fetch("/api/feed/for-you", { credentials: "same-origin" })
            .then(function (r) { return r.json(); })
            .then(function (d) {
              var items = (d && (d.items || d.listings || d.results)) || [];
              if (Array.isArray(items) && items.length) paintLive(items);
              else loadListings("&type=SELL");
            })
            .catch(function () { loadListings("&type=SELL"); });
        } else if (cid === "all") {
          loadListings(w.__adikaIsBuy ? "&type=BUY" : "&type=SELL");
        } else {
          loadListings((w.__adikaIsBuy ? "&type=BUY" : "&type=SELL") + "&category=" + encodeURIComponent(cid));
        }
        return;
      }
      if (t.getAttribute("data-live") === "1" || (t.classList && t.classList.contains("adika-card"))) {
        var card = (t.closest && t.closest(".adika-card")) || t;
        var items = w.__adikaLiveItems || [];
        var it = null;
        var did = card.getAttribute("data-id");
        if (did && items.length) {
          for (var i = 0; i < items.length; i++) {
            if (String(items[i].id) === String(did)) { it = items[i]; break; }
          }
        }
        if (!it) {
          var cards = Array.prototype.slice.call(document.querySelectorAll("#grid .adika-card"));
          var idx = cards.indexOf(card);
          if (idx >= 0 && items[idx]) it = items[idx];
        }
        if (!it) return;
        e.preventDefault();
        e.stopPropagation();
        if (typeof w.openDetailModal === "function") {
          try { w.openDetailModal(it); } catch (err) {}
        } else {
          if (el("modalTitle")) el("modalTitle").textContent = titleOf(it);
          if (el("modalPrice")) el("modalPrice").textContent = money(it.price);
          if (el("modalDesc")) el("modalDesc").textContent = it.description || "";
          showM("modalOverlay");
        }
      }
    }, true);
  }

  function boot() {
    bindLightbox();
    bindTabs();
    bindNav();
    bindIntent();
    bindPromo();
    bindGlobalClicks();
    markTabs(false);
    loadListings("&type=SELL");
    restoreHomeChrome();
  }

  /* Exports */
  w.showM = showM;
  w.hideM = hideM;
  w.goBack = goBack;
  w.restoreHomeChrome = restoreHomeChrome;
  w.forceShowFab = forceShowFab;
  w.openLightbox = openLightbox;
  w.closeLightbox = closeLightbox;
  w.markTabs = markTabs;
  w.switchTab = switchTab;
  w.paintLive = paintLive;
  w.loadListings = loadListings;
  w.openIntentModal = openIntentModal;
  w.closeIntentModal = closeIntentModal;
  w.openAddListingModal = openAddListingModal;
  w.openAddRequestModal = openAddRequestModal;
  w.openAiChat = openChat;
  w.handleStartAiChat = openChat;
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

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})(window);

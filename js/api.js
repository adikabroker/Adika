/* js/api.js — Flask / Supabase data layer for Adika Marketplace */
(function (w) {
  "use strict";

  var LISTINGS_TABLE = "listings";
  var PHOTOS_TABLE = "listing_photos";
  var REQUESTS_TABLE = "buyer_requests";

  function sbClient() {
    try {
      if (w.supabase && typeof w.supabase.from === "function") return w.supabase;
      if (w.__supabaseLib && w.__ADIKA_SUPABASE) {
        var c = w.__ADIKA_SUPABASE;
        if (c.url && (c.anonKey || c.key)) {
          w.supabase = w.__supabaseLib.createClient(c.url, c.anonKey || c.key);
          return w.supabase;
        }
      }
    } catch (e) {}
    return null;
  }

  function uid() {
    try {
      if (typeof w.getTelegramUserId === "function") {
        var id = w.getTelegramUserId();
        if (id) return String(id);
      }
    } catch (e) {}
    try {
      var u = w.Telegram && w.Telegram.WebApp && w.Telegram.WebApp.initDataUnsafe && w.Telegram.WebApp.initDataUnsafe.user;
      if (u && u.id) return String(u.id);
    } catch (e2) {}
    try {
      if (w.currentUser && w.currentUser.id) return String(w.currentUser.id);
    } catch (e3) {}
    return "";
  }

  function normalizeListing(r) {
    r = r || {};
    var photos = r.photos || r.photo_urls || r.images || r.listing_photos || [];
    if (typeof photos === "string") {
      try { photos = JSON.parse(photos); } catch (e) { photos = photos ? [photos] : []; }
    }
    if (!Array.isArray(photos)) photos = photos ? [photos] : [];
    photos = photos.map(function (p) {
      if (!p) return "";
      if (typeof p === "string") return p;
      return p.url || p.src || p.image_url || "";
    }).filter(Boolean);
    if (!photos.length && r.image_url) photos = [r.image_url];
    r.photos = photos;
    r.photo_urls = photos.slice();
    r.images = photos.slice();
    r.image_url = photos[0] || r.image_url || "";
    return r;
  }

  async function fetchListings(opts) {
    opts = opts || {};
    var limit = opts.limit || 40;
    var offset = opts.offset || 0;
    var page = opts.page || (Math.floor(offset / limit) + 1);
    var type = opts.type || "";
    var category = opts.category || "";
    var qs = "page=" + page + "&limit=" + limit + "&order=DESC&active_only=1";
    if (type) qs += "&type=" + encodeURIComponent(type);
    if (category) qs += "&category=" + encodeURIComponent(category);
    if (opts.has_chassis) qs += "&has_chassis=1";

    var urls = ["/api/listings?" + qs, "/api/explorer/listings?" + qs];
    for (var i = 0; i < urls.length; i++) {
      try {
        var res = await fetch(urls[i], { credentials: "same-origin" });
        if (!res.ok) continue;
        var j = await res.json().catch(function () { return {}; });
        var rows = j.items || j.listings || j.results || j.data || [];
        if (!Array.isArray(rows) && rows && Array.isArray(rows.items)) rows = rows.items;
        if (Array.isArray(rows) && rows.length) {
          return rows.map(normalizeListing);
        }
      } catch (e) {}
    }

    var sb = sbClient();
    if (sb) {
      try {
        var q = sb.from(LISTINGS_TABLE).select("*").order("created_at", { ascending: false }).range(offset, offset + limit - 1);
        var out = await q;
        if (out && !out.error && Array.isArray(out.data)) {
          return out.data.map(normalizeListing);
        }
      } catch (e2) {}
    }
    return [];
  }

  async function fetchBuyerRequests(opts) {
    opts = opts || {};
    var limit = opts.limit || 40;
    var offset = opts.offset || 0;
    var page = opts.page || (Math.floor(offset / limit) + 1);

    var urls = [
      "/api/buyer-requests?page=" + page + "&limit=" + limit + "&order=DESC&active_only=1",
      "/api/requests?page=" + page + "&limit=" + limit + "&order=DESC",
      "/api/listings?page=" + page + "&limit=" + limit + "&order=DESC&active_only=1&type=BUY"
    ];
    for (var i = 0; i < urls.length; i++) {
      try {
        var res = await fetch(urls[i], { credentials: "same-origin" });
        if (!res.ok) continue;
        var j = await res.json().catch(function () { return {}; });
        var rows = j.items || j.listings || j.results || j.data || [];
        if (!Array.isArray(rows) && rows && Array.isArray(rows.items)) rows = rows.items;
        if (Array.isArray(rows) && rows.length) {
          return rows.map(function (r) {
            r = normalizeListing(r);
            r.listing_type = r.listing_type || r.req_type || "BUY";
            r.req_type = r.req_type || "BUY";
            r._source = r._source || "buyer_requests";
            r.is_buyer_request = true;
            return r;
          });
        }
      } catch (e) {}
    }

    var sb = sbClient();
    if (sb) {
      try {
        var out = await sb.from(REQUESTS_TABLE).select("*").order("created_at", { ascending: false }).range(offset, offset + limit - 1);
        if (out && !out.error && Array.isArray(out.data) && out.data.length) {
          return out.data.map(function (r) {
            r = normalizeListing(r);
            r.listing_type = "BUY";
            r.req_type = "BUY";
            r._source = "buyer_requests";
            r.is_buyer_request = true;
            return r;
          });
        }
      } catch (e2) {}
    }
    return [];
  }

  async function fetchMyListings() {
    var id = uid();
    if (!id) return [];
    var results = [];

    try {
      var res = await fetch("/api/my-listings?telegram_id=" + encodeURIComponent(id), { credentials: "same-origin" });
      if (res.ok) {
        var j = await res.json().catch(function () { return {}; });
        var rows = j.items || j.listings || j.data || [];
        if (Array.isArray(rows)) results = rows.map(normalizeListing);
      }
    } catch (e) {}

    if (!results.length) {
      var sb = sbClient();
      if (sb) {
        try {
          var out = await sb.from(LISTINGS_TABLE).select("*").or(
            "telegram_id.eq." + id + ",user_id.eq." + id + ",user_chat_id.eq." + id
          ).order("created_at", { ascending: false });
          if (out && !out.error && Array.isArray(out.data)) {
            results = out.data.map(normalizeListing);
          }
        } catch (e2) {}
      }
    }

    // local stash fallback
    try {
      var key = "adika_my_posts_" + id;
      var stash = JSON.parse(localStorage.getItem(key) || "[]");
      if (Array.isArray(stash) && stash.length) {
        var seen = {};
        results.forEach(function (r) { if (r.id) seen[String(r.id)] = true; });
        stash.forEach(function (r) {
          if (r && r.id && !seen[String(r.id)]) results.push(normalizeListing(r));
        });
      }
    } catch (e3) {}

    return results;
  }

  async function submitListing(data) {
    data = data || {};
    // API first for photos
    try {
      var res = await fetch("/api/submit-listing", {
        method: "POST",
        credentials: "same-origin",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
      });
      var j = await res.json().catch(function () { return {}; });
      if (res.ok && (j.success || j.status === "success" || j.req_id || j.id)) {
        if (j.req_id) data.id = j.req_id;
        if (j.id) data.id = j.id;
        return { ok: true, data: data, response: j };
      }
    } catch (e) {}

    var sb = sbClient();
    if (sb) {
      try {
        var slim = Object.assign({}, data);
        var keep = (slim.photos || []).filter(function (p) {
          return typeof p === "string" && (p.indexOf("http") === 0 || p.length < 50000);
        });
        slim.photos = keep;
        slim.photo_urls = keep.slice();
        slim.images = keep.slice();
        slim.image_url = keep[0] || "";
        var out = await sb.from(LISTINGS_TABLE).insert(slim);
        if (out && !out.error) return { ok: true, data: data };
      } catch (e2) {}
    }
    return { ok: false };
  }

  async function submitRequest(data) {
    data = data || {};
    var sb = sbClient();
    if (sb) {
      try {
        var out = await sb.from(REQUESTS_TABLE).insert(data);
        if (out && !out.error) {
          try {
            fetch("/api/notify-brokers", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify(data)
            }).catch(function () {});
          } catch (e) {}
          return { ok: true };
        }
      } catch (e2) {}
    }
    try {
      var res = await fetch("/api/submit-request", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
      });
      if (res.ok) return { ok: true };
    } catch (e3) {}
    return { ok: false };
  }

  async function deleteListing(id) {
    if (!id) return { ok: false };
    try {
      var res = await fetch("/api/delete-listing", {
        method: "POST",
        credentials: "same-origin",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id: id, telegram_id: uid() })
      });
      if (res.ok) return { ok: true };
    } catch (e) {}

    var sb = sbClient();
    if (sb) {
      try {
        var out = await sb.from(LISTINGS_TABLE).delete().eq("id", id);
        if (out && !out.error) return { ok: true };
      } catch (e2) {}
    }
    return { ok: false };
  }

  w.sbClient = sbClient;
  w.uid = uid;
  w.normalizeListing = normalizeListing;
  w.fetchListings = fetchListings;
  w.fetchBuyerRequests = fetchBuyerRequests;
  w.fetchMyListings = fetchMyListings;
  w.submitListing = submitListing;
  w.submitRequest = submitRequest;
  w.deleteListing = deleteListing;
  w.ADIKA_TABLES = { listings: LISTINGS_TABLE, photos: PHOTOS_TABLE, requests: REQUESTS_TABLE };
})(window);

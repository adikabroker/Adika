/* api.js — listings CRUD against ONE table: listings
   Photos live in listing_photos (FK listing_id) AND as arrays on the row.
   Feed GET and DELETE must use the same table. Do not mix adika_clean_market. */
(function (w) {
  "use strict";

  var LISTINGS_TABLE = "listings";
  var PHOTOS_TABLE = "listing_photos";
  var REQUESTS_TABLE = "buyer_requests";

  function sbClient() {
    try {
      if (w.supabase && typeof w.supabase.from === "function") return w.supabase;
      var lib = w.__supabaseLib || w.supabase;
      var cfg = w.__ADIKA_SUPABASE || {};
      var url = cfg.url || w.SUPABASE_URL || "";
      var key = cfg.anonKey || cfg.key || w.SUPABASE_ANON_KEY || "";
      if (url && key && lib && typeof lib.createClient === "function") {
        w.supabase = lib.createClient(url, key);
        return w.supabase;
      }
    } catch (e) {}
    return w.supabase && typeof w.supabase.from === "function" ? w.supabase : null;
  }

  function uid() {
    return String((w.currentUser && w.currentUser.telegram_id) || (typeof w.tgId === "function" && w.tgId()) || "");
  }

  function normalizeListing(row) {
    if (!row || typeof row !== "object") return row;
    var photos = row.photos || row.photo_urls || row.images || [];
    if (!Array.isArray(photos)) photos = photos ? [photos] : [];
    if (!photos.length && row.image_url) photos = [row.image_url];
    row.photos = photos;
    row.images = photos;
    row.image_url = row.image_url || photos[0] || "";
    row.telegram_id = row.telegram_id != null ? String(row.telegram_id) : "";
    return row;
  }

  async function fetchListings(opts) {
    opts = opts || {};
    var limit = opts.limit || 20;
    var offset = opts.offset || 0;
    var sb = sbClient();

    try {
      var res = await fetch("/api/listings?limit=" + limit + "&offset=" + offset, { credentials: "same-origin" });
      if (res.ok) {
        var j = await res.json().catch(function () { return {}; });
        var rows = j.data || j.listings || j.items || [];
        if (Array.isArray(rows) && rows.length) return rows.map(normalizeListing);
      }
    } catch (e) {}

    if (sb) {
      var q = sb.from(LISTINGS_TABLE).select("*").order("created_at", { ascending: false }).range(offset, offset + limit - 1);
      var out = await q;
      if (out && !out.error) return (out.data || []).map(normalizeListing);
    }
    return [];
  }

  async function fetchMyListings() {
    var me = uid();
    if (!me) return [];
    var sb = sbClient();
    if (sb) {
      var out = await sb.from(LISTINGS_TABLE).select("*").eq("telegram_id", String(me)).order("created_at", { ascending: false });
      if (out && !out.error) return (out.data || []).map(normalizeListing);
    }
    var all = await fetchListings({ limit: 200, offset: 0 });
    return all.filter(function (r) { return String(r.telegram_id || "") === String(me); });
  }

  async function submitListing(payload) {
    var data = payload || {};
    data.telegram_id = String(data.telegram_id || uid() || "");
    try {
      var res = await fetch("/api/submit-listing", {
        method: "POST",
        credentials: "same-origin",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
      });
      var j = await res.json().catch(function () { return {}; });
      if (res.ok && (j.success || j.status === "success" || j.id)) return { ok: true, data: j };
    } catch (e) {}

    var sb = sbClient();
    if (sb) {
      var ins = await sb.from(LISTINGS_TABLE).insert(data).select();
      if (ins && !ins.error) {
        var row = (ins.data && ins.data[0]) || null;
        if (row && Array.isArray(data.photos)) {
          try {
            var photoRows = data.photos.map(function (url, i) {
              return { listing_id: row.id, url: url, sort_order: i };
            });
            await sb.from(PHOTOS_TABLE).insert(photoRows);
          } catch (e2) {}
        }
        return { ok: true, data: row };
      }
      return { ok: false, error: ins && ins.error };
    }
    return { ok: false, error: "no backend" };
  }

  function confirmDelete(msg) {
    return new Promise(function (resolve) {
      try {
        if (w.Telegram && Telegram.WebApp && typeof Telegram.WebApp.showConfirm === "function") {
          Telegram.WebApp.showConfirm(msg, function (ok) { resolve(!!ok); });
          return;
        }
      } catch (e) {}
      try { resolve(!!w.confirm(msg)); } catch (e2) { resolve(false); }
    });
  }

  async function deleteListing(id) {
    if (id == null || id === "") return { ok: false, error: "missing id" };
    var okConfirm = await confirmDelete("ይህን ማስታወቂያ ማጥፋት ይፈልጋሉ?");
    if (!okConfirm) return { ok: false, cancelled: true };

    var me = uid();
    var admin = typeof w.isAdikaAdmin === "function" && w.isAdikaAdmin(me);

    try {
      var res = await fetch("/api/items/" + encodeURIComponent(id), {
        method: "DELETE",
        credentials: "same-origin",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ telegram_id: me, is_admin: admin })
      });
      var j = await res.json().catch(function () { return {}; });
      if (res.ok && (j.status === "success" || j.success || j.deleted)) {
        return { ok: true, data: j };
      }
      return { ok: false, error: j.message || ("HTTP " + res.status), status: res.status };
    } catch (err) {
      return { ok: false, error: String(err) };
    }
  }

  w.ADIKA_TABLES = { listings: LISTINGS_TABLE, photos: PHOTOS_TABLE, requests: REQUESTS_TABLE };
  w.fetchListings = fetchListings;
  w.fetchMyListings = fetchMyListings;
  w.submitListing = submitListing;
  w.deleteListing = deleteListing;
  w.sbClient = sbClient;
})(window);
